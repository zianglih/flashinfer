| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 28 | -0.056% | 10 | 0.415% | 0.256% |
| band/prefill | 28 | -0.375% | 16 | 6.787% | 6.454% |
| band/all | 56 | -0.216% | 26 | 6.787% | 6.454% |
| mode/CuteDSL MXFP4x8 | 14 | -0.225% | 6 | 6.787% | 6.454% |
| mode/CuteDSL MXFP8 | 10 | -0.348% | 4 | 2.062% | 4.602% |
| mode/CuteDSL PER-TOKEN | 16 | -0.415% | 10 | 0.793% | 0.212% |
| mode/CuteDSL W4A4 | 16 | +0.074% | 6 | 0.718% | 1.180% |
| model_topology/kimi-k3/ep | 6 | +0.585% | 3 | 3.343% | 1.959% |
| model_topology/kimi-k3/tp | 6 | -0.648% | 3 | 0.718% | 0.405% |
| model_topology/nemo3-ultra/ep | 8 | -0.603% | 6 | 2.165% | 4.593% |
| model_topology/nemo3-ultra/tp | 8 | -0.281% | 3 | 1.377% | 0.963% |
| model_topology/v3/ep | 8 | -0.558% | 3 | 6.787% | 6.454% |
| model_topology/v3/tp | 8 | -0.568% | 5 | 0.246% | 0.669% |
| model_topology/v41-flash/ep | 8 | +0.550% | 2 | 1.419% | 2.517% |
| model_topology/v41-flash/tp | 4 | +0.009% | 1 | 0.116% | 0.256% |
| model_topology_mode/kimi-k3/ep/CuteDSL MXFP4x8 | 2 | -0.021% | 1 | 3.343% | 1.959% |
| model_topology_mode/kimi-k3/ep/CuteDSL PER-TOKEN | 2 | +1.780% | 1 | 0.793% | 0.159% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A4 | 2 | +0.007% | 1 | 0.425% | 1.180% |
| model_topology_mode/kimi-k3/tp/CuteDSL MXFP4x8 | 2 | +0.118% | 0 | 0.392% | 0.405% |
| model_topology_mode/kimi-k3/tp/CuteDSL PER-TOKEN | 2 | -1.645% | 2 | 0.145% | 0.071% |
| model_topology_mode/kimi-k3/tp/CuteDSL W4A4 | 2 | -0.410% | 1 | 0.718% | 0.192% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP4x8 | 2 | -2.012% | 2 | 2.165% | 4.593% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP8 | 2 | +0.308% | 1 | 2.062% | 0.619% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL PER-TOKEN | 2 | -0.214% | 2 | 0.146% | 0.086% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 2 | -0.480% | 1 | 0.062% | 0.074% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP4x8 | 2 | -0.110% | 1 | 0.064% | 0.963% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP8 | 2 | +0.258% | 0 | 1.377% | 0.915% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 2 | -0.947% | 1 | 0.233% | 0.064% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL W4A4 | 2 | -0.320% | 1 | 0.415% | 0.125% |
| model_topology_mode/v3/ep/CuteDSL MXFP4x8 | 2 | +0.377% | 0 | 6.787% | 6.454% |
| model_topology_mode/v3/ep/CuteDSL MXFP8 | 2 | -3.213% | 2 | 0.428% | 4.602% |
| model_topology_mode/v3/ep/CuteDSL PER-TOKEN | 2 | +0.098% | 0 | 0.105% | 0.212% |
| model_topology_mode/v3/ep/CuteDSL W4A4 | 2 | +0.553% | 1 | 0.064% | 0.146% |
| model_topology_mode/v3/tp/CuteDSL MXFP4x8 | 2 | +0.271% | 1 | 0.246% | 0.193% |
| model_topology_mode/v3/tp/CuteDSL MXFP8 | 2 | -0.123% | 1 | 0.139% | 0.669% |
| model_topology_mode/v3/tp/CuteDSL PER-TOKEN | 2 | -2.449% | 2 | 0.055% | 0.040% |
| model_topology_mode/v3/tp/CuteDSL W4A4 | 2 | +0.053% | 1 | 0.106% | 0.060% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP4x8 | 2 | -0.179% | 1 | 1.419% | 1.378% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP8 | 2 | +1.087% | 0 | 1.153% | 2.517% |
| model_topology_mode/v41-flash/ep/CuteDSL PER-TOKEN | 2 | +0.162% | 1 | 0.466% | 0.062% |
| model_topology_mode/v41-flash/ep/CuteDSL W4A4 | 2 | +1.137% | 0 | 0.303% | 0.211% |
| model_topology_mode/v41-flash/tp/CuteDSL PER-TOKEN | 2 | -0.044% | 1 | 0.033% | 0.028% |
| model_topology_mode/v41-flash/tp/CuteDSL W4A4 | 2 | +0.062% | 0 | 0.116% | 0.256% |
| implementation/swap_ab | 56 | -0.216% | 26 | 6.787% | 6.454% |
