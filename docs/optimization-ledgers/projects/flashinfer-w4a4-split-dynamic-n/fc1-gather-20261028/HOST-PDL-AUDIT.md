# FC1 gather host and PDL contract

Base: `d35fcfda03875077b3af8455575cc1d20e866a8c`. Changes are experimental and unstaged in `flashinfer-fc1-gather-review`.

## Host handoff

`launch_gather_gemm` passes `gather_input=True`, original activation/SF pointers, original token count, and the existing expanded-to-routed metadata. `_run_blockscaled_gemm` no longer allocates or launches standalone preparation. The compiled-kernel key includes `gather_input`; the constructor receives this explicit behavior argument. Input SF is linear per original token, with four-byte alignment, while FC2 retains its prepared SF layout and sixteen-byte pointer alignment.

`launch_finalize_gemm` passes `gather_input=False`; its allocation, output layout, metadata, math options and prefetch policy are unchanged. The public launcher signatures and tactic catalogue are unchanged. `fused_moe.py` needs no edit because its swap-AB FC1 dispatch already passes original `x`/`x_sf` and the route map. W4A16 still calls the shared prepare implementation. Shared prepare, per-token quantization, legacy and Rubin paths remain untouched.

Removing the prepare call must not remove its input checks. The gather launcher now checks the same original activation/SF CUDA placement, contiguous storage, logical SF geometry, byte-valued linear SF extent, payload/SF alignment, int32 metadata and capacity contract. Checks of automatically allocated routed tensors disappear with those tensors. A CPU source-extracted audit compares 390 original/new validation cases, including a valid four-byte-aligned but not sixteen-byte-aligned SF view.

## Routing dependency

The relevant retained source establishes this order:

1. `moe_sort` in `cute_dsl/moe_utils.py` calls `flashinfer_moe_sort` on the current stream. `csrc/moe_utils_binding.cu:357` forwards `enable_pdl` to the native routing data.
2. The block and dynamic-block routing paths in `trtllm_fused_moe_routing_custom.cuh:113` and `:439` wait for their predecessor, then call `cudaTriggerProgrammaticLaunchCompletion()` **before** writing routing outputs. Their adjacent comments explicitly require downstream routing consumers to wait. Therefore a launch signal alone is not a publication of `num_tiles`, experts, row limits or maps.
3. Retained `PrepareRouted.kernel` waits at entry, then executes a device-scope release and signals FC1. That establishes completed routing ancestors before FC1's weight/scheduler roles run ahead; its payload/SF stores still require FC1's payload wait.
4. Direct gather removes that intermediate publication. For `gather_input=True`, the host sets `prefetch_weights_before_wait=False`; with PDL enabled, the existing kernel startup path consequently waits every role before the first `num_tiles[0]` read and all later metadata/payload/SF accesses. Initial barrier/TMEM/descriptor setup precedes this wait and may overlap routing.
5. `pdl_signal_at="startup"` and `publish_routing_before_signal=enable_pdl` remain set for FC1. Its activation-control warp signals only after acquiring the routing dependency, with the existing `release_gpu()` publication. FC2 can therefore retain `prefetch_weights_before_wait=enable_pdl`: routing metadata is ready while FC2 activation readers still wait for FC1 output. The per-token intermediate quantizer keeps its existing dependency chain.

No routing producer or shared prepare contract changes are required. The prototype deliberately cannot issue expert-dependent FC1 weight loads before routing completion; expert identity itself is a dependency. This limitation must remain separate from initialization overlap and from FC2's preserved weight/SF overlap.

## Device integration obligations

The kernel owner must preserve the wait-before-read order above for every gather-warpgroup lane, account for the new participants in CLC metadata and final rendezvous, and retain the existing startup publisher role. With PDL disabled, ordinary stream sequencing supplies the dependency and no GDC instructions are needed. The new input path must continue to mask invalid route rows rather than read uninitialized mapping slots. These are runtime gate obligations, not claims established by the CPU host proof.

Artifacts: `check_host_contract.py`, `host-proof.json`, `host.patch`, `host-precommit.log`, `host-receipt.json`. No GPU execution was performed by the host owner.
