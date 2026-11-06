# Packed FC2 alpha scaling: focused qualification

Candidate: `fd72759b15b8d417d6c791c0382f90d14262a8e4` plus one unstaged W4A16 kernel change. Kernel SHA256 `a8072d86763f4ebd48e516b39bf2a5f4904c87495ef9764d2babd2f0a3bc9bc2`; patch SHA256 `9befca580574f6cff261c7b5aaf5a2d4ce55e491cbed5470a6730c81b2646e69`. No tactic changes.

- **Change:** scale the native FP32 accumulator fragment once with explicit paired RN multiplication before choosing the full-TMA or partial-SIMT store. Remove the two branch-local copies. Activated FC1 and fused-finalize paths retain their existing behavior.
- **Exact gate:** 48 maintained W4A16 route-boundary cases per source, each checked against the existing bit-exact reference and an eager/graph byte comparison. All 48 cross-source output hashes match. PDL on/off, static/CLC, one/two CTA, route tiles 8/16/32/64/128/192, full plus partial tiles.
- **Layouts/API:** existing `TestCuteDslMoeW4A16::test_weight_scale_update` passed all four wrapper/functional × old64/new16 layout combinations on the candidate. The larger boundary matrix uses old64; FC2 weight packing is shared across these options.
- **Codegen:** 48 owned compile pairs saved. All 24 FC1 instruction streams are identical. Every FC2 specialization keeps the same resource declaration (`REG:128`); the unchanged warp register budgets remain 176 epilogue / 80 generic. No local `LDL/STL` or uniform `MOV.SPILL/R2UR.FILL` sites in either source.
- **Important limit:** the original scalar source already auto-vectorizes to `FMUL2` with `.F32x2` operands. This change removes duplicated *static* full/tail branch blocks; it does not halve the dynamically executed multiply count. No performance conclusion is drawn from this gate.

| FC2 MMA tile | CTA group | Static paired FMUL2 sites | Non-NOP instruction reduction across PDL/CLC |
|---|---:|---:|---:|
| (128, 8, 256) | 2 | 8 → 4 | 4–4 |
| (128, 16, 256) | 1 | 16 → 8 | 7–8 |
| (256, 32, 256) | 2 | 32 → 16 | 16–16 |
| (128, 64, 256) | 2 | 32 → 16 | 16–16 |
| (256, 128, 256) | 2 | 32 → 16 | 16–16 |
| (256, 192, 256) | 2 | 32 → 16 | 16–16 |

Environment: one NVIDIA B300 (primary GPU3), `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2; runtime paths, image, cache configuration, and commands are pinned in `evidence/runtime.json`, `evidence/status.json`, and `evidence/layout-smoke/completed.json`. Native compilation-cache links were retained. No sanitizer or performance test was run by this gate.

Raw pytest result:
```text
4 passed, 220 warnings in 8.63s
```

Raw case-by-case outputs: `evidence/control.log` and `evidence/candidate.log`. All PTX, cubins, SASS, and resource dumps are in `evidence/{control,candidate}`. The archive contains 407 hash-verified files: `evidence-verification.json`. Final source-bound gate receipt: `evidence/GATE.json`, SHA256 `297c4d6a430f7aca1b6cd377d060cd13a7ff07212408cbe74c155223826cf4db`. The local comparison independently reproduces the remote receipt.

The inherited 348-file source receipt omits the existing shared W4A16 oracle. Supplemental `reference-binding.json` binds its bytes to the tracked `fd72759b` file in both control/candidate checkouts and to the canonical local file; the postflight diff contains only the intended candidate kernel. No oracle changes were made.
