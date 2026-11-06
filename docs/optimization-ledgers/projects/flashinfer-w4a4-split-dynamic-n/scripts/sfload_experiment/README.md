# FC1 SF load experiment

Task-local GPU1 comparison against the frozen two-CTA overlap kernel, with all dependencies copied into `sfload_trial`. No production changes. Exact file hashes are in `manifest.json`.

For FC1 SF16 with K divisible by256, `vector_core.py` uses one128-bit global load per16 scale bytes, followed by four bank-conflict-free32-bit shared stores and an async-proxy fence. Nonaligned/short K and SF32 explicitly retain the original cp.async loop. `prefetch_core.py` moves the register load before the empty-stage wait, while keeping stores after A/B copy issue.

Both variants passed8 byte-for-byte paired FC1 cases, including N1/129/255/257, nonuniform scale factors, reverse routing and per-token scaling. These focused cases exercise the vector path; the rejected fallback was not exhaustively retested.

| NVFP4 FC1, balanced16384 routes, stage5 | N128 us | N256 us |
| --- | ---: | ---: |
| Frozen two-CTA overlap |281.472|286.400|
| Synchronous vector SF loads |496.641|338.305|
| SF vectors prefetched before stage acquire |354.113|325.471|

The vector variants are rejected for production. Reducing global-load instruction count loses cp.async latency hiding; early prefetch recovers some cost but remains slower. The following NCU profile targets the unchanged fast baseline to determine its current bottleneck.

Run from the remote candidate repository:

```bash
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. TRTLLM_ENABLE_PDL=1 OMP_NUM_THREADS=1 \
  ../.venv/bin/python ../scripts/sfload_experiment/run_variant.py \
  --variant baseline --script probe_perf.py --repo . --mode nvfp4 \
  --tokens 16384 --tiles 128,256 --factors 1 --stages 5 --phases fc1
```

The frozen two-CTA N128/stage5 baseline profile (`sfload-ncu-twocta-fc1-01`) measured288.832us,38.776% tensor activity,51.709% TMEM activity,33.929% TC shared-data throughput and60.614% LSU/L1 data throughput. It uses94registers/thread and144.384kB dynamic SMEM; local-load/store sectors are bothzero. These register/spill counters belong only to the frozen baseline and cannot rule out spills in rejected vector variants.

Source PC sampling finds3495 long-scoreboard samples at the producer AB-empty wait (offset0x78),6048 at epilogue accumulator-full wait/sleep (0xa0),606 at MMA local AB-full,53 at A-full and44 at peer relay-full. There are1504 SASS instructions. Much of the epilogue's wait reflects mainloop progress. This core still uses cp.async for B; the planned group2 Gather4 composition changes LSU pressure, so further SF-loader work is deferred until that composed core is measured.
