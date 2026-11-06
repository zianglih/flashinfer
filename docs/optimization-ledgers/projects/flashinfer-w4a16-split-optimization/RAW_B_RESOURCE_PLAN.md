# Unequal raw/SF and B depths — static budget

2026-09-13; source-only planning, no CuTe/CUDA imports, compilation, GPU/remote work or production edits. The top-k candidate remains the first trial. This note does not propose another implementation or infer a speedup.

**Only three fused-finalize geometry families have enough remaining conservative fitter budget for one extra raw/SF slot with all other current depths fixed:** M128/N16, M128/N128, and M256/N32. Ordinary output paths cannot add one this way because the fitter already spends the leftover budget on C stages. Canonical M256/N128 and N192 are not eligible under this rule.

## Source and dependency basis

Current baseline `488ffbd9fe4455c3b4c3030cf668b5603c6698e4` plus the three-line top-k candidate has unchanged fitter/layout formulas. Current tactics: `flashinfer/fused_moe/cute_dsl/tuner.py:974–1017`. Fitter/layout/allocator: `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:190–305,765–800,990–1066,2320–2495`.

The current catalog uses K256, CTA M128, route N8/16/32/64/128/192. M128 covers both cluster C1 and C2 with **one-CTA MMA** and the same per-CTA budget. M256 is two-CTA MMA/C2; N8 is excluded. N192 is available only for M256. The table collapses launch-topology duplicates, not distinct MMA groups.

The layout-size derivation was read from the saved actual DSL4.7.1 helper `../flashinfer-w4a16-megamoe/candidates/w4a16_n256_activation_width/execution/installed-dsl471/blackwell_helpers.py:173–272,915–965,1713–1891`: BF16 output/CTA M128 gives epilogue N=min(route N,32); gated FC1 replaces epilogue M128 with64. `make_smem_layout_epi` tiles this into the staged shared layout. The SM100 capacity map is227KiB, and the TMEM allocator rounds each ACC stage to at least32 columns and then a power of two. These source-derived layout assumptions still need agreement with the actual installed dependency before allocation is treated as observed.

## Arithmetic (bytes, existing conservative SF accounting)

- Capacity `P=227*1024=232448`.
- Raw packed A per stage: `round1024(128*256/2)=16384`.
- SF charge per stage: `round1024(128*(256/16)*2)=4096`. This intentionally preserves the existing **BF16 capacity charge**, not the physical E4M3 element width.
- B per stage: `round1024(2*(N/mma_group)*256)`, where mma_group is1 for M128 and2 for M256.
- Each raw or B pipeline stage has16 barrier bytes; hence **one extra raw/SF stage costs20496** in this budget, and a paired stage costs `20496+B+16`.
- Decoded TMEM stage uses128 columns plus16 shared barrier bytes; there is no decoded-A payload in SMEM. ACC stage columns are max(32,next_power_of_two(N)); ACC depth2 except N192 depth1. This yields D3 at N<=64 and D2 at N>=128.
- Static tile-info charge96; CLC charge32. Table uses static. For applicable FC1 CLC, spare increases64 bytes without changing these depths.
- C bytes per stage: `128*min(N,32)` gated, `256*min(N,32)` ordinary/fused. Fused also reserves `4*min(N,32)` scale bytes and fixes C=1. Other modes start C=2, fit the paired input/decoded rings, then convert every remaining whole C-stage unit into another C stage.
- Each table cell is **raw=B depth / C depth / remaining fitter budget in bytes**. D/ACC depths appear separately. For ordinary FC1 Relu2, use the ordinary column (plus the FC1 CLC adjustment when selected).

