# F4 versus F8 runtime setup

Each EP has an isolated C2 B300 8-GPU devbox running `nvcr.io/nvidia/pytorch:26.05-py3`. The live NGC release matrix was checked before the requests; 26.05 is the newest CUDA 13.2 release. The actual pod image IDs, nodes, boot IDs and GPU UUIDs are recorded in `ep4-runtime` and `ep8-runtime`.

- EP4: `fi-mega-f4f8-ep4-0924`, namespace `ziangli`, root `/workspace/fi-mega-f4f8-ep4-0924`.
- EP8: `fi-mega-f4f8-ep8-0924`, namespace `infra`, root `/workspace/fi-mega-f4f8-ep8-0924`.
- Requests used the managed `/usr/local/bin/h`, `--bare`, `-g b300`, `--gpus-per-pod 8`, and no size override. The first EP8 request to `ziangli` could not fit its namespace quota; its queued resources were deleted before the `infra` retry.
- Python: `$task_root/.venv/bin/python`; FlashInfer source: `$task_root/flashinfer`.
- Pinned dependencies are in each `runtime-setup/requirements-gpu.txt`; the venv uses the container PyTorch unchanged. CuTe DSL 4.7.1 includes a CUDA 13.3 native compiler even though PyTorch/NVCC use CUDA 13.2; this matches the preceding benchmark campaign.
- Source installation preserves and checks every incoming archived file. The three Git submodule pins were verified against clean source HEAD `19e8aebb541684df09e12cc79610338aa429a2cf`.
- Source environment: `PYTHONDONTWRITEBYTECODE=1`, `FLASHINFER_CUBIN_DIR=$task_root/cache/flashinfer-cubins`, `FLASHINFER_WORKSPACE_BASE=$task_root/cache/flashinfer`.
- Qualification consists of native source import, benchmark CLI help, and native CUPTI capture of one small Torch add. It does not execute any MegaMoE benchmark or numerical test.

`results/source-ready.json` is the readiness receipt. `environment.json` records dependency paths and versions; `node-before.json` records the unmodified container Torch and GPU inventory; `source-install-integrity.json` records source preservation. `pod-receipt.json` separately records the image ID returned by Kubernetes rather than assuming a digest from a previous run.
