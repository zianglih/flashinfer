# Composed retained-head refresh (prepared, not launched)

31 jobs,468 candidate cells, two fresh AA passes (93600 strict CUPTI samples):364 swap cells and104 W4A16 cells. Four models with existing EP/TP topology, all thirteen standard token counts. No retuning or baseline reruns. Existing23 swap-arm caches and8 final W4 `cache-native` caches supply winners; W4 old-baseline config cache is deliberately not used. Historical baselines are scoreboard-only; fresh AA is not a new paired comparison with them.

Before launch, freeze final source hashes/commit and pass27 existing integration tests (23 swap,4 W4 old/new layout/route tails). Diagnostic gate captures PTX/CUBIN with register guards; performance uses normal cached compilation and runtime CUDA attribute guards without diagnostic flags. Input quantizer follows existing benchmark contract. NVML2ms telemetry and strict100sample CUPTI enforce the previous methodology. Persistent C++/CuTe caches and whole flashinfer/data stable seed symlink remain in use.

Prepared source-free plan.json lists every frozen cache/result path. Root must provide final source and authorize launch. No source copy or GPU run was started by preparation.
