# Combined epilogue R1 screen

Frozen kernel `9cb4cc76` on2d60: SF-row formula plus quantization-parameter sharing with an outer valid-row guard. This screen is preserved; the next candidate restores the original guard placement.

- Fifteen matched C-A-A-C public-API jobs across EP/TP and four models;72 cells,28,800 strict CUPTI cold-L2 samples,10 warmups. Saved83df winners/routes, no autotuning or external baseline rerun.
- Scaled modes: +0.165% geomean; decode −0.005%, prefill +0.336%; EP +0.299%, TP +0.011%. Forty-four affected FC1 cells: +0.194%.
- N3U EP per-token T16384 is a credible −0.960% cost: both candidate passes slower than both controls, control/candidate spreads0.078%/0.024%, all diagnostic strata around−0.92% to−1.00%. Its extra branch/control work motivates the original-guard follow-up.
- V3 EP MXFP4x8 T16384 standard median is−1.748%; candidate pass spread4.142% and first/last quartile signs differ. Keep the result, but do not claim a stable source-specific slowdown.
- N3U TP W4A4 T16384 is consistently+2.125%, with0.027%/0.072% control/candidate spread and all strata around+2.08% to+2.24%.
- Gated per-token sanity +0.057%; unchanged W4A16 sanity−0.297%. No sanitizer.

