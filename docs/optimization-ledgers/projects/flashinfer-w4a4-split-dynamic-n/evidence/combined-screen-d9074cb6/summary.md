# Candidate d9074cb6e9e934d387e358a069e90ddf084f5ef7 primary screen

Baseline: `a65d5b09e7e4c4c5c160b0161c48becd100b3970`. One complete candidate sweep versus retained B1; these are screening ratios, not completed ABBA retention results. Tokens 1 and 2 are reported but excluded from all aggregate ratios.

Image `nvcr.io/nvidia/pytorch:26.05-py3`; B200, GPU0 for NVFP4 and GPU1 for the other two modes. Native AUTO, unfused deterministic finalize, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. All 39 token rows, routing histograms, source/preparation contracts, environment fields and AUTO cache hashes verified.

## NVFP4 W4A4, no per-token scale

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 27.439 | 28.960 | 0.9475x | excluded |
| 2 | 37.184 | 39.376 | 0.9443x | excluded |
| 4 | 52.512 | 59.456 | 0.8832x | yes |
| 8 | 69.792 | 78.000 | 0.8948x | yes |
| 16 | 79.200 | 86.592 | 0.9146x | yes |
| 32 | 111.120 | 125.007 | 0.8889x | yes |
| 64 | 143.999 | 150.432 | 0.9572x | yes |
| 128 | 147.648 | 152.255 | 0.9697x | yes |
| 256 | 154.928 | 159.311 | 0.9725x | yes |
| 512 | 157.408 | 161.919 | 0.9721x | yes |
| 4096 | 208.463 | 221.823 | 0.9398x | yes |
| 8192 | 297.456 | 369.247 | 0.8056x | yes |
| 16384 | 472.464 | 662.015 | 0.7137x | yes |

decode **0.930884x**, prefill **0.814472x**, overall **0.897578x**.

## MXFP8 E4M3 × MXFP8 E4M3

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 43.520 | 41.184 | 1.0567x | excluded |
| 2 | 55.520 | 56.800 | 0.9775x | excluded |
| 4 | 81.584 | 86.865 | 0.9392x | yes |
| 8 | 110.209 | 115.329 | 0.9556x | yes |
| 16 | 126.048 | 130.496 | 0.9659x | yes |
| 32 | 182.945 | 188.481 | 0.9706x | yes |
| 64 | 241.760 | 251.152 | 0.9626x | yes |
| 128 | 250.289 | 258.145 | 0.9696x | yes |
| 256 | 266.881 | 271.088 | 0.9845x | yes |
| 512 | 268.400 | 274.433 | 0.9780x | yes |
| 4096 | 359.617 | 335.120 | 1.0731x | yes |
| 8192 | 536.593 | 528.177 | 1.0159x | yes |
| 16384 | 857.874 | 953.394 | 0.8998x | yes |

decode **0.965664x**, prefill **0.993616x**, overall **0.973208x**.

## MXFP4 weights × MXFP8 E4M3 activations

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 40.896 | 33.664 | 1.2148x | excluded |
| 2 | 51.200 | 45.344 | 1.1291x | excluded |
| 4 | 65.440 | 69.888 | 0.9364x | yes |
| 8 | 85.728 | 88.769 | 0.9657x | yes |
| 16 | 90.641 | 98.816 | 0.9173x | yes |
| 32 | 133.873 | 142.032 | 0.9425x | yes |
| 64 | 169.473 | 186.080 | 0.9107x | yes |
| 128 | 177.825 | 191.569 | 0.9283x | yes |
| 256 | 185.649 | 201.233 | 0.9226x | yes |
| 512 | 188.369 | 204.496 | 0.9211x | yes |
| 4096 | 303.281 | 286.544 | 1.0584x | yes |
| 8192 | 461.121 | 468.977 | 0.9832x | yes |
| 16384 | 776.002 | 874.658 | 0.8872x | yes |

decode **0.930436x**, prefill **0.973750x**, overall **0.942054x**.
