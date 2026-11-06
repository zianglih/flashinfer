# Terminal accumulator-tail removal

Retain for removing proven redundant synchronization and instruction work, with no speedup claim. Accept the small reproducible K3 TP decode loss: −0.516% originally and −0.310% in the separate repeat. The full screen is near neutral after accounting for noisy prefill cells.

The only production change deletes `acc_pipe.producer_tail(producer)` on base `b13963b0cc8409aeb92048b9ec7cf3be18f0a57c`. Timed kernel: `dca375bbf01d0fe5fb0c7b8c091e932f2189735c94d4d08b59fa82ea4c6999c1`. All operand drains, the final CTA-wide join, two-CTA TMEM deallocation rendezvous, PDL and W4 code remain unchanged. The actual CuTe 4.8 lifetime proof is in `../accumulator-tail-audit-b139/README.md`; qualification details and archives are in `../accumulator-tail-b139/QUALIFICATION.md`.

- Both arms passed 39 exact cases and four focused graph cases covering static/CLC × one/two CTA, with active → empty → partial → active → empty local routing. No repository test was added.
- All 76 matched executable captures passed before launch with no resource increase. Every kernel removes one terminal PTX barrier-wait site; MMA/TMA issue counts remain unchanged. In 74 kernels, static non-NOP counts fall by 2–22. Two wide MX kernels gain seven instructions from register-transfer scheduling without new local traffic. Two inherited synthetic M512/K8 spills shrink from 168 to 160 bytes, with LDL/STL site pairs falling from 21 to 20.
- Scoped precommit passed without changing the measured source. No sanitizer, retuning, clock changes or historical baseline rerun was performed.

## Original 24-cell screen

| Scope | Cells | Geometric speedup |
|---|---:|---:|
| All | 24 | +0.111% |
| Decode | 8 | −0.067% |
| Middle | 8 | −0.061% |
| Prefill | 8 | +0.461% |
| EP | 12 | +0.509% |
| TP | 12 | −0.286% |

All 24 cells, including 11 negative rows, remain below. The 20 cells with both repeat spreads below 1% average +0.001% as a diagnostic; no cells were removed from the primary aggregate. Apparent prefill gains are not isolated source-only evidence: V41F EP16K +3.846% has 2.245/7.673% control/candidate spreads; K3 EP16K and V3 EP16K also have wide control repeats.

