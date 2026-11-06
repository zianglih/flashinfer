# Final SF epilogue results

Kernel `924be385` on `2d60c885` simplifies SF-row address calculation and extracts common quantization parameters. SF32 nongated output reuses its block parameters across both existing half stores. Original valid-row/channel predicates, arithmetic order, scale ownership and synchronization are preserved; no tactics or public APIs change.

- Qualification:96 byte-exact changing-route replays,48 GEMM/10 combine codegen pairs; all8 per-token FC1 encoded SASS streams and24 FC2 streams remain unchanged. No extra branch sites or local/stack/uniform spill growth. Scaled Relu2 paths remove201–365 static non-NOP sites; registers decrease by0–2.
- Matched performance:72 cells/28,800 CUPTI samples across15 EP/TP jobs, all four models and supported modes. Standard100-sample medians,10 warmups,coldL2,public functional API,frozen83df winners/routes,C-A-A-C. Scaled GM+0.133%,decode−0.056%,prefill+0.323%,EP+0.214%,TP+0.040%. Treat this as near-neutral performance.
- Stable small tradeoff: V3 EP W4A4 T4−0.458%, consistent with preceding formula screens. N3U EP per-token T16384 is restored to−0.009% after the rejected outer-guard version’s−0.960%.
- Mixed prefill evidence: N3U EP MXFP4x8 T16384 remains−4.604% in the full screen. The same-GPU confirmation is+2.364%, with2.239%/3.789% control/candidate pass spreads and first25+0.203% versus last50−4.756%. The two results remain separate; no consistent causal loss or large gain is established.
- Unchanged sanity arms: allper-token+0.022%,W4A16+0.005%. No sanitizer; no external baseline reruns or autotuning.

