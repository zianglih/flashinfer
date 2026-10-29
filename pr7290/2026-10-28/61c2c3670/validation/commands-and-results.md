# PR7290 retained FC2 output simplification: 61c2c367009340ca0ed218511ed9382512860f1b

The committed source matches the completed candidate snapshot byte for byte across all 348 relevant files. The candidate was measured as an unstaged patch on 61249e0bb; committing it did not change the source.

## Environment and timing

`nvcr.io/nvidia/pytorch:26.05-py3`, eight NVIDIA B300 GPUs, CUDA13.2.1.009, driver595.91.07, Python3.12.3, PyTorch2.12.0a0+5aff3928d8.nv26.5.50603568, nvidia-cutlass-dsl4.8.0, cupti-python13.4.0.

Each of 15 jobs ran control/candidate/candidate/control on the same GPU. Fresh processes replayed frozen existing tactics and routes, with 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. Event fallback and autotuning were forbidden. The full comparison has 468 unique workloads, 1,872 medians and 187,200 raw samples. Published external-baseline tables use the geometric mean of the two candidate medians, with every saved external baseline value unchanged. Tokens1/2 were measured but excluded from display and retention.

The local campaign receipt verified all2569 archived files and all source hashes before/after each phase. The PR includes native A2 CSV output; the tables use both A1/A2. The commands below are the recorded candidate observer invocations and environment. Persistent native C++ caches were reused.

## Focused correctness boundary

128 paired graph replays against the earlier padded-output control, NVFP4 N128 and per-token N256. Static/CLC × PDL off/on ×16 routing patterns. Valid FC1 payload/scales, FC2 payload and final values match exactly;16 captured GEMM compilations have no spill sites. Initial stricter poisoned-padding probes reported writes to owned inactive rows. Padding contents are not a public contract; valid-output checks remained enabled. No new full correctness matrix, MX-specific exact gate, or sanitizer run for this candidate.

```json
{
  "complete": true,
  "replays": 128,
  "compiles": 16,
  "spills": 0,
  "lanes": [
    {
      "name": "padding-diagnostic-gpu2",
      "configs": [
        4
      ],
      "shape": [
        385,
        512,
        512
      ],
      "replays": 64,
      "compiles": 8,
      "spills": 0,
      "tensormap_replaces": 0,
      "padding_observations": 32
    },
    {
      "name": "swap-initial-gpu2",
      "configs": [
        5
      ],
      "shape": [
        385,
        512,
        512
      ],
      "replays": 64,
      "compiles": 8,
      "spills": 0,
      "tensormap_replaces": 0,
      "padding_observations": 0
    }
  ]
}
```

## Local checks

All scoped hooks and commit hooks passed without modifying the measured source. The follow-up changes five files, +131/−262 lines. It changes no W4A16 kernel, layout or tactic.

```sh
git diff --check 61249e0bb 61c2c367009340ca0ed218511ed9382512860f1b
pre-commit run --files flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab.py flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_prepare.py flashinfer/fused_moe/cute_dsl/fused_moe.py
```

## Source and result binding

```json
{
  "complete": true,
  "head": "61c2c367009340ca0ed218511ed9382512860f1b",
  "measured_parent": "61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8",
  "source_files_verified": 348,
  "fresh_cells": 468,
  "fresh_medians": 936,
  "fresh_samples": 93600,
  "all_control_fields_unchanged": true,
  "archive_files_verified": 2569,
  "outputs": {
    "ep": {
      "summary-cells.csv": "d1b62312f9b3f3e88ef4ef746fbe7fb781021255f3013547497c9fc140d3d993",
      "summary-table.md": "adfb0d6e476f1509eef0977385d256ecf8968e04a3791b2f7eafabf601c1a0c3",
      "native-a2-output.md": "1e7de89ab8dac75c35aa6e83d3c506f3edf767e2ddaa0b62599c0d940e8ad620",
      "provenance.json": "6c2f4807b3404333e443b8fd2df48558dd04ffffd0067fed422afec8734c7bc9"
    },
    "tp": {
      "summary-cells.csv": "e6259006c560836cf9e0b925d0761250494a5992a67af6fed16bdfa2fde85def",
      "summary-table.md": "517fbbeaca2329a9bb99927ccac47ed9a6ae66df057f73e23c2ea845758279e4",
      "native-a2-output.md": "9f2eb934370e04e9067406183b6c1e6c19563db7510bf40ca09f7e1a82e8ae4d",
      "provenance.json": "9e6c545c47ad4b2dd25b076cb8a4f7a1290a5a22ce56c6b7d38b92b13898af7e"
    }
  }
}
```

## Recorded candidate commands

