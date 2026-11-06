# Negative-cell phase and clock trajectories

Raw evidence is unchanged. Component entries are per-phase medians; quartet clock sequences are Q1→Q4. Reason codes are the observed NVML bitmasks. No rows or clock windows are filtered.

## K3 EP8 / 4096

Both FCs move slower; 5.08/4.06% repeat spreads overlap. Clocks remain 2032/reason0, so clock telemetry alone does not explain the variation. Not a stable FC1-only loss.

| Phase | E2E µs | FC1 µs | FC2 µs | Combine µs | FC1 extension µs | FC2 extension µs | Combine extension µs | Quartile SM medians MHz | Quartile reason sets |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 0-control | 576.804 | 365.171 | 175.778 | 38.433 | 364.899 | 174.913 | 19.456 | 2032/2032/2032/2032 | 0/0/0/0 |
| 1-candidate | 559.701 | 355.075 | 168.418 | 39.377 | 354.803 | 167.714 | 19.392 | 2032/2032/2032/2032 | 0/0/0/0 |
| 2-candidate | 582.404 | 367.266 | 178.721 | 39.056 | 366.962 | 177.841 | 19.744 | 2032/2032/2032/2032 | 0/0/0/0 |
| 3-control | 548.916 | 351.315 | 163.697 | 38.688 | 351.059 | 162.930 | 19.312 | 2032/2032/2032/2032 | 0/0/0/0 |

Δ critical extensions FC1 / FC2 / combine: +2.9035 / +3.8558 / +0.1840 µs.

## K3 EP8 / 16384

Both candidate E2E phases are slower than both controls. FC1 and FC2 contribute similarly; 11 clock-exception quartiles and different throttling trajectories prevent clean instruction-local attribution. Preserve as an unresolved adverse observation.

| Phase | E2E µs | FC1 µs | FC2 µs | Combine µs | FC1 extension µs | FC2 extension µs | Combine extension µs | Quartile SM medians MHz | Quartile reason sets |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 0-control | 1987.040 | 1331.978 | 567.236 | 118.209 | 1331.642 | 565.972 | 79.009 | 2032/1762/1762/1290 | 0/0/0,4/4 |
| 1-candidate | 2021.729 | 1349.851 | 580.309 | 120.689 | 1349.499 | 579.077 | 79.505 | 2032/2032/1282/1282 | 4/4/4/4 |
| 2-candidate | 2040.240 | 1362.330 | 587.925 | 126.881 | 1361.963 | 586.629 | 79.712 | 2032/1815/1815/1275 | 0/0,4/4/4 |
| 3-control | 2015.520 | 1352.155 | 573.493 | 118.945 | 1351.724 | 572.197 | 79.328 | 2032/2032/2032/1305 | 0/0/0/4 |

Δ critical extensions FC1 / FC2 / combine: +14.0478 / +13.7680 / +0.4398 µs.

## N3U EP8 / 4096

Near-neutral loss; FC1 is slightly faster and FC2 slightly slower. Not an FC1 regression signal.

| Phase | E2E µs | FC1 µs | FC2 µs | Combine µs | FC1 extension µs | FC2 extension µs | Combine extension µs | Quartile SM medians MHz | Quartile reason sets |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 0-control | 397.042 | 193.680 | 171.665 | 72.160 | 193.409 | 170.785 | 14.336 | 2032/2032/2032/2032 | 0/0/0/0 |
| 1-candidate | 397.010 | 193.729 | 171.873 | 72.225 | 193.473 | 170.961 | 14.336 | 2032/2032/2032/2032 | 0/0/0/0 |
| 2-candidate | 399.378 | 194.401 | 173.409 | 73.489 | 194.145 | 172.577 | 14.528 | 2032/2032/2032/2032 | 0/0/0/0 |
| 3-control | 398.881 | 194.481 | 173.041 | 73.201 | 194.226 | 172.177 | 14.480 | 2032/2032/2032/2032 | 0/0/0/0 |

Δ critical extensions FC1 / FC2 / combine: -0.0082 / +0.2883 / +0.0240 µs.

## N3U EP8 / 16384

Large 8.08/5.49% phase spreads, mixed clocks, and phase-overlapping medians. No stable source-local regression established.

