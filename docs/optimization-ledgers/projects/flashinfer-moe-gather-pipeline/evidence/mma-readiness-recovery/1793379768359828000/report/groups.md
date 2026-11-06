| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 14 | -0.033% | 8 | 0.483% | 0.511% |
| band/prefill | 14 | -0.022% | 8 | 0.276% | 0.179% |
| band/all | 28 | -0.027% | 16 | 0.483% | 0.511% |
| mode/CuteDSL MXFP4x8 | 6 | -0.011% | 3 | 0.276% | 0.189% |
| mode/CuteDSL MXFP8 | 4 | -0.107% | 4 | 0.164% | 0.096% |
| mode/CuteDSL PER-TOKEN | 8 | +0.010% | 3 | 0.242% | 0.511% |
| mode/CuteDSL W4A4 | 10 | -0.035% | 6 | 0.483% | 0.172% |
| model_topology/kimi-k3/tp | 6 | +0.033% | 1 | 0.139% | 0.189% |
| model_topology/nemo3-ultra/tp | 8 | -0.042% | 7 | 0.483% | 0.511% |
| model_topology/v3/tp | 8 | -0.066% | 5 | 0.276% | 0.160% |
| model_topology/v41-flash/ep | 2 | -0.061% | 1 | 0.047% | 0.056% |
| model_topology/v41-flash/tp | 4 | +0.007% | 2 | 0.267% | 0.179% |
| model_topology_mode/kimi-k3/tp/CuteDSL MXFP4x8 | 2 | +0.120% | 0 | 0.139% | 0.189% |
| model_topology_mode/kimi-k3/tp/CuteDSL PER-TOKEN | 2 | +0.018% | 0 | 0.022% | 0.036% |
| model_topology_mode/kimi-k3/tp/CuteDSL W4A4 | 2 | -0.040% | 1 | 0.038% | 0.172% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP4x8 | 2 | -0.145% | 2 | 0.152% | 0.075% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP8 | 2 | -0.057% | 2 | 0.164% | 0.061% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 2 | +0.131% | 1 | 0.066% | 0.511% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL W4A4 | 2 | -0.097% | 2 | 0.483% | 0.082% |
| model_topology_mode/v3/tp/CuteDSL MXFP4x8 | 2 | -0.007% | 1 | 0.276% | 0.160% |
| model_topology_mode/v3/tp/CuteDSL MXFP8 | 2 | -0.157% | 2 | 0.031% | 0.096% |
| model_topology_mode/v3/tp/CuteDSL PER-TOKEN | 2 | -0.111% | 1 | 0.124% | 0.111% |
| model_topology_mode/v3/tp/CuteDSL W4A4 | 2 | +0.012% | 1 | 0.168% | 0.122% |
| model_topology_mode/v41-flash/ep/CuteDSL W4A4 | 2 | -0.061% | 1 | 0.047% | 0.056% |
| model_topology_mode/v41-flash/tp/CuteDSL PER-TOKEN | 2 | +0.004% | 1 | 0.242% | 0.179% |
| model_topology_mode/v41-flash/tp/CuteDSL W4A4 | 2 | +0.010% | 1 | 0.267% | 0.162% |
| implementation/swap_ab | 28 | -0.027% | 16 | 0.483% | 0.511% |
