# W4 independent scale duplication: full18-cell screen

Retained by parent for instruction simplicity and decode improvement, accepting the documented stable sub1% prefill losses. Committed and pushed as `1e4b127a0901282bda5faec70ef6d5a19c835943`. Candidate `d5105227`, based on retained `b52e4e09`, changes only `moe_w4a16_utils.py` (8+/6−). Each independent16-value scale conversion replaces a two-PRMT low-byte duplication with one PRMT; no floating-point, scope/lifetime, pipeline, role, stage, layout or tactic change.

All39 existing exact/graph cases passed. Exhaustive task-local helper checks cover every scale byte and nibble at all16 positions, four upper24-bit patterns, both sources and both direct/fallback branches. All four262,144-value output streams are bit-identical, including NaNs/signed zeros; finite values also match an independent CPU oracle. Fallback is forced under CUDA13.2, not an older-toolkit claim. Ten native paired codegen captures remove8 PRMT each, preserve REG96/128 and zeroLOCAL;9have−8 non-NOP, N3UTP16KFC2−7.

Full18-cell CAAC uses fresh paired controls on the same physical GPU, frozen native winners/routes,100 strict CUPTI samples per phase, cold-L2 CUDA graph replay,10 warmups, stock clocks and read-only NVML. The W4 metric is `100*((C1+C2)/(A1+A2)-1)`, using each phase median; group aggregates are geometric means of those ratios. No retune, sanitizer or baseline replacement. Raw activity spans were independently recomputed for all7,200 samples; all493 evidence hashes,514source bindings and128 loaded MoE LOCAL0 functions passed.

| Group | Cells | Speedup |
|---|---:|---:|
| all | 18 | +0.261% |
| decode | 8 | +0.519% |
| prefill | 10 | +0.056% |
| spread_at_most_1pct | 14 | +0.128% |
| prefill_spread_at_most_1pct | 6 | -0.391% |

The low-spread subset is a sensitivity diagnostic only; all18 rows are retained. The full prefill aggregate is nearly neutral, but it includes variable positive rows. Tight V3EP4K/V41FEP4K/V3TP4K losses remain. Observed SM clocks range1260–2032MHz with reasons0/4; no windows are missing. No fixed-clock claim.

| Job | Tokens | C µs | A µs | Speedup | C/A spread | FC1 Δµs | FC2 Δµs | FC2-after-FC1 Δµs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ep-kimi-k3-w4a16 | 8 | 83.961 | 83.777 | +0.220% | 0.135/0.077% | -0.144 | +0.304 | +0.112 |
| ep-kimi-k3-w4a16 | 4096 | 560.918 | 558.686 | +0.399% | 0.206/7.244% | -1.015 | -1.464 | -1.264 |
| ep-kimi-k3-w4a16 | 16384 | 1985.311 | 1989.495 | -0.210% | 0.019/0.396% | +7.456 | -3.328 | -3.360 |
| ep-nemo3-ultra-w4a16 | 8 | 51.161 | 51.120 | +0.079% | 0.032/0.062% | +0.104 | -0.047 | -0.208 |
| ep-nemo3-ultra-w4a16 | 4096 | 395.413 | 395.829 | -0.105% | 0.381/0.032% | +0.352 | -0.176 | -0.192 |
| ep-v3-w4a16 | 8 | 69.121 | 69.241 | -0.173% | 0.000/0.024% | +0.504 | +0.032 | -0.456 |
| ep-v3-w4a16 | 4096 | 283.763 | 286.115 | -0.822% | 0.101/0.023% | +3.360 | -0.856 | -1.056 |
| ep-v41-flash-w4a16 | 8 | 51.249 | 50.321 | +1.845% | 0.063/0.064% | -0.608 | +1.384 | -0.367 |
| ep-v41-flash-w4a16 | 4096 | 444.101 | 446.541 | -0.546% | 0.036/0.377% | +3.328 | -0.048 | -0.928 |
| ep-v41-flash-w4a16 | 16384 | 1525.986 | 1503.025 | +1.528% | 1.239/2.785% | -14.472 | -5.993 | -6.016 |
| tp-kimi-k3-w4a16 | 8 | 89.001 | 88.249 | +0.852% | 0.055/0.454% | -0.160 | -0.639 | -0.623 |
| tp-kimi-k3-w4a16 | 4096 | 697.253 | 689.958 | +1.057% | 4.318/2.270% | -1.895 | -3.304 | -3.352 |
| tp-nemo3-ultra-w4a16 | 8 | 65.936 | 65.400 | +0.820% | 0.049/0.025% | -0.032 | -0.400 | -0.464 |
| tp-nemo3-ultra-w4a16 | 4096 | 541.397 | 542.844 | -0.267% | 0.095/0.481% | +1.016 | -0.304 | +0.392 |
| tp-v3-w4a16 | 8 | 57.280 | 57.041 | +0.420% | 0.448/0.001% | -0.200 | -0.368 | -0.120 |
| tp-v3-w4a16 | 4096 | 476.180 | 478.067 | -0.395% | 0.128/0.147% | +1.648 | -0.208 | +0.361 |
| tp-v41-flash-w4a16 | 8 | 63.929 | 63.864 | +0.101% | 0.026/0.024% | +0.272 | +0.056 | -0.336 |
| tp-v41-flash-w4a16 | 4096 | 554.277 | 554.597 | -0.058% | 1.853/1.911% | +1.336 | -1.872 | -0.975 |

