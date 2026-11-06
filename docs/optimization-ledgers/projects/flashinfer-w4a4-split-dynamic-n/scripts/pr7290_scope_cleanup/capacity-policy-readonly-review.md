# Independent read-only capacity and V41 review

No high-confidence correctness defect found in the reviewed source.

- Capacity policy changes shared-memory stage count and scratch selection only. Producer/consumer indices, acquisition/release points, tail drain copies, accumulator staging and TMEM ownership are unchanged.
- Metadata accounting covers A/AB/accumulator barriers, the TMEM handle, alignment before epilogue scratch, and the deallocation barrier plus padding before operands. Operand layouts are recomputed at selected depth and final `SharedStorage.size_in_bytes()` is checked.
- BF16/FP16 bulk scratch formula is identical to the former formula. Reserving the wide two-stage epilogue slab before filling operand stages is an intentional throughput policy, whose retention still requires measurements.
- Non-overlap producers stop to run their epilogue between tiles; bounding stages to ceil(K/tile_k) there is consistent. Dedicated epilogue warps permit cross-tile prefetch, so no artificial K-iteration cap is needed there.
- Reduction size is a compile-time weight shape and part of the compiled-kernel cache key. `num_stages=None` is resolved during compilation; routed capacity and token count remain runtime shape arguments.
- Mixed MXFP4/MXFP8 counts expanded Int8 weight storage and both scale layouts. Two-CTA/channel-tile scale footprints and accumulator allocations remain unchanged.
- V41 all four TRT precisions share the same cached model routes via routed APIs and a common activation materializer. CuTe wrapper/functional/MX FC1 explicitly forward the scalar clamp; the MX autotuning cache includes it.
- CuTe tuning marks route IDs/weights dynamic and allocates new tensors before applying its routing initializer/pre-hook. It does not overwrite cached V41 routes. The normal forward/sort kernels read these inputs.
- V41 routing is untimed CPU sqrtsoftplus with unbiased normalized weights, scale1.5, and stable lower-ID tie order. The same cached tensors are used for histogram and all backend calls. V3 preserves its timed fused router.

Boundary: source review and local AST/recording-stub checks only. No GPU execution, numerical guarantee, profiler result or performance retention is inferred from this review. Other agents own runtime validation and paired timing.

Reviewed file hashes:

- `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`: `9b75063e19b70890f6bbec5ba97998de8147896a7f46832f20693d6bef928a58`
- `flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py`: `8e5181ec51a77be8ebfb2f02ca76b47463b982558ce96a8e7fd02faa4aed5ab6`
- `flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`: `2dd1a9ef4a00b418a4cf151ee01f8e3a6c8c76c5946e2559a4be76076f9ca238`
