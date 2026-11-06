# K-major issue order across independent channel tiles

Read-only proposal on b52. No source change or GPU work.

The current stage issues every K atom for channel tile0, then every K atom for channel tile1. Both independent accumulators consume the same B/SFB descriptors; the generated wide-MX PTX keeps eight B descriptors alive for their second use. Actual b52 SASS still has128B control/MMA stack in two M512/N128/K8 diagnostic variants. Current native benchmark winners are spill-free, so this is not an explanation for every observed latency gap.

A single helper can accept the compile-time tuples of accumulator, A and SFA fragments, iterate K atoms outside channel tiles, and issue `(K0,C0),(K0,C1),(K1,C0),(K1,C1),...`. This preserves the K instruction sequence independently for each output accumulator and uses the same data, SF banks, widths, accumulation predicate, barriers and release/commit sites. For one channel tile it is the same order. For two tiles, each B descriptor's logical reuse distance falls from a whole K-stage instruction count to one MMA. This may reduce generated uniform/GPR live state without changing register quotas or adding an autotune axis. PTXAS may still hoist descriptors, so inspect actual code rather than claiming the benefit from source.

The symbolic proof covers one/two channel tiles, K32/K64 ordinary stages and mixed96/64 tails; every per-accumulator issue order is identical. A/B/SF descriptor/address generation must remain unchanged, especially the K96 bank mapping and partial-K widths. Preserve one stage-release only after every channel/K instruction and the existing accumulator publication.

History search found no matching K-major/channel-interleaved MMA trial in the current Gather4, prior nb2/nb3, regular-TMA and descriptor-spill notes. This differs from the rejected static-SF-selector simplification, which changed descriptor arithmetic and introduced common-state spills. Recheck exact older code before implementation.

Next gate if pursued: minimal private-helper/caller refactor, paired compile-only all supported formats/one-two channel tiles/K96 plus ordinary/tail, no resource increase, inspect actual descriptor/local-memory lifetimes and single-channel code equivalence. Only then exact/performance with frozen native winners. No public knob, tactic axis, model/dtype gating or synchronization change.
