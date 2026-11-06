# Held graph-policy existing-space diagnostic

This task-local harness uses the existing public `MeasurementPolicy(execution_mode="cuda_graph")` at the benchmark's current `_autotune_context` boundary for both tuning and replay. Production source remains exact retained2b8. There is no kernel patch, new public/private tuning knob, tactic axis, synthetic input change, or nested v2 context.

Scope is N3U EP8 / TP1,16384tokens, unfused functional swap-AB W4A4, inputquant included. The original outer `autotune(tune_mode=False,tuning_buckets=(16384,))` limits native search to one bucket and320 currently admitted tactics plus the existing default race. Persistent C++/CuTe caches are reused; winner storage is a fresh `results/cache-native` directory whose manifest must contain `measure_execution_mode=cuda_graph`. Original/default caches are never rewritten.

Only `observe_benchmark.py` differs from the previous search's12 standard helpers. The change sets the public policy at both existing contexts and passively records each returned native profile score, tactic and effective configuration **after** the original profiler returns. Arguments, returns, ordering, candidate admission and device work are untouched. Eleven helpers and the single-bucket wrapper remain byte-identical. `check.py` verifies positional/keyword forwarding and return identity without importing FlashInfer or touching a GPU.

Native selection uses existing coldL2 CUDA-event timing around graph replay on the current synthetic balanced profile inputs. The final public100samples use unchanged strict CUPTI/coldL2/graph timing and the saved real sigmoid route identity. The two domains remain distinct; a selected geometry or score is not a retained performance claim. Any winning candidate would need a separate same-source public-route holdout.

The controller retains the current source/runtime/cache/idle/resource pre/post checks and adds effective-policy/score/cache-manifest assertions. Current native cohort/readiness and all13,245 source hashes are bound. Capture-unsafe candidates follow the native profiler's existing behavior; the resource guard is unchanged and LOCAL0 remains required.

**Held:** no deployment or GPU execution has happened. `deploy_launch.py` requires the explicit task-local approval environment flag; do not set it until the parent clears the active NCU timing overlap. GPU0 is only the planned lane, not an active reservation. Current setup/compiler signatures do not imply successful graph capture.

Completed after explicit parent authorization and NCU metrics release. See `RESULTS.md`, `summary.json`, and `launch-authorization.json`; the earlier held setup is preserved as preparation history. No retained improvement or production change resulted.
