# Split W4A16 constexpr top-k candidate

Base: current upstream `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`. Applied locally, uncommitted. No other implementation change or alignment specialization is included.

The production diff has three changed lines across two files: annotate the private kernel wrapper's `top_k` as `cutlass.Constexpr`, include its actual value in the existing compile-cache key, and omit it from the compiled runtime invocation. The `cute.compile` call still receives top-k, matching the existing `max_active_clusters` constexpr ABI pattern. This makes the fused-finalize score layout's second dimension static and exposes the existing quotient/remainder to constant-divisor lowering. It adds no public knob, helper, pipeline state or new math expression.

Both public functional/wrapper calls reach the existing W4A16 runner and `launch_w4a16_moe`; the private launch derives top-k from actual route/scale shapes. Different values now select different compiled entries. Non-fused GEMMs pass effective top-k0, but their constexpr finalize flag removes the score tensor and every associated division. Runtime m/k/n and token count remain dynamic. No performance gain is claimed, and the usual `--no-fused-finalize` benchmark should not be assumed to benefit from fused-finalize arithmetic changes.

The existing route-boundary test now forms six unchanged geometries × top-k `[2,3]` × finalize `[False,True]`: 24 cases, using its original tensor factory, reference and tolerances. This includes a non-power-of-two divisor and exercises both effective top-k0 and distinct fused values in a single-process selection. The original test was deterministic/non-fused; its False/top-k2 product remains. Each selected expert receives one full and one partial route tile. No new upstream test file is added.

Existing selector for the sole executor:

```bash
pytest -q tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy
```

Local checks completed: Python syntax compilation without imports for all three files; AST confirms the6×2×2 existing test product; `git diff --check`; scoped pre-commit including mypy and Ruff. GPU numerics and native compiler/ABI inspection have **not** run. Native review should confirm static top-k2/3 arithmetic and absence of the old runtime argument, with unchanged non-fused behavior, resources and synchronization.

Independent bounded source review passed: compile-time argument retention, runtime argument removal, cache-value separation, dynamic m/n/k/token extents and the non-fused zero-value branch are consistent. This adds no native or GPU execution claim.

Artifacts: [source-only diff](source.patch), [test diff](tests.patch), [complete diff](candidate.patch), [source pins and local validation](source-review.json), [hook output](pre-commit.log), [syntax/product result](static-validation.json). No commit, push, benchmark or GPU action was performed by this task.
