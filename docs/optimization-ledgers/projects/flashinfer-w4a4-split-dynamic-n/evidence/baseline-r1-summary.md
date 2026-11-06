# Baseline R1 preserved

This is one baseline sweep per public dtype, not a retained before/after result. GPU0, B200, CUDA13.2; source a65d5b09e7e4c4c5c160b0161c48becd100b3970. W4A4 uses unfused finalization; W4A8 uses its required fused finalization.

| Tokens | W4A4 us | W4A8 us |
|---:|---:|---:|
| 1 | 27.439 | 43.118 |
| 2 | 37.184 | 50.112 |
| 4 | 52.512 | 61.279 |
| 8 | 69.792 | 80.608 |
| 16 | 79.200 | 87.600 |
| 32 | 111.120 | 128.000 |
| 64 | 143.999 | 166.992 |
| 128 | 147.648 | 169.552 |
| 256 | 154.928 | 178.719 |
| 512 | 157.408 | 180.607 |
| 4096 | 208.463 | 264.895 |
| 8192 | 297.456 | 381.408 |
| 16384 | 472.464 | 714.223 |

Both raw JSON/log/cache archives are preserved under evidence/. Do not rerun these observations. Future ABBA campaigns must reuse their complete provenance. T1/T2 are reported and excluded from retention.

## Per-token W4A4 baseline R1

GPU1; unfused finalize; initial activation quantization excluded. Internal per-token scaling and requantization remain timed. Before/after comparisons must use this same GPU.

| Tokens | Latency (us) |
|---:|---:|
| 1 | 32.064 |
| 2 | 42.592 |
| 4 | 60.768 |
| 8 | 77.264 |
| 16 | 86.689 |
| 32 | 120.913 |
| 64 | 154.800 |
| 128 | 159.264 |
| 256 | 168.592 |
| 512 | 173.617 |
| 4096 | 252.160 |
| 8192 | 360.865 |
| 16384 | 625.217 |
