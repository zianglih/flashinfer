# Remaining b139 gaps and next bounded qualification

This audit uses the full current b139 swap refresh and unchanged6be W4 evidence. Historical baselines are reused across GPU instances: small repeat spread is a stability observation, not a causal source comparison. `remaining-d35-gaps.csv` preserves all396 displayed rows, including60 negative cells; `external-gap-ranking.json` preserves every supported displayed external comparison.

The largest repeat-stable candidate gaps versus d35 remain quantized FC1 EP prefill. At16K: K3 W4A4 is−10.58% /+84.95µs (candidate spread0.90%); N3U W4A4−11.67% /+68.04µs (0.04%); N3U per-token−7.23% /+66.33µs (0.09%); V3 W4A4−8.46% /+43.96µs (0.02%). The larger W4 V41F16K loss has2.20% repeat spread and does not motivate another W4 source change by itself.

Current component evidence (`current-components.json`; medians of disjoint completion-extension samples, averaged across the two phases) locates useful work without claiming removable time:

| Case | E2E µs | FC1 exposed µs | FC2 exposed µs | Combine exposed µs |
|---|---:|---:|---:|---:|
| K3 EP16K W4A4 |803.2|469.8|228.1|70.2|
| N3U EP16K W4A4 |582.8|313.8|187.2|53.9|
| V3 EP16K W4A4 |519.4|227.7|118.2|84.3|
| V3 TP16K MXFP8 |1333.3|467.1|493.4|329.7|
| N3U TP16K W4A4 |1182.3|475.1|408.8|270.0|
| K3 TP16 MXFP4x8 |122.9|75.3|28.1|5.8|

Component medians need not sum exactly to the E2E median. No TRTLLM/non-swap per-kernel timeline is available from the saved raw results. Their largest gaps are V3 TP16K MXFP8 versus old fused MXFP8 (+214µs), V3 TP8K MXFP4x8 versus old fused (+136µs), and N3U TP16K per-token/W4A4 versus TRTLLM (+121/+117µs). The exposed329.7µs V3 TP MX combine makes fused versus unfused attribution especially important; it is not evidence that all214µs belongs to FC1.

## Selected minimum change

A balanced tree inside the existing16-value `_absmax` helper is the smallest distinct dependency experiment. Current compiler output already uses eight fused `FMNMX3` sites, so the claim is reduced dependence depth, not eliminating32 unoptimized instructions. It affects all quantized FC1 formats/activations using block-scale generation; per-token BF16 intermediate kernels are unaffected controls. The max function is order-independent with final positive-zero/NaN filtering, and no ownership, scratch, barrier or tactic changes are needed. Read `DESIGN.md` for source references and gates.

The current N3U iKET trace shows epilogue load/transpose scopes at37–43% of instrumented epilogue time; rejected native-TMEM layout changes were slower. Therefore a compact scheduling/dependency improvement inside the retained ownership is preferred to repeating native layout, live-group pruning, extra warpgroup budgets or gather transport changes.

A separate promising source precedent is Rubin's phase-interleaved32x32 transpose (two16x32 fragments). Root owns that isolated experiment. Its proof is recorded in `DESIGN.md`; it changes issue order without adding shuffles or changing stores. The minimal tree will not address per-token BF16 gaps, and no broad closure claim is made.

Qualification has begun on frozen b139/control and tree/candidate, using39 existing exact cases plus paired prelaunch resources. Only after actual codegen proves no new spills and a useful dependency shape should a fixed-winner CAAC screen cover all four models EP/TP, three affected types, smallN16 and large prefill, plus per-token controls. No kernel timing has been launched for this audit.
