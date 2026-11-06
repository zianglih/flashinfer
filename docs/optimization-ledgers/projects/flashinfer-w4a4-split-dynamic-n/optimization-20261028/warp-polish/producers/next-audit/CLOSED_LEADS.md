# Bounded follow-up producer/MMA/scheduler audit

Read-only audit against the retained sole-announcer candidate (`5d3b3b003b37052671aa362bb2d41166e64dca7e12ae14ab11f6da838a3c9bd4`) and its existing generated code. No additional small runtime optimization is justified by the inspected evidence.

- **MMA/SF elections:** repeated `elect.sync` in PTX is not repeated hardware election. In config9 CLC FC1 PDL-on, PTX lines roughly 2138–2369 contain the helper elections; the SASS region `0x6ba0`–`0x6fa0` issues the SF copies/MMAs with no `ELECT`. The compiler already merges the elected issue region. A source-only hoist would not demonstrate instruction savings.
- **Dynamic-N descriptor work:** rounding and descriptor-bit setup are already outside the K loop. No repeated K-loop N calculation was found in the inspected variants.
- **Operand waits and reuse:** both independent producers need the local empty-phase wait. The one full-phase announcement is now retained. MMA releases the shared stage only after all A/B/SFA/SFB consumers (including both channel tiles) have been enqueued, so splitting/removing that release would need a new lifetime protocol rather than a cleanup.
- **CLC metadata and request ordering:** consumers release metadata after loading it; the scheduler acquires a free metadata slot before taking another CLC request. Existing request-ahead experiments already rejected hoarding pressure. The final join protects terminal metadata consumers. No redundant wait with a clear dependency proof was identified.
- **Startup rendezvous:** TMEM retrieval's all-thread join also publishes initialized operand and metadata barriers. Bypassing it for producers without a replacement synchronization would not preserve the existing initialization proof.
- **Weight-cache neighbors:** the two adjacent-expert reads happen once per work tile. Moving them to scheduler metadata adds work on the sensitive scheduler and changes the metadata contract; no generated-code evidence currently justifies it.

## Per-token single-transpose lead is already rejected

`scripts/per_token_single_transpose_20261026/{README.md,source.patch}` implements exactly the proposed native-token scaling mechanism: token `2*i+(lane//2)%2`, per-token scale broadcast, unchanged multiply/activation rounding, and a single transpose of the activated result. Its proof covers 512 coordinate assignments and 16,896 expression comparisons; five GPU selectors passed. It reduced FC1 registers (110→100 for N16, 107→96 for N128) and TMEM instructions but added 16 shuffles. Three-model public C-A-A-C geomean speedups were V3 0.999513, V41F 0.997873 and K3 0.995208, so it was rejected.

The present epilogue has since moved accumulator release immediately after the two transposes and before activation. Repeating the historical transformation would hold the native accumulator/scratch through activation, losing that newer release opportunity. This is the same mechanism, with no new evidence to reopen it; no patch or GPU repeat was made.
