# W4A16 SiTU prefill attribution

**Conclusion:** retained commit `2b8eb9d8` did not introduce a measured K3 prefill regression in its paired experiment. All six primary prefill ratios are positive. It nominally lifts the three published K3 TP prefill deficits; the smaller 8K/16K effects are noisy and must not be presented as dependable improvements. `49c91adf` cannot explain W4A16 losses: it changes only the swap-AB kernel, and every W4A16 publication row was reused unchanged.

This audit replays 3,600 original CUPTI samples (36 phase medians), including raw launch/activity correlations and NVML quartile joins. No reruns or changes to sealed evidence. `receipt.json` contains every original phase median and clock record.

## Primary paired comparison: 49c → 2b8

Each arm latency is the geometric mean of its two 100-sample phase medians, using C–A–A–C. Positive percentages mean the SiTU candidate is faster. Repeat spread is `(max phase median/min phase median − 1)×100`; no samples are excluded.

| K3 shape | Tokens | Before49 (µs) | After2b8 (µs) | Paired change | Before/after spread | Clock-exception quartiles | Observed SM MHz |
|---|---:|---:|---:|---:|---:|---:|---:|
| K3 EP8 | 4096 | 565.999318 | 542.267950 | +4.376318% | 0.880% / 0.086% | 0/16 | 2032–2032 |
| K3 EP8 | 8192 | 996.209029 | 992.139470 | +0.410180% | 1.802% / 6.281% | 5/16 | 1500–2032 |
| K3 EP8 | 16384 | 2008.942359 | 2007.132937 | +0.090150% | 0.354% / 1.751% | 13/16 | 1282–2032 |
| K3 TP8 | 4096 | 718.235368 | 710.646515 | +1.067880% | 0.266% / 0.789% | 1/16 | 1672–2032 |
| K3 TP8 | 8192 | 1286.722007 | 1283.177557 | +0.276224% | 3.710% / 3.580% | 5/16 | 1597–2032 |
| K3 TP8 | 16384 | 2475.844695 | 2464.518684 | +0.459563% | 0.572% / 0.046% | 13/16 | 1275–2032 |

Clock exceptions mean a quartile median differs from2032MHz or a nonzero clock-event reason is present. All144 quartile windows across the nine replayed cells have telemetry; none is missing. All8K/16K primary rows have reason0/4 observations; TP4K has one1672MHz window but reason0 only. EP4K has stable2032MHz/no reasons and both candidate phases are faster than both controls. The prefill aggregate is nominally +1.102582%, not a clock-controlled guarantee.

## Reverse-order diagnostic, kept separate

Only three of the six ACCA diagnostic cells were prefill; the other three were EP16/32/128. None replaces the primary rows or the published table.

| K3 shape | Tokens | Before49 (µs) | After2b8 (µs) | ACCA change | Before/after spread | Clock-exception quartiles |
|---|---:|---:|---:|---:|---:|---:|
| K3 EP8 | 4096 | 554.285471 | 541.580151 | +2.345972% | 3.068% / 0.121% | 0/16 |
| K3 TP8 | 4096 | 705.996205 | 704.586222 | +0.200115% | 1.901% / 1.059% | 0/16 |
| K3 TP8 | 8192 | 1285.005225 | 1277.701735 | +0.571612% | 0.333% / 2.972% | 4/16 |

EP4K stays positive in reverse order, but its control spread increases to3.07%. TP4K is broadly neutral in the repeat and TP8K remains variable. The repeat does not support a prefill regression from SiTU, nor does it establish all small positive values as reproducible speedups.

## Why current red cells are not a SiTU regression

The PR table compares to historical326c4a79 measurements (source-qualified to82254e20), rather than the fresh same-session49 control. These are different comparisons and runtime cohorts.

| K3 TP8 tokens | Historical baseline (µs) | Fresh49 control vs historical | Published2b8 vs historical | Causal49→2b8 |
|---:|---:|---:|---:|---:|
| 4096 | 679.566692 | -5.383845% | -4.373458% | +1.067880% |
| 8192 | 1263.210881 | -1.827211% | -1.556034% | +0.276224% |
| 16384 | 2362.730845 | -4.568697% | -4.130131% | +0.459563% |

The deficit is present before applying SiTU in this matched session. This rules out blaming2b8 for creating those reported prefill losses, but does **not** isolate which earlier commit or cohort difference produced the historic gap. Root/other audit owns02de andbf072 evidence. A variance flag ofFalse in the historical table only means its two per-arm medians are close; it does not exclude clock or cross-session effects.

## Source and inheritance proof

- `49c91adf` changes only `moe_swap_ab_kernel.py` (43+/19−). Its W4 kernel Git blob equals its parent. All104 W4A16 full-row dictionaries in `publication-integer-store/report/cells.csv` equal `publication-w4-tail/report/cells.csv` exactly.
- `2b8eb9d8` is a direct child of49 and changes only `moe_w4a16_kernel.py` (23+/36−), matching qualified hash5e61d045. The paired scaled-tanh calls remain under the existing constexpr SiTU guards.
- Among the four benchmark models only K3 uses SiTU (`beta=4`, `linear_beta=25`). V3/V41 use ordinary SwiGLU; N3U uses ReLU². All78 non-K3 W4 rows are exact dictionary reuse in the current publication. All364 swap rows are source-unaffected.
- Native qualification verifies unchanged resources/LOCAL0, unchanged FC2 and non-SiTU images in the qualified cases, explicit RN packed math, and unchanged scalar FTZ EX2/RCP. Actual FC1 arithmetic counts decrease; local scheduling changes are recorded rather than claimed absent.
- The primary26 had nine negative retention cells, all at4–512 tokens. They remain valid observations; saying “no prefill losses from SiTU” does not erase those losses. The reverse-order EP16/32 cases flip to near-neutral positive, while EP128 remains−0.101%.

Evidence: `evidence/w4-paired-situ-screen/1793379864881706000`, `evidence/w4-paired-situ-acca/1793380968593160000`, `experiments/w4-paired-situ/{source-reuse-proof,integration,retention}.json`, and existing independent source/native/data audit receipts.
