# Two-warpgroup NVFP4 weight-decode audit

Audit date: 2026-10-08. Read-only source review; no GPU tests or fresh profiling.

Primary source snapshot: FlashInfer `bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4`, archived in `evidence/weight-layout-current/`. `SPLIT` below is `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`; `UTILS` is sibling `moe_w4a16_utils.py`; `MEGA` is `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py`. URLs use this immutable commit.

## What exactly is split between the groups?

- Split kernel roles are explicit at SPLIT 153–164: four epilogue warps (0–3), one MMA warp (4), scheduler (5), weight TMA (6), activation TMA (7), and two transform warpgroups (warps 8–11 and 12–15). Thus the decoder alone is eight warps / 256 threads; the complete CTA has 16 warps / 512 threads. Do not call the whole kernel a two-warpgroup kernel.
- Each decoder group computes its group ID from `(warp_idx - 8) // 4` and resets its local thread index to 0–127 (SPLIT 1587–1618). Both groups execute the same transform program and handle different data.
- `_setup_transform_partitions` obtains the TMEM-store-compatible copy partition, counts the transform blocks in mode 3, asserts divisibility by two, and divides source and destination by the same two-way block tiler (SPLIT 337–374). It applies exactly that partition to the matching E4M3 scale source (386–389). This is a split of each K tile into two disjoint halves, NOT one group for gate and one for up, not an FC1/FC2 split, and not alternate tiles assigned to the two groups. A K256 tile is decoded as two K128 halves. Complete NVFP4 scale blocks stay intact: each fragment is required to be a multiple of 16 values (409–424).
- The groups have matching work and arrival contracts. The last group to finish a decoded tile controls when its consumer can proceed; avoiding imbalance is part of keeping the BF16 tensor-core pipeline fed. This is a source-based scheduling explanation, not an isolated benchmark attribution.
- Do not invent a scalar lane-to-element formula in the article. The authoritative per-thread addressing is generated from `tcgen05.make_tmem_copy` and the composed source/destination layouts. An archived installed CuTe DSL 4.7.1 helper at `/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/candidates/w4a16_n256_activation_width/execution/installed-dsl471/mixed_input_helpers.py:113–198` confirms that the destination TMEM copy defines the source partition and local 0–127 thread mapping. The blog can explain the two half-tiles without reproducing the full generated layout.

Source links:
- [Roles](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L153-L164)
- [Matching source/destination/scale partition](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L337-L424)
- [Group and local-thread mapping](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L1587-L1618)

## Memory path and native arithmetic

The path is HBM packed E2M1 + E4M3 block scales → TMA → raw shared-memory ring → decoder registers → operand TMEM → BF16 MMA. BF16 activations have their own TMA/shared-memory pipeline. Full BF16 expert matrices are never materialized in HBM.

1. Dedicated weight TMA loads packed weights and their scales; the raw ring is governed by `PipelineTmaAsync` (SPLIT 926–944). The activations are on a separate `PipelineTmaUmma` ring (962–977).
2. Each decoder waits for raw input readiness and acquires a free decoded-TMEM slot (503–524). It loads compact E4M3 scales and packed E2M1 fragments from SMEM into registers through `cute.autovec_copy` (526–559).
3. One native helper consumes a complete 16-value NVFP4 block: two 32-bit packed E2M1 words (eight bytes) plus its one-byte E4M3 scale (UTILS 19–30). It converts the shared scale once and uses it for all 16 values.
4. CUDA 13.2+ emits `cvt.rn.bf16x2.e4m3x2`, eight `cvt.rn.bf16x2.e2m1x2`, and eight `mul.rn.bf16x2` operations (UTILS 13–65). This is native packed conversion and packed multiplication, **not a single fused E2M1×E4M3→BF16 instruction**. Earlier toolkit support uses FP16 packed conversion/multiply and widens the exact result to BF16 (67–135); avoid implying all recorded results used the 13.2 form unless their provenance confirms it.
5. Decoder output first lives in BF16 register fragments, then `store_transformed_a` writes it to operand-A TMEM (SPLIT 560–575). The TMEM store copy atom is `tcgen05.St32x32bOp(Repetition(8), Unpack.NONE)` (1157–1169). This uses a dedicated operand region after the FP32 accumulator region, not an overwrite of the accumulator (325–333).
6. The MMA warp reconstructs the same operand-TMEM layout (1680–1694), waits for transformed A and activation B (1731–1735), and issues BF16 MMA with FP32 accumulation from those operands (1736–1763).

The E2M1×E4M3 product is exact in BF16: the two small significands fit within BF16 precision and its exponent range covers all finite NVFP4 block products. The separate FP32 tensor/expert factor is intentionally deferred until the FP32 accumulator epilogue. Applying that FP32 factor during decode would add work on the feed path and introduce a rounding boundary when storing the fully scaled weight back to BF16. Exactness applies to the block product, not arbitrary full FP32-scaled weights or all subsequent accumulation.

