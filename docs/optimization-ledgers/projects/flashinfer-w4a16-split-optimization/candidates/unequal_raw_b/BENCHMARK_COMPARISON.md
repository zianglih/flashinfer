# Unequal raw/B depths: immediate before versus after

Before `logs/candidate002-cluster-m-repeat-ep8-fused.json` (`d3e5068ec7f3f3a07caea4206c4960e1e88e0c3302e95b9eddfdbdd6eb89680b`); after `logs/candidate004-raw-b-ep8-fused.json` (`9a95d04f569d3966424f8872e63d114d604d5a82fcd08a8a1047a82c5bd76d5e`). Full normal AUTO100CUPTI with all14 cache and source/protocol pins checked.

| Tokens | Before (µs) | After (µs) | Speedup | Latency change |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 36.3845 | 36.3845 | 1.0000× | +0.0000% |
| 2 | 42.3680 | 43.7445 | 0.9685× | +3.2489% |
| 4 | 59.6800 | 59.3290 | 1.0059× | -0.5881% |
| 8 | 74.6240 | 74.3365 | 1.0039× | -0.3853% |
| 16 | 81.5850 | 82.1610 | 0.9930× | +0.7060% |
| 32 | 116.3695 | 115.9530 | 1.0036× | -0.3579% |
| 64 | 149.6970 | 150.4490 | 0.9950× | +0.5023% |
| 128 | 153.6010 | 154.0810 | 0.9969× | +0.3125% |
| 256 | 160.8975 | 160.7695 | 1.0008× | -0.0796% |
| 512 | 165.5540 | 165.8095 | 0.9985× | +0.1543% |
| 1024 | 184.2890 | 184.5780 | 0.9984× | +0.1568% |
| 2048 | 228.9625 | 228.6420 | 1.0014× | -0.1400% |
| 4096 | 353.7470 | 352.9950 | 1.0021× | -0.2126% |
| 8192 | 666.5500 | 667.2860 | 0.9989× | +0.1104% |

8–8192: 0.999309×, +0.069194% latency; 5/11 lower. One complete current sweep against reused immediate control; no row selection, fixed-tactic or significance claim.
