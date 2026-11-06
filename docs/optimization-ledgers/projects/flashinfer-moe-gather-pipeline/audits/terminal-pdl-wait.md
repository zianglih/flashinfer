# Swap-AB terminal PDL wait: dependency audit and minimal candidate

Base `02de7785c10847b3528340840bed40bd405d85b4`. Candidate is the three-line deletion in `flashinfer-terminal-pdl-review`, branch `codex/swap-terminal-pdl-wait`. No production checkout edit, new condition, role, barrier, state, stage, tactic or public option. No GPU run or performance claim yet.

## Proposed deletion

Remove only `moe_swap_ab_kernel.py:3559–3561`, the final `griddepcontrol_wait()` executed by MMA and scheduler warps when weight prefetch is enabled. Keep the following all-thread named barrier and TMEM release, every pipeline acquire/release/tail, startup payload waits, and weight-producer wait/publication/signal unchanged. This is the sole promising simple candidate from this audit.

## Exact dependency and progress argument

The PTX [griddepcontrol contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-griddepcontrol) distinguishes the per-executing-thread wait from the CTA launch signal. The wait completes prerequisites and exposes their memory; the launch signal is effective once per CTA, with a preceding GPU release publishing earlier memory to a dependent start. The [CUDA guide](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html) requires verification before consuming primary results, and does not require an independent role to re-execute the wait after its work. Neither document says every thread must execute it.

| Role / transition | Existing synchronization retained | Why the removed terminal wait is not its publication edge |
|---|---|---|
| Activation and epilogue readers | `:2733–2744` waits for `warp == activation_warp` or `warp >= 4` under prefetch | B/SFB TMA, output-scale/route payload reads and epilogue work remain after their original dependency wait. |
| Weight TMA / downstream signal | `:2900–2912` waits, conditionally release-publishes ancestors, then signals | This is the FC2 signal owner. Its upstream wait remains even when no weight tile exists. Removing another role's later wait cannot advance this signal. |
| MMA | `:3178` acquires the combined FC2 operand full barrier before any MMA; `:3271` releases after all channels | Activation producer first waited for the prerequisite and only then issued B/SFB TMA. Transaction completion, pipeline acquire and existing async-proxy/MMA machinery carry that data. MMA does not issue global loads of prior-grid activation payload. Its terminal wait occurs after all MMA submissions and cannot be the visibility edge for those submissions. |
| Scheduler | Reads `num_tiles`, `expert_idx`, `mn_limit`; CLC metadata publish and response waits at `:2770–2835` remain | Routing is already release-published by the earlier FC1 startup signal. A wait at scheduler exit cannot repair an unsafe earlier metadata read. The same readiness contract already permits weight-prefetch routing reads. |
| CTA completion / TMEM teardown | `:3562–3568` joins every thread before weight warp frees TMEM | Every activation and epilogue warp must have returned from its startup wait before it reaches this join. Weight also retains its wait. The CTA therefore cannot finish or free TMEM ahead of the prerequisite even if MMA/scheduler reach the join earlier. No wait for a future grid is introduced. |

In FC1, gather input means `prefetch_weights_before_wait=False` (`moe_swap_ab.py:247`), so the deleted block was already absent. The original FC1 all-role startup wait remains; its activation-warp release then startup signal at `:2745–2755` publishes routing before FC2 can begin. This is important because FC2 scheduler and weight prefetch intentionally read routing before immediate-parent payload completion.

For standalone FC2, the existing caller contract is unchanged: weights and the routing metadata read during prefetch must already be ready (or release-published by the early predecessor signal). If a custom caller instead publishes routing only at predecessor completion, the original FC2 is already unsafe before the terminal wait. The deletion does not widen prefetch, change any early read, or fix/relax that contract. Activation/output payload remains protected by direct waits.

## Boundary cases