| Phase | E2E µs | FC1 µs | FC2 µs | Combine µs | FC1 extension µs | FC2 extension µs | Combine extension µs | Quartile SM medians MHz | Quartile reason sets |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 0-control | 1457.190 | 780.323 | 605.619 | 112.945 | 779.939 | 604.771 | 58.432 | 2032/2032/2032/1552 | 0/0/0/0,4 |
| 1-candidate | 1477.207 | 795.172 | 612.643 | 110.688 | 794.772 | 611.859 | 59.216 | 2032/2032/2032/1395 | 0/0/0,4/4 |
| 2-candidate | 1558.311 | 842.724 | 640.035 | 112.640 | 842.323 | 639.219 | 60.496 | 2032/2032/1522/1522 | 0/0/0,4/4 |
| 3-control | 1574.999 | 834.244 | 642.275 | 113.520 | 833.860 | 641.411 | 60.208 | 2032/2032/1237/1237 | 0/0/0,4/4 |

Δ critical extensions FC1 / FC2 / combine: +11.6480 / +2.4482 / +0.5360 µs.

## V3 EP8 / 4096

Near-zero E2E change; faster FC1 offsets slower FC2. Not an FC1 regression signal.

| Phase | E2E µs | FC1 µs | FC2 µs | Combine µs | FC1 extension µs | FC2 extension µs | Combine extension µs | Quartile SM medians MHz | Quartile reason sets |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 0-control | 289.026 | 163.761 | 109.297 | 33.873 | 163.393 | 87.537 | 20.416 | 2032/2032/2032/2032 | 0/0/0/0 |
| 1-candidate | 288.146 | 162.721 | 109.217 | 33.776 | 162.353 | 87.441 | 20.384 | 2032/2032/2032/2032 | 0/0/0/0 |
| 2-candidate | 287.969 | 162.785 | 109.265 | 32.576 | 162.433 | 87.120 | 20.497 | 2032/2032/2032/2032 | 0/0/0/0 |
| 3-control | 287.074 | 162.705 | 108.273 | 32.272 | 162.338 | 86.497 | 20.480 | 2032/2032/2032/2032 | 0/0/0/0 |

Δ critical extensions FC1 / FC2 / combine: -0.4723 / +0.2637 / -0.0078 µs.

## V41F EP4 / 8192

FC1 is slower, but 6.07/4.34% phase spreads exceed the 0.64% point estimate. Both candidate phases lie within the two control E2E medians; normal clocks do not remove this repeat variation.

| Phase | E2E µs | FC1 µs | FC2 µs | Combine µs | FC1 extension µs | FC2 extension µs | Combine extension µs | Quartile SM medians MHz | Quartile reason sets |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 0-control | 686.661 | 412.836 | 237.810 | 64.433 | 412.548 | 221.266 | 43.041 | 2032/2032/2032/2032 | 0/0/0/0 |
| 1-candidate | 696.773 | 419.540 | 238.482 | 64.416 | 419.267 | 222.433 | 43.200 | 2032/2032/2032/2032 | 0/0/0/0 |
| 2-candidate | 727.045 | 435.347 | 250.434 | 64.353 | 435.028 | 233.841 | 44.993 | 2032/2032/2032/2032 | 0/0/0/0 |
| 3-control | 728.310 | 435.283 | 252.290 | 66.273 | 434.996 | 235.074 | 44.928 | 2032/2032/2032/2032 | 0/0/0/0 |

Δ critical extensions FC1 / FC2 / combine: +3.3755 / -0.0328 / +0.1118 µs.

## K3 TP8 / 4096

FC1 is slightly faster; most measured critical-extension growth is in FC2. Candidate spread is 5.02% and four clock-exception quartiles retain reason4 despite median2032MHz. Not an isolated FC1 selector loss.

| Phase | E2E µs | FC1 µs | FC2 µs | Combine µs | FC1 extension µs | FC2 extension µs | Combine extension µs | Quartile SM medians MHz | Quartile reason sets |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 0-control | 695.366 | 328.722 | 265.170 | 116.001 | 327.411 | 252.418 | 98.993 | 2032/2032/2032/2032 | 0/0/0/4 |
| 1-candidate | 692.790 | 326.051 | 264.818 | 114.401 | 324.963 | 251.587 | 98.929 | 2032/2032/2032/2032 | 0/0/0,4/4 |
| 2-candidate | 727.542 | 338.659 | 279.283 | 116.321 | 337.315 | 266.995 | 100.912 | 2032/2032/2032/2032 | 0/0/0/0,4 |
| 3-control | 706.870 | 337.043 | 265.459 | 115.392 | 335.650 | 253.282 | 99.488 | 2032/2032/2032/2032 | 0/0/0/0 |

Δ critical extensions FC1 / FC2 / combine: -0.3915 / +6.4405 / +0.6800 µs.
