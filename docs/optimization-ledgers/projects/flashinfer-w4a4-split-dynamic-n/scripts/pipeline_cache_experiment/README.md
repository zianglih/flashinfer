# Pipeline, cache, and PDL experiments

Production checkpoint: `7829fc00dc7121341cc40cd4190660507e006490`.
These are isolated diagnostic experiments, not retained full-MoE results. No production source changes are included.

## Controls

- Native DeepSeek inputs and routing from `benchmarks/bench_moe_deepseek.py`: hidden 7168, intermediate 2048, top-k 8, 32 local experts.
- Native phase arguments and returned output/scale buffers are captured from the full pipeline. FC1 returns allocated buffers when its `out` arguments are `None`; the diagnostic reuses those returned buffers for both arms.
- Exact output and output-scale bytes are checked against the frozen implementation before every timed variant.
- 10 warmups, 100 samples, cold-L2 CUDA graph CUPTI median. Isolated phase times are diagnostic and are not added to claim end-to-end speedups.
- `probe_chain.py` measures the complete native route/sort/FC1/FC2/combine chain with a fixed tactic. It is still diagnostic, not AUTO primary retention evidence.
- GPU1 and GPU4, c1 `fi-w4a4-dyn-n-1024`, NVIDIA B200, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.7.1. No shared native JIT cache clearing.

## Source-traced hypotheses

1. Revisit operand stage counts because the retained overlap and bulk epilogue changed shared-memory pressure. The old phase-only selection is not automatically optimal for actual native routing.
2. Test weight A EVICT_FIRST and activation B EVICT_LAST separately. W4A16 retained these hints, but the new blockscaled workload has different reuse and traffic. Scale hints remain unchanged because the W4A16 ledger rejected those.
3. Test TMA descriptor prefetch, used by existing W4A16 and SM100 NVFP4 MegaMoE. This is descriptor prefetch, not an extra data staging pipeline.
4. Signal PDL dependents after the existing dependency wait and before the tile loop. Earlier signaling would violate the standalone finalizer requirement that routing metadata be ready before its pre-wait loads. No operand reads move before the dependency wait.

Prior W4A16 evidence: `/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md`, especially lines 295-337 (PDL/activation-cache), 555-572 (rejected early launch variants), 681-729 (scale-stage depth), 1000-1096 (merged barrier and weight-cache policy). Prior SF scratch experiments are excluded; no new mechanism justifies replaying them.

## Initial screen

NVFP4, T16384, two-CTA M256/N256. All exact checks passed.

| Variant | FC1 us | FC2 us |
|---|---:|---:|
| stages5 control, GPU1 | 328.464 | 180.800 |
| stages2 | 499.153 | 243.905 |
| stages3 | 376.448 | 206.369 |
| stages4 | 320.192 | 185.985 |
| cache control, GPU4 | 324.769 | 181.121 |
| weight A EVICT_FIRST | 329.457 | 188.273 |
| activation B EVICT_LAST | 328.593 | 180.161 |
| both hints | 332.209 | 186.497 |
| descriptor prefetch | 325.441 | 181.216 |
| both hints + descriptor prefetch | 332.833 | 186.673 |

Stages6 exceeds the computed shared-memory capacity for this geometry and was not launched. Stage4 FC1 remains only a candidate pending reverse measurement. Cache hints and descriptor prefetch do not show a large-token benefit here. Initial `-01` stage/cache runs stopped before variant execution because the diagnostic incorrectly read a `None` FC1 output argument; corrected `-02` runs use the returned allocations. No existing baseline data is affected.

## Selected policy for composition (not full-MoE retained)

The minimal candidate changes only one-CTA N128 FC2 from 4 to 5 operand stages. It leaves all FC1 and other geometries unchanged. `pipeline_trial/selected_core.py` is a frozen complete module for reproducibility; its only functional difference from the frozen control is that constructor line.

- NVFP4 reverse: T4 18.048→17.504us; T128 55.680→54.656us; T1024 60.352→58.736us; T16384 182.128→175.952us.
- Mixed W4A8 T16384: first 270.416→246.496us; reverse 268.593→243.424us.
- MXFP8 T16384: first 290.481→267.569us; reverse 286.529→260.929us.
- 24 existing task-local paired cases passed: six input formats, per-token on/off, K384 FP4 tails, M384 channel tails, route tails and untouched-output sentinels. Half the cases exercise the changed N128 one-CTA geometry; half protect unchanged N256 two-CTA behavior.
- Five stages adds operand lookahead while preserving the 64-token, two-stage bulk epilogue. Six stages forces the existing shared-memory fit policy down to its 32-token, single-stage epilogue, explaining its weaker large-token result.

## PDL and wider-K boundaries

Early PDL after dependency wait is unselected: full native fixed-tactic chain T128 165.2805→164.6565us, T16384 618.322→622.098us. Final outputs are byte-identical. Internal routed-buffer padding is unspecified and some intermediates can be reused by downstream phases, so full-chain checks compare final output; isolated phase checks compare complete reused output/SF allocations. The first two chain attempts incorrectly compared unspecified internal bytes and were stopped at the control check. Those are harness failures, not numerical kernel failures.

