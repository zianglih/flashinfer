# Swap paired-SiTU: source-only plan

Status: bounded design only on retained49 (`482b636a` swap source). No candidate checkout, source edit, compile, GPU call or timing. W4 paired-SiTU results are a caution about native scheduling; its different arithmetic is not a reusable numerical contract.

## Minimal source boundary

Keep the existing `_activate` channel-pair loop, alpha products, TMEM/transpose ownership, quantization, accumulator release and all pipeline/PDL code. Add one private swap-only `_scaled_tanh_pair(pair, beta)` helper beside this epilogue and invoke it for the optional linear saturation and the gate saturation. In the existing SiTU branch, compute the gate sigmoid with packed multiply/add plus the same two scalar EX2/RCP calls, then multiply `bounded_gate * sigmoid(gate)` before the existing `up * gate_result` product. Do not mutate the original gate pair before the sigmoid reads it. Remove unused `situ_f32`/`tanh_f32` imports only if this leaves no call sites; retain `f32_reciprocal`.

One private helper avoids duplicating the scaled-tanh sequence in both gate and linear paths. No shared W4 helper, generic activation abstraction, runtime branch, tactic axis, cross-pair batching, layout change or scalar-SFU replacement is needed. This does add source code versus two scalar calls; neutral speed cannot justify retaining it.

## Exact lane recipe

For each original lane x, the new pair operation must project to this same ordered graph:

1. `beta32 = fp32(beta)` and `inv_beta = fp32(1 / beta32)` through the existing `f32_reciprocal`; do not use `fp32(1 / Python_beta)`.
2. `q = mul.rn(x, inv_beta)`.
3. `q = mul.rn(q, -2.0)` and then `q = mul.rn(q, log2(e))`. Do not fold the two constants into W4's `-2log2(e)`.
4. Scalar `ex2.approx.ftz` for each lane, then packed `add.rn(..., 1.0)`, then scalar `rcp.approx.ftz` per lane.
5. Packed **`fma.rn(inverse, 2.0, -1.0)`**. This is one rounding, matching the retained swap PTX and `_tanh_approx_f32` oracle. Do not replace it with W4's separately rounded multiply/subtraction.
6. Packed `mul.rn(beta32, tanh_result)`, preserving operand order.

The gate sigmoid separately uses `mul.rn(original_gate, fp32(-log2(e)))`, scalar EX2.FTZ, packed RN add-one, scalar RCP.FTZ. Its final multiply remains `bounded_gate * sigmoid_result`, followed by the existing up-product. Both arithmetic and multiplication association match the oracle, including beta values not exactly representable as FP32. Pair-lane order is the existing adjacent `(i, i+1)` register order; no shuffle or ownership change is proposed.

CUDA13.2/PTX9.2 defines f32x2 multiply and FMA as two independent FP32 operations; FMA rounds the combined product/sum once. RN arithmetic remains non-FTZ; only the unchanged scalar SFUs retain FTZ. See [PTX multiply/FMA](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#floating-point-instructions-fma). The local CUTLASS wrapper exposes `cute.arch.fma_packed_f32x2` with default RN and no FTZ. Its exact installed4.8 lowering must still be checked in qualification. No universal NaN-payload equality follows from this ISA contract.

## Expected work and risks

Excluding already-packed entry/final products, gate-only SiTU has 18 scalar arithmetic sites per channel pair, nominally replaceable by nine paired sites; its eight scalar SFU sites remain. Optional linear saturation adds12 scalar arithmetic sites, replaceable by six paired sites, and four unchanged scalar SFUs. Thus gate+linear nominally changes30 scalar arithmetic sites to15 paired sites, with12 SFUs unchanged. This estimate excludes packing/MOVs, allocation and instruction scheduling. Existing current-source captures contain the scalar chains, unlike closed proposals where scalar Python already compiled to paired native instructions.

Only two existing channel lanes are live in each helper. There is no new tile-sized cache, but paired register constraints may still extend liveness, add MOV/R2UR work or change scheduling. Exact FC1 resources, full native opcode deltas, scalar SFU counts/modifiers, accumulator release placement, and unchanged FC2/non-SiTU binaries are required. An arithmetic count reduction is not a latency claim.

## History and qualification boundary

The scoped prior audit in `audits/paired-activation-math/README.md` and the old CLOSED_LEADS ledger found no exact swap paired-SiTU implementation. The current W4 candidate is distinct because its reciprocal and unfused rounding recipe differ. Reverted absmax trees, native-TMEM ownership changes and already-packed FC2 rewrites are not mechanisms to reuse here.

Before any timing: source/AST proof of the bounded branch and oracle graph; paired native compile for gate-only and gate+linear with a non-FP32-exact beta; existing bit-exact SiTU tests across NVFP4/per-token/MX and one/two CTA paths; scalar exceptional-input helper diagnostics if authorized (finite raw bits, NaN classification separately); unchanged SFU counts, explicit packed FMA RN, no folding of exponent constants, no new local memory, actual register/occupancy report; binary identity for unaffected FC2/SwiGLU/ReLU2/GeGLU. Existing correctness tests remain unchanged. No swap prototype or GPU launch is proposed while W4's small decode losses are still under review.
