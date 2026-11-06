| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 28 | -0.018% | 16 | 0.816% | 0.401% |
| band/prefill | 28 | -0.163% | 18 | 7.466% | 5.494% |
| band/all | 56 | -0.091% | 34 | 7.466% | 5.494% |
| mode/CuteDSL MXFP4x8 | 14 | -0.309% | 9 | 2.769% | 4.028% |
| mode/CuteDSL MXFP8 | 10 | -0.296% | 8 | 7.466% | 1.689% |
| mode/CuteDSL PER-TOKEN | 16 | -0.034% | 8 | 3.228% | 4.092% |
| mode/CuteDSL W4A4 | 16 | +0.172% | 9 | 4.198% | 5.494% |
| model_topology/kimi-k3/ep | 6 | -0.005% | 5 | 4.198% | 5.494% |
| model_topology/kimi-k3/tp | 6 | +0.101% | 3 | 0.356% | 1.296% |
| model_topology/nemo3-ultra/ep | 8 | -0.299% | 4 | 0.148% | 2.529% |
| model_topology/nemo3-ultra/tp | 8 | -0.031% | 6 | 0.816% | 2.415% |
| model_topology/v3/ep | 8 | +0.114% | 4 | 7.466% | 1.209% |
| model_topology/v3/tp | 8 | +0.039% | 4 | 0.294% | 0.653% |
| model_topology/v41-flash/ep | 8 | -0.498% | 5 | 5.923% | 4.028% |
| model_topology/v41-flash/tp | 4 | -0.061% | 3 | 0.131% | 0.132% |
| model_topology_mode/kimi-k3/ep/CuteDSL MXFP4x8 | 2 | -1.041% | 2 | 2.769% | 1.001% |
| model_topology_mode/kimi-k3/ep/CuteDSL PER-TOKEN | 2 | -0.189% | 2 | 3.228% | 4.092% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A4 | 2 | +1.228% | 1 | 4.198% | 5.494% |
| model_topology_mode/kimi-k3/tp/CuteDSL MXFP4x8 | 2 | +0.461% | 1 | 0.356% | 0.873% |
| model_topology_mode/kimi-k3/tp/CuteDSL PER-TOKEN | 2 | +0.029% | 1 | 0.198% | 0.036% |
| model_topology_mode/kimi-k3/tp/CuteDSL W4A4 | 2 | -0.187% | 1 | 0.085% | 1.296% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP4x8 | 2 | -1.030% | 1 | 0.113% | 2.529% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP8 | 2 | -0.180% | 1 | 0.148% | 0.372% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL PER-TOKEN | 2 | -0.049% | 1 | 0.131% | 0.145% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 2 | +0.065% | 1 | 0.037% | 0.015% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP4x8 | 2 | -0.108% | 2 | 0.118% | 2.415% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP8 | 2 | -0.047% | 2 | 0.369% | 1.410% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 2 | +0.126% | 0 | 0.816% | 0.142% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL W4A4 | 2 | -0.096% | 2 | 0.168% | 0.070% |
| model_topology_mode/v3/ep/CuteDSL MXFP4x8 | 2 | +0.652% | 1 | 2.326% | 0.400% |
| model_topology_mode/v3/ep/CuteDSL MXFP8 | 2 | -0.165% | 1 | 7.466% | 1.209% |
| model_topology_mode/v3/ep/CuteDSL PER-TOKEN | 2 | +0.014% | 0 | 0.100% | 0.106% |
| model_topology_mode/v3/ep/CuteDSL W4A4 | 2 | -0.042% | 2 | 0.032% | 0.162% |
| model_topology_mode/v3/tp/CuteDSL MXFP4x8 | 2 | +0.286% | 0 | 0.294% | 0.146% |
| model_topology_mode/v3/tp/CuteDSL MXFP8 | 2 | -0.057% | 2 | 0.181% | 0.653% |
| model_topology_mode/v3/tp/CuteDSL PER-TOKEN | 2 | -0.026% | 1 | 0.153% | 0.104% |
| model_topology_mode/v3/tp/CuteDSL W4A4 | 2 | -0.045% | 1 | 0.121% | 0.273% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP4x8 | 2 | -1.359% | 2 | 2.053% | 4.028% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP8 | 2 | -1.027% | 2 | 5.923% | 1.689% |
| model_topology_mode/v41-flash/ep/CuteDSL PER-TOKEN | 2 | -0.016% | 1 | 1.198% | 0.540% |
| model_topology_mode/v41-flash/ep/CuteDSL W4A4 | 2 | +0.420% | 0 | 0.145% | 0.444% |
| model_topology_mode/v41-flash/tp/CuteDSL PER-TOKEN | 2 | -0.160% | 2 | 0.131% | 0.132% |
| model_topology_mode/v41-flash/tp/CuteDSL W4A4 | 2 | +0.039% | 1 | 0.070% | 0.126% |
| implementation/swap_ab | 56 | -0.091% | 34 | 7.466% | 5.494% |
