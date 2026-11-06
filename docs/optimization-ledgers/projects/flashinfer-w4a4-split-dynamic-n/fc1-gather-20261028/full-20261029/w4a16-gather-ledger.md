# W4A16 FC1 no-prepare experiments

All changes are local/unstaged. FC2 keeps regular TMA and its four-warpgroup schedule. FC1 adds input gathering as the fifth, last warpgroup. Timing uses fixed existing W4A16 tactics and source-paired C-A-A-C with 10 warmups/100 CUPTI cold-L2 CUDA graph samples, on B300 C3. The initial source is fb66a27e. Native-retune evidence is explicitly separate from implementation comparisons.

| Candidate | Source patch | Status / evidence |
|---|---|---|
| Four-warp staged cp.async, 144/80/96/96/64 | 499ab9e | Rejected: EP prefill−14.38%, TP prefill+5.53%. `w4a16-gather/cpasync-screen.csv` |
| Four-warp direct TMA Gather4, same budgets | 1e6af46c | Preferred: EP prefill+2.91%, TP prefill+19.88%; EP decode−1.48%, TP decode+1.62%. `w4a16-tma-gather/tma-screen.csv` |
| Shared primitive, ancestor publication cleanup, evict-last activation hint | b3617fba | Structural cleanup validated40 existing cases. Cache effect under isolation due K3 EP4096−5.45% vs original TMA. `w4a16-tma-gather/cleanup-screen.csv` |
| Lane-distributed route IDs, 144/80/96/96/64 | 9b79b262 | 40 exact tests passed. Preserved metadata64 control; source-only metadata effect not yet timed independently. |
| Lane IDs +144/80/112/112/32 | 4da51218 | Rejected: EP decode−0.30%, EP prefill−1.39%, TP decode−0.33%, TP prefill−0.65% vs metadata64. 40 exact cases;37 codegen/CFG audits with zero spills. `w4a16-tma-register/register32-screen.csv` |
| Lane IDs +176/80/96/96/32 | dc231d0d | Active: restores universal original epilogue quota, removes FC1/FC2 epilogue register conditional. Compile-only33 cases/CFG passed; exact/performance pending. |
| b361 cleanup with default activation cache hint0 | 7a3cf6bf | Active: one-line cache isolation, same64 gather budget and scalar route IDs. |

W4 native retune on b361 (same implementation, existing tactics only) improves V3 EP8tokens+4.52% and V41F EP8tokens+10.70%; T256−0.69%/−0.60%. Raw medians/tactics in `w4a16-tma-gather/native-retune-screen.csv`.

The linear post-donation SASS register maximum is not a valid role bound: the compiler lays other roles’ cold wait blocks after the gather body. `w4a16-tma-register/cfg_register_remote.py` follows control flow from the gather donation to exits and includes implicit wide-vector endpoints. The32-gather candidate passes all37 relevant compiled cases, despite unreachable R61/R62 in the linear suffix.

Active source copies: `flashinfer-w4a16-tma-gather-review` (frozen b361, shared parent control), `flashinfer-w4a16-tma-epilogue-review`, and `flashinfer-w4a16-tma-cache-review`. The rejected112-decoder local review copy was removed; source manifests/patches and raw evidence remain in the ledger folders. Parent separately owns the one-arrival B-stage experiment.

The rejected W4 cp.async local review clone was removed after both edited files matched its measured source manifest. Durable helper scripts, patches, raw outputs, and immutable remote controls remain.

Both register-redistribution variants are rejected. The176-epilogue EP screen gave−3.28% prefill; no TP run was needed. Cache-default was also not retained: most changes were small, and K3 TP4K's+6.05% had9.71% control-repeat drift. Active source is now `flashinfer-w4a16-tma-clean-review` plus frozen b361 control and the parent-owned one-arrival copy. Clean40 exact tests passed. Its32-cell source screen was interrupted by devbox disappearance; completed jobs must be distinguished from incomplete jobs on recovery. Full104 final harness is prepared but unlaunched.

Methodology clarification: the generic NVFP4-family CLI retains `--include-activation-quant`, but the W4A16 arm consumes BF16 inputs directly and has no activation quantizer. Some inherited helper receipt prose says input quantization is included; the actual commands/source and W4A16 path show that this applies only to quantized activation arms, not W4A16. All W4 comparisons pair the same BF16-input contract.

Clean composition source screen completed32 cells across the original and replacement boxes, without stitching incomplete C-A-A-C sequences across GPU UUIDs: EP decode−0.023%, EP prefill−0.472%, TP decode+0.045%, TP prefill−0.348%. Detailed medians/repeat spreads are in `w4a16-tma-clean/screen.csv`. Final activation pointer annotation was lowered32→16 to preserve the old prepare input alignment contract; final patch26bce62f passed40 existing exact cases. Offset-view exact checks and full104 final-source/native-tactic comparison are next.

Full104 final26bce+native-existing-tactics versus fb66+old-winners completed: EP decode+0.32%, prefill+0.54%; TP decode+2.84%, prefill+17.30%, excluding1/2. Allsource/route/tactic/CUPTI/sample-count guards passed. Source+retune evidence is `w4a16-full/cells.csv`; native timing is `native-search.csv`. Six16-byte-offset exact cases also passed. Active additional experiment: `flashinfer-w4a16-tma-warpindex-review`, replacing warp_idx−16 with warp_idx%4 to expose an exact within-WG range to the compiler. Final26bce remains frozen.

