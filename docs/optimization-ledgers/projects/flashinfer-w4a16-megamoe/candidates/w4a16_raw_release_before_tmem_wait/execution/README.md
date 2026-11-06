# Early raw-slot release — retained

Root retained source `3b42507e7fd9c405c9e4112a0692942dc303c6d2a2cfd5268aeb57e67f72f186` as a modest general scheduling change. Native confirms raw-slot release before TMEM-store completion while decoded publication stays fenced; source review and unchanged numerical checks pass. **Timing is marginal and mixed, with no new whole-run best.** Commit `ceb619b21b02fb9d6235edd3eed10ea06627ba51` is pushed to the fork: two files,+35/−8; all applicable hooks passed including mypy/Ruff, tested source bytes unchanged and checkout clean. The base is published cleanup commit `0f361bc04664c574c91f96ecff3c259b8d4fdb14` / source3efa.

The [complete tables](../../../logs/cu132-recovery0910a-raw-release-before-tmem-wait-independent-comparison-001/README.md) preserve all13 rows and selected tactics for each whole control. Negative latency change means lower latency.

| Whole control | 8–4096 latency GM change | Rows lower | All13 secondary change | Rows lower |
|---|---:|---:|---:|---:|
| Actual retained3efa BEFORE | −0.424211% | 6/10 | −0.034425% | 7/13 |
| Separate historical whole-best098c | +1.532273% | 4/10 | +1.960318% | 5/13 |

The published098c whole-run performance table stays unchanged. These sequential invocations are not a paired measurement; no row minima or drift adjustment is used. Tokens are global source tokens across eight ranks. Tokens1/2/4 remain in the table but do not determine retention.

Validation and closure are complete:

- Two direct-return native fixtures (N64/N128) show raw arrival after final register-fed TMEM-store issue and before the wait; decoded-full arrival still waits for store completion. Raw arrivals have waitmask0, the fence writes dependency2 and decoded arrivals waitmask4. REG96,640 threads,two decode WGs,STACK0/LOCAL0,200064/230784 dynamic shared bytes and grid[2,1,74] remain unchanged. See [native admission](NATIVE_ADMISSION.md).
- Unchanged eight EP2 rank tests/32 compiled objects pass for N64/N128 and both return modes, all REG96/640/two decode WGs/LOCAL0, scheduler2 and effective epilogue pair[2,4]. [Numerical summary](numerical-summary001.json) records original observations; completion is `ebaa79942850120d19f9713543d184ad8c3b7d612144e74378ff5659f886a858`.
- Full13/default8/AUTO100 original19307 exited0 in590.4240545899956s. Closure19932 and fetch71783 exited0. The original reader and arithmetic comparator each ran once:13 rows,104 compiled records,104 ranking records and1,300 samples. [Proof](../../../logs/cu132-recovery0910a-raw-release-before-tmem-wait-default-direct-auto-reconstruction-001/reconstruction.json) is `819534c5`; [result](../../../logs/cu132-recovery0910a-raw-release-before-tmem-wait-default-direct-auto-reconstruction-001/reconstructed-result.json) is `ee550fea`; [comparison](../../../logs/cu132-recovery0910a-raw-release-before-tmem-wait-independent-comparison-001/comparison.json) is `52304da1`.
- [AUTO closure](../../../logs/cu132-recovery0910a-raw-release-before-tmem-wait-default-auto13-direct-001-idle.json) `0d54a5c7` confirms source3b425/native38a68 unchanged and GPU/workers idle. No restoration or additional timing/test/profile run is required by this decision.

The shared split completion hook expands to the prior TMEM/SMEM default sequence; this is source preservation, not a fresh split compile or numerical claim. The historical135 host tests remain on8d; no fresh host run is claimed. Commit hooks passed as confirmed by root; root verified the live PR remains OPEN/draft at headceb619b21, body1b0b855f. [Source review](../INDEPENDENT_REVIEW.md) and [retention.json](retention.json) bind the exact patch, manifest, resources and receipts. This narrative update did not rerun readers, arithmetic, scorers or validators.

[PR readback](../../../logs/pr5019-raw-release-after-body-edit-001.json) and [publication preservation proof](../../../PR_BODY-raw-release-publication-proof.json) confirm that all numeric tables, history and profiling were preserved. Publication is complete.
