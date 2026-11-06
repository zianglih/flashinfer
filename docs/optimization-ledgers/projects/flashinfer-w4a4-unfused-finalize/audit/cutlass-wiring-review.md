# CUTLASS benchmark finalize flag wiring review

Scope: add the previously used CUTLASS benchmark switch fix to PR #5319. Source changes are owned by the parent agent; this review made no repository edits.

## Recovered fix

The earlier minimal patch is `/Users/ziangli/playground/projects/sglang-flashinfer-unfused-finalize-default/benchmarks/cutlass/enable_cutlass_finalize_flag.patch`. It contains exactly three additions in `benchmarks/bench_moe_deepseek.py`:

1. Add `use_fused_finalize=True` to `bench_cutlass`.
2. Pass `use_fused_finalize=use_fused_finalize` from `_benchmark_single` into `bench_cutlass`.
3. Pass it from `bench_cutlass`'s `run` closure into `cutlass_fused_moe`.

The longer historical `benchmark_extensions.patch` also introduces a `cutedsl-w4a4` selector. That is unrelated to this request and should not be copied as part of the flag fix.

The current `main → run_benchmark → _benchmark_single` chain already carries the flag. The single nested `run` is used for autotune prewarm, timing, and CUDA profiling, so the final API keyword covers all three paths. True remains the default and therefore preserves existing benchmark behavior when the CLI switch is omitted. CUTLASS continues to be omitted when per-token activation scaling is selected.

## API semantics

`cutlass_fused_moe(..., use_fused_finalize=True)` **permits** eligible fused-finalize GEMM2 tactics; it does not force autotuning to choose one. `False` disables that family and uses the deterministic non-fused reduction.

Evidence in the current source:

- `flashinfer/fused_moe/core.py:1294,1562`: public default and dispatch forwarding.
- `core.py:739–764`: runner flag and instance key include the value; the flag is passed to native initialization.
- `core.py:798`: persisted autotune key extras include the value. No cache fix is necessary.
- `csrc/fused_moe/cutlass_backend/flashinfer_cutlass_fused_moe_binding.cu:291–301`: set the flag before enumerating GEMM2 tactics and sizing workspaces.
- `csrc/fused_moe/cutlass_backend/cutlass_fused_moe_kernels.cuh:4576–4584`: actual fused execution requires the runner flag **and** a selected `FINALIZE` tactic, together with backend eligibility. The consistency check rejects a fused tactic on a disabled runner.

Do not describe CUTLASS True as proof that a fused kernel ran. Historical speedup measurements compare the API setting, with autotuning allowed to choose compatible tactics.

## Minimal documentation/status changes

- Update `--no-fused-finalize` help to name both CuTe DSL and CUTLASS. Keep TRTLLM explicitly unaffected.
- Keep CuTe DSL's existing status description; add a separate CUTLASS line in both `main` and `_print_header`, using wording such as `fused finalize permitted (tactic dependent)` for True and `deterministic non-fused` for False.
- Update the top usage example/comment and shared `run_benchmark` parameter documentation to avoid implying that CUTLASS True forces atomic fusion.
- Add a short `bench_cutlass` argument description documenting eligibility/tactic dependence.
- No native C++, kernel, backend-selection, quantization, or timing changes are needed.

## Appropriate validation

- Compile the edited Python file and run the repository's changed-file lint hooks.
- Use a local isolated stub/AST harness to exercise both True and False through `_benchmark_single → bench_cutlass → cutlass_fused_moe`. Check that the value reaches the API during both autotune prewarm and the measured/profiled closure; verify the omitted argument still forwards True.
- Check parser default True and `--no-fused-finalize` False, plus both status outputs and help text.
- No new GPU benchmarks or C++ builds are needed for these three keyword-forwarding changes. The earlier EP8 CUTLASS measurements used the same minimal wiring patch and remain historical evidence; do not relabel them as fresh final-head runs.
- No upstream tests need be added; retain local verification artifacts in the effort folder.
