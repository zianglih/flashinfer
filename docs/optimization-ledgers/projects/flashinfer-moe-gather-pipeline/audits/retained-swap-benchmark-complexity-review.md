# Retained swap changes: benchmark and complexity review

Read-only review, 2026-10-30. Optimization work is paused. No GPU execution, source modification, branch edit, or new experiment. Main is clean at `c1ac8ce7341039db65195b99445fcdeb193cf226`.

**Recommendation: keep all three swap changes, for different reasons.** The two `02de` changes qualify as local instruction/ownership simplifications despite neutral timing. The `49c` change needs its measured quantized-prefill benefit to justify its additional source; it has that benefit, with explicit per-token tradeoffs.

| Retained change | Exact source cost | Paired evidence | Decision |
|---|---|---|---|
| `02de`: FC2 bulk commit only in existing writer branch | One indentation change, +1/−1 lines; no added condition, state, argument, helper, or specialization | 140 non-W4 raw cells / 84 retention cells; GM **+0.076%**, 27 negatives. Prefill +0.116%, with substantial repeat/clock variability | **Keep as ownership cleanup.** Do not claim a speedup |
| `02de`: compile-time MMA scale-byte selectors | +4/−3 lines including one explanatory comment; existing private helper/signature unchanged | 30 paired cells; GM **−0.055%**, 13 negatives; decode +0.166%, middle +0.010%, prefill −0.341% | **Keep as invariant-driven instruction simplification.** No broad performance gain established |
| `49c91adf`: integer-carried adjacent nongated FC1 stores | +43/−19 = **+24 lines**; rename `_store` to `_convert`, reuse existing `_store_converted`; epilogue method count stays13 | 104 raw / 88 retention cells, 41,600 samples; GM **+0.643%**. All18 quantized-prefill cells improve, GM **+3.144%** | **Keep for measured quantized-prefill benefit**, not decode or uniform per-token improvement |

All percentages use the original four full C-A-A-C phase medians, `sqrt(C1*C2/(A1*A2))−1`. Tokens1/2 are excluded only from retention where measured. I recomputed these aggregates from the existing CSV rows; no samples/rows were changed or discarded. These isolated experiments must not be multiplied into a claimed combined speedup.

## FC2 writer-owned commit

The commit remains after the existing elected output TMA, inside its existing two-warp writer branch. Nonwriter warps issued no bulk transfer, so their empty commits are removed. Common scratch publication/reuse barriers, read waits and terminal joins remain intact. This is a clearer ownership boundary, with no interface or extra policy cost.

[Native qualification](../validation/swap-writer-r1/RESULTS.md): 20 exact calls /30 native pairs, identical resource counts and LOCAL0; all20 FC1/finalizer pairs have identical cubins. Ten FC2 PTX pairs bypass36 nonwriter commit sites in total. Real writer commits remain; this is executed ownership reduction, not removal of every static commit opcode. The bounded exact suite selected ordinary scheduling; later composed coverage is separate.

The initial K3 EP MXFP4x8 16K result is −4.463% with control repeat spread3.512% and clock exceptions. The [separate diagnostic](../experiments/k3-ep-mx4-prefill/fresh-diagnostic/RESULTS.md) changed sign: CAAC +3.579%, ACCA −1.233%, with1.44–5.09% arm spreads; native FC1 is unchanged. Those results neither prove a win nor erase the original negative. They are insufficient to establish a persistent regression that outweighs this one-indent simplification.

## Static scale-byte selectors

The Python-unrolled MMA descriptor builder already knows `start` and `sf_vec_size`. Both locally constructed scale tensors begin on TMEM words, so `(start // sf_vec_size) %4` replaces runtime address-bit extraction. It uses the current local layout invariant; there is no new parameter, flag, runtime division, synchronization, helper, or specialization axis. The explanatory comment is useful contract documentation.

