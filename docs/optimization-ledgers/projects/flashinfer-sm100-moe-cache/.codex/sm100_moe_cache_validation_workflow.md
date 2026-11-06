# SM100 MoE cache validation workflow

This note records the environment and commands used to validate the closed
FlashInfer PR #4424. Keep it with the local benchmark harness and raw results.

## Images

The PR #4424 measurements used this pinned FlashInfer CI image:

```text
flashinfer/flashinfer-ci-cu132:20260408-4cce866
```

The CUDA 13.2 PyTorch base used in earlier FlashInfer MoE work was NVIDIA's NGC
image:

```text
nvcr.io/nvidia/pytorch:26.05-py3
```

NVIDIA documents `26.05-py3` as Ubuntu 24.04, CUDA 13.2.1.009, and PyTorch
2.12.0a0+5aff3928d8. It is a better general-purpose base when a FlashInfer CI
snapshot is too old, but FlashInfer and the required CuTe DSL version must then
be installed explicitly. Release notes:
https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-05.html

Do not mix results from the two images without recording the final `torch`,
CUDA, CuTe DSL, and FlashInfer revisions.

## Devbox used for PR #4424

Run HAI commands from the central HAI checkout:

```bash
cd /Users/ziangli/rl/hai

uv run h devbox sm100-moe-cache-0809 \
  -c c1 -n infra -g b200 --gpus-per-pod 8 --size xlarge \
  --image flashinfer/flashinfer-ci-cu132:20260408-4cce866 \
  --bare --queue earth \
  --description 'Validate FlashInfer SM100 W4A4 and W4A16 CuTe DSL disk cache'
```

For a future run, use the normal namespace fallback order: request `-n ziangli`
first, retry with `-n infra` if quota is unavailable, and use `--queue hell`
only as the final fallback. Keep `--bare` and always pin the image tag or digest.

To reproduce with the NGC PyTorch base, replace only the image argument:

```bash
--image nvcr.io/nvidia/pytorch:26.05-py3
```

## Checkout and environment

The measured checkout was the pushed branch with its submodules initialized:

```bash
uv run h ssh sm100-moe-cache-0809 -c c1 -n infra -- bash -lc '
  git clone --depth 1 --single-branch \
    --branch agent/sm100-moe-cute-dsl-disk-cache \
    https://github.com/zianglih/flashinfer.git \
    /workspace/flashinfer-sm100-moe-cache-git
  cd /workspace/flashinfer-sm100-moe-cache-git
  git submodule update --init --depth 1 \
    3rdparty/cutlass 3rdparty/cccl 3rdparty/spdlog
  python -m pip install --upgrade "nvidia-cutlass-dsl[cu13]==4.6.0"
'
```

Copy the local-only harness into the checkout:

```bash
kubectl -n infra exec devbox-sm100-moe-cache-0809-0 -- \
  mkdir -p /workspace/flashinfer-sm100-moe-cache-git/.codex

kubectl -n infra cp \
  /Users/ziangli/playground/projects/flashinfer-sm100-moe-cache/.codex/sm100_moe_cache_benchmark.py \
  infra/devbox-sm100-moe-cache-0809-0:/workspace/flashinfer-sm100-moe-cache-git/.codex/sm100_moe_cache_benchmark.py
```

Before benchmarking, record the exact runtime:

```bash
uv run h ssh sm100-moe-cache-0809 -c c1 -n infra -- bash -lc '
  python - <<"PY"
import sys, torch, cutlass
print("python", sys.version)
print("torch", torch.__version__)
print("cuda", torch.version.cuda)
print("device", torch.cuda.get_device_name())
print("capability", torch.cuda.get_device_capability())
print("cutlass", getattr(cutlass, "__version__", "unknown"))
PY
'
```

## Benchmark

The harness isolates FlashInfer's workspace cache, prewarms unrelated JIT work,
and runs cache-disabled, cold-cache, and warm-cache arms in fresh Python
processes. Each arm is repeated twice.

```bash
uv run h ssh sm100-moe-cache-0809 -c c1 -n infra -- bash -lc '
  cd /workspace/flashinfer-sm100-moe-cache-git
  CUDA_VISIBLE_DEVICES=0 PYTHONPATH=$PWD \
    python .codex/sm100_moe_cache_benchmark.py \
      --mode all \
      --phase worker \
      --cache-dir .codex/sm100_moe_cache_smoke \
      --repeats 2 \
    2>&1 | tee .codex/sm100_moe_cache_benchmark_final.txt
  test ${PIPESTATUS[0]} -eq 0
'
```

Preserved artifacts:

- `sm100_moe_cache_benchmark.py`: benchmark harness.
- `sm100_moe_cache_benchmark_final.txt`: complete output and JSON results.
- `pr-body.md`: summarized environment, validation, and timings.

## Cleanup

After copying results back to the local project workspace:

```bash
cd /Users/ziangli/rl/hai
uv run h delete sm100-moe-cache-0809 -c c1 -n infra --force
```
