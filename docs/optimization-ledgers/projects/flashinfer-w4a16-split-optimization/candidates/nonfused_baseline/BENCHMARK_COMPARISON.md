# Non-fused finalize performance

Upstream `488ffbd9fe4455c3b4c3030cf668b5603c6698e4` versus retained `b90b34744491c36d0039f44cba664191f7bb0eb0`; same node and stack, independently autotuned complete 1–8192 sweeps. Ten warmups and 100 cold-L2 CUDA-graph CUPTI iterations per row. H7168/I2048/E256/top-k8, EP8/TP1 simulation on one B300; routing included, no inter-GPU transport.

| Tokens | Upstream (µs) | Retained (µs) | Speedup |
| ---: | ---: | ---: | ---: |
| 1 | 38.0165 | 38.0645 | 0.9987× |
| 2 | 44.1925 | 44.1125 | 1.0018× |
| 4 | 58.4010 | 58.5290 | 0.9978× |
| 8 | 70.9120 | 70.6245 | 1.0041× |
| 16 | 81.5210 | 81.7610 | 0.9971× |
| 32 | 113.2335 | 113.2015 | 1.0003× |
| 64 | 150.2895 | 148.9135 | 1.0092× |
| 128 | 152.2260 | 151.8090 | 1.0027× |
| 256 | 159.8730 | 160.0970 | 0.9986× |
| 512 | 165.0575 | 164.4170 | 1.0039× |
| 1024 | 182.4180 | 182.6100 | 0.9989× |
| 2048 | 223.9215 | 224.5620 | 0.9971× |
| 4096 | 328.1150 | 329.0115 | 0.9973× |
| 8192 | 643.3660 | 630.3580 | 1.0206× |

Tokens 8–8192: 1.002697× geometric-mean speedup, -0.268941% latency; 6/11 lower. Tokens 1/2/4 reported but excluded from retention. One complete run per arm; no statistical-significance claim. All row-cache hashes, routing histograms, protocol fields and measured source bytes verified.

Precision: BF16 expert scratch, fixed ascending top-k accumulation in FP32, one final BF16 cast. No combine atomics or TMA reduction.

Before result `logs/baseline-ep8-nonfused.json` SHA `8840cdf9772295391e834664621f254f67153e7f591edb4c0a99828a7b48ef54`; after `logs/retained-bounds-ep8-nonfused.json` SHA `50fdb26f6960de45489b7b8c76b02808bb0481e1fa9e11160c53e12b87a72f92`.
