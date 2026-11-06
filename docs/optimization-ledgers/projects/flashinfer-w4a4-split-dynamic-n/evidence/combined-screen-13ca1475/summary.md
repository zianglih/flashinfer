# Candidate 13ca1475d96839f3bf3c46699cc63204b4d3b409 primary screen

Baseline: `a65d5b09e7e4c4c5c160b0161c48becd100b3970`. One complete candidate sweep versus retained B1; these are screening ratios, not completed ABBA retention results. Tokens 1 and 2 are reported but excluded from all aggregate ratios.

Image `nvcr.io/nvidia/pytorch:26.05-py3`; B200, GPU0 for NVFP4 and GPU1 for the other two modes. Native AUTO, unfused deterministic finalize, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. All 39 token rows, routing histograms, source/preparation contracts, environment fields and AUTO cache hashes verified.

## NVFP4 W4A4, no per-token scale

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 27.439 | 26.912 | 1.0196x | excluded |
| 2 | 37.184 | 37.184 | 1.0000x | excluded |
| 4 | 52.512 | 54.464 | 0.9642x | yes |
| 8 | 69.792 | 72.224 | 0.9663x | yes |
| 16 | 79.200 | 82.368 | 0.9615x | yes |
| 32 | 111.120 | 112.096 | 0.9913x | yes |
| 64 | 143.999 | 144.623 | 0.9957x | yes |
| 128 | 147.648 | 143.263 | 1.0306x | yes |
| 256 | 154.928 | 151.087 | 1.0254x | yes |
| 512 | 157.408 | 153.663 | 1.0244x | yes |
| 4096 | 208.463 | 208.383 | 1.0004x | yes |
| 8192 | 297.456 | 322.304 | 0.9229x | yes |
| 16384 | 472.464 | 562.911 | 0.8393x | yes |

decode **0.994551x**, prefill **0.918510x**, overall **0.973209x**.

## MXFP8 E4M3 × MXFP8 E4M3

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 43.520 | 36.608 | 1.1888x | excluded |
| 2 | 55.520 | 53.904 | 1.0300x | excluded |
| 4 | 81.584 | 80.768 | 1.0101x | yes |
| 8 | 110.209 | 103.968 | 1.0600x | yes |
| 16 | 126.048 | 121.231 | 1.0397x | yes |
| 32 | 182.945 | 169.792 | 1.0775x | yes |
| 64 | 241.760 | 224.896 | 1.0750x | yes |
| 128 | 250.289 | 231.056 | 1.0832x | yes |
| 256 | 266.881 | 245.729 | 1.0861x | yes |
| 512 | 268.400 | 249.841 | 1.0743x | yes |
| 4096 | 359.617 | 333.376 | 1.0787x | yes |
| 8192 | 536.593 | 503.200 | 1.0664x | yes |
| 16384 | 857.874 | 889.105 | 0.9649x | yes |

decode **1.062953x**, prefill **1.035364x**, overall **1.055357x**.

## MXFP4 weights × MXFP8 E4M3 activations

| Tokens | B1 (us) | Candidate (us) | B1/candidate | Retention |
| ---: | ---: | ---: | ---: | :--- |
| 1 | 40.896 | 38.112 | 1.0730x | excluded |
| 2 | 51.200 | 43.377 | 1.1804x | excluded |
| 4 | 65.440 | 63.936 | 1.0235x | yes |
| 8 | 85.728 | 83.329 | 1.0288x | yes |
| 16 | 90.641 | 91.872 | 0.9866x | yes |
| 32 | 133.873 | 119.808 | 1.1174x | yes |
| 64 | 169.473 | 155.264 | 1.0915x | yes |
| 128 | 177.825 | 158.993 | 1.1184x | yes |
| 256 | 185.649 | 165.792 | 1.1198x | yes |
| 512 | 188.369 | 167.824 | 1.1224x | yes |
| 4096 | 303.281 | 277.777 | 1.0918x | yes |
| 8192 | 461.121 | 465.104 | 0.9914x | yes |
| 16384 | 776.002 | 833.986 | 0.9305x | yes |

decode **1.074825x**, prefill **1.002396x**, overall **1.054568x**.
