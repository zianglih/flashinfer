# Rebased host/wiring audit — 2026-10-26

Base: `215f83cb27e39b6b973c0691b93fc378a53a10e4`; starting PR head: `24da0138fd67dc7172ef3dd9e6d1358e2b059a53`.
Owned: `fused_moe/cute_dsl/{fused_moe.py,tuner.py,_inputs_helper.py}`, `fused_moe/{prepare.py,runners.py}`, `docs/design_docs/flashinfer_moe_api.md`.

## Tightening performed

- Restored upstream `validate_w4a8_inputs(..., weight_elems_per_byte=2)` exactly. Reuse the existing shared FP4/FP8 scale-layout validator rather than renaming it and adding a second dtype-inference path.
- Restored upstream `_moe_core_impl` weight dtype inference/validation and private `weight_dtype` argument. Retains the upstream rejection of FP8 weights with FP4 activations; the pre-audit rewrite inferred FP4 from the activation and lost that rejection on the W4A4 path.
- Kept the public shared dtype check for both GEMM weight tensors, canonical `quant_mode="mxfp8"` wrapper support, and the required MX SiTU/unfused-finalize changes.
- Restored the functional API's invalid-mode diagnostic exactly, including ordering/formatting. Kept existing functional API quant-mode documentation, adding only the new supported activation/finalize contract. Removed unrelated SiTU doc rewrites.
- Restored upstream shared tactic canonicalizer name and call pattern. Removed a new forwarding helper whose only distinction was diagnostic naming; acceptance of three/four/five-field Python and JSON tactics is unchanged.
- Restored localized Rubin FC1/FC2 functions byte-for-byte, including public GEMM wrapper calls without Blackwell K-depth/CLC arguments. The normal Blackwell path continues using private implementation entrypoints so tuning controls remain private.
- Restored upstream input sampler file exactly. Its zero-quota expert behavior is intentionally tracked upstream with TRTLLM issue14146; changing that profiling distribution is separate from the replacement kernel. **Fresh benchmark results must include this sampler change in their measured-source attribution; do not reuse old timing claims as current evidence.**
- Restored upstream weight quantization closure exactly. `mxfp8_quantize` already defaults to the CUDA backend and returns uint8 scales. Weight dimensions are already checked divisible by128, so alignment32 and alignment128 produce the same padded dimensions. Removed redundant backend/alignment/view arguments and a duplicate preparation architecture guard; the runtime/runner still rejects MX modes on Rubin.
- Kept only the necessary weight preparation layout change: Blackwell up16/gate16 pairing and unchanged Rubin up64/gate64. No Rubin tactic enumeration or kernel behavior changed.

Owned PR diff versus base: 254 additions / 210 removals across five files (previously 308 / 270 across six). `_inputs_helper.py` leaves the PR diff entirely.

## Checks

- `python3 audit-rebased-20261026/check_host.py`: passes. Receipt: `host-checks.json`.
- Syntax parse of owned Python files; exact source equivalence for shared validator, entire sampler, localized Rubin functions, Rubin tactic enumerators, and the CuTe DSL weight quantization closure.
- Unrelated preparers and backend runners have identical ASTs to upstream.
- Actual shared validator functions executed with CPU tensor metadata: both MXFP4/MXFP8 contracts succeed; mismatched weight dtypes and malformed activation scales are rejected.
- All360 Blackwell tactics roundtrip through JSON at three/four/five tuple fields (1080 cases), retaining routing-N agreement. All Rubin tactic tuples and preexisting extracted parameters match upstream; new shared Blackwell fields remain neutral (`None`, `None`, `False`).
- Scoped pre-commit: `host-precommit.log`; first formatting pass normalized one file, final pass passed.
- No CUDA/JIT execution in this subtask; parent owns new GPU campaign.

No remaining host integration blocker found. Files are unstaged; no commit or push from this subtask.
