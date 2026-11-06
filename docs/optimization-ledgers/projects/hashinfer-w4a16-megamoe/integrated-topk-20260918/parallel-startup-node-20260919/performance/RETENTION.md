# Fresh hu115 startup retention

Keep both candidates unpromoted. Against fresh d01/A1, early scheduler broadcast2bb/B1 yields **0.987321351×** decode geometric speedup and preinit stagingec742/C1 yields **1.000088673×**, each with 4/8 faster decode rows. Both independent candidates use the same selected tactics as A1 in all 13 shapes and all 8 ranks. Neither establishes a broad startup gain; this result does not justify additional GPU qualification.

B1's material T32/T64 regressions persist across the quarter medians. C1 has favorable T8/T128 observations, but its T64 regression offsets them. All arms show substantial prefill drift; both candidates are slower at 8K/16K. These serial samples do not establish the causal cost or achieved overlap of the source changes. Generated placement has not been captured for these candidates. The derived B1/C1 decode ratio1.012931273× compares two alternatives and is not a gain over retained d01.

Same hu115 boot; EP8/H7168/I2048/E256/K8, O3/AUTO4, 3 warmups and 100 cold-L2 CUDA-graph CUPTI rank-MAX samples per shape. All times and MAD values below are µs; speedups divide the named control median by candidate median. MAD measures within-arm spread, not a causal confidence interval.

|T|A1 median|B1 median|A1/B1|C1 median|A1/C1|B1/C1|Matching tactic|
|---:|---:|---:|---:|---:|---:|---:|---|
|1|68.3210|70.1765|0.973560|68.9285|0.991187|1.018106|N64 / epi_warps|
|2|91.5530|90.6090|1.010418|91.3290|1.002453|0.992116|N64 / epi_warps|
|4|101.5690|103.0730|0.985408|101.8885|0.996864|1.011625|N64 / epi_warps|
|8|125.1205|125.4410|0.997445|122.0170|1.025435|1.028062|N64 / epi_warps|
|16|135.1695|134.9285|1.001786|136.4015|0.990968|0.989201|N64 / epi_warps|
|32|164.9775|176.1780|0.936425|164.5775|1.002430|1.070487|N64 / epi_warps|
|64|180.1455|187.2815|0.961897|188.6260|0.955041|0.992872|N64 / epi_warps|
|128|193.4420|192.5290|1.004742|188.0180|1.028848|1.023992|N64 / epi_warps|
|256|198.0660|196.1945|1.009539|195.9865|1.010610|1.001061|N64 / epi_warps|
|512|198.9295|198.1940|1.003711|200.4500|0.992415|0.988745|N64 / epi_warps|
|4096|478.9330|479.0110|0.999837|476.9165|1.004228|1.004392|N128 / reuse_dispatch_warps|
|8192|786.6795|819.8640|0.959524|816.2320|0.963794|1.004450|N128 / reuse_dispatch_warps|
|16384|1520.8965|1540.6205|0.987197|1537.4545|0.989230|1.002059|N128 / reuse_dispatch_warps|

|T|A1 MAD|B1 MAD|C1 MAD|
|---:|---:|---:|---:|
|1|1.1030|1.8075|1.1195|
|2|1.4240|1.1040|1.4395|
|4|1.0085|1.2160|1.2640|
|8|1.6800|1.4400|1.7600|
|16|1.2635|1.3275|1.6000|
|32|1.8405|1.6160|1.5195|
|64|1.1045|1.9840|1.2960|
|128|2.9755|2.2890|1.1995|
|256|1.2000|1.0240|1.3925|
|512|1.8725|1.2480|1.1200|
|4096|3.0720|3.7110|3.2640|
|8192|14.6875|26.7360|17.1200|
|16384|50.2565|73.0085|78.1745|

|T|A1 successive 25-sample quarters (µs)|B1 quarters (µs)|C1 quarters (µs)|
|---:|---|---|---|
|1|68.449, 67.905, 68.353, 68.672|67.649, 69.601, 72.257, 71.328|68.897, 69.120, 69.569, 68.417|
|2|88.450, 90.177, 92.448, 92.513|89.344, 90.689, 90.945, 90.977|89.089, 91.681, 91.841, 91.617|
|4|101.761, 101.089, 101.633, 101.824|101.825, 103.681, 103.200, 103.297|100.577, 101.633, 102.049, 102.658|
|8|122.946, 125.857, 126.304, 124.641|122.369, 126.049, 126.049, 125.537|119.842, 120.930, 123.809, 122.785|
|16|135.713, 135.170, 135.265, 135.010|133.345, 134.433, 135.073, 136.641|133.793, 135.618, 137.217, 138.017|
|32|161.889, 163.266, 166.465, 165.762|173.954, 176.450, 176.194, 176.609|161.762, 164.545, 165.794, 164.450|
|64|178.817, 180.258, 180.483, 180.673|183.586, 185.538, 187.554, 188.418|186.946, 188.386, 189.410, 189.537|
|128|189.921, 193.185, 195.137, 194.530|187.906, 190.529, 194.178, 193.794|186.275, 188.066, 188.706, 188.194|
|256|197.377, 197.794, 198.146, 198.306|192.833, 195.714, 196.354, 197.026|193.026, 196.226, 196.450, 196.353|
|512|198.626, 199.362, 200.802, 198.370|196.354, 198.946, 198.690, 198.370|200.642, 200.642, 200.098, 200.642|
|4096|476.709, 479.046, 479.525, 479.781|478.885, 478.565, 477.891, 482.373|473.573, 476.517, 477.541, 479.077|
|8192|779.849, 778.278, 817.639, 831.049|786.471, 783.622, 839.945, 840.553|785.544, 782.345, 824.648, 824.328|
|16384|1396.590, 1510.448, 1568.529, 1569.073|1392.651, 1525.036, 1605.100, 1622.029|1401.451, 1528.944, 1542.032, 1625.836|

B1 T32 quarter medians173.954–176.609µs all exceed A1's161.889–166.465µs. At T64, A1 spans178.817–180.673µs, B1 spans183.586–188.418µs and C1 spans186.946–189.537µs. Conversely, C1 T128 spans186.275–188.706µs versus A1's189.921–195.137µs. The opposing changes are visible in the raw subdivisions and cannot be dismissed or selected away. At 8K all three arms drift upward within their runs; at 16K quarter medians span roughly1.39–1.63ms. Preserve the full distribution rather than treating the small aggregate or selected wins as stable improvement.

Independent terminal audit passed once: all436 original sealed member files (412 collected plus24 byte-identical cached outputs),312 source files, runtime/source reviews, node/setup/launch and all process/GPU closure bindings verified. Every comparison A1/B1, A1/C1 and derived B1/C1 preserves104 finite, repeat-exact rank outputs and all1,300 samples per arm. The original gzip is remote and was not locally rehashed; complete member-file reconstruction is a distinct verification boundary.

- Audit SHA256: `757f42aaa1d98823dbe14f4341528071d0c83dea7ebe481f8bed311391ea2118`.
- Original archive SHA256: `ba43e633e0802d10c6237d568dd1f2e46c36bcdc549a6e94990033e2d18b8f5b`.
- A1: `d01f074947d2cc754d6062c2b2ffe674e1577a34`; B1: `2bb3a02ea9951e4d5c999bd2a955a47b3ee55f2e`; C1: `ec7428dc0f96a32010661c18fe154c1dfec1b9b5`.

The conditional qualification plan remains held. No sanitizer or new GPU action followed from this audit.
