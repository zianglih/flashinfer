# Per-token paired-width CAAC screen

Recommendation: hold retention until the N3U TP decode regression is resolved or independently qualified. The broad prefill gains are useful, but the N3U TP32 slowdown is larger than either arm's repeat spread.

- **Source:** byte-equivalent retained `374ed4c07ee3a8c30a30026018a96d8f613ac4b5` versus seven host launch-policy lines in `nvfp4_quantize.py`. Candidate quantizer SHA `374e6f1ab34407d493c274c75f420d56bb3c4b00a2817c6f3fa0b26a1d261b40`; control `0d86930d3e74122009ba1f87c3c9c0068b989532a239050fc5817089238eafa3`. All514 guarded files are source-bound; MoE source, tactics, arithmetic and reductions are unchanged. This screen intentionally isolates the width policy, before later SF/iKET commits.
- **Policy:** pair two scale-factor blocks per lane only when narrower width does not increase padded block loads. Existing small-M branch, override, register cap and wide-row growth remain unchanged. Source-AST evaluation over4,096 K dimensions proves those invariants; see `policy-invariants.json`.
- **Qualification:**80 existing exact cases,64 direct cases,256 graph replays and4 routed-hole cases passed before deployment. Additional precise-error qualification is owned by the parent separately and is not asserted by this report. No sanitizer.
- **Timing:** all four models in EP/TP at32,4096,16384 tokens, per-token only.8jobs/24cells/32 complete C-A-A-C phases/9,600 strict CUPTI samples. One physical B300 per complete job, fixed374 native winners and immutable route/cache hashes, public unfused API, input quantizer included, cold-L2 graphs,10warmups/100samples. All runtime MoE guards passed; no instrumentation compile options. No clocks changed.

|Scope|Cells|Geometric speedup|
|---|---:|---:|
|All|24|+0.380%|
|Decode|8|−0.268%|
|Prefill|16|+0.705%|
|EP|12|+0.528%|
|TP|12|+0.232%|
|EP prefill|8|+0.771%|
|TP prefill|8|+0.640%|

Stable prefill gains include V41F EP4096+1.553%, V41F TP4096/16K+0.961/+0.943%, and N3U TP4096/16K+1.135/+2.037%. K3 EP4096+2.022% has a0.513% control repeat spread; K3 EP16K+0.830% has a0.869% control spread and variable clocks, so the latter is weaker evidence.

**N3U TP32:** −2.231%, with control/candidate spreads0.272/0.547% and sampled clocks2032MHz throughout. Intermediate quantization rises14.584→16.664µs, input quantization remains2.816→2.832µs, and FC1 remains52.953→52.992µs. The fixed tactic has route tile16 and512 experts: worst-case intermediate M is8384 while only704 routed values are live. Its K640 width changes64→32; the persistent grid cap doubles (`SMs * (1024 // threads)`), and inactive-row zero-SF work over40 columns changes from one pass to two. These are hypotheses for follow-up, not isolated causal proof. No shape-specific policy or source change has been introduced.

All24 rows, including six negative cells, remain below. One of384 NVML quartile windows is unavailable ([{'job': 'tp-nemo3-ultra-per-token', 'phase': '2-candidate', 'tokens': 16384, 'quartile': 3}]); it is not treated as fixed-clock coverage. Maximum control/candidate repeat spreads are0.869/0.547%. See `component-summary.json` and each job's full `analysis.json` for stage overlap and telemetry; component durations must not be summed because PDL overlaps kernels.

**External baseline boundary:** the shared input quantizer changes N3U H2048 at input M>4096. If retained, refresh TRTLLM PER-TOKEN EP8/TP8 at8192/16384 (four cells) before updating a current-versus-TRT comparison. Other model input widths and native TRT intermediate quantization are unchanged. `width-impact-proof.json` and `affected-historical-baselines.json` preserve the traced call chain and exact old raw artifacts. No external baseline was rerun here.

Archive SHA256 `6c47ddfe18a6683596fe324230ca5d151a29c6deebf6b2495633614251f539b2` (1,367files) was fetched in4MiB chunks and verified against remote SHA and every file's hash. The first truncated stdout transfer is preserved as failed/incomplete and never used for the final report. The metric is exactly `100*(sqrt(C1*C2/(A1*A2))-1)`.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|V3 EP8|32|PER-TOKEN|106.705|106.433|106.560|106.577|+0.135%|0.121%|0.119%|
|V3 EP8|4096|PER-TOKEN|244.801|243.553|243.553|244.401|+0.430%|0.164%|0.000%|
|V3 EP8|16384|PER-TOKEN|623.940|620.035|620.068|623.939|+0.627%|0.000%|0.005%|
|V41F EP4|32|PER-TOKEN|130.849|130.754|130.705|130.913|+0.116%|0.049%|0.037%|
|V41F EP4|4096|PER-TOKEN|399.091|393.267|393.027|399.411|+1.553%|0.080%|0.061%|
|V41F EP4|16384|PER-TOKEN|743.765|741.910|741.317|744.390|+0.332%|0.084%|0.080%|
|K3 EP8|32|PER-TOKEN|181.409|181.536|181.505|181.377|-0.071%|0.018%|0.017%|
|K3 EP8|4096|PER-TOKEN|451.506|441.458|441.394|449.202|+2.022%|0.513%|0.014%|
|K3 EP8|16384|PER-TOKEN|1025.700|1023.639|1019.701|1034.615|+0.830%|0.869%|0.386%|
|N3U EP8|32|PER-TOKEN|110.145|110.145|110.225|110.209|-0.007%|0.057%|0.072%|
|N3U EP8|4096|PER-TOKEN|326.067|325.268|325.380|325.316|+0.113%|0.231%|0.034%|
|N3U EP8|16384|PER-TOKEN|920.490|917.515|917.866|919.916|+0.274%|0.062%|0.038%|
|V3 TP8|32|PER-TOKEN|115.281|115.505|115.296|115.185|-0.145%|0.083%|0.181%|
|V3 TP8|4096|PER-TOKEN|464.595|464.690|464.771|464.644|-0.024%|0.010%|0.017%|
|V3 TP8|16384|PER-TOKEN|1354.425|1354.281|1353.592|1354.361|+0.034%|0.005%|0.051%|
|V41F TP4|32|PER-TOKEN|145.185|145.233|144.897|145.137|+0.066%|0.033%|0.232%|
|V41F TP4|4096|PER-TOKEN|536.165|530.741|531.363|536.149|+0.961%|0.003%|0.117%|
|V41F TP4|16384|PER-TOKEN|1268.283|1256.907|1256.443|1268.763|+0.943%|0.038%|0.037%|
|K3 TP8|32|PER-TOKEN|175.921|175.953|175.969|176.065|+0.018%|0.082%|0.009%|
|K3 TP8|4096|PER-TOKEN|656.740|657.092|657.091|656.965|-0.036%|0.034%|0.000%|
|K3 TP8|16384|PER-TOKEN|1918.523|1916.779|1916.908|1918.507|+0.087%|0.001%|0.007%|
|N3U TP8|32|PER-TOKEN|123.249|126.578|125.889|123.585|-2.231%|0.272%|0.547%|
|N3U TP8|4096|PER-TOKEN|553.350|547.062|546.886|553.014|+1.135%|0.061%|0.032%|
|N3U TP8|16384|PER-TOKEN|1764.085|1727.364|1728.228|1761.909|+2.037%|0.124%|0.050%|
