Speedup = `100 × (baseline latency / swap-AB latency − 1)`; positive is faster. Each column compares the same dtype. Tokens 1/2 remain visible but are excluded from retention.

| Model | Tokens | TRTLLM W4A4 | TRTLLM PER-TOKEN | TRTLLM MXFP4x8 | TRTLLM MXFP8 | Old CuTe W4A4 | Old CuTe PER-TOKEN | Old CuTe MXFP4x8† | Old CuTe MXFP8† | W4A16 before PR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V3 EP8 | 1 | -11.38% | +0.63% | +11.16% | -7.87% | +13.95% | +13.49% | +33.33% | +31.66% | Pending |
| V3 EP8 | 2 | +8.86% | +10.60% | +17.87% | +6.19% | +11.88% | +19.13% | +43.72% | +30.34% | Pending |
| V3 EP8 | 4 | +3.39% | +10.94% | +11.24% | +15.20% | +17.55% | +26.25% | +28.33% | +15.87% | Pending |
| V3 EP8 | 8 | +5.69% | +8.85% | +1.75% | +6.80% | +18.53% | +24.00% | +29.80% | +14.95% | Pending |
| V3 EP8 | 16 | +6.30% | +9.72% | +9.15% | +3.93% | +15.51% | +19.15% | +26.89% | +9.71% | Pending |
| V3 EP8 | 32 | +3.17% | +6.12% | +2.42% | +0.64% | +12.89% | +17.35% | +28.67% | +11.10% | Pending |
| V3 EP8 | 64 | +6.02% | +7.77% | +5.78% | +1.07% | +12.64% | +17.66% | +26.53% | +9.70% | Pending |
| V3 EP8 | 128 | +3.10% | +5.67% | +3.08% | +2.64% | +10.17% | +15.20% | +26.02% | +8.64% | Pending |
| V3 EP8 | 256 | +4.01% | +4.13% | +2.30% | +1.37% | +8.86% | +13.85% | +23.83% | +7.60% | Pending |
| V3 EP8 | 512 | +4.01% | +5.75% | +6.60% | +3.00% | +7.40% | +14.44% | +22.75% | +8.35% | Pending |
| V3 EP8 | 4096 | +7.57% | +6.91% | +5.27% | +3.91% | +5.91% | +20.46% | +13.01% | +4.48% | Pending |
| V3 EP8 | 8192 | +11.04% | +10.04% | +8.34% | -4.14% | -5.25% | +11.01% | -1.92% | -2.97% | Pending |
| V3 EP8 | 16384 | +20.62% | +12.46% | +8.56% | +2.31% | -6.60% | +7.50% | -6.79% | -6.83% | Pending |
| V4.1-Flash EP4 | 1 | +12.88% | -4.45% | -2.69% | -2.22% | -18.75% | +7.50% | -28.07% | -21.07% | Pending |
| V4.1-Flash EP4 | 2 | -19.08% | -2.70% | -13.26% | -15.09% | +0.42% | +22.55% | +26.67% | +2.75% | Pending |
| V4.1-Flash EP4 | 4 | +3.65% | +10.92% | +9.86% | +6.27% | +21.59% | +36.32% | +30.21% | +21.52% | Pending |
| V4.1-Flash EP4 | 8 | +7.44% | +12.21% | +9.20% | +6.05% | +21.82% | +34.20% | +42.08% | +24.45% | Pending |
| V4.1-Flash EP4 | 16 | +5.42% | +9.57% | +8.33% | +3.32% | +14.59% | +39.57% | +36.17% | +10.86% | Pending |
| V4.1-Flash EP4 | 32 | +4.33% | +5.54% | +3.85% | -0.58% | +12.61% | +27.68% | +31.64% | +10.33% | Pending |
| V4.1-Flash EP4 | 64 | +2.86% | +3.74% | +2.68% | -1.22% | +7.44% | +18.39% | +28.69% | +7.01% | Pending |
| V4.1-Flash EP4 | 128 | +2.82% | +2.55% | +2.01% | -1.34% | +7.94% | +16.20% | +25.41% | +4.92% | Pending |
| V4.1-Flash EP4 | 256 | +1.73% | +1.70% | +1.27% | -0.94% | +7.97% | +15.72% | +24.01% | +6.56% | Pending |
| V4.1-Flash EP4 | 512 | +2.63% | +1.06% | +1.52% | -0.37% | +6.87% | +14.50% | +23.15% | +6.75% | Pending |
| V4.1-Flash EP4 | 4096 | +3.37% | +2.04% | +8.51% | +0.32% | +4.89% | +16.90% | +10.02% | +2.58% | Pending |
| V4.1-Flash EP4 | 8192 | +7.21% | +2.37% | +4.87% | +1.53% | +8.04% | +17.40% | +17.32% | +8.36% | Pending |
| V4.1-Flash EP4 | 16384 | +4.64% | +4.68% | +5.16% | +3.30% | -5.93% | +9.63% | -2.51% | +3.28% | Pending |
| Kimi K3 EP8 | 1 | +3.29% | N/A | +2.12% | N/A | -27.92% | +39.72% | N/A | N/A | Pending |
| Kimi K3 EP8 | 2 | -11.53% | N/A | -3.36% | N/A | +10.02% | +50.20% | N/A | N/A | Pending |
| Kimi K3 EP8 | 4 | +8.02% | N/A | +10.27% | N/A | +22.26% | +41.88% | N/A | N/A | Pending |
| Kimi K3 EP8 | 8 | +3.35% | N/A | +5.18% | N/A | +17.78% | +46.09% | N/A | N/A | Pending |
| Kimi K3 EP8 | 16 | -0.24% | N/A | +1.13% | N/A | +13.93% | +35.93% | N/A | N/A | Pending |
| Kimi K3 EP8 | 32 | +0.10% | N/A | -0.54% | N/A | +10.60% | +26.47% | N/A | N/A | Pending |
| Kimi K3 EP8 | 64 | -1.00% | N/A | -1.57% | N/A | +8.23% | +20.64% | N/A | N/A | Pending |
| Kimi K3 EP8 | 128 | +1.30% | N/A | -0.81% | N/A | +9.32% | +19.26% | N/A | N/A | Pending |
| Kimi K3 EP8 | 256 | +0.47% | N/A | -0.53% | N/A | +7.39% | +18.31% | N/A | N/A | Pending |
| Kimi K3 EP8 | 512 | -0.03% | N/A | -0.69% | N/A | +7.37% | +18.16% | N/A | N/A | Pending |
| Kimi K3 EP8 | 4096 | +7.27% | N/A | +10.71% | N/A | +2.82% | +29.14% | N/A | N/A | Pending |
| Kimi K3 EP8 | 8192 | +11.18% | N/A | +22.87% | N/A | +5.69% | +24.88% | N/A | N/A | Pending |
| Kimi K3 EP8 | 16384 | +4.38% | N/A | +17.22% | N/A | -6.00% | +18.99% | N/A | N/A | Pending |
| Nemotron-3 Ultra EP8 | 1 | Pending | Pending | Pending | Pending | +6.68% | +65.98% | +41.61% | +22.30% | Pending |
| Nemotron-3 Ultra EP8 | 2 | Pending | Pending | Pending | Pending | +7.35% | +51.70% | +6.92% | +11.08% | Pending |
| Nemotron-3 Ultra EP8 | 4 | Pending | Pending | Pending | Pending | +18.19% | +64.03% | +41.21% | +26.41% | Pending |
| Nemotron-3 Ultra EP8 | 8 | Pending | Pending | Pending | Pending | +16.94% | +52.86% | +35.12% | +13.67% | Pending |
| Nemotron-3 Ultra EP8 | 16 | Pending | Pending | Pending | Pending | +15.26% | +38.58% | +29.41% | +12.05% | Pending |
| Nemotron-3 Ultra EP8 | 32 | Pending | Pending | Pending | Pending | +14.49% | +34.38% | +31.51% | +13.78% | Pending |
| Nemotron-3 Ultra EP8 | 64 | Pending | Pending | Pending | Pending | +13.69% | +31.99% | +30.71% | +12.17% | Pending |
| Nemotron-3 Ultra EP8 | 128 | Pending | Pending | Pending | Pending | +14.48% | +30.74% | +28.03% | +10.34% | Pending |
| Nemotron-3 Ultra EP8 | 256 | Pending | Pending | Pending | Pending | +11.29% | +30.98% | +27.38% | +9.47% | Pending |
| Nemotron-3 Ultra EP8 | 512 | Pending | Pending | Pending | Pending | +11.48% | +32.86% | +23.32% | +6.90% | Pending |
| Nemotron-3 Ultra EP8 | 4096 | Pending | Pending | Pending | Pending | -6.54% | +48.07% | +4.45% | +2.11% | Pending |
| Nemotron-3 Ultra EP8 | 8192 | Pending | Pending | Pending | Pending | -4.95% | +45.23% | -0.62% | -7.62% | Pending |
| Nemotron-3 Ultra EP8 | 16384 | Pending | Pending | Pending | Pending | -12.83% | +54.02% | +4.24% | -9.70% | Pending |

† Legacy MX uses its required fused finalize; swap-AB is unfused. N/A means unsupported. Pending means the matching measurement has not been collected.

Retained TRTLLM comparisons: `f7182d5c`; legacy comparisons: `002529e1` → `0b7fe901`. These historical campaigns predate the opt-in API separation. Fresh Nemotron TRTLLM and W4A16 rows are added from their own matched measurements; W4A16 baseline uses the pre-PR legacy layout and the new arm uses swap-AB layout.
