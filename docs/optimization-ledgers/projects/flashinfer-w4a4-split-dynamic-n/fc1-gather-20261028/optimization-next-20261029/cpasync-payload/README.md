# Refreshed cp.async payload experiment

Rejected after the complete 44-cell screen; the verified source copy has been retired. Helpers, patch, generated code and evidence remain here.
Base `c0c0bc41c70100c694ac55585990971aba8b7fb9`, control kernel `3225acf2`, candidate `8baae0e0`.

- Replace FC1 Gather4 payload with 128-bit cp.async vectors from the existing four-warp gather group. No public option or tactic axis.
- Cache source row byte offsets with Int64 arithmetic before K iterations. Preserve unsigned routing-index division, exact SW128 destination mapping, dynamic two-CTA row ownership, partial-K zero-fill, nominal allocation and stage depth.
- Interleave half-warps in the vector-task order. All four warps issue payload even in the smallest 64-vector stage; no shape-specific branch.
- Payload and SF copies precede a single per-thread async completion. Local barrier count is 128 instead of 129; the former TMA transaction-byte announcement is removed. Keep the existing local acquire/proxy fence, shared-scoped release/acquire relay, MMA/SF order, operand-empty reuse and PDL contracts.
- FC2 is unchanged. Control112 / gather128 / epilogue256 register budgets and stage calculations are unchanged.
- The cp.async payload uses the existing CuTe default cache operation, replacing Gather4 plus its TMA cache hint. This is a transport-policy comparison, not a single-opcode attribution.

R5b passed 44 existing tests but predates register donation and the shared-scoped relay release fix. Its four-job comparison against R6 differs only approximately ±1% at job level while both have the dominant common 30–65% regression. This does not cleanly establish the result under the current policy; it also gives no positive evidence to retain cp.async. A bounded codegen/exact/CAAC recheck is justified, not a broad performance claim.

`source_proof.py` checks 40 geometries, 4,008 live-row states, 857,088 absolute-swizzled vector addresses and 470,208 K-tail vectors. All four warps issue; nominal bytes are covered exactly once; invalid routes are zero-filled. FC2 partial evaluation, all other class methods and every kernel section outside the gather branch/local-arrival count match the control AST.

GPU qualification passed 17 exact tests, including the smallest half-warp transfer geometry. All 12 generated variants have zero local-memory bytes and no LDL/STL sites. Payload lowering is 16-byte `cp.async.ca.shared.global` / `LDGSTS.E.LTC128B.128`; FC1 uses the intended 112/128/256 register budgets. See `QUALIFICATION.md` and its immutable evidence archive. The five-job, 44-cell C-A-A-C screen completed with frozen tactics and strict 100-sample CUPTI timing: −4.67% overall and −9.92% prefill, excluding unchanged W4A16. See `RESULTS.md` and `report/cpasync-vs-retained.png`.
