# PR7290 pipeline polish: 33b7e5260132eb4ba2fdfdd97bd71a892f04a481

The committed source matches all348 source hashes of the measured candidate. Three independent screens used same-GPU C-A-A-C against retained61c2. The combined full refresh uses two new candidate passes and reuses the retained61c2/external baselines. Tokens1/2 are measured but excluded from display and retention.

## Environment

`nvcr.io/nvidia/pytorch:26.05-py3`; eight NVIDIA B300 GPUs; CUDA13.2.1.009; driver595.91.07; Python3.12.3; PyTorch2.12.0a0+5aff3928d8.nv26.5.50603568; nvidia-cutlass-dsl4.8.0; cupti-python13.4.0. Native C++ caches remain on persistent cluster storage.

Each public benchmark pass uses frozen winners/routes,10 warmups and100 cold-L2 CUDA-graph CUPTI samples; event fallback and autotuning are forbidden. NVFP4 includes initial activation quantization. The full refresh has468 workloads,936 fresh medians and93,600 fresh samples. All saved external control values remain unchanged.

## Qualification

Combined gate:256 paired exact graph replays over all four scaled formats, static/CLC, PDL off/on, one/two CTA and16 route patterns. Valid intermediate/final payloads and scales match. Resource counts across all32 GEMM pairs are unchanged and no spill sites grow. Independent SF-prefix qualification adds532 paired replays/152 GEMM pairs, including partial K64/K128/K192 and24 aligned raw-PTX identities. Padding contents remain unspecified. No sanitizer run this iteration.

```json
{
  "complete": true,
  "provisional": true,
  "effective_base": "61c2c367009340ca0ed218511ed9382512860f1b",
  "actual_control_git_head": "61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8",
  "control_source_matches_committed_effective_base": true,
  "candidate_git_head": "61c2c367009340ca0ed218511ed9382512860f1b",
  "candidate_kernel_sha256": "b668b2736ea9770e0ca2d45a91f461601953bfaa20f8f807731a641fa20d93d8",
  "candidate_patch_sha256": "678a1e0acdb137fd8101c418dd0ad1eb3e4fdcc58bba81acb8e0c68e226c521f",
  "remote_config": "/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/config.json",
  "config_sha256": "6a22400f3a90244ca8eb8dba2c156a2cd047147bd74094955f045f254dfd30f3",
  "source_files_per_arm": 348,
  "exact_replay_pairs": 256,
  "gemm_pairs": 32,
  "all_resources_equal": true,
  "local_and_uniform_spill_growth": false,
  "static_fc1_all_8_raw_ptx_and_encoded_sass_identical": true,
  "static_all_phase_identities": 10,
  "config_ids": [
    0,
    2,
    5,
    11
  ],
  "hidden": 512,
  "intermediate": 384,
  "tokens": 385,
  "routing_patterns_per_variant": 16,
  "topology": [
    "static",
    "CLC"
  ],
  "pdl": [
    false,
    true
  ],
  "cta_groups": [
    1,
    2
  ],
  "source_outside_kernel_unchanged": true,
  "staged_changes": false,
  "gpu6_released": true,
  "performance_launched": false,
  "sanitizer_run": false,
  "evidence_sha256": {
    "source-local.json": "e3cf9c2c9da9e0f92a2255270c25bb416f121cda4c2ded25f1bcc397978e8aac",
    "composition-proof.json": "748384df2bb0a9ac83aa07fde18173ceb4c83e7b7a1479d1ab0939dc3b1dd423",
    "precommit.log": "87bd1c345e4ae6dd22c74b419eba5c052e7d4f1ad45e4add9eba2627621ef694",
    "evidence/codegen-summary.json": "1716db1dae63497e411b35d4b1a5bee8a637c102b8206f87221731b55a894f7d",
    "evidence/archive-manifest.json": "77df0ddcf59fffbec051a57483d699aea40166159060b325fdc796efc09f384d",
    "evidence-verification.json": "c3f879414cf2f4d8fe9cdf72b3bea5a9729f3545b06aa93a26be842914ae8820",
    "RESULTS.md": "7648f0d1b50b2df37071f552231b2f2b84db91272c5af1ebbed4acc4b775dff3"
  },
  "boundary": "Interaction qualification only. The individual SF-prefix gate retains three other one-CTA per-token FC2 spill-growth variants. Static sites are not executed instruction counts. No retention or performance conclusion."
}
```

