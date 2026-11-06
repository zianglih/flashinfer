# Read-only capacity check

Checked 2026-10-28T03:20:56.832863+00:00. No devbox was requested and no GPU workload was launched. Managed `/usr/local/bin/h` identity was verified before calls.

- **C3 / infra / fi-moe-nvfp4-port-1026:** live, eight B300 SXM6 AC GPUs. All eight are occupied by this project's `retained-rerun/tools/observe_benchmark.py` native AUTO processes: GPU 0 PID 652659, 1 652652, 2 652656, 3 652653, 4 652658, 5 652655, 6 652654, 7 652657. Snapshot utilization was 23–99%, 34–92 GiB allocated; later command-line checks identify the expected eight model/family groups. None is available for concurrent probing.
- **C2:** successful all-namespace live inventory has 12 devboxes, none in ziangli/infra and none from this project. Historical `fi-v41-gap-c2-1025`, `fi-moe-general-c2-1026`, and `fi-moe-rebase-audit-1026` are absent.
- **C1:** both all-namespace and ziangli inventory requests report statefulset/pod timeouts, so live absence is not established. Stopped only these two local read-only inventory CLI processes after parent said no more retries. Project ledger records previous C1 boxes as B200, with the previous boxes removed; they are not a known alternative B300 resource.
- C3 also lists `fi-prefill-autotune` under ziangli, but it is not referenced in this project's ownership ledger. It was not accessed or considered reusable.

## Ready environment on the current box

Existing project receipts identify image `nvcr.io/nvidia/pytorch:26.05-py3`, Torch `2.12.0a0+5aff3928d8.nv26.05`, CUDA 13.2, and CuTe DSL 4.8. Live filesystem checks confirm the established Python remains at `/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python`, and `/usr/local/cuda/bin/cuobjdump --version` reports CUDA13.2 V13.2.78. Full-rerun and retained-rerun config files exist under the persistent project root. Current process paths confirm that exact Python environment is active.

Reuse the persistent native C++ cache with an isolated strict CuTe compilation cache for the finalizer probe. Do not alter the active campaign snapshot or flush caches. The established source-paired codegen helper needs only its independent source/scripts deployed and a released GPU; no package install or native-cache bootstrap is expected. A replacement box would add environment/cold-cache setup without providing a verified existing task-owned alternative. Waiting for the first completed retained-campaign GPU is the practical choice; release must be confirmed by the runtime owner.
