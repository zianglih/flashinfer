# Independent benchmark observer audit

Read-only audit against pushed `d1767be1f42fdc371f90db4fb06598299ea32845`.
No source/helper edits or GPU actions. Audited helper hashes are recorded in
`observer-audit-hashes.json`. No blocking finding or stale-result substitution.

- Public path remains `CuteDslConfig.prepare_weights` and exported
  `cute_dsl_fused_moe` (benchmark lines 704–767, 809–843). The launcher passes
  `--functional-api --swap-ab --no-fused-finalize`; its two backend families
  select all five CuTe formats, including W4A16 (run_job.py:71–79). The optional
  observer-only single-format filtering flags are not enabled.
- Tactic admission wrappers call the original once and return the exact same
  list, without sorting/filtering/replacing candidates (observe_benchmark.py:
  105–145). Search instrumentation calls the original once and returns its result;
  added cache-key extras inspect configuration fields only. Nested compilation
  and profile timers add host spans without GPU synchronization, new device work,
  or tactic overrides. These wrappers were already present in the prior observer.
- MX graph policy is forwarded unchanged into both tune and replay contexts
  (benchmark:865–886, observer:148–161). NVFP4/per-token/W4A16 inherit native
  TuningConfig modes. Both modes use the same context-scoped managed cache
  (benchmark:197–207); AutoTuner applies policy before search in both tuning and
  replay (autotuner.py:2653–2674). W4A16 therefore retains its native profiling mode instead of being forced
  through the MX graph-policy override.
- The public timer requires graph replay, CUPTI, cold L2, 10 configured warmups
  and 100 samples. Event fallback is blocked both by warning escalation and
  wrapped fallback functions (observer:69, 206–238). `_measure_or_profile` must
  enter with tuning disabled; profiling inside it raises (observer:166–176,
  239–263). The SDK timer performs its normal extra graph preparation/estimation
  calls before the 10 configured warmups; this is unchanged standard behavior.
- Raw samples must all be positive finite values, exactly 100, and the native
  median must equal both the observed median and independently calculated
  `statistics.median` (run_job:94–105). The observer also checks native result
  ordering against all recorded measurement medians (observer:429–431).
- A new absent cache directory is required for tuning. Fresh process A1/A2 reuse
  it with no profiling, require every MoE cache lookup to hit, compare each
  key/runner/tactic with the tuned winner, and verify every cache-file hash is
  unchanged before/after (run_job:66–122). Existing result files are read only to
  obtain routing identities (run_job:61–62); no old latency or winner is imported.
- Routing hashes include IDs, FP32 weights, full expert histogram, shapes,
  dtypes and local-expert range, checked against prior identities at every token.
  The histogram observer wraps only the original untimed routing call and hashes
  after timed backend work (observer:333–423). V41F/K3/N3U share the same immutable
  route tensors. V3 independently recomputes routes with the same public router
  and seeded inputs, so its fingerprint is the untimed histogram's routes rather
  than a direct hot-path readback. This matches the earlier observer.
- Arm metadata is byte-identical to the prior helper. NVFP4 quantized-input arms
  time initial activation quantization; W4A16 consumes BF16. Per-token uses the
  explicit MSE/max256/fast-error recipe and activation fast-math setting. MX uses
  prequantized input. Scoped environment restoration is checked after every token.

## Qualifications

1. Generic v2 tuning legitimately races the default tactic `-1`, which may be
   published and later returned as a **cache hit**. Allowing that observed value
   does not permit a missing-cache fallback: misses still raise. Fresh winner
   changes are an intentional tuning-policy effect, so results are not a pure
   fixed-tactic kernel ablation against old measurements.
2. Observation is not completely allocation-neutral: it retains V3's histogram
   route tensors until the token finishes (at most 1 MiB at 16384×8 routes) and
   adds host bookkeeping outside measured graph replay. The prior observer has
   the same lifetime extension. No evidence requires rerunning or changing the
   ongoing campaign; avoid claiming a separate instrumentation-overhead ablation.
3. The recorder guards current benchmark calls and binds source hashes. It does
   not by itself validate the final report's A1/A2 aggregation or old external
   baseline mapping; the independent result/report checker must still do that.
