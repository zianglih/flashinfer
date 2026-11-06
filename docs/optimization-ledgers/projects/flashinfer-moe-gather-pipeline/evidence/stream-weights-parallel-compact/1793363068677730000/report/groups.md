| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 6 | +0.321% | 1 | 0.221% | 0.579% |
| band/prefill | 6 | -4.450% | 6 | 4.187% | 3.362% |
| band/all | 12 | -2.093% | 7 | 4.187% | 3.362% |
| mode/CuteDSL MXFP4x8 | 4 | -1.580% | 2 | 0.221% | 1.178% |
| mode/CuteDSL MXFP8 | 4 | -3.205% | 2 | 4.187% | 3.362% |
| mode/CuteDSL PER-TOKEN | 2 | -0.109% | 1 | 0.213% | 0.579% |
| mode/CuteDSL W4A4 | 2 | -2.843% | 2 | 0.097% | 0.571% |
| model_topology/nemo3-ultra/ep | 2 | -2.843% | 2 | 0.097% | 0.571% |
| model_topology/nemo3-ultra/tp | 2 | -0.109% | 1 | 0.213% | 0.579% |
| model_topology/v3/ep | 4 | -4.081% | 2 | 4.187% | 3.362% |
| model_topology/v3/tp | 4 | -0.682% | 2 | 0.931% | 0.309% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 2 | -2.843% | 2 | 0.097% | 0.571% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 2 | -0.109% | 1 | 0.213% | 0.579% |
| model_topology_mode/v3/ep/CuteDSL MXFP4x8 | 2 | -3.120% | 1 | 0.115% | 1.178% |
| model_topology_mode/v3/ep/CuteDSL MXFP8 | 2 | -5.032% | 1 | 4.187% | 3.362% |
| model_topology_mode/v3/tp/CuteDSL MXFP4x8 | 2 | -0.016% | 1 | 0.221% | 0.309% |
| model_topology_mode/v3/tp/CuteDSL MXFP8 | 2 | -1.343% | 1 | 0.931% | 0.296% |
| implementation/swap_ab | 12 | -2.093% | 7 | 4.187% | 3.362% |
