# W4 output-store acquire: sampled iKET diagnostic

The sampled traces do not expose a large output-store acquisition bubble. The acquire scopes are mostly near the 32 ns timestamp granularity, and moving the wait would retain its instruction cost. No late-acquire or raw-preload implementation is proposed from this evidence.

- Retained source: `b52e4e09649dc180fc7583a25ec35ff55f04654d`; all 514 source files verified. W4 kernel SHA `de042712ac4fcab0f14eb5f870824416f65dce15e2243198b28ffb4226ac0d58`.
- Diagnostic source: `eeba263cba4db592e0a40e993c95c6cc1edea2ba4a951c2c2e3abdb08590333f`. Stripping markers and empty marker conditionals reproduces the retained module AST exactly. Only the existing output `producer_acquire` sites received nested markers; no algorithm, synchronization, or stage count changed.
- Workloads: K3 EP8 and V41F TP4, 4096 tokens, frozen native two-CTA N128/K256 tactics and routes. Both points execute gated FC1. Two resident complete clusters were captured independently per workload.
- Actual NativeDump CUBIN and loaded-function checks passed before both tracker and recorder workloads: 8 guarded processes, REG96, STACK0, LOCAL0, no LDL/STL, 640 threads, original control80/gather64/epilogue144 register policy. The instrumenter adds 1024 static shared bytes; this is not an unchanged-SMEM claim.
- All 20 raw launches remain in the evidence. The summary selects only the final cold-L2 `graph_exec_2:3:0` from each of the four captures. No retuning, clock changes, or E2E speedup measurement was performed.

| Model | Scope | Count | Mean ns | Median ns | P95 ns | Max ns |
|---|---|---:|---:|---:|---:|---:|
| ep-kimi-k3-w4a16 | epi_cstore_acquire | 366 | 52.28 | 32 | 128 | 160 |
| ep-kimi-k3-w4a16 | transform_wait_tmem_slot_free | 14784 | 29.81 | 32 | 64 | 192 |
| ep-kimi-k3-w4a16 | transform_wait_raw_tma_ready | 14784 | 31.48 | 32 | 32 | 2784 |
| ep-kimi-k3-w4a16 | transform_load_decode_nvfp4 | 14784 | 325.96 | 320 | 416 | 544 |
| ep-kimi-k3-w4a16 | epi_body | 528 | 3878.00 | 4160 | 5792 | 6368 |
| tp-v41-flash-w4a16 | epi_cstore_acquire | 236 | 42.71 | 32 | 96 | 160 |
| tp-v41-flash-w4a16 | transform_wait_tmem_slot_free | 15360 | 29.77 | 32 | 64 | 96 |
| tp-v41-flash-w4a16 | transform_wait_raw_tma_ready | 15360 | 30.69 | 32 | 32 | 2880 |
| tp-v41-flash-w4a16 | transform_load_decode_nvfp4 | 15360 | 311.86 | 320 | 384 | 544 |
| tp-v41-flash-w4a16 | epi_body | 384 | 1895.67 | 1728 | 2560 | 2656 |

| Model | Cluster / CTA | Tiles | Body ns/tile | Acquire sum ns/tile | Instrumented fraction |
|---|---|---:|---:|---:|---:|
| ep-kimi-k3-w4a16 | 0 / 0 | 33 | 3895.27 | 152.24 | 3.91% |
| ep-kimi-k3-w4a16 | 0 / 1 | 33 | 3786.67 | 144.48 | 3.82% |
| ep-kimi-k3-w4a16 | 1 / 2 | 33 | 4022.30 | 156.12 | 3.88% |
| ep-kimi-k3-w4a16 | 1 / 3 | 33 | 3818.67 | 127.03 | 3.33% |
| tp-v41-flash-w4a16 | 0 / 0 | 24 | 1910.67 | 118.67 | 6.21% |
| tp-v41-flash-w4a16 | 0 / 1 | 24 | 1780.00 | 85.33 | 4.79% |
| tp-v41-flash-w4a16 | 1 / 2 | 24 | 2048.00 | 110.67 | 5.40% |
| tp-v41-flash-w4a16 | 1 / 3 | 24 | 1864.00 | 105.33 | 5.65% |

The per-tile fraction uses only the issuing epilogue warp's nested acquire scopes divided by that same warp's epilogue-body spans. It includes marker and instruction overhead, excludes the following all-writer join, and is not removable stall time or an E2E speedup estimate. Concurrent warp spans are not summed.

The transformed-weight slot wait remains near the timestamp floor (median 32 ns; P95 64 ns). It does not support moving packed-A/SF loads across that wait now. The prior SF-only preload experiment was already neutral and rejected; its source and timing boundary are indexed in `../w4-late-store-acquire-audit/HISTORY.md` and `../CLOSED_LEADS.md`.

The previous isolated non-descriptor FC2 late-acquire trial was also neutral/rejected. The descriptor-family source03→source04 result moved both FC1 and FC2 and cannot establish a gain for current non-descriptor FC1. See the same history audit for the complete evidence, including negative rows.

`analyze.py` rechecks the evidence manifest, all source hashes, profiler process guards, frozen tactic/route receipts, and raw trace launch selection. `summary.json`, `all-launch-ranges.csv`, and `selected-ranges.csv` preserve aggregate and raw range data. `fetch-receipt.json` records all 76 fetched files and verifies GPUs 6/7 idle. The pre-launch worker syntax failure is preserved under `evidence/failed-worker-syntax`; no workload ran during that failed attempt.
