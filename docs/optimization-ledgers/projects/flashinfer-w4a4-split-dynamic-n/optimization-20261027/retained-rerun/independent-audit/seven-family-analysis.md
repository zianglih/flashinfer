# Independent fresh-ratio audit

Fresh ratios use matched per-campaign baselines. Cross-campaign shifts are historical comparisons, not direct paired source A/B speedups.

Seven completed families; N3U MX is pending. Verified all sampled frozen phases used below against result SHA, receipt status, 100 positive CUPTI samples and sample medians. This audit does not consume assembler outputs. Tokens1/2 are excluded.

## Fresh NV targets

| Model | Tokens | TRTLLM W4A4 | TRTLLM PER-TOKEN | Non-swap W4A4 | Non-swap PER-TOKEN | W4A16 before PR |
|---|---:|---:|---:|---:|---:|---:|
| V3 EP8 | 4 | +2.53% | +22.90% | +15.97% | +28.52% | -1.65% |
| V3 EP8 | 8 | +4.84% | +8.58% | +17.31% | +23.73% | +0.78% |
| V3 EP8 | 16 | +5.35% | +8.95% | +15.06% | +19.81% | -1.46% |
| V3 EP8 | 32 | +2.55% | +5.52% | +11.86% | +18.48% | +0.04% |
| V3 EP8 | 64 | +6.73% | +7.72% | +11.95% | +16.93% | +0.59% |
| V3 EP8 | 128 | +2.71% | +4.88% | +9.41% | +15.37% | -0.17% |
| V3 EP8 | 256 | +3.65% | +5.01% | +8.75% | +14.87% | +0.18% |
| V3 EP8 | 512 | +4.45% | +6.14% | +7.67% | +15.24% | +0.62% |
| V3 EP8 | 4096 | +8.34% | +8.10% | +6.29% | +20.23% | +1.90% |
| V3 EP8 | 8192 | +20.96% | +19.38% | +2.39% | +21.10% | +0.88% |
| V3 EP8 | 16384 | +28.19% | +21.44% | -1.61% | +16.85% | +2.67% |
| V41F EP4 | 4 | +5.10% | +12.19% | +16.88% | +33.68% | -0.50% |
| V41F EP4 | 8 | +11.46% | +11.80% | +21.91% | +33.79% | -1.32% |
| V41F EP4 | 16 | +4.58% | +9.26% | +13.67% | +36.13% | -0.35% |
| V41F EP4 | 32 | +4.33% | +5.08% | +10.23% | +24.67% | -1.69% |
| V41F EP4 | 64 | +2.85% | +4.16% | +6.94% | +17.20% | -0.31% |
| V41F EP4 | 128 | +2.44% | +2.45% | +6.94% | +15.06% | +0.17% |
| V41F EP4 | 256 | +2.39% | +1.64% | +7.81% | +15.51% | -1.56% |
| V41F EP4 | 512 | +2.43% | +1.86% | +7.35% | +15.10% | -0.57% |
| V41F EP4 | 4096 | +3.85% | +1.15% | +2.22% | +11.45% | +3.92% |
| V41F EP4 | 8192 | +7.17% | +2.78% | +5.04% | +13.00% | +0.50% |
| V41F EP4 | 16384 | +15.66% | +11.96% | +2.03% | +12.88% | -0.97% |
| K3 EP8 | 4 | +5.20% | N/A | +18.48% | +39.64% | -0.86% |
| K3 EP8 | 8 | +1.93% | N/A | +13.31% | +40.84% | +0.33% |
| K3 EP8 | 16 | +0.23% | N/A | +12.57% | +34.11% | -0.61% |
| K3 EP8 | 32 | -0.35% | N/A | +9.19% | +26.16% | +0.71% |
| K3 EP8 | 64 | -1.12% | N/A | +8.09% | +20.47% | -0.14% |
| K3 EP8 | 128 | +1.24% | N/A | +8.64% | +19.52% | +0.58% |
| K3 EP8 | 256 | +0.72% | N/A | +7.34% | +18.93% | +0.32% |
| K3 EP8 | 512 | +0.13% | N/A | +7.59% | +17.86% | +0.32% |
| K3 EP8 | 4096 | +7.09% | N/A | +2.17% | +32.90% | -1.95% |
| K3 EP8 | 8192 | +9.39% | N/A | +4.28% | +30.96% | +0.30% |
| K3 EP8 | 16384 | +17.04% | N/A | +3.96% | +28.91% | +1.03% |
| N3U EP8 | 4 | -1.44% | +6.92% | +15.17% | +55.86% | -0.84% |
| N3U EP8 | 8 | +4.12% | +10.47% | +14.76% | +47.16% | +1.09% |
| N3U EP8 | 16 | +4.57% | +8.00% | +14.93% | +37.46% | +0.49% |
| N3U EP8 | 32 | +4.37% | +5.44% | +16.49% | +35.09% | +0.26% |
| N3U EP8 | 64 | +1.09% | +2.20% | +12.41% | +31.22% | +0.56% |
| N3U EP8 | 128 | +2.28% | +4.19% | +11.26% | +33.13% | +1.08% |
| N3U EP8 | 256 | +5.06% | +5.19% | +12.30% | +33.17% | +0.49% |
| N3U EP8 | 512 | +6.17% | +6.70% | +10.65% | +34.57% | +0.90% |
| N3U EP8 | 4096 | -1.71% | -2.44% | -10.48% | +50.84% | +1.00% |
| N3U EP8 | 8192 | +20.97% | +8.22% | +2.41% | +62.27% | -2.12% |
| N3U EP8 | 16384 | +25.00% | +12.87% | -3.69% | +72.92% | -1.70% |

## Historical shifts in matched-baseline ratios

