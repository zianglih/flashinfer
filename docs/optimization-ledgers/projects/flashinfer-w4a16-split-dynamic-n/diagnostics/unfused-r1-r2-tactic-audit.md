# Unfused R1/R2 tactic audit and final diagnostic selection

**Queue T8, T4096 and one common-N128-cache T16384 pair after the primary campaign finishes: ten diagnostic measurements total.** This updates the initial R1 plan. No primary measurement is rerun, and no GPU command was launched by this audit.

All saved row caches were SHA256-checked. There is exactly one W4A16 profile for each observed token count; paired inputs, histogram summaries and runner extras match. Tactic columns show FC1 / FC2 MxN and cluster; every row uses K256 and raster-along-M=True.

| Tokens | R1 speedup | R2 speedup | Paired speedup | R1 before tactic | R1 after tactic | R2 before tactic | R2 after tactic |
| ---: | ---: | ---: | ---: | :--- | :--- | :--- | :--- |
| 1 | 1.007555× | 1.020662× | 1.014087× | 128x8 c1x1 / 128x8 c1x1 | 128x8 c1x1 / 128x8 c1x1 | 256x16 c2x1 / 256x16 c2x1 | 128x32 c1x1 / 128x32 c1x1 |
| 2 | 1.014865× | 1.010900× | 1.012880× | 128x8 c2x1 / 128x8 c2x1 | 128x16 c1x1 / 128x16 c1x1 | 128x16 c1x1 / 128x16 c1x1 | 128x8 c1x1 / 128x8 c1x1 |
| 4 | 1.008224× | 1.026297× | 1.017220× | 128x16 c1x1 / 128x16 c1x1 | 128x32 c1x1 / 128x32 c1x1 | 128x16 c1x1 / 128x16 c1x1 | 128x16 c1x1 / 128x16 c1x1 |
| 8 | 0.984404× | 1.006282× | 0.995283× | 128x16 c2x1 / 256x16 c2x1 | 128x8 c2x1 / 128x8 c2x1 | 128x16 c2x1 / 256x16 c2x1 | 128x32 c1x1 / 128x32 c1x1 |
| 16 | 1.007983× | 1.014364× | 1.011168× | 128x8 c2x1 / 128x8 c2x1 | 128x8 c2x1 / 128x8 c2x1 | 128x8 c2x1 / 128x8 c2x1 | 128x8 c1x1 / 128x8 c1x1 |
| 32 | 1.005278× | 1.009694× | 1.007484× | 128x8 c2x1 / 128x8 c2x1 | 128x8 c2x1 / 128x8 c2x1 | 128x8 c2x1 / 128x8 c2x1 | 128x16 c1x1 / 128x16 c1x1 |
| 64 | 1.008902× | 1.011268× | 1.010084× | 256x16 c2x1 / 256x16 c2x1 | 128x16 c1x1 / 128x16 c1x1 | 128x16 c1x1 / 128x16 c1x1 | 128x16 c1x1 / 128x16 c1x1 |
| 128 | 1.012211× | 1.008080× | 1.010144× | 256x16 c2x1 / 256x16 c2x1 | 128x16 c1x1 / 128x16 c1x1 | 256x16 c2x1 / 256x16 c2x1 | 128x16 c1x1 / 128x16 c1x1 |
| 256 | 1.008341× | 1.004958× | 1.006648× | 128x16 c2x1 / 256x16 c2x1 | 128x16 c1x1 / 128x16 c1x1 | 128x16 c2x1 / 256x16 c2x1 | 128x16 c1x1 / 128x16 c1x1 |
| 512 | 1.013148× | 1.005198× | 1.009165× | 128x32 c2x1 / 256x32 c2x1 | 256x32 c2x1 / 256x32 c2x1 | 256x32 c2x1 / 256x32 c2x1 | 256x32 c2x1 / 256x32 c2x1 |
| 1024 | — | — | — | 256x64 c2x1 / 256x64 c2x1 | — | — | — |
| 2048 | — | — | — | 256x64 c2x1 / 256x64 c2x1 | — | — | — |
| 4096 | 1.046514× | 1.050250× | 1.048380× | 256x128 c2x1 / 256x128 c2x1 | 256x192 c2x1 / 256x192 c2x1 | 256x128 c2x1 / 256x128 c2x1 | 256x192 c2x1 / 256x192 c2x1 |
| 8192 | 1.093088× | 1.081176× | 1.087116× | 256x128 c2x1 / 256x128 c2x1 | 256x128 c2x1 / 256x128 c2x1 | 256x128 c2x1 / 256x128 c2x1 | 256x128 c2x1 / 256x128 c2x1 |
| 16384 | 0.987259× | 1.064290× | 1.025051× | 256x128 c2x1 / 256x128 c2x1 | 256x128 c2x1 / 256x128 c2x1 | 256x192 c2x1 / 256x192 c2x1 | 256x192 c2x1 / 256x192 c2x1 |

