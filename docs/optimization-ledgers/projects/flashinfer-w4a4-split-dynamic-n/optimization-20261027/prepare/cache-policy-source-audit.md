# Independent cache-policy audit

Read-only review of `flashinfer-cache-scales-perf-review`; no edits or GPU work.
No correctness blocker found in the current dynamic routed-reuse policy.

- **Bounds:** `weight_cache_hint` receives only live route indices. Startup is
  guarded by `first_tile_valid && first_tile < num_tiles[0] * total_m_tiles`;
  static block indices and valid CLC initial coordinates are nonnegative.
  The regular producer invokes it only inside `while tile >= 0`. Static work
  checks total tiles in `next_work`; CLC publishes only `route < num_routed_tiles`,
  otherwise skipping padding or publishing the negative terminal sentinel.
  Consequently `num_routes > 0` whenever the helper runs. For live route `r`,
  `min(r+1,n-1)` and `max(r-1,0)` both stay in `[0,n)`, even though boolean `&`
  eagerly loads both sides. A singleton reads its own in-bounds entry and both
  neighbor predicates are false. No speculative read touches allocation padding.
- **Routing contract:** native `moe_sort` binds `tile_idx_to_expert_idx` to
  `mPtrCtaIdxXyToBatchIdx` (`csrc/moe_utils_binding.cu:388`). All three routing
  writers assign an expert to its contiguous CTA range (`RoutingKernel.cuh:473`,
  `780`, `1162`). Neighbor equality therefore detects whether the same expert
  has another token tile. Different channel tiles reference different weights;
  the policy does not mistake channel tiling for token reuse. CLC execution order
  does not alter this logical metadata layout.
- **PDL:** both new neighbor reads use the already-published routing metadata
  prerequisite that permits startup weight prefetch. The policy does not read
  activation payload early or require a new wait/barrier.
- **Generality:** actual routing reuse selects normal versus evict-first for
  both weights and scales; activations remain evict-last. No model, dtype, K-step,
  token threshold, cluster-size or tiler branch is added. Recomputing once per
  routed work item is necessary because graph replay can change routing.
- **Arguments/cache:** obsolete `weight_scale_cache_policy` was removed from
  `_run_blockscaled_gemm`, its compiled key, the private kernel constructor and
  both FC call sites. A repository search found no remaining Python references.
  The only kernel construction is the private wrapper; activation policy string
  validation remains explicit. Public API and autotune tactics are unchanged.
- **Resource policy:** warp0 alone computes the hint and owns both TMA loads;
  other producer warps do not acquire additional ownership. The hint is loop
  invariant across K stages and is reused for startup-prefetched stages.

The incidental final-blank-line deletion in `moe_swap_ab_kernel.py` is resolved;
the restored file matches the audited SHA256 below.
Performance remains the combined campaign's decision; this review establishes
source bounds and policy generality, not speedup.

Audited source SHA256:

```json
{
  "flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab.py": "9f094f2b254b943bd7cdbb89906bb708541c5ce2d2a08ecb196300951bb94ff7",
  "flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py": "7416653446acc6a96d98bc0336d108ffdcba73673aa531b2f2c0b7423b2493fa"
}
```
