# TRTLLM BF16 NCU control audit

Audited 2026-10-11 against local FlashInfer `fresh-profiles-20261011/flashinfer`, commit `7cd20a82caeceb1e4b4a925ac13ddc3458474e94`. Read-only source and methodology review; no GPU runs or performance conclusions in this audit.

## Recommended control

Use a small project-local adapter around the pinned distributed benchmark's input helpers and the public `trtllm_bf16_routed_moe` API. PR [#4985](https://github.com/flashinfer-ai/flashinfer/pull/4985) establishes the pure BF16 API/preparation pattern; its `bench_moe_deepseek.py` CLI is not an exact replacement for this capture because its source realization and default tuning/graph protocol differ.

- Same hardware/runtime/capture protocol: retained B300, same CUDA 13.2 rootfs and exact FlashInfer pin; one visible GPU, single-device simulation of the post-communication EP8 local workload, eager execution, ordinary default tactics, ten warmups, one profiled iteration, cold-L2 preparation, same Nsight Compute command/PM metric and replay policy as the existing W4A4/W4A16 reports. This is not an eight-GPU NCU report or a measurement of communication.
- Same geometry: 4096 global tokens / 4096 local input rows in this simulation, `D=7168`, `E=2048`, `N=256`, `K=8`, 32 local experts starting at 0, TP1, ordinary SwiGLU. Do not accidentally use 512 local input rows simply because EP=8; the pinned NCU helper constructs 4096 rows at this token count.
- Reuse `_create_distributed_weights(32, 2048, 0, device)`: seed1000 for canonical BF16 FC1 `[32,4096,7168]` and FC2 `[32,7168,2048]` weights. Reuse `_create_distributed_inputs(4096,0,1,device)`: activation seed42, router-logit seed137, bias seed911. Reuse `_route_tokens` for DeepSeek-style group routing (8 groups, top4 groups, routed scale2.5). Keeping only dimensions equal is weaker than reusing this realization.
- Prepare through `TrtllmBf16Config.prepare_weights` outside capture, preserving BF16 values. It performs the gated row reorder and BlockMajorK byte layout; a shuffle-only approximation is wrong for SwiGLU (`flashinfer/fused_moe/prepare.py:1271`).
- Pass the unpacked `(topk_indices, topk_values)` tuple: int32 IDs and FP32 weights as produced by `_route_tokens`. Packing IDs and BF16 routing weights would introduce an unnecessary rounding difference. The existing CuTe activation pack preserves these FP32 values (`benchmarks/bench_cute_dsl_moe_distributed.py:1323`).
- API settings: `num_experts=256`, `top_k=8`, `local_num_experts=32`, `local_expert_offset=0`, `intermediate_size=2048`, `tune_max_num_tokens=4096`, `activation_type=Swiglu`, `use_shuffled_weight=True`, `weight_layout=BlockMajorK`, `enable_pdl=True`, `do_finalize=True`. Defaults `alpha=1`, `beta=0`, no effective clamp match the current ordinary-SwiGLU workload. Precomputed routing values already contain their scale; do not rescale the tuple.
- Keep `FLASHINFER_DIST_AWARE_AUTOTUNE=0`, avoid an autotune-enabled scope or imported tactic cache, and record the resolved tactic if available. Default tactics are a matched protocol, not a claim that all backends have been optimally tuned.

## No fused TMA reduction

The public BF16 API has `do_finalize`, not CuTe's `use_fused_finalize` switch. `do_finalize=True` is compatible with the requested prohibition here:

1. `csrc/trtllm_fused_moe_runner.cu:780-794` launches GEMM2 into `workspace.gemm2_output`.
2. Lines797-800 separately call `moe::dev::finalize::run`.
3. `csrc/fused_moe/trtllm_backend/trtllm_fused_moe_dev_kernel.cu:1000` selects the vector-load finalizer for this 4096-token/7168-hidden shape (`28 * 4096 >= 1184`).
4. `finalizeKernelVecLoad`, line842 onward, loads vectors from each selected expert, sums top-k contributions in FP32 registers, converts to BF16, and performs one output store. There is no atomic or TMA reduction in this finalizer. GEMM2 does not receive the routing weights needed to perform the final expert combination.
5. PDL propagates to both GEMM launches and `finalizeData.mUsePdl`. `include/flashinfer/trtllm/fused_moe/DevKernel.h:49` sets programmatic stream serialization in the launch attributes; the vector finalizer waits on the dependency before reading GEMM2 output.

Retain the actual separate finalizer launch in the native capture as runtime corroboration. There is no need to replace the native finalizer or omit it. PR #4985's statement that the CuTe CLI flag does not affect TRTLLM is true but does not mean TRTLLM uses a fused TMA reduction.

## FC1 / FC2 role evidence

