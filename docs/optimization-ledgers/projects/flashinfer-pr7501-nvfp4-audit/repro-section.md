### Reproduction

Run inside `nvcr.io/nvidia/pytorch:26.05-py3`, preserving its PyTorch/CUDA installation. Each source arm has its own checkout and JIT cache. This script uses the PR's dedicated benchmark for every arm.

```bash
mkdir -p nvfp4-regression
cd nvfp4-regression
NVFP4_WORKSPACE_ROOT="$PWD"
mkdir -p "$NVFP4_WORKSPACE_ROOT/results" "$NVFP4_WORKSPACE_ROOT/caches"
git clone --recursive https://github.com/flashinfer-ai/flashinfer.git flashinfer
git -C flashinfer fetch https://github.com/zianglih/flashinfer.git \
  9ac7ef83e8013cc0d37d5fd8ee62f325f211f6c4
git -C flashinfer checkout --detach 9ac7ef83e8013cc0d37d5fd8ee62f325f211f6c4
git -C flashinfer worktree add --detach ../before 03d7f4a399a47e72d93631e19becd804147fc47b
git -C flashinfer worktree add --detach ../regressed fb022756415cc9cad1e1a64ee918860e17638fe8
git -C flashinfer worktree add --detach ../historical-fixed fb022756415cc9cad1e1a64ee918860e17638fe8
git -C flashinfer worktree add --detach ../main-before 3472ad3ab194141353be7199807cb29f0d20af09
git -C flashinfer diff 3472ad3 9ac7ef83 -- \
  csrc/nv_internal/tensorrt_llm/kernels/quantization_utils.cuh | \
  git -C historical-fixed apply

PIP_CONSTRAINT= python -m pip install \
  apache-tvm-ffi==0.1.15.post2 'nvidia-cutlass-dsl[cu13]==4.8.0' \
  nvidia-cudnn-frontend==1.32.0 cuda-tile==1.7.0 \
  cupti-python==13.4.0 nvidia-cuda-cupti==13.4.92 \
  pytest==9.2.0 ninja==1.13.2 einops tabulate packaging
for arm in before regressed historical-fixed main-before flashinfer; do
  git -C "$arm" submodule update --init 3rdparty/cutlass 3rdparty/spdlog 3rdparty/cccl
  (cd "$NVFP4_WORKSPACE_ROOT/$arm" && \
    BUILD_NVEP=0 PIP_CONSTRAINT= python -m pip install --no-deps --no-build-isolation -e .)
done

export CUDA_VISIBLE_DEVICES=0 FLASHINFER_CUDA_ARCH_LIST=10.3a
export MAX_JOBS=8 FLASHINFER_NVCC_THREADS=2 OMP_NUM_THREADS=1
export TRTLLM_ENABLE_PDL=0 FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=0
export TRTLLM_DISABLE_FP4_QUANT_FAST_MATH=0
# Remove inherited recipe-selection variables, including legacy aliases.
for name in $(compgen -v | grep -E '^(FLASHINFER|TRTLLM)_NVFP4_4OVER6'); do
  unset "$name"
done
nvidia-smi -i 0 -lgc 1980,1980
NVFP4_PR_RUNNER="$NVFP4_WORKSPACE_ROOT/flashinfer/benchmarks/bench_nvfp4_quantize_backend_comparison.py"

run_nvfp4_arm() {
  local arm="$1" round="$2" warmups="$3" iterations="$4"
  (
    cd "$NVFP4_WORKSPACE_ROOT/$arm"
    export PYTHONPATH="$PWD"
    export FLASHINFER_WORKSPACE_BASE="$NVFP4_WORKSPACE_ROOT/caches/$arm/native"
    export CUTE_DSL_CACHE_DIR="$NVFP4_WORKSPACE_ROOT/caches/$arm/cute"
    export TRITON_CACHE_DIR="$NVFP4_WORKSPACE_ROOT/caches/$arm/triton"
    python "$NVFP4_PR_RUNNER" \
      --m-values 1024 2048 --k-values 4096 7168 8192 \
      --layouts swizzled_128x4 --dtype bfloat16 --seed 42 \
      --num-iters "$iterations" --dry-run-iters "$warmups" --cuda-graph \
      --csv-output "$NVFP4_WORKSPACE_ROOT/results/$arm-r$round.csv" --no-heatmap
  )
}
# Compilation/warmup is excluded from measured results.
for arm in before regressed historical-fixed main-before flashinfer; do
  run_nvfp4_arm "$arm" 0 1 1
done
orders=(
  'before regressed historical-fixed main-before flashinfer'
  'before flashinfer main-before historical-fixed regressed'
  'historical-fixed main-before flashinfer before regressed'
  'historical-fixed regressed before flashinfer main-before'
  'flashinfer before regressed historical-fixed main-before'
  'flashinfer main-before historical-fixed regressed before'
)
round=1
for order in "${orders[@]}"; do
  for arm in $order; do run_nvfp4_arm "$arm" "$round" 100 1000; done
  round=$((round + 1))
done
```

