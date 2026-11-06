# Source04 focused W4 validation

**All checks passed** on frozen full-gate-04 candidate (`moe_w4a16_kernel.py` SHA256 `777baf6bb832a5152022f8f3e9364f3bddba944c3e17fa2913f68170ea562110`). This is the approved wait-placement-only delta from source03. Source hashes were verified before and after each process.

- **10 existing pytest cases passed**, zero failures/errors/skips, 13.46s: six W4 scale-mapping cases; route16/tail1 and route128/two-CTA/half-plus-one boundaries; functional weight-scale update with original/swap weight layouts. The unchanged swap-AB FC1 case from the earlier gate was not rerun.
- **Four source03→04 fused-finalize compatibility cases passed**, original/swap layouts × PDL off/on. Shape17 tokens, hidden256, intermediate512, four experts, top-k2, fixed N16 one-CTA tactic, two full-plus-tail expert routes and two empty experts. Canonical FC1 rows matched exactly; fused final output also matched exactly (observed max absolute difference0 for all four; required rtol/atol1e-2).
- Combined chain elapsed68.91s. Existing B300 on `fi-moe-descriptor-recover-1028`, C3/ziangli, GPU1; `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2. Persistent source-specific/native caches reused. GPU reservation released after completion.

No autotuning, sanitizer, performance measurement, or source edits ran in these helper gates. Broader changed-routing graph and CLC coverage is owned by the separate source04 graph gate; performance is owned by the separate paired C-A-A-C run.

Receipts and exact commands: `existing-test-chain.json`, `existing-pytest-secondary-gpu1/receipt.json`, `fused-w4-secondary-gpu1/receipt.json`. Raw pytest log/JUnit and paired logs are in the corresponding subfolders. Helpers remain outside the source repository.
