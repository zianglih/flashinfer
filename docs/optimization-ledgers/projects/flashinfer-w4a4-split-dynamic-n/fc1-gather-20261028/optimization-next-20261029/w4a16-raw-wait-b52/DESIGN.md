# W4 raw-ready plain wait

Remove only the optional cached raw-A `consumer_try_wait` result from the dequantization loop. Keep `consumer_wait` at its original point, decoded-slot lookahead, every state reset/advance, the cloned raw-stage release after transformed stores, fences/commits, PDL, stage capacities, register budgets, and tactics. Source AST is identical after removing only this token plumbing.

This differs from retained MMA/weight-producer plain waits and the rejected decoded-slot peek deletion. The raw-A readiness check currently overlaps later decode/store work, so removal can regress latency hiding; no gain is assumed from fewer instructions. Recent W4 sampled raw-ready waits are short, which motivates a bounded test, not proof that the check is redundant.

History search found no deletion of `peek_load2trans_full_status` in this effort's saved patches or original W4 ledger. Multiple prior notes call it useful but preserve it rather than isolate it. Peer review is pending before GPU launch.

First capture five existing native geometries, including N16/N128/N192 and FC2, without launching owned kernels. Require unchanged quotas/storage/tactics and no local-memory growth. Then run existing33 exact cases. No performance launch until a predeclared same-GPU CAAC screen; no sanitizer, retune or shape-specific fallback.
