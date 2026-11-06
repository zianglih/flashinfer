# MMA readiness result — reject

The full 56-cell screen does not justify the extra Boolean, TEST and native code. Root selected rejection after its final independent recovery and union replay passed. Candidate `e9088366` is preserved in immutable snapshots; the rejected local worktree/branch has been retired with exact source, patch and ignored-check-cache preservation. Retained production is unchanged.

| Group | Cells | Geometric speedup | Negative |
|---|---:|---:|---:|
| all | 56 | -0.03633% | 36 |
| decode | 28 | -0.03124% | 18 |
| prefill | 28 | -0.04141% | 18 |

All 22,400 CUPTI spans and 224 phase medians were replayed. The 896 NVML quartiles have no missing or exception windows. Maximum C/A repeat spreads are 0.483%/0.511%; repeat spread is descriptive, not statistical confidence. Every original negative is preserved. Full phases and all 56 rows: [table](combined56/table.md), [groups](combined56/groups.md), [components](combined56/component-deltas.csv).

The initial allocation disappeared after 11 complete jobs (28 cells). Their four-phase jobs remain intact and passed independent source/cache/raw audits. Two partial jobs are preserved but excluded. The separate recovery campaign reran 12 whole jobs (28 cells), including those two; no phases were spliced. Sources, frozen choices, routes, compiler metadata and generated release Ninja descriptions match. A normal recovery rebuild changed routing/moe_utils ELF bytes, so the original and recovery native-library cohorts remain explicitly separate. Each comparison uses both arms within its own cohort and physical GPU. Original 28 row dictionaries are unchanged.

All 448 measured loaded-function records have LOCAL0. Of 112 paired stage configurations, five FC2 pairs grow by 1–4 registers; dynamic shared memory and driver occupancy remain unchanged. The exact gate separately preserved the rejected strict guard, the reviewed 128→130 wide per-token exception, and the full native TEST window; the wide FC2 adds 50 non-NOP instructions, long-K FC2 adds 22. A real independent instruction window does not establish a useful end-to-end gain.

The motivating N3U TP MXFP4x8 T32 cell is −0.16383% (C/A spreads 0.152%/0.075%). Candidate FC2 duration falls 0.368 µs, but FC1 duration rises 0.239 µs and E2E rises 0.208 µs. Critical extensions change +0.231 µs FC1 and −0.176 µs FC2. These component medians are diagnostics, not additive E2E accounting. No shape-specific rescue, further timing, or full refresh is proposed.

Evidence: `evidence/mma-readiness-screen-interrupted/1793378675231416000/{data,report}` and `evidence/mma-readiness-recovery/1793379768359828000/{data,report}`. Recovery source/cache qualification and selection provenance: `runtime/recovery-1030/`. The original incomplete campaign is never relabeled complete. GPUs4/6 released after the successful read-only idle snapshot in `runtime/recovery-1030/gpu-release.json`.
