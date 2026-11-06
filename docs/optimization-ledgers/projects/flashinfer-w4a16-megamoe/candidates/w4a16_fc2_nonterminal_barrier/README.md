# Nonterminal direct-FC2 epilogue barrier

Held source-only candidate; primary is untouched. Based on the CLC-removed epilogue SHA256 `6026bd7a265c4be5e273c4c1af2cbe62dd4eda132ef0944b1f4f70489e69bfde`, independently compared with the retained default path from HEAD `16b7170fe793825ba07cf0f521f4745902c8cc1d`. The removal commit and this optimization must remain separate.

Only the existing BAR1 site in `W4A16Epilogue.run` changes. The existing constexpr `token_back_by_dispatch` keeps the unconditional barrier for dispatch-return mode. Direct epilogue return keeps it for FC1 and whenever the already-consumed NEXT record is invalid; it skips the barrier only after FC2 with valid NEXT. No new knob, state, helper, thread role, stage or allocation is introduced. Both decode WGs and five total WGs remain unchanged.

| Completed tile / NEXT | Direct epilogue return | Dispatch return |
|---|---|---|
| FC1 / valid or invalid | Keep BAR1 | Keep BAR1 |
| FC2 / valid | Skip BAR1 | Keep BAR1 |
| FC2 / invalid | Keep BAR1 | Keep BAR1 |

## Ownership and ordering

- **Publication:** FC1 completion still follows its bulk-store drain and the four-warp barrier. Dispatch-return FC2 still synchronizes before its completion flag can be published. In direct-return mode, `signal_fc2_done` uses a null address and `no_fire=True`; its existing tracker operations are unchanged. The FC1→FC2 transition flushes pending FC1 flags before the first FC2 record, and direct FC2 adds no address. Thus skipping an intermediate direct-FC2 barrier does not advance a release publication.
- **Barrier epochs:** BAR1 is the sole named-barrier site in the owned epilogue; the maintained kernel uses TMEM allocation ID2, while generic communication uses IDs8/9/10. The shared decoder's called transform path does not use BAR1. The saved default PTX likewise has one static BAR1 site. Both conditions come from identical records in the four epilogue warps; the generic scheduler copies a record to registers before releasing its slot (`moe_persistent_scheduler.py:169–191`). The retained barrier sequence is therefore the same subsequence of logical tiles in every participating warp, including zero-token/padded tiles. Warp timing can differ without mixing different retained epochs. No cluster-wide agreement is required by this CTA-local barrier.
- **Accumulator and scratch:** Every existing TMEM load/store/fence and every accumulator consumer release remains in its original order. The current warp-local transpose and accumulator-stage ownership remain unchanged; a faster warp cannot cause a stage to be overwritten before all consumers release it. The successor may use the other stage while remaining output packing/stores finish in slower warps. The final-stage release stays after the last scratch read, including the existing empty/partial guards.
- **Outputs:** The BF16 store mapping in `tmem_epilogue.py` gives warp `w` hidden columns `[32w,32w+32)` within its 128-column CTA tile; each 16-element store stays within that band. Token rows are `lane + 32*(iter//2)`. The existing feature/row predicates and routing preserve these disjoint writes. No intermediate consumer waits for a direct-FC2 flag; the kernel's final system fences and whole-CTA communication-tail rendezvous remain unchanged.
- **Termination is essential:** The terminal NEXT barrier remains even after direct FC2. Without it, warp0 could reach TMEM deallocation before another epilogue warp finishes its last scratch access. The saved default N64 PTX shows the BAR1 at line6469 followed, after loop exit, by warp0 relinquish/deallocation at6561/6588 and no intervening local four-warp barrier. Empty work retains the original zero-iteration behavior. No drain, reset or final flag flush moves.

## Evidence and limits

Saved `profiles/cu132-recovery0909e-central-default-{n64,n128}-001/codegen/compile-metadata.json` identifies `atomic_counter`, `epi_warps` and source57e2. Their default epilogue contains the unconditional BAR1 followed by FC2 tracker arithmetic with no FC2 release, so the operation is present in native code. These are control artifacts, not a native capture of this candidate. The current full-NCU winner used dispatch return; its sampled stalls do not measure this opportunity.

The existing `w4a16_fc2_no_publish_tracker` candidate removes only null tracker arithmetic and explicitly retains BAR1. Current/older ledgers and bounded candidate notes showed no trial of this intermediate-barrier elision. Activation-address preparation is already hoisted by native code; no-peek, decoded-readiness probing, stage/group changes and the rejected shared-operand-release design are not repeated here.

One syntax parse, Ruff check/format check and read-only patch-applicability check pass. Replacing the single new mode/phase guard with the original barrier recovers the entire base module AST exactly (`checks.json`). No tests, references, tolerances, benchmark scorers or selectors changed; no runtime imports, native compilation or GPU execution occurred. The benefit is unmeasured. Normal native review should confirm that direct-mode nonterminal FC2 skips BAR1, terminal/FC1 paths retain it, dispatch-return lowering stays unchanged, and no spills or unintended compute changes appear before using existing numerical/lifecycle and performance coverage.

Proposed epilogue SHA256: `b73fb2373f96821c3c815f116044d87116d67023317525a4c6ac6b802052d3d4`.

Patch SHA256: `988e57ec1fc2ccf07db9c882c6e1399da890d2405c51b5fafdde8809f67f534b` (+6/−1, one file).
