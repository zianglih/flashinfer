# N2 coalesced width16 repeat — unpromoted

One-shot terminal audit PASS: `decode13-benchmark/independent-file-timing-audit.json` SHA256 `72a0b7ac3f118af0021805bc5400d1a3becdfc6624e996426ab940fb719ab7ae`. All 59 original sealed member files are verified, comprising 51 compact-bundle files plus eight exact SHA-identical A1 output files. All 1300 raw samples per arm and 104 finite/repeat-exact rank outputs pass, with 104 exact cross-version outputs independently against A3, A1 and same-source N1. Original archive `0f0cdcb5d0363fbf510851c82b4e1a7f3587dcea1dac76a5ff2d407ee73c816d` remains a remote seal reference: **original gzip not locally verified**. Complete original member bytes, source/cwd/cache provenance, environment, controls and process/GPU closure are verified.

N2 repeats exact `21f598d8db88df87302e96e233599eab2f6db048` on the same hu15 boot and 8 B300 GPUs, with unchanged full13/100 cold-L2 graph-CUPTI rank-MAX methodology, EP8/H7168/I2048/E256/K8, O3/AUTO4. Exact N1 source/cwd and corresponding CuTe/CUDA paths are reused; AUTO4 knob/TRITON/TORCH/output paths are fresh. No persistent CuTe hit or compile-time saving is claimed (`cute.compile` forces no-cache).

Decode T4–512: A3/N2 **1.006041049×**, 4/8 wins; historical A1/N2 **0.997024989×**. N1/N2 **0.998492154×**. All decode/prefill tactics match A3 and N1 on all ranks; only T1 changes tactic. Serial repeats do not cancel drift.

| T | A1 µs | A3 µs | N1 µs | N2 µs | A3/N2 | N1/N2 | A3 / N2 MAD µs |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 66.6560 | 68.0640 | 68.4800 | 66.8320 | 1.018434 | 1.024659 | 0.8480 / 1.0560 |
| 2 | 79.5685 | 84.8330 | 87.4560 | 86.2885 | 0.983132 | 1.013530 | 2.2080 / 0.6245 |
| 4 | 97.1200 | 97.6650 | 98.3050 | 95.5040 | 1.022627 | 1.029329 | 0.7365 / 0.8795 |
| 8 | 117.2655 | 121.6165 | 118.8325 | 120.7680 | 1.007026 | 0.983973 | 0.8955 / 0.7680 |
| 16 | 134.6410 | 135.9210 | 133.3920 | 130.7530 | 1.039525 | 1.020183 | 0.9280 / 0.8955 |
| 32 | 160.7360 | 162.1290 | 161.7605 | 162.8800 | 0.995389 | 0.993127 | 0.7520 / 0.9275 |
| 64 | 182.8005 | 184.0335 | 184.1930 | 184.4485 | 0.997750 | 0.998615 | 0.7995 / 0.8315 |
| 128 | 188.1450 | 189.2325 | 187.5375 | 190.0970 | 0.995452 | 0.986536 | 0.8485 / 0.7515 |
| 256 | 190.4660 | 190.9920 | 189.0570 | 190.9120 | 1.000419 | 0.990283 | 0.7520 / 0.7195 |
| 512 | 196.4970 | 195.8410 | 195.0090 | 197.6005 | 0.991096 | 0.986885 | 1.2160 / 0.8645 |
| 4096 | 465.0895 | 460.7050 | 459.7610 | 460.5475 | 1.000342 | 0.998292 | 3.5205 / 2.8165 |
| 8192 | 759.9215 | 798.4855 | 786.7585 | 760.9805 | 1.049285 | 1.033875 | 30.0335 / 4.1280 |
| 16384 | 1497.7690 | 1499.5880 | 1477.0970 | 1472.2310 | 1.018582 | 1.003305 | 80.8170 / 96.7700 |

The aggregate modest gain over A3 repeats, but the favorable shapes do not. T4 and T16 improve between N1/N2, while T8, T128, T256 and T512 regress. N1’s T128/T256/T512 improvements against every retained median disappear in N2. These changes survive quarter inspection with unchanged decode tactics; no isolated outlier or selected-tactic explanation is established. T16 is the most promising individual case, but it does not establish a general performance benefit.

| T | A3 quarter medians µs | N1 quarter medians µs | N2 quarter medians µs |
|---:|---|---|---|
| 4 | 97.696, 97.569, 97.856, 97.665 | 98.529, 98.208, 97.952, 98.208 | 96.161, 95.233, 95.008, 96.097 |
| 8 | 122.273, 121.312, 121.441, 121.697 | 118.849, 119.169, 118.656, 119.041 | 120.800, 121.056, 120.512, 120.609 |
| 16 | 136.481, 135.425, 135.680, 136.320 | 134.464, 133.152, 133.057, 133.505 | 131.617, 130.145, 129.985, 130.944 |
| 32 | 162.049, 162.241, 162.050, 162.145 | 161.569, 161.665, 162.304, 161.697 | 163.585, 163.521, 162.433, 162.816 |
| 64 | 184.353, 183.521, 184.609, 183.713 | 184.257, 183.905, 184.544, 184.033 | 184.577, 183.744, 184.320, 185.184 |
| 128 | 189.857, 189.153, 188.577, 189.249 | 187.841, 186.881, 187.426, 187.905 | 190.880, 190.464, 190.016, 189.921 |
| 256 | 191.361, 191.105, 190.721, 190.913 | 189.601, 189.057, 188.833, 188.865 | 190.912, 190.593, 190.305, 191.041 |
| 512 | 196.737, 195.457, 195.329, 195.936 | 195.650, 195.521, 194.657, 194.626 | 197.825, 197.568, 197.344, 197.377 |
| 8192 | 764.003, 762.850, 810.499, 826.757 | 754.757, 754.405, 793.958, 819.495 | 760.354, 760.193, 759.239, 801.959 |
| 16384 | 1357.764, 1483.333, 1558.404, 1587.460 | 1350.504, 1374.856, 1487.657, 1567.434 | 1345.866, 1367.591, 1513.100, 1554.540 |

Across retained controls, A1/N1 was0.998530620× and A1/N2 is0.997024989×; favorable comparisons use the slower A3. L1’s large T4 gain did not survive L2, and N1/N2 likewise move individual decode medians despite unchanged source. Keep all arms separately rather than average repeats or choose the most favorable control. MAD and quarter medians are descriptive, not confidence intervals.

At4K N2 is effectively flat against A3. The apparent8K +4.93% versus A3 tracks different late-run slow intervals: A3 quarters move764→827µs, N1 moves755→819µs, N2 stays near760µs for three quarters then reaches802µs. N2 is near original A1’s759.9215µs median. At16K both candidate runs have similar large quarter ramps and about97µs MAD; a1.9% median advantage over A3 is insufficient to attribute a stable kernel improvement. No traffic-sector or instruction-scheduling cause is inferred from timing.

Recommendation: leave retained3de/current PR8 as default; keep the coalesced16 experiments unpromoted. Correctness checks passed, but the repeats do not demonstrate a general gain robust to the historical control range, and the prefill evidence is temporally variable. The independent native validation is separate correctness evidence and cannot change this timing conclusion. No sanitizer was run during performance iteration.
