# Retained W4 prefill regression trace

The 15 negative rows below compare current candidate timings with the historical full run measured at `326c4a79`, whose production source was verified equivalent to PR9 parent `82254e20`. They are not fresh commit-by-commit comparisons. The public external column **W4A16 before PR** instead uses the older `old-nemo-df20fa7fa317` source snapshot and its old layout/native choices (`swap_ab=false`). It is a different denominator.

| Model/placement | Tokens | 02de vs historical parent | bf072 vs same | 49c vs same | 2b8/current vs same | Current vs external old W4 | bf072 paired effect | 2b8 paired effect |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V3 EP | 4096 | -2.413% | -2.413% | -2.413% | -2.413% | +0.470% | unchanged | unchanged |
| V3 EP | 8192 | -5.545% | -5.545% | -5.545% | -5.545% | -2.198% | unchanged | unchanged |
| V3 EP | 16384 | -0.565% | -0.565% | -0.565% | -0.565% | +4.353% | unchanged | unchanged |
| V41F EP | 16384 | -1.882% | -1.882% | -1.882% | -1.882% | +1.430% | unchanged | unchanged |
| V41F TP | 4096 | -0.816% | -1.848% | -1.848% | -1.848% | +14.386% | -0.284% | unchanged |
| V41F TP | 8192 | -2.783% | -0.777% | -0.777% | -0.777% | +12.922% | +2.895% | unchanged |
| K3 TP | 4096 | -0.205% | +0.354% | +0.354% | -4.373% | +19.388% | -0.241% | +1.068% |
| K3 TP | 8192 | -0.775% | +1.667% | +1.667% | -1.556% | +24.216% | +3.591% | +0.276% |
| K3 TP | 16384 | -0.283% | -0.131% | -0.131% | -4.130% | +18.961% | -0.746% | +0.460% |
| N3U EP | 4096 | -1.824% | -1.824% | -1.824% | -1.824% | +0.076% | unchanged | unchanged |
| N3U EP | 8192 | -3.360% | -3.360% | -3.360% | -3.360% | -0.801% | unchanged | unchanged |
| N3U EP | 16384 | -2.855% | -2.855% | -2.855% | -2.855% | -3.297% | unchanged | unchanged |
| N3U TP | 4096 | -0.652% | -1.227% | -1.227% | -1.227% | +12.571% | -0.563% | unchanged |
| N3U TP | 8192 | -2.236% | -3.733% | -3.733% | -3.733% | +20.385% | -0.293% | unchanged |
| N3U TP | 16384 | -2.726% | -3.329% | -3.329% | -3.329% | +15.599% | -0.578% | unchanged |

49c changes only the swap-AB kernel; every W4 publication row is exactly identical before/after. Seven currently negative rows retain the original 02de measurements unchanged through all follow-ups. The five V41F/N3U TP rows were last measured for bf072; the three K3 TP rows were last measured for 2b8. Comparing those later observations with old candidate observations conflates source changes with run-to-run changes.

## bf072: all affected prefill cells, paired CAAC

Each entry below is the original 02de control versus the exact bf072 patch in one four-phase campaign. Percent is `100*(sqrt(C1*C2/(A1*A2))-1)`. Repeat spread is `(max/min-1)*100`; two repetitions are not a confidence interval. Clock exceptions mean a non-2032 median or a nonzero reason in a quartile; transient clock dips can exist even with zero such exceptions.

| Placement | Tokens | C1 / C2 µs | A1 / A2 µs | Paired effect | C/A repeat spread | Clock exceptions /16 (missing) | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| K3 TP8 | 4096 | 675.540 / 675.541 | 668.404 / 686.053 | -0.241% | 0.000% / 2.640% | 2 (0) | Candidate phases straddle controls; ambiguous. |
| K3 TP8 | 8192 | 1292.921 / 1281.320 | 1220.680 / 1264.697 | +3.591% | 0.905% / 3.606% | 6 (0) | Both candidates faster; substantial variation/clocks. |
| K3 TP8 | 16384 | 2385.344 / 2311.616 | 2378.865 / 2352.881 | -0.746% | 3.189% / 1.104% | 11 (0) | Control drift exceeds loss; ambiguous. |
| N3U TP8 | 4096 | 545.428 / 543.957 | 550.597 / 544.965 | -0.563% | 0.271% / 1.033% | 0 (0) | Observed small loss; candidate spread exceeds effect, phases overlap. |
| N3U TP8 | 8192 | 951.480 / 958.312 | 958.520 / 956.872 | -0.293% | 0.718% / 0.172% | 1 (0) | Overlapping phase ranges and a control clock exception. |
| N3U TP8 | 16384 | 1946.816 / 1950.591 | 1954.735 / 1965.344 | -0.578% | 0.194% / 0.543% | 12 (0) | Both candidates slower than both controls; small adverse signal, clock affected. |
| V41F TP4 | 4096 | 559.458 / 578.978 | 557.058 / 584.787 | -0.284% | 3.489% / 4.978% | 0 (0) | Large overlap/variation; ambiguous small loss. |
| V41F TP4 | 8192 | 1006.851 / 1021.429 | 981.381 / 989.797 | +2.895% | 1.448% / 0.858% | 5 (0) | Both candidates faster; clocks/variation limit magnitude. |
| V41F TP4 | 16384 | 1909.272 / 1917.257 | 1902.521 / 1907.898 | +0.423% | 0.418% / 0.283% | 12 (0) | Small observed gain; clock affected. |

