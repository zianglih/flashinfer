# Fresh-workspace initialization ordering

The matched diagnostic identifies an initialization-ordering vulnerability in the test's fresh-workspace launch sequence. A 0.5-second delay on rank 7, after symmetric allocation but before zeroing, stalls the first T2 launch. With the same delay and a collective synchronization after fresh workspace preparation, both T1 and T2 pass every tactic and strict BF16 reference check.

| Arm | Injected delay | Prelaunch synchronization | Result |
| --- | --- | --- | --- |
| Control | None | Original behavior | Both cases pass: 16 rank-local JUnit passes |
| Delayed zero | Rank 7, T2, first tactic, once | Original behavior | All eight ranks stop after the first forward; controlled stop after at least 86 seconds without progress |
| Delayed zero + barrier | Identical delay | Complete local initialization, then collective barrier | Both cases pass: 16 rank-local JUnit passes |

All three runs use identical sealed test, kernel, reference and runtime versions. The two delayed arms use the same helper and plugin bytes; their environments differ only in output paths and the selected arm. Each rank compiles 16 tactics during T1 and reuses those callables during T2. The protected arm executes all 16 tactics twice in each case: 64 logical reference comparisons, or 512 rank-local comparisons. There are no skipped tests.

The unprotected event logs show ranks 0–6 returning from the first frontend launch before rank 7 enqueues its zeroing. Sampled Python stacks from ranks 0 and 7 place the wait at CUDA synchronization immediately after that first forward. The negative run was deliberately interrupted and preserved; it did not hit its configured timeout and is not passing qualification evidence.

The original full-run stall at tactic 12 is strongly consistent with this timing-sensitive ordering problem. These diagnostics do not directly establish its exact device-level cause: no counter values were read, so a particular counter-overwrite sequence remains an inference. The no-delay control succeeds, which also argues against a deterministic failure on every T1-to-T2 transition.

This evidence validates a **prelaunch ordering correction in the test harness**. It does not qualify unsynchronized fresh-first-launch behavior in production. The full revised 104-case run remains separate validation.

Reproduce the artifact audit locally with `python3 runner/audit_numerics_init_ordering.py`. Its machine-readable results, source fingerprints, raw-event hashes, JUnit hashes and interruption receipt are preserved in `evidence/numerics-init-ordering-audit.json`; raw captures and archives remain under `diagnostics/numerics-t1-t2-*`.
