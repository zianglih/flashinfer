# Full B200 matrix: independent audit

Passed all evidence and rendering checks for 8 jobs / 24 workloads / 48 comparisons / 48 phases / 14,400 raw CUPTI samples. The generated CSV, Markdown table, audit JSON, and all 48 SVG heatmap labels agree with independently reconstructed numbers. The PNG was also visually inspected: model/token order, EP/OFF/ON and TP/OFF/ON columns, labels, sign convention, color saturation, and frozen-tactic limitation are clear.

| Scope | OFF speedup | ON speedup |
|---|---:|---:|
| ALL | +2.148856% | +2.964935% |
| EP | -1.776590% | -0.020372% |
| TP | +6.231181% | +6.039380% |

The positive overall aggregate does not remove the EP regressions. OFF has 8 negative comparisons (7 EP, 1 TP); ON has 7 (all EP). Worst OFF is K3 EP8 / 16 tokens at −8.3481%; worst ON is V3 EP8 / 8 tokens at −5.8286%. V3 EP8 / 4 tokens again loses with OFF, consistent with the separate pilot and reviewer concern. The losses therefore are not confined to 4 tokens.

Every phase result/log hash, source head and benchmark hash, exact frozen key/tactic choice, repeated route identity, public timer contract, no-retuning condition, and current resolved tile/cluster/PDL configuration passed. CLC flags match the existing problem-cluster capacity rule; V3 TP8 / 4 tokens correctly uses ordinary FC1 scheduling in both current arms, while FC2 remains ordinary throughout. No blanket FC1-CLC assumption was used in the final audit.

All 144 measured phase/token windows have clock samples, and all 576 quartiles have coverage. Every observed SM clock is1965MHz, memory clock3996MHz, and event reason0. Maximum repeat spread is0.5412%, smaller than the substantial EP losses. Clock observations remain coarse NVML telemetry, not per-kernel measurements.

Before and OFF use the same recorded baseline tactics/layout. ON uses separate retained winners; its comparison is end-to-end behavior, not layout-only attribution. B300-origin frozen choices on B200 do not establish independently optimal B200 performance. This audit performs no new GPU work, retuning, source changes, or native ELF verification; the latter is being checked separately.

Complete reconstruction, per-cell clocks, source/result hashes, render hashes and statistics: `full-matrix-independent-audit.json`. Reproduction: `audit_full_matrix.py`.
