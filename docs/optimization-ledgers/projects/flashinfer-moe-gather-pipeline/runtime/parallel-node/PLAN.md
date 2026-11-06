# Parallel C2 node runtime preparation

No node action is authorized until the parent confirms the exact pod and namespace. Do not change the active GLM5 node.

Target image: `nvcr.io/nvidia/pytorch:26.05-py3` (parent requested). Mirror the existing frozen runtime:

- `nvidia-cutlass-dsl[cu13]==4.8.0` (install CU13 as an extra/dependency, matching original pip provenance)
- `apache-tvm-ffi==0.1.14.post1`
- `cupti-python==13.2.0`, `nvidia-cuda-cupti==13.2.86`
- `cuda-python==13.2.0`, `cuda-bindings==13.2.0`, `cuda-core==1.2.1`
- `pytest==8.4.2`
- `nvshmem4py-cu13==0.3.1`, `nvidia-nvshmem-cu13==3.6.5`

Preserve image PyTorch `2.12.0a0+5aff3928d8.nv26.5.50603568` (distribution metadata; runtime torch.__version__ is `.nv26.05`). Capture the initial versions and complete pip environment before installation. Run pip dry-run/report first with a generated exact torch constraint; reject any plan that installs/replaces torch, torchvision or torchaudio. Pin the packages listed above, preserve the image torch installation, then verify distribution versions and imports. Dependency additions must be recorded in the pip report.

Preserve shared C++ cache path exactly:
`/data/ziangli/flashinfer-w4a4-split-dynamic-n/upstream-integration-20261029/megamoe-glm5/cache/cpp`.

Do not rewrite existing build.ninja, source links, source snapshots, native winner caches or C++ cache files. Inspect persistent source/data symlink targets and dry-run existing Ninja entries; compilation remains controlled by the parent campaign. Use separate node-specific CUPTI run/output directories and driver/CuTe cache namespaces as directed by the parent.

Read-only qualification after setup: record hostname/node/device UUIDs and driver, nvcc version, exact package versions, CuTe/TVM/CUPTI/NVSHMEM imports, and cupti.get_timestamp(). Do not launch kernels/benchmarks until the parent allocates GPUs. Keep all setup logs and receipts in this project folder, and return exact remote paths to the parent.

Pins are sourced from `validation/glm5-r2-attempt2/evidence/runtime.json` and `runtime/qualify-control-r2.log`; pytest/cuda-core are also explicitly confirmed in the parent assignment.

The first qualification correctly rejected a different compiler fingerprint: explicitly requesting libs-cu13 adds an empty pip REQUESTED marker and RECORD row. All four CU13 ELF payloads were identical. The dependency was reinstalled through the original `[cu13]` extra; no metadata or cache record was edited by hand. Failed attempt1 and both pip reports are preserved.
