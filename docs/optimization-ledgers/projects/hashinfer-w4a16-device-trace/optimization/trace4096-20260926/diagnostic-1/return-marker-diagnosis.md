# Reuse-return marker scanner failure and minimal source fix

The failed 4096-global capture used HashInfer `4ba4b61f99a3b6af11b87975af6043978a35899a`, source-plus-fixture SHA256 `c22c4938e43d009f71b89ac578a9312eb86ea6ad663eb791057b9ab8e894a41f`. Preserve its raw capture and FAILED audit; it is not a qualified trace.

All four original CUBINs have 135 PMTRIG sites, but native IKET produced only 133 instrument points. `instrument-points.json` independently compares each native point against `original.sass`. The one anomalous window is the 2080-byte `pop_range` point `[0x12eb0, 0x136d0]`, containing three sentinels:

| Original SASS offset | Instruction | Intended endpoint |
|---|---|---|
| `0x12f00` | `@!P0 PMTRIG 0x4d` | Per-token return push |
| `0x134c0` | `@!P0 PMTRIG 0x1f` | Per-token return pop |
| `0x136d0` | `PMTRIG 0x1f` | Whole return-helper pop |

The separate outer dispatch pop is at `0x13730`. Event77 exists in the decode-context catalog but has no independent configured patch point. This establishes native scanner point merging rather than merely a missing long-duration range in final visualization. It does not assert that no other collector defect is possible.

Source inspection confirms both per-token endpoints share the same `current_expert_idx < num_experts_per_rank` work branch and the same additional representative-warp predicate. Their source stack is balanced. The extra `_iket_emit` predicate (`sm_idx == 0 and warp_idx == 0`) becomes predicated PMTRIG instructions, which the native scan merged through the next unpredicated pop.

Commit `df205c4da276a03ec9f91ec5a697466e995157ce` removes only that unused marker predicate assignment and its two marker-only `if` wrappers. Push/pop stay at the same positions inside the existing actual-token branch for every participating dispatch warp. No computational statements, branches, loops, synchronization, transfer operations, or waits move. The guide now describes actual assigned-token coverage. This is a HashInfer-only vendor marker patch and is not synchronized upstream.

- Source-plus-fixture SHA256: `ee7e6de8cc7c105968cc58cc10a453e07fe4e76bf1547245cd34559fc76ec832`.
- CPU proof: `../return-marker-source-audit.json` verifies the exact allowed edit, full-module computational AST identity after narrowly stripping only this method's marker calls/predicate, Python syntax, and both endpoints in the same actual-work branch.
- Scoped pre-commit and `git diff --check` pass. Existing hook policy excludes the vendor source; it was checked directly by the CPU AST/syntax audit.
- Fresh native baseline, capture, scanner bijection and all-rank numerical/structural audits remain required. This receipt does not claim the new generated code or GPU capture passes.

Expected runtime coverage after the fix: eight whole dispatch/return wrappers for reuse mode; per-token scopes only on CTA0/1 warps8–11, each nested in its own return wrapper. Token counts vary with existing atomic work assignment, and a recorded warp with no assigned token has no per-token scope. Do not require all eight warps to own tokens or retain the old representative-only location rule. The per-token scope still excludes its preceding expert-readiness spin.
