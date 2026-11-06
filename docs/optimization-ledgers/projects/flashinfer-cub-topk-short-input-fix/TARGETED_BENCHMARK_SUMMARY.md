**Longer-batch follow-up for small-case variation**

One page-plus-raw case temporarily crossed the screen after two broad pairs; the complete three-pair sweep has no hits. We retained that full sweep and separately reran all four API forms and both tie modes at batch 1, FP32 random inputs, `(d,k) = (2048,2048), (4096,2048), (16384,256)`. These are 24 existing workload IDs, not 24 additional unique workloads.

Three more alternating pairs used **500 calls per graph and 100 samples**, with seeds `20260923 + round`. All 24 CUB cases and 24 native controls stayed below the screen. The largest CUB increase was **+0.038%**; CUB's geometric-mean change was **−0.075%**. The earlier slowdown did not reproduce with these longer timing batches. Original results remain included above and in the raw files.

| CUB case | Before → after µs | Paired change |
|---|---|---:|
| `page-fp32-random-normal-b1-d16384-k256-Lfull-w0-p64-small` | 10.279296 → 10.265024 | -0.055% |
| `page_raw-fp32-random-normal-b1-d16384-k256-Lfull-w0-p64-large` | 10.549440 → 10.535296 | -0.074% |
| `page_raw-fp32-random-normal-b1-d2048-k2048-Lfull-w0-p64-large` | 3.609664 → 3.609536 | -0.039% |
| `page_raw-fp32-random-normal-b1-d2048-k2048-Lfull-w0-p64-small` | 3.654400 → 3.654368 | -0.051% |
