# SF/payload interleave — rejected

The single 56-cell C–A–A–C screen does not justify retaining the added issue-order control. The complete matrix is **−0.245686%**, decode **−0.078375%**, and prefill **−0.412717%**; **32/56 cells are negative**. Several TP losses have small repeat spread and normal sampled clocks. Large EP MX changes have considerable repeat/clock variation and are not presented as isolated causal regressions. No repeat, larger matrix, shape rescue or source revision follows this result.

- Measured retained control: `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`; candidate swap SHA `a014d6aa7ff8b83add8fd20a808083c0a58562cd3e212ab00f5d31c1cf890a49` in the sole qualification-owned snapshot. Current retained `c1ac8ce7341039db65195b99445fcdeb193cf226` only changes W4; no interleave change was merged.
- Qualification: 22 exact calls / 33 native pairs; identical resource/configuration/occupancy/compiler options, zero local memory. All 22 FC2/finalizer cubins are unchanged; affected FC1 static changes range from −31 to +6 non-NOP. Narrow control overhead is preserved in the native report.
- Performance: 23 jobs / 28 supported swap or per-token model/topology arms, T32/T16384; 100 strict CUPTI samples and 10 warmups per phase, cold-L2 graph replay, frozen choices/routes, per-token input quant included. Estimator is geometric mean of control phase medians divided by geometric mean of candidate phase medians, minus one. No baseline rerun or autotuning.
- Runtime: recovery B300 node, GPUs 0/1/4/5, current shared release C++ cohort. Both complete 13,245-file source inventories and release ELF/Ninja hashes pass postflight; all four GPUs are idle/released. The same persistent compilation cache remains available.
- Complete report replay: 22,400 samples, 224 phase medians, 448 loaded resource records, 896 clock quartiles; 56 clock exceptions, zero missing. All original records and samples remain unchanged. Independent peer verification is recorded separately under `audits/`.

Evidence: `../../evidence/sf-payload-interleave-screen/1793395366333144000/` (archive SHA `adc3b24cafe5ed014a3beff8aa78569288630f1015a38f83b05a49deafaa81e4`). Full phase medians: `report/table.md`; aggregate matrix: `report/matrix.md`; stage timelines: `report/phase-components.csv` and `report/component-deltas.csv`; clocks/resources: their report JSON files. Config SHA `14afee7c49e060c33e572a3dd4ac8c09d6f0fadbb1d15b68a74566e1be45e37d`. Complete native gate SHA `d5f5e0cf38e854096cb605ae99242a2d5134f25442461ea0e5e51318306d8092`.

## Every negative cell

All 32 negatives are retained, including the near-zero negative. C/A spread is `(max phase median / min phase median − 1) × 100`; clock flags count the 16 quartile windows with median SM clock other than 2032 MHz or a nonzero reason. This is descriptive, not a statistical confidence claim. Component deltas are differences of per-phase medians; overlapping durations must not be summed.

