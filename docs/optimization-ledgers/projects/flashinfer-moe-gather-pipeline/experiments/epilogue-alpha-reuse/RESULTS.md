# Post-wait alpha reuse: bounded screen

Status: rejected after the complete 56-cell screen and independent root raw replay. The remaining 308 points were not run. The completed review checkout/branch are retired; source, patch, qualification and all raw evidence are preserved under this experiment.

The screen compares retained `49c91adf` with the single-file `70499a11` candidate. It uses the 28 supported swap model/topology/dtype arms at 32 and 4096 tokens, frozen tactics/routes, CAAC order, 100 CUPTI samples per phase, 10 warmups, cold-L2 graph replay, and input quantization included for the NVFP4 family. The replacement C2 B300 host and the new release-cache cohort are recorded in launch/postflight receipts.

| Scope | Cells | Geometric mean | Negative cells |
|---|---:|---:|---:|
| All | 56 | +0.0111% | 26 |
| 32 tokens | 28 | +0.0087% | 14 |
| 4096 tokens | 28 | +0.0136% | 12 |

All 22,400 samples, 448 loaded-kernel records, and 896 clock quartiles passed replay. There are no missing telemetry quartiles. One V41F EP MXFP4x8 control quartile has median SM clock 2017 MHz; it is retained. All 112 matched compilation-resource pairs have zero local memory and unchanged shared memory/residency. Twelve reduce registers by 1–6; none increase them.

K3 TP at 4096 tokens has opposed results: W4A4 improves by +0.9693% with FC2 critical-path extension −5.072 μs; per-token regresses by −1.0652% with FC2 extension +7.1675 μs. The latter repeats are tight (control 0.080%, candidate 0.014%) and has normal clocks. Overall neutrality must not hide that regression. No new native-image capture or follow-up timing has been performed.

The conservative frozen-tactic two-channel group is +0.0363% over 16 cells; the 40 one-channel controls are +0.0010%. This grouping is descriptive and is not an exact per-cell binary-identity proof.

## Complete screen

| Model | EP/TP | Mode | 32 | 4096 |
|---|---|---|---:|---:|
| kimi-k3 | EP8 | CuteDSL MXFP4x8 | -0.058% | -0.002% |
| kimi-k3 | EP8 | CuteDSL PER-TOKEN | -0.044% | -0.335% |
| kimi-k3 | EP8 | CuteDSL W4A4 | +0.018% | +0.090% |
| kimi-k3 | TP8 | CuteDSL MXFP4x8 | +0.005% | +0.019% |
| kimi-k3 | TP8 | CuteDSL PER-TOKEN | -0.094% | -1.065% |
| kimi-k3 | TP8 | CuteDSL W4A4 | +0.080% | +0.969% |
| nemo3-ultra | EP8 | CuteDSL MXFP4x8 | +0.040% | +0.051% |
| nemo3-ultra | EP8 | CuteDSL MXFP8 | +0.010% | +0.109% |
| nemo3-ultra | EP8 | CuteDSL PER-TOKEN | -0.000% | -0.017% |
| nemo3-ultra | EP8 | CuteDSL W4A4 | -0.062% | +0.059% |
| nemo3-ultra | TP8 | CuteDSL MXFP4x8 | +0.018% | +0.013% |
| nemo3-ultra | TP8 | CuteDSL MXFP8 | -0.052% | +0.065% |
| nemo3-ultra | TP8 | CuteDSL PER-TOKEN | -0.052% | -0.016% |
| nemo3-ultra | TP8 | CuteDSL W4A4 | -0.145% | -0.093% |
| v3 | EP8 | CuteDSL MXFP4x8 | -0.075% | +0.272% |
| v3 | EP8 | CuteDSL MXFP8 | +0.073% | -0.035% |
| v3 | EP8 | CuteDSL PER-TOKEN | +0.106% | -0.026% |
| v3 | EP8 | CuteDSL W4A4 | -0.032% | -0.138% |
| v3 | TP8 | CuteDSL MXFP4x8 | +0.365% | +0.000% |
| v3 | TP8 | CuteDSL MXFP8 | +0.038% | +0.005% |
| v3 | TP8 | CuteDSL PER-TOKEN | -0.028% | +0.014% |
| v3 | TP8 | CuteDSL W4A4 | -0.030% | -0.068% |
| v41-flash | EP4 | CuteDSL MXFP4x8 | +0.054% | +0.261% |
| v41-flash | EP4 | CuteDSL MXFP8 | -0.019% | -0.060% |
| v41-flash | EP4 | CuteDSL PER-TOKEN | -0.006% | -0.156% |
| v41-flash | EP4 | CuteDSL W4A4 | +0.044% | +0.073% |
| v41-flash | TP4 | CuteDSL PER-TOKEN | +0.061% | +0.224% |
| v41-flash | TP4 | CuteDSL W4A4 | +0.029% | +0.181% |

## Evidence

- Raw bundle: `evidence/epilogue-alpha-reuse-screen/1793380997129814000/data`.
- Raw replay, full CAAC table, component deltas, resources and clocks: sibling `report/`.
- Source/native qualification: `qualification-summary.json` and `alpha-load-removal.json`.
- Final source/cache/idle check: `performance/screen/execution-complete.json`; GPUs 0/2 released.
- Machine-readable summary: `performance/screen/summary.json`.

This is a bounded screen, not the full 364-cell refresh or sanitizer coverage. The rejection preserves the native load-reduction evidence but does not trade a tight measured regression for neutral aggregate performance.
