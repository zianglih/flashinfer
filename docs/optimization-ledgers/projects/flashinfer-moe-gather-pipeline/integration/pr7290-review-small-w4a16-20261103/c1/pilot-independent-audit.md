# B200 V3 EP8 / 4-token pilot: independent audit

The default/non-swap arm reproduces the reviewer-scale regression on this workload: **+6.56% latency** (equivalently **−6.16% speedup**). This is a fresh same-GPU before/OFF/ON/ON/OFF/before pilot; the full model/topology/token matrix is still running.

| Arm | Phase medians (µs) | Geometric mean (µs) | Speedup vs before | Repeat spread |
|---|---|---:|---:|---:|
| before | 50.3040, 50.3680 | 50.3360 | +0.0000% | 0.1272% |
| off | 53.6160, 53.6640 | 53.6400 | -6.1596% | 0.0895% |
| on | 51.6640, 51.6645 | 51.6642 | -2.5709% | 0.0010% |

## Where the added time appears

The baseline `other_1` kernel is `MoeW4A16PermuteKernel`, the standalone activation preparation. It is absent from both current arms. Timeline intervals are joined by CUPTI launch correlation, sorted by GPU start time, and assigned only their extension beyond the preceding covered timeline. This accounts for PDL overlap; kernel durations are not summed.

The following are arithmetic means over all 200 samples per arm, so contribution deltas sum exactly to the arithmetic-mean end-to-end delta. They are a separate diagnostic statistic from the geometric mean of phase medians above.

| Timeline contribution | Before (µs) | OFF (µs) | OFF − before (µs) | ON (µs) | ON − before (µs) |
|---|---:|---:|---:|---:|---:|
| route_topk | 2.7283 | 2.7463 | +0.0179 | 2.7365 | +0.0082 |
| route_sort | 2.1841 | 2.2424 | +0.0583 | 2.3120 | +0.1278 |
| prepare | 3.6464 | 0.0000 | -3.6464 | 0.0000 | -3.6464 |
| fc1 | 27.5262 | 35.4980 | +7.9718 | 33.6888 | +6.1627 |
| fc2 | 11.5830 | 10.6851 | -0.8979 | 10.6277 | -0.9553 |
| combine | 2.7435 | 2.4643 | -0.2792 | 2.3923 | -0.3512 |
| End to end | 50.4116 | 53.6361 | +3.2246 | 51.7574 | +1.3458 |

All inter-kernel uncovered gaps are zero in this replay. OFF adds 7.972µs of FC1 timeline extension while eliminating 3.646µs of standalone prepare contribution, leaving a 4.325µs increase across those stages. Improved FC2/combine contributions offset part of it. This identifies the FC1 portion of the pipeline as the visible source of added critical-path time; it does not establish an instruction, synchronization, register, or memory-load mechanism. Shorter overlapping FC2 duration alone is not proof of faster FC2 computation.

## Controls and limits

- Independently verified all 600 raw CUPTI sample spans, launch-to-kernel correlations, phase result/log hashes, source heads, benchmark hashes, fresh route identity, cache hits, no fresh profiling, and current resolved FC1/FC2 configurations. W4A16 consumes BF16 directly; there is no initial activation quantizer in timing.
- Before is `002529e17`, with unchanged published benchmark overlay `8078d09b`; current is `14a338579`. Both execute unfused MoE.
- Before and OFF share exactly the same explicit two-CTA tactic: FC1/FC2 tile `(128,8,256)`, cluster `(2,1)`, raster M. ON uses its recorded one-CTA `(1,1)` winner. Thus before→OFF is a matched-layout/tactic comparison; OFF→ON cannot isolate layout changes. B300-origin choices are replayed on B200; no native B200 optimality claim.
- All 42 sampled NVML records inside the measurement windows (7 per phase, at least one in each sample quartile) show SM1965MHz, memory3996MHz,36°C, and event reasons0. This is coarse telemetry, not per-kernel clock measurement.
- Before and OFF repeat spreads are only0.127% and0.090%, materially smaller than the observed loss. The loss is reproduced within this balanced pilot; broader conclusions await the full eight-job run.
- No additional GPU profiling, retuning, source edits, or assertion relaxation were performed. Detailed reconstruction is in `pilot-independent-audit.json` and `audit_pilot_components.py`.
