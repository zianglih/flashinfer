# MegaMoE input preparation versus W4A16 weight preparation

Read-only re-audit, 2026-10-07. This extends `TRACE_ANALYSIS.md` with a narrower
answer to which input work actually overlaps weight decode. No HAI or GitHub
files were edited by this analysis.

## Finding

The selected traces directly support overlap between weight load/decode and
**in-kernel input fetching, staging into the expert FC1 pool, and publication of
FC1 tile readiness**. They do not demonstrate overlap with the earlier
`dispatch_stage_local_inputs` copy. This distinction lets the article explain a
larger scheduling opportunity without treating all input preparation as one
interval.

MegaMoE publishes expert counts and scheduling metadata before it finishes
pulling every activation into its expert's FC1 input pool. The weight side can
consume the resulting work records immediately. The activation side waits on
the corresponding input-tile readiness counter. The source hence moves the
activation dependency to the activation role instead of placing a common wait
in front of all the roles.

The first local input-copy stage and routing/count exchange still precede the
first work record in these captures. Claiming that weight decoding overlaps the
entire initial copy or host/prelaunch staging would not follow from this evidence.

## Source structure

Pinned public source remains PR5019 head
`7ca3eb567a2400df70579d55e9bc717ea1784b0c`:

- `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/token_comm.py:23-99`:
  `stage_inputs` copies live hidden rows, expert IDs, and routing weights into
  the peer-visible input buffers. It uses 128-bit BF16 copies for the contiguous
  source path and runs on dispatch warps before routing preparation.
- `flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py:1565-1650`:
  `dispatch_warp_body` performs route preparation and the dispatch barrier,
  arrives at the dispatch-to-scheduler named barrier, then calls
  `dispatch_pull`. The scheduler therefore need not wait for all token pulls.
- The same base transport file, lines578-599:
  `fc1_tma_b_predispatch_spin` waits for the required `fc1_ready_counter` threshold
  for a specific work tile, unless the scheduler has already marked it ready.
- The same base transport file, lines900-1150:
  `dispatch_pull` resolves the source token/rank, fetches activation bytes using
  TMA, reads routing weight, stores into the FC1 expert pool, and publishes
  readiness only after stores are safe to consume.
- `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1246-1358`:
  scheduler warp7 waits for metadata; weight warp5 consumes each work record
  without activation-readiness waits; activation warp6 waits on the FC1 token
  counter or the FC1 intermediate for FC2. Decoder warps12-19 independently
  consume weight stages (around1525).
- `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:1411-1504`:
  split already isolates the predecessor-grid dependency in its activation-TMA
  warp when PDL is enabled. Weight preparation can run ahead there as well.

The newly cached base transport source is
`evidence/flashinfer-pr5019-source/base_token_comm.py`, fetched from the pinned
public raw URL. The public source's detailed trace-marker names differ from the
archive's private instrumentation. We infer corresponding roles from semantics;
we do not assert that the source pin is the trace capture commit.

## Direct observations

Times below are microseconds from the capture's own kernel-marker start. Unless
specified otherwise these are CTA0; the captures contain only cluster(0,0,0),
two CTAs, on one selected rank each.

| Event |128-token rank1|4096-token rank3|
|---|---:|---:|
|Initial local input staging, dispatch warp8|1.824–5.376|2.112–25.344|
|Latest end of local input staging across all8 captured dispatch lanes|5.600|26.496|
|Scheduler's dispatch metadata wait returns|14.752|37.152|
|First work record publication|17.440–17.536|41.952–42.048|
|Dispatch warp8 fetches/stages expert inputs|14.752–26.976|37.184–167.776|
|First packed expert-weight TMA issue|18.112|42.368|
|Decoder warp12 actual K0 decode|21.216–22.912|45.280–47.616|
|Decoder warp12 actual K1 decode|24.096–24.480|48.736–49.088|
|Latest K0 commit end across all8 decoder warps|23.584|48.544|
|Latest K1 commit end across all8 decoder warps|24.832|50.400|
|Latest K2 commit end across all8 decoder warps|25.888|86.784|
|Activation warp6 waiting for first FC1 tile|17.760–27.520|42.304–83.840|
|First activation TMA issue|27.712|84.064|
|First asynchronous BF16 MMA issue|28.320|84.640|

At128, three decoded K tiles are committed before first activation TMA. The
first and second weight-decode intervals lie inside dispatch warp8's fetch
interval; K2 preparation overlaps the `pull_flush_fc1_ready_tail` interval
24.608–26.944. This is a decode-shape example of overlapping input readiness
work with useful dequantization.

At4096, the first two decoded K tiles are committed by50.400us; input fetching
continues and first activation TMA starts at84.064us. Decoder warp12 then waits
for a free TMEM slot50.016–85.312us (35.296us), because its finite prepared-weight
buffer is full. Its K0 decode45.280–47.616us overlaps the dispatch lane's next
source resolution46.240–47.104us and token TMA issue47.136–49.088us. K1 decode
48.736–49.088us lies within that token-TMA issue marker. These are intersecting
instrumented instruction intervals, not direct hardware bandwidth measurements.

The4096 capture is a prefill-shaped illustration, not the primary decode
performance evidence. Show the128 example first if using both in the article.

## Marker semantics and limits

- `pull_issue_tma_load_weights` belongs to token movement: the relevant source
  loads activation bytes and top-k routing weights. It is not another expert
  parameter-weight fetch. Expert weights use the dedicated weight warp's
  `weight_issue_nvfp4_and_scale_tma` markers.
- Input fetch intervals include waits; do not label their entire duration
  continuous NVLink activity or sum them with concurrent decoder durations.
- These captures do not include a host/prelaunch trace that would establish
  overlap across a separate staging launch. Their local-stage markers are
  inside the Mega kernel.
- Markers do not show that every prepared tile hides all its dequantization
  cost. TMEM capacity and stage backpressure bound look-ahead; nonzero
  weight-ready waits remain later.
- The source and traces explain the mechanism. They do not causally attribute
  the separately measured Mega-vs-split speedup to this mechanism alone.
- Archive provenance, selected-min-sync sample caveats, trace/source pin
  mismatch, screenshot rank mismatch, and kernel benchmark PDL-disabled scope
  remain as documented in `TRACE_ANALYSIS.md`.

## Suggested article passage

MegaMoE gives the same independent weight pipeline more useful work to overlap.
The kernel owns token movement as well as both GEMMs. Once routing metadata
identifies an expert tile, the weight warps can start loading and decoding it
while the dispatch warps are still fetching tokens and staging them into that
expert's input pool. Only the activation-loading role waits for the tile's data
to become ready.

We can see this in a selected128-token trace: three weight tiles are decoded
before the first activation load, while dispatch is still finishing input
fetching and readiness publication. In the larger4096-token trace, two weight
tiles are ready by about50us and the activation load starts around84us. The
decoder fills its look-ahead buffer and then waits for space. The additional
work is real, but it need not sit on the same serial path as token movement.

This is a particularly useful freedom for W4A16: its conversion work depends on
weights that are already available. W4A4's activation quantization depends on
the arriving activation values, and FC2 requantization must follow the FC1
activation result. Both designs overlap work; W4A16 gives the scheduler a
preparation stage it can move earlier in this input-dependent schedule.