| Model | Topology | Mode | Tokens | Speedup | C spread | A spread | Clock flags / 16 | FC1 extension Δ µs | FC2-after-FC1 Δ µs |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| kimi-k3 | EP | MXFP4x8 | 16384 | -0.063802% | 3.868% | 1.800% | 0 | +0.432 | -0.440 |
| kimi-k3 | EP | PER-TOKEN | 32 | -0.348785% | 0.017% | 0.150% | 0 | +0.688 | -0.152 |
| kimi-k3 | EP | PER-TOKEN | 16384 | -0.881872% | 2.329% | 0.671% | 2 | +1.632 | +5.280 |
| nemo3-ultra | EP | MXFP4x8 | 32 | -0.127171% | 0.032% | 0.127% | 0 | +0.056 | +0.040 |
| nemo3-ultra | EP | MXFP4x8 | 16384 | -3.066107% | 4.047% | 0.644% | 3 | +13.296 | +8.968 |
| nemo3-ultra | EP | MXFP8 | 16384 | -3.975421% | 5.462% | 0.376% | 4 | +19.615 | +10.840 |
| nemo3-ultra | EP | PER-TOKEN | 32 | -0.275666% | 0.174% | 0.144% | 0 | +0.312 | +0.017 |
| nemo3-ultra | EP | W4A4 | 16384 | -0.052936% | 0.054% | 0.184% | 0 | +0.272 | -0.040 |
| v3 | EP | MXFP4x8 | 32 | -0.057263% | 0.049% | 0.032% | 0 | +0.041 | -0.057 |
| v3 | EP | MXFP8 | 32 | -0.127081% | 0.058% | 0.000% | 0 | +0.080 | +0.096 |
| v3 | EP | MXFP4x8 | 16384 | -1.752992% | 1.430% | 5.286% | 0 | +5.024 | +4.641 |
| v3 | EP | PER-TOKEN | 32 | -0.330319% | 0.090% | 0.120% | 0 | +0.424 | -0.000 |
| v3 | EP | PER-TOKEN | 16384 | -0.339060% | 0.033% | 0.000% | 0 | +1.880 | +0.000 |
| v3 | EP | W4A4 | 32 | -0.008038% | 0.064% | 0.016% | 0 | +0.185 | -0.112 |
| v3 | EP | W4A4 | 16384 | -0.121248% | 0.099% | 0.126% | 0 | +0.816 | -0.064 |
| v41-flash | EP | MXFP4x8 | 16384 | -2.895524% | 6.002% | 5.086% | 2 | +12.024 | +7.904 |
| v41-flash | EP | MXFP8 | 16384 | -0.592609% | 3.365% | 4.895% | 6 | +1.680 | +2.096 |
| v41-flash | EP | PER-TOKEN | 32 | -0.067490% | 0.013% | 0.049% | 0 | +0.080 | +0.056 |
| v41-flash | EP | PER-TOKEN | 16384 | -0.392435% | 0.867% | 1.056% | 1 | +1.416 | +0.249 |
| v41-flash | EP | W4A4 | 32 | -0.006398% | 0.102% | 0.013% | 0 | -0.089 | +0.064 |
| v41-flash | EP | W4A4 | 16384 | -0.475022% | 0.003% | 0.670% | 1 | +2.080 | +0.487 |
| kimi-k3 | TP | MXFP4x8 | 32 | -0.161388% | 0.209% | 0.095% | 0 | +0.336 | -0.184 |
| kimi-k3 | TP | PER-TOKEN | 32 | -1.383261% | 0.180% | 0.053% | 0 | +2.448 | +0.081 |
| kimi-k3 | TP | PER-TOKEN | 16384 | -1.250261% | 0.120% | 0.446% | 0 | +24.304 | -0.984 |
| kimi-k3 | TP | W4A4 | 32 | -0.609216% | 0.086% | 0.010% | 0 | +1.105 | -0.072 |
| nemo3-ultra | TP | MXFP8 | 32 | -0.000024% | 0.151% | 0.062% | 0 | -0.080 | +0.000 |
| nemo3-ultra | TP | MXFP4x8 | 16384 | -1.024246% | 0.687% | 0.809% | 7 | +9.656 | +2.520 |
| nemo3-ultra | TP | PER-TOKEN | 16384 | -0.549051% | 0.021% | 0.027% | 0 | +10.041 | +0.376 |
| nemo3-ultra | TP | W4A4 | 16384 | -0.748341% | 0.008% | 0.021% | 0 | +7.960 | +1.344 |
| v3 | TP | MXFP4x8 | 16384 | -0.338773% | 0.081% | 0.101% | 2 | +1.840 | +0.488 |
| v3 | TP | MXFP8 | 16384 | -0.754672% | 0.312% | 0.178% | 7 | +4.344 | +3.912 |
| v3 | TP | PER-TOKEN | 32 | -0.027561% | 0.151% | 0.151% | 0 | -0.040 | +0.143 |

## Complete two-token matrix

| Model | EP/TP | Mode | 32 | 16384 |
|---|---|---|---:|---:|
| kimi-k3 | EP8 | CuteDSL MXFP4x8 | +0.062% | -0.064% |
| kimi-k3 | EP8 | CuteDSL PER-TOKEN | -0.349% | -0.882% |
| kimi-k3 | EP8 | CuteDSL W4A4 | +0.005% | +1.144% |
| kimi-k3 | TP8 | CuteDSL MXFP4x8 | -0.161% | +0.265% |
| kimi-k3 | TP8 | CuteDSL PER-TOKEN | -1.383% | -1.250% |
| kimi-k3 | TP8 | CuteDSL W4A4 | -0.609% | +0.515% |
| nemo3-ultra | EP8 | CuteDSL MXFP4x8 | -0.127% | -3.066% |
| nemo3-ultra | EP8 | CuteDSL MXFP8 | +0.038% | -3.975% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | -0.276% | +0.072% |
| nemo3-ultra | EP8 | CuteDSL W4A4 | +0.000% | -0.053% |
| nemo3-ultra | TP8 | CuteDSL MXFP4x8 | +0.615% | -1.024% |
| nemo3-ultra | TP8 | CuteDSL MXFP8 | -0.000% | +0.852% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | +0.026% | -0.549% |
| nemo3-ultra | TP8 | CuteDSL W4A4 | +0.096% | -0.748% |
| v3 | EP8 | CuteDSL MXFP4x8 | -0.057% | -1.753% |
| v3 | EP8 | CuteDSL MXFP8 | -0.127% | +3.789% |
| v3 | EP8 | CuteDSL PER-TOKEN | -0.330% | -0.339% |
| v3 | EP8 | CuteDSL W4A4 | -0.008% | -0.121% |
| v3 | TP8 | CuteDSL MXFP4x8 | +0.015% | -0.339% |
| v3 | TP8 | CuteDSL MXFP8 | +0.010% | -0.755% |
| v3 | TP8 | CuteDSL PER-TOKEN | -0.028% | +0.041% |
| v3 | TP8 | CuteDSL W4A4 | +0.121% | +0.329% |
| v41-flash | EP4 | CuteDSL MXFP4x8 | +0.000% | -2.896% |
| v41-flash | EP4 | CuteDSL MXFP8 | +0.026% | -0.593% |
| v41-flash | EP4 | CuteDSL PER-TOKEN | -0.067% | -0.392% |
| v41-flash | EP4 | CuteDSL W4A4 | -0.006% | -0.475% |
| v41-flash | TP4 | CuteDSL PER-TOKEN | +0.011% | +0.617% |
| v41-flash | TP4 | CuteDSL W4A4 | +0.326% | +0.372% |