W4 retained in475cae6b. Frozen b361 and final26bce local source copies retired after exact manifest verification; raw evidence and remote controls remain. Rejected modulo workspace bumped to475cae6b and renamed `flashinfer-w4a16-tma-staticbounds-review`, whose only unstaged diff is the current compile-time full-task-group proof. Modulo screen completed20cells before rejection: EP decode−0.02%, middle+0.06%, prefill−1.03%; V3TP decode−0.28%, middle−0.04%, prefill−0.46%. Static proof is codegen-first; no retention claim.

Static full-group proof also rejected from codegen (+64–65 instructions, moreR2UR); no redundant runtime/perf campaign. Its local source copy is removed. No W4 experiment source copy remains; next work is readonly K3EP4K/8K CUPTI kernel breakdown against retained475-equivalent source.

## 2026-10-29 K3 EP prefill clock-state audit

Read-only CUPTI stage decomposition and separate NVML sampling show substantial late-sample drift shared by routing/FC1/FC2/combine. Fresh normal fixed-tactic CAAC produced4K+1.68% with7.72% control spread,8K−4.42% with9.56% control spread. This differs from the full104 headline gaps and cautions against treating those exact percentages as deterministic source overhead.

`w4a16-k3-clock-profile` repeats identical kernels/tactics/routes with read-only2ms NVML.4K medianC535.154/A543.7775µs;8K C997.843/A1006.755. Later quartiles slow10–17% in both sources. Memory3996MHz and clock-event mask0 throughout; SMclock transitions2032→1980(C8K) and2032→1567(A8K), but4K reports2032 throughout. NVML values update coarsely, so DVFS is observed but not a complete causal explanation. No clock/power settings changed; polling is diagnostic only. Raw, guarded evidence and exact aggregate commands remain in the experiment folder. Next decisions should separate source differences from measurement-state effects; don't retain an instruction variant based on noise.

### Fixed-clock K3 diagnostic, not public benchmark data

Parent approved a bounded1500MHz SM-clock experiment on exclusiveGPU6 to separateDVFS from source cost. Supported1500MHz selected below observed1567MHz droop; memory3996 unchanged; no power-limit changes. Identical-source/tactic/route CAAC nowstable:4K C612.9625/A635.394/A635.6325/C610.978µs =−3.70%, spreads0.325/0.038%;8K C1073.0915/A1092.9475/A1095.043/C1072.404 =−1.94%, spreads0.064/0.192%. NVMLtiming samples all1500MHz,reason0. FC1~366→405µs4K/~662→714µs8K, removedprepare20.8/39.0µs;FC2/combine unchanged. Residual optimization target is FC1 itself, not downstreamPDL contention. Larger stock-clock differences contain substantial state variation.

AutomaticGPUclocks restored in finally and verified idle120MHz/0MiB/default2032/memory3996; no otherGPU touched. Firstwrapperattempt failed beforebenchmark dueinterpreterargv/runpy composition, also restored successfully; correctedsecondattempt completed4phases. Evidence `w4a16-k3-fixed-clock/` is diagnostic-only and must not enter stock-clock tables.

## W4 runtime live-group Gather4 rejected

Retained475 versus isolatedcc1c9c83: cached laneIDs outsideK, runtime rowgroup loop outside staticK64 chunks (broadcasts reusedacrossK), exactdynamic4arrival transactionbytes.40exact and33gate+10fullshape cubins no localstorage/spills. Statics shrink5–10%, but10cell stock-clockCAAC loses stableprefill V3EP−10.30%,V3TP−7.71%,N3UEP−5.37%,N3UTP−5.43%; decode roughlyneutral. K3−4.06/−9.65% has appreciabledrift, not neededforrejection. Allraw4000samples/NVML/CUPTIstage data in`w4a16-live-groups/evidence`, source/summary inRESULTS.md. No fixedclockrepeat orfullmatrix warranted; sourcecopyretired afterhashverification.

Follow-on predicated-TMA idea was audited and notimplemented: earlier`live-predicate/RESULTS.md` alreadytested inlinePTX`@issue`, which ptxas loweredto extra branches aroundunpredicatedUTMALDG (N3UW4A4live1127632/182→7696/198). DirectW4completion doesnot changeinstructionlowering; donotreintroduceunusedhelperpredicate. PTXlegality isnot guaranteeofSASS predication. Next auditis Rubin-style electedissuerscope, keeping allcoordinate shuffles outsideelection andstaticgatherunroll.

## W4 wider elected-issuer scope rejected at codegen

Isolated patch `f48bcffb` on retained475 moves election around the static B-stage issue batch, keeping route shuffles and all pipeline operations unchanged. After resolving CuTe staged-view/name dominance, all three representative FC1 captures succeed without spills. K3 N128: 2008→2012 instructions,182→183 branches; K3 N192:2054→2058,185→186; V3 TP N16:1673→1677,199→200. R2UR/SHFL unchanged. This provides no instruction benefit, so no exact/performance run or publication change. Full evidence and the native-cache timeout/IR diagnostics are preserved in `w4a16-elected-issue/`; the inactive review copy is retired after source verification.
