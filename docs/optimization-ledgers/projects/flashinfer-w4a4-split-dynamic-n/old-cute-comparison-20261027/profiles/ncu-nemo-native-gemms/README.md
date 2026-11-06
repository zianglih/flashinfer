# Nemo native GEMM counter comparison

Source-frozen old/current NVFP4 T16384, EP8, both unfused, GPU0 B300. Same native winner caches and public benchmark as primary campaign. NCU2026.1.1 kernel replay profiles FC1 then FC2 with five passes each, cache reset and no clock control. Native PDL overlap is removed by selected-kernel replay; these are diagnostic counters, not end-to-end gains. Full commands, source hashes, cache hashes, report/CSV hashes and pre/post GPU telemetry are in each receipt.

| Arm / phase | Replay duration us | Tensor active % | DRAM peak % | Long scoreboard % | Barrier % | Registers | Shared bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| old FC1 | 234.848 | 54.23 | 30.68 | 61.84 | 1.80 | 105 | 233472 |
| old FC2 | 191.744 | 69.45 | 46.93 | 81.92 | 2.10 | 64 | 227328 |
| current FC1 | 271.200 | 43.86 | 47.76 | 22.38 | 36.75 | 102 | 231168 |
| current FC2 | 204.416 | 53.50 | 53.99 | 40.30 | 36.28 | 96 | 208256 |

Both current GEMMs show lower tensor-active fraction. Current aggregate barrier stalls include inactive producer warps at terminal CTA joins; no PC-level attribution was collected here. Historical FC1/FC2 compact six-warp trials were neutral/slower, so this counter alone does not reopen that change. Old winner uses route tile256; current uses route tile128, so neither resource nor traffic deltas isolate an implementation feature. Existing current route256 trial was slower and remains rejected.

NCU progress logs repeat the preceding kernel name, but exported raw report rows identify old FC1 and FC2 correctly; current shared-core names are equal and sequence plus distinct resources identify their phases. No profiler result is inserted into the primary CUPTI timing tables. GPU0 profiling completed and the device was released to the packed-scale experiment.
