# V41 per-token public-profile NSYS diagnostic

Clean control `0def601d`, B300 GPU7, `nvcr.io/nvidia/pytorch:26.05-py3`, NSYS2026.2.1. Two public saved-tactic profiles (128 and4096tokens), each with three cold-L2 CUDA graph replays and input quantization included. This is a kernel/overlap diagnostic, not the retention benchmark. The same native control tactics from the GPU0 campaign are replayed; source/cache receipts and exact commands are saved in `receipt.json`.

| Phase | 128 tokens (us) | 4096 tokens (us) |
|---|---:|---:|
| input quantization | 3.488 | 39.648 |
| route indexing | 6.688 | 8.640 |
| input prepare | 3.584 | 10.464 |
| FC1 | 168.416 | 199.457 |
| FC2 input quantization | 15.904 | 62.336 |
| FC2 | 89.280 | 107.521 |
| combine | 4.032 | 19.648 |

Numbers are medians across the three diagnostic kernel instances. Kernel durations overlap under PDL and must not be summed as total latency. GPU-chain spans and adjacent overlap are in `summary.json`. The standalone FC2 quantizer is visible but does not dominate: the two GEMMs are the largest phases at both sizes. This narrows the next investigation toward GEMM mainloop/weight traffic; NSYS alone does not identify the specific GEMM stall.

The token128 capture used explicit `capture-range-end=stop-shutdown`, which terminated the target with143 after the completed profiler range. The trace contains all three complete chains and was exported without rerunning. Token4096 used `capture-range-end=stop` and exited0. Original failure receipt/log and the resumed export are preserved. Both reports and SQLite/CSV exports are present.
