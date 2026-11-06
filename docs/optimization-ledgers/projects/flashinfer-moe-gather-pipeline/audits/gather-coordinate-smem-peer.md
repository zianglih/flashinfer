# Warp-private Gather4 coordinate scratch: independent read-only assessment

Retained source: `c1ac8ce7`, swap kernel SHA `482b636a1714486e2ffb34c8ae005da3cef26f25f0ce034ba1eb59c6198d6276`. No source edit, compilation, GPU work, or new harness. This assesses replacing the existing persistent payload coordinate array with a small warp-private shared array; the failed coalesced-SF variants remain rejected.

**Finding:** the ownership mapping is feasible and the recorded tactics have sufficient shared-memory capacity. A single post-store/pre-K warp sync is not a complete scratch-reuse proof. The added per-K shared loads and their dependencies are material, so register relief alone would not justify retention.

## Ownership and ordering

At kernel lines 3437–3476, `groups_per_warp = ceil(b_copy_rows/16)` and `groups_per_load = min(8, next_power_of_two(groups_per_warp))`. The existing route loads include duplicated lanes for small N. A cache shaped `Int32[4, 4*groups_per_warp]`, aligned to 16 bytes, can keep each warp's packets independent. In each current batch, only lanes below `4*min(groups_per_load, remaining_groups)` should store to `batch*4*groups_per_load + lane`. All these unique writers must store the existing OOB sentinel too; skipping invalid-row stores would leave stale coordinates from the preceding work tile.

The existing packet index `first = (task_group % ceil(row_groups/4))*4` selects the same four coordinates. A bounded arithmetic replay checked **131,688 packet comparisons** over N16/32/64/128/256, one/two CTA, every valid-row count, both CTA ranks, and K4/K8. It verifies unique writers and the unchanged dynamic split `cta_rank * (round_up(valid,16)/cta_group_size)`. Small-N duplication between warps is intentional: different warps can issue different K chunks for the same rows. It does not permit overlapping writers to one warp's slots.

The coordinates are refreshed once for every static or CLC work tile. `next_work` at line 2514 provides no static synchronization; its CLC metadata wait/release is not a proven full-warp shared read/write join. A full-mask warp barrier after stores publishes coordinates before the reads, but a **read-complete/reuse join before the next overwrite is also needed**, unless an existing post-read synchronization is established. Otherwise a non-elected lane can start next-tile stores before the previous tile's elected shared reader completes. The current election occurs before that read and is not the missing join. [PTX documents memory ordering for `bar.warp.sync`](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-bar-warp-sync).

No cluster barrier or TMA-completion wait is required just for this scratch: no other warp/CTA reads it, and Gather4 consumes coordinates already loaded into registers. All existing operand waits, SF arrivals, relay, TMA byte accounting, PDL startup and metadata lifetime still remain. Both publication and reuse synchronization must include all participating lanes, including small-N warps with no payload issue in a particular iteration.

## Shared-memory capacity

Cache size is `64*ceil(b_copy_rows/16)` bytes per CTA: **64–1024 bytes**, with group2 using its half-tile payload ownership. Insertion before the existing 128-byte-aligned epilogue scratch can absorb part of this cost. The planner must account for it in `_pipeline_metadata_bytes`, `_operand_stage_capacity` and their callers; appending an unbudgeted field is unsafe for automatic or explicit stage depths.

I reused the extracted production planner in `gated-fc1-warp-ownership/slab_scratch_audit.py` and its 364 frozen FC1 records. Its planner AST remains equal to current source. Adding this cache before the metadata rounding gives:

| Raw cache bytes | Recorded cells |
|---:|---:|
| 64 | 241 |
| 128 | 40 |
| 256 | 43 |
| 512 | 36 |
| 1024 | 4 |

Rounded metadata growth is 0 bytes for 124 cells, 128 for 157, 256 for 43, 512 for 36, and 1024 for four. **No recorded FC1 choice loses an operand stage.** Minimum original planner slack is 1024 bytes. These are predictions from the existing layout/planner formulas, not newly compiled `SharedStorage` sizes or a guarantee for arbitrary explicit-depth/metadata configurations. Record input SHA: `bbe49d92330c043c812142cdde3250f5b4a3f06b316064349469d2d42346cdec`.

## Cost and exact history

The current static issue order needs one four-coordinate packet per Gather4. At N256/group1/K8 this is **32 packet loads per warp per K stage**, or 2 KiB of logical shared reads per CTA/stage; the coalesced G2 SF path has four SF-copy sites per warp/stage. Actual `LDS.128` lowering is not guaranteed, and TMA still needs uniform coordinate operands. Current native code already contains R2UR and uniform/general-register transfers; 64 source-array values are not evidence of 64 removable physical registers. The compiler could also hoist shared reads, so native placement and remaining spills must be inspected.

A row-outer packet-reuse variant would halve wide K8 packet loads but changes issue order. The exact prior [live-groups-row-outer experiment](../../flashinfer-w4a4-split-dynamic-n/fc1-gather-20261028/optimization-next-20261029/live-groups-row-outer/RESULTS.md) reused four coordinates over K chunks: 23 exact cases and 44 LOCAL0 kernels passed; representative code removed 23 instructions, but N3U EP prefill lost 1.343% with 0.131/0.113% repeat spreads. It retained dynamic live-group traversal, so it does not isolate this proposed static shared cache. It does establish that row/K interchange alone is not a new untested mechanism.

The bounded current/prior CLOSED_LEADS and gather/lane-metadata/SF-ownership records contain no matching warp-private shared coordinate-cache trial. The prior [shared SF/payload-coordinate experiment](../../flashinfer-w4a4-split-dynamic-n/fc1-gather-20261028/optimization-next-20261029/sf-payload-linear-guard-typed/RESULTS.md) changed ownership rather than staging coordinates in shared memory and lost 0.651% overall. The failed inline-address attempt's LOCAL48 is a new diagnostic motivation for reducing live coordinate state, not proof that added shared traffic will help. Standalone neutral complexity would not justify retention, and composition with SF coalescing must earn a source-bound performance gain without quota or shape exceptions.
