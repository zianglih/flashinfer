# Shared CLC flag: baseline and retention audit

Current control inspected: `9b4721b08057d0a488c1f0236467acb75c48cd00`. This audit has not run GPUs or edited production source.

## Historical selection signal

The earlier seven-token full-search control selected matching FC1/FC2 flags in 57/84 affected cells. All 28 K3 cells already fit the shared policy. Mixed selections occur in 17/28 V3 cells and 10/28 V4.1 cells. This identifies cells to inspect; it does not measure the shared-policy penalty. All-CLC results cannot stand in for a shared flag, because the shared flag restores static/static tactics.

| Model | Backend | Historical mixed FC1/FC2 selections |
|---|---|---|
| kimi-k3 | CuteDSL MXFP8 | None |
| kimi-k3 | CuteDSL MXFP4x8 | None |
| kimi-k3 | CuteDSL W4A4 | None |
| kimi-k3 | CuteDSL PER-TOKEN | None |
| v3 | CuteDSL MXFP8 | T64: static/CLC, T128: static/CLC, T16384: CLC/static |
| v3 | CuteDSL MXFP4x8 | T4: static/CLC, T32: static/CLC, T64: static/CLC, T128: static/CLC, T4096: CLC/static, T16384: CLC/static |
| v3 | CuteDSL W4A4 | T4: static/CLC, T64: static/CLC, T512: static/CLC, T4096: CLC/static |
| v3 | CuteDSL PER-TOKEN | T32: static/CLC, T64: static/CLC, T128: static/CLC, T512: static/CLC |
| v41-flash | CuteDSL MXFP8 | T4: static/CLC, T4096: CLC/static, T16384: CLC/static |
| v41-flash | CuteDSL MXFP4x8 | T4: static/CLC, T4096: CLC/static |
| v41-flash | CuteDSL W4A4 | T4: static/CLC, T4096: CLC/static |
| v41-flash | CuteDSL PER-TOKEN | T4: static/CLC, T512: CLC/static, T4096: CLC/static |

## Fresh comparison contract

- Full source at the current retained commit versus the same source with only the shared scheduler policy. Fresh native AUTO for each arm; do not load historical winners as the primary baseline.
- One shared boolean gives 360 raw choices versus 720 independent choices. It must map exactly to the full set with equal flags; no new queue, stage or scheduler axis. Kernel launch and low-level fallback logic stay unchanged.
- Run all 13 points: 1,2,4,8,16,32,64,128,256,512,4096,8192,16384. The old diagnostic omitted 1,2,8,16,256,8192; notably it lacks three retained decode points and the middle prefill point.
- Public benchmark, V3 EP8 / V4.1 EP4 / K3 EP8, both families, unfused finalize, PDL on. NV includes initial quantization; MX does not. Standard NV, per-token NV, MXFP8, MXFP4x8 are affected; W4A16 is an unchanged control.
- Keep each model/family A-B-B-A sequence on one GPU, 10 warmups / 100 cold-L2 graph CUPTI samples per cell. Bind exact source, observer, cache and routing hashes. Persistent native cache reuse must not reuse AUTO selections.
- Preserve every observed median and repeat. Paired ratio is sqrt((A1*A2)/(B1*B2)); then geometric means over decode 4–512, prefill 4096/8192/16384 and all retained points. Only 1/2 are excluded. Do not pool samples across source arms or use minima.
- Review both repeat directions, per-cell regressions and chosen tactics. No inherited universal acceptance threshold. Small prefill tradeoffs may be acceptable, but a global geomean must not hide repeatable decode losses in one model/dtype.
- Record actual selected shared flag and physical scheduling fallbacks. A shared requested flag does not imply identical physical work grids in FC1 and FC2. Do not mistake legal one-wave fallback for an independent tuning axis.
- No TRT rerun is required for this scheduler-policy comparison. Old published TRT ratios remain attributed to their measured source, rather than being updated from this candidate without matching evidence.

## Outstanding review

Policy diff and benchmark harness reviewed at the hashes in `source-and-harness-review.json`. The 360 choices exactly map to the equal-flag subset of720, all8 Rubin parameter dictionaries and23 W4A16 tactics are unchanged, and production edits are limited to the tuner plus existing tests. One observer parser-index bug was found and fixed before launch. Fresh native setup and separate cache-only ABBA measurement are correctly separated. GPU results, frozen run configuration, and summarizer/raw-result review remain pending.
