# Cyclic epilogue: completed paired screen

**Recommendation: retain**, with the N3U TP per-token regression explicit. This is the cyclic-only replacement with retained overlap eligibility, not the rejected wider protected-span policy.

- Ten affected prefill cells: **+1.525%** geometric speedup; two unaffected controls: **+0.013%**; all twelve: **+1.271%**. These are screening aggregates, not a full-workload aggregate.
- Strongest stable gains: K3 EP W4A4 **+7.379%**, N3U EP W4A4 **+2.182%**, V41F EP W4A4 **+0.967%**. K3 TP MXFP4x8 improves **+5.766%** with higher0.870%/1.471% C/A repeat spreads.
- **N3U TP PER-TOKEN regresses1.831%**, stable across0.074%/0.026% C/A spreads. The mean disjoint critical path grows7.8us in FC1 and25.0us in FC2; intermediate quantization is approximately unchanged. These extensions include pipeline waits and do not by themselves identify the instruction bottleneck.
- V3 TP MXFP8−0.209% is inconclusive: control/candidate repeat spreads2.684%/1.447%, with clock-event reason4 observed. Other phase clock medians are2032MHz; clocks were unchanged. All192 cell-phase quartile windows have telemetry.
- The candidate removes1,421–4,065 static non-NOP instructions and13–34 static branch sites from26 affected compiled kernels.38 unaffected kernels are byte-identical. No new spill sites; existing two MX M512/K8 stack168B cases remain. This establishes static code-size reduction, not a measured dynamic-instruction reduction.

## Evidence and contracts

Control: exact retained22ffe source, byte-identical swap kernel to current6c (22ffe→6c changes W4A16 only). Candidate: `e252156b43d359f89121f611a341aa200f6bf07ea721a6f93c022f82a1b16101`, one unstaged kernel file in `flashinfer-swap-ab-cyclic-epilogue-review`,37 additions/147 deletions. Its patch applies cleanly to canonical6c. All33 other methods, overlap policy, tactics, PDL, scheduler and stage counts are unchanged.

33/33 exact cases per arm passed;128 diagnostic prelaunch CUBIN resource guards passed. CPU ownership proofs cover16,710 TMEM phase/valid-row cases plus1,028 shared-store-ring cases. Scoped precommit/mypy/ruff passed; sanitizer deferred. Files are bound by sibling `cyclic-epilogue-22ffe/r3/{local-source.json,ast-proof.json,lifetime-proof.json,shared-output-ring-proof.json,codegen-comparison.json,precommit.json}`.

Ten jobs /40 phases /12 cells /4,800 strict CUPTI samples. Each job uses the same physical GPU for C-A-A-C,10 warmups,100 samples per phase,cold-L2 CUDA graphs,public API and included NVFP4 input quantization. Existing native winners and routes are frozen; no AUTO/new tactics or clock setting changes. Persistent native and CuTe caches are retained. All96 actual loaded-kernel resource checks, source/cache/route/tactic/timer guards passed.

The first launch used an invalid backend selector and exited before timing; `failed-selector/` preserves it. The retry changes only that selector to the script's existing `cutedsl` plus `--w4a4-only`. Candidate/control source and timing helpers are unchanged. Raw archiveSHA256 `9c33c0eb3ec9996a921749f0c7f84f33060b0d6bfd1b95846b759b9e70b2d45b`,302 extracted files hash-verified.

## All raw phase medians

Positive: `100*(sqrt(C1*C2)/sqrt(A1*A2)-1)`. Times in microseconds; C/A spread is max/min−1 of the two respective phase medians.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|32|W4A4|103.489|103.457|103.393|103.520|+0.077%|0.030%|0.061%|
|N3U EP8|16384|W4A4|595.734|583.381|582.726|595.813|+2.182%|0.013%|0.112%|
|K3 EP8|8192|W4A4|514.979|479.443|478.963|514.147|+7.379%|0.162%|0.100%|
|V3 EP8|16384|W4A4|516.469|516.454|516.964|516.086|-0.083%|0.074%|0.099%|
|V41F EP4|8192|W4A4|413.635|409.826|409.586|413.699|+0.967%|0.015%|0.059%|
|N3U TP8|16384|W4A4|1213.659|1207.163|1206.603|1214.219|+0.585%|0.046%|0.046%|
|N3U TP8|16384|PER-TOKEN|1763.099|1795.083|1795.547|1761.787|-1.831%|0.074%|0.026%|
|K3 TP8|8192|MXFP4x8|912.696|873.032|860.376|920.632|+5.766%|0.870%|1.471%|
|V41F TP4|16384|W4A4|1047.414|1046.039|1046.439|1047.830|+0.132%|0.040%|0.038%|
|V3 TP8|512|MXFP8|269.698|270.050|270.050|270.130|-0.050%|0.160%|0.000%|
|V3 TP8|16384|MXFP8|1341.741|1317.371|1336.428|1306.665|-0.209%|2.684%|1.447%|
|V3 TP8|8192|MXFP4x8|687.716|682.612|682.724|687.395|+0.716%|0.047%|0.016%|

## Next work, not part of this candidate

Any future wider protected interval must maintain the shared TMA store ring independently of skipped/SIMT output slabs. A naive larger cyclic prefix can reuse a pending shared stage. Preserve the original wider-policy negative results; any repeat must be a new co-design comparison against retained cyclic traversal, with an explicit ring-lifetime proof. No wider-policy variant was launched during this screen.
