"""Untimed independent expert math and distinct W4A16 reduction references.

Adapted from tests/moe_ep/w4a16_reference.py at FlashInfer
ad0a5e5e78e57070ec7c582efe733cb55cd8839f (Apache-2.0).
Source SHA256: 6282388bf42df1cc2580c79ce1cf58644943f958decd2ebf99ff2228629d25a5.
Production expert kernels/finalizers are not called. cuBLASLt expert math and
NCCL transport/reduction are trusted library primitives, not independently
verified implementations. No reference tensor is retained on GPU for timing.
"""

from __future__ import annotations

from dataclasses import dataclass
import functools
import hashlib
import json
from pathlib import Path

from moe_distributed_layout import token_layout

REFERENCE_PROVIDER = "benchmark.w4a16_independent_contract"
REFERENCE_SOURCE_SHA256 = (
    "6282388bf42df1cc2580c79ce1cf58644943f958decd2ebf99ff2228629d25a5"
)
ATOL = RTOL = 1e-2


def validate_refcheck_policy(
    policy, *, refcheck, mode, modes, variants, fused, weighted
):
    if policy not in ("cross-pair", "per-path"):
        raise ValueError("Unknown refcheck policy")
    if policy == "per-path" and (
        not refcheck
        or mode != "benchmark"
        or modes != ["ep"]
        or variants != ["w4a16", "w4a16_megamoe"]
        or fused
        or weighted
    ):
        raise ValueError(
            "--refcheck-policy per-path requires --refcheck, benchmark EP "
            "w4a16,w4a16_megamoe in that order, --no-fused-finalize, "
            "and no FC1 route weighting"
        )


def reduction_contract(variant, communication):
    if communication not in ("allgather", "allreduce", "alltoall"):
        raise ValueError("Unknown reference communication")
    if variant == "w4a16_megamoe":
        return "unweighted_bf16_routes_ordered_fp32_fma_bf16"
    if variant != "w4a16":
        raise ValueError("W4A16 reference does not support this variant")
    return (
        "owner_fp32_fma_bf16_then_topk_slot_fp32_tree_bf16"
        if communication == "alltoall"
        else "owner_fp32_fma_bf16_then_nccl_bf16_sum"
    )


def _dequantize(packed, scales):
    import torch

    lookup = torch.tensor(
        [0, 0.5, 1, 1.5, 2, 3, 4, 6, -0.0, -0.5, -1, -1.5, -2, -3, -4, -6],
        dtype=torch.float32,
        device=packed.device,
    )
    packed = packed.view(torch.uint8)
    codes = torch.stack((packed & 15, packed >> 4), dim=-1).long()
    values = lookup[codes].reshape(*scales.shape, 16)
    return (values * scales.float().unsqueeze(-1)).flatten(-2).bfloat16()