## What repeats establish

- **T8192:** 1.093088× / 1.081176×, combined **1.087116×**. Both GEMMs use M256/N128, cluster2x1, in all four captures. The large gain has consistent direction and identical full tactics; no additional fixed-tactic measurement is needed now.
- **T4096:** 1.046514× / 1.050250×, combined **1.048380×**. Both repeats choose baseline M256/N128 and candidate M256/N192, cluster2x1. The gain is consistent but remains confounded with a stable tile change. This is the main attribution diagnostic.
- **T8:** 0.984404× / 1.006282×, combined **0.995283×**. Baseline keeps FC1 M128/N16 + FC2 M256/N16, cluster2x1. Candidate switches from M128/N8 cluster2x1 in R1 to M128/N32 cluster1x1 in R2. Direction changes and candidate selection changes; the R1 crossover checks whether its slightly losing tactic has a source regression or merely loses against the original AUTO choice.
- **T16384:** 0.987259× / 1.064290×, combined **1.025051×**. R1 matches M256/N128 on both sources; R2 matches M256/N192 on both. The R2 gain is not a repeat of the R1 fixed-N128 comparison. Add one pair using the saved baseline R1 N128 cache on both sources. The source-arm native cache wrapper makes this bounded probe inexpensive, and it directly checks the unresolved N128 observation. Do not claim every fixed tactic improves.

## Bounded crossover commands

```bash
cd /workspace/flashinfer-w4a16-split-dynamic-n
bash scripts/run_fixed_diagnostics_r1.sh 8 4096 16384
```

T8 and T4096 have four source/cache combinations each: baseline source with baseline cache, candidate source with baseline cache, candidate source with candidate cache, baseline source with candidate cache. T16384 adds baseline and candidate with the same baseline R1 appendix N128 cache (two measurements), for ten total. The retained R1 cache files are reused unchanged. Each process uses do_autotune=False and the native cold-L2 CUPTI100 timer with ten warmups.

Every invocation runs through `bash "$project/scripts/with_arm_cache.sh" "$arm" "$project/.venv/bin/python" ...`, from the project root, preserving the matching native JIT build directory. The runner refuses existing output/log paths. All files go to `diagnostics/r1-crossover/`; primary AUTO medians are not replaced or pooled with diagnostics.

For each source/cache pair, compare source heads/hashes, cache SHA256, actual selected full tactic, input shapes, histogram and software before deriving a ratio. T4096 candidate-cache results determine whether dynamic N improves the N192 kernel that AUTO selects; baseline-cache results determine the change under the old N128 choice. T8 baseline-cache results test the original mixed one-/two-CTA tactic; candidate-cache results test its R1 all-one-CTA N8 choice.

Fused results are still pending at this audit. These three rows are the bounded diagnostic set; no further sweep is requested. Retention can reasonably weigh the repeated 8.7% N128 gain at T8192 against a smaller T16384 tradeoff. Report the measured tradeoff and its uncertainty rather than requiring uniform improvement or saying all regressions are resolved.

Raw full tactics, latency values, original cache keys and source/cache hashes: `unfused-r1-r2-tactic-audit.json`.
