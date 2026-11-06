# Candidate 442d2aa53f68b4640c3ab5118a76f1599ff60d34 primary screen

Baseline: `a65d5b09e7e4c4c5c160b0161c48becd100b3970`. One complete candidate sweep versus retained B1; these are screening ratios, not completed ABBA retention results. Tokens 1 and 2 are reported but excluded from all aggregate ratios.

Image `nvcr.io/nvidia/pytorch:26.05-py3`; B200, GPU0 for NVFP4 and GPU1 for the other two modes. Native AUTO, unfused deterministic finalize, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. All 39 token rows, routing histograms, source/preparation contracts, environment fields and AUTO cache hashes verified.

## NVFP4 W4A4, no per-token scale

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 27.439 | 25.152 | 1.0909x | excluded |
| 2 | 37.184 | 33.088 | 1.1238x | excluded |
| 4 | 52.512 | 47.408 | 1.1077x | yes |
| 8 | 69.792 | 63.296 | 1.1026x | yes |
| 16 | 79.200 | 73.696 | 1.0747x | yes |
| 32 | 111.120 | 110.815 | 1.0028x | yes |
| 64 | 143.999 | 139.440 | 1.0327x | yes |
| 128 | 147.648 | 139.599 | 1.0577x | yes |
| 256 | 154.928 | 148.720 | 1.0417x | yes |
| 512 | 157.408 | 150.528 | 1.0457x | yes |
| 4096 | 208.463 | 206.272 | 1.0106x | yes |
| 8192 | 297.456 | 305.312 | 0.9743x | yes |
| 16384 | 472.464 | 532.351 | 0.8875x | yes |

decode **1.057669x**, prefill **0.956047x**, overall **1.028928x**.

## MXFP8 E4M3 × MXFP8 E4M3

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 43.520 | 31.744 | 1.3710x | excluded |
| 2 | 55.520 | 47.168 | 1.1771x | excluded |
| 4 | 81.584 | 70.880 | 1.1510x | yes |
| 8 | 110.209 | 97.601 | 1.1292x | yes |
| 16 | 126.048 | 117.952 | 1.0686x | yes |
| 32 | 182.945 | 167.424 | 1.0927x | yes |
| 64 | 241.760 | 225.456 | 1.0723x | yes |
| 128 | 250.289 | 231.761 | 1.0799x | yes |
| 256 | 266.881 | 245.936 | 1.0852x | yes |
| 512 | 268.400 | 248.864 | 1.0785x | yes |
| 4096 | 359.617 | 320.832 | 1.1209x | yes |
| 8192 | 536.593 | 478.288 | 1.1219x | yes |
| 16384 | 857.874 | 827.473 | 1.0367x | yes |

decode **1.094339x**, prefill **1.092435x**, overall **1.093820x**.

## MXFP4 weights × MXFP8 E4M3 activations

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 40.896 | 28.096 | 1.4556x | excluded |
| 2 | 51.200 | 37.152 | 1.3781x | excluded |
| 4 | 65.440 | 56.032 | 1.1679x | yes |
| 8 | 85.728 | 74.656 | 1.1483x | yes |
| 16 | 90.641 | 84.641 | 1.0709x | yes |
| 32 | 133.873 | 112.064 | 1.1946x | yes |
| 64 | 169.473 | 149.169 | 1.1361x | yes |
| 128 | 177.825 | 153.008 | 1.1622x | yes |
| 256 | 185.649 | 159.888 | 1.1611x | yes |
| 512 | 188.369 | 162.769 | 1.1573x | yes |
| 4096 | 303.281 | 270.497 | 1.1212x | yes |
| 8192 | 461.121 | 437.777 | 1.0533x | yes |
| 16384 | 776.002 | 816.481 | 0.9504x | yes |

decode **1.149295x**, prefill **1.039251x**, overall **1.118177x**.
