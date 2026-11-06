| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 28 | -0.129% | 20 | 0.398% | 0.609% |
| band/prefill | 28 | +0.099% | 13 | 7.248% | 6.400% |
| band/all | 56 | -0.015% | 33 | 7.248% | 6.400% |
| mode/CuteDSL MXFP4x8 | 14 | -1.006% | 10 | 3.782% | 6.254% |
| mode/CuteDSL MXFP8 | 10 | -0.415% | 6 | 7.248% | 6.400% |
| mode/CuteDSL PER-TOKEN | 16 | +0.904% | 8 | 3.601% | 0.609% |
| mode/CuteDSL W4A4 | 16 | +0.194% | 9 | 2.211% | 0.922% |
| model_topology/kimi-k3/ep | 6 | -2.756% | 6 | 3.601% | 6.254% |
| model_topology/kimi-k3/tp | 6 | -0.752% | 5 | 2.287% | 1.884% |
| model_topology/nemo3-ultra/ep | 8 | +0.466% | 4 | 7.248% | 3.582% |
| model_topology/nemo3-ultra/tp | 8 | -0.899% | 5 | 0.398% | 1.169% |
| model_topology/v3/ep | 8 | +1.344% | 4 | 2.646% | 6.400% |
| model_topology/v3/tp | 8 | +0.046% | 4 | 0.874% | 0.699% |
| model_topology/v41-flash/ep | 8 | +1.202% | 4 | 3.782% | 4.461% |
| model_topology/v41-flash/tp | 4 | +0.844% | 1 | 0.080% | 0.103% |
| model_topology_mode/kimi-k3/ep/CuteDSL MXFP4x8 | 2 | -4.498% | 2 | 1.737% | 6.254% |
| model_topology_mode/kimi-k3/ep/CuteDSL PER-TOKEN | 2 | -1.591% | 2 | 3.601% | 0.508% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A4 | 2 | -2.154% | 2 | 2.211% | 0.922% |
| model_topology_mode/kimi-k3/tp/CuteDSL MXFP4x8 | 2 | -2.120% | 2 | 2.287% | 1.884% |
| model_topology_mode/kimi-k3/tp/CuteDSL PER-TOKEN | 2 | +0.944% | 1 | 0.018% | 0.108% |
| model_topology_mode/kimi-k3/tp/CuteDSL W4A4 | 2 | -1.056% | 2 | 0.047% | 0.084% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP4x8 | 2 | -0.394% | 2 | 3.023% | 3.582% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP8 | 2 | -2.513% | 1 | 7.248% | 0.443% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL PER-TOKEN | 2 | +2.524% | 0 | 0.049% | 0.083% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 2 | +2.335% | 1 | 0.172% | 0.156% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP4x8 | 2 | -1.422% | 1 | 0.398% | 1.169% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP8 | 2 | -0.542% | 1 | 0.062% | 0.840% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 2 | +0.869% | 1 | 0.221% | 0.609% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL W4A4 | 2 | -2.469% | 2 | 0.193% | 0.179% |
| model_topology_mode/v3/ep/CuteDSL MXFP4x8 | 2 | +1.435% | 1 | 2.646% | 0.433% |
| model_topology_mode/v3/ep/CuteDSL MXFP8 | 2 | +1.401% | 1 | 0.810% | 6.400% |
| model_topology_mode/v3/ep/CuteDSL PER-TOKEN | 2 | +0.645% | 1 | 0.059% | 0.120% |
| model_topology_mode/v3/ep/CuteDSL W4A4 | 2 | +1.897% | 1 | 0.032% | 0.125% |
| model_topology_mode/v3/tp/CuteDSL MXFP4x8 | 2 | -0.547% | 2 | 0.169% | 0.699% |
| model_topology_mode/v3/tp/CuteDSL MXFP8 | 2 | -0.129% | 1 | 0.874% | 0.288% |
| model_topology_mode/v3/tp/CuteDSL PER-TOKEN | 2 | +0.425% | 1 | 0.151% | 0.013% |
| model_topology_mode/v3/tp/CuteDSL W4A4 | 2 | +0.439% | 0 | 0.030% | 0.028% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP4x8 | 2 | +0.619% | 0 | 3.782% | 4.461% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP8 | 2 | -0.253% | 2 | 0.816% | 0.042% |
| model_topology_mode/v41-flash/ep/CuteDSL PER-TOKEN | 2 | +2.095% | 1 | 0.046% | 0.061% |
| model_topology_mode/v41-flash/ep/CuteDSL W4A4 | 2 | +2.370% | 1 | 0.126% | 0.317% |
| model_topology_mode/v41-flash/tp/CuteDSL PER-TOKEN | 2 | +1.372% | 1 | 0.066% | 0.089% |
| model_topology_mode/v41-flash/tp/CuteDSL W4A4 | 2 | +0.320% | 0 | 0.080% | 0.103% |
| implementation/swap_ab | 56 | -0.015% | 33 | 7.248% | 6.400% |
