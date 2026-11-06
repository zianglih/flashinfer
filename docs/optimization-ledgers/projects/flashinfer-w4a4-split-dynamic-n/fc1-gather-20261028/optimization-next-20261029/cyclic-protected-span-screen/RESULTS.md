# Wider cyclic accumulator interval: reject as-is

The complete11-cell fixed-winner screen is **-1.222%** geometric-mean speedup versus retained e780; nine prefill cells are **-1.481%**. N3U FC1 gains do not justify stable TP FC2 regressions. No candidate source was committed or pushed.

Both arms use the same physical GPU per complete C-A-A-C, frozen current winners/routes, public API, input quantizer where applicable, cold-L2 CUDA graphs,10 warmups and100 strict CUPTI samples per phase. All10jobs/40phases/4,400samples completed. All88 runtime kernel guards passed. All176 cell-phase quartiles contain NVML observations; stock clocks unchanged. Maximum phase repeat spreads: control0.232%, candidate0.273%. Small sub-spread controls are inconclusive.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|32|W4A4|103.361|103.425|103.377|103.489|+0.023%|0.124%|0.046%|
|N3U EP8|4096|W4A4|231.746|222.082|222.210|231.522|+4.271%|0.097%|0.058%|
|N3U TP8|4096|W4A4|387.123|384.932|384.707|387.507|+0.649%|0.099%|0.058%|
|K3 TP8|8192|W4A4|786.359|803.336|804.024|786.312|-2.158%|0.006%|0.086%|
|K3 TP8|8192|PER-TOKEN|1029.305|1123.945|1123.610|1029.529|-8.397%|0.022%|0.030%|
|V3 TP8|8192|PER-TOKEN|772.903|812.984|813.463|772.839|-4.962%|0.008%|0.059%|
|V41F TP4|16384|PER-TOKEN|1268.283|1290.108|1290.506|1268.058|-1.716%|0.018%|0.031%|
|V3 TP8|512|MXFP8|269.010|270.018|269.282|269.635|-0.121%|0.232%|0.273%|
|N3U TP8|16384|PER-TOKEN|1795.695|1796.223|1796.399|1794.685|-0.062%|0.056%|0.010%|
|K3 EP8|8192|W4A4|475.684|475.555|475.443|475.604|+0.030%|0.017%|0.024%|
|V3 TP8|8192|MXFP4x8|681.764|684.485|684.693|681.190|-0.455%|0.084%|0.030%|

## Qualification and source

Base e780f02cc1f8a7e59f22b8bda6f7acd8f8792b24; candidate kernel09a615dbc4374e3a9ebe653e69a07c297698bc3fc7a27ae0d85ff4b27a1eb14b. Source proof, exact patch, design, independent ring audit, and scoped precommit are in sibling `cyclic-protected-span-e780/`. Both33-case exact gates passed;128 diagnostic prelaunch CUBIN guards passed.32/64 compiled kernels are byte-identical. No new local spill cases; the existing MX local-stack cases remain. New FC1 overlap adds1,642–3,597 static instructions versus the former non-overlap path; FC2 deltas are−30…+101. No additional static bulk-commit sites. Static counts are not dynamic instruction measurements. Sanitizer intentionally skipped.

## What the timelines show

K3 TP8K per-token loses94.14us of exposed FC2 extension, while FC1 changes−0.13us and the intermediate quantizer+0.11us. K3 TP W4A4 loses17.61us in FC2. N3U EP4K wins9.43us in FC1; N3U TP4K wins5.24us in FC1 but loses2.46us in FC2. N3U TP16K per-token is neutral within repeats: the previously retained cyclic regression is not fixed here.

The next mechanism to test is decoupling TMEM read order from output store order. With a128-column protected interval and128–191 live rows, phase0 handles the SIMT tail before full TMA groups, leaving a terminal TMA drain without tail work to hide it. This is a source-grounded hypothesis, not a measured causal attribution. The actual-issued-store ordinal alone does not fix that case: no full-store hole occurs. Prefix caching can preserve early TMEM release while restoring monotonic full-TMA-then-SIMT stores. It must preserve the native/full versus row-owned/partial register layouts without an extra transpose.

Raw/derived source-bound artifacts are in `evidence/`. `components.json` uses disjoint completion-frontier extensions, not a sum of overlapping kernel durations. All negative cells remain included. The earlier duplicated-body wider-span rejection remains a separate historical experiment.
