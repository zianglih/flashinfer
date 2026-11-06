# Relevant existing-test validation

All selected tests passed; see [RESULTS.md](RESULTS.md).

Validation targets pushed commit `d1767be1f42fdc371f90db4fb06598299ea32845`.
GPUs 6 and 7 use the same clean snapshot and persistent cache as the benchmark.
No duplicate source deployment is created.

The selection extends the 28-case retained R2 accuracy gate recorded in
`optimization-20261027/warp-specialization/full-rerun/validation.md` and reuses
its existing pytest/receipt pattern. Tests are selected directly from the
repository; this folder adds no repository tests or reference self-tests.

| Group | GPU | Expected cases | Coverage |
|---|---:|---:|---|
| `exact` | 6 | 33 | Swap-AB W4A4/per-token/MXFP8/MXFP4x8 reference checks, SwiGLU/SiTU/GeGLU/ReLU2, narrow/two-CTA explicit five-field tactics, default tactics, strict/fast 4over6 recipes, K tail, W4A16 layouts and scale updates. Includes two existing legacy MX ReLU2 controls. |
| `api` | 7 | 62 | Eight wrapper mode/finalize cases each in eager and CUDA graph execution, all 16 unified typed-activation/layout cases, seven legacy W4A8 fused API/tactic cases, all 17 scope tests (including strict and non-strict GPU replay/capture), and six policy override/identity/replay tests. |

Counts must be confirmed by collection; the runner refuses mismatches. Swap-AB
reference assertions inspect storage bits; legacy cases retain their existing
numerical tolerance. The test matrices exercise both newly prepared weights and
untagged unified packs after removal of the layout tag/assertion. W4A16 keeps its
existing implementation and tactic set. These are relevant focused tests, not an
exhaustive cross-product or Rubin qualification. Sanitizers remain skipped.

Run each group on its assigned idle GPU using the same clean pushed checkout,
Python environment, and persistent native compilation cache as the benchmark.
The previously used interpreter is
`/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python`;
its directory name does not imply sanitizer execution. Root supplies the exact
current environment paths and image. The source is imported from `--repo` and
checked against the exact `--commit`; logs, collection, JUnit, package versions,
source hashes, telemetry, and phase status are recorded. No cache is deleted.

```bash
python3 run_existing_tests.py \
  --repo "$PR_SOURCE" --commit "$PR_COMMIT" \
  --python "$VALIDATION_PYTHON" --python-deps "$PYTHON_DEPS" \
  --workspace "$PERSISTENT_WORKSPACE" --image "$EXACT_IMAGE" \
  --gpu 6 --group exact --output "$ARTIFACTS/exact"
python3 run_existing_tests.py \
  --repo "$PR_SOURCE" --commit "$PR_COMMIT" \
  --python "$VALIDATION_PYTHON" --python-deps "$PYTHON_DEPS" \
  --workspace "$PERSISTENT_WORKSPACE" --image "$EXACT_IMAGE" \
  --gpu 7 --group api --output "$ARTIFACTS/api"
```

After GPU7 pytest, the runner executes the existing Linux-only CI helper tests:
`python3 -m unittest discover -s ci/tests -p test_compile_cache.py -v`.
The full benchmark separately exercises real tuning and replay. The selected
scoped GPU tests prove disk hydration and graph capture with profiling blocked
in the replay phase. No sanitizer is run.
