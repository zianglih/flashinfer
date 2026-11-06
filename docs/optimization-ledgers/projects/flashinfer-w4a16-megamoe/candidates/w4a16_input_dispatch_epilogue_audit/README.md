# Input dispatch on the epilogue warpgroup

Source-only proposal against the observed combined safe-FC2 kernel **28a58c2d…**. No production file, runtime helper, remote environment or GPU was changed. The graph-scoring adapter was frozen separately before this audit. `source-and-proof.json` records fourteen source hashes and a CPU arithmetic check; it is not native or numerical validation.

**The direction is feasible and has a real overlap window.** The scheduler publishes count-derived work before input payload pulls finish. Moving input dispatch from decode group0 to the epilogue group can let both existing decode groups start in that window, while preserving512 threads and the65,536-register allocation. It trades delayed weight decode for delayed epilogue consumption. The source establishes that tradeoff, not an end-to-end gain or an explanation for an unbracketed cross-source timing difference.

Source references below use paths relative to `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/` in the repository.

## Work can be published before input completion

- `shim/w4a16/communication.py:51–76` completes the existing count/NVLink barrier, then has all128 input threads **arrive** on dispatch-to-scheduler barrier9 before calling `dispatch_pull`.
- `src/src/token_comm.py:570–575` makes scheduler warp7 the other32 participants. Current `shim/w4a16/kernel.py:1181–1191` then generates/publishes work without waiting for input-pull tail.
- Scheduler sizes alias the low32 bits of `expert_recv_count_sum` (`kernel.py:478–486`). The fused scheduler advances experts from these counts, not payload completion (`src/moe_nvfp4_swapab/fc1_fc2_fuse_sched.py:979–1025`). The extension performs only `peek_only=True` reads for FC1/FC2 readiness (`custom_ext.py:357–420`); its descriptor prefetch is the inherited no-op (`moe_persistent_scheduler.py:241–243`).
- Weight TMA and both decode groups consume published work independently (`kernel.py:1193–1235`, `897–1007`). The **activation** TMA role retains its FC1-ready spin (`1237–1257`, `token_comm.py:578–599`) and FC2 dependency on FC1 output (`1259–1267`). Those waits must stay.
- Work storage has480 consumers. Each read immediately releases that consumer's share after the copy (`moe_persistent_scheduler.py:170–191`); an epilogue consumer delayed by input dispatch prevents the three-slot metadata ring from overwriting unread work. Fresh role-local consumer construction remains essential (`1017–1041`). Both decode groups start from the original raw/decoded pipeline state and consume the same sequence.

Today decode group1 can begin, but decode group0 performs all its input pulls first (`kernel.py:918–928`). The decoded-stage arrival count includes **both** groups, so MMA cannot treat group1's partial decoded stage as complete. With input on epilogue, MMA may compute early ready tiles before epilogue starts, limited by the existing two accumulator stages and scheduler/decoded rings. This is bounded pipeline overlap, not an additional stage or unrestricted lookahead.

## Minimal role and ownership arrangement

Keep the physical roles and register layout: warps0–3 epilogue,4–7 control,8–11 decode0/output push,12–15 decode1. Only warps0–3 additionally perform input dispatch before their normal epilogue.

1. Preserve pipeline initialization and the **416-thread TMEM allocation rendezvous before input dispatch** (`kernel.py:1127–1175`). In particular, allocator warp0 and the rest of the epilogue group cannot defer allocation/retrieval until after a count barrier on which the scheduler depends.
2. Input runs at the initial128-register cap. Control still donates with one warpgroup-wide DEC80 (`1177–1179`). After input dispatch returns and its private temporaries die, epilogue executes the existing INC176 immediately before its unchanged body (`1352–1374`). Two decode groups retain128 each: `128*(176+80+128+128)=65536`. No additional register redistribution or dummy allocation is needed by this design; actual REG128 remains a codegen admission requirement.
3. Isolate input plus epilogue in a private JIT role method returning `None`. Keep the existing private transform method, minus its input phase, with no input phase value carried through MMA or decode loops. This follows the role-local source pattern that fixed the earlier512 CFG duplication.
4. Keep `token_comm.dispatch_warp_start=8` for **output and kernel-tail cleanup**. Normalize input's local warp index explicitly to0–3 in the private input phase; blindly calling its current `warp_idx - dispatch_warp_start` calculation from physical warp0 would produce invalid negative scratch/grid indices. Existing vendor phase bodies continue receiving the same local IDs, pointers and arguments. No public role or policy knob is needed.

All existing counts remain unchanged:

