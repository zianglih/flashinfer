# W4A16/finalizer cleanup review

Owned sources are frozen and unstaged in the primary PR checkout. Base 658a0c89. Hashes and checks: `w4a16-finalize-cleanup.json`; scoped patch: `w4a16-finalize-cleanup.patch`.

Changes:
- Move regular B atom-kind selection and global tiling/partition setup into the existing non-gather compile-time branches. Gather FC1 does not construct unused regular-TMA views. The same four assignment expressions remain for non-gather execution.
- Finalizer stores the original mapping value and tests its sign directly, removing expanded-mode compare-to-Boolean followed by Boolean-to-valid conversion. Explicit expanded/permuted row selection remains; load masking, ordered first-slot multiply/subsequent FMA, vectorization and barriers are unchanged.
- Correct the stale finalizer PDL doc: W4A16 FC1 acquires sort output, publishes routing and signals FC2; there is no standalone prepare/permute in this retained path.

Self-review findings:
- **Fixed, high confidence:** unused regular-B setup in gather FC1; redundant expanded-route validity representation; stale publication description.
- **Preserved:** dequantization byte-permutation optimization and toolkit conversion paths; all stage/tactic calculations, register targets, layouts, one/two-CTA behavior, producer ownership, synchronization and PDL instructions. No rejected A/B or thin producer experiment is included.
- **Validation boundary:** syntax, scoped repository hooks and source-level equivalence checks pass. GPU compilation/runtime validation remains for the combined cleanup. Relevant checks should exercise W4 gathered FC1 and regular-TMA FC2 with one/two CTA, plus both finalizer layouts with negative/all-masked routes through existing accuracy coverage. No performance gain is claimed from this cleanup.

No source files outside the assigned W4 kernel/finalizer were edited; `moe_w4a16_utils.py` is unchanged. No commit, push or GPU launch was performed by this agent.
