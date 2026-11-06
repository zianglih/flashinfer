# MMA channel interleave — rejected

The frozen candidate `3b0114ea…` is rejected against retained `b52e4e09…`. Native performance is close to neutral, while the source-bound MXFP4x8 stress case loses 1.425% with tight repeat agreement. The smaller MMA stack does not justify additional common-state loads across producers, gather, epilogue and polling paths. The source change is 110 additions / 107 deletions, mostly loop rearrangement; it offers no substantial reduction in implementation size.

## Qualification and method

- Actual-source AST proof preserves each accumulator’s K sequence, first-K initialization, K96 descriptor arithmetic, SF publication, operand release, barriers, staging and register quotas.
- Experimental numerical qualification passed 41 existing cases / 80 captures: 78 zero-local captures and two precisely source-bound inherited M512/N128/K8 spill signatures. The original no-new-local-site gate remains failed and preserved. No sanitizer was run.
- Native screen: 24 predeclared cells, 19 affected and five unchanged controls; seven decode and 17 prefill. Same physical GPU per C-A-A-C job, 10 warmups and 100 strict CUPTI samples per phase, cold-L2 CUDA graphs, frozen routes/tactics, normal compiler settings and caches. NVFP4 includes input quantization; all swap-AB finalization is unfused.
- All 9,600 native samples and 192 loaded-kernel guards passed; every native function had zero local bytes. Independent raw/source/route/tactic audit passed. Historical TRTLLM and non-swap baselines were not rerun.

## Native result

| Scope | Cells | E2E |
|---|---:|---:|
| All | 24 | +0.113% |
| Affected | 19 | +0.251% |
| Unchanged controls | 5 | −0.408% |
| Decode | 7 | −0.040% |
| Prefill | 17 | +0.177% |

Changed FC1 durations across 11 cells improve 0.549%; changed FC2 durations across nine cells regress 0.069%. FC1-only cells average +0.470% E2E and FC2-only cells −0.007%. Some FC1-only cells also have faster unchanged FC2, so these small differences do not establish a broad causal gain. FC durations overlap under PDL and cannot be added to reconstruct E2E.

All eight negative rows are retained. The largest loss is an unchanged one-channel control, N3U TP16K MXFP8 −2.106%, with control/candidate repeat spreads 1.142% / 3.249%. It remains in both the full and unchanged-control aggregates. Maximum native spreads are 5.499% / 3.249%; one 2ms NVML quartile window has no sample and is explicitly unavailable. No fixed-clock claim or clock-based exclusion is made.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|V3 EP8|16384|W4A4|523.507|523.026|522.898|523.187|+0.074%|0.061%|0.025%|
|N3U EP8|16384|W4A4|592.100|591.347|591.491|591.428|+0.058%|0.114%|0.024%|
|K3 EP8|4096|W4A4|381.058|380.019|380.354|380.786|+0.194%|0.071%|0.088%|
|K3 TP8|8|W4A4|78.049|78.048|78.144|77.809|-0.214%|0.308%|0.122%|
|V41F TP4|4096|W4A4|420.147|419.859|419.955|419.810|+0.017%|0.080%|0.023%|
|V3 TP8|8|W4A4|49.984|49.857|50.033|49.936|+0.030%|0.096%|0.353%|
|K3 EP8|16384|PER-TOKEN|1030.662|1030.149|1028.293|1030.549|+0.135%|0.011%|0.180%|
|N3U EP8|4096|PER-TOKEN|331.042|331.266|330.642|330.786|-0.012%|0.077%|0.189%|
|V41F EP4|16384|PER-TOKEN|772.548|766.195|767.923|767.957|+0.416%|0.598%|0.226%|
|V3 TP8|8|PER-TOKEN|56.288|56.224|56.257|56.416|+0.199%|0.227%|0.058%|
|K3 TP8|4096|PER-TOKEN|663.747|663.653|663.428|663.028|-0.023%|0.109%|0.034%|
|N3U TP8|8|PER-TOKEN|64.288|64.401|64.336|64.240|-0.162%|0.074%|0.100%|
|V3 EP8|16384|MXFP4x8|676.869|673.492|655.507|665.029|+0.976%|1.780%|2.744%|
|V41F EP4|16384|MXFP4x8|830.837|831.237|827.349|830.934|+0.192%|0.012%|0.470%|
|N3U EP8|8192|MXFP4x8|443.203|441.026|440.562|441.186|+0.317%|0.457%|0.105%|
|K3 TP8|8|MXFP4x8|80.192|80.353|80.433|80.256|-0.210%|0.080%|0.100%|
|V3 TP8|8|MXFP4x8|51.009|51.056|50.977|50.976|-0.048%|0.065%|0.156%|
|N3U TP8|4096|MXFP4x8|386.866|386.338|386.162|386.627|+0.128%|0.062%|0.046%|
|V3 EP8|4096|MXFP8|292.194|292.097|292.226|292.098|-0.005%|0.033%|0.044%|
|V3 EP8|16384|MXFP8|745.748|737.540|742.116|748.515|+0.988%|0.371%|0.621%|
|V41F EP4|16384|MXFP8|989.029|952.470|963.093|937.477|+0.537%|5.499%|1.115%|
|N3U EP8|8192|MXFP8|496.034|496.163|495.363|507.058|+1.160%|2.223%|0.161%|
|V3 TP8|8|MXFP8|71.072|70.849|70.960|70.912|+0.124%|0.226%|0.157%|
|N3U TP8|16384|MXFP8|1272.407|1328.247|1286.456|1286.935|-2.106%|1.142%|3.249%|