| MMA M/N | B bytes/stage | D / ACC depths | Gated FC1 raw=B / C / spare B | Ordinary raw=B / C / spare B | Fused GEMM2 raw=B / C / spare B | +1 raw/SF with fused C fixed? |
| --- | ---: | --- | --- | --- | --- | --- |
| 128/8 | 4096 | 3 / 2 | 9 / 10 / 560 | 9 / 5 / 560 | 9 / 1 / 8720 | No |
| 128/16 | 8192 | 3 / 2 | 7 / 15 / 624 | 7 / 7 / 2672 | 7 / 1 / 27184 | Yes |
| 128/32 | 16384 | 3 / 2 | 6 / 2 / 2704 | 5 / 5 / 6832 | 6 / 1 / 2576 | No |
| 128/64 | 32768 | 3 / 2 | 4 / 4 / 2768 | 4 / 2 / 2768 | 4 / 1 / 10832 | No |
| 128/128 | 65536 | 2 / 2 | 2 / 14 / 2848 | 2 / 7 / 2848 | 2 / 1 / 51872 | Yes |
| 256/16 | 4096 | 3 / 2 | 9 / 5 / 560 | 9 / 2 / 2608 | 9 / 1 / 6640 | No |
| 256/32 | 8192 | 3 / 2 | 7 / 7 / 2672 | 7 / 3 / 6768 | 7 / 1 / 23024 | Yes |
| 256/64 | 16384 | 3 / 2 | 6 / 2 / 2704 | 5 / 5 / 6832 | 6 / 1 / 2576 | No |
| 256/128 | 32768 | 2 / 2 | 4 / 4 / 2784 | 4 / 2 / 2784 | 4 / 1 / 10848 | No |
| 256/192 | 49152 | 2 / 1 | 3 / 5 / 2832 | 3 / 2 / 6928 | 3 / 1 / 14992 | No |

Because ordinary/gated C-stage expansion leaves `spare < C_bytes`, remaining conservative budget is always <8192/<4096 bytes, respectively—less than20496. For the three eligible fused families, budget after one additional raw/SF stage would be6688,31376,2528 bytes respectively. This table only asks about **one** extra stage; it does not recommend filling all nominal capacity.

## What remains open

These are **fitter-accounting residuals**, not queried CUDA dynamic-SMEM allocations. Preserve all1024-byte allocation alignment, actual SharedStorage size/padding, scale layout, C/finalize metadata, and per-ring barrier arrays. The fitter conservatively overcharges SF payload but does not individually itemize every struct/allocation-alignment term; do not silently credit that difference or present this table as an exact physical allocation report. The smallest follow-up, if one of these cases is selected, is to print current `num_load2trans_stage`, `num_trans2mma_stage`, `num_acc_stage`, `num_c_stage`, `cute.size_in_bytes` for A/SF/B/C, `SharedStorage.__sizeof__/__alignof__`, and the compiled dynamic-SMEM byte count from the existing native capture. No new evaluator framework is needed.

The larger unequal-depth idea would have to reclaim output stages or change another resource choice to affect ordinary M256/N128 or N192. That is a different experiment with epilogue-overlap costs; it is not free unused storage. Extra raw depth also adds initialization/drain work and traffic pressure and remains bounded by decoded TMEM/ACC progress. Mega raw6/B3 and the split common-ring stage trials provide reasons to measure cautiously, not evidence of benefit here.

## Observed selected-shape context

The fresh baseline T128 cache `logs/baseline-ep8-fused.t128.autotune.json` selects FC2 tactic `((128,16,256),(2,1),True)` on source `488ffbd9fe4455c3b4c3030cf668b5603c6698e4`. This belongs to the M128/N16 family above: launch cluster C2, one-CTA MMA. Saved NSYS selection `profiles/baseline-t128-ncu-selection.json` records the second grouped GEMM node with 191552 bytes dynamic shared memory, 128 registers/thread, block 512 and grid `(2,1,74)`. This is actual allocation evidence for the **unchanged selected kernel**, not the hypothetical extra raw stage. Neither a changed allocation nor a latency benefit has been compiled or measured; the conservative table and its open layout/alignment checks remain planning evidence.

## Independent state-coupling review

[RAW_B_STATE_REVIEW.md](RAW_B_STATE_REVIEW.md) traces the minimal implementation points. A/raw, decoded A and B already use independent indices/phases, logical K counts and producer tails. No loop or work-publication change is needed: add a B-depth fitter result, construct B with the existing direct layout helper, and bind its two barrier arrays, pipeline and producer/consumer states to that depth. Keep A/SF coupled, conservative SF charging and current C/D/ACC choices. The thin installed combined layout helper can be replaced by its three existing A/A-transform/B helper calls; do not modify the dependency or introduce a new public knob.

The completed top-k repeat selects eligible FC2 families at T8/16/32/64/128/256, six of eleven retention rows. This is a credible later bounded experiment after the smaller release reorder, but capacity alone is insufficient evidence of benefit: extra raw depth does not add decoded or B capacity. The old scale-accounting rejections remain distinct negative context. No unequal-ring source edit or GPU trial has been performed.
