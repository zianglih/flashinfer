# Independent benchmark helper review

Approved the frozen helpers listed in `independent-helper-review.json`; no blocking issue found.

- `observed_measure` uses the captured `scheduler_policy`, fixing the earlier variadic-argument shadowing. All wrappers call their originals with unchanged arguments and return values. AUTO admission order and profiling are unchanged.
- NVFP4 calls the existing single-token routine once per desired format with `profile_backend` used only as its backend filter. `profile_cuda` remains false, so both arms use ordinary public timing; W4A16 is neither tuned nor measured. Inputs are reproducible because the unchanged `create_inputs` seeds 42; both native route tensors are also explicitly compared.
- The timing wrapper requires 100 samples, 10 warmups, cold L2, CUPTI and CUDA graphs, then preserves the returned samples and native median. Metadata serialization and route copies occur after each timed result. Scheduler observation adds no device operation and reads the actual compiled-cache key after production admission.
- Each source gets a fresh native winner cache, then frozen source-specific C/A/A/C replay. Cache hashes, source manifests, input-route hashes, quantization contracts, public results and per-row cache snapshots are cross-checked. Every timed winner hit is tied back to the saved native cache; requested flags are checked against those winners and effective flags against the production cache lookup.
- Analysis uses `sqrt(c0*c3)/sqrt(a1*a2)` from independently measured phase medians. `100*(ratio-1)` is positive for a speedup. AUTO samples are excluded; 1/2-token cells remain raw evidence but are excluded from retention aggregates. Expected scope is 156 cells and 62,400 CAAC samples across all three models and four formats.

This compares independently selected policy winners. It does not isolate a same-tactic kernel effect. Host AUTO telemetry is inclusive/exclusive API wall time, not isolated compiler CPU time. Effective FC1 CLC remains subject to existing launch eligibility and must not be inferred from its requested flag alone.
