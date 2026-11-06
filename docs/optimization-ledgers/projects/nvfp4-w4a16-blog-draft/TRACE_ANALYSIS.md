# W4A16 MegaMoE trace analysis for the blog draft

This note separates observations from two selected instrumented HashInfer traces,
the current public FlashInfer implementation, and the historical uninstrumented
kernel benchmarks. It does not treat any one of these as a substitute for the others.

## Main finding

The captures show weight preparation running ahead of activation availability.
In the 128-token capture, the first three decoded K tiles have finished their
commit markers before the first activation TMA is issued. In the 4096-token
capture, the first two decoded K tiles are committed more than 33 microseconds
before the first activation TMA. The decoder then waits for a free TMEM slot:
it has exhausted its finite look-ahead buffer while the input is still pending.

This is a concrete scheduling opportunity, already present in split W4A16 MoE.
MegaMoE exploits the same independence inside a larger persistent schedule that
also owns token dispatch, both GEMMs, activation, return traffic, and combine.
Neither the traces nor the benchmark prove that dequantization is universally
free, or that all of its latency is hidden. The kernel benchmark explicitly
disables PDL; its speedups must not be attributed to PDL.

## Provenance and scope

- Access-restricted trace source: [zianglih/soul issue 12](https://github.com/zianglih/soul/issues/12).
  The parent verified that this repository is private and that unauthenticated
  issue/archive access returns 404. Do not label the raw archive public or assume
  readers of a public blog can download it. This local analysis used the archive
  already retrieved with authorized access by the parent.
- Exact archive: [Archive.zip](https://github.com/user-attachments/files/32680601/Archive.zip).
- Local archive: `evidence/soul-12-Archive.zip`.
- Archive SHA256: `ab66ba904686fc0997949bb9fd983a767ac8a27402ee9b708fdc7172c7c00dcf`.
- `selected-min-sync-rank1-128.pftrace` SHA256:
  `803fa45c20cdf2d7bdd7f5f9a909480efae675311bc4dc24fd0a639ba7450bea`.
- `selected-min-sync-rank3-4096.pftrace` SHA256:
  `ff567b6f3ae4cc1efcffb9cee2d3b0994cbd6da37381d0a43d3cf408c539ac44`.
- Public implementation/benchmark source: [FlashInfer PR 5019](https://github.com/flashinfer-ai/flashinfer/pull/5019).
- Source interpretation is pinned to public PR head
  `7ca3eb567a2400df70579d55e9bc717ea1784b0c`, downloaded to
  `evidence/flashinfer-pr5019-source/`. The archive does not include an exact
  trace capture commit, command, tactic manifest, complete shape manifest, or
  a full multi-rank trace. Do not assert that the capture equals this source pin.
- The kernel markers explicitly say **cluster (0,0,0) only**. Each trace contains
  two CTAs, twenty warp lanes per CTA, and one selected rank.
- The PR screenshots were also inspected. Their window titles show **rank2**
  for both sizes, whereas the downloadable archive contains rank1 and rank3.
  The screenshots are useful illustrations of the same role structure, not the
  exact trace samples quantified below.
- The archive's filename says `selected-min-sync`. The selection procedure and
  representativeness are not established by the archive. Do not call it a median
  sample or an unbiased selection.

| Capture | Rank | Kernel-marker envelope | Total slices including lifetimes | Scope |
|---|---:|---:|---:|---|
| 128 total tokens | 1 | 551.584 µs | 39,249 | 2 CTAs / 40 warp lanes |
| 4096 total tokens | 3 | 1,088.160 µs | 40,667 | 2 CTAs / 40 warp lanes |

These envelopes belong to instrumented selected captures, not benchmark latency.
In particular, do not compare them to the PR's 186.7535/453.7795 µs EP8 medians.
The metadata does not establish identical shapes or tactics. The captured first
FC1 task has K markers 0–23 and FC2 tasks have 0–7; this is another reason not to
silently equate the captures with the PR's H7168/I2048 benchmark configuration.

The official Perfetto processor reported no nonzero `error` or `data_loss`
statistics. There are four/five explicitly zero-duration epilogue-wait markers,
respectively; no negative/incomplete-duration slices were found. This checks
parser output, not absence of tracing overhead or global capture loss.

## Warp roles and why the pipeline can run ahead

The role mapping is visible in both traces and matches the pinned public source:

| Warp group | Warps | Role | Registers/thread after redistribution |
|---|---|---|---:|
| WG0 | 0–3 | FC1 epilogue/activation; FC2 conversion/store | 144 |
| WG1 | 4 | MMA wait/issue | 80 |
| WG1 | 5 | Packed NVFP4 weight + scale TMA | 80 |
| WG1 | 6 | BF16 activation readiness + TMA | 80 |
| WG1 | 7 | Work scheduler | 80 |
| WG2 | 8–11 | Input staging, token dispatch, and tactic-dependent output return | 64 |
| WG3–4 | 12–19 | Two groups decoding disjoint halves of a weight K tile | 96 |

Each trace has eight `register_acquire_96_to_144`, eight
`register_donate_96_to_80`, and eight `register_donate_96_to_64` ranges across its
two CTAs. The two decoder groups retain their initial allocation. The budget is
`128 × (144 + 80 + 64 + 96 + 96) = 61,440` 32-bit registers per 640-thread CTA.
This is source/trace structure, not a measured ablation of register allocation.

The data path is:

1. Warp 5 moves packed weights and scales to raw shared-memory stages.
2. Warps 12–19 read those stages, decode NVFP4 fragments into BF16 registers,
   and store decoded fragments directly to **TMEM**.
3. Warp 6 independently waits for the relevant BF16 activations, then loads them
   into their shared-memory stages.
4. Warp 4 waits for both operands and issues asynchronous BF16 MMA.
5. Warps 0–3 consume accumulator results, apply FC1 activation or convert/store
   FC2 output; decoded-weight preparation can continue for later work.

The expanded BF16 weight matrix is not materialized in global memory or shared
memory on this TMEM path. Packed weights/scales do use shared memory. Registers
hold decoded fragments before the TMEM store. This distinction matters when
describing the avoided bandwidth: do not say the pipeline uses no shared memory.

Source pointers:

- [Mega role branches, register redistribution, MMA/decode, and tail](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1239).
- [TMEM stage allocation and early raw-stage release](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L89): two accumulator stages leave three decoded K256 stages for N64, two for N128.
- [Shared split decoder and transform pipeline](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L471).
- [Split activation-TMA dependency boundary](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L1411): when PDL is enabled, only this role waits on the preceding grid.
- [Split static weight/scales can start earlier](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L1477).

The split kernel already has the critical independence. Mega reuses its decoder
and broadens the schedule; it does not invent weight/activation independence.

## A concrete early window to show in the article

All timestamps here are microseconds relative to the capture's kernel-marker
start and refer to **CTA0**. Decoder commit ends use the latest marker end across
all eight decoder warps, not one conveniently early warp.

| Event | 128-token capture | 4096-token capture |
|---|---:|---:|
| First activation-dispatch wait starts | 17.760 | 42.304 |
| First weight/scales TMA issue | 18.112 | 42.368 |
| All decoder warps finish first K0 commit marker | 23.584 | 48.544 |
| MMA warp's first weight-ready wait returns | 23.712 | 48.608 |
| All decoder warps finish first K1 commit marker | 24.832 | 50.400 |
| All decoder warps finish first K2 commit marker | 25.888 | 86.784 |
| Activation-dispatch wait ends | 27.520 | 83.840 |
| First activation TMA issue | 27.712 | 84.064 |
| First BF16 MMA issue | 28.320 | 84.640 |

In the 128-token capture, K0/K1/K2 are committed while the activation role is
still waiting. In the 4096-token capture, K0/K1 are committed early, then decoder
warp 12's `transform_wait_tmem_slot_free(payload=2)` lasts **35.296 µs**, from
50.016 to 85.312 µs. The corresponding MMA activation-ready wait lasts **35.968
µs**, from 48.640 to 84.608 µs. This is a particularly clear example of finite
buffering/backpressure after useful weight preparation has already run ahead.

These observations are consistent with three versus two decoded stages; the
current source associates those stage counts with N64 versus N128. Without the
capture tactic manifest, present the stage-count behavior as observed and the
exact N-tile selection as an inference, not recovered configuration.

There is also repeated overlap once the pipeline is moving. For example:

- At 56.352–56.544 µs in the 128 capture, CTA0 warp 4's MMA issue for K5 overlaps
  warp 12's decode of K6.
- At 87.072–87.264 µs in the 4096 capture, CTA0 warp 4's MMA issue for K2 overlaps
  warp 12's decode of K3.
- At 167.744–168.672 µs in the 4096 capture, CTA0 warp 0's FC1 compute/store
  overlaps warp 12's load/decode work for a later tile.

The source explicitly labels `mma_issue_k_tile` as asynchronous **issue, not
completion**. These are intersecting instrumented code intervals, not a tensor
core utilization measurement. Do not add their durations together as latency.

## Small versus large capture: different work and return paths

| Observation across the two captured CTAs | 128 | 4096 |
|---|---:|---:|
| Weight-load task ranges | 72 | 66 |
| Weight/scales TMA issue ranges | 960 | 976 |
| Activation TMA issue ranges | 960 | 976 |
| MMA K-tile issue ranges, leader CTA role | 480 | 488 |
| Decoder load/decode ranges across 16 decoder warps | 7,680 | 7,808 |
| Decoder store/commit ranges across 16 decoder warps | 7,680 | 7,808 |
| FC1 compute/store ranges across epilogue warps | 96 | 112 |
| FC2 convert/store ranges across epilogue warps | 192 | 152 |
| Explicit dispatch output-return issue ranges | 0 | 102 |
| Actual combine-worker ranges | 16 | 336 |

Counts are instrumented ranges, often duplicated across cooperating warp lanes.
For example, 7,680 decoder ranges are not 7,680 independent GEMMs. Task counts
in one selected cluster do not scale with total tokens or reconstruct global work.

The 128-token CTA0 task stream is `6 FC1 → 12 FC2 → 6 FC1 → 12 FC2`, showing the
persistent grouped FC1/FC2 schedule. Its dispatch warp 8 enters
`cta_wait_all_roles_finished` after initial token exchange and remains there
for **509.504 µs**. There are no `return_wait_and_push_outputs` or
`return_stage_and_issue_output` ranges. Together with the FC2 epilogue markers,
this is consistent with the epilogue-return tactic. Absence of a private marker
alone would not prove a tactic; this interpretation uses the public return-path
structure as supporting evidence.

The 4096-token CTA0 stream is `14 FC1 → 19 FC2`. The dispatch role fetches inputs
and then participates in output return. Across captured dispatch lanes,
`return_wait_and_push_outputs` spans 113.312–1032.096 µs, while actual
`return_stage_and_issue_output` ranges occur from 704.736–1019.584 µs. The long
return interval includes waiting for FC2 experts; it is not 918 µs of continuous
NVLink transmission. This trace directly shows reuse of dispatch warps for output
return while the other roles progress through GEMMs and epilogues.

At the end, dispatch warps drain peer returns. Other retired roles join ordered
top-k reduction, while the dispatch group handles cleanup. In the 128 capture,
actual combine markers occur only on decoder warps 12–19, 16 ranges across both
CTAs, within 550.080–551.104 µs. In the 4096 capture, combine uses warps 0–7 and
12–19, 336 ranges, within 1061.600–1087.872 µs. This matches the current source's
work assignment: decoder groups own the first reduction strips, with other
retired roles available when there is more work. Combine preparation can happen
before the final MMA/tail drain, but reads of remote output wait for return
completion. That last preparation detail comes from source, not a separate
timed marker in these captures.

Source pointers:

- [FC2 epilogue direct peer-output routing](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py#L261).
- [Reduction worker ownership/preparation](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1035).
- [Decoder retirement, common tail, peer drain, and reduction](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1609).
- [Separate drain and cleanup contract](https://github.com/zianglih/flashinfer/blob/7ca3eb567a2400df70579d55e9bc717ea1784b0c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/token_comm.py#L13).

## Wait ranges are useful evidence, not an overhead decomposition

Selected CTA0 per-lane marker distributions:

| Lane / range | 128 count | 128 median / max µs | 4096 count | 4096 median / max µs |
|---|---:|---:|---:|---:|
| Warp4 weight-ready wait | 480 | 0.704 / 5.824 | 488 | 1.440 / 6.112 |
| Warp4 activation-ready wait | 480 | 0.064 / 4.576 | 488 | 0.064 / 35.968 |
| Warp12 raw-TMA-ready wait | 480 | 0.032 / 3.232 | 488 | 0.032 / 2.560 |
| Warp12 TMEM-slot-free wait | 480 | 0.064 / 2.592 | 488 | 0.192 / 35.296 |
| Warp12 load/decode | 480 | 0.320 / 1.696 | 488 | 0.512 / 2.336 |
| Warp12 store/commit | 480 | 0.256 / 0.832 | 488 | 0.480 / 1.120 |

Nonzero weight-ready waits remain. Their durations mix pipeline availability,
instruction execution, synchronization, and instrumentation effects; they are
not an isolated dequantization tax. Conversely, short waits and visible overlap
are not proof of zero cost. Register pressure, TMEM capacity, raw/activation
stage occupancy, and instruction issue all constrain look-ahead.

No concurrent event durations are summed in this analysis. The helper reports
counts, marker distributions, first/last bounds, and specific timestamped
intersections. First/last bounds are explicitly envelopes, not exclusive work.

## Keep the measured benchmark claim separate

The historical [PR 5019 performance section](https://github.com/flashinfer-ai/flashinfer/pull/5019)
reports kernel revision `44a04fd247cf2f93bee4052bf439bc93f32c7f8c` plus its
benchmark extension, before tracing changes. It uses B300, CUDA 13.2,
`nvcr.io/nvidia/pytorch:26.05-py3`, H7168/I2048/E256/top-k8, and **PDL disabled**.
Timing is pooled median of 200 untrimmed rank-MAX first-to-last GPU activity
spans, including gaps, across two sweeps. Forward includes staging, copies,
communication, compute, combine, and W4A4 quantization/requantization. Routing,
weight preparation, compilation, tuning, capture, and L2 flush are untimed.

| Decode tokens 4–512, geometric speedup of Mega W4A16 | Over Split W4A16 | Over Mega W4A4 |
|---|---:|---:|
| EP4 | 1.1259× | 1.0153× |
| EP8 | 1.2265× | 1.1208× |

Near-one ratios should be called near parity. EP4 Mega W4A16 loses to Mega W4A4
at several larger decode points; W4A4 is substantially faster on measured
prefill shapes. The experiment uses fixed arm order and different native AUTO
candidate timing methods for the two Mega precisions. There is no accuracy
parity or causal attribution claim. The traces explain the scheduling structure;
they do not apportion these speedups among overlap, fusion, communication, or
register redistribution.

These are comparisons with the contemporaneous distributed Split baseline in
PR 5019, not a current-split comparison. Do not splice in PR 5319's separate
one-GPU simulated-EP8/PDL-on split measurements or use the resulting ratio as a
matched benchmark. The blog's latest split-kernel evidence should cite the
separately audited historical head/unfused comparison in PR 5319.

## Suggested blog prose

### Start with the split-kernel insight

Weight dequantization has an unusual advantage: it does not need the activations.
Once we know which expert and tile to execute, we can load its packed weights,
decode them, and prepare the next matrix multiply while the activations are
still on their way. A split W4A16 MoE kernel already has substantial room for
this overlap. Weight loading, decoding, activation loading, MMA, and the
epilogue have different dependencies, so they need not march in lockstep.

### Explain what MegaMoE adds

MegaMoE gives that pipeline a larger schedule to work with. One persistent
kernel owns input staging, token dispatch, FC1, activation, FC2, output return,
and combine. Five warp groups divide the work: one handles the epilogue, one
handles MMA/loading/scheduling, one handles token movement, and two decode
weights directly into TMEM. The low-register control and dispatch groups donate
registers to the epilogue. When the GEMMs finish, retired compute roles help with
the final reduction. The point is to do the preparation when its inputs are
ready, instead of adding every operation to a single sequential path.

### Let one trace moment explain the idea

The 4096-token trace makes the ordering visible. In the selected CTA, the first
two decoded weight tiles are committed by roughly 50 µs, while the activation
load does not start until roughly 84 µs. The decoder fills its look-ahead buffer
and waits for a TMEM slot. This is the opportunity W4A16 gives us: weight
preparation can get ahead of the data dependency that gates the matrix multiply.
The smaller trace shows the same effect, with three weight tiles prepared before
the first activation load. These are selected instrumented traces; the separate
kernel benchmarks measure the resulting performance.

### Optional transition to the measured results

That schedule makes W4A16 competitive with W4A4 at decode shapes. In our
historical B300 kernel benchmark, Mega W4A16 is 1.23× faster than its contemporaneous distributed Split W4A16 baseline and
1.12× faster than Mega W4A4 by geometric mean over 4–512 global tokens at EP8.
At EP4, the same comparison is closer to parity with W4A4, and W4A4 remains
substantially faster at prefill shapes. The tradeoff follows the workload:
independent preparation and reduced weight traffic are valuable when the
arithmetic itself is not the dominant cost.

## Reproduce the trace analysis

The saved official binary is Perfetto `v58.2-add693d8b`, RPC API 14.
Binary SHA256:
`d29864d1ba3b36855527bb1b0ca3aa7f703cdce338b9680bb922c5c151b358fa`.
The launcher came from `https://get.perfetto.dev/trace_processor`; analysis uses
the copied project-local executable directly. The official launcher initially
cached its download under the normal Perfetto user cache before it was copied.

```sh
cd /Users/ziangli/playground/projects/nvfp4-w4a16-blog-draft
tools/trace_processor_shell export sqlite \
  -o evidence/soul-12-traces/128.sqlite \
  evidence/soul-12-traces/selected-min-sync-rank1-128.pftrace
tools/trace_processor_shell export sqlite \
  -o evidence/soul-12-traces/4096.sqlite \
  evidence/soul-12-traces/selected-min-sync-rank3-4096.pftrace
python3 analyze_traces.py
```

Derived files are `128-analysis.json`, `4096-analysis.json`,
`128-event-summary.csv`, and `4096-event-summary.csv` in
`evidence/soul-12-traces/`. They preserve lane-count semantics and omit summed
parallel durations. Source downloads and SQLite exports remain project-local.
