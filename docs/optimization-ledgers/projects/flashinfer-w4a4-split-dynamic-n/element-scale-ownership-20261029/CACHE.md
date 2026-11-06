# Preserve native compilation across Python-only experiment copies

Read-only audit, 2026-10-29. Source inspected: `flashinfer` at
`4376662a9ddefb1f62f0f81f4453964dc1f5a307`. No repository sources,
remote environment, or GPU jobs were changed by this audit.

## Recommendation

Give every experiment copy the same immutable native assets and the same
persistent native JIT workspace. Keep Python sources separate and keep the
CuTe DSL cache isolated or strictly source-keyed as before. No FlashInfer
kernel or JIT implementation change is needed.

Use the existing editable-install data layout: each copy's
`flashinfer/data/{csrc,include,cutlass,cccl,spdlog}` should resolve to the
**same absolute directories** in one pinned native asset snapshot. That
snapshot contains `csrc/`, `include/`, and the three `3rdparty/` trees. Do not
point them to the individual copy's native directories, and do not rewrite
or recopy the snapshot between phases.

This is not relying on a symbolic spelling that remains in the compiler
arguments. The current JIT generator explicitly calls `Path.resolve()` on:

- Every input source before emitting its Ninja build rule.
- FlashInfer, CUTLASS, CCCL, and spdlog include directories.
- Each module-specific extra include directory, including both
  `csrc/nv_internal` include paths used by FP4/FP8 quantization.
- Output objects under the shared JIT directory.

Thus identical canonical targets plus an identical native workspace and
flags produce identical source, include, object, and depfile paths. The
command-equality check below should verify this rather than assuming it.

If avoiding even a one-time rebuild matters, retain the currently warmed
native directories at their **existing absolute paths** as the canonical
snapshot and leave them immutable. Moving native assets to a new canonical
path changes commands once and may rebuild once; afterwards all copies
reuse it. A new native-content revision gets a separate asset snapshot and
cache namespace; do not edit a shared native snapshot in place.

## Current cache miss and source evidence

The MegaMoE harness already shares `FLASHINFER_WORKSPACE_BASE` across its
control/candidate processes. But `copytree(..., symlinks=True)` retains the
copies' data-link structure, while their native directories can resolve to
separate control/current roots. Sharing the output directory alone does
not make compiler commands equal. Ninja checks command/dependency
freshness even when the `.so` exists, so changing arms can rebuild the same
named `fp4_quantization_103` module.

Relevant source:

- `build_backend.py:1089`: `_create_data_dir` creates the five editable data
  links. Calling editable installation again resets links to that copy's
  native tree, so install first and set canonical targets afterwards.
- `flashinfer/jit/env.py:66`: `FLASHINFER_WORKSPACE_BASE` selects the cache
  base. Its workspace also includes FlashInfer version and target arch.
- `flashinfer/jit/env.py:395`: source/include constants derive from the
  package's `data` directory; there is no `FLASHINFER_CSRC_DIR` or
  `FLASHINFER_INCLUDE_DIR` environment-variable override here.
- `flashinfer/jit/cpp_ext.py:131`: standard and extra include paths resolve
  before emitting `-I`/`-isystem` options.
- `flashinfer/jit/cpp_ext.py:354`: source and object paths resolve in Ninja.
- `flashinfer/jit/fp4_quantization.py:35`: all seven FP4 native sources and
  both additional include paths use `jit_env.FLASHINFER_CSRC_DIR`.
- `flashinfer/jit/fp8_quantization.py:21`: MXFP8 quantization uses the same
  native source/include contract.
- `flashinfer/jit/core.py:578,617`: existing JIT output is checked through
  Ninja, not accepted blindly; build time logs also record Ninja no-ops.
- `upstream-integration-20261029/megamoe-glm5/run_comparison.py:49,79`:
  separate source copies and shared native workspace; source manifests
  intentionally exclude `data`, so add a separate native-asset receipt.

The module-level `jit_env` constants are overrideable for AOT tooling (the
comment at the top of `env.py` says so), but changing all of them in a
benchmark bootstrap is less simple and easier to get incomplete than using
the established editable data layout. No monkey patch is recommended.

## Persistent contract for the next experiment

- Same native snapshot and manifest, including every symlink target and
  native file SHA256; same source-generator code for native modules.
