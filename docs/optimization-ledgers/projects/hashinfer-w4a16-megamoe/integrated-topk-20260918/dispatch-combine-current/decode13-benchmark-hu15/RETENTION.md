# Current-base fifth-WG W1 retention

Do not promote `2739b8d5fbe67437afb682f9413917dd16a26c20`. Active prefill ratios are **1.010541× / 0.960070× / 0.979782×** at 4K / 8K / 16K. The small 4K gain does not establish a broad benefit; larger rows regress amid substantial sample drift. All 13 selected tactics match on all 8 ranks.

The source capacity gate omits dispatch participation whenever `capacity * hidden_tiles <= 512 * launched_CTAs`; that false specialization restores the complete d01 AST. Canonical decode is expected to use that path. Generated identity has not been captured, so the observed 0.989708× decode aggregate is recorded without attributing it to the fifth group's execution or using it as the principal rejection rationale.

Fresh same-boot hu15 d01/A1 from the prefix study is the control; S2 is only the immediately preceding closed process/source namespace. EP8/H7168/I2048/E256/K8, AUTO4/O3, 3 warmups and 100 cold-L2 CUDA-graph CUPTI rank-MAX samples per row. Speedup is A1/W1. All times and MAD values below are µs. MAD is descriptive, not a causal confidence interval; serial arms do not cancel drift.

|T|A1 median|W1 median|Speedup|A1 MAD|W1 MAD|Matching tactic|
|---:|---:|---:|---:|---:|---:|---|
|1|65.6640|66.4805|0.987718|0.9605|0.5280|N64 / epi_warps|
|2|87.3285|90.9605|0.960071|0.7685|0.9755|N64 / epi_warps|
|4|96.5285|96.6085|0.999172|0.6395|1.1680|N64 / epi_warps|
|8|121.9200|121.2000|1.005941|0.8485|0.8480|N64 / epi_warps|
|16|132.0170|135.1040|0.977151|0.9120|1.1515|N64 / epi_warps|
|32|160.1920|161.2805|0.993251|0.8325|0.9600|N64 / epi_warps|
|64|183.0565|182.9605|1.000525|0.7680|0.8165|N64 / epi_warps|
|128|185.3935|187.8250|0.987054|0.9115|0.8800|N64 / epi_warps|
|256|190.2565|200.8485|0.947264|0.9280|0.8965|N64 / epi_warps|
|512|197.3120|195.6005|1.008750|1.6160|1.0730|N64 / epi_warps|
|4096|464.8015|459.9530|1.010541|3.1685|3.8720|N128 / reuse_dispatch_warps|
|8192|769.0255|801.0100|0.960070|5.9200|24.1155|N128 / reuse_dispatch_warps|
|16384|1496.6120|1527.4945|0.979782|49.4715|45.6015|N128 / reuse_dispatch_warps|

At 4K every W1 quarter is faster than every A1 quarter. At 8K W1 rises from 761.573 to 822.722µs; at 16K both arms drift strongly, with W1 quarters 1352.296/1475.974/1543.459/1566.212µs. This supports a limited favorable 4K observation, not consistent prefill improvement.

|T|A1 successive 25-sample quarters (µs)|W1 quarters (µs)|
|---:|---|---|
|1|66.848, 65.632, 65.568, 65.440|66.785, 66.272, 66.369, 66.560|
|2|87.392, 87.585, 87.072, 87.360|91.424, 91.233, 91.008, 90.464|
|4|96.833, 96.224, 96.609, 96.257|96.768, 96.192, 96.064, 97.697|
|8|122.368, 122.016, 120.897, 121.984|121.344, 121.280, 120.928, 121.184|
|16|131.714, 131.937, 131.810, 132.193|135.424, 135.232, 134.496, 135.200|
|32|159.713, 159.361, 160.481, 160.832|160.930, 161.216, 160.866, 161.793|
|64|183.072, 183.585, 183.169, 182.785|183.297, 183.040, 182.144, 183.041|
|128|185.729, 185.633, 185.218, 185.057|188.321, 186.945, 188.033, 187.618|
|256|190.496, 190.433, 190.081, 190.048|201.409, 200.961, 200.353, 201.088|
|512|197.313, 198.881, 196.641, 196.192|195.936, 195.520, 195.489, 195.777|
|4096|462.529, 464.225, 464.833, 465.793|459.714, 459.521, 461.793, 458.529|
|8192|764.098, 763.458, 771.041, 811.010|761.573, 764.709, 803.106, 822.722|
|16384|1356.739, 1392.771, 1505.827, 1540.388|1352.296, 1475.974, 1543.459, 1566.212|

Independent terminal audit passed once: 104 finite/repeat-exact cross-arm outputs, all 169 original sealed member files (161 new plus 8 exact cached files), source 104, runtime, control, predecessor and final closure. No original gzip bytes were locally verified; complete member verification is a distinct boundary.

- Audit SHA256: `a63435e1d187e34b15c669e01ddbe3ca3de2e76537be78d9376c2d320f294a1f`.
- Original remote archive SHA256: `da5ca0064c79cf779a4f1215db1e01d6a78d87a4285f82417abd704cd5c4f1a8`.
- Final closure epoch 1789831445.9920802: all recorded owned process groups absent and GPUs idle.

No additional generated capture, native qualification or sanitizer is warranted by this result alone. Preserve the candidate and evidence unpromoted.
