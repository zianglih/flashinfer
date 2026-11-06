| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 30 | +0.100% | 10 | 0.433% | 0.507% |
| band/middle | 18 | +0.062% | 6 | 0.613% | 0.226% |
| band/prefill | 18 | +0.184% | 6 | 0.692% | 5.993% |
| band/all | 66 | +0.113% | 22 | 0.692% | 5.993% |
| mode/CuteDSL MXFP4x8 | 22 | -0.083% | 12 | 0.624% | 5.993% |
| mode/CuteDSL PER-TOKEN | 22 | +0.067% | 6 | 0.687% | 3.253% |
| mode/CuteDSL W4A4 | 22 | +0.355% | 4 | 0.692% | 3.135% |
| model_topology/kimi-k3/ep | 33 | -0.013% | 14 | 0.692% | 5.993% |
| model_topology/kimi-k3/tp | 33 | +0.238% | 8 | 0.613% | 2.929% |
| model_topology_mode/kimi-k3/ep/CuteDSL MXFP4x8 | 11 | -0.228% | 7 | 0.624% | 5.993% |
| model_topology_mode/kimi-k3/ep/CuteDSL PER-TOKEN | 11 | -0.085% | 4 | 0.687% | 3.253% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A4 | 11 | +0.276% | 3 | 0.692% | 3.135% |
| model_topology_mode/kimi-k3/tp/CuteDSL MXFP4x8 | 11 | +0.061% | 5 | 0.613% | 2.929% |
| model_topology_mode/kimi-k3/tp/CuteDSL PER-TOKEN | 11 | +0.220% | 2 | 0.433% | 0.507% |
| model_topology_mode/kimi-k3/tp/CuteDSL W4A4 | 11 | +0.433% | 1 | 0.372% | 0.748% |
| implementation/swap_ab | 66 | +0.113% | 22 | 0.692% | 5.993% |
