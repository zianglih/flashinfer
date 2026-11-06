# Two-block throughput width diagnostic

Raw two-block policy rejected because it can increase rounded SF work. K1280/1536 regress7.95/1.98% despite zero LOCAL. Source candidate in ../per-token-paired-width instead narrows only if padded SF loads do not increase, preserving old widths for these cases. No shape exception.

| M | K | Threads before/after | Gain | Control/candidate spread |
|---:|---:|---:|---:|---:|
| 360448 | 640 | 64/32 | +7.103% | 0.004/0.078% |
| 98304 | 576 | 64/32 | +7.711% | 0.058/0.031% |
| 262144 | 384 | 32/32 | -0.009% | 0.057/0.075% |
| 131072 | 256 | 32/32 | -0.085% | 0.170/0.112% |
| 16384 | 512 | 32/32 | +0.058% | 0.116/0.000% |
| 16384 | 768 | 64/32 | +8.111% | 0.000/0.084% |
| 16384 | 1024 | 64/32 | +15.729% | 0.146/0.087% |
| 16384 | 1280 | 96/64 | -7.950% | 0.101/0.184% |
| 16384 | 1536 | 96/64 | -1.984% | 0.092/0.136% |
| 16384 | 2048 | 128/64 | +14.216% | 0.077/0.000% |
| 16384 | 2304 | 128/96 | +0.592% | 0.097/0.128% |
| 16384 | 3072 | 128/96 | +1.123% | 0.058/0.087% |
| 16384 | 3584 | 128/128 | +0.039% | 0.105/0.131% |
| 16384 | 5120 | 128/128 | -0.061% | 0.080/0.040% |
| 16384 | 7168 | 128/128 | -0.000% | 0.122/0.031% |
| 16384 | 8192 | 128/128 | -0.084% | 0.027/0.112% |
| 128 | 640 | 64/64 | +0.000% | 0.000/0.000% |

17cells/6800strictCUPTIsamples,C-A-A-C,100cold-L2CUDAgraphsamples/phase,10warmups,B300GPU6. Same source374/sameinputs/MSE256error-fast-mathrecipe, existing thread override, exactpayload/scales/rowscales.25compiledconfigs zeroLOCAL/stack. Artifactarchive3a5cff18a2e9554dd73d85f2c9b3c91613e22cefafae14ee2dd98d93c2a2f8e2;108hashverifiedfiles. Per-phase2msNVMLtelemetryretained, no clockschanged. This is microbenchmark evidence, not E2Eretention.
