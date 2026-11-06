# Routing → gathered FC1 PDL handoff

Read-only source audit at retained base `82254e206a44b95d9925e4594fac936731f80d21`. No implementation, GPU run, or performance claim.

**Finding:** expert/tile metadata is computed before token maps in every current `moe_sort` path. This is a real opportunity to overlap expert-dependent weight/scales loading with the final permutation-index stores. It requires a defined memory-publication boundary, not just moving a launch instruction or removing FC1's wait.

## Current path and dependencies

`moe_sort` passes precomputed TopK IDs through `csrc/moe_utils_binding.cu:357–436` → DeepSeek `run` → `runPostTopKPipeline` in `trtllm_fused_moe_routing_common.cu:44–167`. The dispatch uses all expert/topK/input configurations, not model names.

| Current route path | Trigger location | Metadata complete before token-map loop? | Existing local synchronization at that boundary |
|---|---|---|---|
| Static block, ≤4 tokens | Entry, before metadata | Yes, after custom.cuh:287 | No post-metadata barrier |
| Dynamic block, eligible ≤16 tokens / dispatched expert tier ≤512 | Entry, before metadata | Yes, after custom.cuh:617 | No post-metadata barrier |
| Single cluster, precomputed routes up to 8192 tokens | After token-map loop | Yes, RoutingKernel.cuh:510 | Existing CTA `__syncthreads` at :514; cluster wait at :519 protects DSM lifetime |
| Cooperative route, larger supported shapes | After token-map loop | Yes, RoutingKernel.cuh:1194 | Existing CTA `__syncthreads` at :1201; existing grid sync is earlier, after histogram reduction |
| Histogram + offsets fallback | After token-map loop | Yes, RoutingKernel.cuh:798 | No unconditional post-metadata barrier at this boundary |

The earlier local gather ledger correctly explained why FC1 had to wait, but its blanket description of `moe_sort` as an early-signalling kernel is incomplete for today's source: cluster/cooperative/offsets signals are already at the end. Their comments explicitly retain the complete-map signal after a prior stale-data/NaN failure. Those comments are a compatibility warning, not proof that metadata itself depends on the maps.

**Metadata-only readers:** both split backends' weight producers and schedulers use the tile count, tile→expert ID, row limit, and static shape/weight/scale pointers. They do not read `permuted_idx_to_expanded_idx` or expanded→permuted maps. W4's raw-weight dequantization also depends only on weight/SF arrival. These roles can genuinely run ahead once that smaller metadata set is published.

**Dependent readers:** the FC1 gather warpgroup reads the token map to form input addresses, so it must retain the complete routing dependency wait. Epilogue/combine consumers must preserve their existing payload/map dependency chain. Both kernels already initialize their descriptors, pipeline barriers and TMEM before the current FC1 dependency wait.

## Minimal possible publication design

One uniform contract could publish expert/tile metadata before the token-map loop in all paths:

1. Every metadata-writing thread performs a device-scope release/fence after its metadata stores.
2. All threads reach a CTA rendezvous before that CTA triggers its dependent launch. Reuse the existing cluster/cooperative CTA barrier. The small-block and offsets paths would need one local barrier at this boundary. A trigger issued by an early thread before the other writers finish is insufficient.
3. Each CTA triggers once at this boundary. The PDL launch condition already waits for all producer CTAs to trigger or finish, so no additional grid counter, global barrier, kernel, or public argument is inherently needed.
4. FC1 weight/scheduler roles may read only the published metadata. Token-map/input readers still call the full grid dependency wait. Keep the current FC1→FC2 full-routing publication role until its downstream requirements are separately proved.

The CUDA runtime documentation explicitly says the trigger itself has no memory-visibility guarantee and permits a correctly scoped fence to supply visibility. The programming guide likewise requires a dependency wait or another availability proof. See [CUDA PDL guide](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html) and [CUDA Runtime API](https://docs.nvidia.com/cuda/archive/12.4.1/pdf/CUDA_Runtime_API.pdf). The existing `release_gpu()` before FC1's dependent signal is the same category of publication, but the sort's multiple metadata writers need their own ordered collective boundary.

For swap-AB, the existing `prefetch_weights_before_wait` role split already distinguishes metadata-only weight/MMA/scheduler work from the activation-control and payload warpgroup waits. After sort publication is established, that existing machinery could serve gathered FC1 without another mode or state machine. W4 currently places the full gather-input wait before role specialization; it would need the wait scoped to token-map readers while keeping a separate safe publication role for FC2. This is more than flipping its one condition, but does not require another producer ring or public knob.

## Why this is not yet an approved source change

- These C++ routing kernels are shared by legacy CuTe DSL, Rubin, TRTLLM routing, and other callers. Moving cluster/cooperative signals before maps would weaken their existing signal timing. The legacy Blackwell CuTe DSL gather implementation (:1579), Rubin gather implementation (:1731), and visible TRTLLM permute kernels in trtllm_fused_moe_dev_kernel.cu contain full dependency waits before map-dependent work, but that alone does not qualify all other consumers, especially generated TRTLLM GEMM kernels. Their map loads must be audited before changing the shared contract. Do not hide this risk behind a runtime shape branch.
- A release only on thread 0 or a trigger before the existing barrier would not prove that every metadata writer has published. The current small-block early trigger also must be removed/repositioned; a second late trigger cannot revoke an earlier launch.
- This sacrifices early prologue overlap for the ≤16-token block paths while allowing earlier expert-specific work on paths that currently signal at exit. All token sizes need matched measurement; the sign of the end-to-end effect is unknown.
- Earlier weight traffic can compete with input activations in L2. Retain the established cache-policy hierarchy and measure the whole chain, including input quantization when enabled. No extra prefetch depth/tactic axis follows from the handoff itself.
- PDL overlap is opportunistic, not guaranteed. The routing kernel must always be able to finish independently of FC1; no cross-grid resource dependency should be introduced.

The clearest next design decision is whether to strengthen the *shared routing publication contract* after auditing every consumer. If that scope is undesirable, keep today's FC1 wait. Adding a bespoke readiness counter or a second routing API would cost more complexity than this opportunity currently justifies.

Historical references checked: `fc1-gather-20261028/{HOST-PDL-AUDIT,INDEPENDENT_AUDIT,HOST-HARNESS-REVIEW}.md` and `optimization-next-20261029/pipeline-audit.md` in the prior project. They contain no retained/timed implementation of this intermediate metadata publication.
