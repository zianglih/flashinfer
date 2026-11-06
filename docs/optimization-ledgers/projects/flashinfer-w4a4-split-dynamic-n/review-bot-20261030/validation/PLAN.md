# Focused review-fix validation plan

Status: awaiting root's frozen edit manifest and available GPU node. No source copied and no tests launched.

## Capacity

The managed CLI resolves to `/usr/local/bin/h`. A read-only access attempt reports that prior C2 devbox `fi-mega-scale-1029` is absent from namespace `ziangli`. No replacement requested. Root has been notified. The previous persistent cache location is:

```
/data/ziangli/flashinfer-w4a4-split-dynamic-n/upstream-integration-20261029/megamoe-glm5/cache/cpp
```

Cache existence cannot be confirmed while this node is unavailable. Do not delete or replace it. Once a node is approved, use only a distinct source snapshot at `review-bot-20261030/validation/source`, preserving earlier performance sources/evidence/caches.

## Frozen scope

Wait for root to freeze all final edits. Record the retained commit, each modified/untracked file hash, and the complete tracked-source manifest. The new validation source must equal that frozen tree, including the moved fixture in `tests/moe/conftest.py`. Recheck hashes before and after tests. Use the existing source snapshot/native include links if still available, verifying native Ninja command equality before reusing the C++ cache. Never copy a changing checkout or sync over an entire remote experiment root.

## Targeted tests

First collect the selected tests against the frozen source on SM103. Expected GPU scope is32 cases:

```bash
python3 -m pytest -q --full \
  tests/moe/test_unified_moe.py::test_cute_dsl_typed_activation_matches_flat_reference \
  tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy
```

- Unified typed activation:16 cases, four activations × NVFP4/BF16 activation pairs × legacy/swap-AB. This directly exercises the newly shared K96-aware exact reference on SM103 while retaining both layout modes and W4A16 coverage.
- Existing deterministic accuracy:16 cases, including per-tensor/per-token W4A4 in both layout modes and12 MX activation/tile cases. This checks that moving the fixture preserves the original main module's oracle integration, including native compile/cache observation and its exactness boundary.
- New CPU weight-layout/pack guard tests: add only root's final named selectors after freeze. Run separately with their intended CPU-only isolation. Do not infer a broad suite or add new tests to the repository here.

Use one exclusive idle B300 per independent test process (unified/main can run on two separate GPUs if available); no overlap on the same GPU. Preserve normal test/compiler behavior and production tactics. No sanitizer, profiling, compilation-option instrumentation, autotune performance sweep, or benchmark rerun.

Environment matches the prior test setup: `FLASHINFER_CUDA_ARCH_LIST=10.3a`, strict CuTe cache key, `FLASHINFER_DIST_AWARE_AUTOTUNE=0`, `TRTLLM_ENABLE_PDL=1`, one OpenMP thread, persistent native/driver caches. Keep these correctness tests independent from the already frozen full performance evidence.

Save source provenance, exact commands/environment, native build log, full pytest stdout, exit status, selected node IDs, GPU inventory and final idle state. A skipped or missing expected case must remain explicit. Stop and report failures; do not silently change source/tactics, weaken assertions, or use a default oracle plan.
