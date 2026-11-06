# Host admission and uniform cache policy candidate

The admission-only patch removes the duplicated M/N/cluster rule table and moves the unchanged shared-core capability check before CUDA stream acquisition and input preparation. The core remains the sole geometry contract; the public compatibility adapters retain their dtype/output-specific checks.

The separate cache delta resolves requested policy names literally. FC1 and FC2 both select evict-first weight scales and evict-last activations. This applies across geometry, dtype, PDL state and finalize mode. It changes performance policy only: prefetch admission, pipeline ordering and buffer sizing remain unchanged. Core weight hints are a separate, coordinated delta owned by the kernel agent.

Both wrappers pass scoped pre-commit (including mypy/Ruff), py_compile and exact AST-transform checks. The literal policy test covers 288 combinations plus two unknown-policy rejections; six invalid launches reject before stream/preparation. No GPU result or retention claim is made.

Evidence: admission-only.patch isolates the semantics-preserving cleanup; uniform-cache-host.patch includes that cleanup and the host cache candidate. Before, admission-only and uniform source snapshots preserve attribution independently of concurrent core edits.
