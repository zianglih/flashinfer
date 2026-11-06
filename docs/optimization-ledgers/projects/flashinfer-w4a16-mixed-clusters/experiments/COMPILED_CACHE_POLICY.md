# Separate FlashInfer workspaces for future captures

Implemented locally in project helpers only. The active remote middle pair and its frozen helpers are unchanged. No source repository, native driver, policy wrapper, GPU run, or remote file was modified for this change. The previous helpers and middle-pair script are preserved in [`cache-policy-v1-before/`](cache-policy-v1-before/), with exact SHA256 values in its `manifest.json`.

## Evidence

The A2 baseline and candidate both used `compile-cache/baseline/flashinfer` as `FLASHINFER_WORKSPACE_BASE`. Their `fp4_quantization_103` and `dsv3_fused_routing` modules therefore occupied the same build directories. Each module's two saved `build.ninja` files are byte-identical after replacing only the full absolute checkout prefix (`.../baseline/` versus `.../flashinfer/`); include paths and input source paths change when switching arms.

| A2 arm | Support-prewarm receipt elapsed time | Receipt |
| --- | ---: | --- |
| Baseline AUTO16/all | 26.178690 s | [baseline support JIT](../evidence/remote/queues/glm5-baseline-auto16-all-pc-t4096-a2/support-jit/receipt.json) |
| Candidate3r AUTO18/mixed-only | 137.673541 s | [candidate support JIT](../evidence/remote/queues/glm5-candidate3r-auto18-mixed-only-pc-t4096-a2/support-jit/receipt.json) |

These are wall-clock intervals between receipt timestamps, including build/load and artifact hashing. They are not kernel timings or an estimate of the time saved by this change. Binary hashes can differ because absolute paths are embedded; the receipt does not establish byte-identical support binaries.

The underlying [FlashInfer JIT build path](../flashinfer/flashinfer/jit/core.py) writes Ninja input and invokes Ninja on each build (`build`, lines618–640). Its build directory is keyed by workspace/version/architecture/module, not checkout identity. Separating the workspace preserves each checkout's own Ninja commands and objects across arm switches. Initial compilation remains necessary in a newly selected workspace; actual repeated-run reuse has not been GPU-validated here.

## Helper contract

- [`harness/run.py`](../harness/run.py) accepts optional `--workspace-base`. Without it, all four paths retain the old `--cache-root` layout and the receipt records `compiled_cache_policy="cache-root-v1"`. With it, only `FLASHINFER_WORKSPACE_BASE` changes and the receipt records `"separate-flashinfer-workspace-v1"`.
- The shared pure `compiled_cache_settings` function resolves paths without imports of CUDA or filesystem mutation. Timing runs still use shared `CUTE_DSL_CACHE_DIR`, `CUDA_CACHE_PATH` and `TRITON_CACHE_DIR` when passed the same `--cache-root`.
- [`harness/compare.py`](../harness/compare.py) continues allowing different absolute cache paths but now compares the semantic policy. Missing fields in old captures mean `cache-root-v1`. Unknown policies and mixed old/new policies are rejected before writing a comparison report. Do not retroactively relabel old captures.
- [`remote/profile_pair.py`](../remote/profile_pair.py) now selects `compile-cache/<source_name>/flashinfer` for each checkout, before both support prewarm and NCU. The prewarm helper already consumes and records that environment, so it is unchanged. The launcher retains its historical pair labels; a future coordinated launch still needs fresh labels/output paths.

`FLASHINFER_WORKSPACE_BASE` is a whole FlashInfer workspace: it also holds FlashInfer-managed CuTe exports. It is not exclusively a C++ cache. W4A16 MegaMoE's frontend uses direct `cute.compile`. Keeping compiled caches enabled does not prove persistent CuTe reuse; the recorded historical DSL4.7.1 direct-compile behavior remains unchanged.

Native `profile_ncu` overrides the inherited CuTe cache with a fresh per-report `cute_dsl_lineinfo_cache` and `CUTE_DSL_LINEINFO=1` ([driver](../flashinfer/benchmarks/bench_cute_dsl_moe_distributed.py), lines554–563). Preserve that policy. The profile receipt now records these effective overrides separately; do not describe NCU's worker CuTe cache as shared across arms.

## Future invocation and fairness boundary

Add the following to the existing timing command for each arm, leaving all other arguments unchanged:

```bash
# Baseline arm
--cache-root "$MIXED_ROOT/compile-cache/baseline" \
--workspace-base "$MIXED_ROOT/compile-cache/baseline/flashinfer"

# Candidate arm
--cache-root "$MIXED_ROOT/compile-cache/baseline" \
--workspace-base "$MIXED_ROOT/compile-cache/flashinfer/flashinfer"
```

Both arms explicitly select the new policy even though the baseline path happens to equal its legacy path. Keep native AUTO selection, `FLASHINFER_MOE_EP_KNOB_CACHE=0`, timing, warmups, fixtures and compiled-cache enablement unchanged. Do not reuse winner configurations or copy `.so` files between sources. The goal is to retain correctly built artifacts within each checkout's stable workspace, not to alter measured execution. Compilation and tuning remain outside reported kernel timing.

No remote sync is authorized by this note. Coordinate with the root GPU owner after the active pair completes. At the first future use, retain per-source prewarm receipts and Ninja logs; a subsequent same-source prewarm should report no new compilation commands when inputs/flags are unchanged. This validation has not run yet.

## CPU validation

Eight focused tests in [`harness/test_cache_policy.py`](../harness/test_cache_policy.py) passed. They cover legacy/override environment construction, the actual profile-arm cache assignment for both sources, argparse dry runs with identical native AUTO/timing commands, full comparison CLI acceptance of old missing-field captures and explicit legacy captures, matching split policies with different paths, and rejection of mismatched/unknown policies. Tests use synthetic captures and import no CUDA stack. Ruff and AST parsing passed.

The first local test invocation exposed macOS `/var` versus `/private/var` path resolution in the test fixture. The fixture was corrected to use a resolved project-local temporary directory; no production behavior changed for that test repair. Detailed commands, final hashes and untouched-file verification are in [`compiled-cache-validation.json`](compiled-cache-validation.json).
