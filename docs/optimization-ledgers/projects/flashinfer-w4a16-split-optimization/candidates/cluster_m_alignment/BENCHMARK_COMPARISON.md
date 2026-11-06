# Full cluster bounds: immediate before versus after

Before: `logs/candidate-topk-repeat-ep8-fused.json` (`0fa87eb84e88ee1d58a80e0c88e72ff99769a2c9783096048e3048d05d64cf2e`). After: `logs/candidate002-cluster-m-ep8-fused.json` (`560c1cb4e8506a4379a37f658e83945b27267c58fb14c0794c9de7357522405d`).

Same node, source-pinned protocol, full normal AUTO 1–8192, 10 warmups and 100 cold-L2 CUDA-graph CUPTI iterations; row medians. Single-GPU simulated EP8, H7168/I2048/E256/top-k8, routing included. All saved row-cache hashes verified.

| Tokens | Before (µs) | After (µs) | Speedup | Latency change |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 36.4005 | 36.3840 | 1.0005× | -0.0453% |
| 2 | 43.0880 | 42.3845 | 1.0166× | -1.6327% |
| 4 | 59.2165 | 59.7120 | 0.9917× | +0.8368% |
| 8 | 75.2485 | 74.4650 | 1.0105× | -1.0412% |
| 16 | 81.6640 | 84.3360 | 0.9683× | +3.2719% |
| 32 | 115.7445 | 115.2010 | 1.0047× | -0.4696% |
| 64 | 150.1455 | 149.6980 | 1.0030× | -0.2980% |
| 128 | 153.8890 | 153.6650 | 1.0015× | -0.1456% |
| 256 | 160.8970 | 160.8975 | 1.0000× | +0.0003% |
| 512 | 165.4405 | 165.7615 | 0.9981× | +0.1940% |
| 1024 | 183.7130 | 184.1945 | 0.9974× | +0.2621% |
| 2048 | 228.8335 | 229.3140 | 0.9979× | +0.2100% |
| 4096 | 352.6265 | 353.6680 | 0.9971× | +0.2954% |
| 8192 | 666.5000 | 675.6870 | 0.9864× | +1.3784% |

8–8192: 0.996744× speedup, +0.326679% latency; 4/11 lower. Tokens1/2/4 excluded from retention. One current-source sweep versus the reused complete immediate baseline; no statistical-significance or matched-tactic claim.
