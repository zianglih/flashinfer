# N3U MXFP4x8, four-token causal check

Eight mirrored passes,100 cold-L2 CUDA-graph CUPTI samples each. Both sources use unfused finalize, the same routing and saved native tactics; no AUTO or new tactic was used.

| Source | K steps8/8 | K steps4/4 |
|---|---:|---:|
| e2728 |37.10425 us|38.96017 us|
| Combined |37.30423 us|39.18450 us|

At fixed tactics, the source effect is -0.536% atK8 and -0.573% atK4. On the combined source, changing the AUTO winner toK4 costs -4.799%; the native-winner total is -5.309%.

Both tactics keep routeN16, FC1/FC2 M128N16, one CTA and shared CLC enabled. Most of the slowdown is winner selection; fixed-tactic source overhead is about0.2 us. These are targeted diagnostic timings, not replacements for the full-campaign tables.

| Pass | Source | Winner | Median us |
|---|---|---|---:|
|c0-old|legacy|old|37.08850|
|a1-old|current|old|37.34400|
|a2-new|current|new|39.18450|
|c3-new|legacy|new|38.88000|
|c4-new|legacy|new|39.04050|
|a5-new|current|new|39.18450|
|a6-old|current|old|37.26450|
|c7-old|legacy|old|37.12000|
