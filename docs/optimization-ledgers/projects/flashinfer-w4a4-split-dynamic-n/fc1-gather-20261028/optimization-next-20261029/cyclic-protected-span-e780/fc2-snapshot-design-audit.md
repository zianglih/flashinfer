# FC2 protected-register snapshot: read-only design audit

The design is feasible with the existing output layouts: capture the protected
TMEM interval in final packed output registers, release the accumulator, then
emit output slabs in monotonically increasing token order. It removes the
rotated SIMT tail from ahead of the full TMA-store prefix. This is a proposed
mechanism, not a measured speedup or proof of the cause of the previous losses.

Source read: retained `d9dee2dae50fef5d14c609e277fbc29d48df08b4`, swap kernel
SHA256 `5037dea841027df0e3fccb4b214b2ea763408e5fd9c1233868c0356508e5cb0b`,
plus the archived wider-span `candidate.patch`. The wider-span review clone
has already been retired; its immutable gate/codegen evidence remains here.
No repository source, GPU state, tests, or benchmark results changed in this audit.

## Ownership and ordering

- `_run_bulk` supports BF16/FP16 output only, through
  `bulk_output_element_bytes`; its 128-channel CTA uses 128 epilogue threads.
  A full 64-token slab is 64 half elements/thread, or 32 registers. The native
  `Ld16x256b` fragment directly feeds `stmatrix.trans` after scaling/conversion.
- A partial slab already calls `_scale_pack_transpose` through
  `_run_token_group`. Its 32-token result is 32 half elements/thread, or
  16 registers, in the row-oriented ownership expected by the vector stores.
  This path uses TMEM scratch. **The existing transpose must finish before
  release for every protected partial slab.** It cannot be called on the
  protected interval after release.
- These layouts can share one cache of `P` half elements/thread for a protected
  interval of `P` columns. The existing full-slab predicate selects the cached
  interpretation. A native full fragment cannot be sent directly to the SIMT
  vector stores: its half pairs belong to different token rows.
- Fill the protected cache using the existing scaling, per-token metadata,
  output conversion, and partial transpose. Do not multiply or convert again
  when draining it. Then use the existing TMEM-read fence and one accumulator
  release. Any subsequent fresh TMEM loads/transposes must be outside the
  protected interval. Empty protected slabs need no load or initialized cache.
- Traverse output groups `0..groups-1`. Protected groups use their cache;
  other groups use the current load/convert path. Emit full TMA slabs first,
  then the one partial SIMT slab. A CTA with no live output channels retains
  its current direct release and does not read cache or issue zero-byte TMA.

The cache is thread-local. It needs no extra CTA barrier, mbarrier, TMEM
transpose, output workspace, metadata pass, or scheduler/PDL change. Preserve
the existing shared-output-stage wait, async proxy fence, warpgroup barriers,
and terminal TMA source-read drain. Monotonic output makes full TMA commits a
contiguous prefix again, so the old full-store-only commit policy is sound;
empty logical commits were needed for the *rotated* store order.

The earliest safe release is after the final protected TMEM load and all
protected partial-tail transposes, not necessarily after all conversion work.
For a final full slab, its register values can finish scaling/conversion after
release, preserving the current `half == 1` early-release point. Avoid adding
a conversion-before-release dependency to the P64 case simply to fill a packed
cache first. The partial path still has to finish its TMEM transpose first.

## Register and code-size boundary

| Protected columns | Packed registers per epilogue thread |
| --- | ---: |
| 32 | 16 |
| 64 | 32 |
| 128 | 64 |
| 192 | 96 |
| 256 | 128 |

**FC2 does not inherit FC1's 256-register dynamic epilogue quota.**
`setmaxregister_increase(256)` is guarded by `gather_input`; FC2 launches
256 threads with `min_blocks_per_mp=1` and has no `maxnreg`/`setmaxnreg` in the
captured PTX. Raising epilogue pressure may raise allocation for the whole CTA.
The existing gate's FC2 maximum is 154 registers, zero stack/local; the
overlapping N256/P128 subset peaks at 149. These are baseline allocations,
not live-register counts at the snapshot boundary. Adding 64 to 149 is not a
resource forecast: the cache can replace the current slab fragment and some
temporary lifetimes, while conversion/metadata can introduce other overlap.
Inspect actual generated registers and local traffic before timing.

Keep register indexing compile-time constant. For phase 0 the protected group
range is `[groups-cached_groups, groups)` and cache index is
`group-(groups-cached_groups)`; for phase 1 it is `[0,cached_groups)` and index
is `group`. A complete low/high phase branch is straightforward but may clone
the entire epilogue. Prefer one monotonic output loop, static low/high group
membership, and constant fragment views selected by phase where necessary.
Do not assume `P` divides the tile: modulo indexing happens to work for
P128/N256 but fails for overlapping low/high memberships at P192/N256.

A first implementation should keep the current register policy. If a
protected-cache footprint cannot be compiled without local traffic, reject or
reconsider the mechanism before adding quotas or model-specific exceptions.

## Source references and analogue limits

- Current swap kernel: `_store_converted` around 737; `_scale_pack_transpose`
  around 759; BF16/FP16 `_run_token_group` around 873; `_run_bulk` around 1075;
  no-live-channel release around 1288; bulk eligibility around 1601; FC1-only
  register increase around 3263.
- Project-local CUTLASS checkout `references/cutlass`, commit
  `91843b71d90737e0a9b86f7d9df213cff5a3526f`,
  `include/cutlass/epilogue/collective/sm100_epilogue_tma_warpspecialized.hpp`:
  lines 729–738 describe protected TMEM/reversed traversal; lines 880–888 load
  the protected fragment and fence/release before register visitor/R2S work.
  Lines 754–758 and 901–912 separate TMA issuing from the next register step.
  This supports the lifetime boundary, not a prebuilt wide packed snapshot or
  a performance claim for this proposed change.
- Current Rubin MegaMoE `block_scaled_swap_ab_fc12_epilogue.py`: FC2
  `__call__` around 2025–2066 releases after all subtile processing;
  `fc2_tma_store_function` around 2574 accepts a converted BF16 register
  fragment, then stages it to shared memory and issues TMA. Its separation of
  conversion and storage is useful, but its current release order is not the
  proposed early-release design.
- [CUDA 13.2.2 bulk wait semantics](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async-bulk-wait-group)
  explain why the existing `.read` wait protects shared source reuse; changing
  accumulator read order does not remove those shared-stage requirements.

## CPU proof and GPU qualification needed

`prove_fc2_snapshot.py` / `fc2-snapshot-proof.json` cover 7,716 combinations:
tile N128/N256, slab32/slab64, every slab-aligned protected span, both phases,
every live-row count, and one/two shared output stages. They verify native
full-fragment row/channel coverage, constant cache indices, no post-release
protected reads, complete live-row coverage, and monotonic shared-stage reuse.
This is an ownership model, not a compiled-kernel or numerical test.

Reuse existing exact cases with persistent alternating wide/narrow tiles,
both phases, one/two CTAs, per-token/per-tensor output scaling, BF16/FP16,
and no-live-channel second CTAs. Exercise every supported protected span and
live-row transitions around 32/64/128/192/256, especially 129/193 where the
protected interval contains a partial tail. Codegen should preserve MMA,
operand and scheduler behavior, avoid local storage, and reduce partial-tail
work before the first full TMA store. Only then compare the existing fixed
K3 TP FC2 loss cells and general decode/prefill controls.