@functools.cache
def _swiglu_kernel():
    import triton
    import triton.language as tl

    @triton.jit
    def kernel(
        FC1,
        SCORES,
        OUT,
        I: tl.constexpr,
        N: tl.constexpr,
        CLAMP: tl.constexpr,
        WEIGHTED: tl.constexpr,
    ):
        index = tl.program_id(0) * 256 + tl.arange(0, 256)
        offset = (index // I) * (2 * I) + index % I
        gate = tl.load(FC1 + offset, index < N, other=0)
        up = tl.load(FC1 + offset + I, index < N, other=0)
        if CLAMP is not None:
            limit = tl.full((), CLAMP, tl.float32)
            gate = tl.inline_asm_elementwise(
                "min.NaN.f32 $0, $1, $2;",
                constraints="=f,f,f",
                args=[gate, limit],
                dtype=tl.float32,
                is_pure=True,
                pack=1,
            )
            up = tl.inline_asm_elementwise(
                "{ .reg .f32 lo; min.NaN.f32 $0, $1, $2; "
                "neg.f32 lo, $2; max.NaN.f32 $0, $0, lo; }",
                constraints="=f,f,f",
                args=[up, limit],
                dtype=tl.float32,
                is_pure=True,
                pack=1,
            )
        # Match epilogue.py::_swiglu_act, including operation association.
        activated = tl.inline_asm_elementwise(
            """{
                .reg .f32 neg, exponent, denominator, sigmoid, silu;
                mul.rn.f32 neg, $1, 0fBFB8AA3B;
                ex2.approx.ftz.f32 exponent, neg;
                add.rn.f32 denominator, exponent, 0f3F800000;
                rcp.approx.ftz.f32 sigmoid, denominator;
                mul.rn.f32 silu, $1, sigmoid;
                mul.rn.f32 $0, $2, silu;
            }""",
            constraints="=f,f,f",
            args=[gate, up],
            dtype=tl.float32,
            is_pure=True,
            pack=1,
        )
        if WEIGHTED:
            score = tl.load(SCORES + index // I, index < N, other=0)
            activated = tl.inline_asm_elementwise(
                "mul.rn.f32 $0, $1, $2;",
                constraints="=f,f,f",
                args=[activated, score],
                dtype=tl.float32,
                is_pure=True,
                pack=1,
            )
        tl.store(
            OUT + index,
            activated.to(tl.bfloat16, fp_downcast_rounding="rtne"),
            index < N,
        )

    return kernel


def _gather_rows(tensor, counts):
    import torch
    import torch.distributed as dist

    if len(counts) == 1:
        return tensor
    padded = torch.zeros(
        (max(counts), *tensor.shape[1:]), dtype=tensor.dtype, device=tensor.device
    )
    padded[: tensor.shape[0]].copy_(tensor)
    parts = [torch.empty_like(padded) for _ in counts]
    dist.all_gather(parts, padded)
    return torch.cat([part[:n] for part, n in zip(parts, counts, strict=True)])


def _all_rank_guard(condition, device, message):
    import torch
    import torch.distributed as dist

    failed = torch.tensor(not bool(condition), dtype=torch.int32, device=device)
    if dist.is_initialized():
        dist.all_reduce(failed, op=dist.ReduceOp.MAX)
    if failed.item():
        raise ValueError(message)


def _ordered_combine(terms, scores, owned=None):
    """Independent FP32 FMA loop; return BF16 only after all selected slots."""
    import torch

    if owned is None:
        result = terms[:, 0].float() * scores[:, 0, None]
        first = 1
    else:
        result = torch.zeros_like(terms[:, 0], dtype=torch.float32)
        first = 0
    for slot in range(first, terms.shape[1]):
        updated = torch.addcmul(
            result, terms[:, slot].float(), scores[:, slot, None], value=1
        )
        result = (
            updated
            if owned is None
            else torch.where(owned[:, slot, None], updated, result)
        )
    return result.bfloat16()


def _a2a_tree_combine(partials, ids, experts_per_rank):
    """Legacy TRTLLM combine: first owner slot, K8 FP32 tree, one BF16 cast.

    moeAlltoAllKernels.cu:506-535,982-1014,1098-1115,1157-1159 at ad0.
    This does not invoke MoeAlltoAll.combine or assume numerical-rank order.
    """
    import torch

    if ids.shape[1] != 8:
        raise ValueError("The independently traced A2A reference requires K8")
    owners = ids.long() // experts_per_rank
    rows = torch.arange(ids.shape[0], device=ids.device)
    slots = []
    for slot in range(8):
        first = (owners[:, :slot] != owners[:, slot, None]).all(dim=1)
        value = partials[owners[:, slot], rows].float()
        slots.append(torch.where(first[:, None], value, 0.0))
    pairs = [slots[i] + slots[i + 1] for i in range(0, 8, 2)]
    return ((pairs[0] + pairs[1]) + (pairs[2] + pairs[3])).bfloat16()


@dataclass
class ContractReference:
    """Only CPU tensors survive construction; no oracle work enters timing."""

    mega: object
    split: object
    partials: object
    hidden_states: object
    topk_ids: object
    topk_weights: object
    counts: tuple[int, ...]
    rank: int
    communication: str
    num_experts: int
    input_contract_passed: bool = False


def build_reference(
    hidden_states, ids, scores, weights, communication, *, gate_up_clamp=None
):
    """Decode canonical weights and independently calculate both contracts.

    Expert terms are limited to 256 global rows at a time. The full independent
    rank partial is needed for one native-shaped NCCL SUM in gather modes;
    all GPU temporaries are released on return. Standard cuBLASLt GEMMs and
    NCCL integer transport/SUM are explicit trusted primitive boundaries.
    """
    import torch

    with torch.no_grad():
        return _build_reference(
            hidden_states,
            ids,
            scores,
            weights,
            communication,
            gate_up_clamp=gate_up_clamp,
        )


def _build_reference(
    hidden_states, ids, scores, weights, communication, *, gate_up_clamp
):
    import torch
    import torch.distributed as dist

    reduction_contract("w4a16", communication)
    matmul = torch.backends.cuda.matmul
    if not hasattr(matmul, "allow_bf16_reduced_precision_reduction_split_k"):
        raise RuntimeError("Independent oracle requires BF16 split-K precision control")
    # Import failures are fatal; a benchmark must not silently skip its oracle.
    import triton  # noqa: F401

    rank = dist.get_rank() if dist.is_initialized() else 0
    world = dist.get_world_size() if dist.is_initialized() else 1
    counts = [None] * world
    if world > 1:
        dist.all_gather_object(counts, hidden_states.shape[0])
    else:
        counts[0] = hidden_states.shape[0]
    layout = token_layout(sum(counts), world)
    _all_rank_guard(
        tuple(counts) == layout.counts,
        hidden_states.device,
        "Oracle expects the benchmark rank-major token partition",
    )
    x, ids, scores = (
        _gather_rows(tensor, counts) for tensor in (hidden_states, ids, scores)
    )
    total, hidden = x.shape
    experts = weights.w13.shape[0]
    intermediate = weights.w2.shape[2] * 2
    _all_rank_guard(
        x.dtype == torch.bfloat16
        and ids.shape == scores.shape == (total, 8)
        and scores.dtype == torch.float32
        and ids.dtype in (torch.int32, torch.int64)
        and weights.w13.dtype == weights.w2.dtype == torch.uint8
        and weights.w13_scale.dtype == weights.w2_scale.dtype == torch.float8_e4m3fn
        and weights.w13.shape == (experts, 2 * intermediate, hidden // 2)
        and weights.w2.shape == (experts, hidden, intermediate // 2)
        and weights.w13_scale.shape == (experts, 2 * intermediate, hidden // 16)
        and weights.w2_scale.shape == (experts, hidden, intermediate // 16),
        x.device,
        "Canonical W4A16 oracle shape/dtype mismatch",
    )
    _all_rank_guard(
        bool(torch.isfinite(x).all())
        and bool(torch.isfinite(scores).all())
        and bool(((ids >= 0) & (ids < experts * world)).all())
        and bool(
            (ids.sort(dim=1).values[:, 1:] != ids.sort(dim=1).values[:, :-1]).all()
        ),
        x.device,
        "Invalid oracle inputs, routes or duplicate route slots",
    )
    positions = torch.tensor(
        layout.padded_positions, dtype=torch.int64, device=x.device
    )
    partials = torch.zeros(
        (layout.padded_tokens, hidden), dtype=torch.bfloat16, device=x.device
    )
    mega_cpu = torch.empty((counts[rank], hidden), dtype=torch.bfloat16)
    a2a_cpu = torch.empty_like(mega_cpu) if communication == "alltoall" else None
    offset = layout.offsets[rank]
    previous_blas = torch.backends.cuda.preferred_blas_library()
    previous_reduction = (
        matmul.allow_bf16_reduced_precision_reduction,
        matmul.allow_bf16_reduced_precision_reduction_split_k,
    )
    previous_tf32 = matmul.allow_tf32
    try:
        torch.backends.cuda.preferred_blas_library("cublaslt")
        matmul.allow_bf16_reduced_precision_reduction = (False, False)
        matmul.allow_tf32 = False
        for start in range(0, total, 256):
            end = min(start + 256, total)
            chunk_ids, chunk_scores = ids[start:end], scores[start:end]
            owned = chunk_ids.long() // experts == rank
            ownership = owned.int()
            if world > 1:
                dist.all_reduce(ownership)
            _all_rank_guard(
                bool((ownership == 1).all()),
                x.device,
                "Every valid route must have exactly one expert owner",
            )
            term_bits = torch.zeros(
                (end - start, 8, hidden), dtype=torch.int32, device=x.device
            )
            for expert in range(experts):
                rows, slots = torch.where(chunk_ids == rank * experts + expert)
                if not rows.numel():
                    continue
                w13 = _dequantize(weights.w13[expert], weights.w13_scale[expert])
                w2 = _dequantize(weights.w2[expert], weights.w2_scale[expert])
                fc1 = torch.mm(x[start:end][rows], w13.T, out_dtype=torch.float32)
                activation = torch.empty(
                    (rows.numel(), intermediate), dtype=torch.bfloat16, device=x.device
                )
                _swiglu_kernel()[((activation.numel() + 255) // 256,)](
                    fc1,
                    None,
                    activation,
                    intermediate,
                    activation.numel(),
                    gate_up_clamp,
                    False,
                )
                fc2 = torch.mm(activation, w2.T, out_dtype=torch.float32)
                # The benchmark's canonical global scale and both expert alphas
                # are one. There is no FC1 route weighting or IKR re-rounding.
                term_bits[rows, slots] = (
                    fc2.bfloat16().view(torch.int16).to(torch.int32)
                )
                del w13, w2, fc1, activation, fc2
            owner_terms = term_bits.to(torch.int16).view(torch.bfloat16)
            partial = _ordered_combine(owner_terms, chunk_scores, owned)
            partials.index_copy_(0, positions[start:end], partial)
            lo, hi = max(start, offset), min(end, offset + counts[rank])
            if communication == "alltoall":
                # Integer transport of independently computed BF16 partial bits;
                # the custom production A2A combine is not used by this oracle.
                partial_bits = partial.view(torch.int16).to(torch.int32)
                all_bits = torch.empty(
                    (world * (end - start), hidden), dtype=torch.int32, device=x.device
                )
                if world > 1:
                    dist.all_gather_into_tensor(all_bits, partial_bits)
                else:
                    all_bits.copy_(partial_bits)
                all_partials = (
                    all_bits.to(torch.int16)
                    .view(torch.bfloat16)
                    .reshape(world, end - start, hidden)
                )
                a2a = _a2a_tree_combine(all_partials, chunk_ids, experts)
                if lo < hi:
                    a2a_cpu[lo - offset : hi - offset].copy_(
                        a2a[lo - start : hi - start].cpu()
                    )
                del partial_bits, all_bits, all_partials, a2a
            if world > 1:
                dist.all_reduce(term_bits)
            terms = term_bits.to(torch.int16).view(torch.bfloat16)
            mega = _ordered_combine(terms, chunk_scores)
            if lo < hi:
                mega_cpu[lo - offset : hi - offset].copy_(
                    mega[lo - start : hi - start].cpu()
                )
            del terms, owner_terms, term_bits, partial, mega
    finally:
        matmul.allow_bf16_reduced_precision_reduction = previous_reduction
        matmul.allow_tf32 = previous_tf32
        torch.backends.cuda.preferred_blas_library(previous_blas)
    if communication == "alltoall":
        split_cpu = a2a_cpu
    else:
        reduced = torch.empty(
            (layout.per_rank_capacity, hidden), dtype=torch.bfloat16, device=x.device
        )
        if world > 1:
            dist.reduce_scatter_tensor(reduced, partials, op=dist.ReduceOp.SUM)
        else:
            reduced.copy_(partials)
        split_cpu = reduced[: counts[rank]].cpu()
    return ContractReference(
        mega_cpu,
        split_cpu,
        partials.cpu(),
        x.cpu(),
        ids.cpu(),
        scores.cpu(),
        tuple(counts),
        rank,
        communication,
        experts * world,
    )


def validate_inputs(reference, hidden_states, ids, scores, *, padded_global=False):
    """Exact input/routing identity; output tolerance cannot waive these checks."""
    import torch

    layout = token_layout(sum(reference.counts), len(reference.counts))
    if padded_global:
        positions = torch.tensor(layout.padded_positions, device=ids.device)
        valid = torch.tensor(layout.valid_mask, device=ids.device)
        actual_x, actual_ids, actual_scores = (
            t.index_select(0, positions).cpu() for t in (hidden_states, ids, scores)
        )
        padding_valid = bool((ids[~valid] == reference.num_experts).all()) and bool(
            (scores[~valid] == 0).all()
        )
        expected = (reference.hidden_states, reference.topk_ids, reference.topk_weights)
    else:
        start = layout.offsets[reference.rank]
        end = start + layout.counts[reference.rank]
        actual_x, actual_ids, actual_scores = (
            t.cpu() for t in (hidden_states, ids, scores)
        )
        expected = tuple(
            t[start:end]
            for t in (
                reference.hidden_states,
                reference.topk_ids,
                reference.topk_weights,
            )
        )
        padding_valid = True
    equal = (
        padding_valid
        and torch.equal(actual_x.view(torch.int16), expected[0].view(torch.int16))
        and torch.equal(actual_ids.long(), expected[1].long())
        and torch.equal(actual_scores.view(torch.int32), expected[2].view(torch.int32))
    )
    _all_rank_guard(
        equal,
        hidden_states.device,
        "Native inputs/routes differ from the independent reference",
    )
    reference.input_contract_passed = True


def a2a_partial_reference(reference, received_x, received_ids, received_scores):
    """Map atomic compact receive order using exact untimed payload identities.

    Dispatch rows are not original token order. No extra dispatch payload or
    production tracking metadata is used. Ambiguous/duplicated/missing payloads
    are rejected rather than choosing a convenient reference permutation.
    """
    import torch

    layout = token_layout(sum(reference.counts), len(reference.counts))
    experts = reference.num_experts // len(reference.counts)
    rank = reference.rank
    # Legacy sanitize fills only unreceived/padding rows with E. Received
    # rows retain the complete original K IDs; MoE sort filters expert owners.
    expected_ids = reference.topk_ids
    owned = (expected_ids.long() // experts == rank).any(dim=1)
    cpu_x, cpu_ids, cpu_scores = (
        tensor.cpu() for tensor in (received_x, received_ids, received_scores)
    )

    def row_bytes(x, ids, scores, row):
        return (
            x[row].contiguous().view(torch.uint8).numpy().tobytes(),
            ids[row].long().contiguous().view(torch.uint8).numpy().tobytes(),
            scores[row].contiguous().view(torch.uint8).numpy().tobytes(),
        )

    error = None
    result = torch.zeros_like(reference.partials)
    try:
        if (
            cpu_x.shape != result.shape
            or cpu_ids.shape != cpu_scores.shape
            or cpu_ids.shape != (layout.padded_tokens, 8)
        ):
            raise ValueError("Unexpected A2A receive shape")
        candidates = {}
        for global_row in owned.nonzero().flatten().tolist():
            payload = row_bytes(
                reference.hidden_states,
                expected_ids,
                reference.topk_weights,
                global_row,
            )
            key = hashlib.sha256(b"".join(payload)).digest()
            if key in candidates:
                raise ValueError("Ambiguous canonical A2A payload identity")
            candidates[key] = (global_row, payload)
        seen = set()
        for recv_row in range(layout.padded_tokens):
            row_ids = cpu_ids[recv_row]
            valid = (row_ids >= 0) & (row_ids < reference.num_experts)
            if not bool(valid.any()):
                if not bool((row_ids == reference.num_experts).all()):
                    raise ValueError("Invalid A2A padding expert sentinel")
                continue
            if not bool((row_ids[valid].long() // experts == rank).any()):
                raise ValueError("Received token has no route owned by this rank")
            payload = row_bytes(cpu_x, cpu_ids, cpu_scores, recv_row)
            key = hashlib.sha256(b"".join(payload)).digest()
            if key not in candidates or candidates[key][1] != payload:
                raise ValueError(
                    "A2A received payload differs from canonical input/routes"
                )
            global_row = candidates[key][0]
            source_rank = recv_row // layout.per_rank_capacity
            if not (
                layout.offsets[source_rank]
                <= global_row
                < layout.offsets[source_rank] + layout.counts[source_rank]
            ):
                raise ValueError("A2A received token is in the wrong source-rank block")
            if global_row in seen:
                raise ValueError("Duplicated A2A received token")
            seen.add(global_row)
            result[recv_row].copy_(
                reference.partials[layout.padded_positions[global_row]]
            )
        if seen != set(owned.nonzero().flatten().tolist()):
            raise ValueError("Missing A2A received token")
    except ValueError as exc:
        error = str(exc)
    _all_rank_guard(
        error is None,
        received_x.device,
        error or "A peer's A2A receive-to-reference mapping failed",
    )
    return result


def _metrics(actual, expected):
    import torch
    import torch.distributed as dist

    _all_rank_guard(
        actual.shape == expected.shape
        and actual.dtype == expected.dtype == torch.bfloat16,
        actual.device,
        "Oracle output shape/dtype mismatch",
    )
    expected = expected.to(actual.device)
    a, b = actual.float(), expected.float()
    error = (a - b).abs()
    nonfinite = ~torch.isfinite(a) | ~torch.isfinite(b)
    invalid = nonfinite | (error > ATOL + RTOL * b.abs())
    maximum = torch.stack(
        (
            invalid.any().float(),
            error.max() if error.numel() else torch.zeros((), device=actual.device),
        )
    )
    totals = torch.stack(
        (
            error.double().square().sum(),
            b.double().square().sum(),
            (actual.view(torch.int16) != expected.view(torch.int16)).sum().double(),
            nonfinite.sum().double(),
        )
    )
    if dist.is_initialized():
        dist.all_reduce(maximum, op=dist.ReduceOp.MAX)
        dist.all_reduce(totals, op=dist.ReduceOp.SUM)
    return {
        "status": "FAIL" if maximum[0].item() else "PASS",
        "atol": ATOL,
        "rtol": RTOL,
        "max_abs": maximum[1].item(),
        "relative_l2": (totals[0] / totals[1].clamp_min(1e-30)).sqrt().item(),
        "bitwise_mismatches": int(totals[2].item()),
        "nonfinite_count": int(totals[3].item()),
    }


def check_output(
    reference, variant, actual, global_tokens, *, partials=None, expected_partials=None
):
    """Print the independent result and fail all ranks together on any failure."""
    import torch.distributed as dist

    expected = reference.split if variant == "w4a16" else reference.mega
    report = _metrics(actual, expected)
    partial_validation = (
        _metrics(
            partials,
            reference.partials if expected_partials is None else expected_partials,
        )
        if partials is not None
        else None
    )
    if partial_validation is not None and partial_validation["status"] != "PASS":
        report["status"] = "FAIL"
    if not reference.input_contract_passed:
        report["status"] = "FAIL"
    report.update(
        variant=variant,
        global_tokens=global_tokens,
        reference_provider=REFERENCE_PROVIDER,
        reference_source_sha256=REFERENCE_SOURCE_SHA256,
        reference_module_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        contract=reduction_contract(variant, reference.communication),
        communication=reference.communication,
        partial_validation=partial_validation,
        input_contract_passed=reference.input_contract_passed,
        trusted_primitives=[
            "cuBLASLt BF16 inputs / FP32 accumulation",
            "NCCL integer-bit transport",
        ]
        + (
            ["NCCL BF16 SUM reduce-scatter"]
            if reference.communication != "alltoall" and variant == "w4a16"
            else []
        ),
    )
    if not dist.is_initialized() or dist.get_rank() == 0:
        print(
            "ORACLE_REFCHECK_JSON,"
            + json.dumps(report, sort_keys=True, separators=(",", ":")),
            flush=True,
        )
    if report["status"] != "PASS":
        raise AssertionError(
            f"Independent {variant} contract oracle failed at atol=rtol=1e-2"
        )
    reference.input_contract_passed = False
    return report
