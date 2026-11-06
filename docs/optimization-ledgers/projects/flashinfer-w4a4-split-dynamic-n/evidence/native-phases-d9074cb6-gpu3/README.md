# Native candidate phase diagnostic

Candidate `d9074cb6e9e934d387e358a069e90ddf084f5ef7`, C1 B200 GPU3, image `nvcr.io/nvidia/pytorch:26.05-py3`. Native T16384 routing, H7168/I2048, top-k8, 32 local experts, deterministic unfused finalize. Each fixed tactic uses 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples; all samples, histograms, source and environment metadata are archived. This is diagnostic evidence, not primary retention data.

The paired baseline diagnostic is `../native-baseline-phase-gpu3-a65d5b09`: FC1 218.065us, FC2 128.9125us, full 480.401us. All 11 current tactics were measured with the same actual routed inputs. AUTO's selected N128/M256 FC1 and N128/M128 FC2 is near the fastest full-pipeline tactic; changing the tactic list alone does not close the kernel-time gap. Isolated phase times need not sum to whole-pipeline time.

| Route N | FC1 M | FC2 M | FC1 us | FC2 us | Whole us |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 128 | 128 | 1643.748 | 1134.499 | 2891.046 |
| 32 | 128 | 128 | 880.562 | 621.121 | 1613.700 |
| 64 | 128 | 128 | 549.730 | 365.921 | 1028.930 |
| 128 | 128 | 128 | 437.569 | 201.841 | 750.770 |
| 128 | 128 | 256 | 436.864 | 205.281 | 762.066 |
| 128 | 256 | 128 | 335.985 | 205.536 | 654.962 |
| 128 | 256 | 256 | 335.249 | 216.465 | 661.138 |
| 256 | 128 | 128 | 455.937 | 192.065 | 774.082 |
| 256 | 128 | 256 | 455.682 | 199.809 | 778.962 |
| 256 | 256 | 128 | 336.801 | 190.129 | 656.369 |
| 256 | 256 | 256 | 335.745 | 202.144 | 662.737 |

Archive SHA256: `0405668cf30a41615f821242cf802158dc57f07295eecea0355e9ca318ed8f4b`. Primary NVFP4 B1 remains the existing GPU0 472.464us result; this diagnostic does not replace or repeat that baseline sweep.
