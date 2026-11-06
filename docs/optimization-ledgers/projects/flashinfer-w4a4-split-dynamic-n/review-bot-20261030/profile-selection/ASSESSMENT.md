# CodeRabbit 4422345958 — valid, benchmark profiling only

Assessed retained PR head `f173414b5b256f78a5356f611366a0b092944a1d`.
Source: `benchmarks/bench_moe_deepseek.py`, SHA
`0d1d6c8bc4aa4d6305c2576c9af6cfc41986479779bb5f9310c0fffbc82c2409`.

The finding is correct. `main()` accepts an omitted `--backends` and uses the
profile target for its validation/logging, but forwards `backends=None` to
`run_benchmark()`. `_benchmark_single()` independently rebuilds the family
selection and only replaces it for four MX profile targets. For an excluded
target, the family selection is nonempty, so input preparation still runs;
every backend condition fails, and the function returns an empty result list.
Profiling suppresses table output, and `main()` returns success. The actual
`cudaProfilerStart()` is inside `_measure_or_profile()`, reached only through a
selected `bench_*` call, so this path never begins the requested capture.

## CPU reproduction

`python3 review-bot-20261030/profile-selection/audit.py`

The harness compiles the actual `main`, `run_benchmark`, `_benchmark_single`,
family selection and output-validation AST. GPU queries, allocation and backend
execution are replaced with inert CPU stubs. No GPU was initialized.

| Family | Silent success with no backend dispatch |
|---|---|
| NVFP4 | `cutlass` |
| MXFP | `cute-dsl`, `cute-dsl-w4a16`, `cute-dsl-per-token`, `cutlass`, `trtllm-nvfp4`, `trtllm-per-token` |

All seven cases returned exit code 0 with zero backend calls. These include both
examples in the comment. The other 15 profile/family combinations dispatched.

The proposed local replacement was also tested **in memory only**: when
`backends is None` and `profile_backend is not None`, select that target, mapping
`cute-dsl` and `cute-dsl-w4a16` to the existing `cutedsl` selector. All 22
profile/family combinations then dispatched exactly one requested backend.
All 22 explicit-compatible-backend cases were unchanged; both ordinary family
defaults were unchanged; explicit target exclusion still failed in argparse.

## Severity and minimal-fix boundary

- Low severity / P2-class tooling bug: explicit supported profiling requests can
  silently produce no capture. It does not affect kernel correctness, normal
  benchmark execution, or the completed source-bound performance measurements.
- The inline replacement suggested by the review is sufficient; no shared
  selection abstraction or production API change is necessary.
- Preserve the `backends is None` condition: an explicit list remains user
  authority and `main()` already rejects a conflicting profile target.
- Preserve both CuTe aliases. `cutedsl` selects the family, while the existing
  inner `profile_selector` condition chooses exactly W4A4 or W4A16.
- Do not rewrite `backends` in `main()` as part of this fix. The default table
  validator runs before profiling; feeding it a cross-family explicit selector
  can reject a valid profiling request. The local selection change avoids this.
- Existing unsupported-model checks must still raise their current error once
  the requested backend is selected. The CPU reproduction deliberately treats
  every backend as supported to isolate this dispatch issue.
- Direct Python callers can still pass inconsistent explicit lists/profile
  targets without the CLI guard; that pre-existing API boundary is outside this
  narrowly verified finding.

No repository edits, GPU runs, commits or review replies were made. Evidence is
`results.json`; the in-memory proposed-fix experiment is not a production change.
