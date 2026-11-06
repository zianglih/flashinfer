| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 28 | -0.078% | 14 | 0.287% | 0.227% |
| band/prefill | 28 | -0.413% | 18 | 6.002% | 5.286% |
| band/all | 56 | -0.246% | 32 | 6.002% | 5.286% |
| mode/CuteDSL MXFP4x8 | 14 | -0.616% | 9 | 6.002% | 5.286% |
| mode/CuteDSL MXFP8 | 10 | -0.090% | 5 | 5.462% | 4.895% |
| mode/CuteDSL PER-TOKEN | 16 | -0.319% | 11 | 2.329% | 1.056% |
| mode/CuteDSL W4A4 | 16 | +0.054% | 7 | 5.110% | 0.795% |
| model_topology/kimi-k3/ep | 6 | -0.016% | 3 | 5.110% | 1.800% |
| model_topology/kimi-k3/tp | 6 | -0.440% | 4 | 0.304% | 0.795% |
| model_topology/nemo3-ultra/ep | 8 | -0.935% | 5 | 5.462% | 0.644% |
| model_topology/nemo3-ultra/tp | 8 | -0.093% | 4 | 2.911% | 0.951% |
| model_topology/v3/ep | 8 | +0.121% | 7 | 4.928% | 5.286% |
| model_topology/v3/tp | 8 | -0.076% | 3 | 0.312% | 0.227% |
| model_topology/v41-flash/ep | 8 | -0.555% | 6 | 6.002% | 5.086% |
| model_topology/v41-flash/tp | 4 | +0.331% | 0 | 0.165% | 0.154% |
| model_topology_mode/kimi-k3/ep/CuteDSL MXFP4x8 | 2 | -0.001% | 1 | 3.868% | 1.800% |
| model_topology_mode/kimi-k3/ep/CuteDSL PER-TOKEN | 2 | -0.616% | 2 | 2.329% | 0.671% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A4 | 2 | +0.573% | 0 | 5.110% | 0.112% |
| model_topology_mode/kimi-k3/tp/CuteDSL MXFP4x8 | 2 | +0.052% | 1 | 0.209% | 0.375% |
| model_topology_mode/kimi-k3/tp/CuteDSL PER-TOKEN | 2 | -1.317% | 2 | 0.180% | 0.446% |
| model_topology_mode/kimi-k3/tp/CuteDSL W4A4 | 2 | -0.049% | 1 | 0.304% | 0.795% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP4x8 | 2 | -1.608% | 2 | 4.047% | 0.644% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP8 | 2 | -1.989% | 1 | 5.462% | 0.376% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL PER-TOKEN | 2 | -0.102% | 1 | 0.236% | 0.144% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 2 | -0.026% | 1 | 0.062% | 0.184% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP4x8 | 2 | -0.208% | 1 | 0.687% | 0.809% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP8 | 2 | +0.425% | 1 | 2.911% | 0.951% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 2 | -0.262% | 1 | 0.065% | 0.039% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL W4A4 | 2 | -0.327% | 1 | 0.055% | 0.110% |
| model_topology_mode/v3/ep/CuteDSL MXFP4x8 | 2 | -0.909% | 2 | 1.430% | 5.286% |
| model_topology_mode/v3/ep/CuteDSL MXFP8 | 2 | +1.812% | 1 | 4.928% | 1.256% |
| model_topology_mode/v3/ep/CuteDSL PER-TOKEN | 2 | -0.335% | 2 | 0.090% | 0.120% |
| model_topology_mode/v3/ep/CuteDSL W4A4 | 2 | -0.065% | 2 | 0.099% | 0.126% |
| model_topology_mode/v3/tp/CuteDSL MXFP4x8 | 2 | -0.162% | 1 | 0.093% | 0.101% |
| model_topology_mode/v3/tp/CuteDSL MXFP8 | 2 | -0.373% | 1 | 0.312% | 0.178% |
| model_topology_mode/v3/tp/CuteDSL PER-TOKEN | 2 | +0.007% | 1 | 0.151% | 0.151% |
| model_topology_mode/v3/tp/CuteDSL W4A4 | 2 | +0.225% | 0 | 0.287% | 0.227% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP4x8 | 2 | -1.458% | 1 | 6.002% | 5.086% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP8 | 2 | -0.284% | 1 | 3.365% | 4.895% |
| model_topology_mode/v41-flash/ep/CuteDSL PER-TOKEN | 2 | -0.230% | 2 | 0.867% | 1.056% |
| model_topology_mode/v41-flash/ep/CuteDSL W4A4 | 2 | -0.241% | 2 | 0.102% | 0.670% |
| model_topology_mode/v41-flash/tp/CuteDSL PER-TOKEN | 2 | +0.314% | 0 | 0.021% | 0.154% |
| model_topology_mode/v41-flash/tp/CuteDSL W4A4 | 2 | +0.349% | 0 | 0.165% | 0.128% |
| implementation/swap_ab | 56 | -0.246% | 32 | 6.002% | 5.286% |
