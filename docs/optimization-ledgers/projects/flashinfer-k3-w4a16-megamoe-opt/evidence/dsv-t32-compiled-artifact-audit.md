# DSV T32 compiled-artifact audit

**No compiled-code causal explanation is established for DSV's ON/OFF difference.** Existing captures and caches do not supply an attributable pair of DSV T32 M128/N32/G1024/epi binaries, so register count, spill traffic, emitted instruction count and control-flow differences cannot be compared reliably. Older K3 exports are not evidence for this DSV specialization.

Inspection used read-only filesystem queries through the verified macOS-managed `/usr/local/bin/h` on the retained C2 devbox. It did not import CUDA, CuTe or Torch, compile code, launch GPU work, change environment/source, touch running processes, or alter samples. The experiment environment is preserved; any future cache strategy is separate.

## Durable receipt

`dsv-t32-existing-artifact-inspection.json` records the installed-source hashes and exact line-numbered excerpts, configured environment from the completed DSV ON capture, inspected paths/counts and timestamps. SHA256:

```text
12d88cc378580ea15d7a95691d5ec27b6a3437814b3191a211fb592339e5c235
```

Runtime is the captured **CuTe DSL4.7.1**, in `nvcr.io/nvidia/pytorch:26.05-py3` (CUDA13.2.1). Installed source base:

```text
/usr/local/lib/python3.12/dist-packages/nvidia_cutlass_dsl/dsl_packages/cutlass
```

## Why the configured CuTe file cache is empty

The current Mega frontend's `_compile()` calls `cute.compile(mega.kernel, **kwargs)` directly with the existing max-register compiler option; see `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py:335–359`.

Installed `cute/__init__.py:229–233` binds:

```python
compile = _dsl.CompileCallable()
```

Installed `base_dsl/compiler.py:1514–1515`, within `CompileCallable.__call__`, unconditionally sets:

```python
kwargs["compile_only"] = True
kwargs["no_cache"] = True
```

Installed `base_dsl/dsl.py:2227–2231` guards file-cache loading with `if not no_cache`; `dsl.py:2353–2366` likewise guards in-memory DSL insertion and file-cache write-through with `if not no_cache`. Its setup also forces `no_cache=True` for `compile_only` at `dsl.py:2862–2864`. Thus this explicit compile entry point bypasses the DSL file cache even though the environment requests caching. The frontend still keeps its compiled callables in its own in-process specialization dictionaries; this finding concerns cross-process CuTe file reuse, not the absence of all caching.

Installed `base_dsl/env_manager.py` reads `CUTE_DSL_NO_CACHE` with default False at605, `CUTE_DSL_CACHE_DIR` at615, and `CUTE_DSL_DISABLE_FILE_CACHING` with default False at685–687. The completed DSV ON capture records:

| Setting | Captured value / effect |
|---|---|
| `CUTE_DSL_NO_CACHE` | `0`; does not override the explicit `no_cache=True` keyword above |
| `CUTE_DSL_DISABLE_FILE_CACHING` | unset; runner explicitly removes this flag |
| `CUTE_DSL_CACHE_DIR` | persistent project `compile-cache/c2-sm103/cute-dsl` |
| `CUTE_DSL_DUMP_DIR` | project FlashInfer source root |
| `CUTE_DSL_KEEP` | unset; naming a dump directory alone does not request PTX/cubin retention |
| `FLASHINFER_CUTE_DSL_DISABLE_CACHE` | `0`; does not change this direct compile-call behavior |
| `CUDA_CACHE_DISABLE` | `0`; CUDA-driver caching is separate from CuTe file caching |

The inspected CuTe cache and `/tmp/root/cutlass_python_cache` both contain **zero entries**. This agrees with the installed source behavior; it is not evidence that the requested directory or cache flags were omitted from the harness.

## Attribution boundary

- The configured source dump root contains no PTX, cubin, SASS or MLIR artifacts.
- Existing explicit exports are K3 T512/T4096 baseline/native captures, not DSV T32 ON/OFF.
- The separate CUDA-driver cache has37 opaque files. Its latest modification was `2026-10-09T05:33:34.172838Z`, before DSV ON started at `2026-10-09T07:15:06.706507Z`. There is no exact DSV source/tactic-to-binary mapping in the captures. Bounded marker inspection found no identifiable MegaMoE/W4A16 labels; it is not a full decode of those files.
- Consequently no claim of more registers, spills, heavier division, or altered machine-level scheduling is supported. The source-derived single-group T32/G1024 bound remains valid, but it does not explain the measured difference by itself.

No further artifact search, benchmark, profile or cache change was performed. Preserve the ON/OFF AUTO results as measured policy evidence; compiled-code causality remains unresolved.

## Existing repository helper for a future cache integration

The local repository already documents this distinction in `CLAUDE.md:502–514`: direct `cute.compile()` has no persistent cache, while `flashinfer/jit/cute_dsl_core.py` provides `JitSpecCuteDsl` and `build_and_load_cute_dsl_kernel()` for explicit export/reload. The implementation reloads via `cute.runtime.load_module(..., enable_tvm_ffi=True)` at `cute_dsl_core.py:246` and exports via `export_to_c()` at254. The public wrapper begins at281 and includes source-based invalidation; `flashinfer/quantization/kernels/nvfp4_quantize.py` is the documented usage example.

That helper is a concrete starting point for a separate future MegaMoE cache integration. This optimization PR does not integrate it, change compilation behavior, or alter the running comparison environment.
