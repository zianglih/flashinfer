R1 paired transpose + explicit completion:16-cell screen

Frozen base b13963b0; candidate kernel232e3a6a. This combines the formal generic-TMEM completion fix for every helper caller with paired transpose ordering in gated per-token and non-gated/ReLU2 branches. It is not an isolated pairing comparison. R0 was never executed.

Qualification:39 existing exact cases and76 matched compiled-kernel checks passed; no new REG/STACK/local growth. The two known synthetic MX FC1 STACK168 cases remain unchanged. The16 native performance cells have128 loaded MoE functions with runtime LOCAL0.

Method: same-GPU C-A-A-C, frozen native winners/routes, public API, unfused swap-AB, input quantizer included for the NVFP4 family,10warmups and100strict CUPTI samples per phase. No AUTO, retuning, clock changes or sanitizer. Persistent native/CuTe caches retained. Primary cell speedup=100*(sqrt(C1*C2)/sqrt(A1*A2)-1); aggregate is the geometric mean of cell ratios. Arithmetic phase-pair estimates remain in cells.csv as diagnostics.

Result: aggregate-0.723%, decode-0.188%, prefill-1.256%;14/16 cells negative. All6,400 samples,32 source-bound runtime-guard receipts and128 loaded functions were verified. No quartile NVML window is missing; stock clocks varied during execution. Four prefill cells have>2% within-arm phase spread and remain in all aggregates.

Do not expand to56 cells yet. The comparison does not support a performance retention claim. Preserve the required completion ordering and separate its cost from pairing by comparing to a serial helper with the same explicit waits.

|Model/topology|Mode|Tokens|C1 us|A1 us|A2 us|C2 us|Speedup|C spread|A spread|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
|kimi-k3 EP|PER-TOKEN|8|82.9770|83.0730|83.0575|83.1370|-0.010%|0.193%|0.019%|
|kimi-k3 EP|PER-TOKEN|16384|1018.2525|1050.7795|1022.3800|1018.7630|-1.734%|0.050%|2.778%|
|nemo3-ultra EP|W4A4|8|47.7930|47.4885|47.9370|47.9045|+0.286%|0.233%|0.944%|
|nemo3-ultra EP|W4A4|16384|585.1265|589.5270|590.4870|585.3185|-0.811%|0.033%|0.163%|
|v3 EP|MXFP8|8|88.4490|88.5130|88.4970|88.4490|-0.063%|0.000%|0.018%|
|v3 EP|MXFP8|16384|757.6250|747.2570|748.9695|722.4570|-1.107%|4.868%|0.229%|
|v41-flash EP|MXFP4x8|8|49.8720|50.0160|49.9525|49.8880|-0.209%|0.032%|0.127%|
|v41-flash EP|MXFP4x8|16384|789.7860|820.9700|826.9855|806.9540|-3.113%|2.174%|0.733%|
|kimi-k3 TP|MXFP4x8|8|79.5850|79.9045|79.8885|79.7120|-0.310%|0.160%|0.020%|
|kimi-k3 TP|MXFP4x8|16384|1632.2380|1656.3340|1624.0620|1577.9820|-2.148%|3.438%|1.987%|
|nemo3-ultra TP|PER-TOKEN|8|63.6485|64.0330|63.7770|63.7130|-0.351%|0.101%|0.401%|
|nemo3-ultra TP|PER-TOKEN|16384|1785.8710|1803.2930|1803.9510|1786.0625|-0.979%|0.011%|0.036%|
|v3 TP|MXFP8|8|70.8485|71.1690|71.2325|70.7840|-0.540%|0.091%|0.089%|
|v3 TP|MXFP8|16384|1344.1070|1344.2040|1343.3400|1344.7795|+0.050%|0.050%|0.064%|
|v41-flash TP|W4A4|8|52.4800|52.5440|52.6245|52.3690|-0.304%|0.212%|0.153%|
|v41-flash TP|W4A4|16384|1041.5765|1043.4320|1043.1445|1041.5610|-0.165%|0.001%|0.028%|

The stable N3U TP per-token16K loss is predominantly FC1 duration(+18.088us); FC2 adds0.503us and its end-after-FC1 interval falls0.344us. N3U EP W4A4 FC1 grows4.920us and FC2 grows3.344us, but their overlap prevents summing those durations as end-to-end cost. Full per-phase quartiles, component durations, exposed extensions and raw samples are retained under evidence/results/*/{analysis.json,component-samples.json}; no overlapping durations were summed for end-to-end timing.

Sources and methodology receipts: evidence/perf-config.json, metadata-fetch-receipt.json, fetch-receipts/*.json and harness-proof.json. Every row, including negatives and noisy cells, is preserved in summary.json and cells.csv.