## Per-FC durations

|Job|Tokens|Format|E2E|FC1|FC2|
|---|---:|---|---:|---:|---:|
|ep-v3-w4a4-w4a4|16384|CuteDSL W4A4|+0.074%|+0.165%|+0.247%|
|ep-nemo3-ultra-w4a4-w4a4|16384|CuteDSL W4A4|+0.058%|+0.055%|-0.073%|
|ep-kimi-k3-w4a4-w4a4|4096|CuteDSL W4A4|+0.194%|+0.082%|+0.386%|
|tp-kimi-k3-w4a4-w4a4|8|CuteDSL W4A4|-0.214%|-0.079%|+0.195%|
|tp-v41-flash-w4a4-w4a4|4096|CuteDSL W4A4|+0.017%|+0.053%|+0.026%|
|tp-v3-w4a4-w4a4|8|CuteDSL W4A4|+0.030%|-0.115%|-0.140%|
|ep-kimi-k3-per-token-per-token|16384|CuteDSL PER-TOKEN|+0.135%|+0.401%|-0.110%|
|ep-nemo3-ultra-per-token-per-token|4096|CuteDSL PER-TOKEN|-0.012%|+0.065%|+0.421%|
|ep-v41-flash-per-token-per-token|16384|CuteDSL PER-TOKEN|+0.416%|+0.688%|+0.197%|
|tp-v3-per-token-per-token|8|CuteDSL PER-TOKEN|+0.199%|+0.089%|-0.141%|
|tp-kimi-k3-per-token-per-token|4096|CuteDSL PER-TOKEN|-0.023%|+0.025%|-0.246%|
|tp-nemo3-ultra-per-token-per-token|8|CuteDSL PER-TOKEN|-0.162%|-0.430%|-0.138%|
|ep-v3-mxfp-w4a8|16384|CuteDSL MXFP4x8|+0.976%|+0.941%|+1.314%|
|ep-v41-flash-mxfp-w4a8|16384|CuteDSL MXFP4x8|+0.192%|+0.379%|+0.526%|
|ep-nemo3-ultra-mxfp-w4a8|8192|CuteDSL MXFP4x8|+0.317%|+0.488%|+0.450%|
|tp-kimi-k3-mxfp-w4a8|8|CuteDSL MXFP4x8|-0.210%|+0.056%|-0.026%|
|tp-v3-mxfp-w4a8|8|CuteDSL MXFP4x8|-0.048%|-0.381%|-0.566%|
|tp-nemo3-ultra-mxfp-w4a8|4096|CuteDSL MXFP4x8|+0.128%|+0.245%|+0.089%|
|ep-v3-mxfp-mxfp8|4096|CuteDSL MXFP8|-0.005%|+0.024%|+0.131%|
|ep-v3-mxfp-mxfp8|16384|CuteDSL MXFP8|+0.988%|+0.987%|+4.258%|
|ep-v41-flash-mxfp-mxfp8|16384|CuteDSL MXFP8|+0.537%|+0.386%|+0.016%|
|ep-nemo3-ultra-mxfp-mxfp8|8192|CuteDSL MXFP8|+1.160%|+1.496%|+0.146%|
|tp-v3-mxfp-mxfp8|8|CuteDSL MXFP8|+0.124%|+0.000%|+0.022%|
|tp-nemo3-ultra-mxfp-mxfp8|16384|CuteDSL MXFP8|-2.106%|-2.487%|-2.699%|

