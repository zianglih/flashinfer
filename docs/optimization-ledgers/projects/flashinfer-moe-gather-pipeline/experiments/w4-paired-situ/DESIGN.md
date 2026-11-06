# W4A16 paired scaled tanh

Prototype only; local and unstaged in `flashinfer-w4-paired-situ-review`, based on retained `49c91adf47d30fc2049c76cbaf34d0ccf3291434`. One file changed, +23/−36. Candidate SHA256: `5e61d04544524410b273b8e49ee2b8f6d9e20266c22346aba06ab3743c2c4e1d`.

Replace the private scalar helper and its adjacent call pairs with one paired helper. Use existing CuTe packed RN operations for the same independent channels; leave EX2 and reciprocal scalar. The original reciprocal-from-Python-beta convention, `0xC038AA3B` constant, non-FTZ arithmetic, FTZ approximate SFUs, and separate `2 * inverse` / `result - 1` rounding boundaries are preserved. No new branch, state, public argument, tactic, oracle or shared helper change. The existing rationale comment and docstring remain.

`source_audit.py` parses the original inline PTX and symbolically executes the actual candidate helper with documented CuTe operation stubs. It verifies 4,118 lane expression graphs over 2,059 Python betas, including betas for which rounding beta before reciprocal would change the answer. It also restores the old helper call pairs and proves the rest of the module AST identical, except removal of the now-unused `T` import. The literal's bits are exactly `0xC038AA3B`. This is a source arithmetic proof, not device equivalence.

Local syntax, whitespace and all applicable scoped pre-commit hooks passed. `precommit.log`, `source-audit.json` and `candidate.patch` are the receipts. No GPU work has run.

Before timing, native qualification must verify:

- Actual RN packed multiply/add/sub lowering, with no FMA contraction of the original separate multiply/subtract.
- Unchanged scalar `ex2.approx.ftz` and `rcp.approx.ftz`, beta/reciprocal constants and channel order.
- Reduced actual arithmetic issue instructions after counting packing/MOV effects; unchanged LOCAL0/resource constraints.
- Existing exact SiTU gate-only and gate+linear cases, with both integer and non-fp32-exact beta values; representative one/two-CTA and old/swap layouts.
- Bounded direct helper comparisons for signed zeros, subnormals, finite extremes and exceptional values, without weakening the existing finite-output MoE oracle or claiming unspecified NaN payload identity from source alone.
- Non-SiTU specializations remain native-identical; FC2 and shared MegaMoE helpers are not modified.

The separate swap SiTU proposal remains read-only in `audits/paired-activation-math/`. It has a different FMA and reciprocal contract and is not folded into this prototype.
