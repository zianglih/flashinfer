# Protected-prefix resource policy revision

Based on retained `f175faea`, with only the core file changed and left unstaged in `flashinfer-register-roles-20261027`. Frozen source and helpers are named in the adjacent receipts; rejected `651b` artifacts remain unchanged.

- Buffer only prefixes spanning more than one 32-column slab. A one-slab prefix uses the retained direct loop and its original release point, including the empty-slab release.
- Exchange registers only when the existing activation-accumulator overlap path uses that buffer (`overlap_activation_accumulators and overlap_activation_steps > 1`). The derived `buffered_activation_steps` count is assigned once and reused by the buffer and both register-role operations; no new public parameter or tactic axis.
- The arithmetic factoring is unchanged. Three branch AST checks and 1,544 interval/row cases pass; the direct one-slab loop body matches the retained AST.
- This specifically removes the unnecessary FC2 donor reduction responsible for the rejected 144-byte producer spill, and avoids the one-slab array's 16 extra register moves. Actual compiler output must verify both before timing.

## Ordered validation

First run unchanged extra cases 6, 1 and 2: one-CTA N256/M128 per-token FC2 and the MXFP8/mixed single-slab paths, both PDL modes, exact changing routes. Require no role instructions in these unaffected cores, no hot/local spills, and no one-slab extra moves. Then run existing two-slab cases 0, 3 and 4 and compare release ordering/register pressure. Preserve the task-local fail-closed resource guard; the cold verifier is byte-identical to the independently reviewed version and does not accept the rejected fresh-warp-index case5.

The parent will decide bounded beneficial-cell timing after codegen. No full48 timing is authorized by this receipt, no performance claim, and no forced-tactic result is native-AUTO evidence.