| Contract | Count |
| --- | --- |
| CTA / kernel-tail barrier8 |512 threads |
| TMEM retrieval barrier2 |416 threads: epilogue128 + MMA32 + decode256 |
| Scheduler consumers |480: every warp except scheduler7 |
| Raw consumers |8 decode warps × existing A multicast count |
| Decoded producers |256 threads × MMA CTA-V size |
| Accumulator consumers |128 threads × MMA CTA-V size |
| Dispatch-to-scheduler barrier9 |128 input threads + scheduler32 |
| Dispatch internal barrier10 |128 input threads initially; existing output cleanup group later |

These formulas cover M256/V2, M128/V1, physical C2 and C1 without changing masks, layouts, stage fitting or either return mode's precision. There are still twelve unique physical warps outside the four-warp input group; `num_other_warps=12` is correct despite role reuse.

## Scratch lifetime is the required additional contract

Raw weights, scales and activation SMEM **do not alias** communication scratch: `kernel.py:315–327` accounts for separate allocations, matching `1072–1074` and `1150–1168`. Epilogue receives no epilogue-SMEM storage and uses accumulator TMEM for its transpose scratch. Moving the input role therefore cannot overwrite weight TMA destinations or epilogue TMEM scratch.

Input and dispatch-based output **do reuse the same communication scratch**, however: four `pull_mbar` entries and four hidden-byte `pull_buffer` regions (`token_comm.py:535–543`). Input completes every TMA load, commits/drains every outgoing pool store, then flushes its final readiness flags (`1075–1148`). Output later issues TMA loads/stores into those same per-local-warp regions (`1355–1416`). The old single-owner ordering established this lifetime automatically; different physical WGs need an explicit handoff.

Do not infer that handoff from `transform_pipe.producer_tail()` or a consumer reading the scheduler sentinel. A CTA with no assigned compute work may read the initial sentinel while its input group is still pulling globally assigned tokens. With only a few scheduled tiles, consumers can also advance ahead of epilogue through free metadata/accumulator slots. A global token-return schedule can subsequently assign output work to that otherwise compute-idle CTA. Immutable count availability says nothing about scratch ownership.

For `reuse_dispatch_warps`, add one precise nonblocking-input/blocked-output rendezvous: all128 input threads **arrive after `dispatch_pull` returns**; all128 decode0/output threads arrive-and-wait after their unchanged transform producer tail and before any scratch use. The input side must not wait, because later MMA/epilogue progress is needed for decode/output completion. The256-participant handoff adds no shared-memory array and is compile-time absent for `epi_warps`. Source barrier IDs0–10 are already used/reserved; a separate private named barrier11 is simpler to audit than repurposing an earlier barrier generation. Actual emitted named-barrier IDs/counts still require codegen review.

The concrete source map is: barrier0 is reserved for implicit CTA synchronization;1 is epilogue128;2 is TMEM retrieval416;3 is the inherited deallocation reservation;4–7 are inherited epilogue-subtile reservations (`kernel_fc12.py:176–179`, `epilogue_refactor.py:986–987`);8 is kernel-tail512;9 is metadata-ready160;10 is dispatch128 and is also hardcoded in the reused software-grid primitive (`src/src/grid_sync.py:65–77,131–134`). The borrowed local decoder's named barriers are constructor fields for its standalone kernel, not calls inside the inherited transform helper. No called source path uses11. The proposal uses11 exactly once with the same256 count on both sides, including empty work/empty input; there is no new mbarrier allocation or generation reuse. Inspect native code for hidden/compiler-generated use before execution.

This is CTA-local, not another inter-CTA synchronization. On idle compute CTAs, output safely waits for local input completion; on active CTAs it usually arrives after substantial MMA progress. Every input group still completes the existing grid/NVLink count protocol and its full allocated input-pool writes without waiting for a compute consumer. It then arrives and continues into epilogue. A full raw/decoded/accumulator ring or a stalled output group cannot stop input pulls. Likewise, input does not wait for output's arrival or completion. Thus there is no newly introduced inter-CTA dependency cycle, provided input remains after the initial TMEM rendezvous and before INC176, and the input handoff remains `arrive`, not `arrive_and_wait`. Residency/grid assumptions are the existing512 kernel's assumptions because the launch/resource layout is unchanged.

The final512-thread barrier8 remains before counter reset, so input, epilogue, decode and output complete before shared-count reset and subsequent launch reuse (`token_comm.py:1783–1849`). Keeping cleanup on the existing physical output group preserves the vendor's local warp indexing, NVLink barrier cycles and zeroing strides. The FC2 workspace is fully allocated and its epilogue waits for no token-return acknowledgement; this handoff introduces no compute/output backpressure cycle.

## Recovering the output mbarrier phase without a live input scalar