## Local checks

Scoped and commit pre-commit hooks passed without changing the measured source. This follow-up changes only moe_swap_ab_kernel.py; no W4A16 implementation, public API, layout or tactic change.

```sh
git diff --check 61c2c367 33b7e5260132eb4ba2fdfdd97bd71a892f04a481
pre-commit run --files flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py
```

## Source/result binding

```json
{
  "complete": true,
  "head": "33b7e5260132eb4ba2fdfdd97bd71a892f04a481",
  "measured_parent": "61c2c367009340ca0ed218511ed9382512860f1b",
  "source_files_verified": 348,
  "fresh_cells": 468,
  "fresh_medians": 936,
  "fresh_samples": 93600,
  "all_control_fields_unchanged": true,
  "archive_files_verified": 2103,
  "outputs": {
    "ep": {
      "summary-cells.csv": "85732d57ca35e03821bec942ec127d7ded756a79152d34b9751a11eb3286d113",
      "summary-table.md": "01c79cbb4fe8c356a1dcdbf9804bf24a53f60dc4033220e701f3ff3c065d2f70",
      "native-a2-output.md": "77b41068be83a9e684ddae26e8d8cffbb575c0e7491e00c76e48c0f12c406962",
      "provenance.json": "80ac596fe71a670ba31cbc9a6c4622e4048fde7af772cbafb0c8defe9ca1446c"
    },
    "tp": {
      "summary-cells.csv": "f2b20cb0a08e13cc4778f69292d1babb7f4b798fd2940eceb62c2969780b07ba",
      "summary-table.md": "30f21c7050a00a704e42a51aa6c5540e8c247ef7c9054e5201877b4def0c04f2",
      "native-a2-output.md": "754ba543c8799dcbe5b61eebfa3fec38882b693ae61de8658707d671f09af51a",
      "provenance.json": "eafe99c2c15605eeed426c39fbee9f52b71ca1475bb75513311ca38ab48d1e43"
    }
  }
}
```

## Recorded candidate commands

