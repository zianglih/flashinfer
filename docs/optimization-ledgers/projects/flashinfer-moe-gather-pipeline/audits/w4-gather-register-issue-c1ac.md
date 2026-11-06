# W4 gather registers/issue versus MegaMoE and Rubin

**No new actionable W4 source change is supported by this bounded review.** The current gather role already caches routed coordinates outside K and shares election across native issues. The saved profile primarily shows reuse backpressure, while the reference kernels have different routing/publication contracts. No source, cache, sealed evidence, GPU or benchmark work was changed.

Current source is c1ac8ce7341039db65195b99445fcdeb193cf226, W4 SHA `cbef9186`. The entire gather-role source block (`moe_w4a16_kernel.py:2754–2871`) is byte-identical to measured2b8 (`89971ec2…`). The saved V41F TP4/T4096 FC1 profile remains a 2b8 measurement, not newly measured c1ac. Its loaded image and all PCs are bound by `profiling/v41f-tp-w4a16-4k/evidence/fc1-pc/pc-proof.json`; the native disassembly used here is `loaded-codegen/34019/fc1.sass` in that leaf.

## Actual native work

- Gather donation at `0x51d0` is `USETMAXREG.DEALLOC.CTAPOOL 0x40`: 64 registers/thread. The launch is 640 threads at initial96, LOCAL0, with222,208B dynamic shared memory and one-CTA/SM shared-memory capacity. The source's144/80/96/96/64 five-warpgroup allocation balances to640×96 registers. A smaller gather quota would not remove this shared-memory occupancy limit; quota redistribution is separately measured and closed.
- Before K (`0x5390–0x5820`), four route `LDG.E`,16 `SHFL.IDX` and16 `R2UR` sites build the cached row coordinates. The actual20-stage K loop (`0x5840–0x5ef0`, backward branch to`0x5840`) has **zero route LDG/SHFL/R2UR**, **one ELECT**, and16 Gather4 sites. Source-level per-copy election/accessor spelling is not repeated native election work.
- The loop still has uniform coordinate/descriptor moves and stage/column arithmetic. Those fields depend on the current K column and circular slot; this pass found no proven dead/redundant native definition. Packing them differently would require a new lowering/dataflow case, not deletion justified by source appearance.
- Existing `WAIT_DIAGNOSTIC.md` records **zero MMA B-full fallback queries after transformed-A acquisition**. Gather-empty fallback is taken98.956%, with5,898,964 polls for307,200 acquisitions. These establish reuse backpressure in this specialization, not a measured gather-supply or register-pressure bottleneck. PC/poll counts are not removable time fractions.

## Reference boundary

| Reference | Relevant source pattern | Why it is not a free W4 gather improvement |
|---|---|---|
| W4 MegaMoE `bf16_nvfp4/megamoe_kernel.py:977–1040,1250,1327–1387,1486–1509` | Distributed dispatch/staging owns a64-register WG; one80-register control warp uses ordinary BF16 TMA after token readiness. | Its source activation plane is already routed/staged. Removing split's four Gather4 issuers would move routing/data work into a different stage, not remove it. Same overall144/80/64/96/96 allocation is a different role assignment. |
| Rubin split `blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:335–369,1973–2086` | Four80-register gather warps, cached rows before K, broad elected issue scope, separate activation-SF gather/transform. | W4 has no activation-SF pipeline to eliminate. Its native election is already shared; the exact wider-scope W4 source trial added4 instructions/one branch in all three inspected cases. |
| Rubin Mega `block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:74–85,1175–1275` | Four warps explicitly bound live uniform row coordinates; aligned8-row vector loads consume a predecoded gather-index plane. A160-thread rendezvous joins TMA-B with Gather4. | Vector loading requires that different plane/ownership. W4 retains expanded-route IDs and native-top-k division outside K, with independent issuer arrivals. Importing the plane/rendezvous changes work/publication rather than deleting an existing duplicate. |

The locally fetched reference is `origin/main=b8551cc9ef7852d3e1fd76193be08c686c08c178`. Both Rubin files and W4 Mega's producer/register behavior are unchanged relative to the inspected c1ac files; W4 Mega's diff only removes this fork's explicit consumed-K/group transform handoffs. No newer reference-side gather simplification was found.

## Closed-lead check

Reviewed current and both prior CLOSED_LEADS indices, `w4-prefill-next-lead-c1ac.md`, `w4-prefill-followup-after-startup-c1ac.md`, `w4-gather-lifetime-2b8.md`, and `w4-oob-m-zero-fill-reassessment.md`. The older `full-20261029/w4a16-gather-ledger.md` already rejects32-register gather redistribution, runtime live-row grouping, modulo/static-bound rewrites and Rubin-style wider election. Raw TRY/TEST, SF bank remapping, empty-M/partial-K work, output-ring changes and producer tails likewise have explicit boundaries. The active swap coordinate-cache composition is not duplicated here.

**Decision:** preserve the current W4 gather implementation. This is a bounded no-lead finding, not a universal claim that gather cannot improve. A new experiment needs a distinct executed redundancy or critical-path signal beyond these already-tested mechanisms. Exact source hashes, native counts and referenced evidence hashes are in the adjacent JSON receipt.
