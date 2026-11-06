# N3U EP8 W4A4 16K iKET diagnostic

Source-bound FC1 capture at frozen d35fcfda versus fb66a27e, same old winner/routes, GPU0 B300. Only the first two clusters emit markers; marker-only source copies preserve all non-marker AST nodes. Both native profiler captures completed successfully. Full trace JSON, source proofs, route/winner bindings, capture receipts and summaries are archived in `evidence/`; archive hash is recorded in `fetch-receipt.json`. Initial two attempts stopped in argument parsing before kernel execution; the third uses the script's distinct `--backends cutedsl` and `--profile-backend cute-dsl` selectors.

- Startup dependency wait is small in this sample (mean5ns in gather candidate); this does not support startup/descriptor work as the primary N3U prefill issue.
- Candidate relay wait averages461ns and MMA's separate gather-ready interval57ns. These overlap other roles and are not additive bottleneck costs.
- Epilogue accumulator waits increase substantially (590ns→1983ns mean), consistent with more mainloop starvation. Epilogue body spans also grow; register-spill removal is independently being tested from actual SASS evidence.
- Gather issue averages115ns per warp perstage versus45ns for the old activationTMA warp. Four warp issuers and different marker counts make this a scheduling clue, not an equal-instruction latency comparison.
- There is no CLC work in this winning tactic. Do not attribute this regression to CLC scheduler pressure.

Instrumented first-two-cluster spans are not end-to-end timings and must not be used for retention. Use the independent full CUPTI table for the stable -31.37% N3U EP W4A4 16K regression, and new paired screens for subsequent changes. The existing-tactic retune independently identifies wider channel tiles as a way to reuse gathered inputs.
