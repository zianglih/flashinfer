### Benchmark review validation

- **Follow-up:** `2bd125681b8d34c1835c1bd1916f8b9e3a630f6a`; only the dedicated benchmark changes. The benchmark diff against main shrinks from 214 to 152 changed lines while retaining the reproduction options. No `--fail-on-error` option is added.
- **C3 checks:** same B300/container/software above, BF16 M128×K64, layout128x4, one warmup and three measured samples per backend. Each case runs in a separate process. These are functional checks, not new performance comparisons. The source SHA-256 is `5535996f9117e89c457fae73155ff0eb6e819a7ef347a1fe26ff011cd907108b`.
- **Failure injection:** process-local CUPTI import failures (`ModuleNotFoundError` and a multiline `RuntimeError`) and a mocked `cupti-python` version of `12.0.0`. All three graph cases raise before the event fallback and export zero rows; eager fallback still completes with cold-L2 flushing. No package installation is changed.

```text
per-token-graph:             PASS, exit=0, rows=6
standard-graph:              PASS, exit=0, rows=6
graph-missing-cupti:         PASS, exit=1, rows=0 (expected rejection)
graph-old-cupti:             PASS, exit=1, rows=0 (expected rejection)
graph-multiline-cupti-error:  PASS, exit=1, rows=0 (expected rejection)
eager-missing-cupti:         PASS, exit=0, rows=6
bandwidth-graph:             PASS, exit=0, rows=3

CPU CLI checks: comparison (6 rows), bandwidth (3 rows), default timing
(60 rows), full sample precision, identical input seeds, and 4 invalid
shape/iteration controls passed.
pre-commit run --all-files: all checks passed
```

<details>
<summary>Reproduce the benchmark-mode checks</summary>

After the environment setup above, check out `2bd125681b8d34c1835c1bd1916f8b9e3a630f6a`. Run from the checkout with `PYTHONPATH="$PWD"`. This loop handles the three expected fallback exceptions and verifies the exported sample counts.

```bash
for mode in per-token standard missing old multiline eager-missing bandwidth; do
  NVFP4_REVIEW_MODE="$mode" python - <<'PY'
import builtins, csv, importlib.metadata, os, pathlib, runpy, sys
mode = os.environ["NVFP4_REVIEW_MODE"]
script = "benchmarks/bench_nvfp4_quantize_backend_comparison.py"
output = pathlib.Path(f"review-{mode}.csv")
reject = mode in ("missing", "old", "multiline")
if mode in ("missing", "eager-missing", "multiline"):
    original_import = builtins.__import__
    def injected_import(name, *args, **kwargs):
        if name == "cupti" or name.startswith("cupti."):
            if mode == "multiline":
                raise RuntimeError("line one\nline two")
            raise ModuleNotFoundError("CUPTI intentionally absent")
        return original_import(name, *args, **kwargs)
    builtins.__import__ = injected_import
elif mode == "old":
    original_version = importlib.metadata.version
    importlib.metadata.version = lambda name: (
        "12.0.0" if name == "cupti-python" else original_version(name)
    )
sys.argv = [script, "--m-values", "128", "--k-values", "64",
            "--dtype", "bfloat16", "--layouts", "swizzled_128x4",
            "--num-iters", "3", "--dry-run-iters", "1", "--seed", "42",
            "--no-heatmap", "--csv-output", str(output)]
if mode != "eager-missing":
    sys.argv.append("--cuda-graph")
if mode == "per-token":
    sys.argv.append("--per-token-activation")
if mode == "bandwidth":
    sys.argv.append("--bandwidth")
try:
    runpy.run_path(script, run_name="__main__")
except UserWarning as exc:
    assert reject and "Falling back to CUDA events for benchmarking." in str(exc)
else:
    assert not reject
with output.open(newline="") as stream:
    rows = list(csv.DictReader(stream))
assert len(rows) == (0 if reject else 3 if mode == "bandwidth" else 6)
assert all(row["cold_l2_cache"] == "True" for row in rows)
print(f"PASS: {mode}, rows={len(rows)}")
PY
done
```

</details>
