# Additive-mode compatibility cleanup

Published head: `e25af36cea727cf473dfea72b6d9630c28f0b8d8` (one commit over `002529e17b22567a071091053c6c4dc2a55e050e`). The existing archive PR #7 is unchanged.

The user clarified that preserving old functionality does not require freezing old source: useful universal optimizations stay shared. There is one public per-token quantizer, with optional `valid_rows`, `row_limits`, and `rows_per_group` metadata. The temporary duplicate quantizer/finalizer files were removed before publication. Shared combine and quantizer optimizations remain included.

W4A16 retains compile-time M/K, complete compile-cache identity, and elected-producer shared-metadata publication without redundant warp synchronization/async-proxy fences. Both layout modes retain the same upstream 23 tactics, filter, default, and scheduler heuristic. The kernel layout constructor option defaults to legacy 64 rows for compatibility. One shared preparation implementation keeps the original BF16/alignment acceptance domain while retaining the common early PDL publication.

Swap-AB retains the earlier 360 ordered candidates, filters and default: five route tiles, three FC1 geometries, three FC2 geometries, four K-depth pairs, and one shared FC1/FC2 CLC Boolean. Explicit NVFP4 tactics retain their earlier structural acceptance instead of being restricted to the AUTO list. MX explicit tactics retain candidate canonicalization.

Legacy False preserves the old block-scaled kernels and dispatch, preparation without a new architecture restriction, dtype acceptance, hash/cache identities, and direct runner construction without backend-specific options. Stronger swap-AB weight checks apply only to True. An MX SiTU documentation note now states the explicit mode requirement.

The exported per-token kernel class preserves its original positional call arguments; new launch/metadata arguments are optional at the end. Its normal host wrapper still passes the bounded persistent-grid size. Metadata and inputs are read after the PDL wait, including standalone use before FC1. Consumer waits protect outputs after early launch signaling.

Review was source-only. No imports, compilation, tests, lint, formatting or GPU benchmarks were run. Git hooks were disabled. The source tree was compared between the active review copy and canonical clone before publication, then the review copy was bumped to the pushed commit without discarding work. Both FlashInfer copies are clean. SGLang's demo remains unstaged and unpublished.

The PR body retains all 23 raw benchmark/test blocks, including six family tables and sixteen legacy/current CSV blocks, unchanged. It identifies the evidence as historical, retains the repository checklist, and updates the current scope, tactic policies, validation boundary, and diff counts (+6,385 / -1,054).
