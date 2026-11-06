# W4A16 A/B simplicity review

Read-only comparison against retained `658a0c8942c7454050f990c0be3083aa61b6a89f`, 2026-10-29. A hash `0ba17644a3cb75f6096b7e549a2b8006aa1e86b8c81e97b521ce4e539e6db187`; B hash `b29cce29257e56d91ff2152ae6f423bc15e2eebad86640cbbe6174483d181228`. Frozen sources unchanged.

**Conclusion:** Most extra control is the cost of putting one static weight stream and dependent activation loads on the same warp while preserving cross-tile PDL prefetch. Neither variant has a decisive control-flow simplicity advantage: both use the same bounded two-cursor protocol. A is slightly shorter; B keeps the retained weight-elements producer, PDL publication and raw tail together. Performance evidence should decide between them.

## Necessary state and control

| Addition | Why it is needed |
| --- | --- |
| Second metadata cursor | Static work can cross routed-tile boundaries before B starts. B still needs the original tile later. Holding the existing ring avoids a new queue or a second consumer release. Restricting prefetch to the current tile would remove this state but weaken the requested small-K/cross-tile overlap. |
| Cached fast work tile, tensor slice and K cursor | The fast and dependent cursors can address different tiles. The cached slice avoids repeating address/layout setup for every K stage and remains valid after B releases the metadata item. |
| Both raw and B producer states in one warp | These were already independent pipeline states in separate warps. They still need independent stage lifetimes. Their global counts provide the outstanding-work comparison; there is no extra pending counter. |
| Nonblocking raw/metadata readiness plus warp vote | Optional lookahead must yield to B instead of blocking on a raw slot whose progress eventually needs B from this same warp. Lane-uniform readiness is required before advancing a shared cursor or elected TMA issue. |
| Blocking when raw-issued count equals B-issued count | The current B stage must obtain its own A/SFA stage. Older B work has already issued, so this is the safe blocking case rather than an optional lookahead. |
| Copy-fast-before-slow-release catch-up | When optional prefetch did not reach the next metadata item, B must cache it for the fast cursor before releasing that ring slot. |
| First-B PDL acquisition and empty-work fallback | The payload owner must wait exactly before dependent loads; empty CTAs must still honor the grid contract. Reusing the B global count avoids another Boolean flag. |
| FC1 scale-warp metadata participation | Warp 7 now actually loads SFA. Its added metadata arrival and independent raw-empty wait are required. FC1 does not compile the two-cursor/B control. |

These additions apply to both static and CLC scheduling because W4A16 already publishes both through the same metadata ring. No new staging, shared storage, tactic axis or model-specific policy was introduced.

## Potential simplifications, with boundaries

- **Metadata-distance guard is logically redundant for correctness.** A lines 1931–1935 / B lines 1952–1956 test `fast_info.count - slow_info.count < num_tile_info_stage` before the full-barrier test. With the single slow release and retained barrier phase, wrapping onto an unreleased slot already makes `test_wait` false. The integer guard can still be cheaper than a saturated-ring barrier test plus vote, so deleting it is not an established instruction improvement. This is the clearest optional policy/control check, not an immediate bug or retention recommendation.
- **First-B test runs every K iteration.** A line 1996 / B line 2013 checks global B count zero; only the first occurrence invokes PDL. Hoisting would need an explicit startup-prefill phase or factoring/duplicating the refill body. There is no clean deletion preserving the current startup overlap, and compiled output may already simplify it.
- **Unused fields of the fast work-tile object are source verbosity, not proven device cost.** The fast cursor needs validity and the static slice coordinates. SSA dead-code elimination may remove other loaded fields. Inspect generated code before introducing a narrower metadata object.
- The repeated fast-work validity check while draining the final pending B stages is small control overhead. Folding it into the refill loop condition is a source cleanup candidate; no lower instruction count is established.
- Tensor zero filtering in B's `_weight_scale_slice` is CuTe layout construction at compile time. It is not evidence of repeated runtime scale traversal. Both variants cache the current fast slice outside the K-stage issue path.

No additional queue, branch whitelist, independent FC1/FC2 ownership tactic or startup-specific stage geometry is warranted by this review.

## A versus B

| Aspect | A: elements / scales | B: weight elements / activation + scales |
| --- | --- | --- |
| Merged FC2 producer | Warp 6: A + B | Warp 7: SFA + B |
| Independent static stream | Warp 7: SFA | Warp 6: A |
| Extra refill state/logic | Same two cursors and global-count comparison | Same two cursors and global-count comparison |
| Source organization | Literal elements/scales policy; two added helpers; +264/−135 lines | Retains old warp-role attributes and weight signal/tail location; four added helpers; +277/−138 lines |
| Possible scheduling benefit | Scales can progress independently of payload | High-byte weight loads can progress independently of payload |
| Shared limitation | Raw readiness still needs both A and SFA; a dependent wait can delay later static refill by the merged owner | Same |

B's extra helpers isolate the repeated scale-slice construction and empty-wait/copy operation; they do not add a new pipeline or extra runtime ownership state. A's smaller line count does not by itself establish lower kernel instruction cost.

## Profile first if timings regress

1. Warp 6/7 issue cost for `test_wait`, `vote_all_sync`, pipeline count/phase updates and refill branches; inspect generated PTX/SASS and register/local-byte receipts. Both FC2 streams now keep their cursor state live in one control warp.
2. Repeated unsuccessful refill polls per B stage, especially metadata polling at small K and per-stage raw-ring polling at larger K. Compare useful TMA issues per control instruction.
3. Raw-full/dequantizer starvation versus B-empty waits. A/B can shift which half of the raw A+SFA transaction arrives last; weight issue alone is insufficient evidence that the dequantizer can proceed.
4. PDL wait/startup interval and the first useful FC2 MMA: verify that the extra prefill work actually reduces the bubble rather than merely moving commands before a longer wait.
5. Metadata producer backpressure and slow release, especially across CLC turns. Existing IKET ranges separate TMA empty/issue, activation wait/issue and scheduler work; refine instrumentation only if those traces implicate refill control.

This review establishes source complexity and plausible overhead sites only. It does not infer performance or spilling from line count.
