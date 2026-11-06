# hu15 staging and reducer trials

All three trials use retained `d01f074` A1 from the same hu-pdx-15 boot and the same original prefix study. These are serial comparisons; intervening runs and within-run drift remain visible. No hu59 timing was reused. All 13 tactics matched the control and all 104 finite rank outputs matched exactly for each trial. No candidate was promoted.

| Tokens | d01 A1 µs | CTA-ready µs | A1 / CTA | Dispatch-combine µs | A1 / dispatch | Recurrence µs | A1 / recurrence |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 65.6640 | 66.1130 | 0.993209× | 66.4805 | 0.987718× | 66.0645 | 0.993938× |
| 2 | 87.3285 | 92.9285 | 0.939739× | 90.9605 | 0.960071× | 84.0165 | 1.039421× |
| 4 | 96.5285 | 105.6000 | 0.914096× | 96.6085 | 0.999172× | 97.4880 | 0.990158× |
| 8 | 121.9200 | 127.7600 | 0.954289× | 121.2000 | 1.005941× | 121.1680 | 1.006206× |
| 16 | 132.0170 | 141.0720 | 0.935813× | 135.1040 | 0.977151× | 134.9440 | 0.978310× |
| 32 | 160.1920 | 168.5130 | 0.950621× | 161.2805 | 0.993251× | 156.9295 | 1.020790× |
| 64 | 183.0565 | 189.2340 | 0.967355× | 182.9605 | 1.000525× | 183.5685 | 0.997211× |
| 128 | 185.3935 | 196.1610 | 0.945109× | 187.8250 | 0.987054× | 187.9525 | 0.986385× |
| 256 | 190.2565 | 202.0485 | 0.941638× | 200.8485 | 0.947264× | 191.1040 | 0.995565× |
| 512 | 197.3120 | 207.8405 | 0.949343× | 195.6005 | 1.008750× | 192.5605 | 1.024675× |
| 4096 | 464.8015 | 479.1540 | 0.970046× | 459.9530 | 1.010541× | 461.2805 | 1.007633× |
| 8192 | 769.0255 | 781.4420 | 0.984111× | 801.0100 | 0.960070× | 776.2130 | 0.990740× |
| 16384 | 1496.6120 | 1484.0150 | 1.008488× | 1527.4945 | 0.979782× | 1483.9720 | 1.008518× |

Decode 4–512 geometric speedups: CTA readiness **0.944671×** (0/8 faster), Dispatch combine **0.989708×** (3/8 faster), Coordinate recurrence **0.999797×** (3/8 faster).

CTA readiness loses all decode rows. Dispatch combine loses 8K and 16K. Recurrence changes active-prefill medians by less than 1% with mixed signs; the 8K/16K quarter trends do not establish a repeatable benefit. Source proof that a change is inactive for a workload does not prove generated whole-kernel identity. Keep the original per-row results, including those inactive-path variations.

Each namespace preserves sealed source/runtime/sample/output evidence, its exact same-node control binding and process/GPU closure. The local compact bundles plus SHA-identical audited output bytes reconstruct all 169 original member files per trial. Original gzip bytes remain remote and are explicitly not verified locally.

Evidence:
- CTA readiness: `cta-ready-staging/decode13-benchmark-hu15-recovery/comparison.json`; terminal review `cta-ready-staging/decode13-benchmark-hu15-recovery/independent-file-timing-audit.json`; complete distribution table `cta-ready-staging/decode13-benchmark-hu15-recovery/RETENTION.md`.
- Dispatch combine: `dispatch-combine-current/decode13-benchmark-hu15/comparison.json`; terminal review `dispatch-combine-current/decode13-benchmark-hu15/independent-file-timing-audit.json`; complete distribution table `dispatch-combine-current/decode13-benchmark-hu15/RETENTION.md`.
- Coordinate recurrence: `reducer-coordinate-recurrence/decode13-benchmark-hu15/comparison.json`; terminal review `reducer-coordinate-recurrence/decode13-benchmark-hu15/independent-file-timing-audit.json`; complete distribution table `reducer-coordinate-recurrence/decode13-benchmark-hu15/RETENTION.md`.

Method: EP8/H7168/I2048/E256/K8, O3/AUTO4, deterministic unfused finalize, public forward, CUDA graph, 3 warmups / 100 cold-L2 CUPTI samples per row, per-iteration rankMAX. Decode 4–512 primary; 1/2 visible/excluded; 4K/8K/16K separate guards. No trimming. No sanitizer, pretests, or additional qualification after these performance results.

The hu59 ca05 attempt was interrupted after four rows and remains separate incomplete evidence. The later full hu15 ca05 trial replaces none of those original records.
