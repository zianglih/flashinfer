# Separate finalizer rounding spotcheck

This is an isolated follow-up to the user-approved W4A4/W4A16 deterministic-combine rounding change. It does not replace or amend any primary split-MoE result measured at `9ec90d0`.

Before source is extracted byte-for-byte from `c610e3c9d46078a131bd84cd6d98ab682d03eb54`; `source/before-provenance.json` records its hash. The script snapshots the current candidate finalizer as the after arm and records its actual Git revision, status, and source hash. Both modules run in the same process on identical tensor objects, with separate compile caches.

- Four shapes: T8/T8192 × expanded W4A4 layout/permuted W4A16 layout; H7168, top-k8, BF16 route terms/output, FP32 scales.
- All routes are valid/local. This deliberately exercises all eight weighted terms; it is not the primary benchmark's EP8 traffic distribution.
- PDL is disabled by default because this isolated measurement has no FC2 producer. `--enable-pdl` is available for an explicitly requested additional check.
- Native CUPTI timer, CUDA graph, cold L2, ten requested warmups and 100 samples per arm. Import/version checks and warning escalation prohibit a fallback timer.
- Each shape runs before R1 → after R1 → after R2 → before R2. Compilation, input generation, permutation and snapshots are untimed.
- Output keeps every one of the 1,600 samples, all 16 absolute medians and four paired ratios. It also checks BF16 bit equality between sources on these ordinary finite inputs; edge numerical contracts belong to the new exact tests.

Run only after correctness is accepted, in the existing C2 project environment:

```bash
project=/workspace/flashinfer-w4a16-split-dynamic-n
cd "$project"
CUDA_VISIBLE_DEVICES=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0 \
  bash "$project/scripts/with_arm_cache.sh" candidate \
  "$project/.venv/bin/python" "$project/scripts/bench_finalize_rounding.py" \
  --repo "$project/candidate" \
  --before-source "$project/diagnostics/finalizer-rounding/source/before-moe_finalize.py" \
  --output "$project/diagnostics/finalizer-rounding/rounding-spotcheck.json"
```

Minimal existing W4A4 deterministic-finalize regressions (two source-declared exact node IDs):

```bash
cd "$project/candidate"
CUDA_VISIBLE_DEVICES=0 PYTHONPATH="$PWD" "$project/.venv/bin/python" -m pytest -v --tb=short \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]'
```

These exercise W4A4 per-tensor activation scaling at T128/top-k1 and per-token scaling at T515/top-k8. They are existing end-to-end numerical regression checks with their existing tolerance; the new direct finalizer tests must enforce the signed-zero, subnormal, masked-route and exact rounding contracts. The W4A4 cluster-padding cases in the same file use fused finalize and therefore do not exercise this changed standalone finalizer.

Prepared and statically checked locally; no GPU measurement or test execution was launched by this helper-preparation step.
