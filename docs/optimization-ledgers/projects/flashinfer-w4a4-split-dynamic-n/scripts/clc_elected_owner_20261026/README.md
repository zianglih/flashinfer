# Elected CLC response owner experiment — rejected

- Historical review source (removed after rejection): `../../flashinfer-clc-elected-owner-20261026`, clean retained base `9b4721b08057d0a488c1f0236467acb75c48cd00` plus unstaged `kernel.patch`.
- Patch SHA-256: `96cfbfbe7c2c779fcdaf9e46ce76f19d2989d879903f5037c8eefeb152925dc8`.
- Scope: device kernel and its local pipeline helper only. Host tactics remain the full six-field policy. Probes must explicitly choose CLC `True/True`; fixed timing uses identical saved native all-CLC selections in both arms without changing host enumeration.
- The separate shared-flag experiment remains unchanged at patch `76ded8f758dc1103f442c5f1c1256f7c43b162fb4c4a74e0323b3552da37852d`.

`PipelineClcOwner` reuses the installed SDK barrier construction and inherited wait/release/tail operations. Its empty barrier expects one owner per CTA. Only CTA0 waits for this empty phase; each CTA owner publishes its own local 16-byte full-barrier transaction expectation. A single elected owner invokes the private `_schedule_clc` helper in each CTA, keeping its loop-carried state local to that invocation. CTA0 issues the raw multicast query without a second election. The info ring still has one publisher and all existing worker consumers.

Protocol invariants:

1. The same metadata-slot acquire precedes the next query; empty/padded routes retain their original filtering.
2. The raw response is not reused until both owners have read it, executed the existing generic-to-async proxy fence, and released CTA0's empty barrier.
3. A peer may publish its local full expectation before CTA0 issues, or receive the completed transaction before it publishes the expectation. The pending full-barrier arrival prevents completion until both events occur, matching the FlashMLA protocol.
4. Both owners advance their producer state once per valid current work, and consumer state once per completed query. Terminal invalid work publishes the same sentinel without issuing a new query.
5. CTA0 retains the final raw-response producer tail; the existing final CTA and TMEM teardown joins remain. The delayed PDL wait remains outside election and still runs across the scheduler warp.

No queue-depth axis, first-tile bypass, TMEM allocation change, dtype branch, cluster-specific optimization gate, or math change is included. The loop still has IKET scheduler-item markers. The source evidence motivating the experiment is `../clc_reference_audit_20261026/flashmla.md` and the exact SDK captures there.

V3 validation completed: Python syntax compilation, `git diff --check`, and scoped pre-commit (including mypy and Ruff). V3 GPU validation passed64 exact replays/source and32 core pairs; both V2 and V3 were rejected by their48-point timing screens. See [complete results and codegen](owner-screen-results.md), [V2 disposition](full_screen/decision-v2.md), [V3 disposition](full_screen_v3/decision-v3.md), and [local clone cleanup](local-source-cleanup.json). V1 outer-elect loop failed IR dominance verification; its freeze is under `freeze-v1-elect-context`. V2 fixed-lane loop passed 64 exact replays per source and 32 core codegen pairs, but added static instructions; its independent 48-point timing evidence is under `full_screen`, and its source freeze is under `freeze-v2-fixed-lane`. Never attribute V2 results to V3. Election does not imply a 32x reduction in SIMT instruction issue or allocated registers.

`freeze.py` records the historical freeze procedure; the local source clone has now been removed. Source receipts, patches, validation logs, and timing evidence remain.
