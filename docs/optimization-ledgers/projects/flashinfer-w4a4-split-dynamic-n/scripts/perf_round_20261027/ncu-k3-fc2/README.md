# Current K3 T64 FC2 counters

Current source `f7182d5c`, same public saved native tactics and graph as the preceding NSYS diagnostic. Two selected FC2 reports each use six NCU replay passes with reset caches and base clocks. Replay serializes kernels, so duration is diagnostic and must not replace native CUPTI full-chain medians.

| Counter | CuTe | TRTLLM |
|---|---:|---:|
| DRAM read, MB | 480.828 | 477.299 |
| TMA global read, MB | 582.844 | 506.677 |
| L2 traffic, MB | 783.932 | 738.849 |
| Executed instructions, million | 7.532 | 9.207 |
| DRAM throughput, % peak | 77.600 | 78.310 |
| Tensor utilization, % peak | 3.380 | 3.410 |

Both kernels remain memory bound in this replay. CuTe executes about 18% fewer instructions, with nearly the same DRAM reads, but 15% more TMA global reads and 6% more L2 traffic. The current CuTe N32 versus TRT N8 tile difference is a plausible activation-overfetch contributor; these counters do not alone isolate it. Avoid concluding that additional producer warps or generic instruction reductions necessarily close this particular gap.

The exported report names, grid, block size and register counts match NSYS FC2; CuTe FC1 would have 82 rather than 76 registers. The NCU progress log prints a misleading TRT SiTU/FC1 name, but the authoritative report is the BFloat16 FC2 kernel, with grid 6328 and 128 registers. No rerun was needed.

Source/cache invariance, helper hashes and exact commands are in `evidence/receipt.json` and observers. `analyze_ncu.py` checks the two report hashes, finite 27-metric sets and expected native kernel identities, then produces `evidence/ncu-summary.json`. No production source or autotune cache was changed.
