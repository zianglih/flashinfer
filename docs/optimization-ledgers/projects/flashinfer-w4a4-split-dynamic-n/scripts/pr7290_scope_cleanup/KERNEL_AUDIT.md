# PR7290 kernel scope audit

Compared the retained implementation at `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e` against base `a65d5b09e7e4c4c5c160b0161c48becd100b3970`. Cleanup edits are in the independent `flashinfer-pr-scope-review` checkout, initially unstaged. The replacement architecture remains intact.

## Scope read

- Complete new Blackwell shared grouped-GEMM core, FC1/FC2 capability adapters, and shared epilogue.
- Complete routed input preparation and deterministic combine, plus W4A16's changed input-layout handling.
- Traced host call configurations to distinguish supported geometry and compile-time policy from unreachable historical paths.

## Findings fixed

1. The cross-CTA cp.async SF relay is unreachable: two-CTA geometry only permits N128/N256, and those geometries always use canonical SF TMA. Removed relay pipeline construction, state, waits, releases, drains, and shared barriers.
2. Removed an empty `producer_gather4_issue` iKET range left by the old activation gather implementation. All active trace ranges remain.
3. Removed unused `activations` and `weights_sf` kernel arguments, unused `tiled_mma` and `expert_idx` epilogue arguments, and never-read shared-core `mma_tiler`/`use_per_token_scale` fields. Checked all call-site arities statically.
4. Removed redundant B-TMA placeholder assignment and divide-by-one in byte accounting.
5. Routed payload copying already occurs under `if valid`, with full 256-bit coverage guaranteed by the existing 32-byte row-alignment requirement. Removed the duplicate valid branch and zero-fill that was overwritten by the full load. Fixed spacing in its alignment diagnostic.

## Shared-memory impact

The deleted relay reserves `16 * num_stages` bytes before 128-byte alignment. The accounting formula changes from

`round_up_128(8*(6*num_stages + 2*acc_stages) + 4) + 128`

to

`round_up_128(8*(4*num_stages + 2*acc_stages) + 4) + 128`.

For the production stage counts 3/4/5 and accumulator stage counts 1/2, metadata totals change respectively 384→256, 384→384, and 512→384 bytes. Kernel `num_stages` is selected by the host before this calculation and therefore cannot change. Every production operand allocation and the two bulk-epilogue thresholds (8,704 and 34,816 bytes) are multiples of 512 bytes; old/new metadata have the same 512-byte ceiling, so this deletion cannot change bulk token or stage selection. `kernel_layout_audit.py` checks this using actual CuTe-generated layouts for all 90 dtype/FC1/FC2 tactic policies.

## Active-path audit

No additional high-confidence indexing, arithmetic, or synchronization bug found by static inspection. Checked:

- Runtime N descriptor rounding, physical N32 scratch for logical N16, two-CTA activation row offsets, channel tails, and canonical SF offsets.
- Operand byte accounting for mixed FP4/FP8 storage, K tails, scale-copy completion and async shared-memory proxy fencing.
- Accumulator windows and scale TMEM footprint, protected-column release before reuse, including skipped token slabs and inactive second-CTA channel tails.
- Gated up16/gate16 lane ownership, per-token scaling order, SF16/SF32 absmax ownership, and output copy alignment.
- Producer drains on independent pipeline-state clones and PDL startup/producer-exit handoff boundaries.
- Routed payload masking and physical SF zero-fill; deterministic combine's masked routes, ordered first-slot multiply/subsequent FMAs, and vector tails.
- W4A16's removed decode permutation is necessary because the prepared weights now directly supply up16/gate16 order.

Static inspection is not a substitute for GPU validation of the resulting source. Parent task owns focused compile/runtime validation and final commit/publication; this audit does not claim sanitizer or full matrix results.
