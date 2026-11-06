# SF source-pointer shuffle: rejected

The candidate was rejected at the unchanged no-local-memory native gate and its local review/branch retired. Retained `c1ac8ce7` is unchanged; no timing. Kernel SHA `371510e6a745e8c7845d0918a7d5984386b07ff7eea3eb4749f3f5f8fe6ad6e4`, patch `5b94bb24` (+55/−14).

The original payload register coordinates, one Int64 SF offset per lane/row block, and pre-loop route loads/division remain intact. R1's coalesced destinations/masks/arrival count are retained. The existing copy primitive takes two constexpr private parameters, exchanges both halves of the original full source pointer, and adds the lane's word offset with full 64-bit carry. All lanes execute the shuffles; only the async copy is predicated. G1 emits the original asm string.

No shared coordinate cache, planner/storage change, new barrier, helper, API, tactic, register quota, task-order change, volatile operation or compiler option is introduced. This replaces the rejected composition's LDS→R2UR coordinate chain and duplicated SF setup with two SHFLs per SF copy. It does not establish a performance improvement or guarantee ptxas keeps compact offsets.

[Patch](candidate.patch), [source/static receipt](source-proof.json), [scoped hooks](precommit.log), [mapping/history audit](../../audits/sf-pointer-shuffle-feasibility.md). The source inverse preserves the rest of the module; original SF offset setup is byte-identical. Actual lowering, LOCAL0/resources, full-warp execution and exact outputs remain native gates.

The authorized first gate is only the existing `pilot-mx8-wide-g2`, `pt-g4-w8-n256` and `mx4-g1-control` pairs from the corrected current-cohort `sf-coordinate-cache/qualification-extra-r1` harness. Reuse its parallel source verification and normal private-arm loader checks, current046 cache/readiness receipts, canonical generated symlinks and explicit `FLASHINFER_CUBIN_DIR`; do not copy the stale pre-recovery controller or mutate preserved caches/receipts. Controls are reused from the preserved current046 cohort after source/helper/runtime/native checks; only the three candidate calls run.

[Final results](RESULTS.md), [independent native peer](../../audits/sf-pointer-shuffle-native-peer.json), [retirement receipt](retirement/receipt.json). Both wide FC1s failed the resource guard before invocation (driver local48/16; native stack48/16). Narrow G1 passed with all three raw native images identical. No retry, quota change or narrower policy.
