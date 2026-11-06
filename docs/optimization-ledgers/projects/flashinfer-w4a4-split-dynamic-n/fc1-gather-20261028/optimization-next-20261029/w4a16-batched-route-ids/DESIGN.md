# Batched W4 route-ID preload

Base retained6c6515f2; independent unstaged review. Only route metadata loading before K changes. Four Gather4 issuers, existing warp-uniform coordinate cache, SHFL count, static TMA traversal, bytes/arrivals, stages, PDL, quotas, CLC/static scheduling, FC2 and public interfaces stay unchanged.

Current metadata instruction loads four distinct IDs duplicated across eight lane quartets. N128/N192 two-CTA kernels repeat4/6 LDG sites and4/6 divisions before K. Batch up to eight four-row groups across32 lanes, then broadcast desired lanes into exactly the old statically indexed coordinate slots. All SHFLs remain outside K; no dynamic hot-loop iteration, indexing, metadata reload or pruning.

One compile-time rule: groups_per_load=min(8,next_power_of_two(groups_per_warp)). The lane mask folds the narrow single-group geometry to the old mapping. Short batches retain original row/valid bounds; only existing cache slots are filled. Each TMA coordinate remains warp-uniform, including−1 OOB sentinels; dynamic group-2 half-N offset remains unchanged.

CPU proof345,600 cases: all N8..256 at8*CTA-group alignment, groups1/2,4issuers, valid0..N, static/dynamic second-CTA shift, topK1/2/3/8/22. Source addresses, quotients, sentinels and cache order match. Current W4 tactics useN8/16/32/64/128/192; largest1CTA isN128, N192 requires2CTA due existing shared-memory capacity. No tactic change.

One per-lane Int32 ID remains live through its static broadcast batch; the cross-K uniform cache size is unchanged. Metadata indexing ends before K. No shared buffer, barrier or quota changes. Require actual LDG/divide-site reduction and zero-local codegen before timing.

This does not repeat rejected live-group loops: those retained lane IDs and repeatedly shuffled inside K. It also does not change SF/payload ownership or bank mapping. Rubin uses wider index loads outside K at block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:1197–1235; its padded index-allocation contract is not imported.

Other read-only findings: dynamic BF16 idesc is already hoisted before K in retained N128 SASS (1f30–1f50, backedge24c0→1f70). Decoded fragments already stream through STTM.x8 interleaved with later decode. No descriptor-hoist or chunk-store rewrite is justified.

GPU3 only: representative N16/N128/N192 zero-local codegen, largest1CTA N128 with nonpower2 topK/partial tails, existing33 exact cases, then bounded fixed-winner CAAC only if codegen passes. No sanitizer, clock changes, quota sweep or retune.
