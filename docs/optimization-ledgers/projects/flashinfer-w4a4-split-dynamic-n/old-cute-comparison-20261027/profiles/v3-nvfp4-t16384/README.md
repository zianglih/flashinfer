# V3 T16384 standard NVFP4 pipeline trace

Old002529 versus retained0b7, EP8, both unfused, functional public API, input quantization included. Same frozen native winners as the primary CAAC campaign; no AUTO. Each trace contains20 CUDA-graph replays with the public L2 flush. Nsight timing is diagnostic and is not substituted for the primary100-sample CUPTI timing.

| Phase | Old start–end (us) | Current start–end (us) | Old duration (us) | Current duration (us) |
|---|---:|---:|---:|---:|
| input_quant | 0.00–50.56 | 0.00–51.07 | 50.56 | 51.07 |
| topk | 46.29–80.34 | 46.70–80.91 | 34.00 | 34.22 |
| routing_init | 77.83–81.09 | 78.30–81.66 | 3.30 | 3.30 |
| routing_indices | 80.93–89.23 | 81.54–89.86 | 8.21 | 8.32 |
| prepare | N/A | 89.66–115.60 | N/A | 25.84 |
| fc1 | 89.04–287.35 | 110.43–306.99 | 198.35 | 196.45 |
| fc2 | 284.83–403.54 | 289.15–435.19 | 118.66 | 146.11 |
| combine | 288.56–489.84 | 431.95–522.07 | 201.30 | 90.54 |

Graph span:489.84us old,522.07us current. Primary CAAC medians are490.71us and525.37us.

The added prepare precedes FC1 and shifts its start by about21us; FC1 durations are similar. FC2 completion moves later by31.65us, and final output by32.22us. This points to prepare plus the FC2 critical tail. It does not establish isolated compute throughput or prove a particular optimization.

PDL matters when reading durations: old combine begins while FC2 runs, so its201.30us includes a large wait. The current90.54us combine starts close to FC2 completion. The final tail after FC2 ends is approximately86.30us old versus86.88us current; a claim of2× combine improvement from duration alone would be misleading.

Both native winners use256×256 tiles and2-CTA clusters. Current usesKsteps4/4 andsharedCLCoff. Full per-iteration timestamps, registers, shared memory and launch dimensions are in `kernel-timeline.json`; raw reports/SQLite and frozen source/cache receipts are alongside it.
