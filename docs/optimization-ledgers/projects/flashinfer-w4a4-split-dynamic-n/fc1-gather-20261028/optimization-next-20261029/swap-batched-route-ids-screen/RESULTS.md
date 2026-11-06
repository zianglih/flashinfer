# Batched swap route metadata — independent review

Recommend retaining for instruction efficiency with near-neutral broad performance. The policy groups independent route-ID preloads into warp-wide batches at compile time, with no model/dtype branch, new tactic, altered register quota or additional synchronization. The measured source is `5037dea841027df0e3fccb4b214b2ea763408e5fd9c1233868c0356508e5cb0b` on retained `e780f02cc1f8a7e59f22b8bda6f7acd8f8792b24`.

- Source/proof: only the preload region changes. All four K-loop ASTs and the complete SF suffix are identical. Independent enumeration covers42,084 geometry/valid/CTA/top-K cases and1,230,992 cached-coordinate comparisons, including sparse rows, OOB sentinels and the dynamic two-CTA row split.
- Qualification:23 existing exact cases per arm,44 codegen captures per arm. All21 FC2 binaries are identical. Thirteen FC1 kernels reduce route load sites; total non-NOP instruction counts fall13–97 in changed kernels, while shuffle, branch, TMA, tensor-core data and asynchronous SF-copy site counts remain unchanged. All captures have zero stack/local storage.
- Compiler boundary: generated changes extend beyond the source preload. Two N128/two-CTA variants remove two ELECT instructions; three N256/one-CTA variants add two or four in the MMA/scale-copy region. Gather-role election counts are unchanged. The exact N3U EP4K N256/two-CTA/ReLU2/K512 native kernel was not in the diagnostic capture set, and runtime guards do not save SASS. Its small regression cannot be attributed to those election changes from present evidence.

|Scope|Cells|Geometric speedup|
|---|---:|---:|
|All|24|+0.248%|
|Decode|11|+0.049%|
|Prefill|13|+0.417%|
|EP|13|+0.360%|
|TP|11|+0.116%|

Stable examples: N3U TP per-token16K +0.620% (C/A repeats0.059/0.001%), with FC1 critical-path extension−10.04µs; K3 EP W4A4 8K +0.215% (0.003/0.020%). N3U EP W4A4 4K loses0.318% (0.020/0.123%), with FC1 extension+0.89µs. Component durations overlap under PDL and are not additive.

V3 EP16K MXFP8 appears +4.079% but C/A repeats are5.886/5.431%, so it is inconclusive. The other V3 EP16K MX format also has repeats above1%. As a diagnostic, the22 cells with both repeats below1% average +0.080% overall /+0.111% prefill; the complete24-cell aggregate and every raw phase remain primary. No best-of selection or noisy-row deletion was used. Coarse NVML reports2032MHz in the unstable MXFP8 windows and does not explain the drift; do not claim a clock cause.

All8 jobs /32 complete C-A-A-C phases /9,600 strict-CUPTI samples use matched source/tactics/routes/cache and one physical GPU per complete job. Input quantization, cold-L2 graphs,10 warmups and100 samples/phase are unchanged.32 runtime receipts /188 loaded MoE kernels pass with unchanged compile flags and zero local bytes; this excludes quantizer resource claims. Two of384 NVML quartile windows have no sample. GPUs2/4 completed successfully and were verified idle. No new GPU tests, sanitizer, source edits, clocks changes or GitHub writes were performed by this auditor.

The8 per-job archives and all file manifests are verified. `independent-method-audit.json` binds the exact23-case gate/codegen receipts to both timed sources and proves timing-engine AST equivalence apart from description text. `independent-perf-audit.json`, `phase-clock-summary.json` and `component-summary.json` preserve all qualifications. Fetch-only metadata helper corrections handle absent optional files; no measured source or process changed.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|8|W4A4|47.281|47.248|47.488|47.472|+0.018%|0.405%|0.508%|
|N3U EP8|4096|W4A4|233.105|233.969|233.682|233.058|-0.318%|0.020%|0.123%|
|N3U EP8|16384|W4A4|589.075|589.732|589.204|591.156|+0.110%|0.353%|0.090%|
|K3 EP8|8|W4A4|78.704|78.512|78.513|78.641|+0.203%|0.081%|0.001%|
|K3 EP8|8192|W4A4|481.619|480.531|480.627|481.603|+0.215%|0.003%|0.020%|
|V3 EP8|8|MXFP4x8|56.320|56.353|56.257|56.321|+0.028%|0.001%|0.172%|
|V3 EP8|8|MXFP8|89.153|88.849|89.008|89.041|+0.189%|0.126%|0.179%|
|V3 EP8|16384|MXFP4x8|638.324|637.588|644.068|645.844|+0.196%|1.178%|1.016%|
|V3 EP8|16384|MXFP8|775.941|705.606|743.924|732.805|+4.079%|5.886%|5.431%|
|V41F EP4|32|MXFP4x8|119.520|119.585|119.505|119.569|-0.001%|0.041%|0.067%|
|V41F EP4|32|MXFP8|211.250|211.170|211.106|211.314|+0.068%|0.031%|0.031%|
|V41F EP4|4096|MXFP4x8|348.530|349.667|348.611|349.858|+0.016%|0.381%|0.303%|
|V41F EP4|4096|MXFP8|576.004|575.796|575.652|574.931|-0.045%|0.187%|0.025%|
|N3U TP8|32|PER-TOKEN|123.489|123.218|123.394|123.170|+0.019%|0.259%|0.143%|
|N3U TP8|4096|PER-TOKEN|551.798|550.392|550.006|551.975|+0.307%|0.032%|0.070%|
|N3U TP8|16384|PER-TOKEN|1796.678|1785.079|1785.094|1795.622|+0.620%|0.059%|0.001%|
|K3 TP8|8|PER-TOKEN|81.537|81.681|81.570|81.601|-0.069%|0.078%|0.137%|
|K3 TP8|8192|PER-TOKEN|1028.044|1027.900|1027.949|1028.621|+0.040%|0.056%|0.005%|
|V3 TP8|8|MXFP4x8|50.209|50.193|50.209|50.209|+0.016%|0.001%|0.033%|
|V3 TP8|8|MXFP8|70.705|70.769|70.513|70.753|+0.125%|0.068%|0.363%|
|V3 TP8|8192|MXFP4x8|679.944|680.360|679.081|679.337|-0.012%|0.089%|0.188%|
|V3 TP8|8192|MXFP8|731.913|732.569|732.729|734.249|+0.059%|0.319%|0.022%|
|V41F TP4|8|W4A4|51.921|51.889|52.000|51.904|-0.061%|0.033%|0.215%|
|V41F TP4|16384|W4A4|1043.885|1042.205|1042.653|1045.869|+0.235%|0.190%|0.043%|
