# CuTe DSL cache audit for the activation experiment

**Conclusion:** the reused persistent `CUTE_DSL_CACHE_DIR` cannot cause these fresh-process W4A16 MegaMoE arms to reuse the baseline's stale CuTe binary after an imported epilogue helper changes. This path calls `cute.compile`, which unconditionally disables both CuTe's module cache reads and writes in the installed DSL 4.7.1.

This was checked using source inspection only. No GPU launch, compilation, source modification, cache deletion, or setup change was performed. Managed HAI resolved to `/usr/local/bin/h`; live C2 reads ran from the earlier blog HAI checkout.

## Decisive call chain

1. `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py::_compile`, around lines 338–357, directly returns `cute.compile(mega.kernel, **kwargs)`. It does not call FlashInfer's separate `JitSpecCuteDsl` disk-object cache.
2. Installed `cutlass/base_dsl/compiler.py::CompileCallable._compile`, lines 1514–1515, sets:

   ```python
   kwargs["compile_only"] = True
   kwargs["no_cache"] = True
   ```

3. `cutlass/base_dsl/dsl.py::_prepare_compilation`, around lines 2845–2863, consumes that `no_cache` argument and preserves it. Even a compile-only request without that argument would force it to true.
4. In `generate_original_ir`, line 2119, `module_hash` becomes `None` when `no_cache` is true.
5. In compilation, lines 2227–2238, `load_cache_from_path(...)` is guarded by `if not no_cache`; the in-memory JIT cache is also bypassed and the compile branch is taken.
6. Lines 2353–2362 guard both cache insertion and `dump_cache_to_path(...)` with the same `if not no_cache` condition.

Thus `CUTE_DSL_NO_CACHE=0`, `CUTE_DSL_DISABLE_FILE_CACHING` being unset, or a shared persistent cache directory do not override the explicit `no_cache=True` on this call. No epilogue source-dependency fingerprint is needed to invalidate a disk binary on this direct compile path: no disk binary is read.

## What happens on the ordinary cached DSL path

For completeness, the separate cache-enabled path hashes the **traced original IR module**, environment settings, and compile options. `get_module_hash` at `dsl.py:1862–1879` serializes MLIR bytecode and hashes it; `generate_original_ir` builds the module and runs trace-finalization hooks before calling this function. It is not merely a hash of the top-level Python filename, so an imported helper change that changes traced IR would change the ordinary module key too. This fallback observation is not needed for the direct-compile conclusion above.

## Fresh-process requirement

The W4A16 frontend has process-local `_staging_variants` and `_unstaged_variants` dictionaries. They intentionally retain compiled callables within a process and are not keyed by helper source hashes. Editing Python files after an object has already compiled in a live worker would not replace that callable automatically. The experiment's separate `torchrun` processes per arm avoid this issue. Reusing C++ helper builds and persistent cache directories is compatible with that separation.

Exporting matched baseline/native PTX and CUBIN is still useful to verify the expected `tanh.approx.f32`/`MUFU.TANH` replacement, arithmetic packing, register resources, and spills. A flat timing result should not be attributed to CuTe disk-cache invalidation based on these sources.

## Live source identity

Live C2 reports `nvidia-cutlass-dsl==4.7.1`. Installed files are under:

```text
/usr/local/lib/python3.12/dist-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/
```

Their hashes exactly match the already archived files in `nvfp4-w4a16-blog-draft/evidence/glm5-mma-instruction-audit/`:

| Installed file | SHA256 |
|---|---|
| `base_dsl/compiler.py` | `91f5428a98e8cf8e5b9a6c665fab9690373124f0d67449aa00e537ec70f52f56` |
| `base_dsl/dsl.py` | `3f48d11009b190b54904742c103d58f972b6925fac68b645fcc65faddb8212b0` |
| `base_dsl/env_manager.py` | `8597e5d158865b4dd6fb0ed73f12564a0d12af9bcac8353f622345e7467dffa1` |
| `base_dsl/cache_helpers.py` | `b0e156e7cba6d21f77a7f2090b938c28378189592a3654123da837868d8de8ab` |

The archived filenames are `dsl471-compiler.py`, `dsl471-dsl.py`, `dsl471-env_manager.py`, and `dsl471-cache_helpers.py`. Inspection of live `type(cute.compile)` also confirmed `cutlass.base_dsl.compiler.CompileCallable`.