Source links:
- [Native CUDA 13.2 conversion/multiplication](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py#L13-L65)
- [Raw load, decode, TMEM store](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L503-L582)
- [MMA consume/release](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L1680-L1772)

## Publication, reuse, and finite buffering

`PipelineAsyncUmma` has all eight decoder warps (256 threads per CTA, extended across the CTA group when used) as producers (SPLIT 946–960). A transformed tile becomes ready only through the producer commits after its TMEM stores and `fence_view_async_tmem_store`; it cannot be consumed when just one group is done. SPLIT 456–468 fences TMEM stores, releases raw SMEM, and commits the transformed stage. The MMA consumer waits before issuing the tile and releases that stage through the UMMA-aware consumer operation after issue (1731–1766). This is an async pipeline contract protecting reuse; do not say the consumer simply overwrites immediately after the CPU-like issue call.

The source verifies raw-stage counts ≥2 and transformed-stage counts ≥2, subject to the selected shared-memory/TMEM capacity calculation (SPLIT 2392–2536). Run-ahead is bounded by these rings and required weight/scheduler readiness. It has no activation-output data dependency, but it is not literally free of all dependencies, synchronization, or resource contention.

Why this matters for prose: W4A16 uses lower-throughput BF16 MMA hardware. Making the smaller-weight memory regime favorable is not enough if software weight decode then starves that pipeline. Two balanced decoder groups, packed native arithmetic, one scale conversion per block, and keeping FP32 scaling out of the decoder all reduce pressure on this feed path. The observed high tensor-core pipeline utilization is consistent with this design; a profiler alone does not establish the speed contribution of every design choice. Existing article capture placeholders must remain visibly pending fresh profiling.

## MegaMoE reuse and exact differences

- `_MegaMixedInput` subclasses the split `Sm100W4A16GroupedGemmKernel` and inherits `_setup_transform_partitions` and `_transform_tile`, including the exact microproduct helper (MEGA 55–57, 319–349, 1549–1603).
- Mega also uses exactly two decoder warpgroups, now warps 12–15 and 16–19 in a 20-warp / 640-thread CTA (244–249). Its source explicitly states that each group decodes a disjoint half of the same K tile (1526–1534).
- The same TMEM store atom and inherited partitions are installed for both FC1 and FC2 (1535–1572). Mega gate16/up16 storage already matches the desired TMEM row grouping; split's gate/up row remap is not repeated.
- Mega fits two FP32 accumulator stages and either three decoded K256 stages for N64 or two for N128 (89–108), retaining independently sized raw and activation rings. This is a finite run-ahead window.
- Mega overrides the finish sequence: raw/SF loads finish before the final TMEM store, so raw SMEM is released **before** the TMEM store fence/commit (112–125), allowing earlier raw-ring reuse. It still publishes decoded readiness only after the TMEM fence.
- Both retain the same BF16 operand-TMEM / activation-SMEM consumption pattern (1381–1439).
- Consequently the article's later Mega section can state that it reuses the same two-group decoder, then discuss overlap with dispatch, input staging, persistent scheduling, FC1/FC2 progress, and reuse of available warps for final combine. There is no need to reteach decoding there.

Source links:
- [Inherited decoder and raw-release ordering](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L55-L125)
- [Mega roles](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L244-L249)
- [Same two disjoint halves and shared transform](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1525-L1603)

## Suggested compact article insertion

Weight decoding is the part we cannot afford to get wrong. BF16 tensor cores have less peak arithmetic throughput than native FP4, so a decoder that leaves them waiting would quickly spend the bandwidth savings. We dedicate two warpgroups—eight warps—to feeding them. Both work on the same weight tile, each decoding one half of its K dimension, with each 16-value NVFP4 block and its scale kept together.

The weight TMA warp brings packed E2M1 values and E4M3 scales into shared memory. The decoder warps load their portions into registers, convert the values and the shared scale with native packed PTX, multiply in BF16, then store the resulting BF16 operand directly into TMEM. CUDA 13.2 provides direct E2M1-to-BF16 and E4M3-to-BF16 conversion forms; we convert each scale once for its 16 weights. Both groups publish the completed tile through a pipeline barrier, and the MMA warp consumes it alongside the separately staged BF16 activations. Multiple decoded slots let preparation of upcoming weights overlap the current MMA.

Only the exact E2M1×E4M3 product passes through this decoder. Deferring the remaining FP32 factor to the FP32 accumulator epilogue both preserves precision and keeps extra scaling instructions off the path feeding MMA. That balance matters: the goal is not just fewer bytes from HBM, but a well-fed BF16 tensor-core pipeline. [Follow with the existing clearly labeled utilization illustration/capture note.]
