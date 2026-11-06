# Can the weight-cache hint avoid adjacent expert-ID reads?

Read-only audit against retained `1e69d0a39`; no production edit or GPU work.

`blackwell/moe_swap_ab_kernel.py:2305` identifies reuse across token tiles by comparing the current expert against the clamped previous and next route IDs. The hint is computed by the TMA producer once per routed work item and reused across K; startup computes it once before weight prefetch. These loads are bounded by the live route count.

The existing per-route metadata is insufficient to remove both comparisons:

- `RoutingKernel.cuh:483`, `:790`, `:1172` write `mn_limit = min((route + 1) * route_tile, expert_start * route_tile + expert_token_count)`. It is a tile-valid-row end, not the expert end. A full single-tile expert and a full tile within a multi-tile expert can have identical current route/expert/limit metadata but require different reuse hints.
- `moe_utils.py:766` allocates `expert_counts` only for routing paths that require it. Small block/dynamic-block/cluster paths may not populate that buffer. It is not part of the tuple returned at `:808`, so GEMM does not receive an authoritative expert count.
- CLC `next_work` publishes tile, expert and valid rows. Its fourth aligned info slot is unused, but publishing a precomputed reuse bit there merely moves the two reads to the scheduler; it does not remove them, and startup/static paths would need separate handling.
- Reusing the prior loop's expert cannot prove whether the current expert has multiple adjacent token tiles: static strides and CLC cancellation need not traverse adjacent routes.

Recommendation: retain the current bounded neighbor comparisons. Eliminating them cleanly requires an explicit routing-produced reuse bit or authoritative per-expert count/range, consistently emitted by all routing producers. That is a distinct routing contract change, not a local arithmetic simplification. Do not infer expert extent from `mn_limit` or add a CLC-only alternate policy.
