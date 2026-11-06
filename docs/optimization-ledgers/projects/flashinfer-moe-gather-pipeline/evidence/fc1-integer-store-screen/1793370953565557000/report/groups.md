| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 8 | +0.135% | 0 | 0.241% | 0.322% |
| band/middle | 8 | -0.004% | 5 | 0.261% | 0.349% |
| band/prefill | 16 | +2.414% | 2 | 3.778% | 3.750% |
| band/all | 32 | +1.233% | 7 | 3.778% | 3.750% |
| mode/CuteDSL MXFP4x8 | 8 | +1.504% | 2 | 3.778% | 3.750% |
| mode/CuteDSL MXFP8 | 8 | +1.327% | 2 | 2.452% | 2.072% |
| mode/CuteDSL PER-TOKEN | 8 | +0.037% | 3 | 0.179% | 0.322% |
| mode/CuteDSL W4A4 | 8 | +2.075% | 0 | 0.255% | 0.174% |
| model_topology/nemo3-ultra/ep | 16 | +1.265% | 4 | 3.778% | 3.750% |
| model_topology/nemo3-ultra/tp | 16 | +1.200% | 3 | 2.452% | 2.072% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP4x8 | 4 | +1.786% | 1 | 3.778% | 3.750% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP8 | 4 | +0.908% | 1 | 2.337% | 0.497% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL PER-TOKEN | 4 | -0.034% | 2 | 0.153% | 0.322% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 4 | +2.418% | 0 | 0.140% | 0.072% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP4x8 | 4 | +1.223% | 1 | 1.655% | 1.193% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP8 | 4 | +1.748% | 1 | 2.452% | 2.072% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 4 | +0.107% | 1 | 0.179% | 0.107% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL W4A4 | 4 | +1.733% | 0 | 0.255% | 0.174% |
| implementation/swap_ab | 32 | +1.233% | 7 | 3.778% | 3.750% |
