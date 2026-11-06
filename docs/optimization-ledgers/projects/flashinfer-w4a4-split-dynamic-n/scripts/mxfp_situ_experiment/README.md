# MX SiTU public admission

Independent unstaged source: `flashinfer-mxfp-situ-review`, base `adf02fdd4a8fd2a5d4d2ca54b6969cd65572d93d`, frozen patch `1c6801111f41d57ad16db4fc7aa58c5bce84a5aea669535c881ae5dc8bf2851a`.

Only two public MX rejection checks and their documentation were changed in fused_moe.py. The existing test file covers both MX modes with default SwiGLU, gate-only SiTU, and gate+up SiTU on N16 one-CTA and N128 two-CTA tactics. The existing cache-key test includes both new modes. No kernel, tuner, trace, benchmark, prepare utility, or PDL implementation changed.

The shared Blackwell epilogue already applies SiTU in FP32 before format-specific quantization. Both beta parameters reach FC1 compile/cache inputs. SiTU bypasses SwiGLU alpha/beta/clamp parameters; a missing linear beta leaves up unclamped. The shared trace reference reverses MX row interleave and uses the same algebra; it remains an approximate numerical reference. Independent read-only review by benchmark_scope_cleanup confirmed this contract.

Validation: scoped pre-commit passes;19 focused tests pass on B300 SM103 with zero failures/skips. Function/wrapper equality uses atol=rtol=0. Eight SiTU cases additionally pass the existing numerical accuracy criterion and are closer to SiTU than ordinary SwiGLU. No fused-finalize or sanitizer expansion was requested. All85 source hashes and the full patch are identical before/after the gate.

Evidence: `evidence/mxfp-situ-r1/{source.json,candidate.patch,audit.json,validation.json,pytest.log,pytest.xml,pre-commit-final.log}`. Initial transport exceeded the remote single-argument limit before execution. `retry_transport.py` uploaded the exact frozen program in hash-checked50K chunks; no test was repeated. Remote clone `/workspace/flashinfer-w4a4-split-dynamic-n/mxfp-situ-r1` remains frozen.
