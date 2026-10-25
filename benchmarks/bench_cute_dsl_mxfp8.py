"""Full split-MoE benchmark assembly for MXFP8 and MXFP4 x MXFP8.

Both modes use the existing generic FC1/FC2 wrappers and deterministic BF16
finalizer. This benchmark helper does not extend the public MoE API. Initial
activation/weight quantization is outside timing; FC1 output quantization is
inside timing. The native MoE dynamic-bucket tuning policy is reused verbatim.
"""


def bench_cute_dsl_mxfp8(
    benchmark,
    inputs,
    warmup,
    iters,
    num_local,
    local_offset,
    use_cuda_graph,
    use_cupti,
    weight_format,
    gated_group_size,
    do_autotune=True,
    profile_cuda=False,
    profile_iters=10,
    autotune_cache=None,
):
    import torch
    import cutlass

    from flashinfer import mxfp8_quantize
    from flashinfer.autotuner import AutoTuner, TunableRunner
    from flashinfer.cute_dsl.utils import convert_sf_to_mma_layout
    from flashinfer.fp4_quantization import fp4_quantize
    from flashinfer.fused_moe import fused_topk_deepseek
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
    if gated_group_size not in (16, 64):
        raise ValueError(f"unsupported gated weight group: {gated_group_size}")
    cfg = benchmark.CFG
    device = inputs["hidden_bf16"].device
    architecture = torch.cuda.get_device_capability(device)
    n = inputs["hidden_bf16"].shape[0]
    x, x_sf = mxfp8_quantize(
        inputs["hidden_bf16"],
        is_sf_swizzled_layout=False,
        alignment=128,
        backend="cuda",
    )
    x_sf = x_sf.view(torch.uint8).reshape(n, cfg.hidden_size // 32)
    alpha = torch.ones(num_local, dtype=torch.float32, device=device)
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

    expert_end = local_offset + num_local
    w1, w1_sf = quantize_weight(
        _interleave_linear_and_gate(
            inputs["w1_bf16"][local_offset:expert_end],
            group_size=gated_group_size,
            dim=1,
        )
    )
    w2, w2_sf = quantize_weight(inputs["w2_bf16"][local_offset:expert_end])
    output = torch.empty((n, cfg.hidden_size), dtype=torch.bfloat16, device=device)
    topk_values = torch.empty((n, cfg.top_k), dtype=torch.float32, device=device)
    topk_indices = torch.empty((n, cfg.top_k), dtype=torch.int32, device=device)

    # Only borrow the native policy/seeded routing helper. The native runner's
    # forward and tactic filtering assume packed FP4 weights, so neither is used.
    policy = CuteDslFusedMoERunner(
        forward_impl=None,
        num_experts=cfg.num_experts,
        top_k=cfg.top_k,
        num_local_experts=num_local,
        local_expert_offset=local_offset,
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
                cfg.num_experts,
                num_local,
                local_offset,
                cfg.top_k,
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
                    tokens, cfg.top_k, num_local, route_tile
                )
                common = dict(
                    a_dtype=cutlass.Float8E4M3FN,
                    b_dtype=weight_cutlass_dtype,
                    sf_dtype=cutlass.Float8E8M0FNU,
                    sf_vec_size=32,
                    m=capacity,
                    l=num_local,
                    a_major="k",
                    b_major="k",
                )
                gemm1_ok = Fc1Kernel.can_implement(
                    **common,
                    c_dtype=cutlass.Float8E4M3FN,
                    c_major="n",
                    n=2 * cfg.intermediate_size,
                    k=cfg.hidden_size,
                    mma_tiler_mn=gemm1[0],
                    cluster_shape_mn=gemm1[1],
                )
                gemm2_ok = Fc2Kernel.can_implement(
                    **common,
                    out_dtype=cutlass.BFloat16,
                    out_major="n",
                    final_scale_dtype=cutlass.Float32,
                    n=cfg.hidden_size,
                    k=cfg.intermediate_size,
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
                    tokens, cfg.num_experts, cfg.top_k, num_local, route_tile, device
                )
                capacity = sort["out_permuted_idx_to_expanded_idx"].numel()
                intermediate = torch.empty(
                    (capacity, cfg.intermediate_size),
                    dtype=torch.float8_e4m3fn,
                    device=device,
                )
                intermediate_sf = torch.empty(
                    (
                        32,
                        4,
                        (capacity + 127) // 128,
                        4,
                        (cfg.intermediate_size + 127) // 128,
                        1,
                    ),
                    dtype=torch.uint8,
                    device=device,
                )
                expanded = torch.empty(
                    (tokens * cfg.top_k, cfg.hidden_size),
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
                    raise RuntimeError(f"no supported unfused {weight_format} tactics")
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
                num_experts=cfg.num_experts,
                top_k=cfg.top_k,
                local_expert_offset=local_offset,
                num_local_experts=num_local,
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
                topk=cfg.top_k,
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
                top_k=cfg.top_k,
                input_is_expanded=True,
                enable_pdl=True,
            )
            return tensors[11]

    runner = SplitMxfp8Runner()

    def run(x, x_sf, router_logits, routing_bias, topk_values, topk_indices):
        fused_topk_deepseek(
            scores=router_logits,
            bias=routing_bias,
            n_group=cfg.n_group,
            topk_group=cfg.topk_group,
            topk=cfg.top_k,
            routed_scaling_factor=cfg.routed_scaling_factor,
            topk_values=topk_values,
            topk_indices=topk_indices,
        )
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

    input_kwargs = dict(
        x=x,
        x_sf=x_sf,
        router_logits=inputs["router_logits"],
        routing_bias=inputs["routing_bias"].float(),
        topk_values=topk_values,
        topk_indices=topk_indices,
    )
    with benchmark._autotune_context(do_autotune, autotune_cache):
        run(**input_kwargs)
        torch.cuda.synchronize()
    return benchmark._measure_or_profile(
        run,
        input_kwargs,
        warmup,
        iters,
        use_cuda_graph=use_cuda_graph,
        use_cupti=use_cupti,
        profile_cuda=profile_cuda,
        profile_iters=profile_iters,
    )
