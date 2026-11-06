# deepseek-v41-flash — before AUTO sweep (8 tactics)

Synthetic single NVFP4 routed-expert backbone layer with DeepSeek V4.1 Flash shapes; not end-to-end model performance.

Median of 100 untrimmed per-iteration rank-MAX CUPTI spans; microseconds. One fresh EP8 process group; 3 warmups, CUDA graphs, cold L2, precomputed routing.
PDL enabled, fused FC2/TMA reduction disabled, deterministic combine enabled; apply_topk_in_fc1=False.
No cross-model speedup comparison. AUTO selection scores are reported separately.

| Global tokens | Median µs | P25–P75 µs | Samples | Selected M/N/G/return |
|---:|---:|---:|---:|---|
| 1 | 62.209 | 61.313–63.041 | 100 | M256/N64/G512/epi_warps |
| 2 | 66.368 | 65.657–67.513 | 100 | M256/N64/G1024/epi_warps |
| 4 | 71.745 | 70.305–72.537 | 100 | M256/N64/G512/epi_warps |
| 8 | 86.481 | 85.137–87.273 | 100 | M256/N64/G1024/epi_warps |
| 16 | 102.337 | 101.585–103.073 | 100 | M256/N64/G1024/epi_warps |
| 32 | 122.593 | 121.721–123.546 | 100 | M256/N64/G512/epi_warps |
| 64 | 172.002 | 170.819–173.011 | 100 | M256/N64/G1024/epi_warps |
| 128 | 210.706 | 209.826–211.658 | 100 | M256/N64/G1024/epi_warps |
| 256 | 214.770 | 213.874–215.971 | 100 | M256/N64/G512/epi_warps |
| 512 | 217.011 | 216.194–217.779 | 100 | M256/N64/G512/epi_warps |
| 4096 | 332.755 | 330.763–335.652 | 100 | M256/N128/G1024/reuse_dispatch_warps |
| 8192 | 500.949 | 498.397–504.542 | 100 | M256/N128/G1024/reuse_dispatch_warps |
| 16384 | 873.786 | 852.241–886.441 | 100 | M256/N128/G1024/reuse_dispatch_warps |

M128 selected at tokens []; selected N values: [].
Image: `nvcr.io/nvidia/pytorch:26.05-py3`. Source HEAD: `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`; exact measured source is captured by the source manifest and patch SHA `63b80709b9ee78ce46f27b2aa7ebd4245e4e7eeac0a94f6a425fcde14708476c`.
The adjacent JSON preserves model metadata, runtime versions, every raw span, rank winner receipts, and source hashes.
