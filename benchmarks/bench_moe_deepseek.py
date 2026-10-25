#!/usr/bin/env python3
"""DeepSeek-V3 MoE Performance Benchmark - CuteDSL vs CUTLASS vs TRTLLM.

Compares NVFP4, MXFP8, MXFP4 x MXFP8, and BF16 MoE backends:
- CuteDSL W4A4: NVFP4 activations and weights
- CuteDSL W4A16: BF16 activations with NVFP4 weights decoded online
- CuteDSL MXFP8 / W4A8 (opt-in): MXFP8 activations with MXFP8 / MXFP4 weights,
  using the generic split kernels and deterministic unfused combine
- CUTLASS: NVIDIA CUTLASS-based implementation
- TRTLLM NVFP4: TensorRT-LLM's NVFP4 implementation
- TRTLLM MXFP8 / MXFP4 x MXFP8 (opt-in): native block-scaled MoE baselines
- TRTLLM BF16: unquantized BF16 activations and weights

Usage:
    # Separate MXFP8 / MXFP4 x MXFP8 table with matched TRTLLM baselines
    python bench_moe_deepseek.py --quant-family mxfp --ep 8 --no-fused-finalize

    # Throughput benchmark (large batches: 128-4096 tokens)
    python bench_moe_deepseek.py

    # Generation phase benchmark (small batches: 1-128 tokens)
    python bench_moe_deepseek.py --gen-phase

    # With Expert Parallelism simulation
    python bench_moe_deepseek.py --ep 1    # 256 local experts (no parallelism)
    python bench_moe_deepseek.py --ep 8    # 32 local experts (8-way EP)
    python bench_moe_deepseek.py --ep 16   # 16 local experts (16-way EP)

    # With Tensor Parallelism simulation
    python bench_moe_deepseek.py --tp 8    # 256-wide local expert intermediate

    # Custom token counts
    python bench_moe_deepseek.py --num-tokens 64,128,256

    # Include activation quantization for FP4-activation backends
    python bench_moe_deepseek.py --include-activation-quant

    # Compare CuTe DSL W4A4/W4A16 against pure BF16 TRTLLM MoE
    python bench_moe_deepseek.py --backends cutedsl,trtllm-bf16

    # Compare TRTLLM NVFP4 and BF16
    python bench_moe_deepseek.py --backends trtllm-nvfp4,trtllm-bf16

    # Disable CUDA graph (useful for debugging or profiling)
    python bench_moe_deepseek.py --no-cuda-graph

    # Disable CUPTI (use CUDA events for timing instead)
    python bench_moe_deepseek.py --no-cupti

    # Capture one backend for an external CUDA profiler
    python bench_moe_deepseek.py --num-tokens 128 \
        --profile-cuda --profile-backend cute-dsl

    # Nsight Systems: trace individual graph kernels after tuning/warmup.
    # The moe NVTX range excludes the separately labeled cold-L2 flush.
    nsys profile --trace=cuda,nvtx --cuda-graph-trace=node --sample=none \
        --cpuctxsw=none --capture-range=cudaProfilerApi --capture-range-end=stop \
        -o moe_bf16 python bench_moe_deepseek.py --num-tokens 32 --ep 8 \
        --profile-cuda --profile-backend trtllm-bf16 --profile-iters 20

    # CuTe DSL / CUTLASS finalize modes (TRTLLM keeps its native finalize)
    python bench_moe_deepseek.py --functional-api  # fused allowed (default)
    python bench_moe_deepseek.py --functional-api --no-fused-finalize  # deterministic

Metrics:
    - ms: Latency in milliseconds
    - TFLOPS: Computational throughput
    - Speedup: other backend latency / CuteDSL latency (>1 = CuteDSL faster)
"""

import argparse
import contextlib
import gc
import os
from dataclasses import dataclass
import numpy as np
import torch


@dataclass
class DeepSeekConfig:
    hidden_size: int = 7168
    intermediate_size: int = 2048
    num_experts: int = 256
    n_group: int = 8
    topk_group: int = 4
    top_k: int = 8
    routed_scaling_factor: float = 2.5


CFG = DeepSeekConfig()
BASE_INTERMEDIATE_SIZE = CFG.intermediate_size
TOKEN_COUNTS = [128, 256, 512, 1024, 2048, 4096]

# Generation phase token counts (small batches typical in decode)
GEN_PHASE_TOKENS = [1, 2, 4, 8, 16, 32, 64, 128]

# Expert Parallelism configurations
# EP=1: all 256 experts on single GPU
# EP=8: 32 experts per GPU (256/8)
# EP=16: 16 experts per GPU (256/16)
EP_CONFIGS = {
    1: {"num_local_experts": 256, "local_expert_offset": 0},
    2: {"num_local_experts": 128, "local_expert_offset": 0},
    4: {"num_local_experts": 64, "local_expert_offset": 0},
    8: {"num_local_experts": 32, "local_expert_offset": 0},
    16: {"num_local_experts": 16, "local_expert_offset": 0},
}


def _autotune_context(do_autotune, cache):
    """Create a tuning, cache-only, or ordinary no-cache benchmark scope."""
    from flashinfer.autotuner import autotune

    if cache is not None:
        return autotune(do_autotune, cache=cache)
    if do_autotune:
        return autotune(True)
    return contextlib.nullcontext()


def is_sm100_family():
    """Check for SM100 family (Blackwell: SM100, SM103).

    CuteDSL MoE NVFP4 kernels are optimized for SM10x architecture.
    """
    if not torch.cuda.is_available():
        return False
    props = torch.cuda.get_device_properties(0)
    return props.major == 10


def calc_tflops(n, ms, num_local_experts=None):
    """Calculate TFLOPS for MoE computation.

    With EP, only tokens routed to local experts are computed.
    Assumes uniform routing distribution across experts.
    """
    if num_local_experts is None:
        num_local_experts = CFG.num_experts

    # Fraction of work done locally (assuming uniform distribution)
    local_fraction = num_local_experts / CFG.num_experts

    flops = (
        n
        * CFG.top_k
        * local_fraction  # Only local expert pairs are computed
        * (
            2 * CFG.hidden_size * 2 * CFG.intermediate_size
            + 2 * CFG.intermediate_size * CFG.hidden_size
        )
    )
    return flops / (ms * 1e-3) / 1e12


def interleave(x, gs=64):
    M, K = x.shape[-2], x.shape[-1]
    return (
        x.view(*x.shape[:-2], 2, M // (gs * 2), gs, K)
        .transpose(-4, -3)
        .contiguous()
        .view(*x.shape)
    )


def create_inputs(n, dev="cuda", routing_bias_scale=0.01):
    """Create inputs for all backends (CuteDSL, CUTLASS, TRTLLM)."""
    from flashinfer.fp4_quantization import fp4_quantize

    torch.manual_seed(42)
    sv = 16
    FP8M = torch.finfo(torch.float8_e4m3fn).max
    FP4M = 6.0

    # Router logits and bias
    rl = torch.randn(n, CFG.num_experts, device=dev, dtype=torch.float32)
    rb = (
        torch.randn(CFG.num_experts, device=dev, dtype=torch.bfloat16)
        * routing_bias_scale
    )

    # Hidden states
    hb = torch.randn(n, CFG.hidden_size, device=dev, dtype=torch.bfloat16) / 10
    hg = FP8M * FP4M / hb.abs().max().float()

    # Weights (BF16)
    w1b = (
        torch.randn(
            CFG.num_experts,
            2 * CFG.intermediate_size,
            CFG.hidden_size,
            device=dev,
            dtype=torch.bfloat16,
        )
        / 10
    )
    w2b = (
        torch.randn(
            CFG.num_experts,
            CFG.hidden_size,
            CFG.intermediate_size,
            device=dev,
            dtype=torch.bfloat16,
        )
        / 10
    )

    # Compute per-expert global scales
    w1_gs_list, w2_gs_list = [], []
    for e in range(CFG.num_experts):
        w1_gs_list.append(FP8M * FP4M / w1b[e].abs().max().float())
        w2_gs_list.append(FP8M * FP4M / w2b[e].abs().max().float())
    w1_gs = torch.tensor(w1_gs_list, device=dev)
    w2_gs = torch.tensor(w2_gs_list, device=dev)

    # CUTLASS format: quantize with swizzled scale factors
    w1_fp4_list, w1_sf_list = [], []
    w2_fp4_list, w2_sf_list = [], []
    for e in range(CFG.num_experts):
        q1, s1 = fp4_quantize(w1b[e], w1_gs[e], sv, False, True)  # swizzled
        w1_fp4_list.append(q1)
        w1_sf_list.append(s1)
        q2, s2 = fp4_quantize(w2b[e], w2_gs[e], sv, False, True)  # swizzled
        w2_fp4_list.append(q2)
        w2_sf_list.append(s2)

    return {
        "router_logits": rl,
        "routing_bias": rb,
        "hidden_bf16": hb,
        "hidden_gs": hg,
        "w1_bf16": w1b,
        "w1_gs": w1_gs,
        "w2_bf16": w2b,
        "w2_gs": w2_gs,
        # CUTLASS specific
        "w1_fp4": torch.stack(w1_fp4_list),
        "w1_sf": torch.stack(w1_sf_list),
        "w2_fp4": torch.stack(w2_fp4_list),
        "w2_sf": torch.stack(w2_sf_list),
    }


# =============================================================================
# Benchmark Functions
# =============================================================================


def _measure_or_profile(
    run,
    input_kwargs,
    warmup,
    iters,
    use_cuda_graph,
    use_cupti,
    profile_cuda,
    profile_iters,
):
    from flashinfer.testing.utils import bench_gpu_time, get_l2_cache_size

    da_capture = use_cuda_graph and os.getenv(
        "FLASHINFER_DIST_AWARE_AUTOTUNE", "0"
    ).lower() not in ("", "0", "false", "no", "off", "none")

    if not profile_cuda and da_capture:
        from flashinfer.fused_moe import trtllm_moe_acquire_da_graph_leases

        graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):
            run(**input_kwargs)
        leases = trtllm_moe_acquire_da_graph_leases(graph)
        l2_flush = torch.empty(2 * get_l2_cache_size(), device="cuda", dtype=torch.int8)
        times = []
        try:
            for _ in range(warmup):
                graph.replay()
            torch.cuda.synchronize()
            start = torch.cuda.Event(enable_timing=True)
            end = torch.cuda.Event(enable_timing=True)
            for _ in range(iters):
                l2_flush.zero_()
                torch.cuda.synchronize()
                start.record()
                graph.replay()
                end.record()
                end.synchronize()
                times.append(start.elapsed_time(end))
        finally:
            torch.cuda.synchronize()
            graph.reset()
            for lease in leases:
                lease.release()
        return np.median(times)

    if not profile_cuda:
        times = bench_gpu_time(
            run,
            dry_run_iters=warmup,
            repeat_iters=iters,
            cold_l2_cache=True,
            enable_cupti=use_cupti,
            use_cuda_graph=use_cuda_graph,
            input_kwargs=input_kwargs,
        )
        return np.median(times)

    def runner():
        return run(**input_kwargs)

    leases = ()
    if use_cuda_graph:
        from flashinfer.fused_moe import trtllm_moe_acquire_da_graph_leases

        graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):
            run(**input_kwargs)
        leases = trtllm_moe_acquire_da_graph_leases(graph)
        runner = graph.replay
    for _ in range(3):
        runner()
    torch.cuda.synchronize()

    l2_flush = torch.empty(2 * get_l2_cache_size(), device="cuda", dtype=torch.int8)
    torch.cuda.cudart().cudaProfilerStart()
    for _ in range(profile_iters):
        with torch.cuda.nvtx.range("l2_flush"):
            l2_flush.zero_()
            torch.cuda.synchronize()
        with torch.cuda.nvtx.range("moe"):
            runner()
            torch.cuda.synchronize()
    torch.cuda.cudart().cudaProfilerStop()
    if use_cuda_graph:
        torch.cuda.synchronize()
        graph.reset()
        for lease in leases:
            lease.release()
    return float("nan")


