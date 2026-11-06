# SF coordinate cache: complete 56-cell screen

Retention review is pending. No additional timings are planned.

All 23 jobs, 56 cells, 224 phase medians and 22,400 CUPTI samples passed the existing checks. Overall geometric speedup is -0.014834%; T32 -0.128760% and T16384 +0.099222%. All 33 negative rows remain, including 21 with both repeat spreads ≤0.5% (descriptive, not statistical confidence).

| Group | Cells | Speedup | Negative |
|---|---:|---:|---:|
| band/decode | 28 | -0.128760% | 20 |
| band/prefill | 28 | +0.099222% | 13 |
| band/all | 56 | -0.014834% | 33 |
| mode/CuteDSL MXFP4x8 | 14 | -1.006288% | 10 |
| mode/CuteDSL MXFP8 | 10 | -0.414918% | 6 |
| mode/CuteDSL PER-TOKEN | 16 | +0.903622% | 8 |
| mode/CuteDSL W4A4 | 16 | +0.193526% | 9 |
| model_topology/kimi-k3/ep | 6 | -2.756057% | 6 |
| model_topology/kimi-k3/tp | 6 | -0.752087% | 5 |
| model_topology/nemo3-ultra/ep | 8 | +0.466346% | 4 |
| model_topology/nemo3-ultra/tp | 8 | -0.898738% | 5 |
| model_topology/v3/ep | 8 | +1.343749% | 4 |
| model_topology/v3/tp | 8 | +0.046131% | 4 |
| model_topology/v41-flash/ep | 8 | +1.201814% | 4 |
| model_topology/v41-flash/tp | 4 | +0.844306% | 1 |
| topology/ep | 30 | +0.239928% | 18 |
| topology/tp | 26 | -0.307985% | 15 |

The strongest tight adverse row is N3U TP W4A4 T16384: C1/C2 1136.3145/1136.074 µs versus A1/A2 1192.059/1192.090 µs, −4.687648%. All 16 clock quartiles are available at median 2032 MHz with reason 0. K3 TP W4A4 T16384 is −1.608823% with tight repeats but one 2025 MHz quartile; larger MX/K3 EP losses carry repeat or clock caveats. The complete row and component tables preserve these distinctions.

All 448 loaded resource records are LOCAL0. Across 112 ordered cell/stage comparisons, registers, stage counts, launch configuration and driver CTA capacity are unchanged; 34 FC1 pairs add 128–1024 shared bytes. Same-arm repeated resources are identical. This is capacity evidence, not achieved residency.

Clock evidence retains all 896 quartiles: 56 exceptions and 0 missing. No sample or row was excluded. Component durations overlap under PDL; use exposed extensions and avoid inferring causality from resources alone.

The 13,245-file source inventories per arm, current four-library ELF/Ninja hashes and final Ninja no-op checks passed. All eight GPUs are idle and released. Both arms use the explicitly adopted same-source moe_utils046552b8 cohort plus the other three original libraries; failed original-identity restoration and earlier held preparation remain preserved.

Evidence:

- [Complete raw bundle](../../evidence/sf-coordinate-cache-screen/1793411008505163000/data/)
- [Full phase table](../../evidence/sf-coordinate-cache-screen/1793411008505163000/report/table.md)
- [All negative rows, clocks and components](performance/negative-cells.md)
- [Resource comparison](performance/runtime-resource-comparison.json)
- [Source/cache/execution closure](performance/screen/execution-complete.json)
- [Performance closure](performance/performance-closure.json)

Method: c1ac control versus sole15d6 swap delta; frozen routes/tactics, T32/T16384, C-A-A-C, 100 CUPTI graph samples after 10 warmups per cell/phase, cold L2 and input quantization included. Positive speedup means control/candidate −1. Primary estimator is the ratio of geometric means of the two phase medians. No source or timing-method changes occurred during the screen.
