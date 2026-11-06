# 442d2aa5 versus previous 13ca1475 screen

Same B1, frozen measurement helpers, GPU allocation, workload, and timing. Checkpoint ratios are diagnostic comparisons of one screen each.

| Mode | Tokens | 13ca1475 us | 442d2aa5 us | Previous/current |
| :--- | ---: | ---: | ---: | ---: |
| nvfp4 | 1 | 26.912 | 25.152 | 1.069975x |
| nvfp4 | 2 | 37.184 | 33.088 | 1.123791x |
| nvfp4 | 4 | 54.464 | 47.408 | 1.148836x |
| nvfp4 | 8 | 72.224 | 63.296 | 1.141044x |
| nvfp4 | 16 | 82.368 | 73.696 | 1.117673x |
| nvfp4 | 32 | 112.096 | 110.815 | 1.011555x |
| nvfp4 | 64 | 144.623 | 139.440 | 1.037174x |
| nvfp4 | 128 | 143.263 | 139.599 | 1.026247x |
| nvfp4 | 256 | 151.087 | 148.720 | 1.015923x |
| nvfp4 | 512 | 153.663 | 150.528 | 1.020830x |
| nvfp4 | 4096 | 208.383 | 206.272 | 1.010236x |
| nvfp4 | 8192 | 322.304 | 305.312 | 1.055655x |
| nvfp4 | 16384 | 562.911 | 532.351 | 1.057406x |

nvfp4 decode previous/current geometric mean: **1.063464x**.

nvfp4 prefill previous/current geometric mean: **1.040868x**.

nvfp4 overall previous/current geometric mean: **1.057253x**.
| mxfp8 | 1 | 36.608 | 31.744 | 1.153226x |
| mxfp8 | 2 | 53.904 | 47.168 | 1.142819x |
| mxfp8 | 4 | 80.768 | 70.880 | 1.139503x |
| mxfp8 | 8 | 103.968 | 97.601 | 1.065240x |
| mxfp8 | 16 | 121.231 | 117.952 | 1.027804x |
| mxfp8 | 32 | 169.792 | 167.424 | 1.014141x |
| mxfp8 | 64 | 224.896 | 225.456 | 0.997516x |
| mxfp8 | 128 | 231.056 | 231.761 | 0.996962x |
| mxfp8 | 256 | 245.729 | 245.936 | 0.999154x |
| mxfp8 | 512 | 249.841 | 248.864 | 1.003924x |
| mxfp8 | 4096 | 333.376 | 320.832 | 1.039098x |
| mxfp8 | 8192 | 503.200 | 478.288 | 1.052086x |
| mxfp8 | 16384 | 889.105 | 827.473 | 1.074482x |

mxfp8 decode previous/current geometric mean: **1.029528x**.

mxfp8 prefill previous/current geometric mean: **1.055121x**.

mxfp8 overall previous/current geometric mean: **1.036445x**.
| mxfp4 | 1 | 38.112 | 28.096 | 1.356492x |
| mxfp4 | 2 | 43.377 | 37.152 | 1.167541x |
| mxfp4 | 4 | 63.936 | 56.032 | 1.141062x |
| mxfp4 | 8 | 83.329 | 74.656 | 1.116166x |
| mxfp4 | 16 | 91.872 | 84.641 | 1.085438x |
| mxfp4 | 32 | 119.808 | 112.064 | 1.069103x |
| mxfp4 | 64 | 155.264 | 149.169 | 1.040863x |
| mxfp4 | 128 | 158.993 | 153.008 | 1.039112x |
| mxfp4 | 256 | 165.792 | 159.888 | 1.036926x |
| mxfp4 | 512 | 167.824 | 162.769 | 1.031059x |
| mxfp4 | 4096 | 277.777 | 270.497 | 1.026913x |
| mxfp4 | 8192 | 465.104 | 437.777 | 1.062422x |
| mxfp4 | 16384 | 833.986 | 816.481 | 1.021439x |

mxfp4 decode previous/current geometric mean: **1.069286x**.

mxfp4 prefill previous/current geometric mean: **1.036767x**.

mxfp4 overall previous/current geometric mean: **1.060317x**.
