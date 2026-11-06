# Lane-distributed Gather4 metadata: completed screen

**Recommendation: retain and compose atop112 + universal SF, then validate the composition.**

The candidate uses each lane to load/decode one of four route IDs and four warp shuffles to publish the existing warp-uniform Gather4 coordinates. It removes the full-vector/scalar-tail split. Row/K ownership, stages, barriers, PDL, scale-factor mapping and FC2 are unchanged.

## Evidence

- Both sources have Git HEAD `fb66a27e6b40bdbbefd1b8bf0c0fc3f3ada8af90`; control is the measured112 register policy, not cleanfb66.
- Control kernel SHA256: `d9af059b4121b0c251b4fcae67a4edc4920e49ec69fcca82be7ae5984c37d310`.
- Candidate kernel SHA256: `bb8958ea8413a201e40e67e91cadc74b715a199201a6ec46d9d6d285c01f3b18`.
- Candidate full-index patch SHA256: `05a56b69ba9afab14d5f54aec649884a546da436476cd9876e44858227ee5636`.
- B300 GPUs0/3, CUDA13.2, `nvcr.io/nvidia/pytorch:26.05-py3`, CuTe DSL4.8.0. Persistent native/C++ caches retained.
- Seven selected exact tests passed, zero failures/errors/skips. Static enumeration checked219,820 row groups including partial/OOB and2CTA.
- Five jobs, four tokens, C-A-A-C,10 warmups and100 strict-CUPTI cold-L2 samples per phase;17,600 raw samples. Frozen routing/winners, noAUTO, no event fallback. NVFP4 includes input quantizer; finalize unfused.
- 10 candidate runtime guard receipts, 128 compilation observations passed; all66 FC1 observations have zero local bytes. Normal compiler options unchanged.
- Remote envelope SHA256 `b5a41f9ecb43779512e606443abfbb45dbc25f158e4061c79e0e1ff9fa8939e2`; all175 file hashes verified.

## Summary

Percentages are geometric-mean control latency / candidate latency minus1. W4A16 is unchanged diagnostic data and excluded from retention.

| Group | Affected cells | Change |
|---|---:|---:|
| All | 36 | +0.510% |
| Decode T8 | 9 | +0.007% |
| Middle T256 | 9 | -0.038% |
| Prefill | 18 | +1.038% |
| nemo3-ultra EP | 8 | +1.096% |
| v41-flash EP | 8 | +0.332% |
| kimi-k3 EP | 4 | +0.079% |
| v3 TP | 8 | +0.356% |
| v41-flash TP | 8 | +0.474% |

N3U EP W4A4 gains at4096/+7.04% and16384/+1.31% have control/candidate repeat spreads below0.12%. TP V41F W4A4/per-token gains at16384 are+1.62%/+1.52%. The largest negative cell is V41F EP MXFP4x8 at16384/−0.55%, but its candidate spread is1.51%; K3 EP at16384 and V41F EP MXFP8 at16384 also have phase drift. Treat those cells as noisy, not isolated causal claims.

## Full44-cell output

Raw phase medians are in`report/cells.csv`. Percentages below include all cells; W4A16 rows are diagnostic only.

