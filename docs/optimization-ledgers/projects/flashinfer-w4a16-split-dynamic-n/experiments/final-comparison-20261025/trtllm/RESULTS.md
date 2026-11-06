# Native backend comparison

Commit `97e8d0c8bb86b352ccb42f2654ddc2ab9a8e6939` on hu-pdx-7 / GPU-edf3141e-7e43-ff20-2c4e-a0e11b5ae000. All medians in microseconds; native cold-L2 CUDA-graph CUPTI, 10 warmups / 100 samples, independent AUTO per sweep. Same-GPU A-B-C-C-B-A order. T1/T2 are shown but excluded from every aggregate.

| T | CuTe W4A16 R1 | CuTe W4A16 R2 | TRTLLM quant excluded R1 | TRTLLM quant excluded R2 | TRTLLM quant included R1 | TRTLLM quant included R2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 31.5210 | 31.5520 | 24.5440 | 26.5280 | 25.1200 | 24.8485 |
| 2 | 37.8565 | 36.8325 | 33.2800 | 33.3445 | 35.1680 | 37.4720 |
| 4 | 51.1845 | 50.9925 | 48.0960 | 52.1770 | 50.8965 | 50.3685 |
| 8 | 66.0810 | 66.8645 | 62.2720 | 61.8410 | 62.9600 | 63.3610 |
| 16 | 75.5850 | 75.5045 | 72.8480 | 73.4570 | 74.0810 | 73.8570 |
| 32 | 107.3605 | 107.5205 | 103.5690 | 103.6650 | 105.0885 | 105.4090 |
| 64 | 142.2735 | 141.6325 | 138.5135 | 139.5530 | 141.4730 | 140.5770 |
| 128 | 144.3215 | 144.4490 | 140.4495 | 141.0735 | 142.8650 | 143.9215 |
| 256 | 153.0890 | 153.3130 | 149.7295 | 150.6260 | 153.7285 | 152.7370 |
| 512 | 156.6895 | 156.6735 | 155.6655 | 155.6180 | 158.4490 | 158.6735 |
| 4096 | 295.8585 | 294.5305 | 212.0660 | 212.4665 | 225.3775 | 225.4900 |
| 8192 | 621.9085 | 587.5090 | 331.2345 | 330.9465 | 357.1540 | 357.0270 |
| 16384 | 1215.4500 | 1190.1060 | 582.0210 | 582.6775 | 632.8675 | 633.0295 |

Paired ratio is TRTLLM latency / CuTe latency; above 1 means CuTe faster.

| T | Quant excluded | Quant included |
| ---: | ---: | ---: |
| 1 | 0.809117x | 0.792221x |
| 2 | 0.892109x | 0.972168x |
| 4 | 0.980554x | 0.991063x |
| 8 | 0.933574x | 0.950183x |
| 16 | 0.968325x | 0.979141x |
| 32 | 0.964413x | 0.979599x |
| 64 | 0.979427x | 0.993460x |
| 128 | 0.974900x | 0.993123x |
| 256 | 0.980262x | 1.000202x |
| 512 | 0.993364x | 1.011997x |
| 4096 | 0.719074x | 0.763681x |
| 8192 | 0.547742x | 0.590756x |
| 16384 | 0.484197x | 0.526268x |

| Group | Quant excluded R1 | R2 | Paired | Quant included R1 | R2 | Paired |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| overall | 0.835537x | 0.849304x | 0.842392x | 0.866573x | 0.871993x | 0.869279x |
| decode | 0.965947x | 0.977504x | 0.971708x | 0.988076x | 0.986314x | 0.987195x |
| prefill | 0.567544x | 0.583779x | 0.575604x | 0.610722x | 0.627828x | 0.619216x |

Verified all 7,800 raw samples against the native medians, all source hashes against the pinned commit, the same GPU UUID/power limit, identical runtime/cache metadata and routing histograms, native timing input dtypes/shapes, all 78 saved tactic-cache hashes, and no competing compute processes before each sweep.

- Six sweeps/two repeats per backend are not a statistical significance claim.
- Normal AUTO selects independently in each fresh process; timing includes selection variation.
- Native backend intermediate precision, weight quantization/scales, route-weight precision and finalize differ.
- Quant included times FP4 packing/block-scale generation using precomputed tensor-global scale; global amax/calibration excluded.
- Quant included minus excluded is not an isolated quantization cost because AUTO can differ.
- Single-GPU EP8 simulation excludes inter-GPU communication; no new correctness or sanitizer run.
