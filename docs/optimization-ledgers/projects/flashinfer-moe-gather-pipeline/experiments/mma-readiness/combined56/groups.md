| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| all | 56 | -0.036% | 36 | 0.483% | 0.511% |
| decode | 28 | -0.031% | 18 | 0.483% | 0.511% |
| prefill | 28 | -0.041% | 18 | 0.449% | 0.502% |
| mode/CuteDSL MXFP4x8 | 14 | -0.067% | 11 | 0.430% | 0.254% |
| mode/CuteDSL MXFP8 | 10 | -0.041% | 7 | 0.164% | 0.172% |
| mode/CuteDSL PER-TOKEN | 16 | -0.023% | 9 | 0.449% | 0.511% |
| mode/CuteDSL W4A4 | 16 | -0.020% | 9 | 0.483% | 0.172% |
| model_topology/kimi-k3/ep | 6 | +0.045% | 3 | 0.449% | 0.502% |
| model_topology/kimi-k3/tp | 6 | +0.033% | 1 | 0.139% | 0.189% |
| model_topology/nemo3-ultra/ep | 8 | -0.065% | 7 | 0.175% | 0.172% |
| model_topology/nemo3-ultra/tp | 8 | -0.042% | 7 | 0.483% | 0.511% |
| model_topology/v3/ep | 8 | -0.113% | 7 | 0.212% | 0.131% |
| model_topology/v3/tp | 8 | -0.066% | 5 | 0.276% | 0.160% |
| model_topology/v41-flash/ep | 8 | -0.030% | 4 | 0.111% | 0.248% |
| model_topology/v41-flash/tp | 4 | +0.007% | 2 | 0.267% | 0.179% |
| model_topology_mode/kimi-k3/ep/CuteDSL MXFP4x8 | 2 | -0.013% | 2 | 0.430% | 0.254% |
| model_topology_mode/kimi-k3/ep/CuteDSL PER-TOKEN | 2 | +0.017% | 1 | 0.449% | 0.502% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A4 | 2 | +0.131% | 0 | 0.147% | 0.063% |
| model_topology_mode/kimi-k3/tp/CuteDSL MXFP4x8 | 2 | +0.120% | 0 | 0.139% | 0.189% |
| model_topology_mode/kimi-k3/tp/CuteDSL PER-TOKEN | 2 | +0.018% | 0 | 0.022% | 0.036% |
| model_topology_mode/kimi-k3/tp/CuteDSL W4A4 | 2 | -0.040% | 1 | 0.038% | 0.172% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP4x8 | 2 | -0.148% | 2 | 0.096% | 0.084% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP8 | 2 | +0.039% | 1 | 0.057% | 0.172% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL PER-TOKEN | 2 | -0.092% | 2 | 0.175% | 0.044% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 2 | -0.060% | 2 | 0.082% | 0.124% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP4x8 | 2 | -0.145% | 2 | 0.152% | 0.075% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP8 | 2 | -0.057% | 2 | 0.164% | 0.061% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 2 | +0.131% | 1 | 0.066% | 0.511% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL W4A4 | 2 | -0.097% | 2 | 0.483% | 0.082% |
| model_topology_mode/v3/ep/CuteDSL MXFP4x8 | 2 | -0.152% | 2 | 0.114% | 0.131% |
| model_topology_mode/v3/ep/CuteDSL MXFP8 | 2 | -0.083% | 2 | 0.127% | 0.022% |
| model_topology_mode/v3/ep/CuteDSL PER-TOKEN | 2 | -0.160% | 2 | 0.212% | 0.026% |
| model_topology_mode/v3/ep/CuteDSL W4A4 | 2 | -0.057% | 1 | 0.049% | 0.098% |
| model_topology_mode/v3/tp/CuteDSL MXFP4x8 | 2 | -0.007% | 1 | 0.276% | 0.160% |
| model_topology_mode/v3/tp/CuteDSL MXFP8 | 2 | -0.157% | 2 | 0.031% | 0.096% |
| model_topology_mode/v3/tp/CuteDSL PER-TOKEN | 2 | -0.111% | 1 | 0.124% | 0.111% |
| model_topology_mode/v3/tp/CuteDSL W4A4 | 2 | +0.012% | 1 | 0.168% | 0.122% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP4x8 | 2 | -0.123% | 2 | 0.111% | 0.248% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP8 | 2 | +0.055% | 0 | 0.053% | 0.072% |
| model_topology_mode/v41-flash/ep/CuteDSL PER-TOKEN | 2 | +0.009% | 1 | 0.004% | 0.074% |
| model_topology_mode/v41-flash/ep/CuteDSL W4A4 | 2 | -0.061% | 1 | 0.047% | 0.056% |
| model_topology_mode/v41-flash/tp/CuteDSL PER-TOKEN | 2 | +0.004% | 1 | 0.242% | 0.179% |
| model_topology_mode/v41-flash/tp/CuteDSL W4A4 | 2 | +0.010% | 1 | 0.267% | 0.162% |
