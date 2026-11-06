| Group | Cells | Speedup | Negative | Max C spread | Max A spread |
|---|---:|---:|---:|---:|---:|
| band/decode | 80 | -0.038% | 44 | 1.081% | 1.218% |
| band/middle | 48 | +0.009% | 28 | 0.447% | 0.573% |
| band/prefill | 48 | +0.025% | 23 | 6.458% | 4.295% |
| band/all | 176 | -0.008% | 95 | 6.458% | 4.295% |
| mode/CuteDSL MXFP4x8 | 33 | -0.090% | 21 | 1.654% | 1.218% |
| mode/CuteDSL MXFP8 | 33 | -0.121% | 19 | 5.119% | 1.002% |
| mode/CuteDSL PER-TOKEN | 44 | +0.018% | 21 | 0.515% | 0.563% |
| mode/CuteDSL W4A16 | 22 | +0.346% | 12 | 6.458% | 4.295% |
| mode/CuteDSL W4A4 | 44 | -0.065% | 22 | 0.636% | 1.328% |
| model_topology/v3/ep | 44 | -0.128% | 31 | 5.119% | 0.853% |
| model_topology/v3/tp | 44 | +0.034% | 17 | 0.599% | 1.218% |
| model_topology/v41-flash/ep | 55 | +0.013% | 34 | 6.458% | 4.295% |
| model_topology/v41-flash/tp | 33 | +0.060% | 13 | 3.439% | 2.875% |
| model_topology_mode/v3/ep/CuteDSL MXFP4x8 | 11 | -0.209% | 10 | 1.081% | 0.853% |
| model_topology_mode/v3/ep/CuteDSL MXFP8 | 11 | -0.279% | 7 | 5.119% | 0.400% |
| model_topology_mode/v3/ep/CuteDSL PER-TOKEN | 11 | -0.012% | 8 | 0.447% | 0.282% |
| model_topology_mode/v3/ep/CuteDSL W4A4 | 11 | -0.010% | 6 | 0.636% | 0.573% |
| model_topology_mode/v3/tp/CuteDSL MXFP4x8 | 11 | +0.102% | 4 | 0.368% | 1.218% |
| model_topology_mode/v3/tp/CuteDSL MXFP8 | 11 | +0.006% | 5 | 0.599% | 0.431% |
| model_topology_mode/v3/tp/CuteDSL PER-TOKEN | 11 | +0.018% | 4 | 0.198% | 0.160% |
| model_topology_mode/v3/tp/CuteDSL W4A4 | 11 | +0.010% | 4 | 0.241% | 0.302% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP4x8 | 11 | -0.163% | 7 | 1.654% | 0.618% |
| model_topology_mode/v41-flash/ep/CuteDSL MXFP8 | 11 | -0.089% | 7 | 0.376% | 1.002% |
| model_topology_mode/v41-flash/ep/CuteDSL PER-TOKEN | 11 | -0.004% | 6 | 0.515% | 0.563% |
| model_topology_mode/v41-flash/ep/CuteDSL W4A16 | 11 | +0.671% | 6 | 6.458% | 4.295% |
| model_topology_mode/v41-flash/ep/CuteDSL W4A4 | 11 | -0.347% | 8 | 0.324% | 1.328% |
| model_topology_mode/v41-flash/tp/CuteDSL PER-TOKEN | 11 | +0.071% | 3 | 0.355% | 0.219% |
| model_topology_mode/v41-flash/tp/CuteDSL W4A16 | 11 | +0.022% | 6 | 3.439% | 2.875% |
| model_topology_mode/v41-flash/tp/CuteDSL W4A4 | 11 | +0.087% | 4 | 0.204% | 0.183% |
| implementation/swap_ab | 154 | -0.059% | 83 | 5.119% | 1.328% |
| implementation/w4a16 | 22 | +0.346% | 12 | 6.458% | 4.295% |
