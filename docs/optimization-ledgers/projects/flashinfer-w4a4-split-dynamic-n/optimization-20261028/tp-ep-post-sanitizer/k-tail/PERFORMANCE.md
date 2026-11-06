# Tail-only fixed-winner screen

113 cells,452 medians,45,200 CUPTI samples. Overall +0.071%; decode +0.073%; prefill +0.070%.

|Topology|Model|Backend|Decode|Prefill|
|---|---|---|---:|---:|
|EP|kimi-k3|CuteDSL MXFP4x8|-0.02%|+1.65%|
|EP|kimi-k3|CuteDSL PER-TOKEN|-0.06%|+0.23%|
|EP|kimi-k3|CuteDSL W4A4|+0.05%|-2.73%|
|EP|nemo3-ultra|CuteDSL MXFP4x8|-0.09%|-0.55%|
|EP|nemo3-ultra|CuteDSL MXFP8|-0.01%|-0.46%|
|EP|nemo3-ultra|CuteDSL PER-TOKEN|+0.10%|+0.03%|
|EP|nemo3-ultra|CuteDSL W4A4|+0.06%|-0.04%|
|EP|v3|CuteDSL MXFP4x8|-0.01%|+1.78%|
|EP|v3|CuteDSL MXFP8|+0.05%|+1.12%|
|EP|v3|CuteDSL PER-TOKEN|-0.01%|-0.07%|
|EP|v3|CuteDSL W4A4|-0.08%|-0.12%|
|EP|v41-flash|CuteDSL MXFP4x8|+0.03%|-1.24%|
|EP|v41-flash|CuteDSL MXFP8|+0.06%|+0.16%|
|EP|v41-flash|CuteDSL PER-TOKEN|+0.01%|+0.13%|
|EP|v41-flash|CuteDSL W4A4|-0.00%|-0.16%|
|TP|kimi-k3|CuteDSL MXFP4x8|+0.46%|+0.03%|
|TP|kimi-k3|CuteDSL PER-TOKEN|+0.19%|-0.06%|
|TP|kimi-k3|CuteDSL W4A4|+0.22%|+1.15%|
|TP|nemo3-ultra|CuteDSL MXFP4x8|+0.09%|-0.24%|
|TP|nemo3-ultra|CuteDSL MXFP8|+0.08%|+0.09%|
|TP|nemo3-ultra|CuteDSL PER-TOKEN|+0.36%|+0.05%|
|TP|nemo3-ultra|CuteDSL W4A4|+0.03%|+0.16%|
|TP|v3|CuteDSL MXFP4x8|-0.16%|-0.03%|
|TP|v3|CuteDSL MXFP8|+0.08%|+0.01%|
|TP|v3|CuteDSL PER-TOKEN|+0.22%|+0.52%|
|TP|v3|CuteDSL W4A4|+0.36%|+0.16%|
|TP|v41-flash|CuteDSL PER-TOKEN|-0.08%|+0.18%|
|TP|v41-flash|CuteDSL W4A4|+0.09%|+0.33%|

Same retained frozen winners, C-A-A-C,100 CUPTI samples per pass; no tuning or event timing. Standard medians are primary; raw temporal strata are retained only for diagnosis. This is a candidate-source comparison, not an updated external-baseline table.

Focused aligned controls (same frozen winners, independent CAAC): K3 EP8 W4A4 16K −2.403% standard median, V41F EP4 MXFP4x8 16K +2.430%. These are retained as separate diagnostics, not replacements. Both FC1/FC2 PTX, cubin, SASS and resource outputs are byte-identical between sources for BOTH rows; STACK/LOCAL remain zero. K3 first25 medians0.703–0.706ms and last25 medians0.730–0.788ms show temporal drift shared by both sources. The aligned outliers are not attributable to altered GEMM machine code. Retain the isolated tail peel for instruction sanity with neutral overall113-cell evidence; claim no broad performance gain. See focused-evidence/byte-identity-proof.json and focused-summary.json.
