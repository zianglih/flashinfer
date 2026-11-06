## Benchmarks

Current `d1767be1f`: all five CuTe formats on an eight-B300 devbox, eight independent benchmark workers, `nvcr.io/nvidia/pytorch:26.05-py3` (CUDA 13.2, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CuTe DSL 4.8.0). Fresh native managed-cache tuning precedes two frozen replay passes using the public functional API, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples per pass; event fallback and tuning during measurement are prohibited. Ratios compare geometric means of the two pass medians.

Comparison baselines reuse the saved campaign: TRTLLM retained as `1e69d0a39`, non-swap CuTe `e2728a290`, and pre-PR W4A16 `002529e1` with up64/gate64 weights. NVFP4 includes initial activation quantization; MX inputs are prequantized. Per-token uses MSE 4over6, 256 scaling and 4over6 fast math, with FP4 quantization fast math disabled. Communication and tokens 1/2 are excluded from the summary and retention.

Models: V3 EP8; V4.1-Flash EP4; Kimi K3 EP8 with SiTU; Nemotron-3 Ultra EP8 routed latent experts (D2048/I5120, 512 experts, top-22, ReLU2, normalized sigmoid routing scaled by 5). Nemotron projections and shared experts are excluded. Swap-AB finalize is unfused; saved non-swap MX uses its required fused finalize. Unsupported K3 baselines are N/A.

Public workload commands below perform tuning, then two replay passes. The recorded campaign also uses an observer to verify native cache hits, routes and all raw CUPTI samples. Use empty cache directories for a new campaign:

```bash
unset FLASHINFER_NVFP4_4OVER6 FLASHINFER_NVFP4_4OVER6_ERR_MODE \
  FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH FLASHINFER_NVFP4_4OVER6_E4M3_USE_256
export FLASHINFER_CUDA_ARCH_LIST=10.3a TRTLLM_ENABLE_PDL=1
export FLASHINFER_DIST_AWARE_AUTOTUNE=0 FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1
export FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0
tokens=1,2,4,8,16,32,64,128,256,512,4096,8192,16384
for model in v3 v41-flash kimi-k3 nemo3-ultra; do
  if [ "$model" = v41-flash ]; then ep=4; else ep=8; fi
  for phase in tune a1 a2; do
    replay=()
    if [ "$phase" != tune ]; then replay=(--no-autotune); fi
    python benchmarks/bench_moe_deepseek.py --functional-api --model "$model" --ep "$ep" --tp 1 \
      --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token \
      --num-tokens "$tokens" --swap-ab --no-fused-finalize --include-activation-quant \
      --warmup 10 --iters 100 --cache "$model-nvfp4-cache" "${replay[@]}"
    python benchmarks/bench_moe_deepseek.py --functional-api --model "$model" --ep "$ep" --tp 1 \
      --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 \
      --num-tokens "$tokens" --swap-ab --no-fused-finalize \
      --warmup 10 --iters 100 --cache "$model-mxfp-cache" "${replay[@]}"
  done
done
```

Small differences may reflect fresh tuning choices or pass-to-pass timing variation; reported values use the complete two-pass campaign.
