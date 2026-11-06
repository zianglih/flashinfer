# Unused fallback: EP1 runtime reinitialization without Mega

Preparation only. Retry job1 passed, so leave this command unused unless the
same host-init failure recurs and root schedules the diagnostic. Run only on
the admitted source/environment in a fresh standalone process. This repeats
the existing public layer's bootstrap/finalize API boundary nine times (the
nine layers in the original EP1 job), without creating a layer/workspace,
calling CuTe compile or launching Mega. Torch device setup and the original
Gloo/NVSHMEM UID bootstrap still execute; this is not a no-GPU-activity test.

The standalone EP1 tests lack RANK/WORLD_SIZE. The existing bootstrap therefore
creates a one-rank Gloo group at tcp://127.0.0.1:29500 and finalization destroys
that owned group. Do not replace this with torchrun or a custom NVSHMEM init.
Preserve the admitted library environment, including any existing
MEGA_SINGLE_GPU_GLOO setting. The required API set is the unchanged CuTe runtime
requirements: TORCH_DIST and NVSHMEM.

```bash
cd /workspace/flashinfer-w4a16-megamoe/flashinfer
env -u RANK -u WORLD_SIZE -u LOCAL_RANK \
  CUDA_VISIBLE_DEVICES=0 MEGA_NO_DIST=0 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 \
  timeout --kill-after=10s 180s /usr/bin/python3 -u - <<'PY'
import torch
import torch.distributed as dist
from flashinfer.moe_ep import BootstrapConfig, ensure_moe_ep_cuda_device
from flashinfer.moe_ep.core.runtime import (
    NVSHMEM,
    TORCH_DIST,
    bootstrap_moe_ep_runtime,
    finalize_moe_ep_runtime,
)

for cycle in range(1, 10):
    bootstrap = BootstrapConfig(world_size=1, rank=0)
    ensure_moe_ep_cuda_device(bootstrap)
    print(f"cycle={cycle} before runtime init", flush=True)
    handle = bootstrap_moe_ep_runtime(
        bootstrap, frozenset({TORCH_DIST, NVSHMEM})
    )
    try:
        print(f"cycle={cycle} after runtime init", flush=True)
    finally:
        print(f"cycle={cycle} before runtime finalize", flush=True)
        finalize_moe_ep_runtime(handle)
        print(f"cycle={cycle} after runtime finalize", flush=True)
    # Same post-destroy barrier shape used by the existing public tests.
    torch.cuda.synchronize()
    if dist.is_initialized():
        dist.barrier()
print("completed nine runtime-only init/finalize cycles", flush=True)
PY
```

A recurrence here would establish host reinitialization failure without prior
Mega activity in that process. A pass would not exonerate the library or prove
that earlier kernel activity caused the original failure. Do not change the
kernel/observer, relax a numerical oracle, or infer a successful raw7 suite
from this diagnostic. No execution has been performed.
