# Focused existing-test validation for 8c1a2017

Exactly the ten parent-authorized, unchanged pytest nodes passed on frozen commit `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e`. No rerun, test override, plugin, source change, broader suite, or sanitizer was added.

```text
10 passed, 24 warnings in 6.00s
```

The warnings are CuTe deprecations. JUnit records ten cases, zero failures/errors, and zero skips. The runner verified clean tracked source, the six implementation/source hashes plus five shared source hashes, and the test-file hash before and after execution. GPU5 was live-checked idle (0 MiB, no compute process) before launch; GPUs2/3/4 were not used. Start `2026-10-25T21:44:49.452934+00:00`, finish `2026-10-25T21:44:59.582312+00:00`.

- Hardware: NVIDIA B200, GPU5 `GPU-a4c14cdc-d487-e8b3-9e76-1fdbbb5e1a21`, devbox `fi-w4a4-narrow-1025`, c1/ziangli.
- Environment: recovered `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.78, CuTe 4.7.1, PyTorch 2.12.0a0+5aff3928d8.nv26.05. These software versions belong to the previously verified campaign environment; this small runner records runtime variables and the live GPU identity, not a fresh package inventory.
- Private CuTe cache: `/workspace/flashinfer-w4a4-split-dynamic-n/cache/pdl-behavior-focused-validation-r1/cute_dsl`. Native cache remains `/workspace/flashinfer-w4a4-split-dynamic-n/cache/candidate-442`. No KEEP or DEBUG compiler override.
- Test file: `tests/moe/test_cute_dsl_fused_moe.py`, SHA256 `eaedf38e81d8c2e6f17432b3d8daafb10d73a00da5be23a4c7a79c0795a04f09`.
- Original read-only plan: [original-test-plan.md](original-test-plan.md). It remains an unchanged pre-execution document; this receipt records completion.

## Exact scope

| Cases | Coverage | Boundary |
|---|---|---|
| SwiGLU/per-tensor and ReLU2/per-token deterministic finalize | Two unfused NVFP4 full-chain numerical tests, including partial routing and both scale modes | Existing tolerance-based reference; PDL on via public default |
| Six FC1 K-tail cases | N16/32/64/128/256; K64/192/384/512; live1/17; reversed mapping and poisoned extra SF source tail | PDL off, BF16 output, one CTA; analytic oracle with `rtol=atol=0`, not a raw-byte assertion |
| PDL off/on forwarding | Both values reach the routing call | Host sentinel stops before routing/GEMM; no numerical execution |

This selection does not establish GeGLU/SiTU, homogeneous MXFP8, all six operand/SF combinations, two-CTA, full-chain PDL-off, or true-zero GEMM numerical coverage. Mixed W4A8 API tests are fused-finalize and were intentionally excluded. The previously completed source-pinned five-point native exact/true-zero records are separate evidence and were not rerun. No W4A16, CAKE, fused-finalize, or sanitizer scope was added.

## Command and raw evidence

The exact executed pytest command and environment are [executed-command.sh](executed-command.sh); the guarded original runner is archived under `raw/scripts/epilogue_codesign_audit/run_focused_validation_8c1a.py`. The executed top-level invocation was:

```sh
cd /workspace/flashinfer-w4a4-split-dynamic-n
source scripts/recovery442/env_candidate.sh
CUDA_VISIBLE_DEVICES=5 .venv/bin/python scripts/epilogue_codesign_audit/run_focused_validation_8c1a.py
```

Raw log, JUnit, preflight, and result are under `raw/logs/pdl-behavior-focused-validation-r1/`. [verification.json](verification.json) verifies the exact ordered node identities, all recorded raw hashes, the runner, and unchanged before/after pins. [fetch-receipt.json](fetch-receipt.json) records the read-only retrieval.

Raw archive SHA256: `512816640f26c12cc3bf66101c856266c6bd4112b83993638e555149b695e67a`.
