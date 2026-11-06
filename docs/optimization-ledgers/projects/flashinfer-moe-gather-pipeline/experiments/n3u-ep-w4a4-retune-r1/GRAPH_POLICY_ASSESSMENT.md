# Existing graph-profile policy boundary — read-only

Current native selection changed FC2 geometry but the public CUPTI holdout is neutral. This does not establish a misranking: individual event scores were not recorded, and the public and synthetic-route workloads differ.

The repository already exposes `MeasurementPolicy(execution_mode="cuda_graph")` through public `autotune_v2`. `bench_moe_deepseek.py:865–876` supplies it only for W4A8/MXFP8; W4A4 supplies None. `autotune_cache.py:127–234` derives real capture/replay and an identity-bearing manifest, while `autotuner/autotuner.py:1902–1949` applies it to the existing tuning configuration without changing its admitted tactics. Cold-L2 selection still uses CUDA events, not the final strict-CUPTI estimator.

A task-local existing-space diagnostic could pass that existing policy at the benchmark's two `_autotune_context` calls (tuning and replay) through its existing observer wrapper, keep a fresh separate managed cache and the existing one-bucket outer `autotune`, and passively record `_profile_single_kernel` return scores. No production edit, CLI/API knob, tactic axis, or private timer override is required. An outer nested `autotune_v2` is **not** valid: `autotune_cache.py:854–865` explicitly rejects nested v2 contexts. The current public `--use-cuda-graph` behavior alone does not opt W4A4 selection into that policy.

Such a search would isolate graph-versus-eager profiling, but retain the existing synthetic balanced routing and therefore would still need a separate public-route holdout. No graph-policy search has been launched or prepared. Given the neutral current holdout, the next evidence can instead be the already-held NCU profile of the original FC1 winner, at the parent's discretion.