### ep-kimi-k3-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=5 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-kimi-k3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-kimi-k3-mxfp/1-candidate -- --functional-api --model kimi-k3 --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-kimi-k3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=5 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-kimi-k3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-kimi-k3-mxfp/2-candidate -- --functional-api --model kimi-k3 --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-kimi-k3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### ep-kimi-k3-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=4 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-kimi-k3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-kimi-k3-nvfp4/1-candidate -- --functional-api --model kimi-k3 --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-kimi-k3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=4 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-kimi-k3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-kimi-k3-nvfp4/2-candidate -- --functional-api --model kimi-k3 --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-kimi-k3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### ep-nemo3-ultra-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=7 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-nemo3-ultra-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-nemo3-ultra-mxfp/1-candidate -- --functional-api --model nemo3-ultra --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-nemo3-ultra-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=7 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-nemo3-ultra-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-nemo3-ultra-mxfp/2-candidate -- --functional-api --model nemo3-ultra --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-nemo3-ultra-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### ep-nemo3-ultra-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=6 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-nemo3-ultra-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-nemo3-ultra-nvfp4/1-candidate -- --functional-api --model nemo3-ultra --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-nemo3-ultra-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=6 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-nemo3-ultra-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-nemo3-ultra-nvfp4/2-candidate -- --functional-api --model nemo3-ultra --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-nemo3-ultra-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### ep-v3-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v3-mxfp/1-candidate -- --functional-api --model v3 --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v3-mxfp/2-candidate -- --functional-api --model v3 --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### ep-v3-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v3-nvfp4/1-candidate -- --functional-api --model v3 --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v3-nvfp4/2-candidate -- --functional-api --model v3 --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### ep-v41-flash-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=3 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v41-flash-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v41-flash-mxfp/1-candidate -- --functional-api --model v41-flash --ep 4 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v41-flash-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=3 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v41-flash-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v41-flash-mxfp/2-candidate -- --functional-api --model v41-flash --ep 4 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v41-flash-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### ep-v41-flash-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=2 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v41-flash-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v41-flash-nvfp4/1-candidate -- --functional-api --model v41-flash --ep 4 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v41-flash-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=2 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v41-flash-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v41-flash-nvfp4/2-candidate -- --functional-api --model v41-flash --ep 4 --tp 1 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/ep-v41-flash-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### tp-kimi-k3-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=4 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-kimi-k3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-kimi-k3-mxfp/1-candidate -- --functional-api --model kimi-k3 --ep 1 --tp 8 --quant-family mxfp --backends cute-dsl-w4a8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-kimi-k3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=4 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-kimi-k3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-kimi-k3-mxfp/2-candidate -- --functional-api --model kimi-k3 --ep 1 --tp 8 --quant-family mxfp --backends cute-dsl-w4a8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-kimi-k3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### tp-kimi-k3-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=3 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-kimi-k3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-kimi-k3-nvfp4/1-candidate -- --functional-api --model kimi-k3 --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-kimi-k3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=3 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-kimi-k3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-kimi-k3-nvfp4/2-candidate -- --functional-api --model kimi-k3 --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-kimi-k3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### tp-nemo3-ultra-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=6 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-nemo3-ultra-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-nemo3-ultra-mxfp/1-candidate -- --functional-api --model nemo3-ultra --ep 1 --tp 8 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-nemo3-ultra-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=6 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-nemo3-ultra-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-nemo3-ultra-mxfp/2-candidate -- --functional-api --model nemo3-ultra --ep 1 --tp 8 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-nemo3-ultra-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### tp-nemo3-ultra-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=5 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-nemo3-ultra-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-nemo3-ultra-nvfp4/1-candidate -- --functional-api --model nemo3-ultra --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-nemo3-ultra-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=5 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-nemo3-ultra-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-nemo3-ultra-nvfp4/2-candidate -- --functional-api --model nemo3-ultra --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-nemo3-ultra-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### tp-v3-mxfp

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v3-mxfp/1-candidate -- --functional-api --model v3 --ep 1 --tp 8 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v3-mxfp/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v3-mxfp/2-candidate -- --functional-api --model v3 --ep 1 --tp 8 --quant-family mxfp --backends cute-dsl-w4a8,cute-dsl-mxfp8 --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v3-mxfp/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune
```

### tp-v3-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v3-nvfp4/1-candidate -- --functional-api --model v3 --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=0 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v3-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v3-nvfp4/2-candidate -- --functional-api --model v3 --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v3-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

### tp-v41-flash-nvfp4

Pass A1: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=2 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v41-flash-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v41-flash-nvfp4/1-candidate -- --functional-api --model v41-flash --ep 1 --tp 4 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v41-flash-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

Pass A2: exit0; verified=True

```sh
env CUDA_VISIBLE_DEVICES=2 PYTHONPATH=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate:/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-benchmark-table-20261027/python-deps FLASHINFER_WORKSPACE_BASE=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/compile FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1 FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0 TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0 MAX_JOBS=8 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 TRITON_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v41-flash-nvfp4/triton/candidate /data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/observe_benchmark.py --repo /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/flashinfer-candidate --output /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v41-flash-nvfp4/2-candidate -- --functional-api --model v41-flash --ep 1 --tp 4 --quant-family nvfp4 --backends cutedsl,cute-dsl-per-token --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/post-hybrid-polish/composed/full/perf/tp-v41-flash-nvfp4/cache-candidate --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

## Full-PR file accounting

Diff at `33b7e5260` against merge base `002529e1`, including comments and docstrings:

| Component | Added | Removed | Net |
|---|---:|---:|---:|
| New swap-AB kernel | +3,248 | −0 | +3,248 |
| New swap-AB dispatch and autotuning | +764 | −0 | +764 |
| W4A16-specific kernel, dispatch and reference | +129 | −333 | -204 |
| Shared preparation, combine and quantization | +723 | −181 | +542 |
| Shared API, wrappers, weight preparation and autotuning | +380 | −115 | +265 |
| Benchmark scripts | +1,046 | −477 | +569 |
| Testing and manual sanitizer | +2,201 | −59 | +2,142 |
| Trace templates | +68 | −35 | +33 |
| Documentation | +5 | −2 | +3 |
| **Total** | **+8,564** | **−1,202** | **+7,362** |

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
    "added": 3248,
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