The packed count's upper32 bits are **not this phase**. Input preparation adds `1<<32` for each CTA contribution (`token_comm.py:670–678`), and the cross-rank barrier sums that packed status (`756–780`). The returned `dispatch_pull` phase instead starts at0 after per-warp mbarrier initialization (`825–829`) and toggles once per actual token pulled (`1140–1142`). Reading only expert0/lane0's packed count cannot recover it.

Output already reloads every expert's low32 count into lane-distributed registers (`communication.py:114–129`). Let `T` be their sum, `G=4*num_sms`, and `g=4*cta_linear_id+local_warp_idx`. Input visits exactly `g, g+G, … < T`, independently of expert boundaries, skipped empty experts and padded pool offsets. Therefore:

```
pull_count = (T + (G - 1 - g)) // G
initial_output_mbarrier_phase = pull_count & 1
```

The numerator is nonnegative even at T0, since0≤g<G, so no new runtime case branch is required. Use sufficiently wide addition under the existing token/address range contract. Sum each lane's already-loaded valid counts (unused lanes remain0), then one `cute.arch.warp_redux_sync(..., "add")`; the repository already uses that integer reduction in `flashinfer/fused_moe/cute_dsl/blackwell_sm12x/moe_w4a16_kernel.py:1319`. This adds reduction/division arithmetic, **not another global read or a phase shared-memory handoff**. The existing warp sync is not a sum and cannot itself provide the phase. Retain the scratch ownership rendezvous above regardless of how phase is recovered.

`source-and-proof.json` records43,200 CPU cases comparing the formula to explicit strided expert walks, including zero counts, one expert, non-multiple-of32 expert counts, multiple rounds, sparse experts and several grid sizes. This proves the integer identity only, not its CuTe lowering. Reinitializing live mbarriers or reading the high32 publication count would change the synchronization protocol and is unnecessary.

An alternative preserves the phase directly without carrying it through either long role loop: after input's final drain, its lane0 stores the returned phase in the first aligned Int32 of **that warp's now-dead `pull_buffer` region**, then all input threads arrive on the same handoff. Output reads that slot only after the handoff and broadcasts it within its corresponding warp before its first TMA overwrites the region. H is at least32 and the buffer is16-byte aligned, so four per-warp Int32 slots fit the existing allocation for every supported geometry. This adds one shared store/load and a warp broadcast per local warp, with no extra global read or shared allocation. The input scalar dies before epilogue; output recovers it after decode, so it does not lengthen their live register ranges. The named-barrier ordering covers these ordinary shared accesses as well as the ownership transfer. It must not overwrite a buffer whose previous asynchronous store has not drained. This simpler direct phase handoff avoids count reduction/division; the count-derived option avoids modifying scratch contents but has more arithmetic. Neither variant should introduce a runtime policy branch, and neither removes the required ownership rendezvous.

## Reference, risks and a bounded future gate

The vendor swapped Mega places input dispatch on dedicated warps8–11 and optionally has a separate token-return group12–15 (`src/moe_nvfp4_swapab/megamoe_kernel.py:279–299`). Its standalone output uses **separate** scratch and starts after the same metadata-ready handshake (`token_comm.py:1688–1722`), reinforcing that early metadata and payload/scratch readiness are distinct. The BF16 Mega uses the same dedicated input group (`src/moe_bf16_glu/kernel_bf16_glu_fc12.py:297`). None of these inspected references directly implements input-on-epilogue; this proposal reuses their phase bodies and the existing512 full-register roles rather than claiming an existing kernel already has it.

The current effort's initial512 note already documented loss of input/decode overlap (`candidates/w4a16_dispatch_decode_reuse512/README.md:5,24–28`). The main ledger records the role-reuse/register experiment at758 and distinguishes later tuning versus source effects at1004/1082. No earlier input-on-epilogue trial was found in that targeted search. Current source has `enable_pdl=False` for its borrowed mixed helper (`kernel.py:261`); changing launch dependencies is not part of this intra-kernel role proposal.

If authorized later, the smallest artifact would change the two private W4A16 kernel/communication files only, preserving all vendor bodies, arithmetic, public dictionaries, return modes and resource fitting. First inspect sealed native compilation for all four geometries/both return modes: actual REG128,512 threads, unchanged two-group mapping, DEC80/INC176, no new decoder or epilogue locals, no MMA cloning, and exactly the one intended scratch handoff in dispatch-return mode. Inspect count-reduction code size and phase use. Then reuse the public ring/tail/empty-rank and all16 lifecycle gates, emphasizing compute-idle CTAs with nonzero dispatch work and graph relaunches. Only after those pass should matched same-source controls and full13 timing assess the tradeoff. No per-shape role selector or extra autotune axis is proposed.
