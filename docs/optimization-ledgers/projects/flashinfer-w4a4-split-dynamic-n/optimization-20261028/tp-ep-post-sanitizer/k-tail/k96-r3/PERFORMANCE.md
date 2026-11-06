# K96 fixed-winner screen

64 cells,256 medians,25,600 CUPTI samples. Overall +0.139%; decode -0.066%; prefill +0.345%.

|Topology|Model|Backend|Decode|Prefill|
|---|---|---|---:|---:|
|EP|kimi-k3|CuteDSL PER-TOKEN|+0.07%|+0.28%|
|EP|kimi-k3|CuteDSL W4A4|-0.18%|+1.71%|
|EP|nemo3-ultra|CuteDSL PER-TOKEN|-0.23%|+0.33%|
|EP|nemo3-ultra|CuteDSL W4A4|-0.19%|+0.40%|
|EP|v3|CuteDSL PER-TOKEN|-0.03%|+0.49%|
|EP|v3|CuteDSL W4A4|-0.09%|+0.64%|
|EP|v41-flash|CuteDSL PER-TOKEN|-0.15%|+0.09%|
|EP|v41-flash|CuteDSL W4A4|+0.36%|+0.61%|
|TP|kimi-k3|CuteDSL PER-TOKEN|-0.20%|+0.05%|
|TP|kimi-k3|CuteDSL W4A4|+0.02%|+0.21%|
|TP|nemo3-ultra|CuteDSL PER-TOKEN|-0.28%|-0.02%|
|TP|nemo3-ultra|CuteDSL W4A4|+0.17%|+0.01%|
|TP|v3|CuteDSL PER-TOKEN|-0.25%|+0.13%|
|TP|v3|CuteDSL W4A4|-0.22%|+0.12%|
|TP|v41-flash|CuteDSL PER-TOKEN|+0.13%|+0.14%|
|TP|v41-flash|CuteDSL W4A4|+0.02%|+0.36%|

Same retained frozen winners, C-A-A-C,100 CUPTI samples per pass; no tuning or event timing. Standard medians are primary; raw temporal strata are retained only for diagnosis. This is a candidate-source comparison, not an updated external-baseline table.
