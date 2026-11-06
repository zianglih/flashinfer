# Shared routed preparation candidate

Base 1496b557. Working tree: `flashinfer-w4a16-prepare-review`; all production changes remain unstaged.

- W4A16 calls existing `moe_prepare.prepare` with absent SF buffers. Its old 216-line module is deleted. There is one compiled routed-copy implementation and cache.
- Absent SF buffers use `None` and zero compile-time SF columns. SF padding and scale publication compile away; payload rows remain byte-preserving BF16.
- Common vector copies use 256 bits when row stride and both pointers permit it, or 128 bits for 16-byte-aligned contiguous views. Blockscaled host validation retains the 32-byte pointer alignment promised by its GEMM wrapper.
- Initial candidate preserves 256 threads for payload-only and 128 threads when SF publication exists. This isolates consolidation from launch-policy tuning. A common launch policy can be benchmarked separately.
- Preparation waits for routing metadata and source payload before reads. After this wait, the first warp per CTA triggers the downstream grid; FC1 activation TMA's dependency wait still protects every payload/SF load. The first block publishes completed routing ancestors through the existing device release fence. No CTA/warp barrier is added. Payload and scale buffers have no intra-grid producer/consumer relationship: row copies and SF publication use registers and independent global stores. Padding has no unmasked payload consumer; zeroed SF padding remains required for TMA.
- Allocation ownership is unchanged: W4A16 reuses its caller workspace, blockscaled allocates per invocation, and compiled kernels are the only cached objects.

Scoped pre-commit, AST parse, and `git diff --check` pass. GPU validation is running using the source receipt in `deployment.json`: 32 existing W4A16 exact cases, existing MXFP public API and NVFP4 recipe cases, and a task-local 36-case byte-copy/padding/alignment harness.

Deployment helper: `../deploy.py NAME /absolute/review-copy`. It applies a small patch to remote 1496, verifies all native source hashes against the rebased reference, and reuses that reference's immutable native data and native compilation artifacts. DSL workspaces are keyed by full source identity. No AUTO timing results are reused. Optional `_build_meta.py` presence is preserved exactly; deployment-only data symlink and optional build metadata are excluded through clone-local Git metadata. Helper installation is hash-keyed and atomic for concurrent agents.
