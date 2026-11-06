
## Matched stage attribution

Independent20-graph NSYS diagnostic, V3 MXFP4x8 T16384, same fixed winners. These traces are not substituted into the CAAC matrix; PDL-overlapped durations are not added.

| Topology | Stage | Control µs | Candidate µs | Change |
|---|---|---:|---:|---:|
| TP | Graph span | 1733.340 | 1577.531 | -8.99% |
| TP | Prepare | 315.122 | 313.571 | -0.49% |
| TP | FC1 | 443.571 | 442.851 | -0.16% |
| TP | FC2 | 713.589 | 513.012 | -28.11% |
| TP | Combine | 346.210 | 388.867 | +12.32% |
| EP | Graph span | 655.365 | 660.548 | +0.79% |
| EP | Prepare | 40.017 | 40.081 | +0.16% |
| EP | FC1 | 321.090 | 320.578 | -0.16% |
| EP | FC2 | 222.002 | 216.242 | -2.59% |
| EP | Combine | 83.424 | 92.352 | +10.70% |

TP FC2 registers122→108; EP108→100. Combine registers80→86 in both. Prepare/FC1 instruction ownership unchanged. The ordinary-TMA store removes a significant FC2 issue bottleneck under TP, but the changed global order increases combine cost. Compacting output capacity alone is not proof that this locality penalty disappears.

All26 profile files were SHA-verified. Native traces and SQLite: `profile-evidence/stage-profile`. Archive SHA256 `8cd44820d91959b4ee577f7e8e3b868de56ff5f8a52f24cf6de4a336bd10ca23`.