| Topology | Model | Tokens | Backend | Control us | Candidate us | Change |
|---|---|---:|---|---:|---:|---:|
| EP | v3 | 4 | CuteDSL W4A4 | 47.032 | 47.249 | -0.458% |
| EP | v3 | 4 | CuteDSL PER-TOKEN | 50.488 | 50.560 | -0.142% |
| EP | v3 | 4 | CuteDSL W4A16 | 51.264 | 51.240 | +0.047% |
| EP | v3 | 16384 | CuteDSL W4A4 | 479.938 | 478.891 | +0.219% |
| EP | v3 | 16384 | CuteDSL PER-TOKEN | 614.795 | 614.619 | +0.029% |
| EP | v3 | 16384 | CuteDSL W4A16 | 1150.867 | 1141.707 | +0.802% |
| EP | v3 | 4 | CuteDSL MXFP8 | 68.304 | 68.336 | -0.047% |
| EP | v3 | 4 | CuteDSL MXFP4x8 | 46.864 | 46.896 | -0.068% |
| EP | v3 | 16384 | CuteDSL MXFP8 | 724.589 | 715.694 | +1.243% |
| EP | v3 | 16384 | CuteDSL MXFP4x8 | 675.260 | 670.085 | +0.772% |
| EP | v41-flash | 4 | CuteDSL W4A4 | 33.792 | 33.808 | -0.048% |
| EP | v41-flash | 4 | CuteDSL PER-TOKEN | 38.936 | 38.912 | +0.062% |
| EP | v41-flash | 4 | CuteDSL W4A16 | 38.792 | 38.784 | +0.021% |
| EP | v41-flash | 16384 | CuteDSL W4A4 | 562.603 | 561.314 | +0.230% |
| EP | v41-flash | 16384 | CuteDSL PER-TOKEN | 744.074 | 742.603 | +0.198% |
| EP | v41-flash | 16384 | CuteDSL W4A16 | 1536.010 | 1476.019 | +4.064% |
| EP | v41-flash | 4 | CuteDSL MXFP8 | 49.832 | 49.864 | -0.064% |
| EP | v41-flash | 4 | CuteDSL MXFP4x8 | 34.080 | 34.064 | +0.047% |
| EP | v41-flash | 16384 | CuteDSL MXFP8 | 972.122 | 957.395 | +1.538% |
| EP | v41-flash | 16384 | CuteDSL MXFP4x8 | 832.926 | 837.789 | -0.580% |
| EP | kimi-k3 | 4 | CuteDSL W4A4 | 52.856 | 52.888 | -0.060% |
| EP | kimi-k3 | 4 | CuteDSL PER-TOKEN | 56.136 | 56.264 | -0.227% |
| EP | kimi-k3 | 4 | CuteDSL W4A16 | 58.040 | 57.984 | +0.096% |
| EP | kimi-k3 | 16384 | CuteDSL W4A4 | 729.444 | 734.111 | -0.636% |
| EP | kimi-k3 | 16384 | CuteDSL PER-TOKEN | 1018.447 | 1013.711 | +0.467% |
| EP | kimi-k3 | 16384 | CuteDSL W4A16 | 1983.669 | 1976.939 | +0.340% |
| EP | kimi-k3 | 4 | CuteDSL MXFP4x8 | 50.632 | 50.624 | +0.016% |
| EP | kimi-k3 | 16384 | CuteDSL MXFP4x8 | 1014.781 | 971.890 | +4.413% |
| EP | nemo3-ultra | 4 | CuteDSL W4A4 | 35.680 | 35.744 | -0.179% |
| EP | nemo3-ultra | 4 | CuteDSL PER-TOKEN | 42.096 | 42.088 | +0.018% |
| EP | nemo3-ultra | 4 | CuteDSL W4A16 | 42.080 | 42.080 | +0.001% |
| EP | nemo3-ultra | 16384 | CuteDSL W4A4 | 528.653 | 522.250 | +1.226% |
| EP | nemo3-ultra | 16384 | CuteDSL PER-TOKEN | 857.267 | 857.347 | -0.009% |
| EP | nemo3-ultra | 16384 | CuteDSL W4A16 | 1449.796 | 1533.389 | -5.452% |
| EP | nemo3-ultra | 4 | CuteDSL MXFP8 | 49.552 | 49.512 | +0.080% |
| EP | nemo3-ultra | 4 | CuteDSL MXFP4x8 | 35.544 | 35.592 | -0.136% |
| EP | nemo3-ultra | 16384 | CuteDSL MXFP8 | 836.561 | 809.081 | +3.396% |
| EP | nemo3-ultra | 16384 | CuteDSL MXFP4x8 | 735.506 | 771.000 | -4.604% |
| TP | v3 | 4 | CuteDSL W4A4 | 36.096 | 36.137 | -0.113% |
| TP | v3 | 4 | CuteDSL PER-TOKEN | 40.512 | 40.504 | +0.019% |
| TP | v3 | 4 | CuteDSL W4A16 | 39.912 | 39.856 | +0.142% |
| TP | v3 | 16384 | CuteDSL W4A4 | 1351.513 | 1351.057 | +0.034% |
| TP | v3 | 16384 | CuteDSL PER-TOKEN | 1716.659 | 1716.739 | -0.005% |
| TP | v3 | 16384 | CuteDSL W4A16 | 2235.014 | 2227.895 | +0.320% |
| TP | v3 | 4 | CuteDSL MXFP8 | 46.064 | 46.144 | -0.173% |
| TP | v3 | 4 | CuteDSL MXFP4x8 | 35.553 | 35.496 | +0.158% |
| TP | v3 | 16384 | CuteDSL MXFP8 | 1620.078 | 1620.438 | -0.022% |
| TP | v3 | 16384 | CuteDSL MXFP4x8 | 1561.901 | 1561.509 | +0.025% |
| TP | v41-flash | 4 | CuteDSL W4A4 | 35.529 | 35.616 | -0.246% |
| TP | v41-flash | 4 | CuteDSL PER-TOKEN | 40.504 | 40.576 | -0.177% |
| TP | v41-flash | 4 | CuteDSL W4A16 | 41.936 | 41.952 | -0.038% |
| TP | v41-flash | 16384 | CuteDSL W4A4 | 1046.094 | 1046.230 | -0.013% |
| TP | v41-flash | 16384 | CuteDSL PER-TOKEN | 1349.008 | 1348.688 | +0.024% |
| TP | v41-flash | 16384 | CuteDSL W4A16 | 2152.731 | 2151.290 | +0.067% |
| TP | kimi-k3 | 4 | CuteDSL W4A4 | 42.649 | 42.656 | -0.017% |
| TP | kimi-k3 | 4 | CuteDSL PER-TOKEN | 45.816 | 45.736 | +0.175% |
| TP | kimi-k3 | 4 | CuteDSL W4A16 | 50.616 | 50.640 | -0.047% |
| TP | kimi-k3 | 16384 | CuteDSL W4A4 | 1657.210 | 1656.906 | +0.018% |
| TP | kimi-k3 | 16384 | CuteDSL PER-TOKEN | 2260.485 | 2260.878 | -0.017% |
| TP | kimi-k3 | 16384 | CuteDSL W4A16 | 2984.146 | 2983.545 | +0.020% |
| TP | kimi-k3 | 4 | CuteDSL MXFP4x8 | 40.104 | 40.136 | -0.079% |
| TP | kimi-k3 | 16384 | CuteDSL MXFP4x8 | 1972.519 | 1966.392 | +0.312% |
| TP | nemo3-ultra | 4 | CuteDSL W4A4 | 38.160 | 38.216 | -0.146% |
| TP | nemo3-ultra | 4 | CuteDSL PER-TOKEN | 42.664 | 42.656 | +0.019% |
| TP | nemo3-ultra | 4 | CuteDSL W4A16 | 47.873 | 47.952 | -0.165% |
| TP | nemo3-ultra | 16384 | CuteDSL W4A4 | 1323.602 | 1311.179 | +0.948% |
| TP | nemo3-ultra | 16384 | CuteDSL PER-TOKEN | 2051.073 | 2052.601 | -0.074% |
| TP | nemo3-ultra | 16384 | CuteDSL W4A16 | 2274.955 | 2272.690 | +0.100% |
| TP | nemo3-ultra | 4 | CuteDSL MXFP8 | 50.848 | 50.840 | +0.016% |
| TP | nemo3-ultra | 4 | CuteDSL MXFP4x8 | 36.449 | 36.376 | +0.198% |
| TP | nemo3-ultra | 16384 | CuteDSL MXFP8 | 1556.090 | 1563.925 | -0.501% |
| TP | nemo3-ultra | 16384 | CuteDSL MXFP4x8 | 1481.724 | 1471.418 | +0.700% |

The full table is unchanged by the separate confirmation. Positive percentages mean the candidate is faster. Strata are diagnostic and do not replace standard medians. Fullsource/cache/routes/sample provenance: `perf-evidence/`; exact/codegen provenance:`evidence/`; independent audit receipts are stored alongside.

Decision: retain as a general instruction simplification with near-neutral aggregate timing, with the measured tradeoff and uncertainty recorded. No large speedup claim.
