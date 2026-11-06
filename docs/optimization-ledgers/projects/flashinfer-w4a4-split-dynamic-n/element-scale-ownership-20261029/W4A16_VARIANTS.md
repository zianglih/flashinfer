# Frozen W4A16 ownership comparison

Both candidates are unstaged on base `658a0c8942c7454050f990c0be3083aa61b6a89f` in separate project-local review worktrees. No retention decision or performance claim has been made.

| Candidate | Workspace | Warp6 | Warp7 | Frozen kernel SHA256 |
|---|---|---|---|---|
| A, elements/scales v3 | `flashinfer-element-scale-review` | A elements; FC2 B elements | SFA | `0ba17644a3cb75f6096b7e549a2b8006aa1e86b8c81e97b521ce4e539e6db187` |
| B, crossed v1 | `flashinfer-crossed-producers-review` | A elements only | SFA; FC2 B elements | `b29cce29257e56d91ff2152ae6f423bc15e2eebad86640cbbe6174483d181228` |

Patches are `w4a16-elements-scales-v3.patch` (SHA256 `d9b5e766dcf05bd48d1452465abd9a7c1ccf94d03457cde921432cf4bb287164`) and `w4a16-crossed-v1.patch` (SHA256 `48078778b8ebf4416c446dc5a39a547ba799e29206520e27a6e346b1055900c7`).

Both preserve the final FC1 gather warpgroup, stages, tactics, register allocations, layout contracts, raw A+SFA full-byte total, one full-barrier announcer, independent raw/transform/B rings and existing MMA/epilogue lifetimes. Both activate warp7 in FC1 and include its32 metadata consumers. In A, the single raw tail stays in warp6; in B it also stays in warp6. The helper methods inherited by MegaMoE (`_setup_attributes`, `_transform_tile`, `_finish_transform_stage`, `_compute_stages_and_tmem_cols`) are AST-identical to the base.

The combined FC2 producer uses bounded lookahead in the existing metadata ring: A lookahead in candidate A, SFA lookahead in candidate B. It caches its current work item and tensor slice. The B payload cursor releases each metadata item exactly once after copying it, including the terminal item. No auxiliary metadata queue, public behavior flag or tactic axis is added.

Both probes controlling refill-loop branching now use `vote_all_sync(sync_object.test_wait(index,phase))`. CUTLASS's raw `try_wait` result is per-thread and may suspend; neither property is suitable for advancing a shared warp cursor without establishing convergence. `make_warp_uniform` alone is a compiler assertion, not a synchronization fix. The voted nonblocking query ensures all participating lanes observed readiness before the warp copies metadata or advances a cursor. The required-current-stage path still performs the normal blocking wait/acquire.

Candidate B retains an independently executing weight-element warp while the other warp waits for FC1 activations. It moves the bounded static lookahead to SFA instead. Its safety invariant is `issued_SFA >= issued_B`; if a raw slot is unavailable while the counts are equal, every older SFA and B stage has been issued and the independent weight-element warp can complete the old raw stages. It does not require another B operation from the blocked warp to free the slot. The metadata-ring invariants in `W4A16_CURSOR_PROOF.md` apply with SFA as the fast cursor.

Candidate A still exhausts ready A work before its first B dependency wait, but cannot issue new weights while that same warp is blocked. Candidate B preserves that weight-element overlap while moving the equivalent potential stall to SFA. This is a measurable ownership tradeoff, not an assumed win. B's source diff is +277/−138 versus base; A uses fewer helper functions. GPU measurements and register/instruction inspection should decide whether either benefit justifies the resulting implementation.

Scoped pre-commit, Python syntax, whitespace checks and inherited-helper equivalence checks pass. GPU exactness/liveness and performance for these hashes are pending with the benchmark agent. The earlier v1 passing smoke belongs to its earlier hash and does not validate these snapshots.
