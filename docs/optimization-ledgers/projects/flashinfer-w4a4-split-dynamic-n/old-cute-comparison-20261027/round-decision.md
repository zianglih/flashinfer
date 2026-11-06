# Completed performance round

Retained and pushed: `7ae6244de4ad60d92b6341f8f04dc73d2b1b0549` on [PR7290](https://github.com/flashinfer-ai/flashinfer/pull/7290). The canonical checkout is clean. The PR body contains the raw old/current comparisons and the retained change's bounded validation; readback and an independent audit pass.

## Old/current comparison

Four models (V3 EP8, V4.1-Flash EP4, Kimi K3 EP8, Nemotron-3 Ultra EP8) and four formats. Current is unfused. Old NVFP4 and per-token NVFP4 are unfused; old MX uses its native fused path where unfused is unavailable. Old K3 MX is unsupported. W4A16 is excluded.

Primary measurements remain attributed to old `002529e1` and current `0b7fe901` (kernel-identical to benchmark-only `d02c487a`), not to the later packed-scaling commit. There are 208 cells, 182 paired comparisons and 26 current-only K3 MX cells, with 78,000 raw samples. Tokens 1/2 are shown but excluded from retention.

| Format | Decode speedup | Prefill speedup |
|---|---:|---:|
| NVFP4 W4A4 | +12.94% | −1.94% |
| Per-token NVFP4 | +27.38% | +24.41% |
| MXFP8 | +11.67% | −0.88% |
| MXFP4x8 | +29.11% | +3.87% |
| All comparable cases | +20.00% | +6.51% |

All 112 comparable decode cells improve. Individual prefill gaps remain; the largest standard NVFP4 gap is Nemotron 16K at −12.83%. No claim is made that those gaps are closed. See [full report](benchmark-report.md), [signed table](speedups.md), and [raw samples](raw-samples.csv).

## Retained instruction cleanup

Pair the existing per-token FC2 FP32 scale products using `mul_packed_f32x2`. The lane map and scalar scale shuffles are unchanged. This removes 64–256 non-NOP instructions in each of six tested FC2 specializations, adds four net source lines, and introduces no policy, tactic axis, buffer, layout or synchronization change.

Eighteen paired exact output checks pass, with no spills. Six FC1 executable sections are identical. Eight native C/A/A/C cells across all four models contain 3,200 samples. Timing is neutral overall (1.000217×), with V4.1 prefill −0.688% and Nemotron prefill +0.302%. Decode bypasses the changed path, and K3 prefill drift prevents a gain claim. This is retained for instruction efficiency, accepting the small prefill tradeoff, not as an end-to-end speedup.

[Exact/codegen review](bulk-scale-pairs/independent-review.md), [raw timing review](bulk-scale-pairs/independent-timing-review.md), [retention receipt](bulk-scale-pairs/retention.json). Scoped pre-commit passes; this round does not add broad sanitizer or full-suite coverage.

## Rejected alternatives

- One-CTA channel reuse: loses in all four measured wide-prefill cases.
- Half-grid PDL preparation: neutral/slower; Nemo NVFP4 prefill loses 1.62%.
- Destination-linear scale stores: MXFP8 prefill loses 5.04%.
- Existing Nemo N256 tactic: loses 5.75% versus its native N128 winner; no tuning axis or shape override added.
- Balanced amax tree: no instruction-count reduction, neutral decode and Nemo NVFP4 16K −0.895%.
- Delayed FC2 bulk drain: correct in bounded checks, but gains do not repeat; reject the extra entry/tail work.
- FC1 protected-prefix buffering: bounded exact/codegen checks pass after avoiding a spill, but four completed timing cells average −0.93%, including Nemo per-token 4096 −2.54%. The twelve-cell plan stopped early; the incomplete next cell is excluded. Extra code and registers are not justified.

These decisions keep the simpler production pipeline. No rejected change is in the PR. Helpers, raw data, profiles, source receipts and persistent native/DSL compilation caches remain local or in cluster storage; completed candidate source copies are removed after verification. All eight GPUs are idle in `final-gpu-status.log`.
