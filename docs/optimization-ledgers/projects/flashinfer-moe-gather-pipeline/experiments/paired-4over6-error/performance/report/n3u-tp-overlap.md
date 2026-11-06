# N3U TP per-token overlap, existing42-cell screen

All values below are medians of the100 original per-iteration observations in each phase. Starts/ends are relative to that iteration’s first activity; no durations or samples are replaced. GPU3 is the same UUID throughout. All48 clockquartiles for these three CuTe cells are present,2032MHz/reason0.

| T | Phase | E2Eus | Inputquantus | FC1end | Interquantstart | Interquantend | Interquantduration | Interquantexposed | FC2start | FC2duration | FC2exposed | Q/FC2overlap | FC2tailafterQ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0-control | 124.017 | 2.800 | 64.001 | 56.928 | 71.376 | 14.688 | 6.880 | 66.305 | 50.400 | 44.944 | 4.896 | 44.944 |
| 32 | 1-candidate | 124.097 | 2.784 | 64.000 | 56.784 | 71.792 | 15.408 | 7.551 | 65.792 | 50.960 | 44.832 | 5.824 | 44.832 |
| 32 | 2-candidate | 124.913 | 2.784 | 63.889 | 56.640 | 72.160 | 15.889 | 8.256 | 65.632 | 52.224 | 44.992 | 6.576 | 44.992 |
| 32 | 3-control | 123.520 | 2.816 | 63.968 | 56.880 | 70.944 | 14.273 | 6.592 | 66.257 | 49.856 | 44.912 | 4.593 | 44.912 |
| 4096 | 0-control | 555.123 | 11.456 | 185.202 | 169.249 | 312.018 | 142.529 | 127.089 | 271.778 | 204.546 | 164.641 | 39.809 | 164.641 |
| 4096 | 1-candidate | 571.299 | 12.000 | 185.666 | 169.760 | 328.001 | 158.017 | 141.856 | 187.089 | 305.154 | 164.640 | 140.417 | 164.641 |
| 4096 | 2-candidate | 571.813 | 12.000 | 185.873 | 169.730 | 328.067 | 158.082 | 141.905 | 187.313 | 305.219 | 164.642 | 140.417 | 164.642 |
| 4096 | 3-control | 555.667 | 11.488 | 185.185 | 169.233 | 312.306 | 143.024 | 127.137 | 272.178 | 204.705 | 164.673 | 40.080 | 164.673 |
| 16384 | 0-control | 1800.969 | 36.736 | 595.203 | 576.082 | 1041.429 | 465.298 | 445.842 | 994.453 | 524.947 | 478.066 | 46.736 | 478.066 |
| 16384 | 1-candidate | 1870.314 | 41.280 | 599.603 | 580.644 | 1110.166 | 529.731 | 510.451 | 600.995 | 986.997 | 478.355 | 509.043 | 478.354 |
| 16384 | 2-candidate | 1870.770 | 41.281 | 599.878 | 580.645 | 1110.874 | 530.245 | 510.564 | 601.206 | 986.969 | 478.373 | 509.045 | 478.373 |
| 16384 | 3-control | 1801.930 | 36.736 | 595.203 | 576.067 | 1042.693 | 466.578 | 447.251 | 995.382 | 526.051 | 477.763 | 48.416 | 477.763 |

Candidate FC2 starts earlier and overlaps almost the entire intermediate quantizer in the two prefill cells. Its longer activity duration is predominantly overlap/wait time: the exposed FC2 extension and tail after quantization remain near the control. The whole-chain loss is concentrated in the intermediate quantizer’s exposed interval, plus a smaller initial quantizer increase. This establishes the timing relationship, not its cause. PDL resource/cache interference and a changed arithmetic dependency schedule remain hypotheses; these data do not isolate them.

Source component samples SHA256 `68cefcbe7d4455d50c4cb60361912c59aa333bb3409b1011f12f67bd18aacb78`; analysis `f131bea3fab359a95fbdee5d145ebf03185286774670a7147b33d6eea9b04cab`; raw receipt `9b52a888979b2a1a8ed762bb265c62410f8cf68b4474426b3461d6fc04835483`.
