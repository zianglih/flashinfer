# Focused rebase validation

Source: `1496b557f9b606f3a0bb36bcebf5293d3e11555a`, rebased on `002529e17b22567a071091053c6c4dc2a55e050e` after merged #7196/#7501. The initial staging commit 4172 has identical runtime/header/test files; only upstream GDN benchmark files differ. The final checkout and each selected source hash are checked before and after execution.

Environment: existing C3 `fi-moe-nvfp4-port-1026`, NVIDIA B300, CUDA 13.2, PyTorch 2.12.0a0+5aff3928d8.nv26.05, CuTe DSL 4.7.1. Managed `/usr/local/bin/h` only. Three independent workers use GPUs 0–2. No performance measurement, AUTO search, broad parameter matrix, or sanitizer campaign.

The new persistent workspace does not reuse previous native objects. Package data links `include` and `csrc` into the new checkout so #7501's headers are used. Only third-party source trees are shared, after exact gitlink checks. No `flashinfer-jit-cache` or `flashinfer-cubin` package is installed. Previous persistent caches and source snapshots remain unchanged.

Existing selected tests:
- 39 W4A16 cases: the complete 32-case exact W4A16 class; two gated/nongated functional cases; GeGLU; both SiTU configurations; cluster/tail finalize; one graph wrapper case. All W4A16 results use the merged shared bit-exact oracle.
- 16 unfused split cases: two deterministic NVFP4 cases; per-tensor/per-token padded finalize; all 12 public MXFP8/MXFP4x8 API cases across one/two CTA and SwiGLU/SiTU.
- 49 quantizer cases: 20 MXFP4 payload/scale/decode cases; 6 layout/backend parity cases; 8 MXFP8 cases; one grouped boundary case; six trace references; eight NVFP4 strict/fast cases including scale underflow.

The task-local selection plugin filters existing pytest items by their parameter values and fails before execution if a count differs. `selection.json` is the authoritative list of exact node IDs and parameters for each group. The first quantizer collection selected 23 cases because the repository spells its FP4 device `cuda:0`; it ran zero tests. That attempt remains in `quant-collection-v1`; the corrected helper accepts `cuda` and `cuda:0` and selects 49. No production or test-source edits were made.

`deployment.json`, `source.json`, launch receipts, selected-case manifests, pytest logs/JUnit, native-cache audit, and final GPU inventory provide the source/environment/command/results trail. The staging directory is named 4172 but its final checkout and all execution receipts are 1496; no result is attributed to the prior head.

Rubin hardware is unavailable. Any explicit legacy64-row layout check on B300 validates the shared code's layout branch only, not Rubin hardware support.

## Completed

All 104 existing selected tests passed with zero failures/errors/skips. The legacy64 B300 check also passed all 4,352 BF16 output elements (69,632 bit positions); no Rubin hardware claim. The three native modules were freshly built. The sole cache symlink connects newly downloaded versioned TRT header content within this same private workspace. All 8 GPUs were idle at final collection. No further runs were launched.

```text
========= 39 passed, 695 deselected, 754 warnings in 502.22s (0:08:22) =========
========= 16 passed, 718 deselected, 176 warnings in 490.13s (0:08:10) =========
========= 49 passed, 2637 deselected, 3 warnings in 187.25s (0:03:07) ==========
```
