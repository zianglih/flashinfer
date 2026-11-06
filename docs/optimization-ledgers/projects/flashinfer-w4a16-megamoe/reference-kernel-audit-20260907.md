# Existing kernel patterns for W4A16 MegaMoE

Read-only source audit at local HEAD `eeb255008369b78cd1619943403a3e187e38038b`, 2026-09-07. The active W4A16 kernel had an in-progress edit; references below identify the established checked-in implementations. No GPU measurements were made for this audit.

## Geometry and tuning

| Implementation | MMA operand orientation | Established tiles and clusters | Selection |
|---|---|---|---|
| Local CuTe W4A16 | A = decoded weights; M = output channels. B = BF16 activations; N = routed rows. | K256; routed N in 8,16,32,64,128,192. Each GEMM uses M128 with cluster(1,1) or (2,1), or M256 with cluster(2,1). M256 uses 2-CTA instructions; M128 uses 1-CTA instructions even with a 2-CTA cluster. | 23 FC1/FC2 tactic pairs before shape validation. FC1/FC2 share routed N, but can choose different M128/M256 topologies. N8 excludes M256; N192 requires M256 on both legs. |
| NVFP4 Mega | Swap-AB: A = NVFP4 weights; M = output channels. B = NVFP4 activations; N = routed rows. | Measured heuristics use M256, N128 or256, K256, cluster(2,1,1). Runtime block-scaled MMA N is rounded valid-token count to16, even though storage geometry is N128/256. | Four per-rank-capacity profiles; collective online tuner has24 candidates with in-kernel reduction enabled,12 without. |
| BF16 Mega | Non-swap: A = BF16 activations; M = routed tokens. B = BF16 weights; N = output channels. | Fixed M256/N256/K64, cluster(2,1,1),2-CTA. | One validated candidate for every capacity. |
| Current W4A16 Mega | Inherits BF16 Mega orientation, replacing dense B with online decoded weights. | Fixed M256/N256/K64, cluster(2,1,1),2-CTA. | Same fixed geometry; no W4A16-specific measured candidate table. |

Sources (paths relative to `flashinfer/` checkout):

- `flashinfer/fused_moe/cute_dsl/tuner.py:971-1014` contains all23 local W4A16 tactic pairs; `:1148-1198` filters them with actual shapes. `blackwell/moe_w4a16.py:41-46` explicitly labels the both-leg `(256,128,256),(2,1),True` tuple a correctness fallback, **not** a measured per-token winner.
- `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/moe_nvfp4_swapab/kernel_fc12.py:843-892` defines swapped operands/scales. `dynamic_mainloop.py:1-6,39-56` explains runtime N and the non-leader CTA TMA offset adjustment. `kernel_fc12.py:2275-2283` passes the actual valid-token count into the MMA helper. That helper emits block-scaled FP4 PTX; a BF16 implementation must adapt it or initially use fixed N.
- `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/tuner.py:157-165` defines BF16's sole geometry. `src/moe_bf16_glu/kernel_bf16_glu_fc12.py:816-828` confirms non-swapped A/B. `shim/w4a16/frontend.py:34-43,69-75` defines/requires the same current geometry.

## EP8 DeepSeek-V3 global tokens1..4096

The benchmark has H7168/I2048/E256/top8 (`benchmarks/bench_moe_deepseek.py:61-67`). Each rank owns32 experts. The split local runner receives `8*ceil(global_tokens/8)` rows after dispatch, **not** `ceil(global_tokens/8)` rows (`benchmarks/bench_cute_dsl_moe_distributed.py:873-884,936-950`). Consequently global1,2,4,8 all present8 rows to the local tuning surface; larger power-of-two rows remain unchanged. Its route generator samples global E256 with FP32 scores and cold-L2 timing (`flashinfer/fused_moe/cute_dsl/tuner.py:1060-1110`), so the expected per-expert route density is global_tokens/32, rather than the token count divided by32 local experts. Actual routing can be skewed.

Local W4A16 buckets round up to powers of two through256, multiples of256 through2048, then multiples of512 through4096 (`flashinfer/fused_moe/utils.py:195-242,276-290`). There is no source table assigning a best tactic to each bucket: those winners are measured/cached. The real EP benchmark tunes after finishing setup collectives (`benchmarks/bench_cute_dsl_moe_distributed.py:1010-1037`).

Mega capacity is `ceil(global_tokens/8)` (`benchmarks/bench_cute_dsl_moe_distributed.py:1111-1122`). NVFP4's default lookup keys on that capacity, not global tokens (`shim/nvfp4.py:1066-1080`; `shim/knob_cache.py:241-273`). For this power-of-two sweep, global1..2048 would use the `<512` NVFP4 profile and global4096 the `512..1023` profile. Those are **reference W4A4 profiles**, not defaults currently used by W4A16 Mega.

