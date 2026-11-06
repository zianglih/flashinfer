# deepseek-v41-flash — original_scheduler24 (AUTO with 24 tactics)

Synthetic single NVFP4 routed-expert backbone layer with DeepSeek V4.1 Flash shapes; not end-to-end model performance.

Median of 100 untrimmed per-iteration rank-MAX CUPTI spans; microseconds. One fresh EP8 process group; 3 warmups, CUDA graphs, cold L2, precomputed routing.
PDL enabled, fused FC2/TMA reduction disabled, deterministic combine enabled; apply_topk_in_fc1=False.
No cross-model speedup comparison. AUTO selection scores are reported separately.

| Global tokens | Median µs | P25–P75 µs | Samples | Selected M/N/G/return |
|---:|---:|---:|---:|---|
| 1 | 66.897 | 66.017–67.577 | 100 | M256/N32/G1024/epi_warps |
| 2 | 67.201 | 66.368–68.073 | 100 | M128/N32/G1024/epi_warps |
| 4 | 60.881 | 60.088–62.216 | 100 | M128/N32/G512/epi_warps |
| 8 | 88.034 | 87.129–89.385 | 100 | M128/N32/G512/epi_warps |
| 16 | 103.201 | 102.457–104.705 | 100 | M128/N32/G512/epi_warps |
| 32 | 130.545 | 129.602–131.281 | 100 | M128/N32/G1024/epi_warps |
| 64 | 167.490 | 166.738–168.362 | 100 | M128/N32/G1024/epi_warps |
| 128 | 204.209 | 203.154–205.570 | 100 | M128/N32/G512/epi_warps |
| 256 | 208.369 | 207.362–209.273 | 100 | M128/N32/G1024/epi_warps |
| 512 | 212.242 | 211.385–213.153 | 100 | M128/N32/G1024/epi_warps |
| 4096 | 333.748 | 332.636–335.157 | 100 | M256/N128/G512/epi_warps |
| 8192 | 503.111 | 500.094–506.095 | 100 | M256/N128/G512/reuse_dispatch_warps |
| 16384 | 860.361 | 829.201–874.066 | 100 | M256/N128/G1024/reuse_dispatch_warps |

M128 selected at tokens [2, 4, 8, 16, 32, 64, 128, 256, 512]; selected N values: [32].
Image: `nvcr.io/nvidia/pytorch:26.05-py3`. Source HEAD: `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`; exact measured source is captured by the source manifest and patch SHA `027344b471938682b648c26c2dfe2f744cdc88982a0a63d22139d3f4b849a8e8`.
The adjacent JSON preserves model metadata, runtime versions, every raw span, rank winner receipts, and source hashes.
