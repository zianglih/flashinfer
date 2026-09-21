"""Pinned SGLang GLM-5.2 router for this benchmark, with preallocated outputs.

The complete Triton kernel below is copied verbatim from SGLang (Apache-2.0):
https://github.com/sgl-project/sglang/blob/50eeb742961908afa68f4f523a1a19c5de6eb0b3/python/sglang/kernels/ops/moe/moe_fused_gate.py
Only the adapter is new. It uses the original GLM E256/K8 launch contract and
writes the benchmark's existing buffers, without an installed SGLang dependency.
"""

from functools import lru_cache

import torch
import triton
import triton.language as tl

SGLANG_ROUTING_COMMIT = "50eeb742961908afa68f4f523a1a19c5de6eb0b3"
SGLANG_ROUTING_SOURCE_SHA256 = (
    "5663a23cf30e6b2e1e2f8ba6d25b9c3eac39e319658c05f0f400b78b3862c47b"
)
SGLANG_ROUTING_KERNEL_AST_SHA256 = (
    "075eb2d017d66233cb3ac41155ab1ef8105fa1f0c0f81fccea253bd0e94ffe0a"
)


@triton.jit
def _router_triton_kernel(
    scores_ptr,  # [M, N] fp32, GEMM output (raw logits)
    bias_ptr,  # [N]    fp32/fp16/bf16 (upcast to fp32 on load)
    out_weights_ptr,  # [M, K] fp32
    out_indices_ptr,  # [M, K] int32
    M,
    routed_scaling_factor,
    moe_softcapping,
    N: tl.constexpr,
    K: tl.constexpr,  # total topk (includes fused shared experts)
    K_ROUTED: tl.constexpr,  # K - num_fused_shared_experts
    BLOCK_M: tl.constexpr,  # rows processed per program (row tiling)
    BLOCK_N: tl.constexpr,  # >= N, power of 2
    BLOCK_K: tl.constexpr,  # >= K, power of 2
    N_GROUP: tl.constexpr,  # expert groups (1 = ungrouped)
    TOPK_GROUP: tl.constexpr,  # groups kept per token (grouped routing)
    EXPERTS_PER_GROUP: tl.constexpr,  # N // N_GROUP
    BLOCK_G: tl.constexpr,  # >= N_GROUP, power of 2
    SCORING_FUNC: tl.constexpr,  # 0 = sigmoid, 1 = sqrtsoftplus, 2 = softmax
    HAS_SOFTCAP: tl.constexpr,  # tanh softcapping (softmax only)
    RENORMALIZE: tl.constexpr,
    APPLY_SCALE: tl.constexpr,  # apply_routed_scaling_factor_on_output
    HAS_BIAS: tl.constexpr,
    USE_PDL: tl.constexpr,
    stride_sm,
    stride_sn,
    stride_wm,
    stride_wk,
    stride_im,
    stride_ik,
) -> None:
    # Row-tiled: each program handles BLOCK_M rows; all reductions run along the
    # expert (N) axis. Tiling rows keeps CTAs large enough to stay occupancy-bound
    # rather than launch-bound at small N (many tiny 1-warp CTAs otherwise).
    pid = tl.program_id(0)
    offs_m = pid * BLOCK_M + tl.arange(0, BLOCK_M)  # [BLOCK_M]
    offs_n = tl.arange(0, BLOCK_N)  # [BLOCK_N]
    mask_m = offs_m < M
    mask_n = offs_n < N

    # Prefetch a real bias before the PDL wait. Plain softmax routing has no
    # bias, so keep the zero value in registers rather than materializing and
    # clearing a device tensor for every routing call.
    if HAS_BIAS:
        bias = tl.load(bias_ptr + offs_n, mask=mask_n, other=0.0).to(tl.float32)
    else:
        bias = tl.zeros([BLOCK_N], dtype=tl.float32)

    if USE_PDL:
        tl.extra.cuda.gdc_wait()

    row_ptr = scores_ptr + offs_m[:, None] * stride_sm + offs_n[None, :] * stride_sn
    mask2d = mask_m[:, None] & mask_n[None, :]
    scores = tl.load(row_ptr, mask=mask2d, other=0.0).to(
        tl.float32
    )  # [BLOCK_M, BLOCK_N]

    if SCORING_FUNC == 0:
        # sigmoid(x) = 1 / (1 + exp(-x)); bias is for ranking only, weight is bias-free.
        activated = tl.sigmoid(scores)
        biased = activated + bias[None, :]
    elif SCORING_FUNC == 1:
        # sqrt(softplus(x)). log(1.0 + exp(x)) rounds to 0 below -16.64 and overflows
        # above 88.7; Triton has no log1p, so recover it from log via z*log(u)/(u-1).
        z = tl.exp(-tl.abs(scores))
        u = 1.0 + z
        exact = u == 1.0
        log1p_z = tl.where(exact, z, z * tl.log(u) / tl.where(exact, 1.0, u - 1.0))
        sp = tl.maximum(scores, 0.0) + log1p_z
        activated = tl.sqrt(sp)
        biased = activated + bias[None, :]
    else:
        # softmax over the row: weight is the softmax probability (bias kept), with
        # optional tanh softcapping. Ranking by the (softcapped, biased) logit is
        # monotonic with the softmax prob, so the topk loop below ranks on `biased`.
        logit = scores
        if HAS_SOFTCAP:
            # tanh(z) = 2*sigmoid(2z) - 1 (avoids relying on tl.math.tanh availability).
            z = logit / moe_softcapping
            logit = moe_softcapping * (2.0 * tl.sigmoid(2.0 * z) - 1.0)
        biased = logit + bias[None, :]
        biased = tl.where(mask_n[None, :], biased, -float("inf"))
        row_max = tl.max(biased, axis=1)[:, None]  # [BLOCK_M, 1]
        exp_row = tl.where(mask_n[None, :], tl.exp(biased - row_max), 0.0)
        row_sum = tl.sum(exp_row, axis=1)[:, None]  # [BLOCK_M, 1]
        activated = exp_row / row_sum

    biased = tl.where(mask_n[None, :], biased, -float("inf"))  # [BLOCK_M, BLOCK_N]

    # Map NaN -> a finite floor
    biased = tl.where(biased == biased, biased, -1e30)  # [BLOCK_M, BLOCK_N]

    # Grouped routing (DeepSeek-V3 noaux_tc): per-group score = sum of the top-2
    # biased values; keep TOPK_GROUP groups (lowest group id wins ties); mask the
    # experts of dropped groups to -inf before the top-k below. Weight is still the
    # bias-free `activated`. Constexpr N_GROUP <= 1 skips this entirely (ungrouped).
    if N_GROUP > 1:
        offs_g = tl.arange(0, BLOCK_G)  # [BLOCK_G]
        group_of_n = offs_n // EXPERTS_PER_GROUP  # [BLOCK_N]
        group_score = tl.full([BLOCK_M, BLOCK_G], -float("inf"), dtype=tl.float32)
        for g in tl.static_range(N_GROUP):
            in_g = (group_of_n[None, :] == g) & mask_n[None, :]
            vals = tl.where(in_g, biased, -float("inf"))
            top1 = tl.max(vals, axis=1)[:, None]  # [BLOCK_M, 1]
            vals2 = tl.where(vals >= top1, -float("inf"), vals)
            top2 = tl.max(vals2, axis=1)[:, None]  # [BLOCK_M, 1]
            group_score = tl.where(offs_g[None, :] == g, top1 + top2, group_score)

        gcur = group_score
        keep = tl.zeros([BLOCK_M, BLOCK_N], dtype=tl.float32)
        for _i in tl.static_range(TOPK_GROUP):
            gmax = tl.max(gcur, axis=1)[:, None]  # [BLOCK_M, 1]
            glane = tl.where(gcur == gmax, offs_g[None, :], N_GROUP + 1)
            win_g = tl.min(glane, axis=1)[:, None]  # [BLOCK_M, 1] lowest-id on ties
            keep = tl.where(group_of_n[None, :] == win_g, 1.0, keep)
            gcur = tl.where(offs_g[None, :] == win_g, -float("inf"), gcur)
        biased = tl.where(keep > 0.0, biased, -float("inf"))

    offs_k = tl.arange(0, BLOCK_K)  # [BLOCK_K]
    mask_k_total = offs_k < K
    mask_k_routed = offs_k < K_ROUTED
    selected_vals = tl.zeros([BLOCK_M, BLOCK_K], dtype=tl.float32)
    selected_idx = tl.zeros([BLOCK_M, BLOCK_K], dtype=tl.int32)

    cur = biased  # [BLOCK_M, BLOCK_N]
    for k in tl.static_range(K_ROUTED):
        max_val = tl.max(cur, axis=1)[:, None]  # [BLOCK_M, 1]
        is_max = cur == max_val
        lane_id = tl.where(is_max, offs_n[None, :], N + 1)  # lowest expert id wins ties
        win_lane = tl.min(lane_id, axis=1)[:, None].to(tl.int32)  # [BLOCK_M, 1]
        win_activated = tl.sum(
            tl.where(offs_n[None, :] == win_lane, activated, 0.0), axis=1
        )[:, None]  # [BLOCK_M, 1]
        slot = offs_k[None, :] == k  # [1, BLOCK_K]
        selected_vals = tl.where(slot, win_activated, selected_vals)
        selected_idx = tl.where(slot, win_lane, selected_idx)
        cur = tl.where(offs_n[None, :] == win_lane, -float("inf"), cur)

    routed_sum = tl.sum(tl.where(mask_k_routed[None, :], selected_vals, 0.0), axis=1)[
        :, None
    ]  # [BLOCK_M, 1]

    # Fill fused-shared-expert slots: weight = routed_sum / routed_scaling_factor,
    # id = num_experts + (slot - K_ROUTED).
    if K_ROUTED < K:
        is_shared = (offs_k[None, :] >= K_ROUTED) & mask_k_total[None, :]
        shared_weight = routed_sum / routed_scaling_factor  # [BLOCK_M, 1]
        shared_idx = (N + (offs_k - K_ROUTED)).to(tl.int32)[None, :]  # [1, BLOCK_K]
        selected_vals = tl.where(is_shared, shared_weight, selected_vals)
        selected_idx = tl.where(is_shared, shared_idx, selected_idx)

    if USE_PDL:
        tl.extra.cuda.gdc_launch_dependents()

    if RENORMALIZE:
        norm = tl.where(routed_sum > 0.0, routed_sum, 1.0)  # [BLOCK_M, 1]
        selected_vals = selected_vals / norm
    if APPLY_SCALE:
        selected_vals = selected_vals * routed_scaling_factor

    out_w_ptr = (
        out_weights_ptr + offs_m[:, None] * stride_wm + offs_k[None, :] * stride_wk
    )
    out_i_ptr = (
        out_indices_ptr + offs_m[:, None] * stride_im + offs_k[None, :] * stride_ik
    )
    store_mask = mask_m[:, None] & mask_k_total[None, :]
    tl.store(out_w_ptr, selected_vals, mask=store_mask)
    tl.store(out_i_ptr, selected_idx, mask=store_mask)


