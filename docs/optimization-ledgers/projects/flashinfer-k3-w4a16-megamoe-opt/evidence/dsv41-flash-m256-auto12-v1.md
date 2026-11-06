# deepseek-v41-flash — m256_auto12_off (AUTO with 12 tactics)

Synthetic single NVFP4 routed-expert backbone layer with DeepSeek V4.1 Flash shapes; not end-to-end model performance.

Median of 100 untrimmed per-iteration rank-MAX CUPTI spans; microseconds. One fresh EP8 process group; 3 warmups, CUDA graphs, cold L2, precomputed routing.
PDL enabled, fused FC2/TMA reduction disabled, deterministic combine enabled; apply_topk_in_fc1=False.
No cross-model speedup comparison. AUTO selection scores are reported separately.

| Global tokens | Median µs | P25–P75 µs | Samples | Selected M/N/G/return |
|---:|---:|---:|---:|---|
| 1 | 67.873 | 67.009–68.937 | 100 | M256/N64/G512/epi_warps |
| 2 | 69.425 | 68.769–70.161 | 100 | M256/N32/G512/epi_warps |
| 4 | 72.960 | 72.072–74.089 | 100 | M256/N32/G1024/epi_warps |
| 8 | 88.641 | 87.960–89.745 | 100 | M256/N32/G512/epi_warps |
| 16 | 103.185 | 102.361–104.153 | 100 | M256/N32/G512/epi_warps |
| 32 | 127.041 | 126.273–128.009 | 100 | M256/N32/G512/epi_warps |
| 64 | 168.017 | 167.194–168.722 | 100 | M256/N32/G1024/epi_warps |
| 128 | 201.043 | 200.418–201.898 | 100 | M256/N32/G512/epi_warps |
| 256 | 208.498 | 207.667–209.378 | 100 | M256/N32/G512/epi_warps |
| 512 | 208.355 | 207.715–208.875 | 100 | M256/N32/G1024/epi_warps |
| 4096 | 330.228 | 328.709–331.580 | 100 | M256/N128/G512/epi_warps |
| 8192 | 503.893 | 501.301–506.917 | 100 | M256/N128/G1024/reuse_dispatch_warps |
| 16384 | 866.679 | 831.079–877.648 | 100 | M256/N128/G1024/reuse_dispatch_warps |

M128 selected at tokens []; selected N values: [].
Image: `nvcr.io/nvidia/pytorch:26.05-py3`. Source HEAD: `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`; exact measured source is captured by the source manifest and patch SHA `774a524092e278d3577db7403f16f399cbbbbe0c67eacb731d90f373f602bad6`.
The adjacent JSON preserves model metadata, runtime versions, every raw span, rank winner receipts, and source hashes.
