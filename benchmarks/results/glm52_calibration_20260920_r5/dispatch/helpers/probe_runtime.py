"""Record this experiment's package/compiler identity without environment discovery."""

import importlib.metadata as md
import json
import pathlib
import subprocess

import torch


packages = (
    "sglang", "sglang-kernel", "flashinfer-python", "flashinfer-cubin",
    "flashinfer-jit-cache", "torch", "triton", "transformers", "setuptools",
    "packaging", "apache-tvm-ffi", "ninja", "nvidia-cutlass-dsl",
    "nvidia-cutlass-dsl-libs-base", "nvidia-cutlass-dsl-libs-core",
    "nvidia-cutlass-dsl-libs-cu12", "nvidia-cutlass-dsl-libs-cu13", "nvshmem4py-cu13", "nvidia-nvshmem-cu13",
    "cuda-python", "cuda-bindings", "cuda-core", "nccl-extensions", "nccl4py",
    "cuda-tile", "nvidia-cudnn-frontend", "nvidia-nccl-cu13", "cupti-python", "nvidia-cuda-cupti",
)
versions = {}
for name in packages:
    try:
        versions[name] = md.version(name)
    except md.PackageNotFoundError:
        versions[name] = None
print(json.dumps({
    "versions": versions,
    "torch_import": str(pathlib.Path(torch.__file__).resolve()),
    "torch_cuda": torch.version.cuda,
    "nccl": torch.cuda.nccl.version(),
    "nvcc": subprocess.check_output(["nvcc", "--version"], text=True),
    "gpu": subprocess.check_output([
        "nvidia-smi", "--query-gpu=name,uuid,driver_version,memory.total", "--format=csv"
    ], text=True),
}, indent=2))
