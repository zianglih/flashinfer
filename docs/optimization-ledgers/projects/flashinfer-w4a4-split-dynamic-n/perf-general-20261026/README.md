# General policy performance iteration, October 26

Control: `0def601d6603df828ea39679b41ccbce64f7f09e`, including the separate NVFP4 epilogue arithmetic port. Upstream PR7290 remains draft. Canonical and review sources stay clean; experiments use independent source copies with unstaged diffs.

Environment: dedicated `fi-moe-nvfp4-port-1026`, c3/infra, node `hu-wtc-101`, eight B300 GPUs, explicit `nvcr.io/nvidia/pytorch:26.05-py3`. `/data` is persistent Weka storage. Root: `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026`; control source/environment live under `control-0def601d/`. All native compilation caches and source-specific DSL caches stay under this persistent root. Reuse native artifacts only after exact source/header identity checks; keep changed DSL modules isolated.

Use the existing public `benchmarks/bench_moe_deepseek.py` and preserved native result observer. Native AUTO, PDL, ten warmups, 100 cold-L2 CUDA-graph CUPTI samples; NVFP4 includes initial activation quantization, MX uses prequantized inputs. Unfused CuTe finalize, no communication. Models: V3 EP8, V4.1-Flash EP4, Kimi K3 EP8. TRTLLM is the performance target; current control is only the causal experiment comparator. Bounded screens do not replace complete retention grids (`1,2,4,8,16,32,64,128,256,512,4096,8192,16384`, with 1/2 excluded from retention).

Parallel directions under investigation:

- Hoist epilogue normalization and tile scale loads ahead of the accumulator dependency wait, without new policy flags.
- Deeper K16 operand stages through the existing resource planner, beginning with fixed-geometry diagnostics to limit compilation.
- Multiple independent preparation rows per CTA, retaining wide payload copies and the canonical scale layout.
- Remove the redundant per-token gated-epilogue transpose by shuffling rounded token scales into native accumulator ownership, preserving arithmetic order.
- Check whether one warp election per native-MMA stage can replace per-instruction elections; require an actual SASS difference before spending time on timing.

Retained follow-ups: `6a910fea` shares the operand-release ring; `dd266b91` bounds per-token quantization by device live rows and SM capacity. Both are pushed to PR7290. The measured frozen patch is byte-identical to the two commits; `retained-full/commit-receipt.json` binds that identity. Canonical and review sources are advanced; the independent experiment sources remain frozen and unstaged.

## Initial observations

All six five-token native-AUTO controls completed. The matching candidate sweeps are in progress. Early completed NVFP4 rows are nearly neutral for earlier epilogue scale loads and slower for warp-owned preparation rows. These are bounded first screens, not retention evidence. The unchanged W4A16 column is retained as a drift diagnostic.

Source-paired PTX and SASS confirm earlier alpha issue for both phases at narrow and wide route widths in NVFP4 and MXFP8. All sixteen captured kernels remain one CTA/SM with zero local memory/spills. Only MXFP8 T32 FC1 register allocation changes, from78 to75; other resources match. See `../codegen-epilogue-prefetch-20261026/README.md`.

K16 diagnostic results are negative across V41 and V3: larger operand tiles reduce stage count and queued reduction coverage. Do not expand production AUTO from360 to810 on this evidence. The complete fixed-tactic diagnostic lives under `../scheduler-k16-20261026/`.

The prior MMA K-tail screen was already executed and rejected, contrary to an older pending-status note. `../V41_GAP_OPTIMIZATION_2026-10-25.md` and `../evidence/mma-k-tail-r2` contain the corrected result. No redundant rerun is planned.

The single-transpose candidate passed five existing tolerance/graph selectors on GPU0, including per-token GeGLU and two SiTU clamp variants. Its public per-token-only CAAC timing campaign is running. No new upstream test was added.

## Completed bounded screens

All epilogue-prefetch CAAC screens completed at tokens4/32/128/512/4096 with identical routing and source-private caches. Across all three models, per-token decode improves about0.36–0.45%; MX improvements are about0.1–0.4%; standard W4A4 is nearly neutral for V41/K3. This remains a small unretained candidate pending a full-grid decision. Raw source-bound ratios are `results/bounded-paired.json`; unchanged W4A16 is a drift diagnostic.

Rejected candidates: warp-owned preparation (up to3.7% decode loss), K16 operand depth (less queued reduction coverage), MMA-election hoisting (compiler already combines the elections), single-transpose per-token epilogue (CAAC model means0.99951/0.99787/0.99521), SF cache priority (wide results0.9989–1.0013 and a narrow inline-PTX lowering failure), and weight lookahead (0.9070–0.9918 across affected V41 fixed points). No unmeasured candidate is pushed.

Fresh source0def full tables are being validated against TRTLLM. Standard W4A4 V3/V41 now wins all retained points; K3 still has small-mid decode losses. Per-token prefill is the larger gap. The inter-FC quantizer currently processes worst-case allocation rows rather than the device live padded-row count; a separate candidate will pass this already-available routing metadata and keep its initial-input use unchanged. The generic buffer-release ring audit found redundant empty rings for TMA and cp.async scale producers; a separate shared-empty experiment retains their distinct ready barriers and cluster scale join.

