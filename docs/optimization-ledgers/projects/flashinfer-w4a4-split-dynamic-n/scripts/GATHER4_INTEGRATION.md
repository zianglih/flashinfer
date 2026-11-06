# FC1 Gather4 integration sketch

The task-local `gather4_snippet.py` contains the one-CTA primitive, descriptor, row-ID preparation and issue loop. It is syntax-checked, not GPU-validated. It does not modify or import MegaMoE production code. Preserve the source license attribution when incorporating code into the existing core/utils files.

## Exact in-tree precedent

All paths below are relative to `flashinfer/`:

- `flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/blackwell_genphase_sources/kernel_src/blackwell/inference/mega/tma_gather.py:35–95`: descriptor extraction and Gather4 PTX. The snippet keeps only its one-CTA, no-multicast form.
- `.../mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:562–578`: one-row TMA descriptor with `Swizzle(3,4,3)`, native activation dtype and box `(1,Ktile)`.
- The same mainloop at `:228–280`: eight-row runs and the requirement that one B row occupies exactly 128 bytes; stage-byte equality with FC2 B TMA.
- The same mainloop at `:1150–1250`: row IDs loaded once before the K loop, two Gather4 instructions per eight-row run, elected issuing thread, stage synchronization and typed B pointer arithmetic.
- `.../mega/block_scaled_swap_ab_mega_moe_kernel_gen_specialized.py:751–763`: preserve a dynamic row extent so a single-source-token tensor retains a 2D descriptor.
- `.../helpers/smem_workspace.py:392–413`: the native producer uses a typed pointer carrying the B swizzle; the gather receives `b_smem_tensor.iterator + destination_offset` before converting to a shared address.

## Invariants

| Mode | Activation B type | Ktile | Bytes per B row |
| --- | --- | ---: | ---: |
| Homogeneous NVFP4/MXFP4, SF16/SF32 | FP4 |256|128|
| Homogeneous MXFP8 E4M3/E5M2, SF32 | FP8 |128|128|
| MXFP4 weights × MXFP8 E4M3 activations, SF32 | FP8 |128|128|

Mixed W4A8's unpack applies only to weight A; B keeps native FP8. SFA/SFB preparation and MMA scale selection are unchanged by this proposal.

- B storage must retain the existing native `K_SW128` stage layout. Use the existing B iterator and native scalar units; do not reinterpret FP4 offsets as byte offsets or perform a second software swizzle.
- The shared B base is128-byte aligned. Each four-row destination advances512 bytes; each stage is `allocatedN*128` bytes. The current allocatedN values32/64/128/256 satisfy these constraints. The existing B storage alignment128 and stage lengths preserve alignment.
- The global source pointer must satisfy the TMA descriptor's alignment (current pointers assume16 bytes and Torch allocations are stronger). Source row stride in bytes must be a multiple of16. The existing K restriction gives at least32-byte row strides for FP4 and128-byte row strides for FP8.
- Use the atom's generated descriptor rather than constructing descriptor addresses manually. The mbarrier pointer is8-byte aligned, as provided by the existing pipeline.
- `col_k` is expressed in logical activation elements, as in the native producer: `k_tile*Ktile`, including FP4. Native TMA bounds handle a short final K tile without changing the expected transfer-byte count.
- Set each inactive row ID to the descriptor's source row extent so TMA zero-fills it. Do not dereference `token_mapping` for an inactive row. The first implementation should issue the complete allocated tile; omitting rows would require a matching dynamic transaction expectation.

## Existing-core placement

1. Create the Gather4 atom once in `__call__`; keep both descriptor dimensions dynamic, especially source rows at token count1.
2. Each existing loader warp owns interleaved eight-row runs: `run_index = warp + 4*local_run`. Hoist its `allocatedN / 4` source IDs before K. Divide expanded IDs by top-k exactly once. At N256 this is64 IDs per warp: check compiler uniform-register allocation/spills before retaining it.
3. Keep the existing TMA pipeline. Its warp0 producer acquires the stage and registers **all current TMA bytes plus allocatedN*128 B bytes**. A/SFA issuance can stay where it is. The four gather warps must rendezvous after that acquire/expect step and before any Gather4 instruction; an unused named barrier with128 participants is sufficient. Keep the existing cp.async pipeline for any remaining SF loads.
4. Issue all Gather4 loads against that same TMA barrier, then perform the existing SF loads and advance the shared stage state once. Gather warps do not separately arrive on the TMA producer barrier.
5. Keep the existing MMA consumer waiting on both pipelines. Pipeline tail state ownership remains unchanged; clone state when two tail methods mutate it.

An alternative first experiment issues every Gather4 from warp0 to avoid the new rendezvous, but concentrates all row IDs and issue work in that warp. It has greater uniform-register pressure, especially at N256. The four-warp version follows the native design and preserves the current128 loader-thread structure.

Before timing, the existing task-local random phase probes should cover all activation dtype families, K tails, validN less than16, routeN16 with allocatedN32, reversed routing, and N256 if enabled. No new production test file is needed.