### ep-kimi-k3-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=5 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-kimi-k3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-kimi-k3-mxfp/1-candidate -- --functional-api --model kimi-k3 --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-kimi-k3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=5 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-kimi-k3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-kimi-k3-mxfp/2-candidate -- --functional-api --model kimi-k3 --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-kimi-k3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### ep-kimi-k3-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=4 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-kimi-k3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-kimi-k3-nvfp4/1-candidate -- --functional-api --model kimi-k3 --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-kimi-k3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=4 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-kimi-k3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-kimi-k3-nvfp4/2-candidate -- --functional-api --model kimi-k3 --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-kimi-k3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### ep-nemo3-ultra-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=7 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-nemo3-ultra-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-nemo3-ultra-mxfp/1-candidate -- --functional-api --model nemo3-ultra --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-nemo3-ultra-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=7 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-nemo3-ultra-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-nemo3-ultra-mxfp/2-candidate -- --functional-api --model nemo3-ultra --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-nemo3-ultra-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### ep-nemo3-ultra-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=6 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-nemo3-ultra-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-nemo3-ultra-nvfp4/1-candidate -- --functional-api --model nemo3-ultra --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-nemo3-ultra-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=6 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-nemo3-ultra-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-nemo3-ultra-nvfp4/2-candidate -- --functional-api --model nemo3-ultra --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-nemo3-ultra-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### ep-v3-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v3-mxfp/1-candidate -- --functional-api --model v3 --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v3-mxfp/2-candidate -- --functional-api --model v3 --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### ep-v3-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v3-nvfp4/1-candidate -- --functional-api --model v3 --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v3-nvfp4/2-candidate -- --functional-api --model v3 --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### ep-v41-flash-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=3 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v41-flash-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v41-flash-mxfp/1-candidate -- --functional-api --model v41-flash --ep 4 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v41-flash-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=3 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v41-flash-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v41-flash-mxfp/2-candidate -- --functional-api --model v41-flash --ep 4 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v41-flash-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### ep-v41-flash-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=2 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v41-flash-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v41-flash-nvfp4/1-candidate -- --functional-api --model v41-flash --ep 4 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v41-flash-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=2 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v41-flash-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v41-flash-nvfp4/2-candidate -- --functional-api --model v41-flash --ep 4 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/ep-v41-flash-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### tp-kimi-k3-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=4 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-kimi-k3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-kimi-k3-mxfp/1-candidate -- --functional-api --model kimi-k3 --ep 1 --tp 8 --quant-family mxfp --backends cute-dsl-w4a8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-kimi-k3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=4 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-kimi-k3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-kimi-k3-mxfp/2-candidate -- --functional-api --model kimi-k3 --ep 1 --tp 8 --quant-family mxfp --backends cute-dsl-w4a8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-kimi-k3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### tp-kimi-k3-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=3 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-kimi-k3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-kimi-k3-nvfp4/1-candidate -- --functional-api --model kimi-k3 --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-kimi-k3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=3 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-kimi-k3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-kimi-k3-nvfp4/2-candidate -- --functional-api --model kimi-k3 --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-kimi-k3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### tp-nemo3-ultra-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=6 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-nemo3-ultra-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-nemo3-ultra-mxfp/1-candidate -- --functional-api --model nemo3-ultra --ep 1 --tp 8 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-nemo3-ultra-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=6 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-nemo3-ultra-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-nemo3-ultra-mxfp/2-candidate -- --functional-api --model nemo3-ultra --ep 1 --tp 8 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-nemo3-ultra-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### tp-nemo3-ultra-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=5 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-nemo3-ultra-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-nemo3-ultra-nvfp4/1-candidate -- --functional-api --model nemo3-ultra --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-nemo3-ultra-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=5 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-nemo3-ultra-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-nemo3-ultra-nvfp4/2-candidate -- --functional-api --model nemo3-ultra --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-nemo3-ultra-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### tp-v3-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v3-mxfp/1-candidate -- --functional-api --model v3 --ep 1 --tp 8 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v3-mxfp/2-candidate -- --functional-api --model v3 --ep 1 --tp 8 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### tp-v3-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v3-nvfp4/1-candidate -- --functional-api --model v3 --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v3-nvfp4/2-candidate -- --functional-api --model v3 --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### tp-v41-flash-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=2 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v41-flash-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v41-flash-nvfp4/1-candidate -- --functional-api --model v41-flash --ep 1 --tp 4 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v41-flash-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=2 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v41-flash-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/swap-ab-hybrid-output/fc2-01/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v41-flash-nvfp4/2-candidate -- --functional-api --model v41-flash --ep 1 --tp 4 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/fc2-hybrid-vs-head/perf/tp-v41-flash-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

## Full-PR file accounting

Diff at `61c2c3670` against merge base `002529e1`, including comments and docstrings:

| Component | Added | Removed | Net |
|---|---:|---:|---:|
| New swap-AB kernel | +3,225 | −0 | +3,225 |
| New swap-AB dispatch and autotuning | +764 | −0 | +764 |
| W4A16-specific kernel, dispatch and reference | +129 | −333 | -204 |
| Shared preparation, combine and quantization | +723 | −181 | +542 |
| Shared API, wrappers, weight preparation and autotuning | +380 | −115 | +265 |
| Benchmark scripts | +1,046 | −477 | +569 |
| Testing and manual sanitizer | +2,201 | −59 | +2,142 |
| Trace templates | +68 | −35 | +33 |
| Documentation | +5 | −2 | +3 |
| **Total** | **+8,541** | **−1,202** | **+7,339** |