- **No live work / no local experts:** activation and epilogue startup waits are outside all tile loops. Weight's terminal wait and signal are outside its loop. Scheduler still publishes/consumes its terminal metadata and reaches the unchanged CTA join. No payload pipeline event is needed to establish prerequisite completion in this case.
- **Ordinary scheduling:** warp3 may have no schedule body; it reaches the same CTA join. It has no dependent payload access. Static routing reads by other independent roles are unchanged.
- **CLC:** one outstanding cancellation and terminal metadata ownership are unchanged. All response drains and consumer counts are unchanged. The proposed deletion does not alter which CTA signals, cancellation eligibility, or grid-wide trigger requirements.
- **Two CTA:** every physical CTA retains its own activation/epilogue startup waits and final CTA join. The follower's otherwise inactive MMA warp can reach that join earlier but cannot release its CTA. Cluster operand/accumulator release and TMEM allocation/free protocol are untouched.
- **PDL off:** the deleted block already compiled out. No other statement changes.
- **Fused finalize:** same payload startup waits, weight wait/signal and final CTA join; no atomic or output initialization change. A source argument is not fused numerical validation.
- **Private startup-signal configuration:** if prefetch is paired with startup signaling, the activation warp still executes wait before its signal. Public FC2 uses producer-exit signaling.

## Established source comparison and honest limits

W4A16 FC2 already waits only in the activation TMA role (`moe_w4a16_kernel.py:1715–1747`); scheduler, static weight/dequantization and MMA roles have no corresponding terminal GDC wait. Its independent B and decoded-A pipelines protect consumption. This supports role-local dependency waits, but the safety argument above stands on the actual swap-AB edges rather than assuming W4 equivalence.

Rubin gather currently waits all roles at entry (`rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1731`), so it is not a proof of delayed-wait deletion. MegaMoE's terminal wait (`block_scaled_swap_ab_mega_moe_kernel_gen_specialized.py:1226–1229`) protects a different action: resetting router/workspace-ready counters after empty routes may have bypassed consumer work. This candidate does not remove or imitate that reset barrier; swap-AB only joins local roles and frees its own TMEM here.

Existing native base822 V3 TP MXFP8 T16384 FC2 capture `profiling/v3-tp-mxfp8-16k/fc1-pc/loaded-codegen/24679/fc2.ptx:3047–3055` has the explicit role predicate, conditional branch, terminal GDC wait and following CTA barrier. Its actual loaded SASS contains `ACQBULK` at0x8270 immediately before `BAR.SYNC...` at0x8280, with role predicate/branch at0x8230/0x8250/0x8260. Base822 has the same terminal block as02de; this is an emitted-site existence proof, not candidate codegen evidence or a performance attribution. Removing the block may let the compiler remove that site and predicate; measure actual codegen/resources before claiming an instruction count.

## Rejected alternatives in this pass

1. **Combine A/SFA readiness with gathered B/SFB readiness:** keep distinct. Swap FC1 uses the first wait to permit early SFA S2T issue while the gather finishes. FC2 already accounts for A/SFA/B/SFB together. W4 uses different raw-weight, decoded-weight and activation rings, and its decoded/activation release lifetimes differ. Merging requires new storage/phase policy, repeating rejected ownership experiments rather than removing a duplicate wait. The current MegaMoE separated weight/token loop likewise waits both pipelines before MMA (`block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:1549–1550`).
2. **Delete output scratch or accumulator barriers:** no new safe deletion established. All four epilogue warps store shared output fragments even though two issue output TMA; both shared-stage reuse and publication joins remain necessary. Earlier duplicate terminal TMEM wait was already removed, and writer-only bulk commit is now retained02de. Remaining PC barrier dominance is largely final role join, not evidence that a steady-state dependency can be dropped.

## Qualification still required

Independent source proof first; then paired compiled code/resource inspection and exact existing coverage including PDL on/off, static/CLC, one/two CTA, no-live-work and ordinary FC1→FC2→combine. Keep actual runtime cache/tactics unchanged. If resources change or a payload/trigger edge cannot be proven, reject. No native qualification, benchmark, sanitizer or retention claim is made by this note.
