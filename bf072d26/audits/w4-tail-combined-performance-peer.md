# Complete W4-tail peer decision evidence

Independent audit passes for the exact union of the original 12 cells and the disjoint 27-cell extension. All 39 row dictionaries, 15,600 CUPTI samples, 156 phase medians, 196 zero-local loaded functions, 78 unchanged cell/stage configurations and 40 default-stage joins are verified. The 624 clock quartiles retain 49 exceptions and one missing observation. No original row or sample was replaced.

| Retention band | Cells | Geomean | Negative cells |
|---|---:|---:|---:|
| Decode 4–64 | 15 | +1.701% | 0 |
| Middle 128–512 | 9 | +2.110% | 0 |
| Prefill 4096–16384 | 9 | +0.456% | 6 |
| All, excluding 1/2 | 33 | +1.471% | 6 |

All 24 token-4–512 cells have both candidate phase medians below both control phase medians. Their repeat spreads remain below 0.462%. This repeated cross-model signal supports the modest private interface/predicate complexity: inactive transform groups skip work that MMA does not consume, while synchronized stage publication remains common. It is stronger evidence than a neutral aggregate or instruction-count argument.

Prefill is a tradeoff, not a reliable gain. The positive aggregate is influenced by K3 8K +3.591% (0.905%/3.606% C/A spreads) and V41F 8K +2.895% (1.448%/0.858% spreads), both with clock variation. N3U loses at all three prefills (−0.563%, −0.293%, −0.578%; combined −0.478%), and the worst loss overall remains K3 16K −0.746%. Those small losses are consistent with the user's accepted slight prefill cost, but must remain explicit. No threshold-based dismissal, row filtering, shape gate or further tuning is justified by this audit.

The complete rows and all four phases are in `experiments/w4-tail-dequant/combined39/table.md`; machine-readable audit is `audits/w4-tail-combined-data-peer.json`. Source-qualified reuse of 429 other cells is a separate publication boundary and is not included in this causal gain. The original 12-cell assessment remains preserved separately.
