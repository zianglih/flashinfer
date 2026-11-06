# Fresh cumulative W4 prefill: 82254e20 → c1ac8ce7

All 24 fresh cells yield **-0.4617%** geometric-mean speedup, with **12/24 negative cells** and a range of **-5.5650% to +2.3315%**. EP is -0.7403%; TP is -0.1823%. This does not establish a broad tight prefill loss or isolate a causal commit; the adverse observations remain included.

The immutable full 13,245-file arms equal Git822 and retained c1ac, with exactly four source files changed. Eight original W4 jobs use the same frozen routes and public choices (14 explicit, ten recorded defaults). Both arms were freshly timed in C–A–A–C order, 100 strict CUPTI samples per phase, ten warmups, cold-L2 CUDA Graphs. Current release native cohort is moe_utils046552b8 plus the three unchanged modules. Private per-arm cached_ops/CuTe roots share only those native modules and canonical generated/cubin inputs; normal loaders preserved all ELF/Ninja hashes and no-op. No retune, source edit, TRT/legacy rerun, or historical-row substitution.

Complete replay covers 9,600 raw spans, 96 phase medians, 120 loaded LOCAL0 records, 48 actual stage resource configurations and 80 default-stage/resource joins. All stage resource fields are equal between arms. All 384 clock quartiles are present; 100 have a non2032 median clock or nonzero reason. No negative cell has both repeat spreads ≤0.5%; that descriptive boundary is not a confidence interval. Clock flags are observations, not an explanation for losses.

| Model | EP GM | TP GM |
|---|---:|---:|
| K3 | -1.3162% | +0.3399% |
| N3U | +1.0544% | -0.3204% |
| V3 | -0.4769% | +0.0358% |
| V41F | -2.1938% | -0.7812% |

## Complete 24 cells

| Model | EP/TP | Mode | 4096 | 8192 | 16384 |
|---|---|---|---:|---:|---:|
| kimi-k3 | EP8 | CuteDSL W4A16 | -0.012% | -4.230% | +0.360% |
| kimi-k3 | TP8 | CuteDSL W4A16 | +0.720% | -1.244% | +1.564% |
| nemo3-ultra | EP8 | CuteDSL W4A16 | +0.065% | +2.331% | +0.780% |
| nemo3-ultra | TP8 | CuteDSL W4A16 | +0.208% | +0.930% | -2.075% |
| v3 | EP8 | CuteDSL W4A16 | +0.144% | -0.872% | -0.700% |
| v3 | TP8 | CuteDSL W4A16 | +0.256% | -0.154% | +0.005% |
| v41-flash | EP4 | CuteDSL W4A16 | +0.275% | -5.565% | -1.196% |
| v41-flash | TP4 | CuteDSL W4A16 | -0.357% | -1.309% | -0.675% |

## Every negative cell

Positive component Δ means slower candidate. Extensions describe completion beyond preceding stages; overlapping durations or separately aggregated medians must not be added to reconstruct E2E.

| Cell | Speedup | C/A spread | ΔE2E µs | ΔFC1 extension | ΔFC2 extension | Δcombine extension | Clock flags /16 |
|---|---:|---:|---:|---:|---:|---:|---:|
| K3 EP8 T4096 | -0.0118% | 5.690/7.627% | +0.224 | -2.224 | +2.543 | +0.152 | 0 |
| K3 EP8 T8192 | -4.2299% | 8.527/0.117% | +40.975 | +27.679 | +10.240 | +0.496 | 4 |
| V3 EP8 T8192 | -0.8718% | 1.427/4.750% | +5.144 | +0.216 | +3.824 | +0.096 | 0 |
| V3 EP8 T16384 | -0.7003% | 2.446/0.915% | +7.928 | +3.553 | +3.080 | +0.424 | 6 |
| V41F EP4 T8192 | -5.5650% | 2.952/4.042% | +41.232 | +26.368 | +8.576 | +0.680 | 1 |
| V41F EP4 T16384 | -1.1963% | 9.474/0.466% | +16.640 | +12.520 | +7.312 | +0.504 | 10 |
| K3 TP8 T8192 | -1.2441% | 3.288/2.923% | +15.991 | +3.575 | +5.176 | +1.175 | 5 |
| N3U TP8 T16384 | -2.0749% | 2.233/0.403% | +38.631 | +14.728 | +21.464 | +1.712 | 11 |
| V3 TP8 T8192 | -0.1535% | 1.369/2.536% | +1.344 | -0.232 | +0.952 | +0.488 | 1 |
| V41F TP4 T4096 | -0.3575% | 0.067/2.084% | +1.993 | +0.856 | -0.288 | +0.336 | 0 |
| V41F TP4 T8192 | -1.3089% | 7.161/1.242% | +11.929 | +1.929 | +6.256 | +1.648 | 9 |
| V41F TP4 T16384 | -0.6748% | 1.425/0.902% | +12.448 | +3.984 | +9.513 | +0.825 | 8 |

The largest loss, V41F EP8K, is −5.5650%: both candidate phases exceed both controls, with C/A repeat spreads 2.952/4.042% and one flagged clock quartile. FC1/FC2/combine extensions grow +26.368/+8.576/+0.680 µs. This is an adverse whole-branch observation, not an isolated attribution to selector, skip-group, SiTU, or cutoff. K3 EP8K is −4.2299%, but its control phases differ by 8.527% and four clock windows are flagged; keep both the loss and that uncertainty.

All 12 negative trajectories are in [negative-details.md](negative-details.md). Full raw data and component CSVs remain under `evidence/w4-cumulative-prefill/1793414097438305000`. No repeat or subsequent experiment is launched by this summary.
