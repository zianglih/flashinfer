| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 32 | +0.034% | 15 | 1.899% | 0.782% |
| band/middle | 16 | -0.031% | 9 | 0.115% | 0.457% |
| band/prefill | 8 | +2.100% | 1 | 1.706% | 0.787% |
| band/all | 56 | +0.308% | 25 | 1.899% | 0.787% |
| mode/CuteDSL MXFP4x8 | 14 | +0.303% | 7 | 0.711% | 0.377% |
| mode/CuteDSL MXFP8 | 14 | +0.479% | 6 | 1.706% | 0.787% |
| mode/CuteDSL PER-TOKEN | 14 | -0.042% | 6 | 0.155% | 0.782% |
| mode/CuteDSL W4A4 | 14 | +0.493% | 6 | 1.899% | 0.572% |
| model_topology/nemo3-ultra/ep | 28 | +0.330% | 16 | 1.899% | 0.782% |
| model_topology/nemo3-ultra/tp | 28 | +0.285% | 9 | 1.706% | 0.787% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP4x8 | 7 | +0.558% | 3 | 0.711% | 0.187% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP8 | 7 | +0.395% | 3 | 0.593% | 0.138% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL PER-TOKEN | 7 | -0.118% | 4 | 0.071% | 0.782% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 7 | +0.488% | 6 | 1.899% | 0.572% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP4x8 | 7 | +0.049% | 4 | 0.294% | 0.377% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP8 | 7 | +0.562% | 3 | 1.706% | 0.787% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 7 | +0.034% | 2 | 0.155% | 0.305% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL W4A4 | 7 | +0.497% | 0 | 0.380% | 0.249% |
| implementation/swap_ab | 56 | +0.308% | 25 | 1.899% | 0.787% |
