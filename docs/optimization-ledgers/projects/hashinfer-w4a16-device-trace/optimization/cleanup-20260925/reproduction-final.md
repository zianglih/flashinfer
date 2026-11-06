Run separately from each recorded source in the image above, keeping its PyTorch build and using fresh source-specific output/cache directories:

```bash
set -euo pipefail
python -m pip install -e '.[test,bench]' \
  'nvidia-cutlass-dsl[cu13]==4.8.0' 'cuda-python==13.2.0' \
  'nvshmem4py-cu13==0.3.1' 'nvidia-nvshmem-cu13==3.8.0' \
  'apache-tvm-ffi==0.1.14.post1' 'cuda-core==1.2.1' 'pytest==9.1.1' \
  'cupti-python==13.4.0' 'nvidia-cuda-cupti==13.4.92' \
  'nvidia-cuda-cccl==13.3.4.3.1'
export HASHINFER_TRACE_IMAGE=nvcr.io/nvidia/pytorch:26.05-py3
unset CUTE_DSL_COMPILER_OPT
bench_out="$PWD/native-fresh-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir "$bench_out"
CUDA_VISIBLE_DEVICES=0,1,2,3 python -m torch.distributed.run \
  --master-addr=127.0.0.1 --master-port=29874 --nproc-per-node=4 \
  benchmarks/bench_cute_dsl_moe_distributed.py --implementation hashinfer --num-gpus 4 \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 \
  --warmup 3 --iters 100 --timing cupti --cuda-graph --log-timing-samples \
  --megamoe-knobs auto --cache-dir "$bench_out/ep4-cache"
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python -m torch.distributed.run \
  --master-addr=127.0.0.1 --master-port=29874 --nproc-per-node=8 \
  benchmarks/bench_cute_dsl_moe_distributed.py --implementation hashinfer --num-gpus 8 \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 \
  --warmup 3 --iters 100 --timing cupti --cuda-graph --log-timing-samples \
  --megamoe-knobs auto --cache-dir "$bench_out/ep8-cache"
```

These public commands reproduce the native workload and timer. Recorded measurements also use the project-owned source-attestation wrapper for untimed finite/repeated output checks, fixture/output hashes and selected independent references. The original, pre-cleanup x8, and final cleanup sweeps use `benchmark_checked_final.py`, SHA256 `42f7ee3c15b575048013eb9d5f92f0df331cdfffdf17b699dbd9f2fcaa7a9222`, under the same torchrun arguments above. The wrapper checks finite/repeated outputs for every row and independent references only at native global T128 and uniform global T1024. Complete source/fixture/output/cache closure and all raw samples are preserved locally. The plain benchmark does not supply these additional checks.

Run each selected node in a fresh process from commit `d453eb4f49f0bb38cf828f94c5588ec05d1b5b2c`, in the recorded image/runtime. The project driver additionally records per-rank JUnit and imported-source provenance; these repository-only commands preserve the test assertions and numerical JSON output.

```bash
set -euo pipefail
git diff --exit-code d453eb4f49f0bb38cf828f94c5588ec05d1b5b2c -- hashinfer tests/moe_ep
export PYTHONPATH="$PWD" PYTHONFAULTHANDLER=1 PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1 TORCH_NCCL_ASYNC_ERROR_HANDLING=1 MEGA_USE_NCU=0
unset CUTE_DSL_COMPILER_OPT MEGA_NO_DIST
validation_out="$PWD/shared-raw-only-validation-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir "$validation_out"
case_index=0
run_case() {
  local ranks="$1" node="$2" case_dir
  case_dir="$validation_out/case$(printf '%02d' "$case_index")"
  case_index=$((case_index + 1))
  mkdir "$case_dir"
  export HASHINFER_NUMERICS_REPORT_DIR="$case_dir/numerics"
  export HASHINFER_MOE_EP_KNOB_CACHE="$case_dir/knobs.json"
  case "$ranks" in
    8) export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 ;;
    4) export CUDA_VISIBLE_DEVICES=0,1,2,3 ;;
    2) export CUDA_VISIBLE_DEVICES=0,1 ;;
    *) return 2 ;;
  esac
  timeout --signal=TERM --kill-after=30s 3h \
    python -m torch.distributed.run --nnodes=1 \
    --master-addr=127.0.0.1 --master-port=29791 \
    --nproc-per-node="$ranks" --max-restarts=0 \
    -m pytest -q -s -p no:cacheprovider --maxfail=1 "$node" \
    2>&1 | tee "$case_dir/run.log"
}
numeric=tests/moe_ep/test_w4a16_megamoe_numerics.py::test_w4a16_megamoe_numerics
tail=tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails
run_case 4 "${numeric}[topk_fc2-random-ep4-glm5-t1024]"
run_case 4 "${numeric}[topk_fc1-random-ep4-glm5-t1024]"
run_case 8 "${numeric}[topk_fc1-random-ep8-glm5-t128]"
run_case 2 "${tail}[w4a16-tail-epi_warps]"
run_case 2 "${tail}[w4a16-n64-wrap-epi_warps]"
run_case 2 "${tail}[w4a16-n128-wrap-reuse_dispatch_warps]"
```