| Model | Topology | Backend | Tokens | Control1 us | Candidate1 us | Candidate2 us | Control2 us | Change | Control spread | Candidate spread |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| kimi-k3 | EP | CuteDSL MXFP4x8 | 8 | 76.369 | 76.320 | 76.273 | 76.225 | -0.000% | 0.189% | 0.062% |
| kimi-k3 | EP | CuteDSL MXFP4x8 | 256 | 317.121 | 316.898 | 317.058 | 317.058 | +0.035% | 0.020% | 0.050% |
| kimi-k3 | EP | CuteDSL MXFP4x8 | 4096 | 395.234 | 392.579 | 392.594 | 395.122 | +0.660% | 0.028% | 0.004% |
| kimi-k3 | EP | CuteDSL MXFP4x8 | 16384 | 1074.870 | 1046.726 | 1112.438 | 1075.159 | -0.377% | 0.027% | 6.278% |
| nemo3-ultra | EP | CuteDSL W4A4 | 8 | 47.552 | 47.232 | 47.664 | 47.297 | -0.050% | 0.540% | 0.914% |
| nemo3-ultra | EP | CuteDSL PER-TOKEN | 8 | 51.137 | 51.072 | 51.153 | 51.152 | +0.063% | 0.029% | 0.157% |
| nemo3-ultra | EP | CuteDSL W4A16 | 8 | 52.496 | 52.593 | 52.513 | 52.544 | -0.062% | 0.092% | 0.151% |
| nemo3-ultra | EP | CuteDSL W4A4 | 256 | 140.913 | 140.448 | 140.321 | 140.801 | +0.336% | 0.080% | 0.091% |
| nemo3-ultra | EP | CuteDSL PER-TOKEN | 256 | 150.049 | 150.017 | 150.065 | 149.953 | -0.027% | 0.064% | 0.032% |
| nemo3-ultra | EP | CuteDSL W4A16 | 256 | 153.889 | 153.552 | 153.729 | 153.760 | +0.120% | 0.084% | 0.115% |
| nemo3-ultra | EP | CuteDSL W4A4 | 4096 | 275.474 | 257.266 | 257.570 | 275.601 | +7.039% | 0.046% | 0.118% |
| nemo3-ultra | EP | CuteDSL PER-TOKEN | 4096 | 358.546 | 358.434 | 358.611 | 358.722 | +0.031% | 0.049% | 0.049% |
| nemo3-ultra | EP | CuteDSL W4A16 | 4096 | 393.938 | 394.082 | 395.619 | 394.451 | -0.166% | 0.130% | 0.390% |
| nemo3-ultra | EP | CuteDSL W4A4 | 16384 | 717.461 | 708.197 | 707.861 | 717.092 | +1.306% | 0.051% | 0.047% |
| nemo3-ultra | EP | CuteDSL PER-TOKEN | 16384 | 922.038 | 919.525 | 920.167 | 922.598 | +0.269% | 0.061% | 0.070% |
| nemo3-ultra | EP | CuteDSL W4A16 | 16384 | 1502.938 | 1466.233 | 1513.002 | 1488.730 | +0.429% | 0.954% | 3.190% |
| v41-flash | EP | CuteDSL MXFP8 | 8 | 72.832 | 72.864 | 72.672 | 72.800 | +0.066% | 0.043% | 0.264% |
| v41-flash | EP | CuteDSL MXFP4x8 | 8 | 49.505 | 49.585 | 49.600 | 49.600 | -0.081% | 0.193% | 0.031% |
| v41-flash | EP | CuteDSL MXFP8 | 256 | 530.787 | 531.122 | 530.930 | 530.803 | -0.044% | 0.003% | 0.036% |
| v41-flash | EP | CuteDSL MXFP4x8 | 256 | 287.154 | 287.521 | 287.330 | 287.313 | -0.067% | 0.056% | 0.066% |
| v41-flash | EP | CuteDSL MXFP8 | 4096 | 575.251 | 575.236 | 574.915 | 574.787 | -0.010% | 0.081% | 0.056% |
| v41-flash | EP | CuteDSL MXFP4x8 | 4096 | 352.850 | 350.258 | 350.274 | 353.026 | +0.763% | 0.050% | 0.004% |
| v41-flash | EP | CuteDSL MXFP8 | 16384 | 976.197 | 990.774 | 926.197 | 989.797 | +2.613% | 1.393% | 6.972% |
| v41-flash | EP | CuteDSL MXFP4x8 | 16384 | 836.756 | 848.036 | 835.429 | 837.428 | -0.548% | 0.080% | 1.509% |
| v3 | TP | CuteDSL MXFP8 | 8 | 70.800 | 70.944 | 70.721 | 70.849 | -0.011% | 0.068% | 0.317% |
| v3 | TP | CuteDSL MXFP4x8 | 8 | 49.952 | 49.857 | 49.888 | 49.968 | +0.176% | 0.032% | 0.062% |
| v3 | TP | CuteDSL MXFP8 | 256 | 251.665 | 251.809 | 251.458 | 251.378 | -0.044% | 0.114% | 0.140% |
| v3 | TP | CuteDSL MXFP4x8 | 256 | 153.777 | 153.713 | 154.130 | 153.921 | -0.047% | 0.094% | 0.271% |
| v3 | TP | CuteDSL MXFP8 | 4096 | 447.987 | 447.251 | 447.555 | 448.547 | +0.193% | 0.125% | 0.068% |
| v3 | TP | CuteDSL MXFP4x8 | 4096 | 392.514 | 389.891 | 390.355 | 392.626 | +0.627% | 0.028% | 0.119% |
| v3 | TP | CuteDSL MXFP8 | 16384 | 1360.601 | 1353.001 | 1351.305 | 1358.681 | +0.554% | 0.141% | 0.126% |
| v3 | TP | CuteDSL MXFP4x8 | 16384 | 1238.760 | 1241.096 | 1220.744 | 1257.784 | +1.410% | 1.536% | 1.667% |
| v41-flash | TP | CuteDSL W4A4 | 8 | 51.856 | 51.872 | 51.921 | 51.777 | -0.154% | 0.154% | 0.093% |
| v41-flash | TP | CuteDSL PER-TOKEN | 8 | 57.408 | 57.328 | 57.361 | 57.344 | +0.056% | 0.111% | 0.057% |
| v41-flash | TP | CuteDSL W4A16 | 8 | 61.825 | 61.824 | 61.825 | 61.921 | +0.078% | 0.156% | 0.002% |
| v41-flash | TP | CuteDSL W4A4 | 256 | 316.081 | 316.289 | 316.371 | 315.890 | -0.109% | 0.060% | 0.026% |
| v41-flash | TP | CuteDSL PER-TOKEN | 256 | 321.745 | 323.601 | 323.858 | 323.298 | -0.373% | 0.483% | 0.079% |
| v41-flash | TP | CuteDSL W4A16 | 256 | 360.034 | 359.842 | 359.890 | 360.066 | +0.051% | 0.009% | 0.013% |
| v41-flash | TP | CuteDSL W4A4 | 4096 | 443.379 | 441.315 | 439.522 | 443.219 | +0.654% | 0.036% | 0.408% |
| v41-flash | TP | CuteDSL PER-TOKEN | 4096 | 556.852 | 553.763 | 553.364 | 556.899 | +0.598% | 0.009% | 0.072% |
| v41-flash | TP | CuteDSL W4A16 | 4096 | 657.892 | 633.892 | 638.083 | 637.091 | +1.796% | 3.265% | 0.661% |
| v41-flash | TP | CuteDSL W4A4 | 16384 | 1029.797 | 1013.174 | 1013.365 | 1029.622 | +1.622% | 0.017% | 0.019% |
| v41-flash | TP | CuteDSL PER-TOKEN | 16384 | 1498.776 | 1474.456 | 1474.105 | 1494.490 | +1.516% | 0.287% | 0.024% |
| v41-flash | TP | CuteDSL W4A16 | 16384 | 2187.277 | 2166.605 | 2192.893 | 2157.709 | -0.333% | 1.370% | 1.213% |

## Source and limits

The isolated metadata review copy was removed after hash-verified composition into `/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-fc1-gather-composed-review` over retained7106faf. The original source is preserved by `candidate.patch` and all source hashes. This screen isolates metadata on112; it does not yet measure combination with universal SF or the full13-token matrix. No sanitizer run. GPUs0/3 released after all jobs completed. See`AUDIT.md` and`codegen-comparison.json` for executable SASS evidence; all four captured FC2 streams are identical to112.
