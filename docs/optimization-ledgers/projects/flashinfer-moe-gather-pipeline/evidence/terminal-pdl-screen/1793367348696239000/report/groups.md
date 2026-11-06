| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 28 | +0.090% | 9 | 0.379% | 0.399% |
| band/prefill | 28 | -0.164% | 16 | 5.918% | 6.056% |
| band/all | 56 | -0.037% | 25 | 5.918% | 6.056% |
| mode/CuteDSL MXFP4x8 | 14 | -0.060% | 7 | 2.494% | 4.644% |
| mode/CuteDSL MXFP8 | 10 | -0.030% | 3 | 4.562% | 3.667% |
| mode/CuteDSL PER-TOKEN | 16 | -0.086% | 8 | 0.354% | 4.143% |
| mode/CuteDSL W4A4 | 16 | +0.026% | 7 | 5.918% | 6.056% |
| model_topology/kimi-k3/ep | 6 | -0.783% | 5 | 5.918% | 6.056% |
| model_topology/kimi-k3/tp | 6 | -0.044% | 4 | 2.494% | 0.276% |
| model_topology/nemo3-ultra/ep | 8 | +0.700% | 1 | 1.511% | 4.598% |
| model_topology/nemo3-ultra/tp | 8 | -0.300% | 3 | 1.947% | 0.287% |
| model_topology/v3/ep | 8 | +0.180% | 3 | 0.987% | 4.644% |
| model_topology/v3/tp | 8 | +0.044% | 1 | 1.684% | 1.385% |
| model_topology/v41-flash/ep | 8 | -0.231% | 6 | 4.562% | 2.990% |
| model_topology/v41-flash/tp | 4 | -0.055% | 2 | 0.328% | 0.399% |
| model_topology_mode/kimi-k3/ep/CuteDSL MXFP4x8 | 2 | -1.347% | 2 | 0.423% | 0.492% |
| model_topology_mode/kimi-k3/ep/CuteDSL PER-TOKEN | 2 | -0.925% | 1 | 0.198% | 4.143% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A4 | 2 | -0.073% | 2 | 5.918% | 6.056% |
| model_topology_mode/kimi-k3/tp/CuteDSL MXFP4x8 | 2 | -0.082% | 1 | 2.494% | 0.276% |
| model_topology_mode/kimi-k3/tp/CuteDSL PER-TOKEN | 2 | +0.025% | 1 | 0.239% | 0.042% |
| model_topology_mode/kimi-k3/tp/CuteDSL W4A4 | 2 | -0.075% | 2 | 0.303% | 0.075% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP4x8 | 2 | +1.772% | 0 | 0.306% | 4.598% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP8 | 2 | +0.852% | 0 | 1.511% | 2.015% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL PER-TOKEN | 2 | +0.061% | 1 | 0.161% | 0.282% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 2 | +0.124% | 0 | 0.379% | 0.335% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP4x8 | 2 | -0.346% | 1 | 1.947% | 0.273% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP8 | 2 | -0.957% | 1 | 0.739% | 0.287% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 2 | +0.043% | 0 | 0.249% | 0.100% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL W4A4 | 2 | +0.063% | 1 | 0.199% | 0.040% |
| model_topology_mode/v3/ep/CuteDSL MXFP4x8 | 2 | -0.478% | 1 | 0.987% | 4.644% |
| model_topology_mode/v3/ep/CuteDSL MXFP8 | 2 | +0.779% | 0 | 0.203% | 3.667% |
| model_topology_mode/v3/ep/CuteDSL PER-TOKEN | 2 | +0.441% | 1 | 0.100% | 0.036% |
| model_topology_mode/v3/ep/CuteDSL W4A4 | 2 | -0.020% | 1 | 0.284% | 0.242% |
| model_topology_mode/v3/tp/CuteDSL MXFP4x8 | 2 | +0.106% | 0 | 1.684% | 1.385% |
| model_topology_mode/v3/tp/CuteDSL MXFP8 | 2 | +0.067% | 0 | 0.635% | 0.107% |
| model_topology_mode/v3/tp/CuteDSL PER-TOKEN | 2 | -0.018% | 1 | 0.354% | 0.276% |
| model_topology_mode/v3/tp/CuteDSL W4A4 | 2 | +0.022% | 0 | 0.362% | 0.044% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP4x8 | 2 | -0.020% | 2 | 0.049% | 1.270% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP8 | 2 | -0.874% | 2 | 4.562% | 2.990% |
| model_topology_mode/v41-flash/ep/CuteDSL PER-TOKEN | 2 | -0.076% | 1 | 0.170% | 0.209% |
| model_topology_mode/v41-flash/ep/CuteDSL W4A4 | 2 | +0.047% | 1 | 1.130% | 1.503% |
| model_topology_mode/v41-flash/tp/CuteDSL PER-TOKEN | 2 | -0.233% | 2 | 0.041% | 0.399% |
| model_topology_mode/v41-flash/tp/CuteDSL W4A4 | 2 | +0.123% | 0 | 0.328% | 0.009% |
| implementation/swap_ab | 56 | -0.037% | 25 | 5.918% | 6.056% |
