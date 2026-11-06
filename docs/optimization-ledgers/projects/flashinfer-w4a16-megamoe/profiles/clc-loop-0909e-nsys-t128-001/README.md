# CLC loop trace at 128 global tokens

[Open Nsight Systems report](ep_w4a16_megamoe_t128.nsys-rep) · [SQLite](ep_w4a16_megamoe_t128.sqlite) · [kernel CSV](ep_w4a16_megamoe_t128.kernels.csv) · [machine-readable analysis](analysis.json)

Two eager iterations at EP8, 128 global source tokens (16 per rank), H7168/I2048/E256/top-k 8. Exact completed loop winner: M256/N64/K256, C2, F4, S2, bundle1, reused dispatch return. Source `11ea88a3` / manifest `2017b23d`, CUDA 13.2 in `nvcr.io/nvidia/pytorch:26.05-py3`, 8 B300 on `hu-pdx-115`; Nsight Systems 2026.2.1. Actual command, selected-row provenance and tool/hardware records are beside this file.

| Stage | Instances | Aggregate GPU time | Mean µs | Min–max µs |
|---|---:|---:|---:|---:|
| routing | 16 | 0.24% | 3.628 | 3.520–3.872 |
| staging | 16 | 0.35% | 5.298 | 5.056–5.664 |
| dispatch | 16 | 27.11% | 405.587 | 24.992–791.655 |
| compute | 16 | 68.13% | 1019.206 | 973.284–1051.079 |
| finish | 16 | 3.99% | 59.669 | 28.193–106.465 |
| reduction | 16 | 0.17% | 2.612 | 2.400–2.848 |

Compute dominates this trace: 973–1051µs across all 16 calls, with cross-rank start skew only 1.90/1.10µs for the two iterations. It launches 1280 clusters (2560 CTAs) per rank, versus 74 fixed transport clusters. The actual compute resources remain 96 registers, 640 threads, 200192 dynamic shared bytes and zero local memory. This supports investigating compute scheduling and the oversized physical launch budget; the trace alone does not separate scheduler polling from arithmetic inside the compute kernel.

Dispatch varies from 25 to792µs, with cross-rank start skew 765/468µs. That is consistent with peer-arrival waiting contributing substantially to its aggregate GPU time; it is not evidence that raw data transfer takes 406µs. Finish averages 60µs. Staging and reduction together account for about 0.53% of aggregate GPU time.

These percentages sum duration over all eight devices and are not elapsed critical-path shares. The two eager instrumented iterations are diagnostic, not AUTO cold-L2 timings or a new retention comparison. The complete AUTO comparison remains separate and reports a −0.3767% latency GM change for 8–4096 tokens.

Capture 91286, source/native/idle closure 6550 and fetch 64616 all exited 0. Source stayed exact 11ea, native inventory stayed d3ce, and all GPUs were idle at closure. The downloaded report is 1,623,228 bytes, SHA256 `f9ab2915b09648e5783722766d2ec9da39c90ac694ef846f2595aadf374a1747`. Driver/DSL compilation caches are excluded.
