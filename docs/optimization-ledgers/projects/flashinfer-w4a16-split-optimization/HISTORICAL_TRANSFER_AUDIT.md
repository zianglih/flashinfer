# Historical transfer audit — split CuTe DSL W4A16

Read-only source/history audit, 2026-09-13. Current split checkout: `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`. No production edit, import, compilation, GPU run, or saved-result recomputation was performed. Historical timings below belong to their original complete runs, not this checkout or a prediction of current benefit.

Source abbreviations:
- **Split kernel:** `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py` in this project's `flashinfer/` clone.
- **Split history:** `/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md`.
- **Mega kernel:** `/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/megamoe_kernel.py`.
- **Mega history:** `/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md`.

## Ranked candidates

### 1. Release the raw/SF slot after the final TMEM store issue, before its completion fence

**Best narrow transfer; correctness/native precedent is stronger than its timing evidence.** Split `_transform_tile` lines 534–548 currently issues register-to-TMEM stores, fences their completion, releases raw input, then publishes decoded readiness. Mega kernel lines 95–110 releases raw input before that fence. Its Entry078 native evidence explicitly shows final STTM → raw release (no scoreboard wait) → TMEM completion fence → decoded arrival (waits for the fence). Stage counts, participants, instruction count and spills remained unchanged.

This is narrower than the rejected split release-before-store experiment (Split history 5442–5485, and earlier 1388): that prototype released input **before** the R→TMEM collective. It regressed the complete EP8 sweep (0.9923x) and was restored. Moving release only between store issue and completion preserves the current register-fed issue ordering and shortens only the independent raw-storage lifetime. Do not describe generic early raw release as untried.

A direct TMEM-only ordering change should suffice in the split implementation; preserve its SMEM-transform branch, both decoder groups, final raw loads, decoded-ready fence, pipeline phases and tails. No hook framework or public knob is necessary. Native admission must establish that the release actually precedes the fence without an implicit dependency, and that decoded readiness remains behind the fence. Numerical coverage must include both GEMMs, one/multiple K tiles, C1/C2 and partial routes/features.

Mega Entry078 (history 6178–6264) measured −0.424211% latency GM over 8–4096 versus its immediate complete control, 6/10 lower; versus a separate historical best it was +1.532273%. It was retained for a real independent lifetime and marginal mixed evidence, **not** a robust speedup. This is a defensible small experiment, not a promised gain.

### 2. Fit the raw/SF and BF16 activation rings independently

**Structurally new in this bounded split-history scan; larger and lower-confidence than #1.** Split already has separate A/SF and B pipelines/owners, so there is no missing logical operand overlap. However, one `num_load2trans_stage` controls both physical layouts, both barrier arrays (kernel 765–784), the activation state (1393) and weight state (1458). The fitter charges one combined A + SF + B stage and selects one common depth (2420–2470).

Mega keeps raw/SF together but rebuilds the B layout with its own depth (Mega kernel 325–342), gives each ring its own barriers (348–365), and fits actual aligned storage (368–404). This permits, for example, deeper compact raw/SF lookahead while retaining fewer large BF16 B tiles. It transfers a storage-allocation mechanism; it does not transfer transport counters, scheduling policy, or communication waits.

The first useful step is a static resource table over the current split tactics: hold ACC/decoded counts, output buffers, tile-info depth and current B depth fixed, then determine whether spare capacity admits an extra raw/SF slot. Only a concrete changed allocation warrants a device trial. Preserve actual split alignment (currently 1024 bytes), physical scale layout, barrier storage, C-stage/fused-finalize carveouts and capacity limits; do not copy Mega's 128-byte allocator assumptions or its fixed 5/3 preference. No expanded public tactic grid is needed for a bounded candidate.

Costs are extra raw barriers/init/drain plus possible load pressure and register-state changes; more raw lookahead cannot bypass the decoded-TMEM ring or a stalled epilogue. Mega raw6/B3 was rejected (+2.169545% latency GM, Entry081 6433–6490); split's common GEMM2 ring cap 3→2 was neutral/rejected (5216–5239). Those trials discourage blindly increasing depth, but neither tested unequal raw/B depths in the current split fitter. The retained split A+SF barrier merge (1000–1047) must remain: separating SF again would undo a measured synchronization reduction.

## Transfers already present or explicitly closed

| Apparent opportunity | Current source / exact historical disposition |
| --- | --- |
| Load alpha before accumulator wait | Already split kernel 1886 before 1933. Staging alpha with metadata was separately rejected, history 4979. |
| Release ACC after its last TMEM load | Already 1961 / 2124; retained history 1950–1988. |
| Start weight/decode before activations | Already independent; only activation producer performs PDL wait, 1396–1397. GEMM2 CLC was tested and rejected, history 4099–4126. |
| Restrict TMEM allocation wait to consuming roles | Two runnable forms and one lowering failure were explored, history 1311–1346; gains too small/mixed. Post-merge revisit 1667 also exists. |
| E4M3 physical byte accounting instead of BF16 capacity charge | Exact concern is known: history 669–680 and **post-A/SF-merge 1567–1585**. Both restored conservative accounting after no repeatable gain; this is not a novel optimization. |
| Extra activation producer probe / dual MMA operand probes | Rejected history 1927–1949, 1989–2020 and GEMM2 revisit 5308–5355. Source's blocking B wait is intentional. |
| Later decoded-slot acquire; fragment lookahead; wider TMEM stores | Rejected history 5486, 5511, 5168. Current split already uses two transform WGs and x8 stores. |
| One-wave grid right-sizing | Tested using existing scheduler API; full A/B/A overall 1.000233x, rejected, history 5705 onward. |
| Mega's non-power-of-two linear work decoder fix | Split uses CUTLASS persistent/CLC mapping rather than Mega's owned expert-phase decoder; no source-equivalent direct transfer established. |
| Mega transport barrier/return/tail optimizations | Not split pipeline semantics. No proposed transplant. |

## Follow-up: top-k constexpr specialization is the smallest first candidate

Integration independently proposed and root authorized the top-k change. A bounded read-only review of the resulting three production-line changes passes: `moe_w4a16_kernel.py:573` marks top_k Constexpr; `moe_w4a16.py:140` keys the compiled variant by it; the compile call still passes it (188), while the runtime call omits it (339–355). The wrapper's fused-finalize scale-table extent (622) is then static, and the existing kernel derives its divisor from that extent (2146, 2161–2162, 2210). This is genuinely different from blindly copying Mega's linear scheduler fast-divide helper: it restores an already-known launch value to compile-time tensor metadata. Dynamic m/n/k and actual token count remain unchanged. The non-fused top_k=0 path excludes the scale tensor/divisions at compile time.

The existing six-geometry route-boundary test now uses top_k2/3 × fused-finalizeFalse/True with its unchanged numerical oracle. No GPU execution or native division-elimination claim is made here. This very small specialization ranks **ahead of the two pipeline candidates** on implementation size and confidence; #1 remains the closest validated native pipeline transfer and #2 a larger resource-allocation hypothesis. No candidate has a demonstrated speedup on the new checkout yet.
