# Eight-warp resource and lifetime audit

Read-only source audit at `1e69d0a391fd926d21a35388cacf2df3c1c22baf`, 2026-10-27. No kernel edits or GPU work in this audit. The initial redesigned kernel should preserve compiler register allocation; register redistribution is a separate follow-up.

## Role policy

Use one fixed 256-thread CTA: warp0 weights+SFA, warp1 activations+SFB, warp2 MMA, warp3 CLC scheduler (idle for static scheduling), warps4–7 epilogue. The current public wrapper always requests `overlap_epilogue=True`; preserving warps4–7 preserves the epilogue's `tidx-128`, `warp%4`, TMEM-lane and shared transpose ownership without a new mapping.

Current kernels launch288threads static or320CLC, with MMAwarp8 and appended schedulerwarp9. Wide-N TMA-SFB uses only one of the four allocated producer warps; narrow-N uses all four for cp.async SF. The new design removes the cp.async ownership group rather than appending an issuer to it.

|Resource|Initial proposed value/lifetime|
|---|---|
|Physical block|256threads, both static/CLC, `min_blocks_per_mp=1` retained|
|Operand full barrier|2 elected arrivals, weight/SFA and activation/SFB; both producer roles advance the same stage order|
|Operand empty barrier|One UMMA release after the last MMA using all four operands|
|CLC info consumers|224threads = two producer warps + MMAwarp + four epilogue warps|
|CLC fetch consumers|32×CTAgroup, unchanged|
|Accumulator consumer arrivals|128×CTAgroup, unchanged|
|Epilogue transpose barrier|128threads, unchanged (NamedBarrier6)|
|TMEM startup retrieve barrier|256threads (NamedBarrier3)|
|Final CTA join before TMEM free|256threads (NamedBarrier1)|

The weight issuer must wait the shared empty phase and announce its own expected bytes before issuing weight/SFA. The activation issuer independently does the same for B/SFB. A pending second arrival prevents premature full completion if the first issuer finishes early. Do not call the old aggregate-byte `producer_acquire` in addition. For group2, only CTA0 announces each role's **group-total** byte count; both CTAs issue their local transfers into the leader full barrier, preserving the existing TMA/UMMA cluster mapping. The frozen candidate uses the installed4.8 `PipelineTmaUmma.producer_acquire(expected_tx=...)` directly, replacing the earlier proposal to use the project-copy sync objects. The old project copy lacks this keyword; it is no longer used by this kernel.

Per-stage transaction accounting with `G=CTAgroup`, `C=channel_tiles`, `K=tile_k`, `S=sf_vec_size`:

- Weight/SFA role: `G*C*(128*K*weight_bits/8 + 128*K/S)`.
- Activation/SFB role: `G*(route_tile/G*K*activation_bits/8 + max(1,allocated_n/128)*128*K/S)`.
- The sum equals current wide-N total. SMEM uses `allocated_n`, not the logical TMA payload extent; mixed FP4 weights keep byte-slot storage while transfer bytes use weight width.

One producer's empty-only tail remains sufficient because the single MMA release proves all issuers completed each stage. This depends on identical iteration/stage ordering and the final256-thread join. Do not repeat per-role tails or arm unused full stages. The initial audit proposed signaling from the activation issuer. Final protocol review instead retains the weight-issuer producer-exit signal after its predecessor dependency wait. That signal permits successor startup; the successor dependency wait and operand completion barriers still guard dependent data. This avoids conflating PDL launch permission with completion of activation/output work.

## TMEM and SMEM

The initial redesign should retain the current all-CTA TMEM allocation/retrieve join and final join. That startup join also orders deferred pipeline initialization for one-CTA launches; removing it without another join is unsafe. Two-CTA launches already have a cluster init join. CuTe4.8 `cutlass.utils.TmemAllocator` is a deprecated alias; the actual `cutlass.memory.tmem.TmemAllocator` was read from the installed test environment and archived here with source hashes. Its `wait_for_alloc` is exactly the configured named barrier. Its allocator warp handles the peer mbarrier handshake in `free`; no extra128-thread free barrier is needed.

Keep the existing compile-time resource calculations:

- `allocated_n=max(32,route_tile)` (N16 still needs32-column epilogue chunks).
- `acc_cols=allocated_n*channel_tiles`.
- `scale_cols=(K/S)*(channel_tiles+max(1,allocated_n/128))`.
- Accumulator stages come from actual TMEM capacity, capped at2. Retain the protected overlapping-window lifetime rules; a role-count change does not permit releasing unread accumulator columns earlier.
- SMEM operand bytes stay `128*K*max(weight_bits,activation_bits)/8*C + allocated_n/G*K*activation_bits/8 + 128*K/S*(C+max(1,allocated_n/128))`.
- Always-TMA SFB removes the cp.async SF full barrier, not its shared SF storage. Compute metadata from two operand barriers per stage plus existing accumulator/scheduler allocations. Recompute capacity from actual device SMEM and layout sizes; no dtype/model-specific stage thresholds.

