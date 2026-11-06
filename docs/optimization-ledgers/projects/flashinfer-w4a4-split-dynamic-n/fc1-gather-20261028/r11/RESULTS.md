# R11 register-policy experiment

R11 adds the structured control80/gather128/epilogue256 register policy to R6. Candidate kernel SHA `3a2b03635a13faa50549de903eebb265a13c50d8ac804c2ae3b1e245da10650f`. No canonical/review source changes or PR push.

All44 existing qualification tests passed. Final quick4 performance contains32 cells and12,800 CUPTI samples: same-GPU CAAC versus retained `d35fcfda`, frozen native winners/routes, cold-L2 CUDA graphs,10 warmups and100 samples per phase. Tokens8,256,4096,16384. NV includes initial activation quantization; MX does not. W4A16 is an unchanged control. Normal compilation/cache options were used; source-bound runtime register queries occur before launch and outside timing.

| Workload | Decode | Prefill | All affected cells |
|---|---:|---:|---:|
| V3 EP8 NV | -13.51% | -42.04% | -31.39% |
| V41F EP4 MX | -50.03% | -48.15% | -47.69% |
| K3 EP8 MXFP4x8 | -59.18% | -65.52% | -64.90% |
| N3U TP8 MX | -12.73% | -17.45% | -19.15% |

Positive means candidate faster: `geomean(control medians) / geomean(candidate medians) - 1`. W4A16 control geomean is+0.76%; maximum paired phase spreads are2.21% control and1.91% candidate. Donation alone does not recover the gather pipeline performance gap. Saved R6 quick4 is qualitatively similar, but it is not an adjacent same-GPU R6/R11 comparison, so subpercent differences are not causal evidence.

Source/observer/gate proof passed (`report/source-proof.json`). The eight candidate process receipts guard98 compiled kernels; all FC1 initial reservations are168 registers. Runtime local storage is0B for K3/V41, at most16B for V3, and8B for N3U TP. Local bytes are not a dynamic spill count.

Final evidence: `evidence/perf/`, `report/{summary.json,cells.csv,source-proof.json}`, and `evidence/runtime-codegen-summary.json`. Failed artifact-only prelaunch attempts are separate from `evidence/perf` and excluded from all results.

| Model/topology | Tokens | Backend | Control1 µs | Candidate1 µs | Candidate2 µs | Control2 µs | Speedup |
|---|---:|---|---:|---:|---:|---:|---:|
| kimi-k3 ep | 8 | CuteDSL MXFP4x8 | 78.241 | 191.586 | 191.682 | 78.209 | -59.18% |
| kimi-k3 ep | 256 | CuteDSL MXFP4x8 | 319.204 | 1021.513 | 1022.088 | 319.651 | -68.74% |
| kimi-k3 ep | 4096 | CuteDSL MXFP4x8 | 396.467 | 1196.553 | 1195.242 | 396.580 | -66.84% |
| kimi-k3 ep | 16384 | CuteDSL MXFP4x8 | 989.032 | 2788.055 | 2788.057 | 1010.936 | -64.14% |
| v3 ep | 8 | CuteDSL W4A4 | 58.705 | 80.704 | 80.608 | 58.657 | -27.25% |
| v3 ep | 8 | CuteDSL PER-TOKEN | 63.937 | 62.208 | 62.224 | 64.001 | +2.82% |
| v3 ep | 8 | CuteDSL W4A16 | 65.648 | 65.616 | 65.600 | 65.681 | +0.09% |
| v3 ep | 256 | CuteDSL W4A4 | 146.177 | 192.625 | 192.594 | 145.921 | -24.17% |
| v3 ep | 256 | CuteDSL PER-TOKEN | 152.929 | 199.249 | 199.409 | 152.961 | -23.27% |
| v3 ep | 256 | CuteDSL W4A16 | 153.121 | 153.473 | 153.585 | 153.585 | -0.11% |
| v3 ep | 4096 | CuteDSL W4A4 | 205.314 | 344.994 | 345.411 | 205.729 | -40.46% |
| v3 ep | 4096 | CuteDSL PER-TOKEN | 246.978 | 395.715 | 396.195 | 247.266 | -37.59% |
| v3 ep | 4096 | CuteDSL W4A16 | 284.738 | 283.505 | 283.746 | 284.898 | +0.42% |
| v3 ep | 16384 | CuteDSL W4A4 | 477.635 | 790.597 | 789.573 | 477.107 | -39.58% |
| v3 ep | 16384 | CuteDSL PER-TOKEN | 607.092 | 1206.599 | 1208.344 | 607.043 | -49.72% |
| v3 ep | 16384 | CuteDSL W4A16 | 1194.792 | 1160.440 | 1154.824 | 1182.840 | +2.69% |
| v41-flash ep | 8 | CuteDSL MXFP8 | 72.785 | 106.049 | 105.888 | 72.769 | -31.32% |
| v41-flash ep | 8 | CuteDSL MXFP4x8 | 47.168 | 129.873 | 129.681 | 47.200 | -63.64% |
| v41-flash ep | 256 | CuteDSL MXFP8 | 528.979 | 530.052 | 530.531 | 528.899 | -0.26% |
| v41-flash ep | 256 | CuteDSL MXFP4x8 | 290.194 | 932.486 | 932.071 | 290.242 | -68.87% |
| v41-flash ep | 4096 | CuteDSL MXFP8 | 587.332 | 834.871 | 834.774 | 587.603 | -29.63% |
| v41-flash ep | 4096 | CuteDSL MXFP4x8 | 360.226 | 1108.424 | 1108.616 | 359.923 | -67.52% |
| v41-flash ep | 16384 | CuteDSL MXFP8 | 976.935 | 1714.253 | 1714.781 | 964.278 | -43.39% |
| v41-flash ep | 16384 | CuteDSL MXFP4x8 | 840.869 | 1505.116 | 1505.723 | 841.109 | -44.14% |
| nemo3-ultra tp | 8 | CuteDSL MXFP8 | 86.129 | 112.881 | 112.961 | 86.306 | -23.65% |
| nemo3-ultra tp | 8 | CuteDSL MXFP4x8 | 58.577 | 58.801 | 58.624 | 58.561 | -0.25% |
| nemo3-ultra tp | 256 | CuteDSL MXFP8 | 245.362 | 489.829 | 489.012 | 245.250 | -49.88% |
| nemo3-ultra tp | 256 | CuteDSL MXFP4x8 | 148.177 | 143.873 | 143.906 | 148.242 | +3.00% |
| nemo3-ultra tp | 4096 | CuteDSL MXFP8 | 495.876 | 680.165 | 680.133 | 495.812 | -27.10% |
| nemo3-ultra tp | 4096 | CuteDSL MXFP4x8 | 434.724 | 630.181 | 630.022 | 434.628 | -31.01% |
| nemo3-ultra tp | 16384 | CuteDSL MXFP8 | 1469.262 | 1509.037 | 1537.839 | 1477.307 | -3.29% |
| nemo3-ultra tp | 16384 | CuteDSL MXFP4x8 | 1412.412 | 1479.900 | 1480.287 | 1413.996 | -4.52% |