Every measured dedicated CSV has 12,000 rows: six shapes × two backends × 1000 samples. Require successful backend verification and no CUPTI fallback. The historical-fixed header used for measurement has the same executable changes as the patch above; comments/formatting do not affect its measured instructions.

Supplemental exact issue cases use the existing unified runner. The following writes its testlist and runs one arm/round; repeat across the same five arms for six serial rounds with unique output files and isolated caches.

```bash
cat > "$NVFP4_WORKSPACE_ROOT/issue-cases.txt" <<'CASES'
--routine nvfp4_quantize --m 1024 --k 7168 --input_dtype bfloat16 --global_scale 1.0 --sf_vec_size 16 --backends cuda --sf_layout 128x4 --random_seed 42 --num_iters 1000 --dry_run_iters 100 --use_cupti --case_tag nvfp4_m1024_k7168
--routine nvfp4_batched_quantize --batch_size 4 --m 1024 --k 4096 --input_dtype bfloat16 --global_scale 1.0 --sf_vec_size 16 --backends cuda --random_seed 42 --num_iters 1000 --dry_run_iters 100 --use_cupti --case_tag nvfp4_batched_basic
--routine nvfp4_batched_quantize --batch_size 8 --m 2048 --k 8192 --input_dtype bfloat16 --global_scale 1.0 --sf_vec_size 16 --backends cuda --random_seed 42 --num_iters 1000 --dry_run_iters 100 --use_cupti --case_tag nvfp4_batched_large
CASES
arm=flashinfer
round=1
(
  cd "$NVFP4_WORKSPACE_ROOT/$arm"
  export PYTHONPATH="$PWD"
  export FLASHINFER_WORKSPACE_BASE="$NVFP4_WORKSPACE_ROOT/caches/$arm/native"
  export CUTE_DSL_CACHE_DIR="$NVFP4_WORKSPACE_ROOT/caches/$arm/cute"
  python benchmarks/flashinfer_benchmark.py \
    --testlist "$NVFP4_WORKSPACE_ROOT/issue-cases.txt" \
    --output_path "$NVFP4_WORKSPACE_ROOT/results/issue-$arm-r$round.csv"
)
# Validate the actual PR checkout. GPU1 was used for these tests.
cd "$NVFP4_WORKSPACE_ROOT/flashinfer"
export PYTHONPATH="$PWD"
export FLASHINFER_WORKSPACE_BASE="$NVFP4_WORKSPACE_ROOT/caches/flashinfer/native"
export CUTE_DSL_CACHE_DIR="$NVFP4_WORKSPACE_ROOT/caches/flashinfer/cute"
CUDA_VISIBLE_DEVICES=1 python -m pytest -q --disable-warnings \
  tests/utils/test_fp4_quantize.py tests/utils/test_fp4_quantize_padding.py
CUDA_VISIBLE_DEVICES=1 python -m pytest -q --disable-warnings \
  tests/utils/test_fp4_quantize.py::test_nvfp4_quantize_cute_dsl_device_scale_cuda_graph
pre-commit run --all-files
nvidia-smi -i 0 -rgc
```
