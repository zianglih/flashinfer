| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 36 | +0.205% | 9 | 0.613% | 2.600% |
| band/middle | 36 | +0.041% | 11 | 0.593% | 0.506% |
| band/prefill | 36 | +0.073% | 13 | 4.059% | 9.331% |
| band/all | 108 | +0.106% | 33 | 4.059% | 9.331% |
| mode/CuteDSL MXFP4x8 | 21 | +0.022% | 6 | 3.512% | 5.345% |
| mode/CuteDSL MXFP8 | 15 | +0.255% | 6 | 3.596% | 9.331% |
| mode/CuteDSL PER-TOKEN | 24 | +0.030% | 7 | 3.882% | 0.453% |
| mode/CuteDSL W4A16 | 24 | +0.211% | 6 | 4.059% | 2.600% |
| mode/CuteDSL W4A4 | 24 | +0.057% | 8 | 1.526% | 2.914% |
| model_topology/kimi-k3/ep | 12 | -0.235% | 4 | 3.882% | 0.476% |
| model_topology/kimi-k3/tp | 12 | +0.145% | 2 | 0.696% | 1.557% |
| model_topology/nemo3-ultra/ep | 15 | +0.374% | 3 | 2.589% | 9.331% |
| model_topology/nemo3-ultra/tp | 15 | +0.142% | 4 | 1.481% | 2.818% |
| model_topology/v3/ep | 15 | +0.369% | 2 | 4.059% | 4.243% |
| model_topology/v3/tp | 15 | +0.030% | 6 | 1.775% | 0.453% |
| model_topology/v41-flash/ep | 15 | +0.009% | 6 | 3.357% | 4.597% |
| model_topology/v41-flash/tp | 9 | -0.143% | 6 | 0.154% | 0.217% |
| model_topology_mode/kimi-k3/ep/CuteDSL MXFP4x8 | 3 | -1.429% | 1 | 3.512% | 0.233% |
| model_topology_mode/kimi-k3/ep/CuteDSL PER-TOKEN | 3 | -0.089% | 1 | 3.882% | 0.143% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A16 | 3 | +0.697% | 0 | 0.325% | 0.196% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A4 | 3 | -0.108% | 2 | 1.526% | 0.476% |
| model_topology_mode/kimi-k3/tp/CuteDSL MXFP4x8 | 3 | +0.063% | 0 | 0.289% | 0.869% |
| model_topology_mode/kimi-k3/tp/CuteDSL PER-TOKEN | 3 | +0.032% | 1 | 0.111% | 0.388% |
| model_topology_mode/kimi-k3/tp/CuteDSL W4A16 | 3 | +0.201% | 1 | 0.417% | 1.557% |
| model_topology_mode/kimi-k3/tp/CuteDSL W4A4 | 3 | +0.283% | 0 | 0.696% | 0.223% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP4x8 | 3 | +0.412% | 0 | 1.896% | 5.345% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP8 | 3 | +1.355% | 1 | 0.984% | 9.331% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL PER-TOKEN | 3 | +0.061% | 0 | 0.405% | 0.081% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A16 | 3 | -0.317% | 1 | 2.589% | 1.340% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 3 | +0.367% | 1 | 0.086% | 2.099% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP4x8 | 3 | +0.605% | 1 | 0.360% | 2.818% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP8 | 3 | +0.360% | 0 | 1.481% | 0.460% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 3 | +0.044% | 0 | 0.140% | 0.285% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL W4A16 | 3 | -0.326% | 2 | 0.721% | 0.168% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL W4A4 | 3 | +0.031% | 1 | 0.134% | 0.038% |
| model_topology_mode/v3/ep/CuteDSL MXFP4x8 | 3 | +0.691% | 1 | 2.531% | 0.793% |
| model_topology_mode/v3/ep/CuteDSL MXFP8 | 3 | +0.078% | 0 | 3.596% | 4.243% |
| model_topology_mode/v3/ep/CuteDSL PER-TOKEN | 3 | +0.172% | 0 | 0.613% | 0.453% |
| model_topology_mode/v3/ep/CuteDSL W4A16 | 3 | +0.833% | 0 | 4.059% | 2.600% |
| model_topology_mode/v3/ep/CuteDSL W4A4 | 3 | +0.074% | 1 | 0.593% | 0.506% |
| model_topology_mode/v3/tp/CuteDSL MXFP4x8 | 3 | -0.286% | 2 | 1.775% | 0.241% |
| model_topology_mode/v3/tp/CuteDSL MXFP8 | 3 | +0.019% | 2 | 0.668% | 0.335% |
| model_topology_mode/v3/tp/CuteDSL PER-TOKEN | 3 | +0.078% | 1 | 0.159% | 0.237% |
| model_topology_mode/v3/tp/CuteDSL W4A16 | 3 | +0.313% | 0 | 0.750% | 0.453% |
| model_topology_mode/v3/tp/CuteDSL W4A4 | 3 | +0.025% | 1 | 0.176% | 0.225% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP4x8 | 3 | +0.116% | 1 | 0.321% | 0.270% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP8 | 3 | -0.526% | 3 | 3.357% | 4.597% |
| model_topology_mode/v41-flash/ep/CuteDSL PER-TOKEN | 3 | -0.025% | 1 | 0.303% | 0.123% |
| model_topology_mode/v41-flash/ep/CuteDSL W4A16 | 3 | +0.731% | 0 | 1.712% | 1.285% |
| model_topology_mode/v41-flash/ep/CuteDSL W4A4 | 3 | -0.249% | 1 | 0.649% | 2.914% |
| model_topology_mode/v41-flash/tp/CuteDSL PER-TOKEN | 3 | -0.031% | 3 | 0.078% | 0.086% |
| model_topology_mode/v41-flash/tp/CuteDSL W4A16 | 3 | -0.436% | 2 | 0.154% | 0.217% |
| model_topology_mode/v41-flash/tp/CuteDSL W4A4 | 3 | +0.039% | 1 | 0.139% | 0.074% |
| implementation/swap_ab | 84 | +0.076% | 27 | 3.882% | 9.331% |
| implementation/w4a16 | 24 | +0.211% | 6 | 4.059% | 2.600% |
