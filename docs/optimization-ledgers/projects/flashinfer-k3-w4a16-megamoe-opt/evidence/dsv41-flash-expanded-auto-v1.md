# deepseek-v41-flash — expanded24 (AUTO with 24 tactics)

Synthetic single NVFP4 routed-expert backbone layer with DeepSeek V4.1 Flash shapes; not end-to-end model performance.

Median of 100 untrimmed per-iteration rank-MAX CUPTI spans; microseconds. One fresh EP8 process group; 3 warmups, CUDA graphs, cold L2, precomputed routing.
PDL enabled, fused FC2/TMA reduction disabled, deterministic combine enabled; apply_topk_in_fc1=False.
No cross-model speedup comparison. AUTO selection scores are reported separately.

| Global tokens | Median µs | P25–P75 µs | Samples | Selected M/N/G/return |
|---:|---:|---:|---:|---|
| 1 | 64.561 | 63.417–65.281 | 100 | M128/N32/G512/epi_warps |
| 2 | 68.689 | 67.937–69.449 | 100 | M128/N32/G1024/epi_warps |
| 4 | 72.512 | 71.713–73.192 | 100 | M128/N32/G1024/epi_warps |
| 8 | 87.201 | 86.113–87.840 | 100 | M128/N32/G1024/epi_warps |
| 16 | 102.657 | 101.497–103.825 | 100 | M128/N32/G1024/epi_warps |
| 32 | 135.346 | 133.865–145.137 | 100 | M128/N32/G1024/epi_warps |
| 64 | 168.754 | 168.058–169.514 | 100 | M128/N32/G1024/epi_warps |
| 128 | 202.290 | 200.914–239.891 | 100 | M128/N32/G512/epi_warps |
| 256 | 208.546 | 207.586–209.490 | 100 | M128/N32/G1024/epi_warps |
| 512 | 207.698 | 206.778–208.562 | 100 | M128/N32/G512/epi_warps |
| 4096 | 333.396 | 331.868–334.603 | 100 | M256/N128/G512/epi_warps |
| 8192 | 492.581 | 489.638–495.877 | 100 | M256/N128/G1024/reuse_dispatch_warps |
| 16384 | 880.354 | 832.290–900.154 | 100 | M256/N128/G512/reuse_dispatch_warps |

M128 selected at tokens [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]; selected N values: [32].
Image: `nvcr.io/nvidia/pytorch:26.05-py3`. Source HEAD: `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`; exact measured source is captured by the source manifest and patch SHA `35602f634e2f623d6ca989a89e6e149b2d1b705a3142a269c206a39ab86ed565`.
The adjacent JSON preserves model metadata, runtime versions, every raw span, rank winner receipts, and source hashes.
