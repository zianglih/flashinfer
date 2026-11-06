# Coordinate recurrence R1 retention

Do not promote `63f49bc77f34492922985e6760174a93d06286f3`. The active prefill ratios are **1.007633× / 0.990740× / 1.008518×** at 4K / 8K / 16K. The 4K quarters support a small favorable observation; 8K regresses and the 16K median gain is not consistent across quarters. This does not establish a useful broad improvement. All 13 selected tactics match on all 8 ranks.

Only continuation coordinate preparation changes. Initial preparation is unchanged. The prior source-bound prefix diagnostic on the same hu15 boot records 148 CTAs on all 24 rank/case results. Thus the four-group worker stride is 148*512=75,776; canonical decode has at most ceil(512/8)*(7168/8)=57,344 workers and executes no continuation. The 0.999797× decode aggregate (3/8 wins) and isolated T2/T32/T512 gains do not measure the recurrence's execution. A source change could still affect generated allocation or scheduling, but this candidate has no generated capture establishing that effect. The matched tactics rule out a selected-tactic switch as the explanation.

Fresh same-boot hu15 d01/A1 from the prefix study is the control; W1 is only the immediately preceding closed process/source namespace. EP8/H7168/I2048/E256/K8, AUTO4/O3, 3 warmups and 100 cold-L2 CUDA-graph CUPTI rank-MAX samples per row. Speedup is A1/R1. All times and MAD values below are µs. MAD and quarters are descriptive; serial arms do not cancel drift.

|T|A1 median|R1 median|Speedup|A1 MAD|R1 MAD|Matching tactic|
|---:|---:|---:|---:|---:|---:|---|
|1|65.6640|66.0645|0.993938|0.9605|0.9115|N64 / epi_warps|
|2|87.3285|84.0165|1.039421|0.7685|0.8795|N64 / epi_warps|
|4|96.5285|97.4880|0.990158|0.6395|0.8645|N64 / epi_warps|
|8|121.9200|121.1680|1.006206|0.8485|0.9275|N64 / epi_warps|
|16|132.0170|134.9440|0.978310|0.9120|0.9915|N64 / epi_warps|
|32|160.1920|156.9295|1.020790|0.8325|0.7355|N64 / epi_warps|
|64|183.0565|183.5685|0.997211|0.7680|0.9435|N64 / epi_warps|
|128|185.3935|187.9525|0.986385|0.9115|0.7045|N64 / epi_warps|
|256|190.2565|191.1040|0.995565|0.9280|1.1995|N64 / epi_warps|
|512|197.3120|192.5605|1.024675|1.6160|0.7360|N64 / epi_warps|
|4096|464.8015|461.2805|1.007633|3.1685|3.1995|N128 / reuse_dispatch_warps|
|8192|769.0255|776.2130|0.990740|5.9200|20.2085|N128 / reuse_dispatch_warps|
|16384|1496.6120|1483.9720|1.008518|49.4715|79.1525|N128 / reuse_dispatch_warps|

At 4K all R1 quarter medians (459.330–461.955µs) are below all A1 quarters (462.529–465.793µs), a limited favorable result. At 8K R1 rises from 760.679 to 818.565µs, and its last two quarters are slower than the corresponding A1 quarters. At 16K the first two R1 quarters are faster and the last two are slower; R1 MAD is 79.1525µs versus A1 49.4715µs, both larger than the 12.640µs median difference. No repeat or generated-code evidence turns that serial median into a robust causal gain.

|T|A1 successive 25-sample quarters (µs)|R1 quarters (µs)|
|---:|---|---|
|1|66.848, 65.632, 65.568, 65.440|66.368, 66.561, 65.632, 65.664|
|2|87.392, 87.585, 87.072, 87.360|84.000, 84.064, 84.416, 83.520|
|4|96.833, 96.224, 96.609, 96.257|97.505, 97.441, 97.313, 97.505|
|8|122.368, 122.016, 120.897, 121.984|122.048, 120.961, 120.736, 120.896|
|16|131.714, 131.937, 131.810, 132.193|135.137, 135.648, 135.104, 134.528|
|32|159.713, 159.361, 160.481, 160.832|156.929, 157.057, 156.993, 156.705|
|64|183.072, 183.585, 183.169, 182.785|183.584, 183.393, 183.840, 183.584|
|128|185.729, 185.633, 185.218, 185.057|187.649, 188.129, 187.872, 188.032|
|256|190.496, 190.433, 190.081, 190.048|191.297, 190.464, 191.104, 191.137|
|512|197.313, 198.881, 196.641, 196.192|192.801, 192.706, 192.288, 192.417|
|4096|462.529, 464.225, 464.833, 465.793|461.859, 461.089, 459.330, 461.955|
|8192|764.098, 763.458, 771.041, 811.010|760.679, 762.084, 808.199, 818.565|
|16384|1356.739, 1392.771, 1505.827, 1540.388|1352.652, 1372.227, 1516.804, 1547.652|

Independent terminal audit passed once: 104 finite/repeat-exact cross-arm outputs, all 169 original sealed member files (161 new plus 8 exact cached files), source 104, runtime, control, W1 predecessor and final closure. The original gzip bytes were not locally verified; complete member verification is a distinct boundary.

- Audit SHA256: `b0f93d19e26c2da74f4d5ab6e33bd28d0efd2dedeb9bcf36714ba69986dab1dc`.
- Original remote archive SHA256: `d013fa81f7e2779c36e074da12e49744f28429f0f62f7709a91a698939766407`.
- Same-boot prior diagnostic closure SHA256: `6af3c9b5830365270d0f8fecd23bcae3589021d693433d39c88d063afc82da13`; its 24 `prefix_diagnostic.shape` records supply the 148-CTA observation, not a new GPU query.
- Final closure epoch 1789832333.7908282: all recorded owned process groups absent and GPUs idle.

Preserve the candidate and complete evidence unpromoted. No new qualification, generated capture or sanitizer is warranted by this result alone.
