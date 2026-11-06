| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 28 | +0.009% | 14 | 0.357% | 0.252% |
| band/prefill | 28 | +0.014% | 12 | 0.402% | 0.509% |
| band/all | 56 | +0.011% | 26 | 0.402% | 0.509% |
| mode/CuteDSL MXFP4x8 | 14 | +0.069% | 3 | 0.357% | 0.200% |
| mode/CuteDSL MXFP8 | 10 | +0.013% | 4 | 0.323% | 0.259% |
| mode/CuteDSL PER-TOKEN | 16 | -0.090% | 12 | 0.265% | 0.509% |
| mode/CuteDSL W4A4 | 16 | +0.061% | 7 | 0.402% | 0.306% |
| model_topology/kimi-k3/ep | 6 | -0.055% | 4 | 0.402% | 0.509% |
| model_topology/kimi-k3/tp | 6 | -0.016% | 2 | 0.229% | 0.200% |
| model_topology/nemo3-ultra/ep | 8 | +0.024% | 3 | 0.179% | 0.189% |
| model_topology/nemo3-ultra/tp | 8 | -0.033% | 5 | 0.304% | 0.259% |
| model_topology/v3/ep | 8 | +0.018% | 5 | 0.093% | 0.080% |
| model_topology/v3/tp | 8 | +0.037% | 3 | 0.357% | 0.189% |
| model_topology/v41-flash/ep | 8 | +0.024% | 4 | 0.306% | 0.188% |
| model_topology/v41-flash/tp | 4 | +0.124% | 0 | 0.265% | 0.252% |
| model_topology_mode/kimi-k3/ep/CuteDSL MXFP4x8 | 2 | -0.030% | 2 | 0.270% | 0.086% |
| model_topology_mode/kimi-k3/ep/CuteDSL PER-TOKEN | 2 | -0.190% | 2 | 0.115% | 0.509% |
| model_topology_mode/kimi-k3/ep/CuteDSL W4A4 | 2 | +0.054% | 0 | 0.402% | 0.306% |
| model_topology_mode/kimi-k3/tp/CuteDSL MXFP4x8 | 2 | +0.012% | 0 | 0.229% | 0.200% |
| model_topology_mode/kimi-k3/tp/CuteDSL PER-TOKEN | 2 | -0.581% | 2 | 0.225% | 0.162% |
| model_topology_mode/kimi-k3/tp/CuteDSL W4A4 | 2 | +0.524% | 0 | 0.159% | 0.160% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP4x8 | 2 | +0.045% | 0 | 0.179% | 0.064% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL MXFP8 | 2 | +0.059% | 0 | 0.019% | 0.115% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL PER-TOKEN | 2 | -0.009% | 2 | 0.015% | 0.189% |
| model_topology_mode/nemo3-ultra/ep/CuteDSL W4A4 | 2 | -0.001% | 1 | 0.089% | 0.046% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP4x8 | 2 | +0.016% | 0 | 0.304% | 0.114% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL MXFP8 | 2 | +0.006% | 1 | 0.046% | 0.259% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL PER-TOKEN | 2 | -0.034% | 2 | 0.127% | 0.247% |
| model_topology_mode/nemo3-ultra/tp/CuteDSL W4A4 | 2 | -0.119% | 2 | 0.221% | 0.235% |
| model_topology_mode/v3/ep/CuteDSL MXFP4x8 | 2 | +0.098% | 1 | 0.093% | 0.007% |
| model_topology_mode/v3/ep/CuteDSL MXFP8 | 2 | +0.019% | 1 | 0.066% | 0.019% |
| model_topology_mode/v3/ep/CuteDSL PER-TOKEN | 2 | +0.040% | 1 | 0.079% | 0.053% |
| model_topology_mode/v3/ep/CuteDSL W4A4 | 2 | -0.085% | 2 | 0.065% | 0.080% |
| model_topology_mode/v3/tp/CuteDSL MXFP4x8 | 2 | +0.183% | 0 | 0.357% | 0.156% |
| model_topology_mode/v3/tp/CuteDSL MXFP8 | 2 | +0.021% | 0 | 0.323% | 0.189% |
| model_topology_mode/v3/tp/CuteDSL PER-TOKEN | 2 | -0.007% | 1 | 0.042% | 0.097% |
| model_topology_mode/v3/tp/CuteDSL W4A4 | 2 | -0.049% | 2 | 0.227% | 0.037% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP4x8 | 2 | +0.158% | 0 | 0.302% | 0.037% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP8 | 2 | -0.039% | 2 | 0.067% | 0.121% |
| model_topology_mode/v41-flash/ep/CuteDSL PER-TOKEN | 2 | -0.081% | 2 | 0.104% | 0.038% |
| model_topology_mode/v41-flash/ep/CuteDSL W4A4 | 2 | +0.059% | 0 | 0.306% | 0.188% |
| model_topology_mode/v41-flash/tp/CuteDSL PER-TOKEN | 2 | +0.143% | 0 | 0.265% | 0.056% |
| model_topology_mode/v41-flash/tp/CuteDSL W4A4 | 2 | +0.105% | 0 | 0.126% | 0.252% |
| implementation/swap_ab | 56 | +0.011% | 26 | 0.402% | 0.509% |