| Topology | Model | Tokens | Backend | Control us | Candidate us | Change |
|---|---|---:|---|---:|---:|---:|
| EP | v3 | 4 | CuteDSL W4A4 | 47.096 | 47.272 | -0.372% |
| EP | v3 | 4 | CuteDSL PER-TOKEN | 50.504 | 50.528 | -0.047% |
| EP | v3 | 4 | CuteDSL W4A16 | 51.232 | 51.240 | -0.016% |
| EP | v3 | 16384 | CuteDSL W4A4 | 479.827 | 478.627 | +0.251% |
| EP | v3 | 16384 | CuteDSL PER-TOKEN | 615.427 | 615.587 | -0.026% |
| EP | v3 | 16384 | CuteDSL W4A16 | 1158.628 | 1176.506 | -1.520% |
| EP | v3 | 4 | CuteDSL MXFP8 | 68.360 | 68.392 | -0.047% |
| EP | v3 | 4 | CuteDSL MXFP4x8 | 46.896 | 46.928 | -0.068% |
| EP | v3 | 16384 | CuteDSL MXFP8 | 720.406 | 727.358 | -0.956% |
| EP | v3 | 16384 | CuteDSL MXFP4x8 | 658.844 | 670.562 | -1.748% |
| EP | v41-flash | 4 | CuteDSL W4A4 | 33.896 | 33.816 | +0.238% |
| EP | v41-flash | 4 | CuteDSL PER-TOKEN | 38.937 | 38.936 | +0.002% |
| EP | v41-flash | 4 | CuteDSL W4A16 | 38.792 | 38.784 | +0.020% |
| EP | v41-flash | 16384 | CuteDSL W4A4 | 561.818 | 561.162 | +0.117% |
| EP | v41-flash | 16384 | CuteDSL PER-TOKEN | 742.963 | 742.675 | +0.039% |
| EP | v41-flash | 16384 | CuteDSL W4A16 | 1478.542 | 1490.748 | -0.819% |
| EP | v41-flash | 4 | CuteDSL MXFP8 | 49.872 | 49.872 | +0.000% |
| EP | v41-flash | 4 | CuteDSL MXFP4x8 | 34.080 | 34.048 | +0.094% |
| EP | v41-flash | 16384 | CuteDSL MXFP8 | 967.376 | 939.620 | +2.954% |
| EP | v41-flash | 16384 | CuteDSL MXFP4x8 | 833.810 | 823.941 | +1.198% |
| EP | kimi-k3 | 4 | CuteDSL W4A4 | 52.840 | 52.921 | -0.152% |
| EP | kimi-k3 | 4 | CuteDSL PER-TOKEN | 56.240 | 56.176 | +0.114% |
| EP | kimi-k3 | 4 | CuteDSL W4A16 | 57.952 | 57.833 | +0.207% |
| EP | kimi-k3 | 16384 | CuteDSL W4A4 | 737.921 | 707.154 | +4.351% |
| EP | kimi-k3 | 16384 | CuteDSL PER-TOKEN | 1014.055 | 1012.023 | +0.201% |
| EP | kimi-k3 | 16384 | CuteDSL W4A16 | 1977.970 | 1976.801 | +0.059% |
| EP | kimi-k3 | 4 | CuteDSL MXFP4x8 | 50.656 | 50.600 | +0.110% |
| EP | kimi-k3 | 16384 | CuteDSL MXFP4x8 | 1034.980 | 1016.718 | +1.796% |
| EP | nemo3-ultra | 4 | CuteDSL W4A4 | 35.648 | 35.648 | -0.002% |
| EP | nemo3-ultra | 4 | CuteDSL PER-TOKEN | 41.992 | 41.976 | +0.038% |
| EP | nemo3-ultra | 4 | CuteDSL W4A16 | 42.160 | 42.072 | +0.210% |
| EP | nemo3-ultra | 16384 | CuteDSL W4A4 | 527.433 | 521.210 | +1.194% |
| EP | nemo3-ultra | 16384 | CuteDSL PER-TOKEN | 857.155 | 865.467 | -0.960% |
| EP | nemo3-ultra | 16384 | CuteDSL W4A16 | 1496.500 | 1542.621 | -2.990% |
| EP | nemo3-ultra | 4 | CuteDSL MXFP8 | 49.576 | 49.472 | +0.209% |
| EP | nemo3-ultra | 4 | CuteDSL MXFP4x8 | 35.568 | 35.592 | -0.068% |
| EP | nemo3-ultra | 16384 | CuteDSL MXFP8 | 843.936 | 836.343 | +0.908% |
| EP | nemo3-ultra | 16384 | CuteDSL MXFP4x8 | 763.799 | 765.536 | -0.227% |
| TP | v3 | 4 | CuteDSL W4A4 | 36.128 | 36.184 | -0.155% |
| TP | v3 | 4 | CuteDSL PER-TOKEN | 40.480 | 40.408 | +0.178% |
| TP | v3 | 4 | CuteDSL W4A16 | 39.889 | 39.936 | -0.118% |
| TP | v3 | 16384 | CuteDSL W4A4 | 1352.137 | 1350.978 | +0.086% |
| TP | v3 | 16384 | CuteDSL PER-TOKEN | 1716.956 | 1716.693 | +0.015% |
| TP | v3 | 16384 | CuteDSL W4A16 | 2232.665 | 2228.554 | +0.185% |
| TP | v3 | 4 | CuteDSL MXFP8 | 46.113 | 46.201 | -0.191% |
| TP | v3 | 4 | CuteDSL MXFP4x8 | 35.528 | 35.552 | -0.066% |
| TP | v3 | 16384 | CuteDSL MXFP8 | 1619.140 | 1618.887 | +0.016% |
| TP | v3 | 16384 | CuteDSL MXFP4x8 | 1561.548 | 1562.758 | -0.077% |
| TP | v41-flash | 4 | CuteDSL W4A4 | 35.504 | 35.528 | -0.067% |
| TP | v41-flash | 4 | CuteDSL PER-TOKEN | 40.601 | 40.521 | +0.197% |
| TP | v41-flash | 4 | CuteDSL W4A16 | 41.912 | 41.832 | +0.191% |
| TP | v41-flash | 16384 | CuteDSL W4A4 | 1045.583 | 1044.471 | +0.106% |
| TP | v41-flash | 16384 | CuteDSL PER-TOKEN | 1349.784 | 1349.488 | +0.022% |
| TP | v41-flash | 16384 | CuteDSL W4A16 | 2140.641 | 2147.061 | -0.299% |
| TP | kimi-k3 | 4 | CuteDSL W4A4 | 42.688 | 42.664 | +0.057% |
| TP | kimi-k3 | 4 | CuteDSL PER-TOKEN | 45.824 | 45.832 | -0.018% |
| TP | kimi-k3 | 4 | CuteDSL W4A16 | 50.568 | 50.696 | -0.252% |
| TP | kimi-k3 | 16384 | CuteDSL W4A4 | 1656.186 | 1657.202 | -0.061% |
| TP | kimi-k3 | 16384 | CuteDSL PER-TOKEN | 2261.894 | 2261.830 | +0.003% |
| TP | kimi-k3 | 16384 | CuteDSL W4A16 | 2987.971 | 2985.875 | +0.070% |
| TP | kimi-k3 | 4 | CuteDSL MXFP4x8 | 40.057 | 40.113 | -0.140% |
| TP | kimi-k3 | 16384 | CuteDSL MXFP4x8 | 1957.999 | 1964.973 | -0.355% |
| TP | nemo3-ultra | 4 | CuteDSL W4A4 | 38.160 | 38.193 | -0.086% |
| TP | nemo3-ultra | 4 | CuteDSL PER-TOKEN | 42.712 | 42.720 | -0.018% |
| TP | nemo3-ultra | 4 | CuteDSL W4A16 | 47.857 | 47.816 | +0.085% |
| TP | nemo3-ultra | 16384 | CuteDSL W4A4 | 1323.371 | 1295.835 | +2.125% |
| TP | nemo3-ultra | 16384 | CuteDSL PER-TOKEN | 2050.609 | 2051.729 | -0.055% |
| TP | nemo3-ultra | 16384 | CuteDSL W4A16 | 2280.839 | 2274.163 | +0.294% |
| TP | nemo3-ultra | 4 | CuteDSL MXFP8 | 50.864 | 50.808 | +0.110% |
| TP | nemo3-ultra | 4 | CuteDSL MXFP4x8 | 36.400 | 36.400 | +0.000% |
| TP | nemo3-ultra | 16384 | CuteDSL MXFP8 | 1528.174 | 1540.357 | -0.791% |
| TP | nemo3-ultra | 16384 | CuteDSL MXFP4x8 | 1485.379 | 1493.181 | -0.522% |

Each arm is the geometric mean of its two standard100-sample medians; positive means candidate faster. First/last strata are diagnostics only. Raw medians, samples, source, cache and routing proofs are retained in `perf-evidence/`;1,952 member hashes are verified by `perf-evidence-verification.json`. Independent audit: `scheduler-perf-review.json`. Exact/codegen qualification is summarized in `GATE.md`; the earlier SF16 compile failure is retained separately.

Decision: do not retain this outer-guard form; evaluate the universally simpler original-guard form without changing arithmetic, layouts or tactics.
