# C3 review validation

Passed **28/28**, zero failures, errors, or skips. Source edits remain local and unstaged; no commits, pushes, or public replies.

- Devbox: `fi-pr7290-small-w4-1103`, C3 / `ziangli`, NVIDIA B300 (SM103).
- Image: `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.
- Base: `14a338579eb8acddcc5cfd1cc58871fc0788de22` plus the exact six-file review snapshot.
- Review archive SHA256: `2065fb4eb2b1692fc2676717874e6ed86b189802829829afd37b71b06a16633f`.
- Remote tested bytes and current local unstaged bytes both match `payload/review-files-manifest.json`.
- All test jobs had exited; final NVML status listed no compute processes. GPUs were released to the benchmark owner.

| Job | Passed | Pytest elapsed (s) |
|---|---:|---:|
| autotune-legacy-w4a16 | 1 | 61.750 |
| autotune-legacy-w4a4 | 1 | 26.090 |
| autotune-swap-w4a16 | 1 | 57.540 |
| autotune-swap-w4a4 | 1 | 154.780 |
| review-layout-accuracy | 20 | 38.572 |
| review-mx-gated | 1 | 19.245 |
| review-prepare-completion | 3 | 12.380 |

Coverage: 13 CPU layout/helper/guard cases; 8 NVFP4 typed activation cases spanning swap and legacy layouts; 3 real prepared-view cases (legacy64 MXFP4, swap16 MXFP4 and MXFP8); 4 actual autotune-plus-replay cases (legacy/swap × W4A4/W4A16).

The original launcher omitted the existing non-gated row-mismatch guard. The completion job ran that selector plus the existing legacy real-helper case requested by root and the existing MXFP8 swap case. No assertions or source files were changed during validation.

All raw pytest logs, JUnit XML, and launch receipts are under `evidence/tests/`. Final fetch receipt: `evidence/fetch-1793734445.json`. Every fetched file hash and the compressed transport hash were verified.

This is targeted correctness and autotune validation, not a benchmark conclusion or full-suite claim.
