# Paired-error runtime recovery

Replacement: `fi-gather-pipeline-resume-1030`, C2/ziangli, `nvcr.io/nvidia/pytorch:26.05-py3`, bare, eight B300 GPUs. Root allocated it; this bootstrap performs no experiment timing or tuning.

Live source check (2026-10-30T22:45:59.592334+00:00): the root agent's [NGC catalog overview](https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/pytorch/-) lists 26.10 as latest; the tags view returned 26.09 to the bootstrap check. [26.05 release notes](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-05.html) specify CUDA 13.2.1.009; [26.06](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-06.html) moves to CUDA 13.3.0 and [26.09](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-09.html) to 13.4.1. The 26.10 notes URL was unavailable in this check. This preserves the existing CUDA 13.2 image/runtime cohort; it is not a claim that 26.05 is the newest overall image.

Reused `runtime/recovery-1030` install/runtime/warm scripts with only the new host/output leaf and expected current-c1ac source/current native fingerprints. `pins.txt` is byte-identical. Torch/torchvision versions were unchanged by installation. No direct transitive CuTe wheel naming or package metadata edits. All old runtime receipts remain unchanged.

Persistent C++ workspace: `/data/ziangli/flashinfer-w4a4-split-dynamic-n/upstream-integration-20261029/megamoe-glm5/cache/cpp`. The pending pilot will use distinct per-arm quantizer `cached_ops` roots and share only the four release native module directories; deployment must consume this recovery's fresh `runtime.json` and `cache-ready.json`, not historical SF-lane receipts.

Sequence: `install.py`, `assess_persistence.py` and `assess_runtime.py`, then normal release `warm.py` if dependencies require it. Explicit JIT_VERBOSE=0 and JIT_DEBUG=0; no clean/touch/forced rebuild. New runtime/cache readiness is not inferred from old receipts.
