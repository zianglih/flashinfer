# CTA-local Gather4 completion feasibility

Read-only design review against frozen R4 `6fae1558` and R5 `80dc6ad6`; no implementation or GPU execution. This is an alternative payload-transfer mechanism, not a proposal to relax the PDL routing wait.

The proposal is feasible with the existing two completion-barrier arrays and operand-empty ring. Use CTAgroup1 Gather4 into the issuing CTA's existing B allocation, completing on that CTA's local barrier. The R4 gather descriptor already uses a group1 copy atom; its 2D128-byte row box and SW128 layout can stay unchanged. Keep group2 MMA/S2T where selected: TMA's completion scope does not require matching the tcgen group value.

## Required counts and ordering

Initialize each local barrier to129. Every gather lane retains one cp.async noinc completion after its SF copies. One elected lane per CTA and stage executes arrive_expect_tx with local payload bytes:

```
B = b_copy_rows * tile_k * activation_dtype.width / 8
  = (b_copy_rows / 4) * (k_steps / 4) * 512
```

The announcement must follow the existing operand-empty wait and occur once, regardless of valid row count. Out-of-bounds Gather4 rows zero-fill their nominal512-byte transfer; expected bytes must not shrink with live rows. All four issuing warps use the same local barrier and CTAgroup1; do not clear its peer-CTA address bit. A single elected *warp* guard is insufficient unless also limited to exactly one of the four gather warps.

The pending129th arrival prevents phase completion before the expected-byte announcement, even if SF or other-warps' TMA completions arrive first. The model checks298,248 count states over40 geometries and proves completion occurs only after the announcement, all128 SF arrivals and all payload transactions. The maximum checked local payload is65,536 bytes. `counter-proof.json` is authoritative for counts.

Warp1 retains its local acquire wait, async-shared proxy fence and one elected cluster-scoped release arrival into leader-ready. That publication now covers both payload and SF. The leader MMA retains both waits: operand-ready for weights/SFA and leader-ready for gathered payload/SF. Remove payload bytes from the weight producer's expected TMA total only on the gather path. Do not leave both barriers accounting for the same transfer.

The leader-ready count remains1/2, metadata consumers remain352/320 and the local storage footprint is unchanged from R4/R5. Each CTA independently announces its local B extent. The existing group2 leader wait gathers both CTA publications before S2T/MMA touches peer storage. Existing operand-empty release still prevents the next generation from overwriting payload, SF or local barrier state before MMA consumption. The existing final rendezvous/drains remain required.

## ISA basis and qualification boundary

PTX permits CTAgroup1 completion when destination and mbarrier are in the same CTA; group2 permits a peer barrier. Mbarrier completion needs both arrival and transaction counts zero, and tx-count may be negative within its documented range. Noinc arrivals must be included in the initial count. [PTX tensor copy](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cp-async-bulk-tensor), [mbarrier phases](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-mbarrier), [cp.async completion](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-cp-async-mbarrier-arrive).

The source-level argument removes remote per-transfer completion and keeps one relay per CTA/stage. It does not establish that remote completion caused R4's two-CTA slowdown, or that the added expect-arrival will outperform R5 cp.async. Qualification must inspect actual group1 opcode/local barrier address, expected transaction count and both CTA publication paths, then use the existing changing-route/empty/tail/wrap exact gate. No added public knob, new ring, or shape-specific policy is needed.
