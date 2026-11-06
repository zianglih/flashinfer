## 📌 Description

@humansand

Persist the SM100-family CuTe DSL MoE kernels for both W4A4 and W4A16 through the shared on-disk kernel cache.

The existing launchers only memoize `cute.compile` results within one Python process, so fresh workers, serving restarts, and autotuning processes repeat the full MLIR compile. This change keeps those in-process dictionaries as L1 caches and adds the exported TVM-FFI object cache as L2:

- W4A4 gather/activation GEMM and finalize GEMM use separate disk modules.
- W4A16 grouped GEMM uses its own disk module.
- Runtime launches use raw pointer arguments plus one fixed-shape tensor for
  TVM-FFI device/stream discovery; the caller's current stream comes from the
  TVM-FFI environment.
- Cache keys now cover every codegen fact, including `max_active_clusters`, W4A4 pointer dtypes, and optional-pointer ABI state.
- Source hashing covers the launcher and every repository helper that contributes traced device code.
- The B12x cache-contract test is generalized to cover all six MoE cache adopters.

This is a fresh-process startup/JIT-stall improvement. The GPU kernels and steady-state launch configuration are otherwise unchanged.

## 🔍 Related Issues

- Follow-up to #4331
- Helps address #4317

## 🚀 Pull Request Checklist

### ✅ Pre-commit Checks

- [ ] I have installed `pre-commit` by running `pip install pre-commit` (or used your preferred method).
- [ ] I have installed the hooks with `pre-commit install`.
- [x] I have run the hooks manually with `pre-commit run --files ...` and fixed any reported issues.

## 🧪 Tests

- [x] Tests have been added or updated as needed.
- [ ] All GPU tests are passing.

Local checks completed:

- `python3 -m py_compile` on all changed Python files
- `ruff check`
- `ruff format --check`
- `pre-commit run --files ...`
- `git diff --check`

GPU validation environment:

- NVIDIA B200 (SM100)
- `flashinfer/flashinfer-ci-cu132:20260408-4cce866`
- CUDA 13.2, PyTorch `2.12.0.dev20260408+cu132`, CuTe DSL 4.6.0

The benchmark ran one fixed two-kernel specialization per mode in fresh Python
processes. Unrelated JIT dependencies were prewarmed once and excluded. Each
cache-disabled, cold-cache, and warm-cache arm was repeated twice; values below
are medians.

| Mode | Cache state | Direct build/load | Process wall | Compiles / loads |
|---|---:|---:|---:|---:|
| W4A4 | disabled | 3.080 s | 6.520 s | 2 / 0 |
| W4A4 | cold | 3.288 s | 6.723 s | 2 / 0 |
| W4A4 | warm | 0.0117 s | 3.414 s | 0 / 2 |
| W4A16 | disabled | 1.846 s | 5.290 s | 2 / 0 |
| W4A16 | cold | 1.968 s | 5.428 s | 2 / 0 |
| W4A16 | warm | 0.0117 s | 3.387 s | 0 / 2 |

Cold-to-warm direct build/load speedup was **281x for W4A4** and **168x for
W4A16**. End-to-end fresh-process speedup was 1.97x and 1.60x respectively.
W4A4 produced one 101,632-byte gather artifact and one 67,712-byte finalize
artifact (169,344 bytes total); W4A16 produced two artifacts totaling 155,144
bytes. Both warm repeats preserved artifact size/mtime exactly.

GPU checks completed:

- 12/12 measured numerical runs passed; every warm process had zero target
  compiles and two disk-cache loads.
- `tests/moe/test_cute_dsl_moe_kernel_cache.py`: 125 passed.
- W4A16 fused-finalize cold persist + fresh-process warm reload: passed; the
  warm process loaded both artifacts and compiled none.
- CUDA graph capture/replay on a non-default capture stream: W4A4 expanded
  finalize and W4A16 fused finalize both passed.

## Reviewer Notes

Please focus on the mixed Tensor/raw-pointer TVM-FFI ABI and the completeness of
the three SM100 cache keys. CuTe DSL 4.6 requires at least one GPU Tensor
argument to resolve the environment stream, so the fixed one-element
`num_non_exiting_tiles` operand remains a Tensor while dynamic data operands
remain raw pointers. The prior process-local W4A4 finalize key also omitted
pointer dtypes, and all three SM100 keys omitted the compile-time
`max_active_clusters`; the generalized naming-contract test now locks these
down.
