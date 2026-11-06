# Alpha versus retained complete AUTO100 screen

Complete AUTO100 comparison on hu-pdx-115: alpha487b versus retained38870 AUTO only. Both AUTO arms are complete. One Mega epilogue alpha-load assignment moves; shared split kernel/decoder, Mega kernel, graph scorer, logger and primary timing remain identical to retained. Preserve all thirteen unbracketed AUTO rows and observed split movement without row minima or drift adjustment. CONTROL is a separate completed phase, not a substitute for the previous AUTO baseline.

| Tokens | Previous Mega ms | Alpha Mega ms | Mega change | Previous/alpha Mega | Previous split ms | Alpha split ms | Previous split/Mega | Alpha split/Mega |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.090274 | 0.092561 | +2.533% | 0.975292 | 0.079473 | 0.085185 | 0.880353 | 0.920312 |
| 2 | 0.104161 | 0.100545 | -3.472% | 1.035964 | 0.112546 | 0.119697 | 1.080500 | 1.190482 |
| 4 | 0.128353 | 0.126225 | -1.658% | 1.016859 | 0.155762 | 0.138625 | 1.213544 | 1.098237 |
| 8 | 0.154546 | 0.142002 | -8.117% | 1.088337 | 0.160402 | 0.173410 | 1.037892 | 1.221180 |
| 16 | 0.165234 | 0.167202 | +1.191% | 0.988230 | 0.189234 | 0.192370 | 1.145249 | 1.150525 |
| 32 | 0.200450 | 0.202274 | +0.910% | 0.990983 | 0.212481 | 0.197842 | 1.060020 | 0.978089 |
| 64 | 0.226434 | 0.219201 | -3.194% | 1.032997 | 0.233811 | 0.237587 | 1.032579 | 1.083877 |
| 128 | 0.231266 | 0.233203 | +0.838% | 0.991694 | 0.242899 | 0.232243 | 1.050301 | 0.995883 |
| 256 | 0.236579 | 0.235426 | -0.487% | 1.004898 | 0.255139 | 0.254082 | 1.078452 | 1.079244 |
| 512 | 0.243122 | 0.242515 | -0.250% | 1.002503 | 0.244706 | 0.252947 | 1.006515 | 1.043016 |
| 1024 | 0.260115 | 0.251987 | -3.125% | 1.032256 | 0.271139 | 0.277955 | 1.042381 | 1.103053 |
| 2048 | 0.345348 | 0.344467 | -0.255% | 1.002558 | 0.363364 | 0.365268 | 1.052168 | 1.060386 |
| 4096 | 0.507012 | 0.499749 | -1.433% | 1.014533 | 0.573590 | 0.601622 | 1.131314 | 1.203848 |

Versus retained: Mega candidate/baseline GM 0.986931; 9/13 lower. Actual configs match at 40/104 rank/shape pairs; 49/104 split selections change.

Local bytes: {'retained': [0], 'candidate': [0]}. Phase wall: {'retained': 932.1187533939992, 'candidate': 937.0477623010011}. Phase wall includes tuning, setup and measurement; it is not a kernel speedup.


Actual rank-consensus AUTO tactics (M/N, physical cluster, flag batch, return mode):

| Tokens | Previous tactic | Alpha tactic |
| --- | --- | --- |
| 1 | M256/N64, C2, F8, epi_warps | M128/N64, C2, F8, epi_warps |
| 2 | M128/N64, C1, F4, epi_warps | M128/N64, C1, F4, epi_warps |
| 4 | M128/N64, C1, F8, epi_warps | M128/N64, C1, F4, epi_warps |
| 8 | M256/N64, C2, F4, epi_warps | M256/N64, C2, F4, epi_warps |
| 16 | M256/N64, C2, F8, epi_warps | M256/N64, C2, F4, epi_warps |
| 32 | M256/N64, C2, F8, epi_warps | M256/N64, C2, F8, epi_warps |
| 64 | M256/N64, C2, F8, epi_warps | M256/N64, C2, F4, epi_warps |
| 128 | M256/N64, C2, F8, epi_warps | M256/N64, C2, F4, epi_warps |
| 256 | M256/N64, C2, F4, epi_warps | M256/N64, C2, F8, epi_warps |
| 512 | M256/N64, C2, F4, epi_warps | M256/N64, C2, F8, epi_warps |
| 1024 | M256/N64, C2, F4, epi_warps | M256/N64, C2, F4, epi_warps |
| 2048 | M256/N128, C2, F4, reuse_dispatch_warps | M256/N128, C2, F8, reuse_dispatch_warps |
| 4096 | M256/N128, C2, F4, reuse_dispatch_warps | M256/N128, C2, F4, reuse_dispatch_warps |

All tactics retain K256, group_hint512, epi_flag_batch[2,4], atomic_counter, two decode groups and no in-kernel FC2 reduction. Hot selection scores time the prestaged W4A16 Mega wrapper plus reducer, excluding public routing/staging preparation; the primary values above use the unchanged cold-L2 CUPTI full-forward metric.
