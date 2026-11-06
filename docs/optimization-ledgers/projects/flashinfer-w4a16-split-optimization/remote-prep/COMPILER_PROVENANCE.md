# Matched compiler stack

The container/runtime remains CUDA13.2 (system nvcc/ptxas13.2.78), with isolated CuTeDSL4.7.1. Saved native PTX reports NVVM CUDA13.3.27. CPU-only import/ELF inspection locates the effective compiler in `.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/_mlir/_mlir_libs/_cutlass_ir.cu13.cpython-312-x86_64-linux-gnu.so` (SHA256bb367e30bb24541faa974ed05ff201171f61c5b18b01df9e46a406bdde5edbba).

This extension embeds `nvPTXCompilerCreate`, `nvPTXCompilerGetCompiledProgram` diagnostics and `Cuda compilation tools, release 13.3, V13.3.27`, and its ELF NEEDED list has only standard system libraries. Together with the compiler provider path, this supports bundled NVVM/NVPTX compiler assembly rather than the external system ptxas for these CuTe kernels; no process-level assembler tracing was added. System cuobjdump/nvdisasm13.2 were used only to inspect saved cubins. Exact CPU inspection output is in compiler-provenance001.txt and002.txt.

The imported CUDA compatibility user library is `/usr/local/cuda-13.2/compat/lib.real/libcuda.so.595.58.03`; nvidia-smi reports kernel driver590.48.01. Baseline and candidate use the same unchanged resolved environment. CUPTI Python13.4.0/library13.4.58 is recorded separately from the CUDA13.2 runtime.