- BF16 operation wrapper explicitly selects BF16 activations, BF16 weights, and `NoneFp8` in `flashinfer/fused_moe/core.py:2144` onward. This is W16A16, not W4A16 or FP8.
- FC1's gated path sets `fusedAct=!useDeepSeekFp8` in `csrc/trtllm_fused_moe_runner.cu:145-191`; BF16 therefore fuses ordinary SwiGLU. The separate activation branch in the runner applies to DeepSeek FP8 and does not run here. No FC1 activation quantizer is needed in the pure BF16 path.
- FC1 is `mPermuteGemm1.run` at line704 onward, consuming hidden states and GEMM1 weights and producing the intermediate. FC2 is `mGemm2.run` at line781 onward, consuming that intermediate and GEMM2 weights. Finalizer follows separately.
- Bind actual native action identities to this ordered launch sequence, full native names, and dimension/tactic metadata. Do not infer FC1/FC2 from a shared cubin family name alone. Record action order rather than assume fixed ordinal values from the CuTe captures.

## Metric comparability and limits

Use exactly `TPC.TriageCompute.sm__pipe_tensor_cycles_active_realtime.avg.pct_of_peak_sustained_elapsed` with the same Nsight Compute version, PM sampling settings, and source metric units. Apply the same fixed20–80% window of the unique native workload marker pair enclosed by that series' timestamp axis, retaining finite zero samples. Each report has its own native clock; plot-relative alignment is illustrative and does not make the launches concurrent.

This metric compares tensor-pipeline activity, not achieved BF16/FP4 FLOP/s or a percentage of each datatype's maximum arithmetic throughput. A high activity percentage alone does not establish equal instruction throughput, tile efficiency, total speed, or a causal weight-decode overhead. Whole-kernel boundaries, routing/padding, tile choices, and epilogue work can differ even for equal logical dimensions. The pure BF16 baseline has different stored weight bytes from the NVFP4 arms; this is intentional and should be labeled W16A16.

NCU kernel replay isolates launches and can serialize dependency overlap. Use the separately captured NSYS execution for overlap claims, not the BF16 NCU control. Keep the BF16 report/native hashes, exporter identity, adapter hash, command, exact source pin, and resolved settings with the new capture rather than silently treating it as part of the old two-arm report.

## Added TRTLLM W4A4 control

The same adapter can use `TrtllmFp4Config.prepare_weights` and `trtllm_fp4_block_scale_routed_moe`. Preserve the canonical tensor generation and routing tuple above. The weight helper (`prepare.py:469-671`) uses FP32 global scale1 and 16-value E4M3 blocks, then performs the TRTLLM gated reorder/MMA shuffle. CuTe's helper (`prepare.py:2509-2665`) also uses scale1; its row interleave and block-scale layout differ. **The actual weight recipe is 4over6 MSE/256 under this capture's environment.** Both helpers omit `nvfp4_4over6=` when invoking `fp4_quantize`; its `_UNSET` default resolves the environment (`quantization/fp4_quantization.py:1049,1153`) and passes the recipe to native CUDA. The BF16-input branch threads `recipe.use4Over6`, its error mode and E4M3 maximum into the TMA/non-TMA quantizer (`csrc/nv_internal/cpp/kernels/quantization.cu:570-576`). CuTe's preparation docstring saying weights are "standard-NVFP4 either way" is stale and must not override this call-chain evidence. An earlier version of this audit repeated that stale comment; this paragraph corrects it without changing the benchmark.

For matched activation preparation, reuse `_make_distributed_activation_pack` with per-token activation scaling enabled and the existing MSE/256 4over6 environment. Pass its packed E2M1 payload, linear E4M3 scales, and FP32 `per_token_scale` into the routed TRTLLM API, explicitly declaring `hidden_states_scale_layout=SfLayout.layout_linear`. Do not use `TrtllmFp4Config.prepare_activations`: that convenience helper fixes scale1 and does not return per-token scales (`prepare.py:674-721`). The prepared weight view's FP32 output1/output1_gate/output2 scalar arrays are all ones, consistent with the scale1 weight convention.

`per_token_scale` selects per-token scaling for both GEMMs (`core.py:3625`, `trtllm_fused_moe_runner.cu:443-460`). FC1 fuses SwiGLU but outputs BF16; a separate `invokeNvfp4QuantAndPerTokenScale` quantizes that intermediate before FC2 (`runner.cu:741-774`). This native quantizer resolves the 4over6 recipe from the environment, so the runtime environment must remain identical to the input quantizer's recipe. Record these boundaries explicitly: this is not TRTLLM's block-only path with fused in-place FP4 quantization. CuTe's captured per-token/4over6 arm likewise uses a separate FC2 quantizer, though its implementation, layouts, padding, and tactics differ.

The precomputed routing path returns from `routing_deepseek.cu:493-505` through the shared post-topK pipeline. It does not rerun sigmoid, top-k, renormalization, or routed scaling. The post-topK kernel does not overwrite the caller's FP32 route-weight buffer when explicit IDs are supplied (`RoutingKernel.cuh:366-369`); native finalization consumes its declared FP32 dtype.

TRTLLM W4A4 reaches the same separate finalization call at `runner.cu:797-800`. The no-fused-TMA-reduce proof above therefore applies to both TRTLLM controls. Both must pass `enable_pdl=True` and `do_finalize=True`; capture should show a separate vector finalizer. Bind the W4A4 FC1/FC2 actions around the intervening per-token quantizer, not simply two adjacent native actions.
