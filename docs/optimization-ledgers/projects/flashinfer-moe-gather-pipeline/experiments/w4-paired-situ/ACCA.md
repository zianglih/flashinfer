# Separate six-cell opposite-order check

This diagnostic follows A–C–C–A on the same original GPUs and uses the same source, frozen choices/routes, native configuration, CUDA Graph/CUPTI100 samples,10 warmups, and cold-L2 contract. It is **additional evidence**, not a replacement for the original26 C–A–A–C observations. The selected token set differs, so a changed result cannot be attributed uniquely to phase ordering.

| Shape | Tokens | Original CAAC | Repeat ACCA | Repeat C spread | Repeat A spread |
|---|---:|---:|---:|---:|---:|
| K3 EP8 | 16 | -0.720% | +0.007% | 0.120% | 0.133% |
| K3 EP8 | 32 | -0.452% | +0.097% | 0.036% | 0.035% |
| K3 EP8 | 128 | -0.271% | -0.101% | 0.031% | 0.037% |
| K3 EP8 | 4096 | +4.376% | +2.346% | 3.068% | 0.121% |
| K3 TP8 | 4096 | +1.068% | +0.200% | 1.901% | 1.059% |
| K3 TP8 | 8192 | +0.276% | +0.572% | 0.333% | 2.972% |

The tight original EP16/32 losses do not persist. In the repeat, FC1 spans are0.048/0.104us shorter and routing is0.016/0.096us shorter. EP128 remains−0.101%, but its FC1 span improves0.015us while routing increases0.352us. This supports treating the original losses as an uncertain end-to-end execution effect rather than an established arithmetic regression.

All three repeated prefill points are positive, but repeat spread reaches3.07% and four clock-exception quartiles remain. Neither the primary+1.10% nor diagnostic+1.03% prefill aggregate establishes a dependable speedup.

Actual execution order and raw phase medians:

| Shape | Tokens | A1 | C1 | C2 | A2 |
|---|---:|---:|---:|---:|---:|
| K3 EP8 | 16 | 120.2570 | 120.2730 | 120.4175 | 120.4170 |
| K3 EP8 | 32 | 182.4015 | 182.5780 | 182.5130 | 182.3370 |
| K3 EP8 | 128 | 308.1780 | 307.8740 | 307.9705 | 308.2905 |
| K3 EP8 | 4096 | 541.2520 | 545.9730 | 562.7245 | 541.9085 |
| K3 TP8 | 4096 | 708.3080 | 712.6750 | 699.3800 | 700.8840 |
| K3 TP8 | 8192 | 1259.1265 | 1287.1430 | 1282.8710 | 1296.5510 |

2,400 raw samples,48 loaded functions,unchanged native resource policies and LOCAL0; all source/cache/route/native configuration/timing guards passed. No retuning, modified production options, dropped samples, or added policy. The original26 contain10,400 samples and remain primary. GPUs1/3 were checked idle and released after the campaign.

Raw diagnostic: `evidence/w4-paired-situ-acca/1793380968593160000/data`; standard complete report in sibling `report/`. The standard report labels C/A columns by arm for comparison; its actual phase labels and the table above preserve A–C–C–A chronology.