@lru_cache(maxsize=None)
def _supports_pdl(device_index):
    # Matches SGLang kernels/jit/utils/arch.py:is_arch_support_pdl.
    return torch.cuda.get_device_capability(device_index)[0] >= 9


def route_glm52(
    router_logits,
    routing_bias,
    topk_values,
    topk_indices,
    routed_scaling_factor,
):
    """Write fixed GLM E256/K8 sigmoid+bias routes with FP32 normalized weights."""
    if router_logits.ndim != 2 or router_logits.shape[1] != 256:
        raise ValueError("GLM routing requires logits [M, 256]")
    rows = router_logits.shape[0]
    if routing_bias.shape != (256,) or not routing_bias.is_contiguous():
        raise ValueError("GLM routing requires a contiguous bias [256]")
    if topk_values.shape != (rows, 8) or topk_indices.shape != (rows, 8):
        raise ValueError("GLM routing requires outputs [M, 8]")
    for tensor in (router_logits, routing_bias, topk_values):
        if tensor.dtype != torch.float32:
            raise ValueError("GLM logits, bias and route weights must be FP32")
    if topk_indices.dtype != torch.int32:
        raise ValueError("GLM expert IDs must be int32")
    if not router_logits.is_cuda or any(
        tensor.device != router_logits.device
        for tensor in (routing_bias, topk_values, topk_indices)
    ):
        raise ValueError("GLM routing tensors must be on the same CUDA device")
    if rows == 0:
        return
    use_pdl = _supports_pdl(router_logits.device.index)
    extra = {"launch_pdl": True} if use_pdl else {}
    _router_triton_kernel[(triton.cdiv(rows, 1),)](
        router_logits,
        routing_bias,
        topk_values,
        topk_indices,
        rows,
        float(routed_scaling_factor),
        0.0,
        N=256,
        K=8,
        K_ROUTED=8,
        BLOCK_M=1,
        BLOCK_N=256,
        BLOCK_K=8,
        N_GROUP=1,
        TOPK_GROUP=1,
        EXPERTS_PER_GROUP=256,
        BLOCK_G=1,
        SCORING_FUNC=0,
        HAS_SOFTCAP=False,
        RENORMALIZE=True,
        APPLY_SCALE=True,
        HAS_BIAS=True,
        USE_PDL=use_pdl,
        stride_sm=router_logits.stride(0),
        stride_sn=router_logits.stride(1),
        stride_wm=topk_values.stride(0),
        stride_wk=topk_values.stride(1),
        stride_im=topk_indices.stride(0),
        stride_ik=topk_indices.stride(1),
        num_warps=1,
        **extra,
    )