The proposed narrow-N global SF padding is a separate private layout change: pad each route's SF rows to128 while leaving payload compact. The activation-SF audit owner proves mapping/writer coverage. This increases only global SF workspace for narrowN; it does not require expanding current per-stage SFB storage. Existing full-SFB replication in two-CTA mode remains intentional.

## MMA/scheduler work

Always-TMA SFB directly removes the MMA's cp.async full wait, shared proxy fence, two-CTA SF arrival, cluster polling path, and related small-N branches. Weight and activation descriptors/addressing belong in their respective producer roles. The scheduler should continue publishing tile/expert/valid once for CLC; it need not own payload/SF work. Preserve terminal metadata, dependent launch publication and conditional ancestor PDL wait.

Keep SMEM→TMEM scale copies in the MMA role initially. Current scale TMEM slots are reused every K stage, with ordering tied to the following MMA. Moving publication to a producer requires a new ready/overwrite protocol or additional scale slots and can stall producer lookahead. The eight-warp role change alone does not establish that ownership transfer safely. Do not add an SF publisher or additional synchronization to the first version.

## Register redistribution boundary

Initial experiment: **no SETMAXNREG**. This separates the role/layout change from register policy. Existing1e69 artifact probes report72–128 registers/thread with no local/stack bytes across sampled narrow/wide, static/CLC and PDL configurations; these whole-kernel numbers do not prove any particular control-role cap.

A conservative later candidate is one common128-register control warpgroup and256-register epilogue warpgroup. The nominal sum is `128*128 +128*256 =49,152` registers per CTA, below Blackwell's64K SM capacity. This arithmetic is only a capacity screen, not proof of CTA pool reservation or spill-free role code. The per-CTA pool—not all otherwise-free SM registers—supplies increases.

PTX requires a warpgroup-uniform reconfiguration instruction, legal immediate24..256 in steps of8, and direction validity: initial allocation must be at least a `.dec` target and at most an `.inc` target. Therefore all warps0–3, including idle static schedulerwarp3, must execute the same decrease before role divergence; warps4–7 execute the same increase. Never put different caps in individual role branches. A second reconfiguration would require explicit warpgroup synchronization.

Current launch emits `.reqntid` and `.minnctapersm1`, not `.maxnreg`. Hopper finalize uses whole producer/MMA warpgroup40/232 caps under these launch directives; Rubin gather has group80/48/128/168 budgets. These establish repository style, not a safe initial allocation for the new smaller kernel. Do not assume a `.dec128` is valid when the compiler would otherwise allocate74 registers. A compile/resource probe must verify PTXAS allocation and generated SETMAXNREG, spill instructions and per-role live pressure. An explicit max-register ceiling alone is not an allocation floor. No new tactic axis or shape-dependent cap is proposed.

Primary reference: https://docs.nvidia.com/cuda/parallel-thread-execution/#miscellaneous-instructions-setmaxnreg and performance-tuning directives in the same document. Installed SDK snapshots: `sdk48-TmemAllocator.py`, `sdk48-MbarrierArray.py`, `sdk48-PipelineTmaUmma.py`; companion JSON files pin paths and SHA256.

## Prior experiments and why this differs

- `scripts/dedicated_weight_tma_experiment/README.md`: Gather4-era extra weight warp,288→320threads; isolatedFC1 small improvement but whole-chain bracket results conflicted. Not retained.
- `scripts/producer_roles_experiment/README.md`: regular-TMA smallN retained four cp.async SF producers, added a weight warp, then separate/shared empty rings. Whole chain regressed about1.6–1.9%. The later same288-thread three-TMA-issuer variant was neutral. Both left the small-N cp.async SF path intact and measured B200 narrowN; neither tested compact256threads with always-TMA scales.
- `scripts/clc_tmem_startup_20261027/design-v2.md` and `screen-v2/screen-results.md`: role-local TMEM startup synchronization was neutral/slightly negative and increased static code. Keep the simple full-CTA join for this redesign.

## Relevant current source anchors

`flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py`: topology/resource calculations1390–1560; launch2250; weight issue2318; pipeline/TMEM initialization2414–2515; producerloop2637–2877; epilogue2877–2980; MMA2980–3168; scheduler3168–3230; finalfree3231. `moe_swap_ab.py:253` selects dedicated epilogue. Surrounding Hopper/Rubin sources were used for style; SM120 was not consulted. MegaMoE's established80/256 split is a useful capacity reference, not a transferable measured cap.
