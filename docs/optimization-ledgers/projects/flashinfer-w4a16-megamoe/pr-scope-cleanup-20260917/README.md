# PR-scoped implementation cleanup

Audit baseline: PR #5019 at `45c1034bf42c3c7178d8f3a832663a1806750859`, compared with merged upstream `f17b77260919a55b2d18b109370c149a74f34065`. This cleanup removes only code added by the PR. It does not modify vendored source or delete preexisting upstream code.

## Changes

- Reuse `shim.kernel_helpers`' curated export registry instead of maintaining an additional list of 28 kernel primitives in the facade and repeating them in the shim's `__all__`. Preserve the original upstream lazy lookup and export lists. The requested facade's PR additions fall from 53 to 17 lines.
- Remove the unused `is_valid` and `compute_expert_token_range` exports. Replace the identical maintained `init_dist` wrapper with the existing exported function, making the added `bootstrap_dist` export unnecessary. Import the lightweight epilogue resolver normally: the shim already loads its module.
- Pass the autotuner's default-async launch directly to graph timing, removing one forwarding closure. Keep explicit synchronous warmup and all group-scoped barriers/reductions.
- Remove unused internal constructor `local_rank` and JIT `fc1_c` arguments. Use one internal `in_kernel_fc2_reduce` argument and derive dispatch return from `token_back_mode`, instead of accepting redundant aliases. Public permission versus selected-tactic fields remain distinct and unchanged.
- The added routing-round test now uses the existing input-only generator rather than allocating unused expert weights. It preserves the seed, tensors, oracle and tolerance. At E4/H7200/I2112 this avoids 364,953,600 bytes (348.05 MiB) per rank per round; this is allocation accounting, not a measured speedup.

Production changes remove 86 net lines; the explicit test input dictionary adds six net lines. Net cleanup: 80 fewer lines.

## Entire-PR comparison

| Area | Existing pattern and audit outcome |
| --- | --- |
| Backend/config/weights | Retain existing MegaKernelBackend lifecycle hooks, canonical dtype naming, NVFP4 packed layout, and config/runtime FP32 alpha interface. No further wrapper deletion was warranted. |
| Facade/shim | Preserve the required public-drop import boundary and lazy heavy helpers; remove only PR-added duplicate export bookkeeping. All original facade names remain. |
| Frontend/autotune | Reuse existing distribution initialization; retain workspace ownership, capture guards, selected tactic caching and the independently required subgroup-safe timer. |
| Kernel orchestration | Compare with BF16 and BF16×MXFP8 MegaMoE patterns. Epilogue context/transpose and scheduler/communication adapters have concrete ownership/layout purposes; retain them. Prune unused internal call arguments and duplicate aliases. |
| Device pipeline | Preserve two decode WGs, five total WGs, early weight runahead, staged TMEM ownership, all fences/barriers and deterministic default combine. No pipeline or instruction optimization is attempted by this cleanup. |
| Tests | Keep existing cartesian precision/reduction coverage and oracles. Simplify only the PR-added routing-round helper; preexisting input/oracle helpers stay unchanged. |
| Benchmark | Keep the required matched-weight end-to-end timing, rank-MAX CUPTI methodology and coordinated NCU/NSYS flows. Their callbacks represent distinct timed/profiled stages; no deletion is warranted solely to reduce lines. |
| Docs/shared files | Keep the short dtype-specific exceptions and required maintained-kernel import-layer description. No unrelated upstream cleanup. |

## Validation

- `check_scope.py`: confirms removed nonblank lines originate in PR additions; both shared export files preserve original upstream source in order. All maintained/backend imports use the public drop boundary; vendored source is unchanged.
- `check_exports.py`: 105 unique facade exports, 34 retained lazy routes, and 141 repository caller imports verified; no original export removed. The real facade/shim host code is loaded, but the missing CUDA DSL Float32 constant constructor and heavy helper lookups use explicit stand-ins. This is host import/routing validation, not native CUDA execution.
- `autotune-host-results.json`: 14 actual-source control-flow checks pass with mocked CUDA operations and CPU Torch score tensors.
- `routing-input-equivalence.json`: 12 exact CPU-adapted comparisons pass for inputs, shapes, dtypes and strides, including empty, large and skinny shapes. Other test functions and the existing input helper are unchanged.
- `kernel-argument-equivalence.json`: all 18 non-constructor method bodies are AST-identical; 54 tactic/session and 540 explicit-configuration constructor-state comparisons plus eight rejection checks pass under CPU transport/dtype mocks. No native compilation is claimed.
- `pre-commit-full-pr.log`: full-PR scoped checks pass, including mypy and Ruff. `git diff --check` passes.

No GPU tests, compute sanitizer or benchmarks were rerun for this cleanup. The published performance table remains tied to measured commit `1098a348`, not the cleanup head. Internal signature/source equivalence is not a claim of newly verified native codegen or performance.

Run local checks from the source checkout:

```sh
python3 ../pr-scope-cleanup-20260917/check_scope.py
../.venv-weight-layout/bin/python ../pr-scope-cleanup-20260917/check_exports.py
../.venv-weight-layout/bin/python ../pr-scope-cleanup-20260917/check_routing_inputs.py
```

## Publication

```text
fc676ce6821c1dcf51ef2966f1c4ae4da3aae0d7 test(moe): avoid unused routing-fixture weight allocations
455183f57de08e8c4dd56a96c287b75bb0b40574 refactor(moe): trim BF16 NVFP4 glue and unused kernel arguments
```