Component columns are candidate−control. FC1/FC2 durations overlap under PDL and must not be summed to recover E2E; `FC2-after-FC1` measures their completion separation. All are medians of source-bound CUPTI activity spans, averaged across each arm’s two phases.

| Job | Tokens | C1 µs | A1 µs | A2 µs | C2 µs |
|---|---:|---:|---:|---:|---:|
| ep-kimi-k3-w4a16 | 8 | 83.904 | 83.809 | 83.745 | 84.017 |
| ep-kimi-k3-w4a16 | 4096 | 560.342 | 539.158 | 578.215 | 561.494 |
| ep-kimi-k3-w4a16 | 16384 | 1985.127 | 1985.559 | 1993.431 | 1985.495 |
| ep-nemo3-ultra-w4a16 | 8 | 51.153 | 51.136 | 51.104 | 51.169 |
| ep-nemo3-ultra-w4a16 | 4096 | 396.165 | 395.765 | 395.892 | 394.661 |
| ep-v3-w4a16 | 8 | 69.121 | 69.249 | 69.233 | 69.121 |
| ep-v3-w4a16 | 4096 | 283.907 | 286.083 | 286.147 | 283.620 |
| ep-v41-flash-w4a16 | 8 | 51.233 | 50.305 | 50.337 | 51.265 |
| ep-v41-flash-w4a16 | 4096 | 444.181 | 447.381 | 445.701 | 444.021 |
| ep-v41-flash-w4a16 | 16384 | 1535.378 | 1482.384 | 1523.665 | 1516.593 |
| tp-kimi-k3-w4a16 | 8 | 89.025 | 88.049 | 88.449 | 88.977 |
| tp-kimi-k3-w4a16 | 4096 | 711.990 | 697.702 | 682.214 | 682.517 |
| tp-nemo3-ultra-w4a16 | 8 | 65.953 | 65.408 | 65.392 | 65.920 |
| tp-nemo3-ultra-w4a16 | 4096 | 541.653 | 541.540 | 544.148 | 541.140 |
| tp-v3-w4a16 | 8 | 57.409 | 57.041 | 57.041 | 57.153 |
| tp-v3-w4a16 | 4096 | 476.484 | 478.419 | 477.716 | 475.875 |
| tp-v41-flash-w4a16 | 8 | 63.937 | 63.872 | 63.856 | 63.921 |
| tp-v41-flash-w4a16 | 4096 | 559.365 | 559.845 | 549.349 | 549.189 |

Evidence: `source-proof.json`, `bit-proof.json`, `codegen-analysis.json`, `peer-codegen-audit.json`, `QUALIFICATION.json`, `compatibility-cpu-oracle.json`, `perf-summary.json`, `component-summary.json`, `screen.csv`, `raw-audit.json`, and immutable `screen-evidence/`. Independent raw peer review passed in `peer-raw-audit.json`, reproducing all7,200 samples, activity spans/quartiles,32phases and all8negative rows. All514 measured source files match retained1e4. The now-inactive local review copy was retired after patch/hash/no-untracked proof; helpers and immutable remote source remain. A fresh104-cell W4 AA publication refresh is prepared separately in `../retained-w4-scale-dup-full`; these18CAAC rows remain the retention evidence.
