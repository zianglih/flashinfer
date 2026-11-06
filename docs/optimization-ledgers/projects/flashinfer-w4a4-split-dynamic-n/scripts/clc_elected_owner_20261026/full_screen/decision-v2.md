# V2 fixed-lane ownership: reject

The 48-point fresh CAAC screen passed all source, cache, six-field True/True tactic, routing, PDL, label, and raw-100-sample checks. No W4A16/TRTLLM timing was performed. Complete raw records and validated summary are in `results-v2/`.

Control/candidate geomean: **0.97673x overall, 0.99210x decode, 0.96160x prefill**. Per-model: V3 0.98202x, V4.1-Flash 0.98307x, K3 0.96521x. All twelve model/backend aggregates are slower; 44/48 points are slower by paired median and 40/48 are slower in both forward and reverse comparisons.

Control-return drift reaches 5.16% in one point, so tiny individual differences are not decisive. The largest losses are stable in both orders with small control drift: K3 per-token 16384 is 0.91889x (+109.24 us, -0.22% control drift), K3 W4A4 16384 is 0.92421x (+73.62 us, -0.04% drift), K3 MXFP4x8 4096 is 0.93066x (+32.49 us, -0.08% drift). The broad regression and additional static control-flow instructions do not support retaining V2.

V3 helper-isolated election is a separate candidate. These rows must never be presented as V3 measurements. No production commit or PR benchmark update is warranted for this rejected version.

The successor V3 also regressed and is rejected. The local owner review clone was removed after verifying its exact final source; all useful helpers, frozen patches, source receipts and raw evidence remain. No remote compilation caches were removed.
