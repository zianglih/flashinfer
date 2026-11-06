# Swap TMEM startup: rejected

14 source-paired CAAC cells /20 phases /5,600 strict-CUPTI samples compare retained6c with allocator ownership moved to the first epilogue warp and allocation publication narrowed to MMA/epilogue users. The required one-CTA initialization barrier remains; two-CTA cluster publication is unchanged. W4A16 is unaffected.

Overall geometric speedup−0.022%, decode+0.086%, prefill−0.130%. N3U EP W4A4 T8 gains+0.861%, but T4096 loses−1.132% with repeat spreads0.268/0.013% and observed2032MHz/reason0. K3 TP per-token8192 gains+0.229%; most other cells are near-neutral. V3 TP16K MXFP4x8−0.513% and MXFP8+0.258% have clock/power variation; MXFP8 control spread1.085% makes that gain inconclusive. No clock changes. All224 quartile windows have samples.

Parent rejected the candidate: the extra startup work and more selective synchronization do not show a general payoff. The local review copy was retired only after exact source/patch/manifest proof. All helpers, exact gates, codegen and raw timing evidence remain.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|8|W4A4|47.857|47.456|47.361|47.776|+0.861%|0.168%|0.201%|
|N3U EP8|4096|W4A4|233.026|235.363|235.394|232.403|-1.132%|0.268%|0.013%|
|N3U TP8|32|PER-TOKEN|122.945|123.265|122.913|123.122|-0.045%|0.144%|0.286%|
|N3U TP8|16384|PER-TOKEN|1763.926|1761.909|1761.205|1761.077|+0.054%|0.162%|0.040%|
|V3 TP8|8|MXFP4x8|50.272|50.145|50.241|50.241|+0.127%|0.062%|0.191%|
|V3 TP8|8|MXFP8|70.625|70.880|70.769|70.737|-0.203%|0.159%|0.158%|
|V3 TP8|16384|MXFP4x8|1238.911|1242.050|1246.226|1236.610|-0.513%|0.186%|0.336%|
|V3 TP8|16384|MXFP8|1345.168|1349.729|1348.211|1359.760|+0.258%|1.085%|0.113%|
|V41F EP4|32|MXFP4x8|118.626|118.850|118.881|118.721|-0.162%|0.081%|0.026%|
|V41F EP4|32|MXFP8|210.899|210.979|210.850|211.011|+0.019%|0.053%|0.061%|
|V41F EP4|4096|MXFP4x8|349.796|349.269|349.221|349.700|+0.144%|0.027%|0.014%|
|V41F EP4|4096|MXFP8|576.071|575.751|575.479|575.863|+0.061%|0.036%|0.047%|
|K3 TP8|8|PER-TOKEN|81.505|81.489|81.601|81.601|+0.010%|0.118%|0.137%|
|K3 TP8|8192|PER-TOKEN|1073.341|1070.701|1071.197|1073.454|+0.229%|0.010%|0.046%|

All514 control source files match committed6c. Only moe_swap_ab_kernel.py differs; measured sources match the exact/codegen gate. All7 observer helpers are unchanged; the run engine differs from the prior audited engine only in docstring/receipt text.20 runtime receipts /112 loaded MoE kernels passed with unchanged compiler options and zero local bytes. The pre-launch missing-source-JSON failure is preserved separately and excluded from measurements; all accepted phases form complete CAAC sequences.
