# CuTe DSL SwiGLU layout audit

Source pin: `bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4` (current FlashInfer main verified by parent, 2026-10-08). Read-only audit; source snapshots are under `evidence/layout-audit-current/`.

## Naming and shapes

Use the conventional model naming explicitly: `w1` is the gate projection, `w3` is the up (linear) projection, and `w2` is the down projection. For one expert with hidden width H and intermediate width I, stored linear-layer weight shapes are `w1: [I,H]`, `w3: [I,H]`, and `w2: [H,I]`; for row-vector batches, `gate = x @ w1.T`, `up = x @ w3.T`, and `y = (silu(gate) * up) @ w2.T`. FC1 computes the two H-to-I projections together, so its combined weight matrix is `[2I,H]`. FC2 is the I-to-H down projection.

API caveat: FlashInfer CuTe DSL calls the combined FC1 tensor `w1_weight`, not just the gate projection. Its canonical preparation input `w1_bf16` is `[up,gate]` = `[w3,w1]`. The newer unified MegaMoE canonical `w13` uses `[gate,up]`; the distributed benchmark explicitly swaps halves before CuTe preparation. Thus define model names once, then use FC1/FC2 for kernel discussion; avoid implying every API's `w1` identifies a standalone gate weight.

## CuTe W4A4 physical layout

The shared CuTe preparation interleaves 64 rows from each half: `[up[0:64], gate[0:64], up[64:128], gate[64:128], ...]`. Equivalently every 128 output-channel rows contain one matching 64-channel up/gate pair. This is a permutation, not a change to the model. NVFP4 weights are packed two E2M1 values per byte along K. Their E4M3 block scales are separately placed in the block-scaled MMA scale layout.

This CuTe path does **not** apply TRTLLM's extra MMA weight shuffle. The `prepare.py` file has both backends, so the similarly named `get_w3_w1_permute_indices` / TRTLLM shuffle must not be imported into the CuTe explanation. In CuTe, FC1 row interleave and block-scale swizzle are distinct operations.

The W4A4 FC1 epilogue loads adjacent up and gate TMEM subtiles into matching register fragments, applies the FP32 alpha scales, then fused SwiGLU and optional output quantization. Interleaving puts both halves in the same tile, allowing the matching fragments to be consumed locally rather than first materializing the full 2I intermediate as an independent activation-kernel input.

## Exact same external layout for W4A16

`prepare_cute_dsl_weights` handles both `(NVFP4,NVFP4)` and `(NVFP4,BF16)` without branching on activation dtype for weight layout or quantization. They share FC1 64-row up/gate interleaving, packed E2M1 weights, and MMA-layout E4M3 scales. The only non-MXFP4 branch also sets an activation runtime scale, separate from stored weights.

Inside W4A16, the transform reads the same shared-memory weights and scales through a composed row layout `((16,2),4)` with strides `((1,64),16)`. This turns each 64+64 up/gate block into four 16+16 pairs during decode, so each epilogue warp owns both operands within its 32 TMEM lanes. The source comment is unusually explicit. The parent/sibling audit should cover the subsequent TMEM-store and epilogue shuffle instructions before finalizing that detail.

## Pinned primary sources

