| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 10 | +0.024% | 5 | 0.966% | 0.502% |
| band/middle | 6 | +0.075% | 2 | 0.118% | 0.143% |
| band/prefill | 6 | +0.197% | 3 | 0.101% | 0.164% |
| band/all | 22 | +0.085% | 10 | 0.966% | 0.502% |
| mode/CuteDSL PER-TOKEN | 22 | +0.085% | 10 | 0.966% | 0.502% |
| model_topology/nemo3-ultra/ep | 11 | +0.179% | 4 | 0.966% | 0.322% |
| model_topology/nemo3-ultra/tp | 11 | -0.009% | 6 | 0.219% | 0.502% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL PER-TOKEN | 11 | +0.179% | 4 | 0.966% | 0.322% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 11 | -0.009% | 6 | 0.219% | 0.502% |
| implementation/swap_ab | 22 | +0.085% | 10 | 0.966% | 0.502% |
