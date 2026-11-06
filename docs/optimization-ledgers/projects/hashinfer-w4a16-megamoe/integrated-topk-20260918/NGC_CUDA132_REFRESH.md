# CUDA 13.2 image check for profiling-node recovery

Checked live on 2026-09-18 (America/Los_Angeles), before any replacement request.

- Selected explicit image: `nvcr.io/nvidia/pytorch:26.05-py3`.
- CUDA toolkit: 13.2.1.009; PyTorch: `2.12.0a0+5aff3928d8`.
- NGC linux/amd64 manifest digest:
  `sha256:ca73b4795f0d3ae27e9cd81b1b1f1b7fc6c0a129f7d51a359d2326e95af48a3d`.
- The live tag list includes 26.06, 26.07 and 26.08, but the official release
  matrix assigns them CUDA 13.3.0, 13.3.1 and 13.4.1 respectively. Therefore
  26.05 remains the newest listed release satisfying the CUDA 13.2 requirement.

Sources: [NGC tag list](https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/pytorch/-/tags),
[26.08 release matrix](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-08.html),
[26.05 release notes](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-05.html).

This is an image-selection record, not evidence that a replacement devbox exists
or that interrupted profiling completed. New-node performance must use a fresh
paired baseline and candidate, rather than combining measurements across nodes.
