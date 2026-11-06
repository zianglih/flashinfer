# R6 independent protocol/source review

Frozen kernel `deba8b63`, patch `473cf890`, retained base `d35fcfda`. Read-only; no production edits or GPU work.

No source-level blocker found. The actual change implements the reviewed local Gather4 protocol: local count129, one `gather_thread == 0` arrive-expect transaction announcement after operand-empty, all128 SF noinc completions, and every Gather4 completing locally with literal CTAgroup1. Payload byte arithmetic matches every issued nominal512-byte gather transaction in all40 checked geometries. The global operand barrier now counts only weight/SFA TMA for gather FC1.

All R4 kernel AST changes are accounted for by those completion changes and storage/trace names. The20 other class methods are unchanged after the storage rename. The existing TMA descriptor layout, flattened row/K issue, local SF layout, relay acquire/proxy-fence/cluster-release, consumer parity/advance, CLC quorum, final joins and storage planner are preserved. The standalone helper retains its CTAgroup2 branch, but R6's only gather call supplies the compile-time value1; emitted code must confirm that specialization.

The extra pending arrival prevents a local stage from completing before expected bytes are installed. SF and payload may complete in either order. Warp1 observes both before publishing to leader-ready; MMA observes weight/SFA and both CTA gather completions before consuming/releasing. Thus the existing operand-empty ring still protects all local barriers and shared buffers across wrap. The abstract298,248-state byte/count proof is hash-bound from `r6-feasibility/counter-proof.json`; it is not a hardware memory-model test.

FC2 kernel/load_weight_stage partially evaluate exactly to the retained source under gather=False and its256-thread domain. No host/public/tactic contract changed. Source receipt and replayable CPU check are `receipt.json` and `audit.py`; the frozen text snapshot is `kernel.py.txt`. Compiled address semantics, exact numerical output, resources and performance remain parent-run qualification boundaries.
