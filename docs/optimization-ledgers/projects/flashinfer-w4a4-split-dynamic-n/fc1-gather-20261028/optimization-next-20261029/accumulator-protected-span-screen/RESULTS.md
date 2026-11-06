# Protected span: rejected

The resource-derived wider overlap is correct in the focused tests, but regresses all6 affected frozen native winners: **−2.089% geomean**. The2 unchanged control cells are+0.178% together. Max phase repeat spread is0.142% for control and0.356% for candidate; no clock quartiles are missing. Source-paired22ffe control vs candidate53d61354, same GPU2, C-A-A-C,100 strict-CUPTI samples per phase, cold-L2 graphs,10 warmups, public API/input quantizer, unchanged frozen routes/tactics, no AUTO, no clock changes.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|32|W4A4|103.456|103.216|103.584|103.345|+0.000%|0.107%|0.356%|
|N3U EP8|4096|W4A4|232.418|234.480|234.752|232.401|-0.941%|0.007%|0.116%|
|N3U TP8|4096|W4A4|387.266|393.617|393.587|387.539|-1.575%|0.070%|0.008%|
|K3 TP8|8192|W4A4|847.268|847.893|848.965|846.933|-0.157%|0.040%|0.126%|
|K3 TP8|8192|PER-TOKEN|1074.070|1137.997|1137.639|1075.158|-5.555%|0.101%|0.032%|
|V3 TP8|8192|PER-TOKEN|775.284|807.429|807.173|776.149|-3.912%|0.111%|0.032%|
|V41F TP4|16384|PER-TOKEN|1268.408|1271.096|1272.920|1268.776|-0.269%|0.029%|0.143%|
|V3 TP8|512|MXFP8|270.674|269.427|269.618|270.289|+0.356%|0.142%|0.071%|

The large per-token regressions are in FC2, not the quantizer: K3 adds62.978µs of exposed FC2 completion extension, V3 adds31.456µs. These are disjoint completion extensions derived from CUPTI activity timelines; overlapping kernel durations are not summed. N3U EP/TP regressions primarily extend FC1. Static code expansion from separate forward/reverse epilogues remains a hypothesis rather than measured I-cache attribution.

Qualification: isolated374 arms each35 exact tests passed, composed22ffe8-case gate passed, and6 additional ReLU2/GeGLU/SiTU per-tensor/per-token cases passed with existing sm_count=2 to force both accumulator phases across multiple ordinary-scheduler work tiles. The latter uses existing oracle functions without changing production source. All executable/runtime register guards pass. No sanitizer was run.

Raw evidence archive:23,427,965B, SHA25694d873c335b350e4b3c91a5a62ef0639fca415f3b0edd8681be8d53daff844d8;367 files independently hash-verified. `evidence/{summary.json,cells.csv,table.md,results,supplement}` retains all positive/negative rows, full source manifests, samples, timelines, clock telemetry and gates. The rejected local review was removed only after verifying its patch and514-file manifest; the isolated remote source remains immutable evidence.

No K8 alternate-tactic diagnostic was launched. Next experiment isolates cyclic epilogue traversal on retained22ffe with the original overlap eligibility unchanged; see `../cyclic-epilogue-22ffe`.
