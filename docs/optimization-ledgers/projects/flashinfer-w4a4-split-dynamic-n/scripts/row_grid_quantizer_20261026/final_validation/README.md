# Existing-test validation of the combined candidate

Validated the frozen `retained-policy-r2/flashinfer` deployment on c3 B300 GPU 0 (`GPU-5d3301f8-c737-3b0d-a196-8ad9e301399c`), using the parent-controlled `nvcr.io/nvidia/pytorch:26.05-py3` environment and `control-0def601d/.venv/bin/python`. The source HEAD is `0def601d6603df828ea39679b41ccbce64f7f09e`; the unstaged binary/full-index patch SHA256 is `8828ab24d607c27905ab6b53e19ad278869fd84655f1d96b289e43eb0bdcd03b`.

All **82 existing tests passed**, with no failures or skips:

| Existing coverage | Passed | Purpose |
|---|---:|---|
| NVFP4 kernel cache names | 37 | Existing getter signature and generated-name contracts, including the metadata-only `has_valid_rows` correction |
| Large-M per-token quantization | 4 | Default callers, PDL off/default, repeated grid traversal, and row addressing around the 32-bit offset boundary at M=798848/799040 |
| Wide-row per-token quantization | 18 | Exact CUDA/CuTe equality for FP16/BF16, all three SF layouts, K=1536/18432/69632, M=130; includes the default two-pass fallback |
| Per-token output scale and padding | 18 | Unchanged packed bytes/SF, exact output-scale folding, and SF zero padding for M=1/17/130 |
| Gated MoE and wrappers | 5 | Existing GeGLU, both SiTU clamp modes, wrapper accuracy, and CUDA graph replay |

The small external collection plugin only deselects the unused wide-row combinations; it adds no assertions or tests and changes no upstream source. Exact selected node IDs, commands/environment, raw pytest output and JUnit XML are under `results/<group>/`. Each group ran with `-q -x`; all warnings were existing deprecation warnings. Total campaign wall time was 56.09 seconds, including four process startups and source verification.

The cache namespace is source-private `7632c8c89b19fb7f4cb7ae5c7b5ded29a0a16db77c4aa07b5d695131efe76aa0`. All recorded native source hashes and shared-cache symlink targets were checked before testing. Source hashes and the complete unstaged patch were verified before and after; the receipts are identical. No source was changed during validation. GPU 0 was checked idle and released afterward.

This existing-test run complements the earlier source-paired task-local row-grid gate (408 graph replays), which covered the optional live-row count, changing routes/counts including zero work, PDL on/off, one/two CTA, CLC/static, and SiTU/SwiGLU. The current 82 tests concern the final composed source; the earlier paired gate concerned the isolated quantizer candidate. Neither is a full repository suite or sanitizer claim.

`campaign.py` is the exact remote driver; `collect.py` retrieves only receipts/logs, and `results/manifest.json` records their SHA256 hashes. The metadata-only cache-name correction is separately documented in `../cache-name-static.json`, with 1,152 static old/new generated-name equivalence cases. The frozen original row-grid experimental source was not edited.
