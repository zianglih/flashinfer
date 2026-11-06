# glm5 — final16_original_scheduler (AUTO with 16 tactics)

Synthetic NVFP4 routed-expert layer with GLM5 benchmark shapes; single layer, excludes attention and shared experts.

Median of 100 untrimmed per-iteration rank-MAX CUPTI spans; microseconds. One fresh EP8 process group; 3 warmups, CUDA graphs, cold L2, precomputed routing.
PDL enabled, fused FC2/TMA reduction disabled, deterministic combine enabled; apply_topk_in_fc1=False.
No cross-model speedup comparison. AUTO selection scores are reported separately.

| Global tokens | Median µs | P25–P75 µs | Samples | Selected M/N/G/return |
|---:|---:|---:|---:|---|
| 1 | 66.769 | 65.969–67.968 | 100 | M128/N32/G1024/epi_warps |
| 2 | 84.481 | 83.937–85.440 | 100 | M256/N32/G512/epi_warps |
| 4 | 93.377 | 92.442–94.097 | 100 | M256/N32/G1024/epi_warps |
| 8 | 109.169 | 108.130–110.409 | 100 | M128/N32/G512/epi_warps |
| 16 | 120.946 | 119.969–121.937 | 100 | M256/N32/G512/epi_warps |
| 32 | 143.249 | 142.369–144.137 | 100 | M256/N32/G1024/epi_warps |
| 64 | 158.530 | 157.826–159.554 | 100 | M256/N32/G512/epi_warps |
| 128 | 162.802 | 162.034–163.763 | 100 | M256/N32/G1024/epi_warps |
| 256 | 155.793 | 155.010–156.410 | 100 | M256/N32/G1024/epi_warps |
| 512 | 165.890 | 164.753–166.922 | 100 | M256/N32/G512/epi_warps |
| 4096 | 389.060 | 386.796–391.748 | 100 | M256/N128/G1024/reuse_dispatch_warps |
| 8192 | 657.639 | 651.230–669.503 | 100 | M256/N128/G1024/reuse_dispatch_warps |
| 16384 | 1229.966 | 1174.037–1270.069 | 100 | M256/N128/G512/reuse_dispatch_warps |

M128 selected at tokens [1, 8]; selected N values: [32].
Image: `nvcr.io/nvidia/pytorch:26.05-py3`. Source HEAD: `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`; exact measured source is captured by the source manifest and patch SHA `6fe32055e8bf9d4391312904aaba2a60b298660b70d7a9c432a73830c60a4477`.
The adjacent JSON preserves model metadata, runtime versions, every raw span, rank winner receipts, and source hashes.
