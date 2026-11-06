# Remaining gaps at 374ed4c0

The main priorities are FC1 prefill production and the short-K TP output chain. No new GPU run, source edit, clock change, or publication edit was made for this audit. Current data is the full 468-cell AA refresh; historical d35, non-swap and TRTLLM timings are reused.

## Ranking and uncertainty

`all-comparisons.csv/json` retains all 1,248 comparisons, including 1/2-token rows. Among the 1,056 displayed comparisons (tokens >=4), 148 are negative: 64 versus d35, 41 versus TRTLLM, 32 versus legacy non-swap, and 11 versus pre-PR W4A16. Nothing negative is dropped. There are 82 repeat-consistent material gaps; 18 negative comparisons have candidate or baseline phase spread >2%; the remaining 48 are small or their phase envelopes overlap.

For ranking only, a material stable gap requires both repeat spreads <=2% and the fastest candidate phase still >1% slower than the slowest historical baseline phase. This does not make cross-node comparisons causal. `required_gain_percent` is current/baseline−1; the public table uses baseline/current−1. Clock ranges below are sampled quartile medians, not frequency corrections or proof about unsampled execution.

| Representative stable gap | Reference | Current / baseline us | Excess us | Required gain |
|---|---|---:|---:|---:|
| V3 TP8, MXFP8, 16384 | Legacy MXFP8 † | 1369.83 / 1119.33 | 250.50 | 22.38% |
| N3U TP8, W4A4, 16384 | TRTLLM W4A4 | 1212.25 / 1065.53 | 146.72 | 13.77% |
| V3 TP8, MXFP4x8, 8192 | Legacy MXFP4x8 † | 688.47 / 543.22 | 145.24 | 26.74% |
| V3 TP8, MXFP8, 16384 | TRTLLM MXFP8 | 1369.83 / 1268.18 | 101.65 | 8.02% |
| N3U TP8, PER-TOKEN, 16384 | TRTLLM PER-TOKEN | 1762.43 / 1664.10 | 98.33 | 5.91% |
| N3U EP8, W4A4, 16384 | Legacy W4A4 | 595.15 / 503.09 | 92.06 | 18.30% |
| N3U EP8, W4A4, 16384 | d35 | 595.15 / 514.72 | 80.43 | 15.62% |
| K3 EP8, W4A4, 8192 | d35 | 515.61 / 466.68 | 48.93 | 10.48% |
| V3 EP8, W4A4, 16384 | d35 | 522.92 / 475.47 | 47.45 | 9.98% |
| V41F TP4, W4A4, 16384 | d35 | 1046.08 / 1030.13 | 15.94 | 1.55% |
| K3 TP8, MXFP4x8, 16 | d35 | 120.85 / 107.32 | 13.52 | 12.60% |
| V3 EP8, W4A16, 8 | d35 | 69.62 / 65.80 | 3.82 | 5.80% |

† These old MX backends require fused finalize. The current swap-AB chain is unfused with ordered combine. This is a structural comparison boundary, not evidence that the whole difference comes from MMA or TMA. TRT columns have no legacy-fused marker; that does not describe TRT's internal kernel fusion.

N3U TP W4A4/PER-TOKEN and N3U EP W4A4 representative windows all sampled 2032 MHz with reason mask0. V3 TP16K MXFP8 is repeat-stable but sampled 1710–2032 MHz; use V3 TP8K MXFP4x8 (2032 MHz, mask0) as a cleaner diagnostic point. Full per-cell clock context is in `all-comparisons.json`.

The largest unstable negative against d35 is K3 EP16K W4A4 (+112.25 us, +15.63% required), with candidate/baseline phase spreads 2.69/3.08%. V41F EP16K W4A4 (+41.31 us) has 3.40% candidate spread. They remain in `unstable-negative.csv`, not silently filtered. W4A16 prefill has no robust material regression against d35; its meaningful residual gaps are a few microseconds in decode. The running W4 iKET investigation remains separate.

## Current critical spans

These are arithmetic means of disjoint completion extensions from all 200 CUPTI samples per cell. They sum to mean end-to-end duration; overlapping kernel durations are never added. A kernel's duration includes PDL waiting, so an exposed extension is timeline accounting rather than an isolated computational cost or guaranteed removable time. Exact durations, overlaps, current tactics, per-phase medians and clock context are in `components.json`.

| Workload | Mean E2E us | FC1 exposed | FC2 exposed | Intermediate quant exposed | Combine exposed |
|---|---:|---:|---:|---:|---:|
| N3U EP16K W4A4 | 595.20 | 325.59 | 187.49 | — | 53.96 |
| K3 EP8K W4A4 | 516.11 | 305.84 | 134.51 | — | 37.42 |
| V3 EP16K W4A4 | 523.27 | 229.99 | 119.86 | — | 83.14 |
| V41F EP8K W4A4 | 415.43 | 217.15 | 123.55 | — | 43.40 |
| N3U TP16K W4A4 | 1212.30 | 493.84 | 419.77 | — | 270.30 |
| N3U TP16K PER-TOKEN | 1762.50 | 534.28 | 451.70 | 446.99 | 281.12 |
| V3 TP8K MXFP4x8 | 689.90 | 239.11 | 248.85 | — | 172.83 |
| V3 TP16K MXFP8 | 1356.84 | 482.24 | 501.51 | — | 330.11 |
| V41F TP16K W4A4 | 1046.06 | 419.50 | 380.04 | — | 201.26 |
| K3 TP16 MXFP4x8 | 120.84 | 73.60 | 28.22 | — | 5.67 |
| N3U TP32 MXFP4x8 | 123.95 | 62.65 | 45.65 | — | 6.92 |
| V3 EP8 W4A16 | 69.69 | 47.36 | 13.84 | — | 2.45 |

