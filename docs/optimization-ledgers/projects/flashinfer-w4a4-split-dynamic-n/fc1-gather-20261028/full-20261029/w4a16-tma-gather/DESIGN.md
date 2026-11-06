# W4A16 FC1 direct TMA Gather4

Prototype source: `flashinfer-w4a16-tma-gather-review`, unstaged against fb66a27e. FC2 keeps the existing regular-TMA four-WG implementation. Source tensors, layout contract, fixed autotuning tactics, and numerical contract are unchanged.

FC1 retains decoder warps 8–15 and adds activation gather warps 16–19. Register allocation is epilogue144 / control80 / decoder96 / decoder96 / gather64, with initial96 per thread and640 threads: 61,440 reserved registers. The same allocation is used for the separate cp.async comparator. All donation happens inside non-reconverging role branches after common setup.

B uses one existing `PipelineTmaUmma` ring. Four warp-level producer arrivals independently reserve their expected bytes; each warp issues its own Gather4 work and advances without a WG barrier, local completion ring, relay, or software commit. Hardware fills the MMA-ready barrier directly. Existing UMMA consumer release prevents overwriting occupied B slots. Weights/scales and dequantized A remain independent.

The Gather4 descriptor describes four 128-byte BF16 rows with the native K-major SW128 layout. Row IDs are loaded once per routed output tile and reused across K stages. Invalid rows use descriptor OOB zero fill. Source addresses are original token IDs decoded from the existing route map. Two-CTA dynamic N shifts the peer source rows by runtime N/2, preserving the original MMA contract. Four issuers split row groups and K64 chunks; K chunks are also partitioned across B multicast CTAs.

That multicast partition is necessary: issuing the entire B tile from every multicast CTA duplicated destination completion bytes and stalled the first one-CTA MMA / cluster(2,1) test. The corrected partition keeps the destination's total expected bytes unchanged, and the full N8–192 existing exact matrix passes for one-/two-CTA MMA and multicast clusters. No additional synchronization was needed.

Removing prepare also removes its routing publication. All FC1 roles wait on sort before reading route/scheduler metadata. Static pipeline/descriptor/TMEM initialization precedes that wait. The early FC1 weight-warp signal publishes routing ancestors to FC2; FC2 still waits for FC1 data at its activation producer. Scratch allocation remains because FC2 reuses hidden_workspace for its output.

Validation before performance:25 existing exact cases passed, captured FC1/FC2 cubins have zero local bytes and no LDL/STL. Six multi-K/partial-K cases with PDL are a separate follow-up. Performance uses identical native frozen W4A16 winners and paired C-A-A-C CUPTI timing against clean fb66 on the same GPUs, four tokens across all four models and EP/TP.

The first measured TMA prototype reuses Rubin's SM100 primitive and therefore uses its zero cache hint. After this source-pinned screen: extract a shared Blackwell Gather4 primitive, restore existing W4A16 activation evict-last priority, remove unused original_b kernel argument, and narrow static-grid ancestor publication to physical CTA0 (preserving CLC cancellation safety). Do not mix those changes into the current measurements.
