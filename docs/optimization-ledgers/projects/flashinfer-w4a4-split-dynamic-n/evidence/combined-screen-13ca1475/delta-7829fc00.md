# 13ca1475 versus previous 7829fc00 screen

Same B1, frozen measurement helpers, GPU allocation, workload, and timing. Checkpoint ratios are diagnostic comparisons of one screen each.

| Mode | Tokens | 7829fc00 us | 13ca1475 us | Previous/current |
| :--- | ---: | ---: | ---: | ---: |
| nvfp4 | 1 | 28.672 | 26.912 | 1.065398x |
| nvfp4 | 2 | 37.824 | 37.184 | 1.017212x |
| nvfp4 | 4 | 56.367 | 54.464 | 1.034950x |
| nvfp4 | 8 | 74.720 | 72.224 | 1.034566x |
| nvfp4 | 16 | 83.504 | 82.368 | 1.013792x |
| nvfp4 | 32 | 115.391 | 112.096 | 1.029399x |
| nvfp4 | 64 | 145.088 | 144.623 | 1.003212x |
| nvfp4 | 128 | 148.608 | 143.263 | 1.037305x |
| nvfp4 | 256 | 156.191 | 151.087 | 1.033778x |
| nvfp4 | 512 | 158.272 | 153.663 | 1.029991x |
| nvfp4 | 4096 | 221.919 | 208.383 | 1.064957x |
| nvfp4 | 8192 | 351.200 | 322.304 | 1.089653x |
| nvfp4 | 16384 | 621.646 | 562.911 | 1.104342x |

nvfp4 decode previous/current geometric mean: **1.027061x**.

nvfp4 prefill previous/current geometric mean: **1.086196x**.

nvfp4 overall previous/current geometric mean: **1.042862x**.
| mxfp8 | 1 | 41.648 | 36.608 | 1.137675x |
| mxfp8 | 2 | 55.888 | 53.904 | 1.036787x |
| mxfp8 | 4 | 84.992 | 80.768 | 1.052298x |
| mxfp8 | 8 | 111.648 | 103.968 | 1.073869x |
| mxfp8 | 16 | 124.433 | 121.231 | 1.026404x |
| mxfp8 | 32 | 183.248 | 169.792 | 1.079250x |
| mxfp8 | 64 | 242.960 | 224.896 | 1.080322x |
| mxfp8 | 128 | 250.528 | 231.056 | 1.084272x |
| mxfp8 | 256 | 263.840 | 245.729 | 1.073705x |
| mxfp8 | 512 | 266.753 | 249.841 | 1.067691x |
| mxfp8 | 4096 | 337.585 | 333.376 | 1.012624x |
| mxfp8 | 8192 | 510.529 | 503.200 | 1.014564x |
| mxfp8 | 16384 | 909.169 | 889.105 | 1.022567x |

mxfp8 decode previous/current geometric mean: **1.067073x**.

mxfp8 prefill previous/current geometric mean: **1.016576x**.

mxfp8 overall previous/current geometric mean: **1.053057x**.
| mxfp4 | 1 | 33.696 | 38.112 | 0.884131x |
| mxfp4 | 2 | 44.032 | 43.377 | 1.015112x |
| mxfp4 | 4 | 67.952 | 63.936 | 1.062813x |
| mxfp4 | 8 | 86.304 | 83.329 | 1.035708x |
| mxfp4 | 16 | 95.072 | 91.872 | 1.034831x |
| mxfp4 | 32 | 134.784 | 119.808 | 1.125000x |
| mxfp4 | 64 | 177.264 | 155.264 | 1.141697x |
| mxfp4 | 128 | 182.176 | 158.993 | 1.145815x |
| mxfp4 | 256 | 191.104 | 165.792 | 1.152673x |
| mxfp4 | 512 | 193.904 | 167.824 | 1.155401x |
| mxfp4 | 4096 | 292.529 | 277.777 | 1.053107x |
| mxfp4 | 8192 | 473.473 | 465.104 | 1.017994x |
| mxfp4 | 16384 | 824.929 | 833.986 | 0.989140x |

mxfp4 decode previous/current geometric mean: **1.105612x**.

mxfp4 prefill previous/current geometric mean: **1.019746x**.

mxfp4 overall previous/current geometric mean: **1.081501x**.