Columns show geometric means across each token bucket. Historical normalized shift is100*(fresh ratio / previous ratio−1); it is not a causal paired source A/B measurement.

| Model | Target | Bucket | Previous | Fresh | Historical normalized shift | Fresh wins |
|---|---|---|---:|---:|---:|---:|
| V3 EP8 | TRTLLM W4A4 | decode | +4.79% | +4.09% | -0.66% | 8/8 |
| V3 EP8 | TRTLLM W4A4 | prefill | +13.71% | +18.88% | +4.55% | 3/3 |
| V3 EP8 | TRTLLM PER-TOKEN | decode | +7.27% | +8.58% | +1.22% | 8/8 |
| V3 EP8 | TRTLLM PER-TOKEN | prefill | +10.28% | +16.15% | +5.33% | 3/3 |
| V3 EP8 | Non-swap W4A4 | decode | +12.52% | +12.20% | -0.28% | 8/8 |
| V3 EP8 | Non-swap W4A4 | prefill | -1.94% | +2.31% | +4.33% | 2/3 |
| V3 EP8 | Non-swap PER-TOKEN | decode | +18.87% | +19.04% | +0.14% | 8/8 |
| V3 EP8 | Non-swap PER-TOKEN | prefill | +13.49% | +19.38% | +5.19% | 3/3 |
| V3 EP8 | W4A16 before PR | decode | -0.18% | -0.14% | +0.04% | 5/8 |
| V3 EP8 | W4A16 before PR | prefill | +0.46% | +1.81% | +1.34% | 3/3 |
| V41F EP4 | TRTLLM W4A4 | decode | +3.94% | +4.41% | +0.46% | 8/8 |
| V41F EP4 | TRTLLM W4A4 | prefill | +5.32% | +8.78% | +3.29% | 3/3 |
| V41F EP4 | TRTLLM PER-TOKEN | decode | +4.98% | +5.97% | +0.94% | 8/8 |
| V41F EP4 | TRTLLM PER-TOKEN | prefill | +3.34% | +5.19% | +1.79% | 3/3 |
| V41F EP4 | Non-swap W4A4 | decode | +11.27% | +11.35% | +0.07% | 8/8 |
| V41F EP4 | Non-swap W4A4 | prefill | -0.77% | +3.09% | +3.89% | 3/3 |
| V41F EP4 | Non-swap PER-TOKEN | decode | +22.54% | +23.59% | +0.85% | 8/8 |
| V41F EP4 | Non-swap PER-TOKEN | prefill | +10.28% | +12.44% | +1.96% | 3/3 |
| V41F EP4 | W4A16 before PR | decode | -0.84% | -0.77% | +0.07% | 1/8 |
| V41F EP4 | W4A16 before PR | prefill | +4.56% | +1.13% | -3.28% | 2/3 |
| K3 EP8 | TRTLLM W4A4 | decode | +0.65% | +0.98% | +0.33% | 6/8 |
| K3 EP8 | TRTLLM W4A4 | prefill | +7.43% | +11.09% | +3.41% | 3/3 |
| K3 EP8 | Non-swap W4A4 | decode | +10.43% | +10.59% | +0.14% | 8/8 |
| K3 EP8 | Non-swap W4A4 | prefill | +0.47% | +3.47% | +2.99% | 3/3 |
| K3 EP8 | Non-swap PER-TOKEN | decode | +26.46% | +26.88% | +0.33% | 8/8 |
| K3 EP8 | Non-swap PER-TOKEN | prefill | +25.32% | +30.91% | +4.47% | 3/3 |
| K3 EP8 | W4A16 before PR | decode | +0.18% | +0.08% | -0.10% | 5/8 |
| K3 EP8 | W4A16 before PR | prefill | +0.53% | -0.21% | -0.74% | 2/3 |
| N3U EP8 | TRTLLM W4A4 | decode | +3.86% | +3.25% | -0.59% | 7/8 |
| N3U EP8 | TRTLLM W4A4 | prefill | +7.75% | +14.12% | +5.92% | 2/3 |
| N3U EP8 | TRTLLM PER-TOKEN | decode | +6.34% | +6.11% | -0.21% | 8/8 |
| N3U EP8 | TRTLLM PER-TOKEN | prefill | +2.09% | +6.02% | +3.85% | 2/3 |
| N3U EP8 | Non-swap W4A4 | decode | +14.14% | +13.48% | -0.58% | 8/8 |
| N3U EP8 | Non-swap W4A4 | prefill | -9.33% | -4.07% | +5.80% | 1/3 |
| N3U EP8 | Non-swap PER-TOKEN | decode | +38.69% | +38.23% | -0.33% | 8/8 |
| N3U EP8 | Non-swap PER-TOKEN | prefill | +55.89% | +61.76% | +3.76% | 3/3 |
| N3U EP8 | W4A16 before PR | decode | +0.44% | +0.50% | +0.06% | 7/8 |
| N3U EP8 | W4A16 before PR | prefill | -0.89% | -0.95% | -0.06% | 1/3 |

## Residual gaps

- N3U W4A4 vs legacy at4096/16384 remains−10.48%/−3.69%; at8192 it is now+2.41%. Its4096 TRT ratio is−1.71%. These fresh brackets drift≤0.14%.
- K3 W4A4 vs TRT remains−0.35% at32 and−1.12% at64. T16 is+0.23%; decode geometric mean is+0.98%.
- V41F MXFP8 vs TRT is−0.89/−1.23/−1.58/−0.68/−0.18% at32/64/128/256/512. MXFP4x8 is faster on all decode rows.
- W4A16 changes are measured in native AUTO and may select different tactics; its historical ratio shifts cannot be attributed to the new general kernel changes without a fixed-tactic follow-up.
