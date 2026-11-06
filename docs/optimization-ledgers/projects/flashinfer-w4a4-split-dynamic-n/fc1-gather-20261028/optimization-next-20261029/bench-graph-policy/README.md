# Benchmark graph-profiling policy candidate

Independent source `flashinfer-fc1-gather-bench-graph-review`, based on retained `c0c0bc41`. One unstaged benchmark-line edit removes the MX-only condition from the existing `MeasurementPolicy(execution_mode="cuda_graph")` selection. No kernel, tactic, public argument, production runner default, or generated-code change. `--no-cuda-graph` continues to inherit the existing eager native policy. Graph selection still uses CUDA events; final reported public timing uses strict CUPTI.

Current source history and `optimization-20261027/tuning-measurement-audit/README.md` show the MX gate preserved historical NV defaults, without a recorded NV graph-profiling correctness failure. The current generic managed policy applies directly to W4A16 TuningConfig as well. This experiment includes a W4A16 graph-AUTO smoke rather than assuming compatibility.

Replacement c3 devbox `fi-gather-opt-1029`, GPU7, B300, same explicit image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2 and CuTe DSL4.8.0. Immutable remote candidate preserves kernel SHA `3225acf2dfeba54df42481b3186267b1bde642da9887b98cb966d5383d8635af`; only benchmark source changes, SHA `a519cec442caba03fa262e160e55d620a66ff21655d792612a806e159cb3353c`. All 513 source hashes, helper hashes and both source patches are bound in `preparation.json` and remote `perf-config.json`. Existing nine persistent cache links remain intact.

- V3 EP8 W4A16, 8 tokens: one existing-tactic graph search and frozen replay. This is a capture smoke, not performance retention.
- K3 EP8 W4A4, 8192 tokens; K3 TP8 per-token, 16384 tokens: fresh managed graph-policy search, then old/eager/graph/graph/eager/old public replay on the same replacement GPU. Old and eager selections come from immutable completed campaigns; graph selection starts empty. All caches stay separate and policy-bound. No old-node latency enters this comparison.
- Native searches are limited via the existing public tuning-bucket override to each requested bucket. No tactics are removed, added, reordered or forced. Native profile return values are recorded after each unchanged call, with execution mode and timer, and never used to override the native winner.
- Final measurements use 10 warmups and 100 strict CUPTI cold-L2 CUDA-graph samples per median, NV input quantization included, unfused finalize, and matched routes. Search-pass public samples are diagnostic only.

The source is an active review copy, left unstaged. No commit, push, PR change or sanitizer is performed by this experiment. Original native84 outcomes remain unchanged and separate.
