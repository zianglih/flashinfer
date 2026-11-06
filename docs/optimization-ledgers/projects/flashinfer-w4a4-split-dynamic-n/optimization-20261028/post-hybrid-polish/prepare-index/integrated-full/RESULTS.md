# Integrated R1 prepare refresh

Frozen candidate: retained `33b7e526` plus only unsigned prepare-index arithmetic (`603dcdf2`); the original loop policy remains unchanged. The review clone contains one unstaged file. No source was committed or published.

Validation:48 exact graph replays per source and8 compiled pairs,348 source hashes, no spills/local memory. Actual K3 scaled code still uses compiler unrolling (85→301 static instructions,30→32registers); this is recorded rather than hidden. See `prepare-gate/RESULTS.md`.

Performance:15 jobs,13 token counts,2 fresh candidate passes,468 cells,936 medians and93,600 strict CUPTI samples. The retained33b7 candidate1/2 results provide93,600 reused samples. Sources, cached winners, routing, physical UUIDs and all primary ratios verified. No autotuning, external baseline rerun or sanitizer. Tokens1/2 are collected but excluded from displayed aggregates.

Fresh candidate passes began 25.5–34.1 minutes after the corresponding closing retained pass. This is AA versus saved AA, not a fresh CAAC comparison.

| Scope | EP displayed | TP displayed |
|---|---:|---:|
| All formats | −0.087% | −0.120% |
| Scaled formats | −0.055% | −0.165% |
| W4A16 | −0.206% | +0.028% |

Largest negative primary cells:

| Cell | Speedup | Saved C1/C2 µs | Fresh A1/A2 µs |
|---|---:|---:|---:|
| EP v41-flash CuteDSL W4A16 T8192 | -3.666% | 708.371/707.796 | 741.603/728.516 |
| EP kimi-k3 CuteDSL W4A4 T16384 | -3.398% | 719.224/719.688 | 754.376/735.273 |
| EP nemo3-ultra CuteDSL W4A16 T16384 | -3.060% | 1467.525/1532.918 | 1540.854/1553.590 |
| EP nemo3-ultra CuteDSL W4A16 T8192 | -2.501% | 740.883/737.683 | 760.259/756.242 |
| EP kimi-k3 CuteDSL W4A16 T8192 | -2.490% | 995.740/930.874 | 987.931/986.764 |

These losses remain in the raw table. The aggregate is near neutral; the reused-control timing gap limits causal attribution. No additional experiment or retention decision is claimed.

Evidence: `full/evidence/verified.json` (2105 hashed files), `full/completion.json`, `full/independent-audit.json`, `full/analysis/summary.json`, `full/analysis/cells.csv`, and diagnostic `full/analysis/focus-strata.json`. All GPUs were idle at completion.
