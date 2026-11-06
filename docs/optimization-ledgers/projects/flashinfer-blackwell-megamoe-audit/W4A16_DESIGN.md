# Proposed CuTe DSL NVFP4 W4A16 MegaMoE extension

Read-only design audit, 2026-09-07. FlashInfer main
`91bda04c66f7cb851e1ab3b78b9fecea644b9844`; existing SGLang W4A16
`8a7cd7b56a3ad112e4affd453169d72deb77d508`; open SGLang MegaMoE PR
#31470 head `685dabd8dbb4b76236924cc2747447572af1d6be`.
No implementation or GPU measurements were performed.

## Recommendation

Add a backend under the existing `MegaKernelBackend` interface, with proposed
public config `Sm100_Bf16_Nvfp4_Bf16_Cutedsl_MegaMoeConfig` and registry name
`sm100_bf16_nvfp4_bf16_cutedsl`. Keep `MoEEpLayer`, `MegaConfig`, and
`MoEEpTensors` as the public construction and forward interface.

The interface extension is small. A true fused W4A16 FC1/FC2 kernel is new
work: the existing local W4A16 launches distinct GEMMs; NVFP4 MegaMoE uses
blockscaled W4A4 MMA and quantized intermediates.

## Proposed first-backend contract

- SM100-family scope, with hardware and supported geometry validated explicitly.
- Packed NVFP4 E2M1 expert weights, per-16 E4M3 block scales, and explicit
  per-expert FP32 global weight scales, preserving the local W4A16 convention.
- BF16 input, dispatch payload, FC1 activation handoff, combine cells, and output.
- FP32 MMA accumulation and FP32 routed weights; externally computed global
  expert IDs, exactly one application of routed scaling.
- No activation scales, per-token activation quantization, or FC2 input scale.
- Initial SwiGLU coverage matching the selected local W4A16 control.
- Apply routed weights after FC2, using the existing staged top-k reduction
  path as the first implementation; in-kernel remote reduction is separate work.
- Preserve the existing local kernel's global-alpha placement: after FP32 GEMM
  accumulation, before FC1 activation. Folding it into BF16 decoded weights
  changes rounding and is not an equivalent implementation.

## API details

The existing abstract backend already provides weight preparation, workspace
allocation/pooling, input validation/staging and compute methods
(`moe_ep/core/kernel/base.py`). No new `forward` arguments are needed.

`MegaConfig.quantize_input=False` is not a W4A16 switch: current NVFP4
backends interpret it as packed, already-quantized input plus scales. Even
the current BF16 backend requires `quantize_input=True` but copies BF16
without quantizing. Select compute precision through the new config class;
keep existing flag behavior compatible. If cleaning this up, move the
input-format decision/validation to the backend rather than adding a global
quantization-policy framework merely for W4A16.

The common `PrequantizedMoEWeights` currently carries packed weights and block
scale planes, but no global weight scales. Existing `fc1_alpha`/`fc2_alpha`
config and tensor fields can technically carry the necessary global scales.
The cleaner additive weight interface is optional `w13_global_scale` and
`w2_global_scale` on the prequantized pack, retained in the new backend's
transformed weight bundle. Treat these as layer weights rather than workspace
configuration. Defaults preserve old callers; unsupported backends must reject
non-default global-scale metadata rather than silently ignore it. Preserve the
initial shared gate/up scale restriction if matching the current local ABI.

Workspace pool keys should describe workspace geometry and kernel settings,
not identities of per-layer weight-scale tensors. Pass scale pointers as
per-launch weight arguments, or stage them using existing per-call alpha
support. Retain collective warmup, stable graph-captured workspace addresses,
correct output ownership and explicit layer teardown. This avoids copying
SGLang PR #31470's private `_workspace` sharing workaround.

## Kernel reuse and actual missing work

Reuse/port the existing local W4A16 E2M1+E4M3 decoding and load/transform/MMA
pipeline concepts from:

