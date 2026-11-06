| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 50 | +0.037% | 21 | 1.834% | 2.369% |
| band/middle | 30 | +0.002% | 13 | 0.346% | 0.388% |
| band/prefill | 30 | -0.562% | 19 | 8.097% | 6.355% |
| band/all | 110 | -0.136% | 53 | 8.097% | 6.355% |
| mode/CuteDSL MXFP4x8 | 22 | +0.053% | 9 | 8.097% | 4.318% |
| mode/CuteDSL MXFP8 | 11 | -0.331% | 5 | 0.434% | 3.513% |
| mode/CuteDSL PER-TOKEN | 22 | +0.030% | 9 | 1.108% | 2.295% |
| mode/CuteDSL W4A16 | 33 | -0.396% | 18 | 3.322% | 6.355% |
| mode/CuteDSL W4A4 | 22 | -0.002% | 12 | 0.365% | 4.057% |
| model_topology/kimi-k3/ep | 44 | -0.225% | 19 | 4.429% | 4.057% |
| model_topology/nemo3-ultra/ep | 55 | -0.039% | 27 | 8.097% | 4.318% |
| model_topology/v3/ep | 11 | -0.269% | 7 | 1.834% | 6.355% |
| model_topology_mode/kimi-k3/ep/CuteDSL MXFP4x8 | 11 | -0.079% | 6 | 4.429% | 2.870% |
| model_topology_mode/kimi-k3/ep/CuteDSL PER-TOKEN | 11 | +0.031% | 3 | 1.108% | 2.295% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A16 | 11 | -0.791% | 5 | 1.802% | 1.568% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A4 | 11 | -0.058% | 5 | 0.365% | 4.057% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP4x8 | 11 | +0.185% | 3 | 8.097% | 4.318% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP8 | 11 | -0.331% | 5 | 0.434% | 3.513% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL PER-TOKEN | 11 | +0.029% | 6 | 0.326% | 0.239% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A16 | 11 | -0.128% | 6 | 3.322% | 2.990% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 11 | +0.053% | 7 | 0.270% | 2.099% |
| model_topology_mode/v3/ep/CuteDSL W4A16 | 11 | -0.269% | 7 | 1.834% | 6.355% |
| implementation/swap_ab | 77 | -0.024% | 35 | 8.097% | 4.318% |
| implementation/w4a16 | 33 | -0.396% | 18 | 3.322% | 6.355% |
