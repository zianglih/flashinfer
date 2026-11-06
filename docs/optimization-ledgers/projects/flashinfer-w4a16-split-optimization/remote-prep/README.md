# Remote preparation

Observed 2026-09-13. Managed CLI is `/usr/local/bin/h`, invoked from the user-approved existing `/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/hai` checkout.

The former `fi-w4a16-mega-0911c` devbox is gone: it was absent from c2/ziangli listing and the exact SSH lookup returned not found without executing the remote marker. Its historical toolchain/idle state was not treated as current. The unrelated SGL devbox was untouched.

The dedicated `fi-w4a16-split-0913a` was first requested in ziangli, where namespace GPU quota was occupied. Only that new pending request was cancelled/deleted. The authorized infra fallback succeeded on `hu-pdx-43`, default earth queue, eight B300 GPUs, `--bare`, no `--size` argument. Managed CLI auto-update reported a GitHub404; the installed CLI completed the operations normally.

Image selection was checked live against the [NGC PyTorch catalog](https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/pytorch/-) and [NVIDIA26.08 release table](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-08.html): latest26.08 uses CUDA13.4.1;26.07/26.06 use13.3; the newest CUDA13.2 release remains explicit `nvcr.io/nvidia/pytorch:26.05-py3`.

| Item | Actual observation |
|---|---|
| Host | hu-pdx-43 |
| GPUs | 8× NVIDIA B300 SXM6 AC,275040MiB each |
| Initial occupancy | All0MiB/0%; no compute processes |
| Driver | 590.48.01 |
| Container CUDA | 13.2.1.009 |
| nvcc/ptxas | 13.2.78 |
| Python | 3.12.3 |
| PyTorch runtime | 2.12.0a0+5aff3928d8.nv26.05, CUDA13.2 |
| PyTorch distribution | 2.12.0a0+5aff3928d8.nv26.5.50603568 |
| Nsight Systems | 2026.2.1.210 |
| Nsight Compute | 2026.1.1.0 |
| Base CuTe DSL | 4.4.2 |
| Base CUPTI library | libcupti.so.2026.1.1; no cupti-python |
| Writable workspace | 5.6TiB free when inspected |

Independent source checkout: `/workspace/flashinfer-w4a16-split-optimization/flashinfer`, detached exact upstream `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`, clean tracked files. CUTLASS/CCCL/spdlog submodules initialized at source pins. NIXL left uninitialized because this single-GPU simulated-EP split benchmark does not use EP transport.

Project venv: `/workspace/flashinfer-w4a16-split-optimization/.venv`, `--system-site-packages`. Project-local editable source install with `BUILD_NVEP=0`; no global editable install or global package replacement. A constraint preserves the preinstalled Torch distribution. Effective project additions include CuTe DSL[cu13]4.7.1, CUPTI Python13.4.0 plus nvidia-cuda-cupti13.4.58, TVM-FFI0.1.13.post3. Existing cuda-python/cuda-bindings13.2.0 remain. Source/torch/cutlass/cupti import check passed with no visible GPU. Exact resolved package list and installation output are retained; system-image and project-package CUDA versions remain distinct.

Validation now includes the complete upstream488ff baseline and exact top-k candidate (source.patch8ad313cb; candidate files match local commit968380de), using driver3d0cc984. Each normal run uses one visible GPU, simulated EP8, fused finalize, all14 sizes1–8192,10 warmups and100 upstream cold-L2 CUPTI iterations, with fresh normal autotuning and per-row saved tactic caches. Saved JSON contains the upstream median, not the100 raw samples. No old Mega source, environment or benchmark was used.

Completed artifacts: baseline full14 (baseline001,530.82s including first-use common JIT); candidate38 selected tests PASS (36.82s); candidate full14 (candidate-benchmark001,48.84s); baseline and candidate three-case compile-only PTX/cubin/SASS captures; cachedT128 Nsight Systems for both sources; baseline full FC2 Nsight Compute (40 application passes,620.88s). The first native export failed before creating its dump directory; that failure is preserved and corrected captures use precreated directories, KEEP=ptx,cubin and standalone disassembly. Initial test collection lacked pytest; no tests ran in that attempt, and isolated pytest9.1.1 was then installed.

The complete repeat A/B pair passed (baseline44.075s, candidate48.810s), followed by candidate full FC2 NCU using kernel replay:40passes in22.887s. The first candidate NCU invocation rejected an application-only CLI flag before launching the target; its exit1 is preserved. The corrected invocation omitted that flag and passed. Both repeats and the final profile have source/idle closure records; remote remains exact candidate source after all authorized work. The first pair remains immutable. Full profile timing is diagnostic only; normal complete sweeps determine performance. Baseline full NCU omits six unavailable CTC metrics and could not import source from the normal unannotated compile; separate lineinfo native captures provide source attribution. No baseline profile repeat was requested.

See [COMPILER_PROVENANCE.md](COMPILER_PROVENANCE.md) for actual DSL bundled13.3 compiler evidence distinct from system CUDA13.2 and the compatibility driver library. Source hashes, argv, true remote exit markers, source-before/after checks and idle-process snapshots are retained in the corresponding execution/fetch logs.

Evidence: `initial-status001.json`, request logs/receipts, `environment001.json`, `checkout001.log`, and `packages001.log`. CLI return0 alone was never treated as remote execution success; separate remote begin/exit markers were required.
