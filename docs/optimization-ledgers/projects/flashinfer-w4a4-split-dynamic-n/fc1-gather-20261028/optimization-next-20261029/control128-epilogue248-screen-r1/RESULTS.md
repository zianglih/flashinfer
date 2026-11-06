# Fixed FC1 control128 / gather128 / epilogue248 screen

The complete 20-cell source-paired screen is recorded below. This is one fixed register-budget redistribution on retained `ce4a7d8c`, with no new tactic axis or problem-dependent policy. Retention remains a parent decision; static instruction reductions do not establish an end-to-end gain.

## Source and qualification

- Control kernel `77a5495cca8dedef5bccfaacde64a1004b9a7c421175511f12ffef2d996439b3`; candidate `d7c17adfd8ebe86f733ffc724eced54354f9811a00523927852bb4efc10ec815`. Only two quota literals differ. Initial168 registers,384 threads and64,512 registers/CTA are unchanged. FC2 is unchanged.
- All84 paired codegen captures pass resource checks; all41 FC2 PTX/CUBIN pairs are byte-identical. The two inherited synthetic M512/N128/K8 MX FC1 cases shrink160→128 stack bytes and20+20→16+16 LDL/STL sites, with residual control/MMA spills retained. Their two BRA.U→BRA substitutions remain explicit. Eleven FC1 signatures lose static instructions,30 are equal, and two wide one-CTA NVFP4 signatures gain13; no new local sites.
- Candidate-only existing41 exact tests passed against the immutable qualified ce4 control bounds, with80 matched captures. No numeric control rerun or sanitizer. See `../control128-epilogue248-ce4/{COMPILE_RESULTS.md,exact-qualification.json,independent-codegen-audit.json}`.
- The approved20-cell plan covers four models, EP/TP and four affected formats, with6 CLC/14 static native choices. One predeclared row was changed before timing from N3U TP W4A4 T16K to T4096 to cover its actual one-CTA N256/K8 native geometry; original and corrected plan hashes are preserved. No retuning.

## Measurement boundary

- B300 on `fi-gather-6be-1029`, CUDA13.2 / CuTe4.8, stock clocks; exclusive GPU2 or3 per complete C–A–A–C job. Public benchmark API, cold-L2 CUDA Graph replay,10 warmups,100 strict CUPTI samples per phase; no event fallback, instrumentation compile options, or historical baseline rerun.
- Per-cell speedup is `100*(sqrt(C1*C2/(A1*A2))-1)` from the four phase medians. Geometric means aggregate cell ratios. This geometric per-arm estimator is deliberately distinct from the older W4 arithmetic-phase-mean screen.
- The initial campaign stopped at the candidate register-guard precondition before any owned candidate compile/launch. Its two completed control phases are preserved but excluded. R1 changes only the guard precondition to an explicit frozen-source-SHA policy map and the adapter expectation; every source/compiler/runtime check remains. Unknown hashes fail. The fresh complete C–A–A–C phases below are not stitched with R0.
- CUPTI FC1/FC2 spans are summarized from these same timed samples. Under PDL they overlap, so they must not be summed to reconstruct end-to-end latency. Clock/repeat variation is reported rather than used to discard rows.

## Full end-to-end results

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|8|W4A4|47.392|47.712|47.536|47.584|-0.285%|0.404%|0.370%|
|N3U EP8|16384|W4A4|592.771|594.115|593.748|592.659|-0.205%|0.019%|0.062%|
|V41F TP4|8|W4A4|52.032|52.129|51.968|52.001|-0.061%|0.061%|0.309%|
|V41F TP4|16384|W4A4|1042.535|1044.086|1043.398|1044.262|-0.033%|0.166%|0.066%|
|K3 EP8|8|PER-TOKEN|83.169|83.216|83.344|83.248|-0.086%|0.095%|0.154%|
|K3 EP8|16384|PER-TOKEN|1036.214|1030.133|1041.014|1061.910|+1.296%|2.480%|1.056%|
|N3U TP8|8|PER-TOKEN|64.273|64.368|64.336|64.368|-0.049%|0.149%|0.050%|
|N3U TP8|16384|PER-TOKEN|1804.923|1802.874|1804.060|1805.707|+0.102%|0.043%|0.066%|
|V3 EP8|8|MXFP8|89.008|89.153|89.073|88.929|-0.162%|0.089%|0.090%|
|V3 EP8|16384|MXFP8|756.404|752.227|748.340|777.348|+2.202%|2.769%|0.519%|
|V3 TP8|8|MXFP8|71.024|70.928|71.121|71.025|+0.000%|0.001%|0.271%|
|V3 TP8|16384|MXFP8|1359.352|1359.656|1355.096|1353.880|-0.056%|0.404%|0.337%|
|V41F EP4|8|MXFP4x8|49.745|49.728|49.904|49.873|-0.015%|0.257%|0.355%|
|V41F EP4|16384|MXFP4x8|828.229|841.669|829.542|824.676|-1.093%|0.431%|1.462%|
|K3 TP8|8|MXFP4x8|80.288|80.144|80.225|80.208|+0.079%|0.100%|0.100%|
|K3 TP8|16384|MXFP4x8|1649.578|1679.642|1677.754|1674.570|-0.993%|1.515%|0.113%|
|N3U EP8|8|MXFP8|69.888|70.096|70.049|70.112|-0.104%|0.321%|0.068%|
|N3U EP8|16384|MXFP8|904.885|887.413|893.590|885.528|+0.523%|2.186%|0.696%|
|N3U TP8|8|W4A4|59.409|59.296|59.361|59.377|+0.108%|0.053%|0.108%|
|N3U TP8|4096|W4A4|379.283|378.514|378.627|379.474|+0.213%|0.050%|0.030%|

