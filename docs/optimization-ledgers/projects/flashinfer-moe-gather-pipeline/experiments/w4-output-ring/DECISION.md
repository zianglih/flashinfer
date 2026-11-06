# Rejected: W4 bounded output ring index

The retained implementation remains `2b8eb9d8`; no optimization commit or PR update was made. The candidate `b4f80b0a` was rejected after the full104-cell primary and separate six-cell ACCA diagnostic passed source, timing and resource audits.

- The primary88-cell retention geomean is **+0.118%**, effectively neutral: decode+0.031%, middle+0.066%, prefill+0.317%. All31 retention losses remain. Prefill has substantial clock/repeat variation.
- The candidate adds an explicit wrap condition (7 additions/5 deletions) instead of the existing concise modulo. It removes1–4 non-NOP instructions per sampled GEMM, with unchanged resources and exactness, but the timing evidence does not justify that extra control.
- K3 EP4096 is−1.70% primary and−1.46% in the separate diagnostic. Candidate repeat spreads7.63%/2.34% prevent a confident isolated-regression claim. The other selected large losses shrink or reverse; two tight small decode losses reverse. No further rescue run or shape policy is proposed.
- Original104 rows remain primary; the six diagnostic rows are not averaged into or substituted for them. `results-diagnostic/` records all phase medians and primary→repeat GPU assignments. `decision.json` records all primary and diagnostic assignments, negative rows and their raw clock quartiles.
- The review worktree and its local branch were removed after exact source/status checks. Kernel/patch, all harnesses, raw evidence, native captures, plots and native table outputs remain. Main stayed clean at2b8; assigned GPUs are idle/released.

Primary heatmap/native tables: `results-primary/`. Full snapshots: `evidence/w4-output-ring-screen/1793384518306430000` and `evidence/w4-output-ring-acca/1793384891935355000` under the project root. Native qualification, compact-modulo precursor and preflight-only failures remain separate. Do not reopen this as a new modulo/ring optimization without new evidence.