## Separate synthetic stress diagnostic

These two cases are not included in the native aggregate. They exactly reproduce the existing M512/N128/K8, two-CTA, static-scheduler MX cases: 129 tokens, H=I=512, two experts, top-k two, SwiGLU, seed42 and the same dense routes. Input quantization and weight preparation are setup work, excluded from timing.

Fresh C-A-A-C yielded 800 strict CUPTI samples and 16 matched driver-resource guards. Input and output bytes matched across all phases. Observed quartile clocks were 2032MHz with reason mask0 and no missing windows; this is telemetry, not a fixed-clock regime.

|Synthetic format|C1 µs|A1 µs|A2 µs|C2 µs|E2E|FC1|FC2|C spread|A spread|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|w4a8|20.480|20.784|20.768|20.480|-1.425%|-2.699%|-2.228%|0.000%|0.077%|
|mxfp8|21.344|21.376|21.536|21.312|-0.596%|-1.791%|-0.597%|0.150%|0.749%|

The two inherited FC1 cases reduce stack128→48B, but increase static local-load sites16→38 and redistribute common values into other roles. In the exact captured H512/two-K-stage path, MMA-local traffic changes from124B loads +44B stores to40B loads +0 stores per lane. Across participating warps, the cluster fastpath changes from124B loads +44B stores to192B loads +0 stores, plus newly local slow-poll reads. These are static path counts, not measured memory transactions or an arbitrary-K model. The measured FC1 stress losses show that reducing MMA-local traffic alone is insufficient.

## Harness boundaries and preserved failures

The original compile-resource failure and compile-only continuation are immutable. Stress R0 stopped before its first owned MoE launch because normal `cute.compile` exposes `artifacts.CUBIN=None`. R1 preserved normal compilation and optional normal-loader IR extraction, then stopped before launch because it incorrectly equated driver static shared bytes0 with cuobjdump SHARED1024. The qualified PTX declares only extern dynamic shared; the device separately reports1024 reserved shared bytes. R2 requires driver static shared0 and exact source-derived dynamic storage, with unchanged register/local/geometry checks. All R2 phases are fresh; no failed phase is reused.

Normal cached executable bytes were unavailable for all16 stress functions and are explicitly unobserved. Diagnostic CUBIN hashes remain separate evidence, not claimed as runtime binary identity. Normal compiler options and caches were preserved throughout.

Evidence: `evidence/{cells.csv,summary.json,table.md}`, `components.json`, `coverage-analysis.json`, `raw-audit.json`, independent `peer-raw-audit.json`; `../mma-channel-interleave-stress-r2/{analysis.json,table.md}`; original and experimental qualification under `../mma-channel-interleave-b52`. Parent accepted rejection; no commit, push or composition.