| NVFP4 Mega per-rank capacity | Tile M/N/K | Cluster | Group hint | Flag batch | Epi flag batch | Token return | Balance |
|---|---|---|---|---|---|---|---|
| <512 |256/128/256|(2,1,1)|512|4|(2,4)|epilogue warps|atomic counter|
|512..1023|256/128/256|(2,1,1)|512|4|(2,4)|reuse dispatch warps|atomic counter|
|1024..2047|256/256/256|(2,1,1)|512|4|(2,4)|standalone warps|atomic counter|
|>=2048|256/256/256|(2,1,1)|512|8|(2,4)|reuse dispatch warps|atomic counter|

The table is literal `shim/tuner.py:74-123,168-208`, measured historically on4×GB200 in July, not a B300 W4A16 result. `shim/autotune.py:44-84` gives the curated2tiles×2flag batches×3token-return modes×2IKR choices. `TUNING.md:297-327` records that token return dominated those historical profiles and BF16 still had one fixed candidate. W4A16 must preserve its separate FP32 post-FC2 routing contract when adapting that candidate machinery.

## Weight and activation staging

Local W4A16 already has the desired producer/transform separation:

- Packed A weights and E4M3 block scales use TMA into staged SMEM (`blackwell/moe_w4a16_kernel.py:1442-1530`). Their logical shape is `(output_channels,K,experts)` with K contiguous; scale storage is `tile_atom_to_shape_SF(...,16)` (`:577-591`). This is a blocked scale layout, unlike the new public linear scale ABI. Any internal repacking belongs in preparation and must preserve values/global scales.
- Eight transform warps decode into BF16, with a separate `PipelineTmaAsync` load→transform and `PipelineAsyncUmma` transform→MMA, plus an independent BF16 activation `PipelineTmaUmma` (`:891-937`). Producer arrival counts explicitly include the 2-CTA factor.
- The transform uses existing `decode_nvfp4_fragment_to_bf16`, vector copies, `store_transformed_a`, and the appropriate SMEM/TMEM fence before commit (`:442-552`). It computes resource-fitting load/transform stage counts and rejects fewer than2 stages (`:2318-2494`). It does not simply inherit dense BF16 stage counts.
- Warp roles are epilogue0–3, MMA4, scheduler5, weight TMA6, activation TMA7, transform8–15. Registers are176 for epilogue,80 for control,128 for transform (`:151-175`). FC1 uses transform fragments128; long-K FC2 uses32 (`blackwell/moe_w4a16.py:126-130`). Both DeepSeek legs are long-K with Ktile256, so this means128 for FC1 and32 for FC2.
- Weight TMA can start before activation readiness; only activation TMA waits for the preceding PDL grid. Weight cache hint is evict-first and activation hint is evict-last (`moe_w4a16_kernel.py:1376-1427,1442-1522`). Preserve the independence when adapting Mega's FC1/FC2 readiness signals.

NVFP4 Mega instead TMA-loads raw FP4 A/B plus both SF tensors directly into a block-scaled MMA pipeline (`src/moe_nvfp4_swapab/kernel_fc12.py:402-482,1042-1107`). It has no software BF16 weight transform. Its default roles are epi0–3/MMA4/TMA-A5/TMA-B6/scheduler7/dispatch8–11; optional standalone token return adds12–15 (`kernel_fc12.py:153-185`; `megamoe_kernel.py:279-299`). Copying its geometry/comm requires replacing the activation-quantizing epilogue and the block-scaled MMA, not changing only dtype names.

BF16 Mega has separate dense A/B TMA stage counts fitted to SMEM, with an extra B stage if space remains (`src/moe_bf16_glu/kernel_bf16_glu_fc12.py:381-408,451-505`). Current W4A16 Mega instead uses four weight producer warps(6,12,13,14), direct online decode into that BF16 B pipeline,480threads (`shim/w4a16/kernel.py:4-8,62-83`). It does not yet use the existing packed-weight TMA→transform pipeline.

## Priority

1. Adapt local W4A16's **output-M / small routed-N** orientation and packed-weight TMA→parallel transform→BF16 MMA pipeline into the existing swapped Mega scheduler/communication structure. Start from the common established `(256,128,256),(2,1)` geometry; extend to measured small-N tactics after the layout/epilogue is numerically validated. The prior NVFP4 Mega dynamic-N implementation is useful architectural evidence, but its FP4 instruction helper is not directly BF16-compatible.
2. Preserve BF16 input, FC1 intermediate, and per-route FC2 output. Preserve exact per-block BF16 decode, separate FP32 global alpha applied to FP32 accumulators, and FP32 routing scores after FC2. Keep the public weight ABI stable; transform internal storage as needed.
3. Reuse the curated collective tuning lifecycle and capacity cache after adding valid W4A16 candidates. Do not treat W4A4/GB200 winners as W4A16/B300 winners. Small prefetch/store changes can improve the current baseline but do not remove its routed-M256 work geometry.
