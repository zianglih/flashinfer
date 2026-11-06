# SF ownership: linear eligibility and unsigned mapping

This is the final bounded repair after V1 and deferred-offset V2 introduced spills. It keeps V2's shortened address lifetime, then makes two source-equivalent mapping simplifications:

- Test `row_warp + group*row_warps < row_groups` before the row permutation. The permutation only swaps positions inside complete groups; the smallest incomplete group uses XOR0. `sf-payload-ownership-audit/proof.py` now checks exact eligibility equivalence for all3,006 current geometry/live-row/CTA combinations.
- Express `row_warp` and the nonnegative CTA source-group offset as Uint32. These values feed XOR/per-group bank selection; the unsigned range allows masks and shifts instead of signed quotient/remainder corrections. This does not import the rejected broader unsigned-offset experiment.

No new branch policy, tactic, register quota, stage, layout contract, shared buffer, or barrier is introduced. Source kernel `97931545a1d165a1ddcf2e77127c7dbc02251c4652b555c1c14e1f3ca651bd6a`, patch `950981dc8a53645643ba174633e6e8cf01da7e5307d4ce5ee8bfc02bf679cf16`.

Only one local review copy remains: `flashinfer-fc1-gather-sf-ownership-review`, based on475, unstaged. Earlier source/evidence remains immutable in its own persistent directories. Run the full23-case exact/generated-code gate first; no timing if local-memory or instruction-complexity regressions remain unjustified.
