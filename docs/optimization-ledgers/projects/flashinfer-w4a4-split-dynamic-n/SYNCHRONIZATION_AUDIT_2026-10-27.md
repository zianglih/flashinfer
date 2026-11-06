# Split CuTe DSL MoE synchronization audit

Retained baseline: `9334cb34fe9c81653dc4748632f44449e9aecd8d`.
Retained result: `ed67c4857ce4e8d8cc047cf3808e2efa65e874b2`, pushed to PR #7290.
Scope: Blackwell split blockscaled MoE, including standard/per-token NVFP4,
MXFP8 and MXFP4×MXFP8, one-/two-CTA MMA, static/CLC scheduling and the input,
quantization and deterministic-combine handoffs. Rubin and MegaMoE are references,
not modification targets. The shared FC1/FC2 scheduler flag remains the retained
policy; no replacement tuning axis is introduced.

## Dependency map and initial disposition

| Resource / operation | Required ordering | Audit disposition |
|---|---|---|
| Routing → routed input | Count, mapping and limits are produced upstream | Keep preparation's PDL wait before metadata reads. No intra-CTA sharing in the row/vector copy requires a CTA barrier. |
| Routing publication → weight prefetch | Weights/scales are immutable, but expert selection needs completed routing | Keep the explicit ancestor release and designated startup trigger. Cache hints cannot replace publication. |
| Barrier construction | Every consumer must observe initialized barrier state | Retained common init fence plus CTA/TMEM or cluster rendezvous supplies this. Do not repeat rejected startup splitting that added more instructions. |
| Weight/SFA/B/SFB stages | MMA needs all operands; producers may reuse a slot only after its last UMMA read | Audit full-barrier sharing and expected byte/arrival counts. The retained empty ring already protects shared operand reuse. |
| Narrow SFB cp.async | Each CTA's scale bytes must finish and cross the generic/async proxy boundary before group-2 S2T | Preserve local completion and proxy fences. Explore joining readiness to the existing TMA full barrier instead of a separate cluster ring. |
| Accumulators | Epilogue reads follow MMA completion; MMA overwrite follows the last relevant TMEM read | Preserve partial-overlap early-release windows and their internal waits. The previously removed terminal helper wait was redundant with callers. |
| Epilogue transpose / bulk stores | Cross-warp layout conversion and shared-buffer reuse need publication/completion | Audit each barrier against the actual reader set and bulk-store ring; do not merge lifetimes merely because their storage is adjacent. |
| CLC result → metadata | Cancellation result completion precedes decoding; all metadata readers finish before the slot is overwritten | Keep one metadata slot and existing acquire-before-cancel order. Deeper queues, elected-owner handoffs and request-before-acquire were previously rejected. |
| Scheduler → teardown | No role may outlive shared storage or TMEM | Keep the final all-role join. Audit the following 128-thread allocator join for a distinct dependency. |
| Per-token quantizer | Warp maxima are published before cross-warp reads; next row cannot overwrite shared reduction scratch early | The reduction barrier and loop-end reuse barrier remain. Remove the redundant intermediate two-pass barrier if source-paired replay/codegen confirms the proof. |
| FC2 → deterministic combine | Routing can be read early after ancestor publication; expert output requires FC2 completion | Keep the combine wait immediately before output loads. No intra-CTA barrier exists or is needed. Ordered multiply/FMA contract remains unchanged. |
| Host orchestration | Workspaces live through the same-stream chain; fused zeroing/localized fork-join needs its own event ordering | Ordinary deterministic split path does not add stream/event waits. Existing fused-finalize and Rubin/localized event paths remain untouched. |

## Validation policy

Use source-bound changing-route exact replays before timing changes that alter
barrier participation. Inspect PTX/SASS, barrier counts, registers, spills and
storage for instruction-cleanup candidates. Preserve persistent native C++ caches
and private changed-source DSL namespaces. Use the completed shared-flag campaign's
five-field winners for fixed comparisons on V3 EP8, V41-Flash EP4 and K3 EP8, all
four affected formats; NV includes input quantization and fused finalize remains
disabled. Record new baseline timing for the retained 9334 composition, without
relabelling older measurements. Broad correctness and sanitizers remain deferred.

Candidate-specific proofs, raw artifacts and decisions live under
`scripts/sync_audit_20261027/`.

## Candidate status

