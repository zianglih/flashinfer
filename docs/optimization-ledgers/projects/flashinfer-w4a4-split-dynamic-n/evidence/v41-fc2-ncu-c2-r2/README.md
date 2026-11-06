# V41 NVFP4 T128 FC2 targeted NCU diagnostic

B300 GPU0, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2/CuTe4.7.1, clean `0c1e00fc3e4f913c8c241796c70a29673737c542`. The retained853 change only broadens the mixed FC1 overlap policy; this NVFP4 path is unchanged. Same saved native AUTO tactics and exact V41 input-route hashes as the completed paired pipeline trace. No current benchmark or production code changed.

NCU2026.1.1, one selected FC2 launch/backend, five kernel-replay passes each, cache-control all and base-clock control. CuTe kernel name also names FC1, so skip exactly one matching launch; the captured288-thread/grid148 resource record independently confirms FC2. TRT uses its BF16-output FC2 name and captures512 threads/grid40×180. Full source/cache/route checks passed before/after.

| Metric | CuTe | TRT |
|---|---:|---:|
| Kernel replay time (us) | 92.4160 | 90.6240 |
| DRAM reads (MB) | 545.8171 | 544.5768 |
| DRAM writes (MB) | 3.4954 | 5.3532 |
| DRAM throughput (% peak) | 77.5200 | 79.1600 |
| L2 traffic (MB) | 939.4486 | 880.5782 |
| L2 sector hit rate (%) | 11.4200 | 6.5600 |
| Tensor active (% peak elapsed) | 7.3200 | 3.7400 |
| Executed warp instructions (M) | 9.3894 | 12.2591 |
| Issue active (%) | 18.6500 | 24.2200 |
| Eligible warps / scheduler cycle | 0.2300 | 0.3100 |
| Long scoreboard (% active warp cycles) | 71.8100 | 72.4300 |
| Registers / thread | 90.0000 | 128.0000 |
| Threads / CTA | 288.0000 | 512.0000 |
| Allocated shared memory incl driver (B) | 198528.0000 | 204688.0000 |

The counters are consistent with a memory-bound FC2: roughly545 MB read in either kernel, 77–79% DRAM throughput and ~72% long-scoreboard samples, while tensor activity is only3.7–7.3%. CuTe executes fewer warp instructions; this does not support instruction count or tensor saturation as the dominant remaining limit. TRT uses actual descriptorN8 (`0x8020480`), while CuTe rounds live N to16. That explains their tensor-activity difference without establishing a speedup from an N8-only change.

The isolated replay gap is1.792us (~2%). Earlier five-replay native pipeline traces report FC2 lifetimes95.521us versus83.104us, but those include PDL startup/wait and overlap. Total chain medians were273.0095us versus266.897us, not the sum of phase lifetimes. Replay flushes caches and serializes/changes dependency context, and uses base clocks; the difference cannot uniquely prove a cache or PDL cause. It identifies chain-level startup/dependency handling as a useful next diagnostic.

No optimization is retained on these profiler counters. Native10/100 cold-L2 CUDA-graph CUPTI paired measurements remain the retention method. Raw reports, CSV, observer receipts and exact commands are in `raw/`; `summary.json` is parsed only from the selected metric columns. The earlier r1 attempt failed at CLI parsing (`--output` unsupported) before profiling; r2 uses `-o` and both captures completed.
