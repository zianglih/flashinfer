# W4A16 static Gather4 traversal

Isolated unstaged candidate in `flashinfer-w4a16-linear-issue-review`, retained22ffe662 base. Four FC1 activation warp issuers, fifth warpgroup, metadata cache, shared-memory layout, pipeline arrivals/bytes, multicast ownership, register budgets, PDL, FC2 and tactics are unchanged.

The current row-first traversal emits all K64 chunks for one four-row group before advancing rows. The swap implementation uses row groups first within each K chunk. This candidate adopts that ordering with one compile-time task group. Both quotient and remainder are evaluated on `range_constexpr` task-group values, including N192's six groups per issuer; no runtime division by24 is introduced. Runtime warp-to-row/K ownership is unchanged.

Evidence motivating the bounded probe: paired K3EP4K/8K iKET traces show higher activation wait after Gather4 while dequantization load/decode/store and scheduler waits remain similar. Prior source already caches route IDs outside K. The existing SASS emits16/24 Gather4 operations per issuer and per stage for N128/N192, with a uniform bound branch and repeated barrier/cache descriptor setup before each. Traversal may change instruction scheduling or descriptor reuse; fewer instructions or faster execution is not assumed.

This is distinct from rejected live-row loops (runtime group bounds and per-K shuffles), elected scope hoisting (+4 instructions), static-bound removal (+64 instructions), and register redistribution. No old rejected direction or new tuning axis is combined.

`geometry-proof.json` enumerates144 combinations of per-CTA row count8..128, K64 chunk count1..8 and multicast1/2/4. Every CTA rank and issuing warp has the exact same multiset of destination row/K coordinates and cached route-ID slots; original validity guards remain. Four independent arrivals still account for exactly the same bytes. Source proof and full manifests are recorded before compilation.

Gate: actual native K3EP4K M256N128K256, K3EP8K N192, and V3TP8 N16. Capture both retained22ffe and candidate PTX/CUBIN/SASS, reject introduced spills or unnecessary work before timing. Optional markers remain disabled. No sanitizer; no new native autotuning.
