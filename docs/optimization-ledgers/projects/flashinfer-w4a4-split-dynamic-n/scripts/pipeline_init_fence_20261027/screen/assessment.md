# Fence consolidation assessment

The 48-point fixed all-CLC screen validates all source, cache, routing, tactic, selector and raw 100-sample checks. Candidate/control results remain isolated from the TMEM candidates. Exact latest clean9b controls were reused on the same GPUs, followed by fresh candidate/candidate/control.

Overall C/A is 0.99918x, decode 1.00028x, prefill 0.99808x. This is neutral aggregate timing, not a demonstrated end-to-end speedup. 30/48 point estimates improve; 18 improve in both temporal comparisons and 14 regress in both. Median absolute control drift is 0.093%, maximum 3.737%.

The worst point, V3 MXFP8 at 16K, measures 0.96499x (+28.17µs), with −3.737% control drift and forward/reverse ratios 0.99122x/0.93917x. V4.1-Flash MXFP8 at 16K measures 0.99210x (+7.96µs) with 0.572% control drift and both orders slower. K3 MXFP8 at 16K changes sign between temporal comparisons. These observations remain visible in the complete raw table; drift is a limitation, not proof that every regression is measurement noise.

Actual source codegen provides a separate cleanup reason: all 44 cores remove startup instruction sites; registers, storage, pipeline geometry and UMMA commits remain unchanged, and post-init opcode streams match. Summed static-site deltas are −240 for 32 CLC cores and −55 for 12 static cores. Exact gate coverage passes 64 CLC plus 24 static replays per source. Under the requested instruction-cleanup objective and accepted slight prefill regressions, retaining this focused candidate is reasonable without claiming a performance speedup. Canonical integration and retention remain the parent's decision.

See `screen-results.md` for all 48 four-arm raw medians, `results/collection.json` for transferred hashes, and `../gate/result.md` for the actual-source exact/codegen evidence. No native AUTO, TRTLLM, W4A16 or sanitizer runs are claimed.
