# W4 output ring native qualification

**Final decision: rejected.** See [DECISION.md](DECISION.md). The review copy is retired; this qualification record and all timing/native artifacts remain unchanged.

Retained control: `2b8eb9d8`. Candidate: `b4f80b0a`, unstaged in `flashinfer-w4-output-ring-review`. No performance claim.

The explicit wrap replaces the otherwise-unused monotonic output count with its bounded buffer index. It preserves the first `1 % stages` slot and advances only at the same two TMA-store sites. PipelineTmaStore state, SIMT tails, accumulator release and shared-memory synchronization remain unchanged. Source changes are 7 additions and 5 deletions; no new state, argument, tactic or shape policy.

- Exact: six fresh candidate calls against six immutable retained controls; both gated layouts, one/two CTA, CLC/static, PDL off/on, persistent tile transitions and token tails.
- Native: 18 pairs; all resources unchanged (FC1 96 registers, FC2 128), zero local bytes. Six finalizers have identical PTX, cubin and SASS.
- Source sequence proof: all bounded index states for depths1–64, including TMA and skipped/SIMT transitions. The original signed count is assumed not to overflow.
- Boundary: qualification forces existing small exact-test tactics and cluster caps. The held performance screen uses original production winners and no caps. ReLU2 appears in that full model matrix, while the qualification uses gated FC1 plus nongated FC2.

| Case | Stage | Output depth | Retained non-NOP | Candidate non-NOP | Delta |
|---:|:---|---:|---:|---:|---:|
| 0 | FC1 | 7 | 1783 | 1779 | -4 |
| 0 | FC2 | 3 | 1764 | 1763 | -1 |
| 1 | FC1 | 15 | 1549 | 1545 | -4 |
| 1 | FC2 | 7 | 1500 | 1497 | -3 |
| 2 | FC1 | 2 | 1797 | 1796 | -1 |
| 2 | FC2 | 5 | 1727 | 1725 | -2 |
| 3 | FC1 | 4 | 1771 | 1769 | -2 |
| 3 | FC2 | 2 | 1664 | 1663 | -1 |
| 4 | FC1 | 5 | 1769 | 1767 | -2 |
| 4 | FC2 | 2 | 1616 | 1614 | -2 |
| 5 | FC1 | 14 | 1961 | 1957 | -4 |
| 5 | FC2 | 7 | 1577 | 1573 | -4 |

Power-of-two stages also remove instructions, although register/address scheduling differs locally. The compact-modulo precursor left the modulus in generated code and was not selected. Its evidence remains separate.

The held screen comprises eight W4 jobs, all four model shapes in EP and TP, thirteen token counts, four CAAC phases and 100 CUPTI samples per phase (41,600 samples). There are 94 explicit frozen choices and ten previously recorded deterministic defaults; neither routes nor tactics will be retuned. Tokens1/2 remain raw but are excluded from retention.

Evidence: `qualification-summary.json`, `wrap-native-summary.json`, both `qualification-r1/evidence/` and `qualification-wrap/evidence/`, plus `source-audit-wrap.json`. Initial harness-only preflight errors are preserved separately.
