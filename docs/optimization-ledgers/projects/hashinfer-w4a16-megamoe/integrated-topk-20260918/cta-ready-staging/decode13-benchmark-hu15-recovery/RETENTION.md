# CTA-ready S2 recovery retention

Do not promote `ca05e1659a61c63a1d5fa21370fc1aae7cdd62cd`. The complete fresh same-boot hu15 comparison against d01/A1 gives **0.944670589×** decode geometric speedup (T4–512, 0/8 wins). T1 through T8192 are slower; T16384 has a small1.008488× median gain with large within-arm drift. All13 selected tactics match across all8 ranks. This is a measured whole-candidate regression, not a decomposition of bitmap polling, header handling, scheduling, or copy costs. The interrupted hu59 run contributes no timing rows or comparison.

EP8/H7168/I2048/E256/K8, AUTO4/O3;3 warmups and100 cold-L2 CUDA-graph CUPTI samples per row, rank-MAX aggregation. Speedup=A1/S2. Times and MAD below are microseconds; MAD describes within-arm dispersion, not a causal confidence interval. Sequential arms do not cancel temporal drift.

|T|A1 median|S2 median|Speedup|A1 MAD|S2 MAD|Matching tactic|
|---:|---:|---:|---:|---:|---:|---|
|1|65.6640|66.1130|0.993209|0.9605|0.7840|N64 / epi_warps|
|2|87.3285|92.9285|0.939739|0.7685|1.0720|N64 / epi_warps|
|4|96.5285|105.6000|0.914096|0.6395|1.4080|N64 / epi_warps|
|8|121.9200|127.7600|0.954289|0.8485|1.6315|N64 / epi_warps|
|16|132.0170|141.0720|0.935813|0.9120|0.8640|N64 / epi_warps|
|32|160.1920|168.5130|0.950621|0.8325|1.0395|N64 / epi_warps|
|64|183.0565|189.2340|0.967355|0.7680|0.9445|N64 / epi_warps|
|128|185.3935|196.1610|0.945109|0.9115|0.9275|N64 / epi_warps|
|256|190.2565|202.0485|0.941638|0.9280|1.0245|N64 / epi_warps|
|512|197.3120|207.8405|0.949343|1.6160|0.9285|N64 / epi_warps|
|4096|464.8015|479.1540|0.970046|3.1685|3.9195|N128 / reuse_dispatch_warps|
|8192|769.0255|781.4420|0.984111|5.9200|8.6235|N128 / reuse_dispatch_warps|
|16384|1496.6120|1484.0150|1.008488|49.4715|92.5600|N128 / reuse_dispatch_warps|

The successive25-sample quarter medians preserve the regression across every decode aggregate row: every S2 quarter median exceeds every A1 quarter median for T4–512. Thus the aggregate is not driven by one isolated quarter. T1 is a small, overlapping change and is outside the decode aggregate. At T16384 the A1 quarter medians rise from1356.739 to1540.388µs and S2 from1362.925 to1561.679µs; all four time-ordered S2 quarters exceed their corresponding A1 quarters despite the aggregate median gain. That1.008488× result does not establish a prefill improvement.

|T|A1 quarter medians (µs)|S2 quarter medians (µs)|
|---:|---|---|
|1|66.848, 65.632, 65.568, 65.440|66.400, 66.113, 66.113, 66.081|
|2|87.392, 87.585, 87.072, 87.360|93.664, 92.736, 92.736, 92.800|
|4|96.833, 96.224, 96.609, 96.257|106.016, 105.024, 105.313, 106.080|
|8|122.368, 122.016, 120.897, 121.984|128.191, 127.904, 127.392, 127.457|
|16|131.714, 131.937, 131.810, 132.193|141.312, 141.248, 141.249, 140.513|
|32|159.713, 159.361, 160.481, 160.832|168.353, 168.736, 168.417, 168.704|
|64|183.072, 183.585, 183.169, 182.785|189.473, 189.506, 189.250, 188.706|
|128|185.729, 185.633, 185.218, 185.057|197.184, 195.361, 196.225, 196.033|
|256|190.496, 190.433, 190.081, 190.048|201.888, 201.472, 202.176, 203.808|
|512|197.313, 198.881, 196.641, 196.192|208.417, 207.968, 207.681, 207.648|
|4096|462.529, 464.225, 464.833, 465.793|479.426, 478.914, 478.626, 479.395|
|8192|764.098, 763.458, 771.041, 811.010|778.114, 775.970, 800.194, 831.810|
|16384|1356.739, 1392.771, 1505.827, 1540.388|1362.925, 1473.773, 1577.967, 1561.679|

The independent terminal audit passed once:104 finite, repeat-exact cross-arm rank outputs; all169 original sealed members (161 collected plus8 byte-identical cached output files),104 candidate source files, runtime, fresh control, source and process closure bindings verified. The original gzip bytes remain remote and were **not** locally rehashed. Complete member-file verification does not reconstruct or claim verification of original gzip bytes.

- Original archive SHA256: `180879131d00ba5a4fb65d3329909fd256fa8166194c8f31363a67441b2d17ea`.
- Independent file/timing audit SHA256: `645db008b620be09d39fb406f5744e25b559ba887138d771d418df7ec66f8f36`.
- Source `ca05e1659a61c63a1d5fa21370fc1aae7cdd62cd`; baseline `d01f074947d2cc754d6062c2b2ffe674e1577a34` from the same hu15 prefix-study A1.
- Closure epoch1789830278.104872: all recorded owned groups absent and GPUs idle. No further GPU qualification or sanitizer is justified by this performance result.
