# Swap-AB compile-time MMA handoff

Read-only proposal against canonical `fd72759b15b8d417d6c791c0382f90d14262a8e4`.

`num_k_atoms` exists only in `moe_swap_ab_kernel.py`: the private `_blockscaled_dynamic_mma` emitter argument, the compile-time peeled stage calculation, and two calls for the first/optional second channel tile. It is absent from public APIs, wrappers, caches, tactic tuples, producer configuration and shared synchronization state.

Replace the emitter arguments `(cta_group, num_k_atoms)` with `(tiled_mma, stage_k)`, retaining the same argument count. The caller passes the logical extent of the acquired stage (`self.tile_k` for the full section, `tail_k` for the peeled section). The emitter derives CTA group and native atom K from the existing MMA object:

```python
cta_group = cute.size(tiled_mma.thr_id.shape)
atom_k = cute.size(tiled_mma.shape_mnk, mode=[2])
mma_k = cute.ceil_div(stage_k, atom_k) * atom_k
widths = (
    (96, 96) * (mma_k // 192) + (64,) * ((mma_k % 192) // 64)
    if use_k96
    else (0,) * (mma_k // atom_k)
)
```

This removes caller `atoms_per_stage`, `atom_k`, and `num_k_atoms` calculations. All new calculations are Python/static DSL values. It adds no per-atom predicate, runtime arithmetic, kernel argument, synchronization or tactic.

The bundled primary CUTLASS helper `cutlass/utils/blackwell_helpers.py::_make_blockscaled_trivial_tiled_mma_impl` explicitly creates K64 FP4 atoms and K32 mixed/MXFP8 atoms; `MmaAtom.shape_mnk` exposes this static geometry. `TiledMma.thr_id.shape` already supplies CTA-group geometry elsewhere in this kernel. These are stronger sources than decoding dtype/instruction strings or the fragmented A tensor: the K96 path receives raw SMEM tensors while the ordinary path receives descriptor fragments.

K96 remains a special native instruction contract already selected by `use_k96`; the existing K64 SDK atom continues to describe the partition geometry. Its arithmetic sequence is unchanged: every acquired stage resets its 96/64 plan, and SF addressing/descriptor generation still consumes the same sequence. Valid K is admitted in units of 64 for NVFP4 and 128 for SF32, so the direct K96 plan exactly matches the previous `num_k_atoms * 64` expression. Do not merge adjacent stages or change the exact reference traversal.

Validation should compare paired emitted PTX/SASS for ordinary K32, FP4 K64 and SM103 mixed K96/K64, including aligned and partial final stages, both CTA groups, both channel-tile counts, and a nominal N256 narrow tail. Existing exact gates need no reference changes; require identical update sequence/resource/synchronization counts and ideally identical normalized SASS. This is a handoff cleanup, not a performance optimization.

An alternative static fragment trim would encode the live count in a new layout, but adds layout reconstruction and must handle raw versus descriptor representations separately. It is unnecessary for this bounded cleanup.
