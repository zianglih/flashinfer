# FC1 direct gather prototype

Frozen first source: `kernel-r1.json`; base `d35fcfda03875077b3af8455575cc1d20e866a8c`. The launcher chooses `gather_input=True` only for FC1. FC2 and W4A16 retain their existing input contracts. This is an unstaged experiment, not a retained result.

- FC1 uses 384 threads: weight warp 0; startup-publication warp 1; MMA warp 2; scheduler warp 3; unchanged epilogue warps 4–7; activation gather warps 8–11. FC2 stays at 256 threads. The extra warpgroup is included in TMEM allocation and final rendezvous. CLC consumers are 320 leader / 288 follower threads, replacing one activation warp with four gather warps.
- Gather4 moves four independently mapped 128-byte rows per command. Coordinates are retained across K stages. Each CTA uses the same dynamic-N row partition as regular TMA. Invalid logical rows use the source token-count OOB coordinate without reading invalid mapping entries. The original logical K descriptor zero-fills short trailing payload chunks.
- Linear activation SF is loaded by four-byte cp.async words; only 4-byte source alignment is required. Each of the 128 gather threads owns one row in each 128-row SF atom. SF remains full-N in both CTAs. The destination permutation and K-word/stage strides match the retained canonical SFB layout. Invalid rows and trailing K words are zero-filled.
- The weight warp still announces all TMA transaction bytes exactly once. Gather mode removes only SFB bytes from that count: weights, weight SF and Gather4 payload still use the existing operand-full barrier. Both producer roles wait the same operand-empty ring. MMA releases that ring only after all A/B/SFA/SFB uses, so no separate SF-empty ring is needed.
- SF uses one additional readiness barrier per operand stage. Every gather thread locally waits its cp.async group, fences the async shared view, then arrives once. For group 2, both CTAs publish directly to the leader with cluster-scoped release arrivals; the leader waits before S2T. There is no MMA-side relay. Counts are 128/256 for one/two CTA. All added bytes are included in the metadata planner before selecting K/depth.
- Removing prepare removes its routing publication. Therefore FC1 disables weight prefetch-before-wait: all roles acquire the preceding routing/quantizer dependency before reading metadata. The existing startup release still publishes completed ancestors to FC2, whose weight prefetch remains unchanged.
- Arithmetic, epilogue, native MMA grouping, SF-to-TMEM layouts and partial-K S2T are untouched. No tactic or public API axis is added. Source documents and static proofs do not replace the forthcoming GPU exact/codegen qualification.

## Initial codegen boundary

The first version intentionally does not add a guessed register redistribution policy. Its 384-thread launch can constrain registers compared with the retained 256-thread FC1. Compilation/resource evidence must check local and uniform spills and epilogue pressure before performance interpretation. The 256-thread FC2 specialization must also be checked for unchanged generated instructions/resources.

## Prior evidence used

`scripts/loader_experiment/README.md` and its immutable `loader_trial/baseline_core.py` supply the previously qualified Gather4 descriptor/SMEM organization. The old direct cp.async/LDG payload loaders were slower, especially prefill; this prototype uses cp.async only for fragmented SF. The old MMA relay and overlapping producer/epilogue ownership are not reused.

## Compile revisions

- R1 (`b0c061b7`): the four test groups stopped before runtime because CuTe traced the disabled regular-TMA branch and saw a `None` SFB descriptor. Its failed logs remain in the parent campaign.
- R2 (`21df6cc6`): dynamic role dispatch now contains explicit compile-time loader guards. No mapping, transaction, barrier, or arithmetic change. All32 parent-run existing tests passed (6directK/tails,8NV,14MX,4wrapper), zero failures/errors/skips. `kernel-r2-test-summary.json` binds the original receipts.
- R3 (`c259b6cb`): flatten `(row group, 128-byte K chunk)` commands over the four issuing warps. Distinct row coordinates remain hoisted once per route tile. `flatten-proof.json` covers all40 supported transfer geometries and5,952 live-row cases, including narrow group-2 tiles. All four warps issue when at least four commands exist. Scale waits/publication and stage advance remain once per stage. Source frozen pending parent-run GPU gate.

A possible later SF relay through otherwise inactive warp1 is only a hypothesis. It is not part of R3 and will not be introduced without performance evidence.

## R4 SF relay revision

R3's measured regression justified testing the relay hypothesis above. R4 (`6fae1558`) replaces the gather warpgroup's per-stage wait and 128-per-CTA ready arrivals with asynchronous local completion and one elected ready arrival from warp 1. The source-bound protocol, state/byte obligations and FC2 partial-evaluation proof are recorded in `r4/producer-review/`. Its CLC quorum is 352/320 and shared metadata increases by eight bytes per operand stage relative to R3. R3 remains immutable; timing and hardware qualification are separate from this source proof.

## R5 payload-copy diagnostic

R5 (`80dc6ad6`) uses128-bit cp.async for payload and SF under the same R4 local completion/warp1 relay, leaving weight TMA unchanged. This isolates the local copy path from Gather4's CTA-group transfer semantics; it preserves nominal payload coverage and stage allocations. `r5/README.md` and `r5/source-proof.json` record mapping, zero-fill, absolute SW128 addressing, expected transaction counts, historical negative evidence and qualification boundaries. It is a frozen experiment, not retained code.

## R5b and R6 compile revisions

R5 stopped at compilation because payload `source`, `destination` and `predicate` temporaries reused SF-copy names with different tensor container types. R5b (`7251f0ce`) gives the three payload temporaries separate names. Whole-module AST normalization proves that this is only a variable-name/formatting change; it does not change copy arithmetic or synchronization.

R6 (`deba8b63`) independently reconstructs R4 and routes CTA-group1 Gather4 payload completion into the existing local barrier alongside SF copies. Its129 arrivals combine128 SF completions with one payload byte announcement. Global TMA accounting now includes only weights and SFA. This is a separate transport diagnostic, with unchanged staging and four-warp task assignment; see `r6/sourceproof/README.md`. Both variants remain unstaged experiments pending qualification.
