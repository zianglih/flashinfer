# Early release of raw W4A16 weights and scales

Frozen base: `6be4971b2dc3720f168510d09190e6519da38e2c`. Candidate is an unstaged two-line addition/five-line deletion in the dedicated review checkout; exact source and patch hashes are in `source.json`.

The transform loop completes all reads of packed weights and their scales and materializes decoded BF16 values in registers. Release that raw shared-memory stage before storing the decoded values, so its TMA producer can refill it concurrently. Decoded output uses TMEM or a distinct SMEM allocation. The decoded-output fence and `trans2mma` commit remain after the store.

Each transform participant releases once using the existing clone of the old raw-stage state. The stage advance, both useful DQ readiness peeks, multicast arrival counts, register quotas, output math, scheduler, PDL, stage counts and tactics are unchanged. The finish helper no longer accepts the raw pipeline or its state because it owns only decoded-output publication.

Validation sequence: source/lifetime/alias audit; scoped pre-commit; paired compilation of four fixed native FC1/FC2 tactics with runtime-resource/SASS capture; existing 33-case exact gate; then a same-node fixed-tactic CUPTI CAAC screen if code generation qualifies. No sanitizer or new repository tests.