The six bf072 prefill losses are all below 0.75%. None satisfies the ledger’s descriptive “both repeat spreads ≤0.5%” criterion; this criterion is not a significance test. N3U TP16K is the clearest small adverse direction (all candidate phase medians exceed all controls), but 12/16 clock quartiles are affected. It is inappropriate either to erase these losses or claim they prove the larger historical 1–5% gaps. The nine prefill cells average +0.456%, which the original retention note explicitly did not claim as a dependable gain.

The full 39-cell bf072 CAAC was replayed from 15,600 CUPTI intervals and phase medians, with source/hash, same-GPU, route/tactic/cache-hit and LOCAL0 guards checked. All original records are unchanged.

## Evidence

- [Current retained comparison](../publication-w4-paired-situ/report/table.md) and [all current rows](../publication-w4-paired-situ/report/cells.csv).
- [Initial 02de rows](../publication/report/cells.csv); [bf072 rows](../publication-w4-tail/report/cells.csv); [49c rows](../publication-integer-store/report/cells.csv).
- [bf072 causal table](../experiments/w4-tail-dequant/combined39/table.md), [retention explanation](../experiments/w4-tail-dequant/RETENTION.md), [initial raw leaf](../evidence/w4-tail-dequant-screen/1793368574438182000/data/), [remaining raw leaf](../evidence/w4-tail-dequant-remaining/1793369332076642000/data/).
- [Initial clock quartiles](../evidence/w4-tail-dequant-screen/1793368574438182000/report/clock-quartiles.json), [remaining clock quartiles](../evidence/w4-tail-dequant-remaining/1793369332076642000/report/clock-quartiles.json).
- [02de fresh compact CAAC](../evidence/r2-w4-compact/1793358674260664000/report/table.md); only 16K overlaps prefill, so it cannot causally assign 4K/8K historical gaps.
- [2b8 primary paired evidence](../publication-w4-paired-situ/paired-situ-causal/table.md), [separate ACCA](../publication-w4-paired-situ/paired-situ-acca/table.md).
- [External EP baseline rows](../publication-w4-paired-situ/external/ep/summary-cells.csv), [external TP rows](../publication-w4-paired-situ/external/tp/summary-cells.csv).
- [Machine-readable trace with exact source paths](w4-prefill-regression-trace.json).

## Commit attribution boundary

- **02de:** the seven unchanged red rows are already present in its first full publication. Its fresh 16K-only prefill CAAC shows V3 EP −1.130%, V41F EP −0.610%, N3U EP −1.333%, with control/candidate repeat spreads 3.008/4.926%, 1.217/1.864%, and 1.291/4.865%, respectively, and clock exceptions in every row. There is no fresh paired 4K/8K observation in that screen. The larger historical deficits therefore remain observed gaps, not isolated commit effects.
- **bf072:** the six small negative paired observations above are the only directly adverse prefill evidence among these follow-ups. Fresh controls already explain much of the larger historical gap; no claim that this commit caused the full red-cell percentage is justified.
- **49c:** no W4 source change and all 104 W4 row dictionaries exactly reused.
- **2b8:** all six K3 primary prefill paired effects are positive. The fresh 49 controls for TP4K/8K/16K were already −5.384/−1.827/−4.569% against the old parent baseline; candidate values improve them nominally to −4.373/−1.556/−4.130%. Its separate ACCA prefill observations are positive too. The 8K/16K gains are small/noisy, but the data does not support blaming SiTU for creating those deficits. See [the independent K3 source/raw audit](w4-prefill-attribution-situ/RESULTS.md).

The public external old-W4 prefill column has a different set of five negatives: V3 EP8K, K3 EP8K/16K, and N3U EP8K/16K. Every TP prefill comparison against that older layout remains positive (including all eight TP cells red against the newer historical PR9-parent control). Do not mix these two baselines.


## Fresh same-session 822 → 02de prefill isolation (completed follow-up)

The earlier historical tables and audit above are preserved unchanged. The new same-session run supplies the previously missing paired 4K/8K coverage: actual immutable **82254e20 control** versus the exact **02de7785 source snapshot**, all four models × EP/TP × tokens4096/8192/16384. The source changes used by W4 are confined to the initial scale-selector utility; the other changed swap kernel is not invoked. Both arms use the same current recovery release C++ cohort, frozen native choices/routes, and normal persistent cache; old native libraries were not restored.

