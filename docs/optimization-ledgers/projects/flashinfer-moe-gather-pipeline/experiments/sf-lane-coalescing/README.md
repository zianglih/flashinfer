# Gathered-SF lane coalescing — CPU implementation

The unstaged review is `flashinfer-sf-lane-coalescing-review`, branch `codex/sf-lane-coalescing`, based on clean retained `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`. Only `moe_swap_ab_kernel.py` changes (+37/−24); canonical `flashinfer/` remains clean. Candidate SHA is `868363559094068c95c1c5c85257ac1a351e4a59d8efb594b029e7530347faab`.

Both Git directories stay inside this project:

- Worktree Git directory: `flashinfer/.git/worktrees/flashinfer-sf-lane-coalescing-review`.
- Common Git directory: `flashinfer/.git`.

The implementation uses the existing [CPU mapping](../../audits/sf-coalesced-lanes/README.md), with `G=min(tile_k/(4*sf_vec_size),4)` derived internally. It replaces the old mapping; there is no extra API, tactic axis, dtype/model policy, helper, or runtime branch.

For each warp, the first owned row is the old permutation at `lane/G`. Row batch `q` adds `q*(128/G)` rows and `q*(16/G)` shared bytes. Copy step `s` owns word `G*(s/G)+lane%G` and row batch `s%G`. G1 preserves the old per-thread order exactly. Static SF participants are the threads whose minimum row is below route_tile; this equals `min(128,route_tile*G)`, matching the local barrier count plus the unchanged payload announcer. All payload coordinate work, copy width, zero/live predicates, waits, relay, layouts, stage counts, quotas and public signatures remain unchanged.

`source_proof.py` extracts the actual modified arithmetic/predicates from its AST, compares it with the original proof functions, and checks canonical source/destination word identity, unique ownership, all live/zero/unused classifications, and exact arrivals. It covers 40 CPU parameter combinations (20 row/word geometries × two SF vector lengths), 23,040 owned-word records and 38,076 padding/CTA/K-tail classifications. The four declared source regions invert byte-for-byte to the baseline; all signatures and the `_copy_gather_sf` call predicates are equal. Python syntax, `git diff --check` and all applicable scoped pre-commit hooks pass. These are CPU checks, not DSL compilation or numerical validation.

Source complexity is bounded but not free: one private derived constant, one extra constexpr row-batch loop, a two-dimensional register-offset array, and replacement row/word arithmetic. Each thread retains G offsets instead of one, or 2G instead of two at N256: up to six/twelve extra logical 32-bit slots before allocation. The valid source predicate now varies across adjacent lanes even at a common copy step. The unchanged canonical shared layout also puts G distinct word destinations in each selected bank. No claim is made that these effects are free, that registers remain unchanged, or that unique DRAM bytes decrease.

The separately captured retained TP PC evidence supports testing SF issue pressure; it does not establish this candidate's benefit. Native qualification must inspect actual allocation/LOCAL, full-K predicate lowering, cp.async sites and scheduling before any timing decision. No GPU work, sanitizer, commit, push, or retention has occurred for this candidate.
