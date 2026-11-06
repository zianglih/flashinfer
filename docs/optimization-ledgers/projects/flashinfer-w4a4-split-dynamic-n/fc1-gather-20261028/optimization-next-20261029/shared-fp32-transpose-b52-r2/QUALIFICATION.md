# Shared FP32 transpose R2 qualification

The frozen `f5b7124b` kernel passed all 41 existing exact cases with 80 compiled captures. This is an explicit experimental qualification, not a retroactive pass of the original strict static-local-site gate.

- **Source:** retained b52 control versus the shared-transpose candidate; all 514 source files are bound, and only `moe_swap_ab_kernel.py` differs. Production source, quotas, routes and tactics were unchanged during qualification.
- **Normal resources:** 78 exact signatures have zero stack/local traffic and no LDL/STL sites. All native kernels admitted to performance runs must independently report zero runtime local bytes before launch.
- **Inherited stress:** only original M512/K8 MXFP4x8 and MXFP8 signatures 48/50 permit their separately captured exact expectations: REG168, STACK72, 44 LDL sites and 17 STL sites. The control has STACK128 and 16/16 sites. Reduced hot-MMA stores do not imply reduced total local traffic: common-role reloads increase. These exceptions never enter timed native cells.
- **Planner:** the extra FC1 scratch is 8,704 bytes versus 512. Actual planner execution reproduces all 80 baseline captures and 1,456 prior native/automatic evaluations. Expected geometry and physical shared-memory use are specified for every capture. Only automatic-K test rows 6/8 change K4→8 and operand stages9→4. Frozen native winners use explicit K. FC2 planner behavior is unchanged.
- **Evidence:** `qualification-r2/evidence-audit.json` verifies all 583 fetched files and 41 raw XML cases. The exact receipt is `6d9da876…`, the derived planner manifest is `8da4bd61…`, and the expected stress manifest is `31e0e9f8…`. Independent guard and planner reviews are preserved alongside the helpers.

The original static-site rejection remains in `codegen-analysis.json`. The first exact attempt in `qualification-r1` stopped before the fourth case's launch because its old guard did not permit the intended automatic-K planner change; three cases had passed. `qualification-r2` adds only the source-derived geometry manifest, retains all resource constraints, and passed the full matrix. No sanitizer was run.

Performance is a separate predeclared 24-cell, source-paired CAAC screen under `../shared-fp32-transpose-screen-r2`; this qualification makes no speedup claim.
