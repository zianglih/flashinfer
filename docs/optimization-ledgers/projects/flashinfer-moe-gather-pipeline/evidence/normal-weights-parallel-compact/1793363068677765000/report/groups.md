| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 6 | -10.207% | 6 | 0.235% | 0.330% |
| band/prefill | 6 | -0.372% | 1 | 9.410% | 7.476% |
| band/all | 12 | -5.417% | 7 | 9.410% | 7.476% |
| mode/CuteDSL MXFP4x8 | 4 | -6.624% | 3 | 0.223% | 7.476% |
| mode/CuteDSL MXFP8 | 4 | -5.163% | 2 | 9.410% | 7.356% |
| mode/CuteDSL PER-TOKEN | 2 | -3.939% | 1 | 0.073% | 0.330% |
| mode/CuteDSL W4A4 | 2 | -4.961% | 1 | 0.235% | 0.085% |
| model_topology/nemo3-ultra/ep | 2 | -4.961% | 1 | 0.235% | 0.085% |
| model_topology/nemo3-ultra/tp | 2 | -3.939% | 1 | 0.073% | 0.330% |
| model_topology/v3/ep | 4 | -6.838% | 3 | 9.410% | 7.476% |
| model_topology/v3/tp | 4 | -4.945% | 2 | 0.270% | 0.745% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 2 | -4.961% | 1 | 0.235% | 0.085% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 2 | -3.939% | 1 | 0.073% | 0.330% |
| model_topology_mode/v3/ep/CuteDSL MXFP4x8 | 2 | -8.366% | 2 | 0.169% | 7.476% |
| model_topology_mode/v3/ep/CuteDSL MXFP8 | 2 | -5.285% | 1 | 9.410% | 7.356% |
| model_topology_mode/v3/tp/CuteDSL MXFP4x8 | 2 | -4.849% | 1 | 0.223% | 0.439% |
| model_topology_mode/v3/tp/CuteDSL MXFP8 | 2 | -5.040% | 1 | 0.270% | 0.745% |
| implementation/swap_ab | 12 | -5.417% | 7 | 9.410% | 7.476% |