- Same `FLASHINFER_WORKSPACE_BASE`, FlashInfer version, architecture list,
  CUDA/Python/TVM-FFI installation and compiler paths.
- Same `CC`, `CXX`, `CUDA_HOME`, `FLASHINFER_NVCC`, compiler-launcher settings,
  `FLASHINFER_EXTRA_*FLAGS`, JIT debug/line-info flags and NVCC thread flags.
- Do not set `FLASHINFER_DISABLE_JIT`: it rejects needed JIT compilation,
  rather than proving that cached Ninja outputs are fresh.
- Persistent `CUDA_CACHE_PATH` is useful but is a distinct driver cache.
  A persistent `CUTE_DSL_CACHE_DIR` is also distinct from native C++ JIT;
  retain arm isolation or the existing strict source-key policy.
- Native assets and canonical link targets must remain unchanged for all
  fresh-process phases. Preserve dependency mtimes by not rewriting the
  snapshot. Keep build manifests and native build timing logs with results.
- Compiler launchers (`FLASHINFER_CXX_LAUNCHER` and
  `FLASHINFER_NVCC_LAUNCHER`) are supported and can add a second-level cache,
  but do not substitute them for canonical paths or claim hits unverified.

## Verify before GPU timing

In each source environment, with the intended shared environment variables,
run a CPU-side build-description check. It generates strings only; it does
not call `build`, `write_ninja`, `build_and_load`, or a CUDA kernel:

```python
import json
from flashinfer.jit import env
from flashinfer.jit.cpp_ext import generate_ninja_build_for_op
from flashinfer.jit.fp4_quantization import gen_fp4_quantization_sm103_module
from flashinfer.jit.fp8_quantization import gen_mxfp8_quantization_sm100_module

result = {"native_paths": {
    "csrc": str(env.FLASHINFER_CSRC_DIR.resolve(strict=True)),
    "include": str(env.FLASHINFER_INCLUDE_DIR.resolve(strict=True)),
    "cutlass": [str(p.resolve(strict=True)) for p in env.CUTLASS_INCLUDE_DIRS],
    "cccl": [str(p.resolve(strict=True)) for p in env.CCCL_INCLUDE_DIRS],
    "spdlog": str(env.SPDLOG_INCLUDE_DIR.resolve(strict=True)),
    "workspace": str(env.FLASHINFER_WORKSPACE_DIR.resolve()),
}}
for make_spec in (
    gen_fp4_quantization_sm103_module,
    gen_mxfp8_quantization_sm100_module,
):
    spec = make_spec()
    result[spec.name] = generate_ninja_build_for_op(
        name=spec.name,
        sources=spec.sources,
        extra_cflags=spec.extra_cflags,
        extra_cuda_cflags=spec.extra_cuda_cflags,
        extra_ldflags=spec.extra_ldflags,
        extra_include_dirs=spec.extra_include_dirs,
        needs_device_linking=spec.needs_device_linking,
        extra_cuda_cflags_by_source=spec.extra_cuda_cflags_by_source,
    )
print(json.dumps(result, sort_keys=True, indent=2))
```

Set `FLASHINFER_CUDA_ARCH_LIST=10.3a` before imports so architecture selection
is fixed; use the same image/runtime. Compare the **entire JSON byte for
byte** across control/candidate, including the full generated Ninja strings.
The FP4 generator may query `nvcc --version`; it does not compile. Check that
none of the per-copy source roots occur in the resulting native commands.
Also check the source snapshot's native manifest before and after each phase.
For any additional native module admitted by the benchmark, repeat the same
Ninja-description comparison for that module's actual JitSpec.

After the first ordinary warmup, record `FLASHINFER_JIT_BUILD_LOG` and, where
useful, `FLASHINFER_JIT_VERBOSE=1`. A real NVCC compile will be visible in
verbose output; repeated import/build calls may still produce fast timing
records for a valid Ninja no-op. Do not classify all recorded `nvcc` build
entries as compilation. A dry run of the unchanged module's saved Ninja file
(`ninja -n -f <build.ninja>`, using its build directory) is another direct
check that no compiler commands are scheduled.

The above is a source-traced recommendation, not a live proof of cache hits:
no remote compile or GPU action was performed during this audit. Do not
modify the current CAAC measurement process midway; apply it to the next
experiment only, after the current final-data audit.