All24 CAAC cells completed: **9,600 CUPTI samples**,96 phase medians,120 loaded LOCAL0 function records,48 unchanged stage-resource configurations and80 recorded-default stage/resource joins. Full source inventories and current ELF/Ninja hashes remained unchanged before/after. **GM +0.433710%,7negative**;100/384 clock quartiles have a non2032 median or nonzero reason, none missing. Every raw phase and clock window is retained. No threshold converts the adverse observations into zero or establishes statistical significance.

| Model | EP/TP | Mode | 4096 | 8192 | 16384 |
|---|---|---|---:|---:|---:|
| kimi-k3 | EP8 | CuteDSL W4A16 | -1.445% | +2.037% | -1.464% |
| kimi-k3 | TP8 | CuteDSL W4A16 | -1.248% | +0.826% | +0.731% |
| nemo3-ultra | EP8 | CuteDSL W4A16 | -0.058% | +0.598% | -0.149% |
| nemo3-ultra | TP8 | CuteDSL W4A16 | +0.097% | +1.612% | +0.595% |
| v3 | EP8 | CuteDSL W4A16 | -0.003% | +0.910% | +1.506% |
| v3 | TP8 | CuteDSL W4A16 | +0.063% | +1.938% | +0.465% |
| v41-flash | EP4 | CuteDSL W4A16 | +0.971% | -0.642% | +0.595% |
| v41-flash | TP4 | CuteDSL W4A16 | +1.161% | +1.311% | +0.113% |

This does not reproduce the large historical V3/N3U prefill deficits as an initial-selector commit effect. The larger historical red percentages remain cross-session gaps, not isolated regressions. All seven fresh negative cells have FC1/FC2/combine durations and critical extensions tabulated in the [full fresh report](../experiments/w4-initial-selector-prefill/RESULTS.md) and [phase/clock details](../experiments/w4-initial-selector-prefill/negative-details.md).

K3 EP16K was the strongest adverse primary row because both candidate phase medians exceeded both controls. One authorized reverse-order block on the **same GPU1 UUID** was run, with unchanged sources/route/tactic/cache/clock policy and400additional CUPTI samples. It is separate evidence, not a replacement or pooled estimator:

| Block | Chronological phases and E2E medians (µs) | Paired effect | C/A repeat spread | Clock exceptions /16 | FC1/FC2/combine duration delta (µs) |
|---|---|---:|---:|---:|---:|
| Primary CAAC | C1987.040 / A2021.729 / A2040.240 / C2015.520 | −1.464026% | 1.433/0.916% | 11 | +14.024 / +13.752 / +5.208 |
| Separate ACCA | A1996.591 / C2012.943 / C1999.137 / A1988.496 | +0.676962% | 0.691/0.407% | 13 | −14.552 / +0.585 / −0.640 |

Component deltas are arithmetic means of each arm's phase medians, not additive E2E estimators. Primary FC1/FC2 critical extensions grew14.048/13.768µs; reverse FC1/FC2 extensions changed−14.568/+0.681µs. The opposite signs and different clock trajectories leave this small source-local attribution **unresolved**. The positive repeat does not erase the initial all-candidate-slower observation. No additional W4 repeat, clock lock, tuning, or source change followed.

The combined attribution remains: **02de** does not reproduce the broad historical losses in this fresh24 matrix, with K3 EP16K unresolved; **bf072** retains six small adverse prefill observations (−0.24% to−0.75%) with their repeat/clock limits; **49c** changes no W4 code and reuses all104 W4 rows; **2b8** has positive own six K3 primary prefill comparisons, with noisy magnitude explicitly limited. The external old-W4 denominator remains distinct from the historical PR9-parent control.

Evidence and integrity bindings:

- [Primary24 raw data](../evidence/w4-initial-selector-prefill/1793388462716534000/data/), [all phase medians](../evidence/w4-initial-selector-prefill/1793388462716534000/report/table.md), [independent root raw replay](w4-initial-selector-data-root.json), [author receipt](../experiments/w4-initial-selector-prefill/result-receipt.json).
- [Separate ACCA raw data](../evidence/w4-initial-selector-k3-ep16k-acca/1793389072726146000/data/), [ACCA result/clock table](../experiments/w4-initial-selector-prefill/reverse-k3-ep16k/RESULTS.md), [ACCA receipt](../experiments/w4-initial-selector-prefill/reverse-k3-ep16k/result-receipt.json).
- [Append-only audit binding](w4-prefill-regression-fresh-addendum.json) preserves the earlier table prefix and binds both complete blocks and the independent primary replay.

Main remains clean2b8; no production/PR/publication changes. Our completed campaign entries were removed from the active registry without changing other owners' work. GPUs1–4 from the primary and GPU1 from the repeat were released after their respective source/cache/idle postflights.
