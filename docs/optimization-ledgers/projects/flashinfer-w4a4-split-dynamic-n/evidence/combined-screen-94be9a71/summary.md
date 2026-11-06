# Candidate 94be9a712a46ab34b902605c4a34d26a4c570692 primary screen

Baseline: `a65d5b09e7e4c4c5c160b0161c48becd100b3970`. One complete candidate sweep versus retained B1; these are screening ratios, not completed ABBA retention results. Tokens 1 and 2 are reported but excluded from all aggregate ratios.

Image `nvcr.io/nvidia/pytorch:26.05-py3`; B200, GPU0 for NVFP4 and GPU1 for the other two modes. Native AUTO, unfused deterministic finalize, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. All 39 token rows, routing histograms, source/preparation contracts, environment fields and AUTO cache hashes verified.

## NVFP4 W4A4, no per-token scale

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 27.439 | 28.768 | 0.9538x | excluded |
| 2 | 37.184 | 37.760 | 0.9847x | excluded |
| 4 | 52.512 | 56.384 | 0.9313x | yes |
| 8 | 69.792 | 74.704 | 0.9342x | yes |
| 16 | 79.200 | 83.392 | 0.9497x | yes |
| 32 | 111.120 | 115.472 | 0.9623x | yes |
| 64 | 143.999 | 145.216 | 0.9916x | yes |
| 128 | 147.648 | 148.848 | 0.9919x | yes |
| 256 | 154.928 | 155.952 | 0.9934x | yes |
| 512 | 157.408 | 158.176 | 0.9951x | yes |
| 4096 | 208.463 | 222.143 | 0.9384x | yes |
| 8192 | 297.456 | 368.287 | 0.8077x | yes |
| 16384 | 472.464 | 654.399 | 0.7220x | yes |

decode **0.968371x**, prefill **0.817936x**, overall **0.924794x**.

## MXFP8 E4M3 × MXFP8 E4M3

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 43.520 | 41.664 | 1.0445x | excluded |
| 2 | 55.520 | 55.840 | 0.9943x | excluded |
| 4 | 81.584 | 85.760 | 0.9513x | yes |
| 8 | 110.209 | 111.536 | 0.9881x | yes |
| 16 | 126.048 | 124.400 | 1.0132x | yes |
| 32 | 182.945 | 183.040 | 0.9995x | yes |
| 64 | 241.760 | 243.472 | 0.9930x | yes |
| 128 | 250.289 | 250.336 | 0.9998x | yes |
| 256 | 266.881 | 263.776 | 1.0118x | yes |
| 512 | 268.400 | 266.609 | 1.0067x | yes |
| 4096 | 359.617 | 332.784 | 1.0806x | yes |
| 8192 | 536.593 | 530.337 | 1.0118x | yes |
| 16384 | 857.874 | 938.882 | 0.9137x | yes |

decode **0.995249x**, prefill **0.999680x**, overall **0.996456x**.

## MXFP4 weights × MXFP8 E4M3 activations

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 40.896 | 33.424 | 1.2236x | excluded |
| 2 | 51.200 | 44.000 | 1.1636x | excluded |
| 4 | 65.440 | 67.808 | 0.9651x | yes |
| 8 | 85.728 | 86.016 | 0.9967x | yes |
| 16 | 90.641 | 94.256 | 0.9616x | yes |
| 32 | 133.873 | 134.240 | 0.9973x | yes |
| 64 | 169.473 | 176.576 | 0.9598x | yes |
| 128 | 177.825 | 181.536 | 0.9796x | yes |
| 256 | 185.649 | 190.049 | 0.9768x | yes |
| 512 | 188.369 | 193.024 | 0.9759x | yes |
| 4096 | 303.281 | 287.601 | 1.0545x | yes |
| 8192 | 461.121 | 487.297 | 0.9463x | yes |
| 16384 | 776.002 | 864.994 | 0.8971x | yes |

decode **0.976493x**, prefill **0.963775x**, overall **0.973007x**.
