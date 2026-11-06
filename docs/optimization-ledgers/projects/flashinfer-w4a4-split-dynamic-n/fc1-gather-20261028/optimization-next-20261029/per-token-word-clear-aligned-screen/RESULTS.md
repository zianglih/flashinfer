# Aligned word-clear R4: qualified, not retained pending padding cleanup

Seven fixed-winner CAAC cells /12 phases /2,800 strict-CUPTI samples compare retained22ffe with only the aligned SF word-clear change. Original width/grid policies remain unchanged. All source, frozen route/tactic/cache and runtime checks passed; raw evidence is in `evidence/`, with independently verified per-job archives and file manifests.

Overall geometric speedup is+0.122%; decode+0.328%, prefill−0.033%. N3U sparse decode avoids the rejected paired-width regression. Token32 control repeat spread1.023% makes its+0.446% inconclusive. V3 EP/TP16K regress−0.258/−0.153% with tight repeats, and input-quantizer medians increase by1.432µs each. This correlates with the measured32B stack /8LDL /4STL addition in initial-linear K7168 codegen; this screen does not independently prove the spill is the sole cause.

The mechanism is validated: actual routed-hole SASS emits8/16/32-bit zero stores according to gcd(4,SF columns), and both arms pass18 exact hole-layout cases with90 changed-routing graph replays. The7-cell production screen installs no codegen recorder. All observed clock quartiles are2032MHz with reason0; clocks were not changed. No sanitizer.

Keep R4 evidence frozen and assess the separate R5 geometry-based row-bound cleanup before retention. R4 changes initial-linear codegen even without holes; do not claim existing TRT per-token baselines source-equivalent from branch reachability alone.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U TP8|8|PER-TOKEN|63.904|63.825|63.760|63.921|+0.189%|0.027%|0.101%|
|N3U TP8|32|PER-TOKEN|123.553|123.745|123.520|124.818|+0.446%|1.023%|0.182%|
|N3U TP8|64|PER-TOKEN|147.473|146.769|146.961|147.282|+0.349%|0.130%|0.131%|
|N3U TP8|4096|PER-TOKEN|550.531|549.651|549.908|551.604|+0.234%|0.195%|0.047%|
|N3U TP8|16384|PER-TOKEN|1761.931|1760.203|1761.819|1761.676|+0.045%|0.015%|0.092%|
|V3 EP8|16384|PER-TOKEN|621.380|623.123|623.140|621.668|-0.258%|0.046%|0.003%|
|V3 TP8|16384|PER-TOKEN|1351.609|1353.000|1353.673|1350.936|-0.153%|0.050%|0.050%|

12 runtime guard receipts /48 loaded MoE kernels passed; this resource statement excludes quantizer kernels. Full component medians and clock evidence are preserved in `component-summary.json`.
