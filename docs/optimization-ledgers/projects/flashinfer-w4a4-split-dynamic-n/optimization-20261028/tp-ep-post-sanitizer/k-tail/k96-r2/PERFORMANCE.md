# K96 fixed-winner screen

64 cells,256 medians,25,600 CUPTI samples. Overall -0.021%; decode -0.267%; prefill +0.227%.

|Topology|Model|Backend|Decode|Prefill|
|---|---|---|---:|---:|
|EP|kimi-k3|CuteDSL PER-TOKEN|-0.21%|+0.05%|
|EP|kimi-k3|CuteDSL W4A4|-0.30%|+1.86%|
|EP|nemo3-ultra|CuteDSL PER-TOKEN|-0.45%|+0.13%|
|EP|nemo3-ultra|CuteDSL W4A4|-0.15%|+0.70%|
|EP|v3|CuteDSL PER-TOKEN|-0.22%|+0.06%|
|EP|v3|CuteDSL W4A4|-0.36%|+0.56%|
|EP|v41-flash|CuteDSL PER-TOKEN|+0.13%|+0.07%|
|EP|v41-flash|CuteDSL W4A4|-0.76%|+0.33%|
|TP|kimi-k3|CuteDSL PER-TOKEN|-0.31%|-0.10%|
|TP|kimi-k3|CuteDSL W4A4|-0.17%|+0.00%|
|TP|nemo3-ultra|CuteDSL PER-TOKEN|-0.68%|-0.05%|
|TP|nemo3-ultra|CuteDSL W4A4|+0.10%|+0.10%|
|TP|v3|CuteDSL PER-TOKEN|-0.32%|+0.00%|
|TP|v3|CuteDSL W4A4|-0.43%|-0.25%|
|TP|v41-flash|CuteDSL PER-TOKEN|-0.04%|-0.02%|
|TP|v41-flash|CuteDSL W4A4|-0.09%|+0.21%|

Same retained frozen winners, C-A-A-C,100 CUPTI samples per pass; no tuning or event timing. Standard medians are primary; raw temporal strata are retained only for diagnosis. This is a candidate-source comparison, not an updated external-baseline table.
