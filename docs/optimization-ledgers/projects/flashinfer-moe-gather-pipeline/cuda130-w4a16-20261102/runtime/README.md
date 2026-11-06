# CUDA 13.0 C3 runtime receipt

- Devbox: `fi-w4a16-cu130-1102`, cluster `c3`, namespace `ziangli`, host `hu-wtc-5`.
- Container: `nvcr.io/nvidia/pytorch:25.11-py3`; eight B300 SXM6 AC GPUs; driver `595.91.07`.
- Persistent owned root: `/data/ziangli/flashinfer-moe-gather-pipeline/cuda130-w4a16-20261102` (`c3-data`, WekaFS).
- Isolated Python: `<root>/venv/bin/python`, created with container system-site-packages. Native Torch `2.10.0a0+b558c986e8.nv25.11`, `torch.version.cuda == 13.0` preserved; no Torch upgrade or CUDA 13.2 toolkit install.
- System NVCC/PTXAS: `13.0.88`. Runtime libcudart: `13.0.96`.
- CuTe DSL: `4.8.0`, including libs-base/core/cu12/cu13. It embeds NVVM `CUDA 13.4.59` in `_cutlass_ir.cu13.so`. Therefore these are CUDA 13.0 container/runtime/C++ compilation measurements, not an assertion that CuTe's embedded compiler is CUDA 13.0. Actual generated PTX header is to be retained with source smoke evidence.
- CUPTI Python `13.0.1`, CUPTI package `13.0.85`; the loaded container `libcupti.so.2025.3.1` is SHA-identical to the pinned wheel library. CUPTI timestamp call succeeded.
- Exact additional dependencies are in `pins.txt`; install log `pip.log`. `runtime.json` records package versions, GPU UUIDs, loaded library SHA256s, and compiler release strings. `system-before.json` and `install.json` verify native Torch and NVCC remained unchanged.
- Local receipts were copied from remote and SHA256 verified; hashes are in `sha256.json`. Bootstrap and inspection scripts are retained in local task root and remote `<root>/runtime`.

No model benchmark, performance result, or sanitizer was run by runtime bootstrap. Only imports, metadata, and CUPTI timestamp were checked. Runtime inspection has finished; no GPU process remains from this bootstrap.

For compiler artifacts in the separate untimed smoke, CuTe 4.8 supports `CUTE_DSL_KEEP=ptx,cubin` and `CUTE_DSL_DUMP_DIR=<owned smoke directory>`; both artifact flags have `affects_compile=False`. Use normal defaults for measured runs. Keep per-source C++ compilation caches under this persistent CUDA 13.0 root; never reuse CUDA 13.2 ELF artifacts.
