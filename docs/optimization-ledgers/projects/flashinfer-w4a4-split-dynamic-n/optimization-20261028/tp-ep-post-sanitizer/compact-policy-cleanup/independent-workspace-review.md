# Independent compact-output workspace review

Result: **pass, source-only**. The reviewed four-file patch is bound by
`independent-workspace-review.json` and `independent-workspace-reviewed.patch`.
The prior `independent-source-review.json` describes the earlier host revision;
it is not the receipt for this workspace revision.

The private `_CompactOutputWorkspace` owns both prefix offsets and dense row
indices. `_get_output_workspace` contains the unchanged eligibility call and
the same two `torch.empty_like` allocations formerly in `_moe_core_impl`.
The core passes one owner through the launch sequence instead of independently
configuring two metadata tensors and a routed-output boolean. This matches the
existing SM100 W4A16 private dataclass/factory pattern in `moe_w4a16.py:49–92`.

The private `_output_workspace` argument on `moe_unpermute` is appropriate here.
This finalizer is an internal module helper, is not exported by the CuTe DSL,
Blackwell or fused-MoE package initializers, and no public wrapper or functional
API gains an argument. A second private implementation plus a forwarding wrapper
would add indirection without protecting an existing public contract. The generic
finalizer needs only `.indices`; it does not import the swap-AB host module or
depend on its allocation policy. Individual pointers in the compiled kernel ABI
remain necessary data dependencies, not user-selectable behavior flags.

For valid production calls:

- FC1 receives the workspace so prepare can write offsets. Its
  `scatter_output=False` still makes `output_is_routed=False`, and its GEMM
  receives neither compact offsets nor dense indices.
- FC2 receives the same workspace, derives routed output from its presence, and
  receives the same two metadata pointers as before. Fused output remains
  ineligible and rejects an explicitly supplied private workspace.
- Combine uses the same dense-index tensor. The kernel still prefetches original
  mapping validity before the PDL dependency wait and reads dense indices only
  after that wait. No publication, row-bound or output arithmetic changes.
- The owner remains live through combine in the same invocation and stream.
  Tensor allocation shapes, dtypes, device and graph allocator ownership are
  unchanged. Legacy and W4A16 callers use the default `None` path.

`audit_workspace.py` verifies identical ASTs for the host pointer tuple, cache key,
kernel constructor, launch argument tuple, tile-K selection and eligibility call.
The finalizer body after its one workspace-unpack assignment and its entire GPU
class are AST-identical. W4A16 and prepare source are byte-identical. The separate
kernel/planner equivalence review still applies because its reviewed kernel hash
is unchanged.

No repository source changes or GPU jobs were performed by this review. Existing
project-local observation harnesses that inspect launcher metadata must read the
private workspace fields; repository tests and scripts have no old
`dense_indices=` host calls to migrate. This source review does not substitute
for the separately owned GPU qualification or a timing claim.