|Group|Cells|Geometric speedup|
|---|---:|---:|
|all/all|20|+0.0669%|
|all/decode|10|-0.0575%|
|all/prefill|10|+0.1914%|
|ep/all|10|+0.2033%|
|ep/decode|5|-0.1305%|
|ep/prefill|5|+0.5383%|
|tp/all|10|-0.0694%|
|tp/decode|5|+0.0154%|
|tp/prefill|5|-0.1542%|

|Format|Geometric speedup|
|---|---:|
|CuteDSL MXFP4x8|-0.5071%|
|CuteDSL MXFP8|+0.3972%|
|CuteDSL PER-TOKEN|+0.3145%|
|CuteDSL W4A4|-0.0439%|

All20 cells /8,000 strict CUPTI samples and160 loaded kernels passed source/runtime checks; each timed kernel has zero local bytes. All12 negative cells remain. Maximum control/candidate repeat spread is2.769%/1.462%; 0 clock quartile windows are unavailable.

## Per-FC observations

|Job|Tokens|Format|E2E|FC1|FC2|
|---|---:|---|---:|---:|---:|
|ep-nemo3-ultra-w4a4|8|CuteDSL W4A4|-0.285%|-0.098%|-0.818%|
|ep-nemo3-ultra-w4a4|16384|CuteDSL W4A4|-0.205%|-0.336%|-0.386%|
|tp-v41-flash-w4a4|8|CuteDSL W4A4|-0.061%|-0.098%|-0.195%|
|tp-v41-flash-w4a4|16384|CuteDSL W4A4|-0.033%|+0.019%|-0.137%|
|ep-kimi-k3-per-token|8|CuteDSL PER-TOKEN|-0.086%|+0.225%|-0.219%|
|ep-kimi-k3-per-token|16384|CuteDSL PER-TOKEN|+1.296%|+1.408%|+0.672%|
|tp-nemo3-ultra-per-token|8|CuteDSL PER-TOKEN|-0.049%|+0.029%|-0.102%|
|tp-nemo3-ultra-per-token|16384|CuteDSL PER-TOKEN|+0.102%|+0.066%|+0.194%|
|ep-v3-mxfp|8|CuteDSL MXFP8|-0.162%|-0.174%|+0.020%|
|ep-v3-mxfp|16384|CuteDSL MXFP8|+2.202%|+0.957%|+1.820%|
|tp-v3-mxfp|8|CuteDSL MXFP8|+0.000%|-0.124%|+0.341%|
|tp-v3-mxfp|16384|CuteDSL MXFP8|-0.056%|-0.182%|-0.394%|
|ep-v41-flash-mxfp|8|CuteDSL MXFP4x8|-0.015%|-0.138%|+0.186%|
|ep-v41-flash-mxfp|16384|CuteDSL MXFP4x8|-1.093%|-0.952%|-2.188%|
|tp-kimi-k3-mxfp|8|CuteDSL MXFP4x8|+0.079%|+0.036%|-0.224%|
|tp-kimi-k3-mxfp|16384|CuteDSL MXFP4x8|-0.993%|-0.118%|-2.046%|
|ep-nemo3-ultra-mxfp|8|CuteDSL MXFP8|-0.104%|+0.510%|-0.201%|
|ep-nemo3-ultra-mxfp|16384|CuteDSL MXFP8|+0.523%|+1.219%|-0.298%|
|tp-nemo3-ultra-w4a4|8|CuteDSL W4A4|+0.108%|+0.000%|+0.112%|
|tp-nemo3-ultra-w4a4|4096|CuteDSL W4A4|+0.213%|+0.822%|+0.211%|

## Replayable evidence

- `evidence/results/*/` contains all four phase outputs, runtime receipts, timestamps, clocks, frozen cache/route receipts and hash manifests. `fetch-receipts/` binds each verified archive. `evidence/{cells.csv,summary.json}` and `components.{csv,json}` retain every cell and spread.
- `audit_raw.py` independently checks all source/hash/route/tactic/runtime/median ratios; `aggregate.py` and `components.py` regenerate the tables. `method-equivalence.json` and `independent-guard-mapping-audit.json` bind the harness-only R1 correction.
