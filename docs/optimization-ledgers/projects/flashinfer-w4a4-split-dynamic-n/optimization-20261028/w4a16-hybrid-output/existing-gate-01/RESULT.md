# Hybrid-01 focused W4 validation

All checks passed on the frozen hybrid-01 candidate (`moe_w4a16_kernel.py` SHA256 `838acecd15395755dec3b59422f99f886570b1bf237d02a10e439b53ec627b89`). Source hashes were verified before and after each process. The paired control is padded R2, not the descriptor experiment.

- **10 existing pytest cases passed**, zero failures/errors/skips, 12.80s: six W4 scale-mapping cases; route16/tail1 and route128/two-CTA/half-plus-one boundaries; functional weight-scale update with original/swap weight layouts.
- **Four R2→hybrid fused-finalize compatibility cases passed**, original/swap layouts × PDL off/on. Shape17 tokens, hidden256, intermediate512, four experts, top-k2, fixed N16 one-CTA tactic, two full-plus-tail expert routes and two empty experts. Canonical FC1 rows matched exactly; fused final output also matched exactly (observed max absolute difference0 for all four; required rtol/atol1e-2).
- Combined chain elapsed58.93s. B300 on `fi-moe-descriptor-recover-1028`, C3/ziangli, GPU4; `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2. Persistent source-specific/native caches reused. GPU4 reservation released after completion.

No autotuning, sanitizer, performance measurement, reference-self-test, or source edits ran in these helper gates. This selection uses full gated channel tiles; partial output-channel checks are outside this gate. Broader changed-routing graph, exact epilogue-boundary and active CLC coverage is owned by the separate hybrid graph gate; performance is owned by the separate paired CUPTI runs.

Receipts and exact commands: `existing-test-chain-gpu4.json`, `existing-pytest-gpu4/receipt.json`, `fused-w4-gpu4/receipt.json`. Raw pytest log/JUnit and paired logs are in their corresponding subfolders. Helpers remain outside the source repository.
