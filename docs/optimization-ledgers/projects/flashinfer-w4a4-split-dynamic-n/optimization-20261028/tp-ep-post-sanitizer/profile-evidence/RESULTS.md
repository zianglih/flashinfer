# EP/TP prefill pipeline diagnosis

Pinned source `d1767be1f42fdc371f90db4fb06598299ea32845`; T16384, saved current-source autotune winners, PDL on, unfused finalize. The public benchmark profile mode uses cold-L2 graph replays. These are diagnostic profiles, not retention timings or replacements for the CUPTI tables.

All 66 raw artifacts, including Nsight reports, SQLite, commands, source/cache checks and selections, were fetched and SHA256-verified. Native caches remain on persistent storage. EP profiling ran on primary GPU6; the first two EP receipt rows preserve stale GPU1 metadata, but the executed runner overrides to GPU6. The top-level GPU UUID and actual command establish the device. The initial failed EP startup is retained separately; it completed no profiling.

## Nsight Systems

Twenty captured graph replays per cell. Critical extension sums nonoverlapping contributions rather than adding overlapping kernel durations. Reported stage medians need not sum exactly to the graph median.

| Shape/dtype | Graph µs | Prepare | FC1 | FC2 | Combine |
|---|---:|---:|---:|---:|---:|
| prefill v3-cute-dsl-w4a8 | 658.5 | 39.8 / 39.6 | 322.6 / 313.0 | 222.9 / 187.3 | 83.2 / 79.8 |
| prefill v3-cute-dsl-mxfp8 | 697.9 | 40.2 / 40.0 | 355.7 / 347.0 | 226.4 / 189.9 | 86.9 / 82.6 |
| prefill nemo3-ultra-cute-dsl | 520.3 | 21.0 / 20.8 | 235.7 / 233.2 | 202.5 / 184.0 | 56.7 / 53.5 |
| tp-k3 kimi-k3-cute-dsl-w4a8 | 2062.1 | 304.4 / 303.5 | 651.6 / 581.8 | 824.7 / 808.6 | 365.6 / 358.7 |
| tp-v3 v3-cute-dsl-w4a8 | 1736.9 | 315.5 / 315.2 | 448.2 / 352.2 | 713.5 / 684.3 | 347.6 / 347.0 |
| tp-v3 v3-cute-dsl-mxfp8 | 1790.2 | 318.6 / 318.4 | 496.2 / 399.2 | 716.3 / 689.4 | 344.3 / 343.8 |

Each stage cell is duration / critical extension in microseconds.

## Nsight Compute

Application replay, clock/cache control disabled. Replay can perturb PDL scheduling: use counters for direction, not an end-to-end speedup claim.

| Profile / stage | Duration µs | DRAM read MB | DRAM write MB | Tensor elapsed % | Long scoreboard % | Barrier % | Wait % |
|---|---:|---:|---:|---:|---:|---:|---:|
| prefill-profile FC1 | 308.42 | 651.50 | 80.56 | 78.50 | 59.92 | 19.43 | 6.09 |
| prefill-profile FC2 | 187.10 | 286.43 | 211.08 | 60.97 | 46.10 | 25.06 | 14.65 |
| tp-k3-profile Prepare | 304.54 | 528.88 | 998.41 | 0.00 | 87.74 | 0.00 | 5.38 |
| tp-k3-profile FC1 | 588.93 | 2397.46 | 152.59 | 75.57 | 33.61 | 19.94 | 21.73 |
| tp-k3-profile FC2 | 813.66 | 773.75 | 1829.93 | 19.78 | 42.24 | 20.76 | 20.07 |
| tp-k3-profile Combine | 318.05 | 1878.92 | 161.92 | 0.00 | 93.17 | 0.00 | 2.28 |

## Decisions

- TP increases local routing payload and shortens FC2 reduction. K3 FC2 has about 20% tensor utilization, whereas FC1 is already about 76%. V3 is also slow with an aligned K256, so tail peeling alone cannot resolve the TP gap.
- Test compile-time K-tail peeling as an instruction reduction with unchanged operand ownership; qualify K96 numerical grouping and descriptors independently.
- Test routed FC2 scratch plus 2D TMA slab stores. Earlier routed scratch and scatter4 trials retained row-wise stores; the new mechanism must remove that issue work and justify descriptor/allocation costs on decode as well as prefill.
- Prepare and combine move large volumes of data with high long-scoreboard stalls. Aggregate counters do not establish SF-scatter attribution. Collect per-PC prepare evidence before changing ownership; do not repeat broad vectorization experiments without a new mechanism.
- Existing operand producers share one completion phase and independently wait for reuse. TMEM accumulator lifetime, output-store scratch lifetime, CLC response lifetime, and metadata-ring lifetime differ; combining their barriers would add coupling or break ownership. No synchronization removal follows from a high aggregate barrier-stall percentage alone.
