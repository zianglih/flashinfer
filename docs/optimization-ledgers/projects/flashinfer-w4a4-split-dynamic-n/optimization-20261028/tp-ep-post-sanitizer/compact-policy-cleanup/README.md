# Compact FC2 policy and workspace cleanup

Base: `9e3cb4d5fa0f45bba7014f67e968bf04e3cffa0f`.
Retained/pushed as `fd72759b15b8d417d6c791c0382f90d14262a8e4`. The inactive review clone was removed after full tracked-file equivalence verification.
Final candidate hashes and patch are in `source.json` and `candidate.patch`.

## Decisions

- Keep one eligibility rule in `bulk_output_element_bytes`. The routing-tile cutoff of 128 and the capacity-selected 64-row/two-stage or 32-row/one-stage scratch plans predate compact output. They are not new compact-output tuning axes.
- Remove redundant routing-width checks from the K/staging planner. Express bulk accumulator overlap through the existing TMEM-capacity check and single-channel-tile ownership, rather than repeating a literal N256 condition.
- Allocate compact offsets and inverse indices together in the private `_CompactOutputWorkspace` factory. The core forwards one private workspace; the swap-AB host launcher derives the kernel layout from its presence. FC1 receives offsets for prepare but retains its original output layout.
- Remove `output_is_routed`, `compact_offsets`, and `dense_indices` from host launcher arguments, and replace the added `dense_indices` combine argument with the private workspace. Raw CuTe pointer parameters remain internal data dependencies. Public MoE APIs and autotune tactics are unchanged.
- Preserve the runtime full-slab check: a tensor store past a compact tile's last row would overlap the next tile. Preserve the original post-PDL-wait inverse-index read and validity check.

## Scope of evidence

The initial three-file policy-only audit is preserved separately; it predates the user's private-workspace request. The kernel/planner changes are identical in both revisions. Final host validation must bind the four-file workspace candidate in `source.json`.

Pre-commit passed for all four changed files. Independent planner/source review and a bounded live B300 exact/code-generation comparison qualify this as a behavior-preserving refactor; no speedup claim or replacement benchmark matrix is intended. Final GPU results and retention status will be recorded after completion.

The earlier R2 experiment shows that compact metadata on a non-bulk epilogue added decode cost. It does not establish that N64 tensor stores cannot perform well. Broadening eligibility would be a separate performance experiment and must also constrain the selected slab to the route tile; simply deleting the cutoff can choose a 64-row slab for N32.

Final qualification: 154,224 planner comparisons; 240 workspace cases and 480 bindings; 128 paired exact graph replays, eight generic combine checks, and eight public API tests passed. All 70 captured PTX/cubin/SASS pairs are byte-identical. See `gpu/RESULTS.md`, `retention.json`, and `integration-receipt.json`. Published benchmark values/plots remain unchanged and bound to their measured head.
