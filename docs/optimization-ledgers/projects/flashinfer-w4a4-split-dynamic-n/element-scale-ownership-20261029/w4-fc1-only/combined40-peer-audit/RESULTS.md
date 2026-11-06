# Thin W4 FC1-only: final 40-cell independent audit

**Evidence audit passed. The near-neutral result does not justify retaining the added producer/control structure.** All original and broader rows remain present; nothing is filtered by timing, clocks or sign.

| Scope | Cells | Speedup |
|---|---:|---:|
|Initial screen|16|+0.511%|
|Broader extension|24|-0.161%|
|Combined|40|+0.107%|
|Decode: 4/64|16|+0.365%|
|Middle: 512|8|+0.011%|
|Prefill: 4096/16384|16|-0.101%|
|EP|20|+0.365%|
|TP|20|-0.149%|

The metric is `100 × (sqrt(C1 × C2 / (A1 × A2)) − 1)`, each phase being the median of 100 strict-CUPTI samples. Group results are equal-cell geometric means. This campaign uses that geometric phase estimator, not the arithmetic phase-average estimator used by older W4 experiments.

| Model/topology | 4 | 64 | 512 | 4096 | 16384 |
|---|---:|---:|---:|---:|---:|
|V3 EP8|+2.925%|+0.297%|-0.015%|+0.167%|-2.071%|
|V41F EP4|-0.339%|+0.030%|+0.184%|+1.748%|+0.455%|
|K3 EP8|+1.512%|+0.042%|+0.035%|+6.335%|-1.547%|
|N3U EP8|+0.843%|+0.342%|-0.267%|+0.041%|-3.086%|
|V3 TP8|-0.332%|+0.371%|+0.127%|+0.032%|+0.057%|
|V41F TP4|-0.115%|-0.042%|-0.090%|-1.397%|+0.184%|
|K3 TP8|+0.258%|+0.248%|-0.082%|-2.983%|+0.359%|
|N3U TP8|-0.378%|+0.233%|+0.194%|+0.160%|+0.272%|

All 40 C1/A1/A2/C2 medians and both repeat spreads are in [table.md](table.md); [cells.csv](cells.csv) also contains GPU identity, evidence stage, component medians and clock summaries.

## Independent checks

- Replayed the new 9,600 samples and independently checked their union with the already-audited initial 6,400: 16,000 samples, 64 complete CAAC phases, 40 unique cells, all 14 negative cells preserved. Raw medians, CUPTI activity spans, same-GPU identity per job, frozen routes/tuner keys/runner/tactics, source hashes, cache bytes and no-autotune/no-event-fallback contracts all pass. The original eight smoke cases pass the existing exact oracle and remain one shared qualification set, not 16 distinct tests.
- Source maps match all 3,165 bound files per arm. Control is retained 658a; candidate W4 kernel is 1debc908. Only this W4 kernel differs. [final-source-validation.json](../final-source-validation.json) additionally verifies both checkouts at 658a, a clean control, exactly the frozen W4 file dirty in the candidate and no untracked files before retirement. No code or test source was changed by this audit.
- The 24 new recorded cache choices comprise 17 explicit tactics and 7 recorded −1 defaults. All 28 default measurements across four phases pass the actual `−1 → None → DEFAULT_W4A16_MOE_TACTIC` trace. Both FCs resolve to `((256,128,256),(2,1),True)` for those defaults; the trailing boolean is raster order, not CLC. Source AST/default proof and read-only cache preflight are hash-bound.
- All 192 new resolved FC stage records join by `compiled_library` to the loaded CUDA-driver resource record. Tiler, cluster, raster, PDL and CLC match; CLC is independently recomputed from the host geometry formula. There are 184 unique loaded functions because V41F TP reuses the same cached binaries at 64/512. This is legitimate callable reuse, not missing guards. Across both campaigns 312 functions report LOCAL=0 and pass independently recomputed pool/thread checks; the eight smokes add 16 guarded functions. Compiler options and the 80/64/144 policy are unchanged. This is driver-resource evidence, not a fresh SASS audit.
- The initial V41F TP 4/4096 pilot remains reused byte-for-byte and explicitly bound to its original triage config. All other initial/new campaign provenance stays separate. Source/settings equality between screen and broader is verified. Every combined-row phase value, GPU identity, clock list, provenance label, aggregate and negative count matches the independent inputs; the initial audit receipts were not rewritten.

## Clock and repeat limits

All 640 quartile windows have NVML samples. There are 82 quartile exceptions: 3 in the initial 4096 rows, plus 79 in the new 16384 rows. Every 16K model/topology cell has at least one non-2032 MHz median or nonzero event-reason window. Broader quartile medians range down to 1237 MHz; raw event reasons include 0 and 4. No clock settings were changed. These observations limit causal interpretation; they do not by themselves diagnose the cause of a ratio. [clock-exceptions.json](clock-exceptions.json) retains all exceptions and [phase-components-and-clocks.json](phase-components-and-clocks.json) retains all 640 windows.

Maximum within-arm spread is 5.343% control and 2.933% candidate. The N3U EP 16K −3.086% row has 5.343%/1.726% spread; V3 EP 16K −2.071% has 1.000%/2.933%. The initial K3 EP 4096 +6.335% and K3 TP 4096 −2.983% remain included with their earlier limitations. Two repeats are not statistical confidence intervals; no subset is substituted for the full result.

## Local reproduction

Run `python3 element-scale-ownership-20261029/audit_thin_w4_broader.py broader` followed by `python3 element-scale-ownership-20261029/audit_thin_w4_combined.py` from the project root. The first reads the candidate checkout to verify source and therefore requires the preserved snapshot if the rejected checkout is retired. The second is artifact-only. `summary.json` binds the independent input audits, combined report, source-validation receipt and replay script. No GPU, repository source or PR operation was performed.
