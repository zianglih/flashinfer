# Activation-source L1 policy: full incremental result

BEFORE=`7dc96269`; AFTER=`4d527ac6`. The source/codegen change is one L1 no-allocate policy bit on the128-bit caller activation load. Both use fused staging and deterministic integrated reduction. EP8/B300/CUDA13.2, H7168/I2048/E256/top-k8; precomputed-routing public forward. Each row retains all100 cold-L2 CUPTI rank-MAX samples after three warmups, with AUTO over the same four deterministic tactics. Durations areµs.

| Global tokens |7dc median|7dc MAD|4d median|4d MAD|7dc/4d|Both AUTO tactics|
|---:|---:|---:|---:|---:|---:|---|
|1|72.2730|0.9750|73.2170|1.1205|0.987107×|N64 / epilogue return|
|2|90.4650|0.6720|90.5770|0.9920|0.998763×|N64 / epilogue return|
|4|101.8410|0.9120|102.5130|0.6880|0.993445×|N64 / epilogue return|
|8|123.2810|0.8800|125.1695|0.8795|0.984912×|N64 / epilogue return|
|16|135.0890|1.4240|140.6095|0.8485|0.960739×|N64 / epilogue return|
|32|163.0100|0.7370|163.7135|0.8955|0.995703×|N64 / epilogue return|
|64|185.1535|0.7045|186.1460|0.8800|0.994668×|N64 / epilogue return|
|128|189.7135|0.9115|180.9615|0.9915|1.048364×|N64 / epilogue return|
|256|191.2185|0.9130|191.1385|0.9440|1.000419×|N64 / epilogue return|
|512|195.8260|0.7845|194.8980|0.9600|1.004761×|N64 / epilogue return|
|1024|222.7545|1.1365|221.2020|0.6400|1.007018×|N64 / epilogue return|
|2048|300.3705|1.4245|304.2600|2.0965|0.987217×|N128 / dispatch return|
|4096|467.4920|3.9995|468.1335|3.1370|0.998630×|N128 / dispatch return|
|8192|768.8085|11.8255|795.5780|22.2560|0.966352×|N128 / dispatch return|

**8–8192 geometric speedup: 0.995104878×.** Four of eleven retained rows are faster. Rows1/2/4 remain shown but are excluded from retention. All14 rows select the same per-rank tactics as BEFORE. All112 rank-token outputs are exact against both7dc and retained04.

Keep7dc as the performance baseline; this sweep does not support promoting the activation-source cache hint. The128-token gain is clear within this run, but16 tokens is also clearly slower; the other changes are mixed. No specialized dispatch or follow-up timing run is implied.

| Global tokens |7dc Q1 /Q2 /Q3 /Q4 (µs)|4d Q1 /Q2 /Q3 /Q4 (µs)|
|---:|---|---|
|1|72.704 / 72.160 / 72.193 / 72.961|73.153 / 73.249 / 73.442 / 73.089|
|2|91.393 / 90.529 / 90.112 / 90.401|90.850 / 90.657 / 90.273 / 90.017|
|4|101.985 / 101.345 / 101.474 / 102.337|102.401 / 102.465 / 102.785 / 102.304|
|8|123.457 / 123.521 / 123.521 / 122.818|125.537 / 124.801 / 124.705 / 125.282|
|16|134.753 / 135.489 / 134.593 / 135.265|140.705 / 140.801 / 140.642 / 140.129|
|32|163.553 / 163.298 / 162.722 / 162.785|164.194 / 163.585 / 163.714 / 163.330|
|64|185.761 / 184.737 / 185.410 / 185.154|186.690 / 186.146 / 186.498 / 185.506|
|128|189.473 / 189.666 / 189.602 / 189.922|180.931 / 181.217 / 180.066 / 181.859|
|256|191.266 / 191.490 / 190.978 / 191.075|191.843 / 191.330 / 190.659 / 190.499|
|512|195.842 / 194.978 / 196.418 / 196.098|195.746 / 195.106 / 194.498 / 194.818|
|1024|223.938 / 223.522 / 222.306 / 221.891|221.506 / 221.090 / 221.346 / 220.963|
|2048|300.931 / 300.644 / 300.003 / 300.483|304.548 / 305.316 / 304.164 / 303.652|
|4096|463.525 / 467.364 / 469.956 / 468.068|469.477 / 469.574 / 467.942 / 468.294|
|8192|762.056 / 762.505 / 785.321 / 795.081|764.618 / 763.658 / 799.531 / 806.538|

- At128, the median improves8.752µs with MADs0.9115/0.9920µs. At16, it slows5.5205µs with MADs1.4240/0.8485µs. Tactics are unchanged in both cases.
- At8192, the median slows26.7695µs, while both arms rise in later quarters:7dc762.056→795.081µs,4d764.618→806.538µs. MADs are11.8255/22.2560µs. All samples remain included.
- These are serial same-node arms with a reused baseline. MAD and ordered-quarter medians describe within-arm spread, not a causal confidence interval; temporal drift is not eliminated.
- The retained04/4d secondary geometric ratio is1.024696292×, reflecting earlier integrated/fused improvements. It is not the retention criterion for this isolated hint. No main68 or split-MoE timing is included.
