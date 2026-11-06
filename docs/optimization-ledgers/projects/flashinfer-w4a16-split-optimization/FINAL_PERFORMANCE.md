# Current split W4A16 performance

Before 488ffbd9fe4455c3b4c3030cf668b5603c6698e4; after b90b34744491c36d0039f44cba664191f7bb0eb0. Two complete saved baseline controls and two complete current-source normal-AUTO sweeps on the same unchanged GPU/compiler stack. Each cell is a 100-iteration CUPTI median. Speedup is the ratio of the geometric means of the two before and two after medians; no row minima.

| Tokens | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | Speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 36.6720 | 37.4885 | 36.3840 | 36.3845 | 1.0191× |
| 2 | 42.7365 | 44.1600 | 42.3845 | 42.3680 | 1.0252× |
| 4 | 61.1360 | 59.2320 | 59.7120 | 59.6800 | 1.0080× |
| 8 | 74.8965 | 76.0010 | 74.4650 | 74.6240 | 1.0121× |
| 16 | 84.4805 | 84.4325 | 84.3360 | 81.5850 | 1.0182× |
| 32 | 116.4490 | 115.7290 | 115.2010 | 116.3695 | 1.0026× |
| 64 | 150.1130 | 150.1770 | 149.6980 | 149.6970 | 1.0030× |
| 128 | 154.2255 | 154.2095 | 153.6650 | 153.6010 | 1.0038× |
| 256 | 161.7455 | 161.5210 | 160.8975 | 160.8975 | 1.0046× |
| 512 | 166.4020 | 166.7220 | 165.7615 | 165.5540 | 1.0055× |
| 1024 | 186.6250 | 186.6580 | 184.1945 | 184.2890 | 1.0130× |
| 2048 | 232.5460 | 232.8340 | 229.3140 | 228.9625 | 1.0155× |
| 4096 | 362.3400 | 363.1075 | 353.6680 | 353.7470 | 1.0255× |
| 8192 | 711.8145 | 700.0385 | 675.6870 | 666.5500 | 1.0519× |

8–8192: 1.014053×, -1.385793% latency. All14 rows reported; 1/2/4 excluded from retention. Fused-finalize EP8 simulation; no inter-GPU communication. See adjacent JSON and source logs for complete pins/protocol.