- Canonical CuTe prep inherits `[up,gate]` input from TRTLLM prep: [prepare.py 487–495](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/prepare.py#L487-L495); [same-canonical-weights declaration 2509–2516](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/prepare.py#L2509-L2516).
- Shared interleave implementation: [prepare.py 2483–2493](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/prepare.py#L2483-L2493).
- Both precision pairs, 64-row interleave and quantization: [prepare.py 2543–2593](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/prepare.py#L2543-L2593).
- W4A4 FC1 operation and loading contract: [blockscaled_contiguous_gather_grouped_gemm_act_fusion.py 817–827](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py#L817-L827).
- Adjacent TMEM up/gate subtile loads: [same kernel 2733–2759](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py#L2733-L2759).
- Distinguish scale layout from weight interleave: [cute_dsl/utils.py 374–403](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/cute_dsl/utils.py#L374-L403).
- W4A16 load-time 16-row pairing: [moe_w4a16_kernel.py 1061–1074](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py#L1061-L1074).
- Actual benchmark same-weight byte permutation and naming order: [bench_cute_dsl_moe_distributed.py 740–749](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/benchmarks/bench_cute_dsl_moe_distributed.py#L740-L749).

## W4A4 NVFP4 epilogue precision and operation order

Suggested article paragraph (about 150 words):

> For NVFP4, the fused epilogue is more than a SwiGLU. The block-scaled tensor-core instruction consumes the E2M1 values and their E4M3 block scales, leaving FP32 accumulators in TMEM. The epilogue loads the matching up/gate fragments, applies the remaining FP32 scaling factors, and evaluates SwiGLU, including any configured clamps. In the fused output-quantization path, it then finds an absolute maximum for each 16-value block, rounds the output block scale to E4M3, rescales the activation using that rounded scale, and packs it back into E2M1 for FC2. Those steps depend on the completed accumulator. Making the tensor-core operation faster can therefore expose more of this epilogue work; peak FP4 throughput alone does not determine kernel latency. Our per-token activation path has a different boundary: FC1 emits a BF16 intermediate, and a separate quantizer computes the row scale and performs the 4over6 search. The scaling and SwiGLU still stay fused with FC1.

Exact source findings:

1. FP32 `alpha[expert_idx]` is loaded after tile selection. With input per-token scaling, it is multiplied by `a_per_token_scale[token_idx]` before applying it to up/gate FP32 accumulator fragments. These are remaining outer factors; E4M3 block factors are already consumed by the block-scaled MMA. Do not conflate expert/global alpha with the SwiGLU sigmoid parameter also called `swiglu_alpha`.
2. Standard SwiGLU branch performs alpha multiplication on both up and gate, then gate upper clamp and symmetric up clamp if finite limits are configured, then sigmoid/gate-times-up. Default unbounded limits make clamping mathematically inert. User wording "SwiGLU and any configured clamps" is safe; strict operations place the clamps before the sigmoid and product.
3. Fused quantizer uses a 16-element absolute maximum, times `1/6`, times `norm_const` (wrapper's `fc2_input_scale`). It rounds that value into E4M3. It rescales the FP32 activation by `norm_const / rounded_E4M3_scale`, then converts to E2M1. Scale bytes store directly to global memory; packed activation values stage through shared memory to TMA output. No intermediate BF16 round trip in this fused NVFP4 path. "Quantizes the register-resident result in the same epilogue" is more exact than "in-place", which can misleadingly suggest that the input memory is overwritten.
4. Per-token path sets `quantize_output=False`, chooses BF16/FP16 from output dtype (BF16 is the default), and calls the separate rowwise quantizer. That kernel performs a full-row maximum reduction and emits E2M1, E4M3 blocks, and one FP32 row scale. `4over6` is supported there; the fused per-tensor FC1 NVFP4 epilogue explicitly has no 4over6 variant today.
5. FC2 consumes the newly produced FP4 activation and E4M3 scales; when per-token quantization was selected it also receives the intermediate FP32 row scale. Do not claim that all W4A4 paths have identical kernel boundaries or that an epilogue bottleneck has been measured solely from source.

Pinned anchors:

- Block-scaled MMA and remaining epilogue alpha: [kernel 118–137](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py#L118-L137).
- Expert alpha and optional input row-scale multiplication: [kernel 2663–2675](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py#L2663-L2675).
- FP32 scale, clamp, sigmoid and product: [kernel 2948–3060](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py#L2948-L3060).
- Quantization reduction and E4M3 conversion: [kernel 3062–3146](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py#L3062-L3146).
- Reuse rounded scales and E2M1 conversion: [kernel 3180–3216](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py#L3180-L3216).
- Per-token intermediate dtype and separate quantizer: [fused_moe.py 649–655](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/fused_moe.py#L649-L655) and [734–770](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/fused_moe.py#L734-L770).
- Explicit 4over6 boundary: [fused_moe.py 433–442](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/fused_moe.py#L433-L442).
- Per-token output format and row-scale contract: [nvfp4_quantize.py 3097–3107](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/quantization/kernels/nvfp4_quantize.py#L3097-L3107), [3142–3155](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/quantization/kernels/nvfp4_quantize.py#L3142-L3155).
- Row-max reduction in separate quantizer: [nvfp4_quantize.py 1098–1128](https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/quantization/kernels/nvfp4_quantize.py#L1098-L1128).
