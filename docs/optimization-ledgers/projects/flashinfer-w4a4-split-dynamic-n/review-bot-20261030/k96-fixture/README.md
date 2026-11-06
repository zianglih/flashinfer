# Shared SM103 native-MMA-plan observer

Local unstaged change in `tests/moe/conftest.py`, `test_cute_dsl_fused_moe.py`, and `test_unified_moe.py` only.

The shared module-scoped `swap_ab_moe_reference` fixture owns the existing compile/cache observer and returns the same reference with actual FC1/FC2 K plans on SM103. On other architectures it returns the original reference. The existing accuracy module retains a small autouse alias-binding fixture; the typed-activation unified test requests the shared reference directly. No new test file/function, production policy, tactic, oracle arithmetic or tolerance change.

CPU validation passed: the four observer internals are AST-identical to the original; unified test logic and parameterization are AST-identical after reversing fixture wiring. Extracted fixture checks cover independent FC1/FC2 K plans, cache hits, partial-K order, K64/MX and architecture/unavailable fallbacks, unchanged compile arguments/options and cleanup. Scoped pre-commit, py_compile and git diff --check passed.

Runtime boundary: no actual pytest collection or GPU execution was performed. Local Python lacks pytest, Torch and CuTe DSL, and the previous C2 allocation is unavailable. The new unified SM103 exact cases and existing accuracy suite still need GPU verification. The original missing-plan issue is established by source tracing; no seeded test failure is claimed.
