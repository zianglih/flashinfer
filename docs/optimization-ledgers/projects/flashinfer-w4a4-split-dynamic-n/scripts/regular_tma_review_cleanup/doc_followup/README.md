# Public FC1 documentation follow-up

Task-local patch only; it has **not** been applied to production or the frozen review checkout. The `before/` and `after/` trees preserve the complete public wrapper file. `public-fc1-docs-only.patch` updates three docstrings to describe Blackwell's internal routed-input preparation and regular-TMA GEMM while retaining the public gather API, original unpermuted inputs, fused activation, and Rubin's in-kernel gather behavior.

`verify_docs_only.py` strips docstrings from both snapshots and requires exact full-module AST equality. It also verifies the patch against the snapshots, compiles the after snapshot without execution, checks the protected review sources/manifests and original PR body, and runs `git apply --check` against both source checkouts. Independent peer review reproduced the AST hash. No source files were changed, CUDA modules imported, or GPU tests/benchmarks run.

```bash
python3 scripts/regular_tma_review_cleanup/doc_followup/verify_docs_only.py
```

The proof is in [docs-only-proof.json](docs-only-proof.json):

- Before source SHA-256: `e4f8ceb92d5bfef50d40493a982f6fcca2775183d53393eeff39e43b65cd4d3b`
- After source SHA-256: `a738fd07d4750d41707cc84d45d60d686ee0e462f8b2ebb3c36158676f2d9135`
- Patch SHA-256: `b19ea1036e818576d493919e9dd2a9609f59728a27729cb707b49fe6801e851c`
- Normalized AST SHA-256: `63cb681cc122846f24aba903f7a8585604cd63d7e303cba2c2b4c6eb59d126f0`

The parent can apply the patch after the retained implementation's campaign. The verification script intentionally expects the saved pre-application sources; it is not intended to pass after applying the patch.

The PR draft already distinguishes CUDA graph timing correctly: “Graph timing includes the preparation kernel; it excludes host allocator overhead.” Scratch allocation occurs during ordinary invocation or capture; replay measures the captured device preparation. This follow-up makes no PR draft changes or new performance claim.
