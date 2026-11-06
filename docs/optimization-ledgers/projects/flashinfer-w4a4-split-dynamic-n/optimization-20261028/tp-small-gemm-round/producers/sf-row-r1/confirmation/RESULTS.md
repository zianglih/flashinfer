# SF row formula confirmation

Four focused C-A-A-C repeats used the original physical GPU per cell, saved winners/routes, public API and standard100-sample CUPTI medians. These supplement, and do not replace, the original72-cell result.

| Cell | Original | Repeat | Control spread | Candidate spread |
|---|---:|---:|---:|---:|
| EP v3 CuteDSL MXFP4x8 T16384 | -2.067% | +0.169% | 0.554% | 1.453% |
| EP v3 CuteDSL W4A4 T4 | -0.526% | -0.422% | 0.068% | 0.034% |
| TP nemo3-ultra CuteDSL MXFP8 T16384 | -1.444% | -0.510% | 0.885% | 2.614% |
| TP nemo3-ultra CuteDSL W4A4 T16384 | +0.994% | +0.801% | 0.130% | 0.083% |

The V3 prefill negative did not repeat. The V3 W4A4 decode cost repeats at approximately0.4–0.5%, while N3U TP W4A4 prefill repeats at approximately0.8–1.0% faster. N3U TP MXFP8 has inter-pass variation larger than its median delta; no stable source-specific slowdown is established. Retention remains dependent on the final composition screen.

Raw evidence: `perf-evidence/perf-audit.json`, `perf-evidence/perf-cells.csv`; archive/hash verification: `perf-evidence-verification.json`.
