# Final442 focused numerical validation

**95 passed;0 failed,0 errors,0 skipped.** The24 fused W4A16 boundary cases were explicitly deselected. No optional57 wrapper/graph/EP cases were launched. These are existing tests against production442, with no source/test changes or experimental overlay.

Commit `442d2aa53f68b4640c3ab5118a76f1599ff60d34`; C1 `fi-w4a4-pipeline-1025`; image `nvcr.io/nvidia/pytorch:26.05-py3`; B200 GPUs4/5; CUDA13.2, PyTorch2.12.0a0+5aff3928d8.nv26.05, CuTe DSL4.7.1, pytest9.1.1. The numerical source/test hashes were unchanged before/after both runs and match archived source copies.

| Suite | GPU | Passed | Failures/errors/skips | Deselected | Pytest time | Warnings |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| Focused K-tail, deterministic finalize, SF layout, cluster padding |4|71|0/0/0|0|16.59s|366|
| Unfused W4A16 route-boundary matrix |5|24|0/0/0|24 fused cases|6.92s|400|

Warnings are CuTe DSL deprecations; complete warnings are retained in the application logs. These wall times describe test execution and are not kernel benchmark results.

The71 comprise60 exact NVFP4 K-tail cases,4 deterministic-finalize reference cases (NV per-tensor/per-token and W4A16),6 exact W4A16 SF row/K mapping cases, and1 W4A16 cluster-padding test with3 hidden-size invocations. The24 boundary cases cover six route capacities, two tail patterns, and top-k2/3 with fused finalize disabled. Existing reference tolerances remain unchanged; this is not an all-six-format independent-reference or bit-exact claim. The separate72 composed phase pairs and15 native exact configurations remain separate evidence.

Commands, selected environment, package versions, GPU UUIDs, source hashes, original stdout/stderr, and JUnit results are in `raw/`. The only tracked checkout differences are environment-setup symlinks for cccl/cutlass/spdlog. Their resolved Git HEADs exactly match all three442 gitlinks, recorded in `raw/logs/vendor-validation.json`. An initial blanket git-clean guard stopped before pytest/GPU launch because of those symlinks; it was narrowed to protected production/test paths after this verification. Nothing was reset or modified.

GPU4/5 were released after completion; each showed0 MiB and0% utilization. Sanitizer work is owned separately under `../sanitizer/` and is not included in this95-pass claim.

Archive: `144295` bytes, SHA256 `f5582d3968bb13a24b436d11dd90e2df0922b220432f1f1ab8b0ca1e68bd9f32`. `verification.json` independently checks source hashes, suite completion/counts and vendor gitlinks.

Planned selections and remaining boundaries: [validation plan](../../../scripts/final442-validation/README.md). The recovery README is copied locally as `recovery-README.local.md`; the actual remote environment script is in the raw archive.
