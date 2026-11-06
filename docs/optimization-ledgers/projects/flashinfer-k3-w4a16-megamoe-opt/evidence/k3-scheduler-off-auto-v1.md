# kimi-k3 — original_scheduler24 (AUTO with 24 tactics)

Synthetic NVFP4 Kimi K3 latent routed-expert core; no input/output latent projections.

Median of 100 untrimmed per-iteration rank-MAX CUPTI spans; microseconds. One fresh EP8 process group; 3 warmups, CUDA graphs, cold L2, precomputed routing.
PDL enabled, fused FC2/TMA reduction disabled, deterministic combine enabled; apply_topk_in_fc1=False.
No cross-model speedup comparison. AUTO selection scores are reported separately.

| Global tokens | Median µs | P25–P75 µs | Samples | Selected M/N/G/return |
|---:|---:|---:|---:|---|
| 1 | 82.417 | 81.489–83.369 | 100 | M128/N32/G1024/epi_warps |
| 2 | 92.417 | 91.729–93.473 | 100 | M128/N32/G512/epi_warps |
| 4 | 111.777 | 110.585–112.697 | 100 | M128/N32/G512/epi_warps |
| 8 | 145.441 | 144.177–146.817 | 100 | M128/N32/G1024/epi_warps |
| 16 | 153.201 | 152.034–155.042 | 100 | M256/N32/G1024/epi_warps |
| 32 | 229.745 | 228.889–230.890 | 100 | M128/N32/G512/epi_warps |
| 64 | 313.971 | 313.028–315.331 | 100 | M256/N32/G1024/epi_warps |
| 128 | 357.300 | 356.123–358.724 | 100 | M256/N32/G512/epi_warps |
| 256 | 386.003 | 384.892–387.011 | 100 | M256/N32/G1024/epi_warps |
| 512 | 399.029 | 397.948–400.845 | 100 | M256/N32/G1024/epi_warps |
| 4096 | 594.312 | 585.287–598.376 | 100 | M256/N128/G1024/epi_warps |
| 8192 | 1057.437 | 1018.924–1123.509 | 100 | M256/N128/G512/epi_warps |
| 16384 | 2054.436 | 1881.972–2063.155 | 100 | M256/N128/G1024/reuse_dispatch_warps |

M128 selected at tokens [1, 2, 4, 8, 32]; selected N values: [32].
Image: `nvcr.io/nvidia/pytorch:26.05-py3`. Source HEAD: `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`; exact measured source is captured by the source manifest and patch SHA `027344b471938682b648c26c2dfe2f744cdc88982a0a63d22139d3f4b849a8e8`.
The adjacent JSON preserves model metadata, runtime versions, every raw span, rank winner receipts, and source hashes.
