# PR7290 API cleanup, 2026-10-28

Current contract: see [contract-cleanup/README.md](contract-cleanup/README.md). The companion-cache design below is superseded.

Unstaged changes in the canonical `flashinfer/` checkout on retained `17bff619c`.

- Removed the wrapper-only `autotune_use_cuda_graph` option and its W4A16 rejection. Existing functional API arguments remain unchanged.
- MX graph benchmarks use the shared `MeasurementPolicy(execution_mode="cuda_graph")` through `autotune_v2`. Tuning and measured capture/replay use the same policy identity in separate scopes; timing has tuning disabled.
- NV and other existing benchmark paths retain their legacy JSON cache and eager/host-excluded autotuning behavior. With `--cache path`, CuTe DSL MX graph entries use the managed `path.v2/` companion directory. Existing MX JSON entries must be retuned; v2 also races the heuristic fallback. No old benchmark output was relabeled or refreshed.
- Removed the prepared-weight/layout matching assertion at the user's request, the now-unused `swap_ab` weight-view metadata, and the related type/doc changes. Matching prepared weights and execution mode remains the caller's responsibility.
- Kept `CuteDslConfig.swap_ab` as explicit immutable backend selection. The runner is selected and checked before weight packs arrive; surrounding backend configs also carry implementation-specific options. It is not an autotuning axis.

Validation: affected-file pre-commit (including mypy, Ruff), syntax, and diff checks passed. Both existing functional API definitions are AST-identical to the retained head. The local CPU probe exercises the real generic tuner/cache and extracted benchmark helper; 8 contracts passed, including legacy JSON replay, separate MX managed-cache publication/reload, memory-only replay, no-autotune behavior, and no policy leakage. GPU profiling/device metadata are mocked; no CUDA capture, GPU performance, or sanitizer run was performed. See `autotune-context-cpu.json` and `receipt.json`.

No staging, commits, pushes, or PR-body changes.
