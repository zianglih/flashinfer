# Capacity recovery image selection

Live checked 2026-10-28 before requesting a replacement C3 devbox.

- Managed CLI: `/usr/local/bin/h`, verified with `command -v h`.
- [NGC catalog](https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/pytorch/-) latest overall: `26.09-py3`.
- [NVIDIA 26.09 release version table](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-09.html): 26.09/26.08 use CUDA 13.4.1; 26.07 uses 13.3.1; 26.06 uses 13.3.0; 26.05 uses 13.2.1.009.
- Selected newest CUDA 13.2 tag: `nvcr.io/nvidia/pytorch:26.05-py3`, matching original measurements.
- Requested C3 B300, 8 GPUs, bare, size unspecified. First request namespace ziangli.
- CLI requires a HAI checkout even for bare; command executed from shared checkout without editing it.