Eight native MMA steps per stage are isolated in `widek{2,3,4}_core.py`. FP4 uses K512 and FP8/mixed uses K256. The task-local layout inspector verifies that the widened B layout consists of two 128-byte row chunks: each chunk has the ordinary row stride and the second starts after the first full row block. Gather4 keeps its 128-byte descriptor and issues both chunks; each 128-row SF allocation doubles to 32 TMEM columns. No activation or scale arithmetic changes.

- NVFP4 two-CTA N256, two wide stages: FC1 325.409→353.441us, FC2 181.312→196.833us; rejected at that geometry. Three wide stages exceed shared-memory capacity there.
- MXFP8 two-CTA N256: FC1 control 445.330us, wide2 512.385us, wide3 439.666us; FC2 control 256.672us, wide2 288.737us, wide3 263.233us. The small FC1 difference does not justify selecting a universal wide-K policy.
- NVFP4 two-CTA N128: FC1 control 334.369us, ordinary stages6/7 342.465/349.345us, wide3 322.705us, wide4 344.609us. The wide3 case needs reverse/native-size follow-up.
- Wide3 N128 passed 50 bitwise pairs versus the frozen kernel: K64/384/512/768/1024 × validN1/17/129/255/257 × per-token on/off, with multiple persistent work tiles. This preserves the legacy arithmetic exactly; auxiliary PyTorch comparisons in the reused probe have the same tiny rounding differences as the control.

All medians, raw samples, failed attempt logs, source snapshots, source hashes and exact-case logs are retained in this folder. `RESULTS.md` is generated from the raw JSON files; `manifest.json` indexes sources and evidence. No production file was modified by this task.

## Final composition handoff

`integration.patch` applies cleanly to production7829 and only changes the shared Blackwell core. `integration_core.py` is the complete production-import version (SHA256 `29f4c0b23411f91299940c9aa6d128221b8dbaeb0a1d27ffb5fb8db5e79e3c59`). It combines:

1. FC1 M256/N128: eight native K steps, three operand stages, two128-byte Gather4 chunks per stage, doubled SF TMEM reservation. Other geometries retain four steps.
2. FC2 M128/N128: five operand stages, preserving the existing64-token double-buffer bulk epilogue. Other geometry and FC1 stage policy stay unchanged.

The exact-tested frozen module is `pipeline_trial/composed_core.py`, SHA256 `eb75bd7feafaaab6365e87039432a589acd5d617f856a62ee420fb8ece9b1a46`. The integration file differs only in production import naming, corrected comments, and equivalent explicit branching for readability.

Reverse FC1 native medians for the selected M256/N128 geometry:

| Mode | Tokens | Control us | Candidate us |
|---|---:|---:|---:|
| NVFP4 | 4 | 38.1120 | 37.2480 |
| NVFP4 | 128 | 99.6645 | 96.2560 |
| NVFP4 | 1024 | 103.1680 | 99.5840 |
| NVFP4 | 8192 | 192.7525 | 185.2160 |
| NVFP4 | 16384 | 338.2725 | 329.1200 |
| MXFP8 | 128 | 169.5360 | 159.3600 |
| MXFP8 | 1024 | 177.1210 | 167.4560 |
| MXFP8 | 16384 | 591.6805 | 508.4645 |
| Mixed W4A8 | 128 | 134.0480 | 128.1925 |
| Mixed W4A8 | 1024 | 136.8005 | 130.5765 |
| Mixed W4A8 | 16384 | 537.3930 | 512.4980 |

The composed FC1 implementation passed48 paired bitwise cases over all six input formats: short-K and K384, quantized FP4/FP8 output and output scales, per-token BF16 output, the changed N128 and unchanged N256 geometry. Together with the50 NVFP4 boundary/persistent cases and24 FC2 format cases, this provides focused exact evidence. These are task-local diagnostics, not new production tests, exhaustive correctness, sanitizer, or full-AUTO retention claims.

NCU actual-routing NVFP4 T16384 M256/N128 (control vs composed):94 registers/thread for both,96 allocated,1024-byte stack metadata for both, zero local-memory load and store sectors. Dynamic shared memory increases144384→172928bytes; shared-memory occupancy remains one CTA per SM. Raw CSV and `.ncu-rep` are preserved in `results/pipeline-composed-nvfp4-n128-ncu-01*`.

Weight-A EVICT_LAST counter-control is also neutral at native T16384 M256/N256: FC1 control324.785/FIRST329.504/LAST324.225us; FC2 control181.249/FIRST188.209/LAST180.721us. It is not selected. Small T128 full-chain cache hints improve at most0.6%, and descriptor prefetch is unchanged; neither is selected.

All GPU jobs in this experiment batch completed before the handoff. Root owns production composition and full-pipeline retention decisions.
