# Fixed-winner payload geometry audit

R3 source/winner/route evidence covers all112 affected cells. The numerical quantities below are analytical issue/extent counts, not measured HBM traffic. R4 changes scale-completion relay, retaining this payload geometry.

| Model / topology | Tokens | Mode | R3 speedup | N / CTA | Copied / dynamic rows | Gather4 commands per CTA/stage | Live-row duplication |
|---|---:|---|---:|---|---:|---:|---:|
| kimi-k3 EP8 | 8 | MXFP4x8 | -59.8% | 16 / 2 | 1.00 | 2 | 1.00 |
| kimi-k3 EP8 | 4096 | MXFP4x8 | -68.3% | 128 / 2 | 1.55 | 16 | 1.27 |
| kimi-k3 EP8 | 16384 | MXFP4x8 | -68.2% | 128 / 2 | 1.18 | 16 | 1.04 |
| nemo3-ultra EP8 | 16384 | MXFP4x8 | -49.7% | 256 / 2 | 1.19 | 32 | 1.04 |
| v3 EP8 | 8 | MXFP8 | +3.3% | 32 / 1 | 2.00 | 16 | 1.00 |
| v3 EP8 | 8 | MXFP4x8 | -66.1% | 32 / 2 | 2.00 | 4 | 1.00 |
| v3 EP8 | 16384 | MXFP8 | -51.3% | 256 / 2 | 1.19 | 32 | 1.04 |
| v3 EP8 | 16384 | MXFP4x8 | -65.7% | 128 / 2 | 1.10 | 16 | 1.03 |
| kimi-k3 TP8 | 8 | MXFP4x8 | -2.9% | 16 / 1 | 1.00 | 4 | 1.00 |
| kimi-k3 TP8 | 4096 | MXFP4x8 | -53.4% | 128 / 2 | 1.60 | 16 | 1.27 |
| kimi-k3 TP8 | 16384 | MXFP4x8 | -51.4% | 128 / 2 | 1.18 | 16 | 1.04 |
| nemo3-ultra TP8 | 16384 | MXFP4x8 | -4.2% | 256 / 1 | 1.17 | 64 | 1.00 |

## What the counts distinguish

- `route_tile/CTAgroup` payload rows are issued per CTA, while MMA consumes `round_up(valid,16)/CTAgroup` rows. The CTA row origin uses the dynamic extent. Thus tail copies may include OOB zero fill and, for two CTAs, duplicate real rows beyond each CTA's MMA-owned half. Full stage storage strides stay static. Existing regular TMA has the same fixed copied extent, but expresses it with one activation-payload command per CTA/stage instead of many512-byte Gather4 commands.
- K3 EP decode has no excess copied/dynamic rows, yet its two-CTA winner regresses59.8%. K3 TP decode uses one CTA and regresses2.9%. Excess-row removal cannot explain or close that difference.
- N3U TP prefill uses one CTA and64 Gather4 commands per CTA/stage, with only4.2% regression. Its EP prefill uses two CTAs and32 commands per CTA/stage but loses49.7%. This is not a matched geometry experiment: TP also reduces output-channel work and changes the grid. It nevertheless makes two-CTA coordination/latency hiding a more informative discriminator than raw command count alone.
- At K3 EP16384, copied/dynamic rows are1.18x, while throughput loses68.2%. At V3 EP16384 MXFP4x8 they are1.10x while throughput loses65.7%. Trimming tail payload can reduce some issue work, particularly4096-token rows, but cannot account for most of the persistent large-prefill loss.
- For every logical channel tile, direct gather rereads original activation rows. The existing kernel already reuses the activation across its internal channel_tiles. The counts include the outer channel-tile repeats; they do not assume DRAM services each repeat, because cache reuse and OOB fill matter.

## Next diagnostic and bounded policy choice

The next capture is K3 EP8 MXFP4x8 T4096 FC1, retained regular TMA versus R4 Gather4, identical frozen winners/routes. Inspect achieved issue/active-warps, MIO/short-scoreboard/barrier stalls, TMA issue and memory traffic. Do not derive a retention conclusion from instrumented time.

Do not introduce a dtype/model-specific selector or a second tuning axis from these correlations. The already-proposed R5 dedicated-warpgroup cp.async128 payload is a useful single general-purpose experiment: preserve the same route geometry, MMA/scheduler and shared-stage reuse while replacing Gather4 payload issuance with coalesced16-byte asynchronous vectors and one combined payload+scale completion. It tests whether the two-CTA TMA issue/completion path is the bottleneck. Retain only if exactness and end-to-end evidence justify it; historical cp.async results mean success is not guaranteed.

A separate dynamic-prefix Gather4 policy would have to change the weight producer's expected transaction bytes to the same runtime rounded extent and preserve static shared strides; skipping commands alone would deadlock the full barrier. It also risks reducing four-warp issue participation unless task distribution is redesigned. Given the decode/full-tile counterexamples, this is lower priority than the bounded loader-path diagnosis.

## Source/evidence boundaries

R4 `moe_swap_ab_kernel.py`: physical/copy rows1621–1633; expected payload bytes2589–2598; dynamic two-CTA origin3038–3046; flattened Gather4 commands3116–3158; dynamic MMA valid handling3331 onward. These line pointers refer to frozenR4; the active source copy may now contain R5. R3 kernel SHA `c259b6cb4b01037def6f1b8d4be09221f7abc36dd76e910660ced0179daebf75`; R4 SHA `6fae1558326e72aa8beab25520c9e7be1734e03b6ff39d190025f2445d09ed2a`.

`geometry.json` pins all15 source result files and exact winner/route identities; `cells.csv` contains all112 cells. Formulas use512-byte Gather4 payload commands, SF16/SF32 scale copies excluded. Actual global-read duplication is bounded analytically; reported issued bytes include zero-filled rows and therefore must not be labeled DRAM bytes.


## Profiling interruption

The source-bound retained/R4 FC1 NCU controller launched on the released GPU7, but the next managed status call reported that `fi-moe-descriptor-recover-1028` no longer existed in namespace `ziangli` on C3. Capture completion is unknown. No counter or instrumented-duration conclusion is claimed. The controller and any partial output are on persistent `/data/.../fc1-gather-20261028/r4/ncu-fc1`; `../ncu-fc1/local-status.json` records the launch and failure boundary.


The replacement-box retry also produced no counters: NCU exceeded its360-second startup limit before the retained/control capture completed; R4 candidate profiling never started. The process group was cleaned up and GPU7 released. See [failure receipt](../ncu-fc1/resume-01/RESULT.md). The geometry-based hypothesis remains unconfirmed by counters; use the source-paired R5b/R6 loader-path screen to test it.