Counts partition files without double counting. W4A16 includes removal of its old prepare file; the replacement prepare, combine and mixed wrappers are counted under shared code.

```json
[
  {
    "path": "benchmarks/bench_cute_dsl_moe_distributed.py",
    "component": "Benchmark scripts",
    "added": 22,
    "removed": 8
  },
  {
    "path": "benchmarks/bench_moe_deepseek.py",
    "component": "Benchmark scripts",
    "added": 1024,
    "removed": 469
  },
  {
    "path": "docs/design_docs/flashinfer_moe_api.md",
    "component": "Documentation",
    "added": 5,
    "removed": 2
  },
  {
    "path": "flashinfer/fused_moe/__init__.py",
    "component": "Shared API, wrappers, weight preparation and autotuning",
    "added": 2,
    "removed": 0
  },
  {
    "path": "flashinfer/fused_moe/api.py",
    "component": "Shared API, wrappers, weight preparation and autotuning",
    "added": 11,
    "removed": 0
  },
  {
    "path": "flashinfer/fused_moe/cute_dsl/blackwell/custom_pipeline.py",
    "component": "Shared preparation, combine and quantization",
    "added": 4,
    "removed": 1
  },
  {
    "path": "flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py",
    "component": "Shared preparation, combine and quantization",
    "added": 66,
    "removed": 27
  },
  {
    "path": "flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab.py",
    "component": "New swap-AB dispatch and autotuning",
    "added": 602,
    "removed": 0
  },
  {
    "path": "flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py",
    "component": "New swap-AB kernel",
    "added": 3225,
    "removed": 0
  },
  {
    "path": "flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_prepare.py",
    "component": "Shared preparation, combine and quantization",
    "added": 334,
    "removed": 0
  },
  {
    "path": "flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_tuner.py",
    "component": "New swap-AB dispatch and autotuning",
    "added": 162,
    "removed": 0
  },
  {
    "path": "flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py",
    "component": "W4A16-specific kernel, dispatch and reference",
    "added": 25,
    "removed": 11
  },
  {
    "path": "flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py",
    "component": "W4A16-specific kernel, dispatch and reference",
    "added": 88,
    "removed": 100
  },
  {
    "path": "flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_prepare.py",
    "component": "W4A16-specific kernel, dispatch and reference",
    "added": 0,
    "removed": 216
  },
  {
    "path": "flashinfer/fused_moe/cute_dsl/blackwell/utils.py",
    "component": "Shared preparation, combine and quantization",
    "added": 6,
    "removed": 0
  },
  {
    "path": "flashinfer/fused_moe/cute_dsl/fused_moe.py",
    "component": "Shared API, wrappers, weight preparation and autotuning",
    "added": 241,
    "removed": 96
  },
  {
    "path": "flashinfer/fused_moe/cute_dsl/tuner.py",
    "component": "Shared API, wrappers, weight preparation and autotuning",
    "added": 41,
    "removed": 10
  },
  {
    "path": "flashinfer/fused_moe/prepare.py",
    "component": "Shared API, wrappers, weight preparation and autotuning",
    "added": 53,
    "removed": 1
  },
  {
    "path": "flashinfer/fused_moe/runners.py",
    "component": "Shared API, wrappers, weight preparation and autotuning",
    "added": 32,
    "removed": 8
  },
  {
    "path": "flashinfer/quantization/kernels/nvfp4_quantize.py",
    "component": "Shared preparation, combine and quantization",
    "added": 313,
    "removed": 153
  },
  {
    "path": "flashinfer/trace/templates/moe.py",
    "component": "Trace templates",
    "added": 68,
    "removed": 35
  },
  {
    "path": "scripts/sanitize_cute_dsl_moe_swap_ab.py",
    "component": "Testing and manual sanitizer",
    "added": 710,
    "removed": 0
  },
  {
    "path": "tests/moe/test_cute_dsl_fused_moe.py",
    "component": "Testing and manual sanitizer",
    "added": 427,
    "removed": 41
  },
  {
    "path": "tests/moe/test_cute_dsl_mxfp8_moe.py",
    "component": "Testing and manual sanitizer",
    "added": 29,
    "removed": 6
  },
  {
    "path": "tests/moe/test_unified_moe.py",
    "component": "Testing and manual sanitizer",
    "added": 67,
    "removed": 7
  },
  {
    "path": "tests/moe/utils.py",
    "component": "Testing and manual sanitizer",
    "added": 13,
    "removed": 5
  },
  {
    "path": "tests/test_helpers/cute_dsl_moe_swap_ab_reference.py",
    "component": "Testing and manual sanitizer",
    "added": 955,
    "removed": 0
  },
  {
    "path": "tests/test_helpers/w4a16_reference.py",
    "component": "W4A16-specific kernel, dispatch and reference",
    "added": 16,
    "removed": 6
  }
]
```