- `fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py:18`
- `fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:488`

The local kernel uses weight-A/activation-B (swap-AB). Keeping that orientation
favors a dedicated swap-AB BF16-MMA fused-FC12 specialization using the current
MegaMoE scheduling/communication hooks. Reuse BF16 MegaMoE's no-scale dispatch
and BF16 FC1-handoff semantics. Its non-swap compute kernel is not a drop-in
base for the local weight-A transform pipeline.

Common communication already exposes token dtype, scale-plane count and
`is_swap_ab` independently (`kernel_src/cutedsl_megamoe/src/src/token_comm.py:374`).
No new transport abstraction is needed merely to send BF16 for swap-AB compute.

Required work:

1. Adapt FC1/FC2 scheduling, dispatch-ready counters, intermediate publication,
   FC2 readiness and tail-counter reset to the new BF16-MMA weight-transform path.
2. Reconcile warp roles and barrier counts. The local W4A16 kernel uses 16 warps,
   including transform warps 8-15; existing BF16 MegaMoE uses dispatch warps 8-11.
   Classes cannot be composed unchanged. Recalculate SMEM/TMEM budgets and tune.
3. Prepare the new weight/block-scale layout once; do not assume local W4A16,
   BF16 MegaMoE and NVFP4 MegaMoE gate/up interleaves match.
4. Preserve arithmetic and rounding contracts; do not inherit
   `apply_topk_in_fc1=True` from the W4A4 serving adapter.
5. Pool workspaces and cover zero-token ranks, skewed routing, changing live
   token counts and collective graph capture/replay. Ensure reduction work
   tracks actual tokens rather than prefill-sized capacity.

Current BF16 MegaMoE supports a fixed 256x256, two-CTA compute geometry; our
local decode tactics do not transfer automatically to that scheduler.

## SGLang

Reuse its existing NVFP4/online weight loader and BF16 activation path. Select
the mega backend before local backend-specific weight repacking; pass packed
weights plus block/global scales through the public FlashInfer preparation
interface. Refresh prepared weights during reload and preserve graph lifetime.

Use the MegaMoE adapter's no-op outer dispatch/combine with global expert IDs:
one `MoEEpLayer.forward(MoEEpTensors(...))` owns communication and computation.
Avoid wrapping it in the existing separate FlashInfer A2A dispatcher. Keep
FP32 top-k weights and the W4A16 bypass of activation quantization. Do not
globally change the online quantization metadata flag, which also controls
weight-conversion exclusions.

## Validation and performance decision

Use the same packed weights, exact block/global scales, routed IDs and FP32
scores in the new kernel and existing W4A16 plus EP control. Check numerical
parity with the existing tolerance, including all-rank aggregation, zero-token
ranks, skew, CUDA graphs and weight reloads. Include the same finalization
rounding path in both controls where parity is the requested contract.

Compare full layer staging + dispatch + FC1/activation/FC2 + combine, separately
for decode and prefill. BF16 dispatch costs 2H bytes/token versus H/2 plus scales
for NVFP4, and dequantization competes with communication for kernel resources.
Existing NVFP4 MegaMoE speedups do not predict W4A16 MegaMoE gains.

## References

- https://github.com/flashinfer-ai/flashinfer/pull/4048
- https://github.com/flashinfer-ai/flashinfer/pull/4386
- https://github.com/flashinfer-ai/flashinfer/blob/91bda04c66f7cb851e1ab3b78b9fecea644b9844/flashinfer/moe_ep/core/kernel/base.py
- https://github.com/flashinfer-ai/flashinfer/blob/91bda04c66f7cb851e1ab3b78b9fecea644b9844/flashinfer/moe_ep/weights.py
- https://github.com/sgl-project/sglang/pull/35120
- https://github.com/sgl-project/sglang/pull/38215
- https://github.com/sgl-project/sglang/pull/31470
- https://github.com/flashinfer-ai/flashinfer/issues/4727