[Qualification/results](../experiments/static-sf-selector/RESULTS.md): ten exact calls /30 loaded kernels, LOCAL0, including fresh wide K96 coverage. Native shifts/bit manipulation are removed. One MX FC2 signature grows116→118 registers while retaining the existing one-CTA capacity; this is not a universal resource reduction. The [source review](static-sf-peer.md) establishes the selector-field/layout contract.

The largest initial loss is K3 EP MXFP4x8 16K −3.557%, with5.336%/3.237% arm spreads and clock exceptions; the separate diagnostic is +5.148% CAAC /+0.511% ACCA with substantial drift. There is also a genuine small tight N3U TP MXFP4x8 T512 observation: −0.320%, arm spreads0.032%/0.032%, normal clocks. Keep that limitation visible; the recommendation is a small, qualified instruction simplification, not a blanket non-regression claim.

## Integer-carried output stores

This is the only substantial source addition of the three. It joins the two already-converted16-value halves in UInt32 registers, derives the count/copy width from existing static element widths, and reuses the store helper. It adds no public/internal call argument, helper method, autotuning/cache axis, runtime policy branch, shared storage, synchronization or persistent state. The existing fused-atomic branch recasts only there; it is a real compatibility detail, not a new user-facing mode. Gated paths retain their existing geometry. The public alignment/tail contract is unchanged.

Actual output stores halve for quantized payloads: representative FP4 **16×64→8×128 bits**, FP8 **16×128→8×256 bits**; scale stores are unchanged. BF16 per-token still uses16×256-bit stores, so it is not a binary-null control. [Final qualification](../experiments/fc1-integer-store-atomic-fix/qualification-summary.json) selects16 exact calls /20 native pairs, all LOCAL0. The unrelated two-CTA fused FP32 boundary grows122→125 registers; all155 paired measured native configurations retain identical resources. Representative gated native pairs remain identical, not an exhaustive recompile of every reused signature.

[Full results](../experiments/fc1-integer-store-performance/FULL_RESULTS.md): decode +0.054%, middle −0.022% are neutral. Quantized prefill improves in18/18 cells (+0.390% to+5.965%; GM+3.144%), including tight W4A4 gains. Some MX16K arms have3–4% repeat variation, so their individual magnitude is less certain. Overall32/88 retention cells are negative; 17/1,664 clock quartiles have exceptions, none missing.

The per-token losses are real adverse observations, not dismissed as noise:

| N3U EP per-token | Control / candidate geometric latency | Speedup | C / A repeat spread | Clocks |
|---|---:|---:|---:|---|
| 8192 |564.844 /569.325 µs|−0.787%|0.0087% /0.0591%|2032MHz, reason0|
| 16384 |944.519 /949.688 µs|−0.544%|0.1526% /0.0574%|2032MHz, reason0|

Per-token overall is−0.013%; EP prefill−0.313%, TP prefill effectively neutral. The18 consistent quantized-prefill improvements justify the generic +24-line implementation while accepting these sub1% losses. If a zero-regression requirement were imposed, this would fail it; the current instruction is to weigh benefit against interface/source cost. Do not add a per-token rescue policy as part of this review.

## Evidence and current-source binding

- Writer CSV: `evidence/r1-compact/1793358417877966000/report/cells.csv`, filtered to non-W4A16 (the same campaign also tested an unrelated W4 utility change).
- Static selector CSV: `evidence/static-sf-compact/1793358674260782000/report/cells.csv`.
- Integer store CSV: `experiments/fc1-integer-store-performance/combined104/cells.csv`; independent union/raw/resource peer: [combined104 receipt](fc1-integer-store-combined104-peer.json).
- Git objects inspected: `02de7785` and `49c91adf` exact diffs. Swap bytes at02de andbf072 are identical (`788b7f58…`); swap bytes at49c andcurrentc1ac are identical (`482b636a…`). Later retained W4 commits add no swap changes. All three remain present with no drift.
- Public/API additions: **zero**. New tuning/policy axes: **zero**. Epilogue helper count: **13 before and after**. No further experiment is recommended by this review.