The separate quant-load candidate replaces paired128-bit loads with an existing256-bit helper for per-token FP16/BF16 quantization. It aligns storage-offset views before launch and leaves arithmetic unchanged. The fixedCAAC observer reads actual saved tactics and fails on cache misses. An unused historical `FI_K16_EXPECTED_STEPS` environment value remains in this frozen runner; the observer does not read it or constrain Kdepth.

## Full retention sweep: dd266b91

All six public native-AUTO tables (78 token rows,208 derived ratios) passed source, helper, route and histogram checks. Raw outputs and evidence are under `retained-full/`; the PR body uses only this final sweep. Existing scoped tests:82 pass, no failures/skips. Native C++ artifacts remain on Weka with exact-source verification and per-source DSL namespaces.

Compared with fresh0def controls on the same host but different GPU assignments, per-token prefill geometric speedups are1.1562x V3,1.0941x V41,1.2659x K3. Same-GPU component CAAC evidence lives under `../scripts/row_grid_quantizer_20261026`. Matching TRT ratios come from each final public sweep; the initial per-token quantizer is shared by the CuTe and TRT arms. Remaining gaps include V41 per-tokenT8192 (0.9819x), V41MX8T128 (0.9780x), K3W4A4T64 (0.9777x), and K3MXFP4x8T64 (0.9753x). General independent FC2 scheduler AUTO and per-group live-row bounds are still experiments, not retained changes.

## Follow-up candidates after dd266b91

- Independent FC2 scheduler AUTO appends a sixth internal boolean while preserving legacy tactic prefixes. Paired source gates passed64control/128candidate exact replays. Native paired screens select CLC for decode and static scheduling for checked prefill points; full all-format tables are running.
- Per-group row limits use existing routing metadata to avoid quantizing interior padding. Frozen C passed290 exact graph replays and all12pairedCAACcells. Prefill gains0.77–1.45% across all3models. Its only final-composition correction is strict integer host validation.
- Combined candidate `flashinfer-scheduler-row-limits-20261026`: base dd266b91 + patch2b0bd7eaa43af0fbfe6935d3d06f52550c3e916da437172945afbb2b4a4178d1. Combined source-paired replay gate also passes64control/128candidate comparisons. Full public6tables run on GPUs2/4/5; no retention claim until the full data is verified.
- Tail-lane quantization guard: SASS confirms expensive FP4/4over6 work ran before the existing store guard. Moving that guard earlier keeps resources and output bytes identical; no-tail K2048 PTX/SASS is identical. Paired full-chain screens are in progress.
- Producer role-loop factoring removes per-stage role branches but increases static code size; retain only if bounded timings justify that tradeoff.

Seven rejected local source copies were deleted after checking their exact heads/patches and absence of untracked artifacts. `rejected-copy-inventory.json` records the names and source identities; all helper scripts, notes and measured evidence remain. No active source or persistent remote compilation cache was removed.


## Retained follow-ups through 7f4e1703

Pushed three separate commits after scoped pre-commit checks: `b98001fd` independent FC1/FC2 scheduler AUTO; `c69d7034` per-group row limits; `7f4e1703` skip unowned SF-block conversion math. `final-combined/commit-receipt.json` proves whole-tree equality between measured frozen patches and committed sources. Canonical and review checkouts are clean at7f4e1703. Final197 existing cases pass with zero test failures/errors/skips; source hashes remain unchanged. The final six-table refresh is running. It will use new7f4e1703-equivalent NV output and c69d7034-equivalent MX output, with the independently verified unreachable per-token-method difference recorded explicitly.

The completed B+C NV full campaign shows V41 W4A4 decode1.01207x and K3 decode1.00634x versus retainedA, V3neutral0.99886x. These are descriptive native-AUTO same-host sweep changes; paired scheduler screens establish the causal direction. The final guard CAAC improves per-token prefill3.1–3.5% V41 and1.6–2.0% K3 at the measured4096/8192points; decode remains near-neutral. Raw final tables remain authoritative for TRT comparisons.

Producer role-loop factoring is rejected: no repeatable gain and greater static code size. A new independent experiment tests packing FC2 BF16/FP16 output before the existing TMEM transpose, following the MegaMoE ownership pattern. It preserves multiply-before-cast ordering and leaves FC1/bulk output unchanged; it is not retained yet. Parallel V41 mixed-format large-prefill profiling will localize the remaining gap before further policy changes.


## User steering: uniform CLC and simpler execution

The next target is CLC for both phases in every AUTO tactic. Native static/CLC selections at7f4e1703 are now the comparison control, not the intended final policy. All-CLC enumeration reduces720 raw choices to180 without changing geometry/K choices or explicit legacy tactic semantics. The bounded all-format nativeABBA baseline runs from `scripts/all_clc_20261026`, GPUs4/5. Static remains a diagnostic control and existing SM-budget/grid-capacity fallback; no new dtype/model thresholds are introduced.

Simplification itself is now an optimization criterion: retain real redundant-instruction/synchronization removal when correctness holds and timing is neutral. Single-owner CLC metadata publication and packed half-output FC2 transpose are separate general experiments. Their raw gates/codegen and causal timing are kept separate from the final6-table PR evidence.
