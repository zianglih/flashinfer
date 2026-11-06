# Terminal PDL: separate reverse-order follow-up

Original CAAC and follow-up ACCA are separate observations, on the same original physicalGPU per case. All original losses and follow-up results retained. Actual returned native libraries bind ELF/PTX/SASS before launch, options unchanged; no reliance on symbol names alone. No clock lock, sample trimming, retuning or combined replacement ratio.

| Case / order | Phase 0 µs | Phase 1 µs | Phase 2 µs | Phase 3 µs | Speedup | C spread | A spread |
|---|---:|---:|---:|---:|---:|---:|---:|
| ep-kimi-k3-mxfp / original_caac | 0-control: 1074.534 | 1-candidate: 1103.814 | 2-candidate: 1098.407 | 3-control: 1070.005 | -2.6192% | 0.4232% | 0.4923% |
| ep-kimi-k3-mxfp / followup_acca | 0-candidate: 1114.389 | 1-control: 1083.622 | 2-control: 1038.438 | 3-candidate: 1094.918 | -3.9672% | 4.3512% | 1.7784% |
| tp-nemo3-ultra-mxfp / original_caac | 0-control: 1273.418 | 1-candidate: 1296.394 | 2-candidate: 1292.682 | 3-control: 1264.073 | -1.9930% | 0.7392% | 0.2872% |
| tp-nemo3-ultra-mxfp / followup_acca | 0-candidate: 1287.081 | 1-control: 1273.561 | 2-control: 1278.138 | 3-candidate: 1293.113 | -1.1043% | 0.3593% | 0.4687% |
| tp-v41-flash-per-token / original_caac | 0-control: 1279.403 | 1-candidate: 1285.676 | 2-candidate: 1284.972 | 3-control: 1279.819 | -0.4445% | 0.0325% | 0.0548% |
| tp-v41-flash-per-token / followup_acca | 0-candidate: 1287.099 | 1-control: 1282.315 | 2-control: 1282.491 | 3-candidate: 1287.083 | -0.3642% | 0.0137% | 0.0012% |

All three FC1 native images are byte-identical between arms; all 24 native captures have zero driver local bytes and no LDL/STL sites. N3U candidate FC2 and V41F control FC2 each have two captured images with identical PTX/resources/control words and 9/7 changed uniform-register operand sites respectively; both images remain preserved. Full per-phase components, quartiles, resource/image/source bindings are retained in `comparison.json`.
