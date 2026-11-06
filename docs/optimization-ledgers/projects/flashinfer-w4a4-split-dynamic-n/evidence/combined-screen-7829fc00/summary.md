# Candidate 7829fc00dc7121341cc40cd4190660507e006490 primary screen

Baseline: `a65d5b09e7e4c4c5c160b0161c48becd100b3970`. One complete candidate sweep versus retained B1; these are screening ratios, not completed ABBA retention results. Tokens 1 and 2 are reported but excluded from all aggregate ratios.

Image `nvcr.io/nvidia/pytorch:26.05-py3`; B200, GPU0 for NVFP4 and GPU1 for the other two modes. Native AUTO, unfused deterministic finalize, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. All 39 token rows, routing histograms, source/preparation contracts, environment fields and AUTO cache hashes verified.

## NVFP4 W4A4, no per-token scale

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 27.439 | 28.672 | 0.9570x | excluded |
| 2 | 37.184 | 37.824 | 0.9831x | excluded |
| 4 | 52.512 | 56.367 | 0.9316x | yes |
| 8 | 69.792 | 74.720 | 0.9340x | yes |
| 16 | 79.200 | 83.504 | 0.9485x | yes |
| 32 | 111.120 | 115.391 | 0.9630x | yes |
| 64 | 143.999 | 145.088 | 0.9925x | yes |
| 128 | 147.648 | 148.608 | 0.9935x | yes |
| 256 | 154.928 | 156.191 | 0.9919x | yes |
| 512 | 157.408 | 158.272 | 0.9945x | yes |
| 4096 | 208.463 | 221.919 | 0.9394x | yes |
| 8192 | 297.456 | 351.200 | 0.8470x | yes |
| 16384 | 472.464 | 621.646 | 0.7600x | yes |

decode **0.968347x**, prefill **0.845621x**, overall **0.933210x**.

## MXFP8 E4M3 × MXFP8 E4M3

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 43.520 | 41.648 | 1.0449x | excluded |
| 2 | 55.520 | 55.888 | 0.9934x | excluded |
| 4 | 81.584 | 84.992 | 0.9599x | yes |
| 8 | 110.209 | 111.648 | 0.9871x | yes |
| 16 | 126.048 | 124.433 | 1.0130x | yes |
| 32 | 182.945 | 183.248 | 0.9983x | yes |
| 64 | 241.760 | 242.960 | 0.9951x | yes |
| 128 | 250.289 | 250.528 | 0.9990x | yes |
| 256 | 266.881 | 263.840 | 1.0115x | yes |
| 512 | 268.400 | 266.753 | 1.0062x | yes |
| 4096 | 359.617 | 337.585 | 1.0653x | yes |
| 8192 | 536.593 | 510.529 | 1.0511x | yes |
| 16384 | 857.874 | 909.169 | 0.9436x | yes |

decode **0.996139x**, prefill **1.018482x**, overall **1.002184x**.

## MXFP4 weights × MXFP8 E4M3 activations

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 40.896 | 33.696 | 1.2137x | excluded |
| 2 | 51.200 | 44.032 | 1.1628x | excluded |
| 4 | 65.440 | 67.952 | 0.9630x | yes |
| 8 | 85.728 | 86.304 | 0.9933x | yes |
| 16 | 90.641 | 95.072 | 0.9534x | yes |
| 32 | 133.873 | 134.784 | 0.9932x | yes |
| 64 | 169.473 | 177.264 | 0.9560x | yes |
| 128 | 177.825 | 182.176 | 0.9761x | yes |
| 256 | 185.649 | 191.104 | 0.9715x | yes |
| 512 | 188.369 | 193.904 | 0.9715x | yes |
| 4096 | 303.281 | 292.529 | 1.0368x | yes |
| 8192 | 461.121 | 473.473 | 0.9739x | yes |
| 16384 | 776.002 | 824.929 | 0.9407x | yes |

decode **0.972155x**, prefill **0.982986x**, overall **0.975097x**.
