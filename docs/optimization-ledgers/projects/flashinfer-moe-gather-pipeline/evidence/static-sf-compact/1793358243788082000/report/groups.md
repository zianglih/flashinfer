| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 5 | +0.194% | 0 | 0.186% | 0.286% |
| band/middle | 5 | -0.011% | 4 | 0.264% | 0.228% |
| band/prefill | 5 | -0.767% | 4 | 5.336% | 3.237% |
| band/all | 15 | -0.195% | 8 | 5.336% | 3.237% |
| mode/CuteDSL MXFP4x8 | 3 | -1.087% | 2 | 5.336% | 3.237% |
| mode/CuteDSL PER-TOKEN | 6 | +0.021% | 3 | 0.170% | 0.481% |
| mode/CuteDSL W4A4 | 6 | +0.036% | 3 | 0.264% | 0.286% |
| model_topology/kimi-k3/ep | 3 | -1.087% | 2 | 5.336% | 3.237% |
| model_topology/kimi-k3/tp | 3 | +0.075% | 1 | 0.170% | 0.272% |
| model_topology/nemo3-ultra/ep | 3 | +0.118% | 1 | 0.264% | 0.228% |
| model_topology/v3/ep | 3 | -0.045% | 2 | 0.083% | 0.286% |
| model_topology/v41-flash/ep | 3 | -0.033% | 2 | 0.041% | 0.481% |
