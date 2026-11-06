# W4 raw readiness plain-wait: rejected

Base `b52e4e09649dc180fc7583a25ec35ff55f04654d`; isolated candidate kernel `f88299aa4ac64fe1054cba3322b9546fb8ff2323254904e01da92b45d035f9a6`.

The candidate removes only the raw-weight full-status lookahead and its optional consumer-wait argument (12 deleted lines). It retains the required wait, decoded-slot lookahead, all release/phase/fence/PDL operations, roles, register budgets and tactics. The early query can overlap subsequent work; removing it is not a free simplification.

- **Qualification:** 10 native compile captures have no spills and unchanged resource geometry; 39 existing exact/graph tests passed. Static instruction count is mixed, not an overall reduction.
- **Performance:** 18 predeclared native cells across all four models and EP/TP, fresh same-GPU C-A-A-C, fixed routes/tactics, 10 warmups and 100 strict CUPTI samples per phase. The W4 metric is the arithmetic mean of the two phase medians in each arm. No retuning or sanitizer.
- **Decision:** reject as-is. Overall −0.277%, decode −0.455%, prefill −0.135%; EP −0.590%, TP +0.116%. Tight decode regressions include V41F TP −1.797% (control/candidate repeat spreads 0.099%/0.049%), V41F EP −1.158% (0.031%/0.307%), and V3 TP −0.975% (0.055%/0.110%). The V41F TP prefill gain +2.632% has a 4.666% control spread and does not offset the stable losses. Preserve all results and do not add shape-specific gates.
- **Evidence:** `screen.csv`, `perf-summary.json`, `telemetry-summary.json`; all 7,200 samples, 32 guard receipts and 128 loaded kernels checked, all LOCAL=0, all timing windows have NVML samples. 493 archived files verified; archive SHA `c02add051cb8948b9eaebe1ca4fb1adf097addf9448ffc4ba13042f932a2f5ff`. Original exact/codegen evidence and source patch are retained separately.

This does not establish that all try-waits are beneficial; it closes this particular raw-ready lookahead removal. The retained W4 producer-empty and MMA-readiness changes are separate mechanisms.
