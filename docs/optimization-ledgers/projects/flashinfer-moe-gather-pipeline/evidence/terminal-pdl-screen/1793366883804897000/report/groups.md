| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 5 | +0.045% | 2 | 0.228% | 0.302% |
| band/prefill | 5 | +0.054% | 3 | 5.918% | 6.056% |
| band/all | 10 | +0.050% | 5 | 5.918% | 6.056% |
| mode/CuteDSL MXFP4x8 | 4 | +0.201% | 2 | 0.423% | 4.598% |
| mode/CuteDSL MXFP8 | 2 | +0.852% | 0 | 1.511% | 2.015% |
| mode/CuteDSL PER-TOKEN | 2 | -0.925% | 1 | 0.198% | 4.143% |
| mode/CuteDSL W4A4 | 2 | -0.073% | 2 | 5.918% | 6.056% |
| model_topology/kimi-k3/ep | 6 | -0.783% | 5 | 5.918% | 6.056% |
| model_topology/nemo3-ultra/ep | 4 | +1.311% | 0 | 1.511% | 4.598% |
| model_topology_mode/kimi-k3/ep/CuteDSL MXFP4x8 | 2 | -1.347% | 2 | 0.423% | 0.492% |
| model_topology_mode/kimi-k3/ep/CuteDSL PER-TOKEN | 2 | -0.925% | 1 | 0.198% | 4.143% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A4 | 2 | -0.073% | 2 | 5.918% | 6.056% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP4x8 | 2 | +1.772% | 0 | 0.306% | 4.598% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP8 | 2 | +0.852% | 0 | 1.511% | 2.015% |
| implementation/swap_ab | 10 | +0.050% | 5 | 5.918% | 6.056% |
