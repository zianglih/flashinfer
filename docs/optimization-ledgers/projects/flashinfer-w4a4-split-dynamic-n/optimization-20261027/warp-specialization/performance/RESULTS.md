# Fixed warp-role pilot results

All 80 cells completed: overall **+0.759%**, decode (T4/T64) **+1.189%**, prefill (T512/T4096/T16384) **+0.473%**. All cells, including unstable and negative results, remain in these aggregates.

60 phases; 40,000 public CUPTI samples, of which 32,000 frozen samples determine speedups. The 8,000 AUTO diagnostic samples are excluded. Source/config/cache/gate proof passed; archive `0e6cbcb9ed137575d01070fc5741327ac606efe29da02588db7a1494aca7ee86`.

| Format | Overall | Decode | Prefill | Min | Max |
|---|---:|---:|---:|---:|---:|
| CuteDSL W4A4 | +0.988% | +0.901% | +1.047% | -0.834% | +7.318% |
| CuteDSL PER-TOKEN | +0.181% | -0.114% | +0.377% | -1.444% | +1.246% |
| CuteDSL MXFP8 | +0.516% | +1.165% | +0.086% | -2.165% | +4.248% |
| CuteDSL MXFP4x8 | +1.353% | +2.826% | +0.383% | -3.229% | +9.899% |

11 cells exceed 1% absolute control endpoint drift or candidate spread. They are labeled uncertain, not removed:

| Model | Backend | Tokens | Speedup | C drift | A spread |
|---|---|---:|---:|---:|---:|
| v3 | CuteDSL MXFP8 | 16384 | -0.720% | -0.002% | +4.508% |
| v3 | CuteDSL MXFP4x8 | 16384 | -0.453% | +4.833% | -4.841% |
| v41-flash | CuteDSL MXFP8 | 16384 | -0.114% | +0.974% | -1.414% |
| v41-flash | CuteDSL MXFP4x8 | 16384 | -3.229% | -5.907% | +0.844% |
| kimi-k3 | CuteDSL W4A4 | 16384 | +2.882% | -5.359% | -0.532% |
| kimi-k3 | CuteDSL PER-TOKEN | 16384 | +0.054% | -1.526% | -1.105% |
| kimi-k3 | CuteDSL MXFP8 | 16384 | -2.165% | +0.765% | -6.082% |
| kimi-k3 | CuteDSL MXFP4x8 | 16384 | -1.387% | -3.447% | -4.527% |
| nemo3-ultra | CuteDSL W4A4 | 16384 | -0.834% | +0.135% | +1.024% |
| nemo3-ultra | CuteDSL MXFP8 | 16384 | +2.534% | +7.550% | +7.933% |
| nemo3-ultra | CuteDSL MXFP4x8 | 16384 | +2.168% | +1.788% | -3.128% |

Stable negatives below −0.25% (both within-arm differences ≤1%):

- v3 CuteDSL PER-TOKEN T4: -1.201% (C drift -0.159%, A spread -0.033%).
- kimi-k3 CuteDSL PER-TOKEN T4: -1.444% (C drift +0.000%, A spread +0.197%).
- nemo3-ultra CuteDSL PER-TOKEN T16384: -0.499% (C drift +0.039%, A spread +0.215%).

[Full 80-cell table](assembled/table.md). The following diagnostics preserve all original pilot rows and native selections.

[Source × native-winner crosschecks](DIAGNOSTICS.md) completed 16 phases / 1,600 samples. At the old winner, V3 is +0.015% and K3 is −0.256%; the candidate-selected winner costs −1.388% and −0.942%, respectively. The changed native selection accounts for most of these two decode losses. All diagnostic paired drifts are below 0.5%.

[T16384 repeats](drift-repeat/table.md) covered all 11 original drift flags in 28 phases / 4,400 samples. K3 MXFP4x8 settles at +1.743% and Nemo W4A4 at −0.167%, both with within-arm differences below 1%. The other nine remain drift-inconclusive. No repeat replaces a pilot row or changes the aggregates above.
