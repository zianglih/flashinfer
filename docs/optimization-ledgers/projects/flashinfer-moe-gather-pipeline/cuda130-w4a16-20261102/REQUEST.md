# CUDA 13.0 W4A16 before/after

The user requested a fresh C3 comparison of the existing CuTe DSL W4A16
before/after workloads and asked that results be inserted into PR #7290 directly
after its existing GLM5 MegaMoE regression check. The naming refactor was
cancelled; production remains clean at a620ce77. Optimization remains paused.

- Before: pre-PR 002529e1, original 64-row weight layout, using the archived
  benchmark compatibility adapter and original recorded native tactics.
- After: retained a620ce77, new 16-row swap-AB weight layout, current public
  benchmark and recorded tactics. No new kernel changes or retuning.
- V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, N3U EP8/TP8; each uses tokens
  1,2,4,8,16,32,64,128,256,512,4096,8192,16384. 104 paired cases.
- Both arms freshly measured on the same C3 runtime/GPU assignment in
  C1/A1/A2/C2 order, 10 warmups and 100 strict CUPTI cold-L2 CUDA-graph samples
  per phase. Tokens 1/2 remain raw but are excluded from aggregate retention.
- Compare exact route identities within the fresh pair. Historical route hashes
  are diagnostic because the container's PyTorch version differs from 13.2 runs.
- Separate persistent source caches; no CUDA 13.2 native ELF reuse. Record
  system toolkit and bundled CuTe compiler versions separately.

NGC catalog and NVIDIA's PyTorch release matrix were checked on 2026-11-02.
Selected `nvcr.io/nvidia/pytorch:25.11-py3`: latest listed CUDA 13.0 image
(13.0.2.006); 25.12 and 26.01 move to 13.1. The explicit user request overrides
the normal standalone CUDA 13.2 image default.

- https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch/tags
- https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-25-11.html
- https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-25-12.html

Owned runtime: `fi-w4a16-cu130-1102`, C3/ziangli, bare 8×B300, no size override.
Managed CLI `/usr/local/bin/h` was verified before use. The unused CUDA 13.2
naming-test devbox was deleted after cancellation; no naming tests were run.