Remaining span is routing and initial quantization. There are effectively no uncovered inter-kernel gaps in these representative samples. This argues against generic host-launch-gap work or simply moving an already-early PDL signal.

## Prioritized mechanisms

1. **FC1 prefill gather/accumulator production.** This is the clearest regression versus the previous split backend. Current N3U EP16K uses FC1 M512/N128 and FC2 M256/N128, whereas the saved d35 diagnostic used FC1 M256/N128 and FC2 M512/N128. Current FC1 exposes325.59 us versus historical224.39 us; deleting prepare saves19.51 us, and FC2/combine stay within about1 us. Route hashes and quantization recipe match. This cross-node, different-native-tile comparison explains the location of the remaining gap, not its transport-only cause. The earlier same-tile d35→7106 diagnostic isolates a +222.97 us FC1 increase and −19.51 us prepare savings with other tails unchanged; it is an older implementation, not a current matched-tile result. Next useful evidence is current M512 iKET: producer issue, MMA gather wait, weight-ready wait and accumulator/epilogue overlap. Do not redo the old M256-only trace and call it current. See `historical-n3u-comparison.json` and `../ncu-n3u-prefill/RESULTS.md`.
2. **Short-K TP FC2 plus output chain.** FC2+combine exposes519–832 us in the V3 MX examples. Current V3 TP FC2 reduces K256 in only two K128 stages; N3U/V41F NVFP4 reduce K640/K576 with a short final stage. Initialization, inter-work-tile reuse, scale publication and output drain become relatively expensive. The K tail is already peeled at compile time, and MMA only issues the valid tail; simply eliminating nominal padded MMA is not a new optimization. Existing stage capacity deliberately spans successive work tiles, so clamping it to K tiles is unsafe for latency hiding. First separate FC2 MMA/scale-ready/epilogue waits with current-tactic iKET; avoid another tactics axis or a fixed shape rule.
3. **Intermediate per-token quantization still matters.** N3U TP16K has446.99 us of exposed quantization,25.4% of the chain, after the earlier640.55→446.77 us width improvement. FC2 overlaps only its startup portion; moving the PDL signal alone cannot eliminate data dependence. Current K640 uses64 threads for40 SF blocks and still executes a multiwarp row reduction. A future ownership/lifetime change must preserve register retention, exact4over6 and routed-hole semantics. A blanket32-thread register-budget policy already failed due wide-row spills; do not repeat it. Ordinary/per-token native CLC flags differ, so their FC1/FC2 timing difference is not a quantizer-only causal comparison.
4. **Sparse decode SF work is a smaller but clean target.** K3 TP16 MXFP4x8 exposes73.60 us FC1, while the whole deficit to d35 is13.52 us. RouteN16 still has a128-row physical SF block and predicated per-thread copy work. The parent's current SF live-row audit addresses this exact signal. Avoid reviving payload live-group loops or row-outer scheduling: both introduced recurring control/shuffle costs and were rejected. No duplicate experiment is proposed here.
5. **Combine is visibly expensive but not yet a new instruction hypothesis.** TP combine is19–25% of the chain and is almost entirely exposed, which can exceed the old fused-MX gap. This makes legacy-fused comparisons a poor basis for attributing all loss to the new gather pipeline. Wide256, vector-outer, geometry, selective-metadata and cache-handoff combine variants have already failed. Revisit only with a distinct measured mechanism, e.g. changed no-permute cache contention, not another blind vector-width change. No evidence here establishes such a new mechanism.

All1,088 loaded MoE records in the fresh campaign have LOCAL_BYTES=0. Spills are not the first hypothesis for these kernel winners. This says nothing about every explicit quantizer recipe.

## Do not repeat without a new mechanism

- `../cpasync-payload/RESULTS.md`: four-warp cp.async replacement regressed prefill9.92% and all affected dtypes overall; keep Gather4.
- `../live-groups/RESULTS.md`, `../live-groups-row-outer/RESULTS.md`: avoided padded payload work did not compensate for per-K dynamic loops/shuffles/issue overhead.
- `../swap-gather-taskguard/RESULTS.md`: full-group compile-time proof already DCEs; SASS was byte-identical.
- `../swap-gather-unsigned/RESULTS.md`, `../swap-warpindex/RESULTS.md`, `../swap-mma-election/RESULTS.md`: superficial arithmetic/election rewrites increased instructions or produced no benefit.
- `../prefetch/RESULTS.md`: descriptor prefetch was not retained. Current weight startup prefetch and operand staging must remain intact.
- `../per-token-register-width/RESULTS.md`: blanket narrower rows introduced96–128 B stacks and9.83–19.75% regressions for wide rows. `../per-token-warp-reduce/` retains only the independent one-warp synchronization bypass.
- `../../../optimization-20261028/tp-small-gemm-round/prepare-combine-next-audit/RESULTS.md`, `../../../optimization-20261028/post-hybrid-polish/prepare-combine-audit/RESULTS.md`, `../../../optimization-20261028/warp-polish/epilogue/PROFILING.md`: rejected combine variants listed above.

`baseline-component-inventory.json` covers all118 raw scoreboard baseline files: none contains CUPTI activity timelines. No TRT/non-swap stage attribution is fabricated from end-to-end timings. The separate historical d35 N3U diagnostic is the only baseline component comparison used here. There are156 unsupported raw external rows (132 displayed): SiTU limitations and V41F TP MX intermediate-alignment limits remain N/A.
