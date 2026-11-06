# Linear-address D2 retention

Do not promote `3b42f0d1f3d0682cef1bca2ae51c2883259f11b7`. Decode geometric speedup is **1.005822×** (6/8 wins, T4–512), with sizeable mixed row changes. Prefill ratios are **1.008967× / 0.962814× / 0.971607×** at 4K / 8K / 16K. The limited 4K improvement does not compensate for the larger prefill regressions. All 13 selected tactics match on all 8 ranks.

This candidate changes address formation for every reducer worker, including the first worker. Its decode path is active, unlike the separately measured continuation-only R1. Therefore inactive continuation does not explain away D2's decode results; no selected-tactic switch explains them either. T4 and T256 have separated favorable quarter ranges, while T8 and T64 have separated unfavorable ranges. Without generated-code or repeat evidence, the serial run does not establish which allocation/address-lowering changes caused those differences or that the small aggregate gain is repeatable.

Fresh same-boot hu115 d01/A1 from the startup three-arm run is the direct control. There are no cross-host ratios or chained comparison estimates. D1/ce0 failed its first compilation before any measured row; its unchanged source, exception records and closed process groups remain separately preserved and are not a timing control. D2 restores the original stride-derived divisibility proof with `cute.assume`, without adding a caller alignment requirement.

EP8/H7168/I2048/E256/K8, AUTO4/O3, 3 warmups and 100 cold-L2 CUDA-graph CUPTI rank-MAX samples per row. Speedup is A1/D2. All times and MAD values below are µs. MAD and quarters are descriptive; serial arms do not cancel drift.

|T|A1 median|D2 median|Speedup|A1 MAD|D2 MAD|Matching tactic|
|---:|---:|---:|---:|---:|---:|---|
|1|68.3210|71.6325|0.953771|1.1030|1.1520|N64 / epi_warps|
|2|91.5530|79.1205|1.157134|1.4240|0.7355|N64 / epi_warps|
|4|101.5690|96.0010|1.057999|1.0085|1.1840|N64 / epi_warps|
|8|125.1205|132.8330|0.941938|1.6800|1.4240|N64 / epi_warps|
|16|135.1695|133.6015|1.011736|1.2635|0.7845|N64 / epi_warps|
|32|164.9775|164.6100|1.002233|1.8405|1.5830|N64 / epi_warps|
|64|180.1455|186.1770|0.967603|1.1045|1.3920|N64 / epi_warps|
|128|193.4420|189.0890|1.023021|2.9755|1.6795|N64 / epi_warps|
|256|198.0660|190.4660|1.039902|1.2000|1.4720|N64 / epi_warps|
|512|198.9295|197.5375|1.007047|1.8725|1.3925|N64 / epi_warps|
|4096|478.9330|474.6765|1.008967|3.0720|3.3290|N128 / reuse_dispatch_warps|
|8192|786.6795|817.0630|0.962814|14.6875|19.5195|N128 / reuse_dispatch_warps|
|16384|1520.8965|1565.3405|0.971607|50.2565|44.1920|N128 / reuse_dispatch_warps|

At 4K every D2 quarter (473.253–475.715µs) is below every A1 quarter (476.709–479.781µs), a modest favorable observation. At 8K both arms drift upward strongly; D2 is slower in the first three corresponding quarters and nearly equal in the last. At 16K D2 is faster in the first quarter and slower in the remaining three. The latter two prefill rows provide no robust gain despite the favorable 4K result.

|T|A1 successive 25-sample quarters (µs)|D2 quarters (µs)|
|---:|---|---|
|1|68.449, 67.905, 68.353, 68.672|71.809, 71.937, 71.105, 71.777|
|2|88.450, 90.177, 92.448, 92.513|78.560, 78.945, 79.105, 79.648|
|4|101.761, 101.089, 101.633, 101.824|94.496, 95.904, 96.961, 96.448|
|8|122.946, 125.857, 126.304, 124.641|132.417, 132.161, 133.089, 132.513|
|16|135.713, 135.170, 135.265, 135.010|131.777, 134.017, 133.761, 133.729|
|32|161.889, 163.266, 166.465, 165.762|162.338, 164.481, 165.762, 165.377|
|64|178.817, 180.258, 180.483, 180.673|183.105, 186.721, 186.498, 187.009|
|128|189.921, 193.185, 195.137, 194.530|186.754, 188.834, 189.633, 190.306|
|256|197.377, 197.794, 198.146, 198.306|188.130, 189.730, 191.682, 190.690|
|512|198.626, 199.362, 200.802, 198.370|195.426, 198.338, 197.761, 197.825|
|4096|476.709, 479.046, 479.525, 479.781|475.715, 473.253, 473.764, 474.885|
|8192|779.849, 778.278, 817.639, 831.049|785.319, 780.870, 828.328, 830.822|
|16384|1396.590, 1510.448, 1568.529, 1569.073|1389.483, 1534.733, 1606.764, 1586.893|

Independent terminal audit passed once: 104 finite/repeat-exact cross-arm outputs, all 166 original sealed member files (158 new plus 8 exact cached files), source 104, runtime, direct A1 control, failed-D1 predecessor and final closure. Original gzip bytes were not locally verified; complete member verification is a distinct boundary.

- Audit SHA256: `1b64cd87918f3770669c634bdb317ede79c5f207c516ba40e473738eae3bb706`.
- Original remote archive SHA256: `d6d61e46e1b5528326ef69a4c057b41fa75dd3a43f9da4aa301ed4bf1c54919f`.
- Compact bundle SHA256: `736e4d6a8896a892e306433bdc25b10a782f6665f1c401e33cee309735f4247a`.
- Final closure epoch 1789833630.7928925: all recorded owned process groups absent and GPUs idle.

Preserve both the failed D1 and measured D2 artifacts. No further qualification, generated capture, repeat or sanitizer is requested for this unpromoted candidate.
