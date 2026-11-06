# W4A16 static Gather4 elected-issuer scope: rejected

The isolated candidate on retained `475cae6b` moved the elected-lane scope around each entire statically unrolled B-stage issue batch. All route-ID shuffles remain outside the scope and outside K. Four independent producer arrivals, stage state, transaction counts, TMA geometry, padding, registers, PDL, scheduling, and FC2 remain unchanged.

Final source patch: `f48bcffb428634cdc4166595bb8b70f95a96146befdf6329ad93478c48f081d3`. The full before/after Python AST is identical after flattening election scopes, inlining the shared-view extraction, and normalizing issuer-local variable names (`ast-equivalence.json`).

| Actual FC1 specialization | Instructions before / after | Branches before / after | R2UR before / after | SHFL before / after |
|---|---:|---:|---:|---:|
| K3 EP8, T4096, M256 N128 K256, cluster2 | 2008 / 2012 | 182 / 183 | 38 / 38 | 16 / 16 |
| K3 EP8, T8192, M256 N192 K256, cluster2 | 2054 / 2058 | 185 / 186 | 46 / 46 | 24 / 24 |
| V3 TP8, T8, M256 N16 K256, cluster2 | 1673 / 1677 | 199 / 200 | 23 / 23 | 4 / 4 |

All three candidates compile at 96 initial registers, 640 threads, zero local bytes, and no LDL/STL. The larger scope consistently adds four instructions and one branch, with no reduced coordinate-transfer work. Reject at the codegen gate; no runtime accuracy or performance campaign was run. Do not interpret this as a measured latency regression.

The initial capture timed out in a shared native C++ cache rebuild before entering CuTe compilation. After the owning build completed, the idle candidate's whole `flashinfer/data` link was normalized to the established persistent seed, and compilation proceeded. That infrastructure timeout is preserved separately.

Two intermediate forms failed CuTe IR dominance verification: lazy extraction of the shared tensor view inside the elected scope, then reuse of the outer `row` name inside that scope. Explicitly deriving the shared iterator/layout before the scope and using issuer-local names resolves both. The successful final codegen used ordinary settings; line-info/stacktrace retries remain diagnostic artifacts. No native locks were removed.

Hardware/runtime: C3 B300 GPU6 on `fi-gather-opt-1029`, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTeDSL4.8.0. Native and CuTe caches remain in persistent storage. No clock or power setting changed. GPU6 is idle after the completed capture.
