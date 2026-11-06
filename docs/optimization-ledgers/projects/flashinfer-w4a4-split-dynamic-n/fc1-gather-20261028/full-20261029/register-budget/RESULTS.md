# Control112 screen vs clean fork head

Base: `fb66a27e6b40bdbbefd1b8bf0c0fc3f3ada8af90`. Candidate kernel: `d9af059b4121b0c251b4fcae67a4edc4920e49ec69fcca82be7ae5984c37d310`. One unstaged FC1 control-register budget change80→112. Gather128 and epilogue256 unchanged.

36 affected cells: **+0.286%** geometric mean; tokens8/256+0.040%, prefill+0.532%. N3U EP has stable prefill gains after spill elimination, but V3 TP MXFP4x8 at16384 has a stable−2.584% regression. Test120-budget codegen before choosing the retained policy.

All7 tests,20 C-A-A-C phases and17,600 strict-CUPTI cold-L2 samples verified. Sources, routing and tactics frozen; no AUTO; NVFP4 includes input quantization; all candidate runtime register guards pass. W4A16 is unchanged and diagnostic only.

| Topology/model | Backend | T8 | T256 | T4096 | T16384 |
|---|---|---:|---:|---:|---:|
| EP kimi-k3 | CuteDSL MXFP4x8 | +0.136% | +0.025% | -0.028% | -1.921% |
| EP nemo3-ultra | CuteDSL W4A4 | -0.220% | +0.091% | +3.117% | +4.619% |
| EP nemo3-ultra | CuteDSL PER-TOKEN | +0.219% | -0.069% | +1.944% | +0.500% |
| EP nemo3-ultra | CuteDSL W4A16 | -0.137% | +0.125% | -0.002% | -0.117% |
| EP v41-flash | CuteDSL MXFP8 | +0.055% | -0.050% | -0.053% | +2.902% |
| EP v41-flash | CuteDSL MXFP4x8 | +0.162% | +0.022% | -0.011% | +1.230% |
| TP v3 | CuteDSL MXFP8 | -0.191% | +0.067% | -0.014% | -0.265% |
| TP v3 | CuteDSL MXFP4x8 | +0.000% | -0.073% | +0.031% | -2.584% |
| TP v41-flash | CuteDSL W4A4 | +0.200% | -0.041% | -0.063% | -0.083% |
| TP v41-flash | CuteDSL PER-TOKEN | +0.238% | +0.141% | +0.447% | +0.061% |
| TP v41-flash | CuteDSL W4A16 | +0.052% | +0.020% | -0.874% | -0.819% |

N3U EP affected prefill repeat spread≤0.25%; V3 TP MXFP4x8 at16384 control/candidate spread0.01%/0.22%. K3 EP at16384 has7.68% control spread; V41F EP MXFP8 at16384 has8.42% candidate spread, so those individual deltas are inconclusive. Raw medians and spreads: `report/cells.csv`.

One initial attempt stopped before candidate timing because the patch receipt used abbreviated Git index lines. It was corrected to `git diff --binary --full-index`; all final phases reran from scratch. Test and codegen source content was unchanged. Incomplete measurements are excluded.
