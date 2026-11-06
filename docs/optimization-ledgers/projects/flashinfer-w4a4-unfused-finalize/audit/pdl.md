# PR 5319 synchronization audit

Audited source: `ca2692a62679336301758d1b83b193b3c5b1170c`, compared with `eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095`. Read `flashinfer/AGENTS.md`, `CLAUDE.md`, and `docs/code_review_guidance.md`. This is an independent static synchronization review, not a new GPU run.

## Result

No substantiated synchronization correctness defect introduced by this PR. Confidence is high for the explicit PDL ordering, metadata readiness, and masked-work coverage. Existing GPU evidence remains necessary for compiler lowering and architecture-specific behavior; this review does not extend its hardware scope.

## Contract checked against primary documentation

CUDA PDL permits a dependent grid to start after every prerequisite CTA has either signaled or finished; one elected signaling lane per CTA is sufficient. The signal does not publish unfinished producer output. The dependent wait must precede reads of that output and waits for prerequisite completion and memory visibility. Repeated signals within a CTA have no additional effect. Overlap is opportunistic and must not be required for forward progress.

Sources: [CUDA Programming Guide, Programmatic Dependent Launch](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html), [PTX ISA 9.2, griddepcontrol](https://docs.nvidia.com/cuda/pdf/ptx_isa_9.2.pdf).

## W4A4 per-tensor path

1. `fused_moe.py:377-386` calls `moe_sort` without overriding its default `enable_pdl=False` (`moe_utils.py:527`). Thus routing metadata and the caller's scales are ready before the following FC1 grid can begin. FC1 does not modify the mapping or routing scales.
2. FC1 uses its existing PDL input wait and tail launch signal. FC2's existing unconditional `griddepcontrol_wait()` is at `blockscaled_contiguous_grouped_gemm_finalize_fusion.py:1454`; the new elected MMA-warp launch signal at 1458-1461 follows it.
3. The new trigger is outside all per-tile loops and validity predicates. Every launched CTA reaches it, including clusters that have no local routed work. The existing cluster/CTA initialization synchronization remains ahead of it. No producer acquires a new dependency on the finalizer.
4. FC2 may continue its accumulator and epilogue pipelines after signaling. Its bulk-copy group commit/wait and epilogue synchronization remain unchanged at 2235-2237. The new finalizer must, and does, wait for the whole prerequisite grid before reading any FC2 output.
5. The existing unconditional tail signal at 2262 remains harmless. It is useful for unchanged fused behavior; repeated signals in the unfused specialization are not a correctness defect.

## W4A4 per-token path

The same sort and FC2 argument applies. Between FC1 and FC2, `fused_moe.py:445-460` invokes the existing per-token quantizer with the same PDL flag. The quantizer waits before input reads and signals after its work (`quantization/kernels/nvfp4_quantize.py:965-966,1073-1074`); FC2's wait protects both the quantized intermediate and its per-token scale. `convert_sf_to_mma_layout` only rearranges the tensor view for this path. None of these steps writes the finalizer's mapping or routing scales.

## W4A16 path

1. Unlike W4A4, `moe_w4a16.py:419-428` passes the PDL setting into sort. Therefore the W4A4 non-PDL-sort argument must not be copied to W4A16.
2. The native permute kernel executes `cudaGridDependencySynchronize()` before reading any sort output (`csrc/nv_internal/tensorrt_llm/kernels/cuteDslKernels/moeUtils.cu:79-80`). Its launch signal is after the routing loop, outside all valid-route tests (101-102). This covers even an all-nonlocal EP shard: the loop may be empty, but its dependency wait and signal still execute.
3. FC1 launches after that permute signal. Its scheduler and static-weight loader can prepare work before the activation warp waits for permute. Their routing metadata is already safe because every permute CTA that makes launch possible has waited for sort. FC1's existing early weight-warp signal remains unchanged at `moe_w4a16_kernel.py:1470-1472`.
4. FC2 retains the same scheduler/weight preparation. Its activation warp obtains initial tile metadata, then performs its existing PDL wait at 1397-1398. The new elected launch signal at 1401-1405 follows this wait and precedes the work loop at 1407. In particular it is not conditional on `work_tile.is_valid_tile` and therefore covers zero-work CTAs and all-masked EP shards.
5. This after-wait placement means the finalizer can read completed routing metadata in its preamble while FC2 continues, and its own wait protects all expert-output reads. The trigger cannot require FC2 output completion because it is only permission to start independent work.
6. No TMA/accumulator/epilogue tail was removed. The unfused TMA output path still calls `c_pipeline.producer_tail()` at 2334-2335. The old MMA-warp tail signal is now fused-FC2 only at 2337-2342. FC1 and fused FC2 behavior are otherwise unchanged.
7. W4A16 reuses the permuted input workspace for FC2 output only after FC2's activation wait has waited for FC1 completion; moving the launch hint does not move any output write or remove that wait.

## New finalizer

- `moe_finalize.py:114-121` preloads only routing rows and scales, both independent of FC2. No expert-output address is dereferenced here.
- Every thread executes the conditional PDL wait at 123-124 before the first expert-output load at 139. There is no route-dependent branch around the wait. No CTA barrier is needed because each thread consumes only its own scalar metadata and writes disjoint columns.
- Mapping sign is checked before reading expert output. Expanded mode uses mapping only for validity; permuted mode uses the actual nonnegative row, including valid row zero. All-masked tokens still take the wait and write zero without reading uninitialized FC2 rows.
- Output stores occur before the finalizer's tail signal. Any PDL-enabled consumer still needs its own dependency wait, as it did with the old native finalizer. A non-PDL consumer retains ordinary stream ordering.
- With `enable_pdl=False`, launch serialization substitutes for the omitted finalizer wait. No overlap is required for correctness or progress.
- A zero-token direct helper call returns without launching an invalid zero-sized grid. This is a helper behavior claim, not a claim that the full MoE API supports every zero-token configuration.
- There is no new Rubin unfused support: the FC2 wrapper rejects `use_fused_finalize=False` for Rubin (`blockscaled_contiguous_grouped_gemm_finalize_fusion.py:263-280`). W4A8 also rejects unfused finalize in `_moe_core_impl`. The shared helper does not accidentally expand those supported paths.

## Performance opportunities and cleanup

- The new W4A16 hint intentionally begins finalizer setup only after the activation warp waits for FC1. Moving it earlier to the static-weight side might overlap a little more setup, since metadata is already established by native permute. That is a future measurement hypothesis, not a demonstrated bottleneck or requested correctness repair; an earlier signal can also extend finalizer residency and contention. Keep the current clear after-wait boundary unless a controlled profile demonstrates a benefit.
- Removing or restricting the W4A4 old tail signal would reduce redundant instructions in the unfused variant, but PTX defines these as harmless. This is too small and unmeasured to justify changing a validated kernel solely for cosmetic symmetry.
- The new finalizer's public-looking docstring should keep its independent-metadata precondition explicit: it cannot safely be called on arbitrary unfinished mapping/scales and rely on its later wait. Both current callers satisfy the precondition.
- Do not describe this change as fixing a previous metadata race. The predecessor W4A16 chain already makes routing metadata ready through native permute; this PR changes scheduling and finalization implementation.

## Validation boundary

No sanitizer or new GPU run was performed for this audit. The source proof covers the new ordering and preserves existing producer tails; it does not certify all pre-existing cluster, TMA, or scheduler code. The PR's B300 PDL-on/off and graph replay checks provide complementary empirical coverage. Unmeasured architectures, original single-sweep variance, and finalizer occupancy/contended overlap need to remain stated limitations.