| Candidate | Change and reason | Current evidence |
|---|---|---|
| Quantizer fallback | Remove the intermediate CTA barrier after publishing the per-token scale; quantization uses registers, while the existing loop-end barrier protects shared reduction scratch reuse. | 24 source-paired exact graph replays and 18 existing wide-row tests pass. Six fallback specializations each lose one barrier site; registers, SMEM and stack stay unchanged. Two register-resident controls have byte-identical SASS. Approved for retention as instruction cleanup, without an end-to-end speedup claim. |
| Unused wide-SFB ring | Allocate the cp.async full ring only when that transport is used; derive matching metadata storage from the same transport predicate. | Retained with explicit 16-byte metadata alignment. Final codegen preserves or improves every checked wide CLC metadata load; storage decreases by 0–128 bytes. |
| Shared SF/TMA completion | Join the existing two-CTA SF publication arrivals to the TMA full barrier, preserving local cp.async completion, proxy fences, cluster acquire and common empty ownership. | Retained. Independent count/phase proof, 120 event orders, 1,600 abstract ring schedules and final device gate pass, including narrow M512 with CLC and static scheduling. |
| Terminal TMEM join | Remove the 128-thread join between allocator-warp permit relinquishment and free; the final all-role join and SDK peer-CTA handshake remain. | Retained. All 60 final core pairs remove exactly one barrier2 site; required lifetime, peer and completion operations remain. |
| Bulk-store reuse wait motion | Load and convert the next accumulator before waiting for the shared output stage; retain the same wait/join immediately before its first overwrite. | Retained. Real N256 stage reuse covers uniform/nonuniform per-token scales and both PDL modes; no instruction-count or register increase from this component. Combined timing is neutral. |

The quantizer 4over6 specializations already contain local-memory instructions
and 24–40-byte stacks in both arms; this audit does not claim they are spill-free.
The standard recipe uses no stack or spill instructions. The representative
model widths use the unchanged register-resident quantizer path.

## Retained composition

`flashinfer-sync-review-20261027/` held the final source experiment. It was
advanced to the pushed commit, verified clean and removed after retention.
Patch `b4fb9c7a20b216839f4e879b9b576df098d64a10ece2816bbd350f2dafb3223a`
changes three files by +41/−42. It combines the candidates above, explicitly
aligns the 16-byte CLC metadata record, and narrows terminal allocator admission
to warp0. Removing unused barrier slots had exposed an incidental 8-byte
metadata alignment in some specializations; the explicit layout requirement
preserves vectorized loads. The actual installed SDK struct checker covers
2,304 combinations with no scratch/payload offset or total prefix-size increase.

Independent source review verifies the exact composition and retained local
completion, proxy ordering, cluster acquire, stage reuse, final CTA join and
peer deallocation handshake. The final gate passes 120 exact replay comparisons
across 60 compiled core pairs, with no spills and register deltas of −8…+3.
Summed static SASS decreases by 1,049 instructions across those variants; this
is not a dynamic instruction or latency total. No new tuning dimension or
model/dtype dispatch is introduced.

The 48-point fixed-tactic CAAC screen uses fresh 9334 controls, saved shared-flag
selections, 10 warmups and 100 cold-L2 CUPTI samples per arm. It covers all four
affected formats on V3 EP8, V4.1-Flash EP4 and K3 EP8 at 32/128/4096/16384 tokens.
The result is timing-neutral: **1.000965× overall, 1.000658× decode and
1.001271× prefill**. The worst point is V3 MXFP4x8/16384 at 0.992868×, a 0.718%
latency increase. Independent review verifies all 19,200 samples and their
source, route and tactic identities. No AUTO or full public-table rerun was
needed for this instruction-cleanup retention decision.

See [all paired points and subgroup results](scripts/sync_audit_20261027/composed/independent-screen-review.md),
[source-bound retention receipt](scripts/sync_audit_20261027/composed/retention.json),
and [workspace advancement/cleanup](scripts/sync_audit_20261027/composed/workspace-bump.json).

The bulk-wait source motion does not imply that ptxas delays every instruction:
it hoists each issuer's own bulk-read `DEPBAR` early, but moves the 128-thread
reuse rendezvous after independent TMEM loads and some conversion. Codegen
shows no register increase from this component; the combined screen establishes
neutral end-to-end performance, not a meaningful speedup.
