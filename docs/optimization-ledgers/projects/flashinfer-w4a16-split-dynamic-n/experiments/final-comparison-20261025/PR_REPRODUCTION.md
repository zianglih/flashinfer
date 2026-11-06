<details>
<summary>Environment setup and native reproduction commands</summary>

Run inside `nvcr.io/nvidia/pytorch:26.05-py3` on B300. Keep both source checkouts independent and use one pinned Python environment. These commands use only repository entry points; the measurement observers only save provenance, AUTO caches and completed timing vectors outside native timing.

```bash
set -euo pipefail
project=/workspace/w4a16-pr7196
mkdir -p "$project"
cd "$project"
git clone --filter=blob:none https://github.com/flashinfer-ai/flashinfer.git before
git clone --filter=blob:none https://github.com/flashinfer-ai/flashinfer.git after
git -C before checkout --detach 316faec37a4706a2ecc7d46265087f8190b40baa
git -C after fetch origin pull/7196/head
git -C after checkout --detach 97e8d0c8bb86b352ccb42f2654ddc2ab9a8e6939
before="$project/before"
after="$project/after"
for repo in "$before" "$after"; do
  git -C "$repo" submodule update --init --recursive \
    3rdparty/cutlass 3rdparty/cccl 3rdparty/spdlog
done
python -m venv --system-site-packages "$project/.venv"
source "$project/.venv/bin/activate"
python - <<'PY'
import importlib.metadata as metadata
from pathlib import Path
import sys
Path(sys.prefix, "constraints.txt").write_text(
    "torch==" + metadata.version("torch") + "\n"
)
PY
export PIP_CONSTRAINT="$VIRTUAL_ENV/constraints.txt" BUILD_NVEP=0
export MAX_JOBS=32 FLASHINFER_NVCC_THREADS=1
python -m pip install --no-build-isolation -e "${after}[cu13]" \
  'nvidia-cutlass-dsl[cu13]==4.7.1' 'apache-tvm-ffi==0.1.15.post0' \
  'cupti-python==13.4.0' 'nvidia-cuda-cupti==13.4.58' \
  'nvidia-cuda-nvcc==13.3.73' 'nvidia-nvvm==13.3.73' 'pytest==9.1.1'
python -m pip install --no-build-isolation --no-deps -e "$before"
python -m pip install --no-build-isolation --no-deps -e "$after"
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
export FLASHINFER_WORKSPACE_BASE=/root
export TORCH_EXTENSIONS_DIR="$project/torch-extensions"
unset FLASHINFER_AUTOTUNE_TIMER
tokens=1,2,4,8,16,32,64,128,256,512,4096,8192,16384
```

**H7168 full-PR before/after:** each command starts a fresh process, in ABBA order. `--profile-backend` selects the measured backend; `--profile-cuda` is absent. CUDA graphs, CUPTI, normal AUTO and the wrapper API are enabled by default.

```bash
export CUDA_VISIBLE_DEVICES=0
for repo in "$before" "$after" "$after" "$before"; do
  (
    cd "$repo"
    PYTHONPATH="$repo" python benchmarks/bench_moe_deepseek.py \
      --num-tokens "$tokens" --ep 8 --tp 1 --warmup 10 --iters 100 \
      --routing-input-mode logits --backends cutedsl \
      --profile-backend cute-dsl-w4a16 --no-fused-finalize
  )
done
```

**Kimi K3 distributed before/after:** use the same eight GPUs for all four fresh process groups, again in ABBA order. Select the measured NCCL runtime explicitly; PyTorch's compiled NCCL version is separate from the loaded library.

```bash
python -m pip install --no-deps --target "$project/ep-nccl-2.30.7" \
  'nvidia-nccl-cu13==2.30.7'
export LD_LIBRARY_PATH="$project/ep-nccl-2.30.7/nvidia/nccl/lib:${LD_LIBRARY_PATH:-}"
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
for repo in "$before" "$after" "$after" "$before"; do
  (
    cd "$repo"
    PYTHONPATH="$repo" python -m torch.distributed.run \
      --nnodes=1 --nproc-per-node=8 \
      --master-addr=127.0.0.1 --master-port=29538 \
      benchmarks/bench_cute_dsl_moe_distributed.py \
      --model kimi-k3 --num-gpus 8 --parallel-modes ep --variants w4a16 \
      --timing cupti --cuda-graph --no-fused-finalize --precomputed-routing \
      --warmup 10 --iters 100 --log-timing-samples --verbose \
      --num-tokens "$tokens"
  )
done
```

**H7168 backend comparison:** use current head and one GPU for all six fresh processes, in CuTe → TRTLLM input quant excluded → TRTLLM input quant included → included → excluded → CuTe order. Omitting `--use-per-token-activation` selects per-tensor global activation scaling; NVFP4 block scales remain present. `--no-fused-finalize` selects unfused CuTe finalize and does not change native TRTLLM finalize.

```bash
export CUDA_VISIBLE_DEVICES=0
unset TORCH_EXTENSIONS_DIR
cd "$after"
export PYTHONPATH="$after"
for arm in cute excluded included included excluded cute; do
  if [[ "$arm" == cute ]]; then
    backend_args=(--backends cutedsl --profile-backend cute-dsl-w4a16)
  elif [[ "$arm" == excluded ]]; then
    backend_args=(--backends trtllm-nvfp4 --profile-backend trtllm-nvfp4)
  elif [[ "$arm" == included ]]; then
    backend_args=(--backends trtllm-nvfp4 --profile-backend trtllm-nvfp4 \
      --include-activation-quant)
  else
    exit 2
  fi
  python benchmarks/bench_moe_deepseek.py \
    --num-tokens "$tokens" --ep 8 --tp 1 --warmup 10 --iters 100 \
    --routing-input-mode logits --no-fused-finalize "${backend_args[@]}"
done
```

Run campaigns serially, finish native JIT setup before timing, and keep all compilation, tuning, input preparation and graph capture outside the measured sample interval. Do not pass `--cache` or `--no-autotune` for these normal-AUTO comparisons.

</details>