Eight jobs / 32 complete C-A-A-C phases / 9,600 strict CUPTI samples preserve frozen native tactics, routes and caches, one physical GPU per complete job, 100 samples per phase, 10 warmups, cold-L2 CUDA graphs and NVFP4 input quantization. All 184 runtime-loaded MoE functions pass unchanged resource guards with zero local bytes; this does not claim all quantizers are spill-free. One of 384 NVML quartile windows lacks a sample. The seven observers are byte-identical to the retained benchmark engine; only descriptive text changes in the runner.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|8|W4A4|47.584|47.744|47.440|47.456|-0.150%|0.271%|0.641%|
|N3U EP8|512|W4A4|139.728|139.793|139.584|139.857|+0.075%|0.092%|0.149%|
|N3U EP8|16384|W4A4|583.090|583.346|582.962|583.731|+0.044%|0.110%|0.066%|
|V41F TP4|8|W4A4|51.808|52.112|51.904|51.984|-0.216%|0.341%|0.401%|
|V41F TP4|512|W4A4|323.107|323.618|323.635|323.362|-0.121%|0.079%|0.005%|
|V41F TP4|16384|W4A4|1042.584|1042.841|1043.704|1043.352|-0.029%|0.074%|0.083%|
|K3 EP8|8|PER-TOKEN|82.912|82.832|82.880|82.849|+0.029%|0.077%|0.058%|
|K3 EP8|512|PER-TOKEN|354.706|354.786|354.721|354.113|-0.097%|0.167%|0.018%|
|K3 EP8|16384|PER-TOKEN|1020.741|1015.460|1015.972|1035.733|+1.230%|1.469%|0.050%|
|N3U TP8|8|PER-TOKEN|64.129|64.113|63.984|64.064|+0.075%|0.100%|0.201%|
|N3U TP8|512|PER-TOKEN|179.970|180.162|180.161|179.810|-0.151%|0.089%|0.001%|
|N3U TP8|16384|PER-TOKEN|1785.871|1786.414|1786.046|1786.382|-0.006%|0.029%|0.021%|
|V3 EP8|8|MXFP8|88.416|88.512|88.448|88.496|-0.027%|0.090%|0.072%|
|V3 EP8|512|MXFP8|245.745|245.633|245.793|246.049|+0.075%|0.124%|0.065%|
|V3 EP8|16384|MXFP8|736.579|710.403|714.755|703.667|+1.033%|4.677%|0.613%|
|V3 TP8|8|MXFP8|70.960|70.944|70.656|70.912|+0.193%|0.068%|0.408%|
|V3 TP8|512|MXFP8|265.571|266.338|266.866|265.683|-0.366%|0.042%|0.198%|
|V3 TP8|16384|MXFP8|1355.675|1350.459|1337.579|1360.427|+1.045%|0.351%|0.963%|
|V41F EP4|8|MXFP4x8|49.824|49.760|49.824|49.840|+0.081%|0.033%|0.129%|
|V41F EP4|512|MXFP4x8|292.673|292.465|292.465|292.514|+0.044%|0.055%|0.000%|
|V41F EP4|16384|MXFP4x8|810.164|818.579|760.242|828.356|+3.846%|2.245%|7.673%|
|K3 TP8|8|MXFP4x8|80.193|80.609|80.624|80.208|-0.516%|0.019%|0.019%|
|K3 TP8|512|MXFP4x8|347.459|347.650|347.219|347.762|+0.051%|0.087%|0.124%|
|K3 TP8|16384|MXFP4x8|1616.877|1664.398|1652.124|1589.116|-3.336%|1.747%|0.743%|

## Separate confirmation run

The original rows are preserved; repeat values are not substituted into the primary screen. K3 TP8 MXFP4x8 repeats at −0.310% with 0.100/0.000% spreads, confirming a small decode cost. K3 TP16K changes from −3.336% to +0.100% with 0.252/1.029% spreads, so the original large loss did not reproduce. V3 TP512 MXFP8 changes from −0.366% to +0.334% with 0.280/0.400% spreads. K3 prefill still has substantial observed clock variation (1515–2032 MHz, reason flags 0/4); telemetry does not identify an isolated cause.

Both repeat jobs / eight complete C-A-A-C phases / 1,200 strict CUPTI samples use the same frozen source and methodology. All 24 loaded MoE functions pass unchanged guards with zero local bytes. All 48 repeat NVML quartile windows contain samples. GPUs 6/7 completed successfully and were verified idle after each campaign.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|K3 TP8|8|MXFP4x8|79.984|80.192|80.192|79.904|-0.310%|0.100%|0.000%|
|K3 TP8|16384|MXFP4x8|1631.238|1635.910|1619.255|1627.141|+0.100%|0.252%|1.029%|
|V3 TP8|512|MXFP8|268.643|268.659|267.587|269.394|+0.334%|0.280%|0.400%|

## Evidence

`raw-audit.json` and the repeat's corresponding file recompute every phase median, geometric ratio and spread from raw CUPTI arrays, and bind source/qualification/runtime receipts. `independent-harness-audit.json` proves timing-engine AST equivalence apart from descriptions; `independent-raw-audit.json` independently checks all original 24 rows and negative-cell preservation. All ten per-job archives and their file manifests are verified. `phase-analysis.json` in each campaign retains component medians and every telemetry quartile; PDL component durations overlap and must not be summed. The parent retained and pushed the exact measured source as `77391e28d12a01e371196e76e56d4b46ace122df`. All 514 source files match the commit; the completed review copy was retired with evidence preserved.
