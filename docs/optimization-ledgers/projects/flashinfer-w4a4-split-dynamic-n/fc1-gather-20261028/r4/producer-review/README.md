# R4 SF completion relay

Frozen kernel `6fae1558326e72aa8beab25520c9e7be1734e03b6ff39d190025f2445d09ed2a`; patch `91e06acd3dc4f378411cecee85d00a144d028cbb728627018aa38a707f233148`. The replayable source proof is `check.py`, with results in `source-proof.json`. Production source remains unstaged and frozen.

R3's gather warpgroup waited for its SF copies after every operand stage, then issued 128 release arrivals per CTA to the leader. R4 replaces that sequence with a local asynchronous completion barrier and uses otherwise idle warp 1 to publish SF readiness once per CTA. Gather4 addressing, TMA byte accounting, SF copy predicates, and numerical operations are unchanged.

Each of the 128 issuing threads performs one `cp_async_mbarrier_arrive_noinc` after its stage's SF copies. The CTA-local barrier is initialized to 128 arrivals. This completion mechanism tracks the preceding thread copies without requiring commit/wait-group operations. Warp 1 waits with consumer parity starting at zero, fences the async shared view, and elects one thread to release-arrive at the leader's SF-ready barrier. That barrier expects one or two arrivals for the CTA group; group 2 explicitly uses cluster scope. Leader MMA waits for both ordinary operand TMA readiness and this SF readiness before S2T.

The existing operand-empty ring protects reuse. MMA cannot release a generation until SF-ready has been published and SF consumed. Therefore the gather producers cannot overwrite a stage before the relay has observed its local completion, and a second empty ring is unnecessary. Relay state advances once per acquired K stage, across work tiles; it consumes the same valid/padding/terminal CLC metadata sequence as the other roles. Adding its warp to the CLC quorum gives 352 leader / 320 follower consumers.

R4 adds one 8-byte local SF barrier per operand stage relative to R3. Both SF barrier arrays are included in shared-memory planning before stage selection. This can affect an allocation-boundary stage count; the proof does not claim stage-depth identity. FC2's `gather_input=False` and 256-thread partial evaluation reproduces the retained kernel and weight-loader ASTs exactly; actual compiler identity remains a separate qualification.

The earlier `r4-design/` folder records a deferred payload-row-prefix idea. It is not implemented by this R4 relay revision. No payload pruning, register policy, tactic change, or SF arithmetic change is included.