def bench_cute_dsl(
    inputs,
    warmup=10,
    iters=100,
    num_local_experts=None,
    local_expert_offset=0,
    use_cuda_graph=True,
    use_cupti=True,
    use_wrapper=False,
    do_autotune=True,
    quant_mode="w4a4",
    use_per_token_activation=False,
    include_activation_quant=False,
    use_fused_finalize=True,
    profile_cuda=False,
    profile_iters=10,
    autotune_cache=None,
):
    """Benchmark CuteDSL MoE.

    Args:
        use_wrapper: For NV modes, select CuteDslMoEWrapper (recommended
            for CUDA graph) or cute_dsl_fused_moe. MX modes use the generic
            split kernels because their public API lacks unfused finalize.
        do_autotune: If True, run the pre-warm pass under autotune(True) so the
                    autotuner profiles all buckets and populates its cache. The
                    measurement loop runs OUTSIDE the autotune context so that
                    choose_one cache lookups don't appear inside the CUDA-event
                    interval when bench_gpu_time falls back to events (i.e. when
                    both CUDA graphs and CUPTI are disabled).
        quant_mode: ``"w4a4"``, ``"w4a16"``, ``"mxfp8"``, or ``"w4a8"``.
            MX modes use generic split kernels with deterministic combine.
        use_fused_finalize: Use atomic fused finalize; otherwise use the
            deterministic two-stage finalize.
        include_activation_quant: Include the initial activation FP4
            quantization in the measured CuTe DSL W4A4 path. W4A16 consumes
            BF16 activations directly, so this option does not affect it.
        profile_cuda: Capture steady-state CUDA graph replays between
            cudaProfilerStart/Stop instead of benchmarking.
        profile_iters: Number of cold-L2 graph replays to capture.
    """
    from flashinfer.fused_moe import fused_topk_deepseek
    from flashinfer.fused_moe.prepare import _cute_dsl_gated_weight_group_size
    from flashinfer.cute_dsl.utils import convert_sf_to_mma_layout
    from flashinfer.fp4_quantization import fp4_quantize

    if num_local_experts is None:
        num_local_experts = CFG.num_experts
    if quant_mode not in ("w4a4", "w4a16", "mxfp8", "w4a8"):
        raise ValueError(f"Unsupported CuTe DSL quant mode: {quant_mode}")
    if quant_mode in ("mxfp8", "w4a8") and (
        use_fused_finalize or use_per_token_activation or include_activation_quant
    ):
        raise ValueError(
            "CuTe DSL MX modes require unfused finalize and prequantized activations"
        )

    n, dev = inputs["router_logits"].shape[0], inputs["hidden_bf16"].device
    expert_start = local_expert_offset
    expert_end = local_expert_offset + num_local_experts
    w1_local = inputs["w1_bf16"][expert_start:expert_end]
    w2_local = inputs["w2_bf16"][expert_start:expert_end]
    gated_group_size = _cute_dsl_gated_weight_group_size(dev)
    tv = torch.empty(n, CFG.top_k, dtype=torch.float32, device=dev)
    ti = torch.empty(n, CFG.top_k, dtype=torch.int32, device=dev)
    alpha = torch.ones(num_local_experts, dtype=torch.float32, device=dev)
    routing_bias_f32 = inputs["routing_bias"].float()

    if quant_mode in ("w4a4", "w4a16"):
        from flashinfer import SfLayout, nvfp4_quantize
        from flashinfer.quantization.nvfp4_quantization_utils import (
            current_nvfp4_4over6_config,
            make_nvfp4_global_scale,
        )

        sv = 16
        gs1 = torch.tensor([1.0], device=dev)

        activation_global_scale = None
        if quant_mode == "w4a4":
            activation_global_scale = (
                make_nvfp4_global_scale(
                    inputs["hidden_bf16"],
                    per_token_activation=True,
                    nvfp4_4over6_config=current_nvfp4_4over6_config(),
                )
                if use_per_token_activation
                else gs1
            )

        if quant_mode == "w4a16" or include_activation_quant:
            xf = inputs["hidden_bf16"]
            xs = None
            hidden_per_token_scale = None
        elif use_per_token_activation:
            xf, xs, hidden_per_token_scale = nvfp4_quantize(
                inputs["hidden_bf16"],
                activation_global_scale,
                sfLayout=SfLayout.layout_linear,
                per_token_activation=True,
                backend="cute-dsl",
            )
        else:
            xf, xs = fp4_quantize(inputs["hidden_bf16"], gs1, sv, False, False)
            hidden_per_token_scale = None
        if xs is not None:
            xs = xs.unsqueeze(-1)

        def prepare_activation(x, x_sf):
            per_token_scale = hidden_per_token_scale
            if quant_mode == "w4a16":
                return x, None, None
            if include_activation_quant:
                if use_per_token_activation:
                    x, x_sf, per_token_scale = nvfp4_quantize(
                        x,
                        activation_global_scale,
                        sfLayout=SfLayout.layout_linear,
                        per_token_activation=True,
                        backend="cute-dsl",
                    )
                else:
                    x, x_sf = fp4_quantize(x, gs1, sv, False, False, backend="cute-dsl")
                x_sf = x_sf.unsqueeze(-1)
            return x, x_sf, per_token_scale

        w1i = interleave(w1_local, gated_group_size)
        w1f = w1i.view(num_local_experts * 2 * CFG.intermediate_size, CFG.hidden_size)
        w1q, w1s = fp4_quantize(w1f, gs1, sv, False, True)
        w1q = w1q.view(
            num_local_experts, 2 * CFG.intermediate_size, CFG.hidden_size // 2
        )
        w1s = convert_sf_to_mma_layout(
            w1s, 2 * CFG.intermediate_size, CFG.hidden_size, num_local_experts, sv
        )

        w2f = w2_local.view(num_local_experts * CFG.hidden_size, CFG.intermediate_size)
        w2q, w2s = fp4_quantize(w2f, gs1, sv, False, True)
        w2q = w2q.view(num_local_experts, CFG.hidden_size, CFG.intermediate_size // 2)
        w2s = convert_sf_to_mma_layout(
            w2s, CFG.hidden_size, CFG.intermediate_size, num_local_experts, sv
        )

        fc2sc = None if quant_mode == "w4a16" else torch.tensor([1.0], device=dev)

        if use_wrapper:
            # Use CuteDslMoEWrapper (recommended for CUDA graph)
            from flashinfer import CuteDslMoEWrapper

            moe = CuteDslMoEWrapper(
                num_experts=CFG.num_experts,
                top_k=CFG.top_k,
                hidden_size=CFG.hidden_size,
                intermediate_size=CFG.intermediate_size,
                use_cuda_graph=use_cuda_graph,
                max_num_tokens=n,
                num_local_experts=num_local_experts,
                local_expert_offset=local_expert_offset,
                use_fused_finalize=use_fused_finalize,
                quant_mode=quant_mode,
            )

            def run_moe(x, x_sf, topk_values, topk_indices, per_token_scale):
                return moe.run(
                    x=x,
                    x_sf=x_sf,
                    token_selected_experts=topk_indices,
                    token_final_scales=topk_values,
                    w1_weight=w1q,
                    w1_weight_sf=w1s,
                    w1_alpha=alpha,
                    fc2_input_scale=fc2sc,
                    w2_weight=w2q,
                    w2_weight_sf=w2s,
                    w2_alpha=alpha,
                    per_token_scale=per_token_scale,
                )
        else:
            # Use functional API
            from flashinfer import cute_dsl_fused_moe

            def run_moe(x, x_sf, topk_values, topk_indices, per_token_scale):
                return cute_dsl_fused_moe(
                    x=x,
                    x_sf=x_sf,
                    token_selected_experts=topk_indices,
                    token_final_scales=topk_values,
                    w1_weight=w1q,
                    w1_weight_sf=w1s,
                    w1_alpha=alpha,
                    fc2_input_scale=fc2sc,
                    w2_weight=w2q,
                    w2_weight_sf=w2s,
                    w2_alpha=alpha,
                    num_experts=CFG.num_experts,
                    top_k=CFG.top_k,
                    num_local_experts=num_local_experts,
                    local_expert_offset=local_expert_offset,
                    quant_mode=quant_mode,
                    per_token_scale=per_token_scale,
                    use_fused_finalize=use_fused_finalize,
                )

    elif quant_mode in ("mxfp8", "w4a8"):
        import cutlass

        from flashinfer import mxfp8_quantize
        from flashinfer.autotuner import AutoTuner, TunableRunner
        from flashinfer.fused_moe.prepare import _interleave_linear_and_gate
        from flashinfer.fused_moe.cute_dsl.blockscaled_contiguous_gather_grouped_gemm_act_fusion import (
            blockscaled_contiguous_gather_grouped_gemm_act_fusion as fc1,
        )
        from flashinfer.fused_moe.cute_dsl.blockscaled_contiguous_grouped_gemm_finalize_fusion import (
            blockscaled_contiguous_grouped_gemm_finalize_fusion as fc2,
        )
        from flashinfer.fused_moe.cute_dsl.blackwell.blockscaled_contiguous_gather_grouped_gemm_act_fusion import (
            BlockScaledContiguousGatherGroupedGemmKernel as Fc1Kernel,
        )
        from flashinfer.fused_moe.cute_dsl.blackwell.blockscaled_contiguous_grouped_gemm_finalize_fusion import (
            Sm100BlockScaledContiguousGroupedGemmFinalizeFusionKernel as Fc2Kernel,
        )
        from flashinfer.fused_moe.cute_dsl.blackwell.moe_finalize import moe_unpermute
        from flashinfer.fused_moe.cute_dsl.moe_utils import (
            allocate_moe_sort_buffers,
            get_max_num_permuted_tokens,
            moe_sort,
        )
        from flashinfer.fused_moe.cute_dsl.tuner import (
            CuteDslFusedMoERunner,
            get_blackwell_moe_valid_tactics,
            get_w4a8_moe_valid_tactics,
        )

        weight_format = "mxfp8" if quant_mode == "mxfp8" else "mxfp4"
        if weight_format == "mxfp8":
            weight_dtype = "float8_e4m3fn"
            weight_cutlass_dtype = cutlass.Float8E4M3FN
            all_tactics = get_blackwell_moe_valid_tactics()
        elif weight_format == "mxfp4":
            weight_dtype = "float4_e2m1fn"
            weight_cutlass_dtype = cutlass.Float4E2M1FN
            all_tactics = get_w4a8_moe_valid_tactics()
        else:
            raise ValueError(f"unsupported weight format: {weight_format}")
        device = dev
        architecture = torch.cuda.get_device_capability(device)
        xf, xs = mxfp8_quantize(
            inputs["hidden_bf16"],
            is_sf_swizzled_layout=False,
            alignment=128,
            backend="cuda",
        )
        xs = xs.view(torch.uint8).reshape(n, CFG.hidden_size // 32)
        global_scale = torch.ones(1, dtype=torch.float32, device=device)

        def quantize_weight(weight):
            experts, channels, reduction = weight.shape
            flat = weight.reshape(-1, reduction)
            if weight_format == "mxfp8":
                quantized, scales = mxfp8_quantize(
                    flat,
                    is_sf_swizzled_layout=True,
                    alignment=128,
                    backend="cuda",
                )
            elif weight_format == "mxfp4":
                quantized, scales = fp4_quantize(
                    flat,
                    global_scale=global_scale,
                    sf_vec_size=32,
                    sf_use_ue8m0=True,
                    is_sf_swizzled_layout=True,
                    backend="cuda",
                )
            else:
                raise ValueError(weight_format)
            return quantized.reshape(experts, channels, -1), convert_sf_to_mma_layout(
                scales.view(torch.uint8), channels, reduction, experts, 32
            )

        w1, w1_sf = quantize_weight(
            _interleave_linear_and_gate(
                w1_local,
                group_size=gated_group_size,
                dim=1,
            )
        )
        w2, w2_sf = quantize_weight(w2_local)
        output = torch.empty((n, CFG.hidden_size), dtype=torch.bfloat16, device=device)

        # Only borrow the native policy/seeded routing helper. The native runner's
        # forward and tactic filtering assume packed FP4 weights, so neither is used.
        policy = CuteDslFusedMoERunner(
            forward_impl=None,
            num_experts=CFG.num_experts,
            top_k=CFG.top_k,
            num_local_experts=num_local_experts,
            local_expert_offset=local_expert_offset,
            use_fused_finalize=False,
            output_dtype=torch.bfloat16,
            enable_pdl=True,
            quant_mode="w4a4",
            use_cuda_graph=use_cuda_graph,
        )

        class SplitMxfp8Runner(TunableRunner):
            def __init__(self):
                self.workspace_cache = {}
                self.tuning_config = policy.tuning_config

            def __hash__(self):
                # Keep bucket reuse stable across token points, like the native
                # runner. TuningConfig contains fresh initializer closures whose
                # identities must not become part of the runner cache key.
                return hash(self.get_cache_key_extras(None))

            def get_cache_key_extras(self, tensors):
                return (
                    "benchmark_split_mxfp8_v2",
                    architecture,
                    tuple(all_tactics),
                    weight_format,
                    gated_group_size,
                    CFG.num_experts,
                    num_local_experts,
                    local_expert_offset,
                    CFG.top_k,
                    "swiglu",
                    "bf16_unfused",
                    "pdl",
                    use_cuda_graph,
                )

            def get_valid_tactics(self, tensors, profile):
                tokens = tensors[0].shape[0]
                valid = []
                for tactic in all_tactics:
                    route_tile, gemm1, gemm2 = tactic
                    capacity = get_max_num_permuted_tokens(
                        tokens, CFG.top_k, num_local_experts, route_tile
                    )
                    common = dict(
                        a_dtype=cutlass.Float8E4M3FN,
                        b_dtype=weight_cutlass_dtype,
                        sf_dtype=cutlass.Float8E8M0FNU,
                        sf_vec_size=32,
                        m=capacity,
                        l=num_local_experts,
                        a_major="k",
                        b_major="k",
                    )
                    gemm1_ok = Fc1Kernel.can_implement(
                        **common,
                        c_dtype=cutlass.Float8E4M3FN,
                        c_major="n",
                        n=2 * CFG.intermediate_size,
                        k=CFG.hidden_size,
                        mma_tiler_mn=gemm1[0],
                        cluster_shape_mn=gemm1[1],
                    )
                    gemm2_ok = Fc2Kernel.can_implement(
                        **common,
                        out_dtype=cutlass.BFloat16,
                        out_major="n",
                        final_scale_dtype=cutlass.Float32,
                        n=CFG.hidden_size,
                        k=CFG.intermediate_size,
                        mma_tiler_mn=gemm2[0],
                        cluster_shape_mn=gemm2[1],
                    )
                    if gemm1_ok and gemm2_ok:
                        valid.append(tactic)
                return valid

            def workspace(self, tokens, route_tile):
                key = (tokens, route_tile)
                if key not in self.workspace_cache:
                    sort = allocate_moe_sort_buffers(
                        tokens,
                        CFG.num_experts,
                        CFG.top_k,
                        num_local_experts,
                        route_tile,
                        device,
                    )
                    capacity = sort["out_permuted_idx_to_expanded_idx"].numel()
                    intermediate = torch.empty(
                        (capacity, CFG.intermediate_size),
                        dtype=torch.float8_e4m3fn,
                        device=device,
                    )
                    intermediate_sf = torch.empty(
                        (
                            32,
                            4,
                            (capacity + 127) // 128,
                            4,
                            (CFG.intermediate_size + 127) // 128,
                            1,
                        ),
                        dtype=torch.uint8,
                        device=device,
                    )
                    expanded = torch.empty(
                        (tokens * CFG.top_k, CFG.hidden_size),
                        dtype=torch.bfloat16,
                        device=device,
                    )
                    self.workspace_cache[key] = (
                        sort,
                        intermediate,
                        intermediate_sf,
                        expanded,
                    )
                return self.workspace_cache[key]

            def forward(self, tensors, tactic=-1, do_preparation=False, **kwargs):
                if tactic == -1:
                    valid = self.get_valid_tactics(tensors, None)
                    if not valid:
                        raise RuntimeError(
                            f"no supported unfused {weight_format} tactics"
                        )
                    tactic = valid[0]
                route_tile, gemm1, gemm2 = tactic
                tokens = tensors[0].shape[0]
                sort, intermediate, intermediate_sf, expanded = self.workspace(
                    tokens, route_tile
                )
                if do_preparation:
                    return None
                expert_idx, limits, reverse, mapping, _, num_tiles = moe_sort(
                    token_selected_experts=tensors[2],
                    token_final_scales=tensors[3],
                    num_experts=CFG.num_experts,
                    top_k=CFG.top_k,
                    local_expert_offset=local_expert_offset,
                    num_local_experts=num_local_experts,
                    tile_tokens_dim=route_tile,
                    enable_pdl=True,
                    **sort,
                )
                common = dict(
                    tile_idx_to_expert_idx=expert_idx,
                    tile_idx_to_mn_limit=limits,
                    num_non_exiting_tiles=num_tiles,
                    a_dtype="float8_e4m3fn",
                    b_dtype=weight_dtype,
                    sf_dtype="float8_e8m0fnu",
                    sf_vec_size=32,
                    enable_pdl=True,
                )
                fc1(
                    a=tensors[0],
                    b=tensors[4],
                    a_scale=tensors[1],
                    b_scale=tensors[5],
                    alpha=tensors[6],
                    token_id_mapping=mapping,
                    topk=CFG.top_k,
                    out=intermediate,
                    out_scale=intermediate_sf,
                    c_dtype="float8_e4m3fn",
                    quantize_output=True,
                    global_scale=None,
                    mma_tiler_mn=gemm1[0],
                    cluster_shape_mn=gemm1[1],
                    raster_along_m=gemm1[2],
                    **common,
                )
                fc2(
                    a=intermediate,
                    b=tensors[8],
                    a_scale=intermediate_sf,
                    b_scale=tensors[9],
                    alpha=tensors[10],
                    permuted_idx_to_expanded_idx=mapping,
                    token_final_scales=tensors[3],
                    out=expanded,
                    out_dtype="bfloat16",
                    use_fused_finalize=False,
                    mma_tiler_mn=gemm2[0],
                    cluster_shape_mn=gemm2[1],
                    raster_along_m=gemm2[2],
                    **common,
                )
                moe_unpermute(
                    permuted_input=expanded,
                    output=tensors[11],
                    expanded_idx_to_permuted_idx=reverse,
                    topk_scales=tensors[3],
                    num_tokens=tokens,
                    top_k=CFG.top_k,
                    input_is_expanded=True,
                    enable_pdl=True,
                )
                return tensors[11]

        runner = SplitMxfp8Runner()

        def prepare_activation(x, x_sf):
            return x, x_sf, None

        def run_moe(x, x_sf, topk_values, topk_indices, per_token_scale):
            tensors = [
                x,
                x_sf,
                topk_indices,
                topk_values,
                w1,
                w1_sf,
                alpha,
                None,
                w2,
                w2_sf,
                alpha,
                output,
            ]
            selected_runner, tactic = AutoTuner.get().choose_one(
                f"BenchmarkSplitMxfp8::{weight_format}",
                [runner],
                runner.tuning_config,
                tensors,
            )
            return selected_runner(tensors, tactic=tactic)

    else:
        raise ValueError(f"Unsupported CuTe DSL quant mode: {quant_mode}")

    def run(x, x_sf, router_logits, routing_bias, topk_values, topk_indices):
        x, x_sf, per_token_scale = prepare_activation(x, x_sf)
        fused_topk_deepseek(
            scores=router_logits,
            bias=routing_bias,
            n_group=CFG.n_group,
            topk_group=CFG.topk_group,
            topk=CFG.top_k,
            routed_scaling_factor=CFG.routed_scaling_factor,
            topk_values=topk_values,
            topk_indices=topk_indices,
        )
        return run_moe(x, x_sf, topk_values, topk_indices, per_token_scale)

    # Pass input tensors via input_kwargs for cold L2 cache rotation
    input_kwargs = {
        "x": xf,
        "x_sf": xs,
        "router_logits": inputs["router_logits"],
        "routing_bias": routing_bias_f32,
        "topk_values": tv,
        "topk_indices": ti,
    }

    # Pre-warm: run once on the default stream so that autotuning (which
    # allocates tensors and profiles multiple tactics) finishes before
    # bench_gpu_time moves execution to a side stream for CUDA-graph
    # capture.  Autotuning on a non-default stream triggers illegal-
    # memory-access errors in the CuteDSL persistent-tile-scheduler
    # kernels.  Autotune is scoped to the pre-warm only — bench_gpu_time
    # runs outside the autotune context so that choose_one in the
    # measurement loop returns the cached tactic via the non-tuning fast
    # path (no host-side tactic-walking inside the CUDA-event interval).
    with _autotune_context(do_autotune, autotune_cache):
        run(**input_kwargs)
        torch.cuda.synchronize()

    return _measure_or_profile(
        run,
        input_kwargs,
        warmup,
        iters,
        use_cuda_graph,
        use_cupti,
        profile_cuda,
        profile_iters,
    )


def bench_cutlass(
    inputs,
    warmup=10,
    iters=100,
    num_local_experts=None,
    local_expert_offset=0,
    use_cuda_graph=True,
    use_cupti=True,
    do_autotune=True,
    include_activation_quant=False,
    use_fused_finalize=True,
    profile_cuda=False,
    profile_iters=10,
    autotune_cache=None,
):
    """Benchmark CUTLASS MoE.

    Args:
        do_autotune: See ``bench_cute_dsl`` for the autotune-scope rationale.
        use_fused_finalize: Allow fused-finalize tactics when True; exclude
            them when False. Autotuning may still choose an unfused tactic.
    """
    from flashinfer.fused_moe import fused_topk_deepseek, cutlass_fused_moe
    from flashinfer.fp4_quantization import fp4_quantize

    if num_local_experts is None:
        num_local_experts = CFG.num_experts

    n, sv, dev = inputs["router_logits"].shape[0], 16, "cuda"

    tv = torch.empty(n, CFG.top_k, dtype=torch.float32, device=dev)
    ti = torch.empty(n, CFG.top_k, dtype=torch.int32, device=dev)

    # Expert range for this EP partition
    expert_start = local_expert_offset
    expert_end = local_expert_offset + num_local_experts

    # Slice weights to LOCAL experts only (for fair EP comparison)
    w1_fp4_local = inputs["w1_fp4"][expert_start:expert_end]
    w1_sf_local = inputs["w1_sf"][expert_start:expert_end]
    w1_gs_local = inputs["w1_gs"][expert_start:expert_end]
    w2_fp4_local = inputs["w2_fp4"][expert_start:expert_end]
    w2_sf_local = inputs["w2_sf"][expert_start:expert_end]
    w2_gs_local = inputs["w2_gs"][expert_start:expert_end]

    # Prepare CUTLASS inputs
    a1_gs = torch.tensor(1.0, device=dev, dtype=torch.float32)
    a2_gs = torch.tensor(1.0, device=dev, dtype=torch.float32)

    quant_scales = [
        a1_gs,
        w1_sf_local.view(torch.int32),
        1.0 / (a1_gs * w1_gs_local),
        a2_gs,
        w2_sf_local.view(torch.int32),
        1.0 / (a2_gs * w2_gs_local),
    ]

    hidden_fp4, input_sf = fp4_quantize(inputs["hidden_bf16"], a1_gs, sv, False, True)
    output = torch.empty(n, CFG.hidden_size, dtype=torch.bfloat16, device=dev)

    # Pre-convert routing bias to float32
    routing_bias_f32 = inputs["routing_bias"].float()

    # Pre-compute values that need conversion
    w1_fp4_view = w1_fp4_local.contiguous().view(torch.long)
    w2_fp4_view = w2_fp4_local.contiguous().view(torch.long)

    # Compute EP size from config
    ep_size = CFG.num_experts // num_local_experts

    def run(hidden, sf, router_logits, routing_bias, topk_values, topk_indices):
        if include_activation_quant:
            hidden, sf = fp4_quantize(hidden, a1_gs, sv, False, True)
        # Routing (included in timing for fair comparison with TRTLLM)
        fused_topk_deepseek(
            scores=router_logits,
            bias=routing_bias,
            n_group=CFG.n_group,
            topk_group=CFG.topk_group,
            topk=CFG.top_k,
            routed_scaling_factor=CFG.routed_scaling_factor,
            topk_values=topk_values,
            topk_indices=topk_indices,
        )
        cutlass_fused_moe(
            hidden,
            topk_indices.to(torch.int),
            topk_values,
            w1_fp4_view,
            w2_fp4_view,
            torch.bfloat16,
            quant_scales=quant_scales,
            input_sf=sf,
            output=output,
            ep_size=ep_size,
            ep_rank=0,  # Simulating rank 0 of EP
            use_fused_finalize=use_fused_finalize,
        )
        return output

    input_kwargs = {
        "hidden": inputs["hidden_bf16"] if include_activation_quant else hidden_fp4,
        "sf": None if include_activation_quant else input_sf,
        "router_logits": inputs["router_logits"],
        "routing_bias": routing_bias_f32,
        "topk_values": tv,
        "topk_indices": ti,
    }

    # Pre-warm under autotune; measurement runs outside (see bench_cute_dsl).
    with _autotune_context(do_autotune, autotune_cache):
        run(**input_kwargs)
        torch.cuda.synchronize()

    return _measure_or_profile(
        run,
        input_kwargs,
        warmup,
        iters,
        use_cuda_graph,
        use_cupti,
        profile_cuda,
        profile_iters,
    )


def bench_trtllm(
    inputs,
    warmup=10,
    iters=100,
    num_local_experts=None,
    local_expert_offset=0,
    use_cuda_graph=True,
    use_cupti=True,
    do_autotune=True,
    use_per_token_activation=False,
    include_activation_quant=False,
    profile_cuda=False,
    profile_iters=10,
    autotune_cache=None,
    routing_input_mode="logits",
    distributions=("uniform",),
    precision="nvfp4",
):
    """Benchmark TRTLLM quantized or pure BF16 MoE with native finalize.

    Args:
        do_autotune: See ``bench_cute_dsl`` for the autotune-scope rationale.
        precision: ``"nvfp4"``, ``"mxfp8"``, ``"mxfp4"`` (MXFP4 weights
            with MXFP8 activations), or ``"bf16"``. Weight preparation is
            outside timing. NVFP4 per-token/4over6 flags do not affect the
            MX modes or BF16.
    """
    from flashinfer.fused_moe import RoutingMethodType
    from flashinfer.fused_moe.da_tuner import (
        RoutingRealizationFactory,
        RoutingRealizationKey,
    )

    if num_local_experts is None:
        num_local_experts = CFG.num_experts

    n, dev = inputs["router_logits"].shape[0], inputs["router_logits"].device
    expert_start = local_expert_offset
    expert_end = local_expert_offset + num_local_experts
    input_kwargs = {
        "routing_logits": inputs["router_logits"],
        "routing_bias": inputs["routing_bias"],
        "hidden_states": inputs["hidden_bf16"],
    }
    moe_kwargs = dict(
        num_experts=CFG.num_experts,
        top_k=CFG.top_k,
        n_group=CFG.n_group,
        topk_group=CFG.topk_group,
        intermediate_size=CFG.intermediate_size,
        local_expert_offset=local_expert_offset,
        local_num_experts=num_local_experts,
        do_finalize=True,
    )

    if precision == "bf16":
        from flashinfer.fused_moe import (
            TrtllmBf16Config,
            trtllm_bf16_moe,
            trtllm_bf16_routed_moe,
        )

        # Canonical [up, gate] weights need both the gated row reorder and
        # BlockMajorK shuffle. The public helper preserves their BF16 values.
        weights = TrtllmBf16Config.prepare_weights(
            inputs["w1_bf16"][expert_start:expert_end],
            inputs["w2_bf16"][expert_start:expert_end],
            num_local_experts=num_local_experts,
            hidden_size=CFG.hidden_size,
            intermediate_size=CFG.intermediate_size,
            device=dev,
        )
        moe_kwargs.update(
            gemm1_weights=weights["gemm1_weights"],
            gemm2_weights=weights["gemm2_weights"],
        )
        logits_moe, routed_moe = trtllm_bf16_moe, trtllm_bf16_routed_moe
    elif precision in ("mxfp8", "mxfp4"):
        from flashinfer import SfLayout
        from flashinfer.fused_moe import (
            QuantConfig,
            QuantFormat,
            TrtllmFp4Config,
            TrtllmFp8BlockConfig,
            trtllm_fp4_block_scale_moe,
            trtllm_fp4_block_scale_routed_moe,
            trtllm_fp8_block_scale_moe,
            trtllm_fp8_block_scale_routed_moe,
        )
        from flashinfer.tllm_enums import Fp8QuantizationType, WeightLayout

        if precision == "mxfp8":
            config = TrtllmFp8BlockConfig
            weight_format = QuantFormat.MXFP8
            logits_moe = trtllm_fp8_block_scale_moe
            routed_moe = trtllm_fp8_block_scale_routed_moe
        elif precision == "mxfp4":
            config = TrtllmFp4Config
            weight_format = QuantFormat.MXFP4
            logits_moe = trtllm_fp4_block_scale_moe
            routed_moe = trtllm_fp4_block_scale_routed_moe
        else:
            raise ValueError(f"Unsupported MX precision: {precision}")
        quant = QuantConfig(weight=weight_format, activation=QuantFormat.MXFP8)
        # Public helpers handle gated row order and each native scale layout.
        weights = config.prepare_weights(
            inputs["w1_bf16"][expert_start:expert_end],
            inputs["w2_bf16"][expert_start:expert_end],
            quant=quant,
            num_local_experts=num_local_experts,
            hidden_size=CFG.hidden_size,
            intermediate_size=CFG.intermediate_size,
            device=dev,
        )
        moe_kwargs.update(
            gemm1_weights=weights["gemm1_weights"],
            gemm1_weights_scale=weights["gemm1_weights_scale"],
            gemm2_weights=weights["gemm2_weights"],
            gemm2_weights_scale=weights["gemm2_weights_scale"],
            tune_max_num_tokens=max(n, 8192),
        )
        if precision == "mxfp8":
            moe_kwargs.update(
                fp8_quantization_type=Fp8QuantizationType.MxFp8,
                use_shuffled_weight=True,
                weight_layout=WeightLayout.MajorK,
            )
        elif precision == "mxfp4":
            moe_kwargs.update(
                gemm1_bias=None,
                gemm1_alpha=None,
                gemm1_beta=None,
                gemm1_clamp_limit=None,
                gemm2_bias=None,
                output1_scale_scalar=weights["output1_scale_scalar"],
                output1_scale_gate_scalar=weights["output1_scale_gate_scalar"],
                output2_scale_scalar=weights["output2_scale_scalar"],
                hidden_states_scale_layout=SfLayout.layout_linear,
            )
        else:
            raise ValueError(f"Unsupported MX precision: {precision}")

        def quantize_hidden(hidden_states):
            return config.prepare_activations(hidden_states, quant=quant)

        if not include_activation_quant:
            hidden_states, hidden_states_scale = quantize_hidden(inputs["hidden_bf16"])
            input_kwargs.update(
                hidden_states=hidden_states,
                hidden_states_scale=hidden_states_scale,
            )
    elif precision == "nvfp4":
        from flashinfer import SfLayout, nvfp4_quantize
        from flashinfer.fused_moe import (
            trtllm_fp4_block_scale_moe,
            trtllm_fp4_block_scale_routed_moe,
        )
        from flashinfer.fused_moe.core import (
            _maybe_get_cached_w3_w1_permute_indices,
            get_w2_permute_indices_with_cache,
        )
        from flashinfer.fp4_quantization import fp4_quantize, block_scale_interleave
        from flashinfer.quantization.nvfp4_quantization_utils import (
            current_nvfp4_4over6_config,
            make_nvfp4_global_scale,
        )

        sv, etm, cache = 16, 128, {}
        hidden_global_scale = inputs["hidden_gs"]
        if use_per_token_activation:
            hidden_global_scale = make_nvfp4_global_scale(
                inputs["hidden_bf16"],
                per_token_activation=True,
                nvfp4_4over6_config=current_nvfp4_4over6_config(),
            )

        def quantize_hidden(hidden_states):
            if use_per_token_activation:
                hidden_states, hidden_states_scale, per_token_scale = nvfp4_quantize(
                    hidden_states,
                    hidden_global_scale,
                    sfLayout=SfLayout.layout_linear,
                    per_token_activation=True,
                    backend="cute-dsl",
                )
            else:
                hidden_states, hidden_states_scale = fp4_quantize(
                    hidden_states, hidden_global_scale, sv, False, True
                )
                per_token_scale = None
            hidden_states = hidden_states.view(torch.uint8).reshape(
                n, CFG.hidden_size // 2
            )
            hidden_states_scale = (
                hidden_states_scale.view(torch.float8_e4m3fn)
                .flatten()[: n * CFG.hidden_size // sv]
                .reshape(n, CFG.hidden_size // sv)
            )
            return hidden_states, hidden_states_scale, per_token_scale

        hfp, hsc, hidden_per_token_scale = quantize_hidden(inputs["hidden_bf16"])

        def prep(bf16, gs, M, K):
            """Prepare weights for LOCAL experts only."""
            fl, sl = [], []
            for e in range(expert_start, expert_end):
                q, s = fp4_quantize(bf16[e], gs[e], sv, False, False)
                fl.append(q.view(torch.uint8).reshape(M, K // 2))
                sl.append(s.view(torch.float8_e4m3fn).reshape(M, K // sv))
            return torch.stack(fl), torch.stack(sl)

        w1f, w1s = prep(
            inputs["w1_bf16"],
            inputs["w1_gs"],
            2 * CFG.intermediate_size,
            CFG.hidden_size,
        )
        w2f, w2s = prep(
            inputs["w2_bf16"], inputs["w2_gs"], CFG.hidden_size, CFG.intermediate_size
        )

        def shuf(fp4, sf, perm_fn):
            """Shuffle weights for LOCAL experts only."""
            fsh, ssh = [], []
            for i in range(num_local_experts):
                p = perm_fn(cache, fp4[i], etm)
                fsh.append(fp4[i][p.to(dev)].contiguous())
                ps = perm_fn(cache, sf[i].view(torch.uint8), etm, sv)
                ssh.append(
                    block_scale_interleave(
                        sf[i].view(torch.uint8)[ps.to(dev)].contiguous()
                    )
                )
            return torch.stack(fsh), torch.stack(ssh)

        w1f, w1s = shuf(w1f, w1s, _maybe_get_cached_w3_w1_permute_indices)
        w2f, w2s = shuf(w2f, w2s, get_w2_permute_indices_with_cache)
        w1s = w1s.view(torch.float8_e4m3fn).reshape(
            num_local_experts, 2 * CFG.intermediate_size, CFG.hidden_size // sv
        )
        w2s = w2s.view(torch.float8_e4m3fn).reshape(
            num_local_experts, CFG.hidden_size, CFG.intermediate_size // sv
        )

        # Scale tensors sized for LOCAL experts only
        sc = torch.ones(num_local_experts, device=dev, dtype=torch.float32)
        moe_kwargs.update(
            gemm1_weights=w1f,
            gemm1_weights_scale=w1s,
            gemm1_bias=None,
            gemm1_alpha=None,
            gemm1_beta=None,
            gemm1_clamp_limit=None,
            gemm2_weights=w2f,
            gemm2_weights_scale=w2s,
            gemm2_bias=None,
            output1_scale_scalar=sc,
            output1_scale_gate_scalar=sc,
            output2_scale_scalar=sc,
        )
        input_kwargs.update(
            hidden_states=inputs["hidden_bf16"] if include_activation_quant else hfp,
            hidden_states_scale=None if include_activation_quant else hsc,
        )
        logits_moe = trtllm_fp4_block_scale_moe
        routed_moe = trtllm_fp4_block_scale_routed_moe
    else:
        raise ValueError(f"Unsupported TRTLLM precision: {precision}")

    routing_ids = None
    routing_weights = None
    is_routed = routing_input_mode == "routed"
    if is_routed:
        if precision == "mxfp8":
            # The FP8 Renormalize path consumes precomputed, ungrouped routes.
            moe_kwargs.update(n_group=None, topk_group=None)
        # Share this row's cached routes across precisions, including after
        # autotuning advances the RNG. Release the cache with the input row.
        factory = inputs.get("_trtllm_routing_factory")
        if factory is None:
            factory = RoutingRealizationFactory()
            inputs["_trtllm_routing_factory"] = factory
        realized = factory.get_or_create(
            RoutingRealizationKey(
                device=torch.device(dev),
                num_tokens=n,
                distribution=distributions[0],
                sample_index=0,
                local_expert_offset=0,
                num_local_experts=CFG.num_experts,
                top_k=CFG.top_k,
                routing_rule_fingerprint="bench_moe_deepseek:renormalize",
                routed_scaling_factor=1.0,
            )
        )
        routing_ids = realized.expert_ids
        routing_weights = realized.routing_weights

    moe = routed_moe if is_routed else logits_moe
    moe_kwargs.update(
        routed_scaling_factor=1.0 if is_routed else CFG.routed_scaling_factor,
        routing_method_type=(
            RoutingMethodType.Renormalize.value
            if is_routed
            else RoutingMethodType.DeepSeekV3
        ),
    )

    def run(routing_logits, routing_bias, hidden_states, hidden_states_scale=None):
        activation_kwargs = {}
        if precision == "nvfp4":
            per_token_scale = hidden_per_token_scale
            if include_activation_quant:
                hidden_states, hidden_states_scale, per_token_scale = quantize_hidden(
                    hidden_states
                )
            activation_kwargs.update(
                hidden_states_scale=hidden_states_scale,
                per_token_scale=per_token_scale,
            )
        elif precision in ("mxfp8", "mxfp4"):
            if include_activation_quant:
                hidden_states, hidden_states_scale = quantize_hidden(hidden_states)
            activation_kwargs["hidden_states_scale"] = hidden_states_scale
        if is_routed:
            routing_kwargs = {"topk_ids": (routing_ids, routing_weights)}
            if precision in ("nvfp4", "mxfp8", "mxfp4"):
                routing_kwargs["routing_bias"] = None
        else:
            routing_kwargs = dict(
                routing_logits=routing_logits, routing_bias=routing_bias
            )
        return moe(
            hidden_states=hidden_states,
            **routing_kwargs,
            **activation_kwargs,
            **moe_kwargs,
        )

    # Pre-warm under autotune; measurement runs outside (see bench_cute_dsl).
    with _autotune_context(do_autotune, autotune_cache):
        run(**input_kwargs)
        torch.cuda.synchronize()

    return _measure_or_profile(
        run,
        input_kwargs,
        warmup,
        iters,
        use_cuda_graph,
        use_cupti,
        profile_cuda,
        profile_iters,
    )


# =============================================================================
# Autotune
# =============================================================================


# =============================================================================
# Main Benchmark
# =============================================================================


@dataclass
class BenchResult:
    """Single benchmark result for one backend at one token count."""

    backend: str
    tokens: int
    latency_ms: float
    tflops: float


def _family_backends(quant_family):
    if quant_family == "nvfp4":
        return ("cutedsl", "cutlass", "trtllm-nvfp4", "trtllm-bf16")
    elif quant_family == "mxfp":
        return (
            "cute-dsl-w4a8",
            "cute-dsl-mxfp8",
            "trtllm-mxfp4",
            "trtllm-mxfp8",
            "trtllm-bf16",
        )
    else:
        raise ValueError(f"Unsupported quantization family: {quant_family}")


def run_benchmark(
    token_counts,
    warmup=10,
    iters=100,
    ep_config=1,
    tp_config=1,
    do_autotune=True,
    verbose=True,
    use_cuda_graph=True,
    use_cupti=True,
    use_wrapper=True,
    routing_bias_scale=0.01,
    use_per_token_activation=False,
    include_activation_quant=False,
    use_fused_finalize=True,
    profile_cuda=False,
    profile_iters=10,
    profile_backend=None,
    backends=None,
    routing_input_mode="logits",
    distributions=("uniform",),
    autotune_cache=None,
    quant_family="nvfp4",
):
    """
    Unified benchmark for DeepSeek-V3 MoE backends.

    Autotuning runs in each backend's pre-warm step (under ``autotune(True)``)
    so the autotuner profiles all tactics on the default stream before
    ``bench_gpu_time`` switches to a side stream / captures into a CUDA graph.
    This guarantees the autotuner sees the same API (wrapper vs functional),
    EP config, and weight shapes as the timed runs, avoiding cache-key
    mismatches; the measurement loop itself runs outside ``autotune(True)``
    so ``choose_one`` takes the non-tuning fast path and host-side cache
    walks don't appear inside the CUDA-event interval.

    All output is buffered and printed after the benchmark (and autotuning)
    completes, so autotuner log messages do not interleave with the results
    table.

    Args:
        token_counts: List of token counts to benchmark
        warmup: Warmup iterations
        iters: Benchmark iterations
        ep_config: Expert Parallelism config (1, 8, or 16)
        tp_config: Tensor Parallelism degree used to reduce expert intermediate size
        do_autotune: Whether to autotune during benchmarking
        verbose: Print results to stdout
        use_cuda_graph: Whether to use CUDA graph for benchmarking
        use_cupti: Whether to use CUPTI for accurate GPU timing
        use_wrapper: Whether to use CuteDslMoEWrapper API (recommended)
        routing_bias_scale: Scale for random routing bias generation
        use_per_token_activation: Whether supported FP4 MoE backends should use
            per-token NVFP4 activation scaling.
        include_activation_quant: Include the initial activation FP4
            quantization in each backend's timing.
        use_fused_finalize: Use atomic fused CuTe DSL finalize and allow
            CUTLASS fused-finalize tactics; otherwise use non-fused finalize.
        profile_cuda: Capture one backend for an external CUDA profiler.
        profile_iters: Number of cold-L2 graph replays to capture.
        profile_backend: Backend to run when profile_cuda is enabled.
        quant_family: Default backend set and table, ``nvfp4`` or ``mxfp``.
            Explicit ``backends`` overrides the set and retains CSV output.

    Returns:
        List of BenchResult objects
    """
    if tp_config < 1 or BASE_INTERMEDIATE_SIZE % tp_config != 0:
        raise ValueError(
            f"tp_config must be a positive divisor of {BASE_INTERMEDIATE_SIZE}"
        )

    if CFG.num_experts % ep_config != 0:
        raise ValueError("ep_config must divide num_experts")
    num_local = CFG.num_experts // ep_config
    local_offset = 0
    CFG.intermediate_size = BASE_INTERMEDIATE_SIZE // tp_config

    results = []
    rows_and_histograms = []

    # Note: autotune(True) is now scoped to each bench_*'s pre-warm rather than
    # wrapping the entire measurement loop.  See bench_cute_dsl for rationale.
    for n in token_counts:
        row, histogram_record = _benchmark_single(
            n,
            warmup,
            iters,
            num_local,
            local_offset,
            use_cuda_graph,
            use_cupti,
            use_wrapper=use_wrapper,
            routing_bias_scale=routing_bias_scale,
            do_autotune=do_autotune,
            use_per_token_activation=use_per_token_activation,
            include_activation_quant=include_activation_quant,
            use_fused_finalize=use_fused_finalize,
            profile_cuda=profile_cuda,
            profile_iters=profile_iters,
            profile_backend=profile_backend,
            backends=backends,
            routing_input_mode=routing_input_mode,
            distributions=distributions,
            autotune_cache=autotune_cache,
            quant_family=quant_family,
        )
        results.extend(row)
        rows_and_histograms.append((row, histogram_record))
        # Each row rebuilds full-model weights; release cached allocations so
        # measurements do not depend on the token-count scan order.
        gc.collect()
        torch.cuda.empty_cache()

    if verbose and backends is not None:
        print("backend,tokens,latency_ms,tflops")
        for row, _ in rows_and_histograms:
            for result in row:
                print(
                    f"{result.backend},{result.tokens},{result.latency_ms:.6f},"
                    f"{result.tflops:.6f}"
                )
    elif verbose:
        _print_header(
            ep_config,
            tp_config,
            num_local,
            use_cuda_graph,
            use_cupti,
            routing_bias_scale,
            use_per_token_activation=use_per_token_activation,
            include_activation_quant=include_activation_quant,
            use_fused_finalize=use_fused_finalize,
            quant_family=quant_family,
        )
        for row, histogram_record in rows_and_histograms:
            _print_row(row, histogram_record, quant_family=quant_family)
        _print_footer(use_per_token_activation, quant_family=quant_family)

    return results


def _benchmark_single(
    n,
    warmup,
    iters,
    num_local,
    local_offset,
    use_cuda_graph,
    use_cupti,
    use_wrapper=True,
    routing_bias_scale=0.01,
    do_autotune=True,
    use_per_token_activation=False,
    include_activation_quant=False,
    use_fused_finalize=True,
    profile_cuda=False,
    profile_iters=10,
    profile_backend=None,
    backends=None,
    routing_input_mode="logits",
    distributions=("uniform",),
    autotune_cache=None,
    quant_family="nvfp4",
):
    """Benchmark all backends for a single token count.

    Args:
        use_wrapper: If True, use CuteDslMoEWrapper API for CuteDSL.
        do_autotune: Forwarded to each bench_* function — wraps pre-warm only.
    """
    inputs = create_inputs(n, routing_bias_scale=routing_bias_scale)
    histogram_record = _collect_expert_histogram(inputs, num_local, local_offset)

    selected = set(backends or _family_backends(quant_family))
    if backends is None and profile_backend in (
        "cute-dsl-mxfp8",
        "cute-dsl-w4a8",
        "trtllm-mxfp8",
        "trtllm-mxfp4",
    ):
        selected = {profile_backend}
    run_cutlass = "cutlass" in selected and profile_backend in (None, "cutlass")
    run_trtllm_nvfp4 = "trtllm-nvfp4" in selected and profile_backend in (
        None,
        "trtllm-nvfp4",
    )

    run_trtllm_bf16 = "trtllm-bf16" in selected and profile_backend in (
        None,
        "trtllm-bf16",
    )

    lat = {}
    for selector, profile_selector, quant_mode, label in (
        ("cutedsl", "cute-dsl", "w4a4", "CuteDSL W4A4"),
        ("cutedsl", "cute-dsl-w4a16", "w4a16", "CuteDSL W4A16"),
        ("cute-dsl-mxfp8", "cute-dsl-mxfp8", "mxfp8", "CuteDSL MXFP8"),
        ("cute-dsl-w4a8", "cute-dsl-w4a8", "w4a8", "CuteDSL W4A8"),
    ):
        if selector in selected and profile_backend in (None, profile_selector):
            if quant_mode in ("mxfp8", "w4a8") and routing_input_mode != "logits":
                raise ValueError(f"{selector} requires logits routing")
            lat[label] = bench_cute_dsl(
                inputs,
                warmup,
                iters,
                num_local,
                local_offset,
                use_cuda_graph,
                use_cupti,
                use_wrapper=use_wrapper,
                do_autotune=do_autotune,
                quant_mode=quant_mode,
                use_per_token_activation=use_per_token_activation,
                include_activation_quant=include_activation_quant,
                use_fused_finalize=use_fused_finalize,
                profile_cuda=profile_cuda,
                profile_iters=profile_iters,
                autotune_cache=autotune_cache,
            )
    if run_cutlass and not use_per_token_activation:
        lat["CUTLASS"] = bench_cutlass(
            inputs,
            warmup,
            iters,
            num_local,
            local_offset,
            use_cuda_graph,
            use_cupti,
            do_autotune=do_autotune,
            include_activation_quant=include_activation_quant,
            use_fused_finalize=use_fused_finalize,
            profile_cuda=profile_cuda,
            profile_iters=profile_iters,
            autotune_cache=autotune_cache,
        )
    for precision, enabled in (
        ("nvfp4", run_trtllm_nvfp4),
        ("bf16", run_trtllm_bf16),
        (
            "mxfp4",
            "trtllm-mxfp4" in selected and profile_backend in (None, "trtllm-mxfp4"),
        ),
        (
            "mxfp8",
            "trtllm-mxfp8" in selected and profile_backend in (None, "trtllm-mxfp8"),
        ),
    ):
        if enabled:
            label = (
                "TRTLLM MXFP4xMXFP8"
                if precision == "mxfp4"
                else f"TRTLLM {precision.upper()}"
            )
            lat[label] = bench_trtllm(
                inputs,
                warmup,
                iters,
                num_local,
                local_offset,
                use_cuda_graph,
                use_cupti,
                do_autotune=do_autotune,
                use_per_token_activation=use_per_token_activation,
                include_activation_quant=include_activation_quant,
                profile_cuda=profile_cuda,
                profile_iters=profile_iters,
                autotune_cache=autotune_cache,
                routing_input_mode=routing_input_mode,
                distributions=distributions,
                precision=precision,
            )

    # Build results
    results = []
    for backend, latency in lat.items():
        results.append(
            BenchResult(
                backend=backend,
                tokens=n,
                latency_ms=latency,
                tflops=calc_tflops(n, latency, num_local),
            )
        )
    return results, histogram_record


def _table_layout(quant_family, use_per_token_activation):
    if quant_family == "nvfp4":
        modes = ("W4A4", "W4A16")
        backends = [
            ("CuteDSL W4A4", "CuteDSL W4A4", 15),
            ("CuteDSL W4A16", "CuteDSL W4A16", 15),
        ]
        baselines = []
        if not use_per_token_activation:
            backends.append(("CUTLASS", "CUTLASS", 15))
            baselines.append(("CUTLASS", 18))
        backends.extend(
            (("TRTLLM NVFP4", "TRTLLM NVFP4", 15), ("TRTLLM BF16", "TRTLLM BF16", 15))
        )
        baselines.extend((("TRTLLM NVFP4", 23), ("TRTLLM BF16", 23)))
        winner_width = 12
    elif quant_family == "mxfp":
        modes = ("MXFP4xMXFP8", "MXFP8")
        backends = [
            ("CuteDSL W4A8", "CuteDSL MXFP4xMXFP8", 23),
            ("CuteDSL MXFP8", "CuteDSL MXFP8", 23),
            ("TRTLLM MXFP4xMXFP8", "TRTLLM MXFP4xMXFP8", 23),
            ("TRTLLM MXFP8", "TRTLLM MXFP8", 23),
            ("TRTLLM BF16", "TRTLLM BF16", 23),
        ]
        baselines = [
            ("TRTLLM MXFP4xMXFP8", 32),
            ("TRTLLM MXFP8", 25),
            ("TRTLLM BF16", 23),
        ]
        winner_width = 23
    else:
        raise ValueError(f"Unsupported quantization family: {quant_family}")
    widths = [
        6,
        *[width for _, _, width in backends],
        *[width for _, width in baselines],
        winner_width,
        7,
        15,
    ]
    table_width = sum(widths) + 3 * (len(widths) - 1)
    return modes, backends, baselines, winner_width, table_width


def _print_header(
    ep_config,
    tp_config,
    num_local,
    use_cuda_graph,
    use_cupti,
    routing_bias_scale,
    use_per_token_activation=False,
    include_activation_quant=False,
    use_fused_finalize=True,
    quant_family="nvfp4",
):
    """Print either precision family's comparison with the same table layout."""
    modes, backends, baselines, winner_width, table_width = _table_layout(
        quant_family, use_per_token_activation
    )
    print("\n" + "=" * table_width)
    if quant_family == "mxfp":
        print(
            "DeepSeek-V3 MoE Benchmark: CuteDSL MXFP4xMXFP8 / MXFP8 vs TRTLLM MXFP4xMXFP8 / MXFP8 / BF16 "
            f"(EP={ep_config}, TP={tp_config})"
        )
    elif use_per_token_activation:
        print(
            "DeepSeek-V3 MoE Benchmark: CuteDSL W4A4/W4A16 vs TRTLLM NVFP4 / TRTLLM BF16 "
            f"(EP={ep_config}, TP={tp_config})"
        )
    else:
        print(
            "DeepSeek-V3 MoE Benchmark: CuteDSL W4A4/W4A16 vs CUTLASS vs TRTLLM NVFP4 / TRTLLM BF16 "
            f"(EP={ep_config}, TP={tp_config})"
        )
    print("=" * table_width)
    print(
        f"Model: hidden={CFG.hidden_size}, intermediate={CFG.intermediate_size}, "
        f"experts={CFG.num_experts}, top_k={CFG.top_k}"
    )
    print(
        f"EP Config: {num_local} local experts (simulating {CFG.num_experts // num_local}-way parallelism)"
    )
    print(
        f"TP Config: intermediate size {CFG.intermediate_size} "
        f"(simulating {tp_config}-way parallelism)"
    )
    print(
        f"CUDA Graph: {'enabled' if use_cuda_graph else 'disabled'}, CUPTI: {'enabled' if use_cupti else 'disabled'}"
    )
    print(
        f"Routing bias scale: {routing_bias_scale} "
        f"(larger values tend to create expert imbalance)"
    )
    if quant_family == "nvfp4":
        print(
            "Timed initial activation quantization for FP4-activation backends: "
            f"{'included' if include_activation_quant else 'excluded'}; "
            "W4A16 and TRTLLM BF16 consume BF16 directly"
        )
    elif quant_family == "mxfp":
        print("MXFP8 activations: native UE8M0 scale per 32 elements along K.")
        print(
            "Timed initial activation quantization: "
            f"{'included' if include_activation_quant else 'excluded'}; "
            "weight preparation and tuning excluded. TRTLLM BF16 consumes BF16 directly."
        )
    print(
        "CuteDSL finalize: "
        f"{'atomic fused' if use_fused_finalize else 'deterministic two-stage'}"
    )
    if quant_family == "nvfp4":
        print(
            "CUTLASS fused-finalize tactics: "
            f"{'allowed' if use_fused_finalize else 'disabled'}"
        )
        print(
            "TRTLLM NVFP4 / TRTLLM BF16 finalize: native (unaffected by --no-fused-finalize)."
        )
        if use_per_token_activation:
            print(
                "CUTLASS omitted: it does not consume the per-token activation scale."
            )
    elif quant_family == "mxfp":
        print(
            "TRTLLM MXFP4xMXFP8 / MXFP8 / BF16 finalize: native (unaffected by --no-fused-finalize)."
        )
    print("-" * table_width)
    headers = [f"{'Tokens':>6}"]
    headers.extend(f"{label:^{width}}" for _, label, width in backends)
    headers.extend(f"{'Speedup vs ' + label:^{width}}" for label, width in baselines)
    headers.extend((f"{'Winner':^{winner_width}}", f"{'Active':^7}", f"{'Stats':^15}"))
    print(" | ".join(headers))
    units = [f"{'':>6}"]
    units.extend(
        f"{('ms'.rjust(7) + ' ' + 'TFLOPS'.rjust(7)):>{width}}"
        for _, _, width in backends
    )
    for _, width in baselines:
        if width == 18:
            units.append(f"{modes[0]:>8}  {modes[1]:>8}")
        else:
            units.append(f"{(modes[0].rjust(11) + ' ' + modes[1].rjust(11)):>{width}}")
    units.extend(
        (f"{'':^{winner_width}}", f"{'experts':^7}", f"{'min/max/median':^15}")
    )
    print(" | ".join(units))
    print("-" * table_width)


def _print_row(results, histogram_record, quant_family="nvfp4"):
    """Print latency, throughput and both CuTe modes' baseline speedups."""
    rows = {result.backend: result for result in results}
    modes, backends, baselines, winner_width, _ = _table_layout(
        quant_family, "CUTLASS" not in rows
    )
    cute = [rows[key] for key, _, _ in backends[:2]]
    fields = [f"{cute[0].tokens:>6}"]
    for key, _, width in backends:
        latency = f"{rows[key].latency_ms:>7.3f} {rows[key].tflops:>7.1f}"
        fields.append(f"{latency:>{width}}")
    for key, width in baselines:
        speedups = " ".join(
            f"{rows[key].latency_ms / mode.latency_ms:>7.2f}x" for mode in cute
        )
        fields.append(f"{speedups:>{width}}")
    winner_key, winner, _ = min(backends, key=lambda entry: rows[entry[0]].latency_ms)
    if quant_family == "nvfp4" and winner_key in (backends[0][0], backends[1][0]):
        winner = modes[0] if winner_key == backends[0][0] else modes[1]
    stats = (
        f"{histogram_record['min_count']:>3}/"
        f"{histogram_record['max_count']:>3}/"
        f"{histogram_record['median_count']:>7.2f}"
    )
    fields.extend(
        (
            f"{winner:^{winner_width}}",
            f"{histogram_record['active_local_experts']:>7}",
            f"{stats:>15}",
        )
    )
    print(" | ".join(fields))


def _print_footer(use_per_token_activation, quant_family="nvfp4"):
    """Print benchmark footer."""
    table_width = _table_layout(quant_family, use_per_token_activation)[-1]
    print("-" * table_width)
    print(
        "Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend"
    )


def _collect_expert_histogram(inputs, num_local, local_offset):
    from flashinfer.fused_moe import fused_topk_deepseek

    num_tokens = inputs["router_logits"].shape[0]
    dev = inputs["router_logits"].device
    topk_values = torch.empty(num_tokens, CFG.top_k, dtype=torch.float32, device=dev)
    topk_indices = torch.empty(num_tokens, CFG.top_k, dtype=torch.int32, device=dev)

    fused_topk_deepseek(
        scores=inputs["router_logits"],
        bias=inputs["routing_bias"].float(),
        n_group=CFG.n_group,
        topk_group=CFG.topk_group,
        topk=CFG.top_k,
        routed_scaling_factor=CFG.routed_scaling_factor,
        topk_values=topk_values,
        topk_indices=topk_indices,
    )

    expert_hist = torch.bincount(
        topk_indices.reshape(-1).to(torch.int64), minlength=CFG.num_experts
    )
    local_hist = expert_hist[local_offset : local_offset + num_local]
    local_hist_f32 = local_hist.to(torch.float32)
    active_local_experts = int((local_hist > 0).sum().item())
    if local_hist.numel() > 0:
        min_count = int(local_hist.min().item())
        max_count = int(local_hist.max().item())
        median_count = float(torch.quantile(local_hist_f32, 0.5).item())
    else:
        min_count = 0
        max_count = 0
        median_count = 0.0

    return {
        "active_local_experts": active_local_experts,
        "min_count": min_count,
        "max_count": max_count,
        "median_count": median_count,
    }


def main():
    parser = argparse.ArgumentParser(
        description="DeepSeek-V3 MoE Performance Benchmark"
    )
    parser.add_argument(
        "--num-tokens",
        type=str,
        default=None,
        help="Comma-separated token counts (default: 128-4096 for throughput, 1-128 for gen-phase)",
    )
    parser.add_argument("--warmup", type=int, default=10, help="Warmup iterations")
    parser.add_argument("--iters", type=int, default=100, help="Benchmark iterations")
    parser.add_argument(
        "--no-autotune",
        "--skip-autotune",
        dest="no_autotune",
        action="store_true",
        help="Disable profiling; a supplied cache is still loaded",
    )
    parser.add_argument(
        "--cache",
        "--tuning-cache",
        "--bundle-output",
        dest="cache",
        help="Shared AutoTuner JSON cache path",
    )
    parser.add_argument(
        "--num-experts",
        type=int,
        default=CFG.num_experts,
        help="Number of global routing experts",
    )
    parser.add_argument(
        "--quant-family",
        choices=("nvfp4", "mxfp"),
        default="nvfp4",
        help="Default comparison table: NVFP4 W4A4/W4A16 or MXFP4xMXFP8/MXFP8; both include TRTLLM BF16. MX requires --no-fused-finalize.",
    )
    parser.add_argument(
        "--backends",
        type=str,
        help="Override the family with a comma-separated subset of cutedsl,cutlass,trtllm-nvfp4,trtllm-bf16,cute-dsl-mxfp8,cute-dsl-w4a8,trtllm-mxfp8,trtllm-mxfp4; prints CSV. CuTe DSL MX modes require --no-fused-finalize.",
    )
    parser.add_argument(
        "--distributions",
        type=str,
        help="Comma-separated DA tuner distributions",
    )
    parser.add_argument(
        "--routing-input-mode",
        choices=("logits", "routed"),
        default="logits",
        help="TRTLLM routing input representation",
    )
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    parser.add_argument(
        "--gen-phase",
        action="store_true",
        help="Use generation phase token counts (1-128 instead of 128-4096)",
    )
    parser.add_argument(
        "--ep",
        type=int,
        default=1,
        choices=[1, 2, 4, 8, 16],
        help="Expert parallelism simulation.",
    )
    parser.add_argument(
        "--tp",
        type=int,
        default=1,
        help="Tensor Parallelism simulation: divide the expert intermediate size by TP.",
    )
    parser.add_argument(
        "--no-cuda-graph",
        action="store_true",
        help="Disable CUDA graph for benchmarking (enabled by default)",
    )
    parser.add_argument(
        "--no-cupti",
        action="store_true",
        help="Disable CUPTI for GPU timing (enabled by default)",
    )
    parser.add_argument(
        "--functional-api",
        action="store_true",
        help="Use functional API instead of CuteDslMoEWrapper for CuteDSL benchmark",
    )
    parser.add_argument(
        "--use-per-token-activation",
        action="store_true",
        help="Use per-token NVFP4 activation scaling for supported FP4 MoE backends.",
    )
    parser.add_argument(
        "--include-activation-quant",
        action="store_true",
        help="Include initial activation quantization for NVFP4 and TRTLLM MX modes; CuTe DSL MX modes require it excluded. BF16 is unaffected.",
    )
    parser.add_argument(
        "--no-fused-finalize",
        action="store_false",
        dest="use_fused_finalize",
        help="Use deterministic two-stage CuTe DSL finalize and disable CUTLASS fused-finalize tactics.",
    )
    parser.add_argument(
        "--profile-cuda",
        action="store_true",
        help="Capture steady-state iterations between cudaProfilerStart/Stop.",
    )
    parser.add_argument(
        "--profile-iters",
        type=int,
        default=10,
        help="Number of CUDA graph replays captured by --profile-cuda.",
    )
    parser.add_argument(
        "--profile-backend",
        choices=[
            "cute-dsl",
            "cute-dsl-w4a16",
            "cute-dsl-mxfp8",
            "cute-dsl-w4a8",
            "cutlass",
            "trtllm-nvfp4",
            "trtllm-bf16",
            "trtllm-mxfp8",
            "trtllm-mxfp4",
        ],
        help="Backend captured by --profile-cuda.",
    )
    parser.add_argument(
        "--routing-bias-scale",
        type=float,
        default=0.01,
        help="Scale for random routing bias. Larger values tend to create expert imbalance.",
    )
    args = parser.parse_args()

    if args.tp < 1:
        parser.error("--tp must be positive")
    if args.num_experts < 1:
        parser.error("--num-experts must be positive")
    if args.num_experts % args.ep != 0:
        parser.error("--ep must divide --num-experts")
    backends = None
    if args.backends:
        backends = tuple(
            item.strip() for item in args.backends.split(",") if item.strip()
        )
        unknown = sorted(
            set(backends)
            - {
                "cutedsl",
                "cutlass",
                "trtllm-nvfp4",
                "trtllm-bf16",
                "cute-dsl-mxfp8",
                "cute-dsl-w4a8",
                "trtllm-mxfp8",
                "trtllm-mxfp4",
            }
        )
        if unknown:
            parser.error(f"unknown --backends value(s): {', '.join(unknown)}")
    distributions = tuple(
        item.strip()
        for item in (args.distributions or "uniform").split(",")
        if item.strip()
    )
    if not distributions:
        parser.error("--distributions must not be empty")
    if BASE_INTERMEDIATE_SIZE % args.tp != 0:
        parser.error(
            f"--tp must divide the expert intermediate size ({BASE_INTERMEDIATE_SIZE})"
        )
    if args.profile_iters < 1:
        parser.error("--profile-iters must be positive")
    if args.profile_cuda != (args.profile_backend is not None):
        parser.error("--profile-cuda and --profile-backend must be specified together")
    if backends and args.profile_backend is not None:
        profile_backend = (
            "cutedsl"
            if args.profile_backend in ("cute-dsl", "cute-dsl-w4a16")
            else args.profile_backend
        )
        if profile_backend not in backends:
            parser.error(
                f"--profile-backend {args.profile_backend} is excluded by --backends"
            )
    if args.profile_backend == "cutlass" and args.use_per_token_activation:
        parser.error("CUTLASS does not consume the per-token activation scale")
    selected = set(backends or _family_backends(args.quant_family))
    if args.profile_backend is not None:
        selected = {args.profile_backend}
    if selected & {"cute-dsl-mxfp8", "cute-dsl-w4a8"}:
        if args.use_fused_finalize:
            parser.error("CuTe DSL MX modes require --no-fused-finalize")
        if args.use_per_token_activation or args.include_activation_quant:
            parser.error(
                "CuTe DSL MX modes do not support --use-per-token-activation "
                "or --include-activation-quant"
            )
        if args.routing_input_mode != "logits":
            parser.error("CuTe DSL MX modes require --routing-input-mode logits")
    if not is_sm100_family():
        print("ERROR: Requires SM100 family GPU (Blackwell: SM100, SM103)")
        return 1

    CFG.num_experts = args.num_experts
    if args.routing_input_mode == "routed" and not args.no_cuda_graph:
        os.environ["FLASHINFER_DIST_AWARE_AUTOTUNE"] = "1"
        os.environ["FLASHINFER_DA_DISTRIBUTIONS"] = ",".join(distributions)
    else:
        os.environ["FLASHINFER_DIST_AWARE_AUTOTUNE"] = "0"

    # Determine token counts
    if args.num_tokens:
        tokens = [int(x) for x in args.num_tokens.split(",")]
    elif args.gen_phase:
        tokens = GEN_PHASE_TOKENS  # [1, 2, 4, 8, 16, 32, 64, 128]
    else:
        tokens = TOKEN_COUNTS  # [128, 256, 512, 1024, 2048, 4096]
    if args.profile_cuda and len(tokens) != 1:
        parser.error("--profile-cuda requires exactly one token count")
    print("\nDeepSeek-V3 MoE Performance Benchmark")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CuteDSL API: {'Functional' if args.functional_api else 'Wrapper'}")
    print(f"Per-token activation: {args.use_per_token_activation}")
    print(f"Initial activation quantization: {args.include_activation_quant}")
    if args.quant_family == "nvfp4":
        print("CuteDSL modes: W4A4 and W4A16; baselines: TRTLLM NVFP4 and TRTLLM BF16")
    elif args.quant_family == "mxfp":
        print(
            "CuteDSL modes: MXFP4xMXFP8 and MXFP8; baselines: matching TRTLLM modes and BF16"
        )
    print(f"Tensor parallelism simulation: TP={args.tp}")
    print(f"CUDA profiler capture: {args.profile_cuda}")
    print(
        "CuteDSL finalize: "
        f"{'atomic fused' if args.use_fused_finalize else 'deterministic two-stage'}"
    )
    if args.quant_family == "nvfp4":
        print(
            "CUTLASS fused-finalize tactics: "
            f"{'allowed' if args.use_fused_finalize else 'disabled'}"
        )
        print(
            "TRTLLM NVFP4 / TRTLLM BF16 finalize: native (unaffected by --no-fused-finalize)."
        )
    elif args.quant_family == "mxfp":
        print(
            "TRTLLM MXFP4xMXFP8 / MXFP8 / BF16 finalize: native (unaffected by --no-fused-finalize)."
        )

    run_benchmark(
        token_counts=tokens,
        warmup=args.warmup,
        iters=args.iters,
        ep_config=args.ep,
        tp_config=args.tp,
        do_autotune=not args.no_autotune,
        verbose=not args.quiet and not args.profile_cuda,
        use_cuda_graph=not args.no_cuda_graph,
        use_cupti=not args.no_cupti,
        use_wrapper=not args.functional_api,
        routing_bias_scale=args.routing_bias_scale,
        use_per_token_activation=args.use_per_token_activation,
        include_activation_quant=args.include_activation_quant,
        use_fused_finalize=args.use_fused_finalize,
        profile_cuda=args.profile_cuda,
        profile_iters=args.profile_iters,
        profile_backend=args.profile_backend,
        backends=backends,
        routing_input_mode=args.routing_input_mode,
        distributions=distributions,
        autotune_cache=args.cache,
        quant_family=args.quant_family,
    )

    return 0


if __name__ == "__main__":
    exit(main())
