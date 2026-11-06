# Native validation of coalesced16

Candidate `21f598d8db88df87302e96e233599eab2f6db048` passed the requested bounded native validation on hu-pdx-59, boot `dc868539-2ac3-4565-a1d9-3580f5164d0c`. The exact 104-file source manifest is `1e40a5e3f306928f4e6f39b153cebb71f76fdbfb72e6c32456e35c5cf664dadb`. No implementation or test changes were made.

| Existing test scope | Result | Wall time including process startup |
|---|---:|---:|
| Graph/eager equality, H1600/I832 and H2048/I1024, contiguous/transposed/offset/strided input | 8 passed, no skips | 203.36 s |
| H2880 tail reference, epilogue and dispatch-warp return | 2 passed, no skips | 22.00 s |
| GLM5 H6144/I2048/E256/K8, T128/random/EP8, all four tactics × O2/O3 × eager/graph | 1 global case passed on all 8 ranks | 164.18 s |

Total 390.36 s. The GLM5 case checked 16 tactic/compiler/execution combinations, 48 reference comparisons, and 120 pair comparisons: 132,120,576 BF16 element comparisons with zero bit mismatches or nonfinite values. The two existing tail tests retain their existing Torch-oracle criterion; they are not described as bit-exact tests.

Environment: `nvcr.io/nvidia/pytorch:26.05-py3`, eight B300 GPUs, CUDA 13.2, driver 590.48.01, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CuTe DSL 4.7.1, explicit `MEGA_USE_NCU=0`, fresh compilation caches. Exact commands and environment are archived in `collected/evidence/finished.json`.

The archive `collected/evidence.tar.gz` has SHA256 `2f221e2426c5b621f909ead12730173f23377dd1c3baa6b11ac2e14aeb7a3aa3` (371,542 bytes, 135 hash-verified regular-file members). `collected/verification.json` verifies all case names, no skips, all numerical counters, source hashes, same host/boot, and empty owned process groups/GPU process list at collection. The node is idle.

This is a bounded native correctness check, not a full numerical matrix or sanitizer scan. No new timing, sanitizer, full60 suite, PR9 work, publication, or promotion occurred here.
