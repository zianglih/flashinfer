# Cleaned regular-TMA validation

The source is the independent, unstaged `regular-tma-review` checkout at base
`442d2aa53f68b4640c3ab5118a76f1599ff60d34`, with the exact three files pinned in
`manifest.json`. The full experiment manifest is pinned to
`9f174d224c41b18fd59f51deb360464f70654724ed1acf91d38aa1a55fe1e1f2`.

`probe_poison.py` is **byte-for-byte identical** to the frozen helper in
`scripts/prep_validcopy_experiment` (SHA256
`a86f2588a9fba802fa86ef4199f3df9729642f8c983585b509a44b7096b1e1da`). Its historical
docstring and `VALIDCOPY_*` output labels are intentionally unchanged. Only the
adjacent manifest and explicit launch paths select the cleaned source. There
are no modified assertions, new shape selections, or repository test files.

The 126 checks comprise 90 preparation graph replays and 36 paired FC1 plus
downstream checks. They cover six operand/SF formats; graph growth/shrink/zero
tiles; N16 physical padding; valid-payload bytes, complete canonical SF padding
and suffix canaries; partial N16/N128/N256 tiles; quantized FC1 output; and
original-token scaling. FC1 compares all output and SF bytes against frozen442.
Downstream quantization/FC2/combine uses the same unchanged implementation for
both arms, so this is not a separate claim of changed FC2 coverage. Public
per-token support remains NVFP4-only. The deliberately poisoned allocation
checks numerical isolation, not initialization safety; initcheck is not run.

## Authorized focused run

```bash
bash scripts/regular_tma_final_validation/run_exact.sh
```

This runs only GPU4 exact checks, with a separate CuTe cache and the existing
candidate native cache. It records command, timing duration (not performance),
GPU UUID, package versions, environment, source hashes and before/after pins.
The unique output is `results/exact-r1/` beside this README, with a separate
driver log `logs/regular-tma-review-exact-r1-driver.log`. Existing result paths
are refused. No timing campaign or sanitizer is started by that script.

## Deferred existing tests and bounded sanitizers

Run only after the parent's performance decision and GPU assignment. These
commands are a plan, not executed results. The two pytest selections are the
existing 71+24 tests from the final442 campaign. Fused-finalize cases stay
excluded. Before and after each command, check the same manifest pins and save
command/environment/source receipts; use a fresh output directory per run.

```bash
ROOT=/workspace/flashinfer-w4a4-split-dynamic-n
cd "$ROOT"
source scripts/recovery442/env_candidate.sh
export PYTHONPATH="$ROOT/regular-tma-review" OMP_NUM_THREADS=1
export CUTE_DSL_CACHE_DIR="$ROOT/cache/regular-tma-review-validation"
cd regular-tma-review
TEST=tests/moe/test_cute_dsl_fused_moe.py
python -m pytest -q -ra --tb=short \
  "$TEST::test_gather_gemm_k_tail" \
  "$TEST::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy" \
  "$TEST::TestCuteDslMoeW4A16::test_weight_scale_mapping" \
  "$TEST::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a16-ordinary]"
python -m pytest -q -ra --tb=short \
  "$TEST::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy" -k False
```

For bounded memory/race coverage including the new preparation kernel, reuse
the exact same 126-case probe under each tool. This includes preparation graph
growth/shrink and all six FC1 formats without adding another test selection.
Add the existing three memcheck reference cases for independent reference
coverage. Use the parent-assigned GPU and isolated output/log paths. Require
zero exit status, all expected cases, zero sanitizer errors/hazards, and review
any warnings; do not infer sanitizer success from numerical success.

```bash
E="$ROOT/scripts/regular_tma_final_validation"
compute-sanitizer --tool memcheck --error-exitcode 99 --check-bulk-copy yes \
  "$ROOT/.venv/bin/python" "$E/probe_poison.py" \
  --repo "$ROOT/regular-tma-review" --baseline-repo "$ROOT/candidate" \
  --output "$E/results/memcheck-r1/checks.json"
compute-sanitizer --tool racecheck --error-exitcode 99 \
  --racecheck-memcpy-async yes --racecheck-report all \
  "$ROOT/.venv/bin/python" "$E/probe_poison.py" \
  --repo "$ROOT/regular-tma-review" --baseline-repo "$ROOT/candidate" \
  --output "$E/results/racecheck-r1/checks.json"
compute-sanitizer --tool memcheck --error-exitcode 99 --check-bulk-copy yes \
  "$ROOT/.venv/bin/python" -m pytest -q \
  "$TEST::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]" \
  "$TEST::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]" \
  "$TEST::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a16-ordinary]"
```

The earlier cleanup AST proof establishes equality of live source operations
after constant pruning. It does not establish CuTe codegen/binary identity.
New GPU results must remain distinct from the prior validcopy and final442
validation archives and from primary performance evidence.
