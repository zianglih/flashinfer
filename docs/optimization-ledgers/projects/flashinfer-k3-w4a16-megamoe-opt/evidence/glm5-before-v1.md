# glm5 — before (AUTO with 8 tactics)

Synthetic NVFP4 routed-expert layer with GLM5 benchmark shapes; single layer, excludes attention and shared experts.

Median of 100 untrimmed per-iteration rank-MAX CUPTI spans; microseconds. One fresh EP8 process group; 3 warmups, CUDA graphs, cold L2, precomputed routing.
PDL enabled, fused FC2/TMA reduction disabled, deterministic combine enabled; apply_topk_in_fc1=False.
No cross-model speedup comparison. AUTO selection scores are reported separately.

| Global tokens | Median µs | P25–P75 µs | Samples | Selected M/N/G/return |
|---:|---:|---:|---:|---|
| 1 | 64.481 | 64.016–65.128 | 100 | M256/N64/G512/epi_warps |
| 2 | 84.833 | 84.152–85.840 | 100 | M256/N64/G1024/epi_warps |
| 4 | 92.497 | 91.920–93.256 | 100 | M256/N64/G1024/epi_warps |
| 8 | 113.408 | 112.249–114.416 | 100 | M256/N64/G1024/epi_warps |
| 16 | 124.528 | 123.641–125.449 | 100 | M256/N64/G1024/epi_warps |
| 32 | 142.401 | 141.793–143.601 | 100 | M256/N64/G512/epi_warps |
| 64 | 156.881 | 155.961–157.865 | 100 | M256/N64/G1024/epi_warps |
| 128 | 165.665 | 165.073–167.569 | 100 | M256/N64/G512/epi_warps |
| 256 | 169.761 | 168.674–170.873 | 100 | M256/N64/G1024/epi_warps |
| 512 | 172.817 | 171.705–173.865 | 100 | M256/N64/G1024/epi_warps |
| 4096 | 396.435 | 394.651–399.331 | 100 | M256/N128/G1024/reuse_dispatch_warps |
| 8192 | 662.869 | 657.117–685.484 | 100 | M256/N128/G1024/reuse_dispatch_warps |
| 16384 | 1232.413 | 1158.899–1265.766 | 100 | M256/N128/G512/reuse_dispatch_warps |

M128 selected at tokens []; selected N values: [].
Image: `nvcr.io/nvidia/pytorch:26.05-py3`. Source HEAD: `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`; exact measured source is captured by the source manifest and patch SHA `63b80709b9ee78ce46f27b2aa7ebd4245e4e7eeac0a94f6a425fcde14708476c`.
The adjacent JSON preserves model metadata, runtime versions, every raw span, rank winner receipts, and source hashes.
