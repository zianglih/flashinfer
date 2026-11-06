# Predicated gathered-SF live-row screen

Recommendation: retain as removal of unnecessary shared-memory stores; treat end-to-end performance as neutral, without a headline speedup claim.

- **Source:** retained `374ed4c07ee3a8c30a30026018a96d8f613ac4b5` versus R1 kernel SHA `0046a405ab15ffc2b520e873165273fb08892046510978ea9d627be7dc7337f0`. Only `moe_swap_ab_kernel.py` differs. The production copy is frozen. Diagnostic poisoned copies were never timed.
- **Change:** skip the `cp.async` instruction for SFB rows outside the already-selected rounded MMA N. Preserve zero fill for valid-to-rounded padding and K tails. Counts, relay, stage reuse, PDL and FC2 are unchanged. This avoids redundant shared zero stores/completion work, not valid-input HBM traffic.
- **Correctness:** R1 passed23 existing exact cases. Additional production and NaN-poison arms each passed16 cases/80 checks, including one/two CTA,128/129 transition, K96 tails, dynamic routing under graph replay, CLC and true persistent-stage reuse. Exact padding/output hashes agree. Source proof and complete evidence are in `../gather-sf-live-rows-predicated-poison/`.
- **Generated code:**44 kernels; all21 FC2 CUBINs byte-identical to374. No branch/MMA count changes; FC1 non-NOP instruction delta−10 to+4; direct predicated LDGSTS confirmed; no local storage. See `../gather-sf-live-rows-predicated/codegen-comparison.json`.
- **Timing:**24 cells, all four affected formats, all four models in EP and TP. Each job uses one physical B300 for complete C-A-A-C, frozen374 native winners and identical route/cache hashes, public unfused API, input quantizer included for NVFP4, cold-L2 CUDA graphs,10 warmups and100 strict CUPTI samples/phase.32 phases /9,600 samples. Runtime resource guards all passed, with no instrumentation compile options. Stock clocks; no clock settings changed.

|Scope|Cells|Geometric speedup|
|---|---:|---:|
|All|24|+0.126%|
|Decode|8|+0.031%|
|Middle|8|−0.011%|
|Prefill|8|+0.359%|
|EP prefill|4|+0.967%|
|TP prefill|4|−0.244%|

All24 rows, including nine negative cells, are preserved below. The all-cell result includes two inconclusive V3 MXFP8 prefill measurements: EP16K+3.411% with control/candidate repeat spreads3.955/4.466%; TP16K−0.912% with control spread2.253%. Their phases show varying clock samples, and the unchanged FC2 also moved. Telemetry is observational and does not prove causality. All384 quartile windows had NVML samples. As a sensitivity check only, the22 rows with both repeat spreads≤0.5% aggregate+0.027%; the six prefill rows meeting that criterion aggregate+0.072%. This does not replace the full24-cell result or establish statistical significance.

The stable V41F TP W4A4 16K cell improved0.224% (control/candidate spreads0.001/0.015%) and FC1 fell421.971→419.716µs while FC2 remained440.180→440.084µs. N3U EP W4A4 16K improved0.164% and K3 EP per-token8K was−0.015%. These support neutral-to-small-positive behavior, not closing a large end-to-end gap.

Archive SHA256: `eaad3b67c480501aa0ad573a0dc5514eae39f9a4d73fa23637bb593538a90571` (1,146 files, all manifest hashes verified). Source/config receipts, all32 phase medians, component timelines, clock samples and resource guards are under `evidence/`. The derived metric is exactly `100*(sqrt(C1*C2/(A1*A2))-1)`. No historical external baselines were rerun. No sanitizer was run.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|16|W4A4|82.752|82.689|82.880|82.945|+0.077%|0.233%|0.232%|
|N3U EP8|512|W4A4|140.129|139.953|140.161|139.937|-0.017%|0.138%|0.149%|
|N3U EP8|16384|W4A4|595.956|594.516|594.836|595.348|+0.164%|0.102%|0.054%|
|V41F TP4|16|W4A4|87.313|87.297|87.409|87.409|+0.009%|0.110%|0.128%|
|V41F TP4|512|W4A4|321.587|321.298|321.315|321.251|+0.035%|0.105%|0.005%|
|V41F TP4|16384|W4A4|1047.769|1045.337|1045.497|1047.754|+0.224%|0.001%|0.015%|
|K3 EP8|16|PER-TOKEN|117.633|117.440|117.648|117.665|+0.089%|0.027%|0.178%|
|K3 EP8|512|PER-TOKEN|353.954|354.145|355.042|354.082|-0.162%|0.036%|0.253%|
|K3 EP8|8192|PER-TOKEN|630.163|630.564|629.221|629.428|-0.015%|0.117%|0.214%|
|N3U TP8|32|PER-TOKEN|123.681|123.457|123.154|123.170|+0.097%|0.415%|0.246%|
|N3U TP8|512|PER-TOKEN|179.633|179.730|179.890|180.146|+0.044%|0.285%|0.089%|
|N3U TP8|16384|PER-TOKEN|1764.036|1761.909|1761.829|1763.414|+0.105%|0.035%|0.005%|
|V3 EP8|16|MXFP8|107.873|107.665|107.808|107.680|+0.038%|0.179%|0.133%|
|V3 EP8|512|MXFP8|246.626|246.034|246.018|245.810|+0.078%|0.332%|0.006%|
|V3 EP8|16384|MXFP8|740.165|717.508|686.836|712.004|+3.411%|3.955%|4.466%|
|V3 TP8|16|MXFP8|109.537|109.569|109.505|109.473|-0.029%|0.058%|0.058%|
|V3 TP8|512|MXFP8|268.851|269.506|269.378|269.186|-0.157%|0.125%|0.047%|
|V3 TP8|16384|MXFP8|1309.660|1335.324|1337.708|1339.164|-0.912%|2.253%|0.179%|
|V41F EP4|16|MXFP4x8|58.785|58.849|58.705|58.737|-0.027%|0.081%|0.244%|
|V41F EP4|512|MXFP4x8|292.513|292.402|292.466|292.738|+0.065%|0.077%|0.022%|
|V41F EP4|8192|MXFP4x8|495.459|494.516|494.579|497.059|+0.346%|0.323%|0.013%|
|K3 TP8|16|MXFP4x8|120.706|120.674|120.882|120.834|-0.006%|0.106%|0.172%|
|K3 TP8|512|MXFP4x8|348.276|348.228|348.260|348.404|+0.028%|0.037%|0.009%|
|K3 TP8|8192|MXFP4x8|922.251|928.027|927.803|926.332|-0.391%|0.442%|0.024%|
