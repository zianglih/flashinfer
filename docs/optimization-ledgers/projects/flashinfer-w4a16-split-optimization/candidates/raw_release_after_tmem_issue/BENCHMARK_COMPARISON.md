# Raw release after TMEM issue: immediate before versus after

Before `logs/candidate002-cluster-m-repeat-ep8-fused.json` (`d3e5068ec7f3f3a07caea4206c4960e1e88e0c3302e95b9eddfdbdd6eb89680b`); after `logs/candidate003-raw-release-ep8-fused.json` (`f715bc8c601eb4d92339ed18a1b94370fb5fafe2796629be317d9e9574bcd811`). Full normal AUTO, 100 CUPTI iterations and unchanged protocol/source pins. All14 row-cache hashes checked.

| Tokens | Before (µs) | After (µs) | Speedup | Latency change |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 36.3845 | 36.6565 | 0.9926× | +0.7476% |
| 2 | 42.3680 | 42.5605 | 0.9955× | +0.4544% |
| 4 | 59.6800 | 58.8325 | 1.0144× | -1.4201% |
| 8 | 74.6240 | 74.0810 | 1.0073× | -0.7276% |
| 16 | 81.5850 | 83.9210 | 0.9722× | +2.8633% |
| 32 | 116.3695 | 115.7130 | 1.0057× | -0.5642% |
| 64 | 149.6970 | 150.9130 | 0.9919× | +0.8123% |
| 128 | 153.6010 | 153.8260 | 0.9985× | +0.1465% |
| 256 | 160.8975 | 160.7060 | 1.0012× | -0.1190% |
| 512 | 165.5540 | 165.1860 | 1.0022× | -0.2223% |
| 1024 | 184.2890 | 183.8900 | 1.0022× | -0.2165% |
| 2048 | 228.9625 | 228.8340 | 1.0006× | -0.0561% |
| 4096 | 353.7470 | 353.1390 | 1.0017× | -0.1719% |
| 8192 | 666.5500 | 667.1105 | 0.9992× | +0.0841% |

8–8192: 0.998383×, +0.161942% latency, 7/11 lower. One complete current sweep against reused immediate control; no row minima, fixed-tactic or significance claim. Tokens1/2/4 excluded from aggregate.
