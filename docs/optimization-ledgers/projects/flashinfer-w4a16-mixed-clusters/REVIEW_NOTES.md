# Mixed-cluster implementation review

## Established paths reused

- SM100 GenPhase's mixed TMA atom selection and `PipelineTmaUmmaMixedCga`.
  These helpers are byte-identical to the Rubin snapshot. Public shim exports
  preserve the `kernel_src/src` vendoring boundary and load only for mixed code.
- GenPhase's `FixedGroupMixedCgaAtomicCounterWorkIdState` registration and
  handoff protocol. Two physical fallback clusters share one logical work ID.
- CUTLASS `HardwareInfo.get_max_active_clusters` and Rubin's whole-logical-tile
  occupancy arithmetic; this preserves complete two-CTA MMA pairs.
- Existing W4A16 raw-weight/dequantization, BF16 handoff, epilogue, token return,
  and exact reference paths.

## Fixed before GPU testing

- A zero fallback count must normalize to uniform four-CTA construction.
- Uniform AUTO candidates must explicitly clear a prior fallback cluster shape.
- Zero preferred occupancy is rejected before launch, matching Rubin's contract
  instead of allowing a zero grid or silently changing logical tile geometry.
- Padded FC2 channel CTAs still publish done and must remain in the matching
  completion threshold. FC1 masks padded done signals. The original distinction
  is preserved rather than substituting an unpadded FC2 count.

## Independent kernel review

No additional actionable defect found; confidence remains bounded by device
validation. Read descriptor partition/selection, actual-cluster UMMA arrival
counts and masks, static/atomic fallback ownership, initialization order,
workspace reset, physical dispatch IDs, and padded completion accounting.
The raw-weight, transform, and accumulator pipes remain local to each MMA pair;
only activation B multicast dependencies span both pairs in preferred four.

The scheduler-only GPU audit passed actual mixed placement and forced fallback,
but cannot establish full-kernel TMA transaction/layout correctness. Full-kernel
tests must include fallback execution, padded dimensions, N32/N64/N128,
static/atomic scheduling, empty/refill rounds, and repeated graph launches.
All performance evidence must use AUTO sweeps, as directed by the user. The
current project harness compares baseline original AUTO16 against an optimized
arm restricted to new mixed4+2 candidates. This restriction is project-only;
the product catalog retains its uniform candidates. Fixed geometries are used
only for untimed compile/liveness or deferred numerical qualification.

## Focused follow-up: registration, tails, uniform path

Read-only review on 2026-10-24 of candidate2 kernel SHA256
`87839cd3b1c4d68bbaf83c44a3f9838f0d1c3875764187cbe3f2b45f99388fb4`,
including the current local host changes. **No additional P0/P1 finding.**
This is source reasoning; no new GPU validation or performance claim.

- **Registration bound:** grid `(4,1,Z)` has `4Z` CTAs, so at most `2Z`
  physical fallback clusters can register. `fallback_group_capacity=2Z`
  allocates one Int64 token per possible member, and the helper addresses
  `2*group_idx + member_idx`. Remaining physical fallback clusters always form
  complete pairs because total and preferred CTA counts are multiples of four.
  The capacity does not depend on the host-predicted number actually placed.
  See kernel constructor and `_build_local_region_specs`, and
  `work_id_claim.py:503`/`:547`.
- **Reset lifetime:** frontend zero-initializes the entire local workspace.
  Registration and group-token regions precede `l1_token_buffer`, so both fall
  inside `local_zero_i32_count`; `kernel_tail_cleanup` clears that prefix after
  role retirement and the grid drain. Int64 tokens are cleared through both
  Int32 halves before the next stream-ordered launch. No new per-forward host
  memset is needed. Empty workloads still run registration, sentinel/drain,
  and tail cleanup.
- **Padded work:** scheduler work validity is per logical work ID, preserving
  all four channel CTAs in each logical tile. FC1 only publishes for real
  64-channel output slices, matching threshold `ceil((2*intermediate)/128)`.
  FC2 suppresses out-of-range stores but all four logical CTAs publish to the
  dispatch-return counter, matching `ceil(hidden/512)*4` per token tile for
  M256 cluster4. Filtering padded work earlier, or changing only that FC2
  threshold to an unpadded count, would break the existing contract.
  See `epilogue.py:222`, `:240`, `:406`, and kernel constructor.
- **Uniform path:** <=2-CTA launch arithmetic and early atomic preclaim remain
  unchanged. Mixed-only storage, runtime geometry, executable B atom selection,
  and registration are behind compile-time branches. Uniform B TMA still uses
  its original copy/acquire/commit/advance path. F=0 normalizes to uniform4
  without mixed registration. This is a source-level preservation check, not
  proof of identical generated machine code.

Moving mixed-atomic registration earlier is dependency-safe after cluster init
and warpgroup register donation: initialization changes only its registration
counter, DSMEM broadcast phase, and fixed group/channel coordinates. It does not
touch the work counter, group-token payloads, generations, expert sizes, or
FC1/FC2 readiness. Any future move must execute it exactly once and keep static
tile decoding after metadata readiness. The first work claim still follows the
metadata wait. This is an optimization observation, not a defect in current code.

The narrow fresh-AUTO cache bypass and exact host test names are recorded in
`AUTO_CLUSTER_CAPABILITY.md`; non-AUTO cache behavior remains unchanged. The
new host-only changes still await final source sync/qualification.
