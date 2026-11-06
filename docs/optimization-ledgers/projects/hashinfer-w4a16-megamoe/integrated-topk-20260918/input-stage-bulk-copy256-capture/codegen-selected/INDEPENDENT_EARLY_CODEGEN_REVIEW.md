# E1 early selected-code review

PASS for the available early evidence only. Reviewed frozen `0103fe15`, H7168/T16384/EP8, actual selected tactic1 and `fused_int32_align32`. No new GPU/remote action or source/runtime change.

All local early PTX/SASS, six rank0 resource reports, rank0 result, helper/fixture/driver/selection/plan, finished record and closure hashes match the immutable273-member collection receipt. Source identity matches the frozen104-file manifest. The sealed full archive is203226588 bytes, SHA256 `fd77dcf0ed5b653a72cbaa59106c40f1eb158f69efbb4a0d65efb303569658c7`; its local archive remains0 bytes because transfer was intentionally deferred before F1 timing. This is not a full archive/member or all-rank audit.

## Actual staging instructions

Rank0 `early-rank0/00-Sm100W4A16MegaMoEKernel-fused_int32_align32.ptx:4132-4150` preserves one128-bit head copy, then `ld.global.v8.b32` at4143 and `st.global.v8.b32` at4145 for each bulk pair, followed by the existing async-global fence. Bulk starts at head worker+9472 and increments18944, matching W/2 and W for148CTAs×128 dispatch threads.

The actual SASS confirms:

| Part | Address | Instruction |
|---|---|---|
| Head load |0xb440|LDG.E.128|
| Head store |0xb4a0|STG.E.128|
| Bulk load |0xb4e0|LDG.E.ENL2.256|
| Bulk store |0xb520|STG.E.ENL2.256|
| Bulk backedge |0xb530|conditional branch to0xb4c0|
| Writer fence |0xb560|FENCE.VIEW.ASYNC.G|

Therefore this captured alignment family emits a true256-bit staging load/store pair. Other256-bit stores elsewhere in the kernel are not evidence for staging. The first stripe keeps the128-bit mapping. Source/destination bases are loaded before this loop; this observation does not establish performance or register-pressure causality against a different source/tactic.

All six local rank0 resource reports show REG96, STACK0, LOCAL0, SHARED1024. Selected align32 PTX has no local loads/stores; its SASS has no LDL/STL. There is no observed spill in this selected variant. Other ranks' resource reports and other ABIs' SASS are still deferred, so this does not independently establish all48 resource records.

## Execution and closure limits

The hash-bound rank0 record reports the actual align32 selection, bit-exact eager repetition and two graph replays. The pinned helper enforces finite and exact checks. Generic/int64/align16 variants compiled but were not exercised by this canonical fixture. Offset/strided/native fallback coverage remains the separate unexecuted plan; this capture imposes no new input assumption.

The hash-bound terminal record has returncode0, one completed capture case and no GPU processes. Closure identifies the same hu15 boot, exact source, eight rank records, no owned process-group members and no GPU processes. Only rank0's full record has been independently read here; saved output bytes and the other seven records await transfer. The timing winner is bound through the original E1 finished/log/seal hashes and the selection/driver checks, but original E1 timing payload reparse remains deferred in this review.

No speedup, performance causality, full numerical/sanitizer qualification or promotion claim. Machine-readable scope and pins: `independent-early-codegen-audit.json`. The full256 candidate remains an experiment whose measured value must justify any later retention.
