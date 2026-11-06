# Ternary absmax one bounded repeat

Frozen abd55f60 ternary absmax versus retained b139; only _absmax changes.

Decision pending bounded repeat. All predeclared cells are preserved; no retuning, clocks, or post-result source changes.

2/2 cells complete. Same-GPU C-A-A-C, 100 strict CUPTI samples/phase, cold L2 and frozen routes/tactics. Percent is control/candidate minus one; positive is faster.

| Job | Tokens | Backend | C1 us | A1 us | A2 us | C2 us | Speedup | C/A spread |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| ep-nemo3-ultra-mxfp | 16384 | CuteDSL MXFP4x8 | 761.879 | 782.534 | 775.958 | 782.119 | -0.938% | 2.657% / 0.848% |
| ep-nemo3-ultra-per-token | 16384 | CuteDSL PER-TOKEN | 913.496 | 912.600 | 913.624 | 913.976 | +0.068% | 0.053% / 0.112% |

Source and numerical qualification: `../swap-absmax-ternary-b139/QUALIFICATION.md`. Components, sample quartiles and clock timelines remain in each result analysis. Higher-spread cases are not used to claim causality.
