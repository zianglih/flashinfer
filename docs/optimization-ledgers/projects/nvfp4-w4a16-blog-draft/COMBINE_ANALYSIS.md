# Deterministic combine, warp reuse, and vector-width evidence

Read-only audit on 2026-10-05. No new GPU experiments. Repository source below was inspected at the **measured FlashInfer revision `44a04fd247cf2f93bee4052bf439bc93f32c7f8c`**, available in `/Users/ziangli/playground/projects/flashinfer-pr5019-merge-sync-20260921/flashinfer`.

## Conclusions for the article

- W4A16 has **20 warps / 640 threads per CTA**. W4A4 has **12 warps** with epilogue or reused-dispatch return, and **16** with the optional dedicated token-return warp group. Do not call every W4A4 tactic a 12-warp kernel.
- W4A16 reuses **16 retired warps / 512 threads** for ordered deterministic final combine, while the remaining four dispatch warps finish cleanup. This reuse leaves compute-role counts and register budgets intact; it does not add another worker group or imply equal occupancy to a standalone reducer.
- This deterministic combine is already inside the persistent kernel at the exact revision used by #5019. `in_kernel_fc2_reduce=False` disables the separate BF16 atomic route-accumulation option; it does **not** disable the ordered persistent-tail combine. Frontend code supplies the final output tensor on this false branch. The W4A4 implementation instead launches a separate `TopkReduce` by default when its atomic option and deferred-reduction option are both off.
- The persistent kernel keeps its compute-phase resource reservation into the tail. Its fixed worker pool therefore cannot be equated with a standalone combine's independently sized grid/residency. Vectorized loads, packed FP32 arithmetic, and amortized indexing matter because there are fewer freely schedulable combine workers.
- Retained W4A16 uses 128-bit route loads/stores and paired FP32 multiply/FMA, eight BF16 output elements per worker. This audit confirms emitted LDG.128/STG.128 and retained source. It does not recover a clean scalar-versus-vector combine timing ablation; avoid assigning an isolated numerical speedup to LDG.128.
- A true LDG.256/STG.256 combine experiment initially spilled **combine-tail state/payload**, not the repeated MMA/TMA/weight-decode loops. Later variants removed the spills but still failed to improve focused end-to-end timing. Say both facts; do not claim the completed performance regressions were caused entirely by spilling.

## Pinned public source anchors

All links below refer to the actual historical measured revision, not current main.

- [W4A16 640-thread geometry and role setup](https://github.com/flashinfer-ai/flashinfer/blob/44a04fd247cf2f93bee4052bf439bc93f32c7f8c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L224-L277).
- [W4A16 combine worker count and warp-group striping](https://github.com/flashinfer-ai/flashinfer/blob/44a04fd247cf2f93bee4052bf439bc93f32c7f8c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1007-L1030): workers per CTA = 640 minus 128 dispatch threads.
- [W4A16 deterministic tail and cleanup branches](https://github.com/flashinfer-ai/flashinfer/blob/44a04fd247cf2f93bee4052bf439bc93f32c7f8c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1536-L1587): warps 0–7 and 12–19 reduce; dispatch warps 8–11 clean up.
- [W4A16 public frontend supplies final output when atomic reduction is off](https://github.com/flashinfer-ai/flashinfer/blob/44a04fd247cf2f93bee4052bf439bc93f32c7f8c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py#L889-L910).
- [Retained 128-bit reducer and packed FP32 arithmetic](https://github.com/flashinfer-ai/flashinfer/blob/44a04fd247cf2f93bee4052bf439bc93f32c7f8c/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/topk_reduce.py#L70-L119).
- [W4A4 epilogue warps 0–3](https://github.com/flashinfer-ai/flashinfer/blob/44a04fd247cf2f93bee4052bf439bc93f32c7f8c/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/kernel_fc12.py#L161).
- [W4A4 12/16-warp geometry](https://github.com/flashinfer-ai/flashinfer/blob/44a04fd247cf2f93bee4052bf439bc93f32c7f8c/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/megamoe_kernel.py#L294-L314).
- [W4A4 separate TopkReduce launcher](https://github.com/flashinfer-ai/flashinfer/blob/44a04fd247cf2f93bee4052bf439bc93f32c7f8c/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/megamoe_kernel.py#L1527-L1552).
- [Standalone reducer's 128-thread CTA](https://github.com/flashinfer-ai/flashinfer/blob/44a04fd247cf2f93bee4052bf439bc93f32c7f8c/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/topk_reduce.py#L150-L159) and [worker-sized grid](https://github.com/flashinfer-ai/flashinfer/blob/44a04fd247cf2f93bee4052bf439bc93f32c7f8c/flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/moe_nvfp4_swapab/topk_reduce.py#L270-L277).

## 256-bit experiment: exact evidence

Primary local ledger root:

`/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/alignment256-20260926/`

This is internal HashInfer experiment evidence associated with HashInfer PR13 [private repository link omitted], not a public FlashInfer benchmark publication. The local ledgers carry the detailed failed/unretained trials; the PR link should not be presented as hosting all of those raw results.

Initial baseline `cd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7`; payload candidate `e5d91761f8c8a8ab78bf75428006327d1b35e864`.

- Fixed diagnostic: **B300 SM103a, EP4, H6144/I2048/E256/top-k8, uniform global T128**, tactic N64/G1024/epilogue, four ranks.
- Normalized per 16 BF16 output values, route/output instructions change **16 LDG.128 + 2 STG.128 → 8 LDG.256 + 1 STG.256**. Payload bytes and ordered per-element arithmetic are unchanged.
- Initial candidate: **REG96, STACK40, 10 static LDL-family sites and 17 STL-family sites**. PTX had no explicit local accesses; the assembler generated the spills.
- Spill state includes combine worker/token/tile/address/score/payload state across role retirement. No local-memory sites occur inside repeated per-K MMA, scheduler, TMA, or transform loops. At this fixture only WG3 CTAs 0–95 execute the width-16 payload; WG3 already had 96 registers. Restoring only WG1's budget therefore did not fix it.
- Late preparation plus tail register restoration removes spills; late preparation plus scalar score loads also removes them without changing budgets. These are separate candidates, not the initial spilled binary.

Source locations:

- `EXPERIMENTS.md:29-49`: original candidate identity and first fixed diagnostic.
- `DIAGNOSTIC_SPILL_LEDGER.md:1-27`: source-bound fixture and normalized instruction/resource table.
- `DIAGNOSTIC_SPILL_LEDGER.md:29-58`: exact active-worker mapping, static spill-site interpretation, and non-spilling repeated compute loops.
- `FINAL_DECISION.md:41-45`: scope of initial spills and later spill-free refinements.

### Completed focused timing

**B300 EP4 H6144/I2048/E256/top-k8, uniform routing**, T128/4096/8192/16384, eight fresh AUTO candidates per sweep. 3 warmups + 100 cold-L2 CUDA-graph CUPTI samples per sweep; pooled 200 untrimmed rank-MAX samples per source/shape. Balanced A1/B1/C1/D1/D2/C2/B2/A2 order. Public forward includes staging and MegaMoE; JIT/tuning excluded.

- A: original128 `cd7cc07`.
- B: wide payload + late state + scalar scores `679aa752f9292d5cbfe4f129c076e347089b58f2`.
- C: wide payload + late state + participant-only 96-register tail `f8c97bb6eb9026ec6af87c825a5bd99c157a1d52`.
- D: native256 scores + original128 payload `adadbd6b63fa43c4e5a305ccc08fa1f103ee15f6`.

| Global tokens | Original128 µs | B µs | C µs | D µs |
|---:|---:|---:|---:|---:|
| 128 | 282.5140 | 283.9380 | 283.2345 | 284.3075 |
| 4096 | 594.0070 | 596.3880 | 595.2690 | 597.1895 |
| 8192 | 1141.3510 | 1146.7760 | 1148.5705 | 1143.3855 |
| 16384 | 2346.0065 | 2352.4935 | 2364.4450 | 2368.0710 |

All 128 selected winner exports (32 baseline, 96 candidates) were spill-free. All 12 pooled candidate/shape ratios were below one. These small differences justify retaining the original implementation; they do not prove every 256-bit design is slower or attribute all variation to source changes. AUTO changes and drift are recorded. Broad all-tactic, trace-enabled, and SM100a qualification were not completed because the candidates failed retention.

Evidence: `FINAL_DECISION.md:13-26` (methods, identities, table, audit); `FINAL_DECISION.md:3-9` (retention); `FINAL_DECISION.md:53` (image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe4.8.0).

## Earlier concurrency ledger

`/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/integrated-topk-20260918/VECTOR_ILP_RESEARCH.md:33-46` explicitly distinguishes the 512 retired-thread reducer from standalone 128-thread CTA grid/residency and records existing 128-bit accesses/packed arithmetic.

`.../integrated-topk-20260918/EXPERIMENTS.md:3-15,33-50,121-138,168-201` records dispatch-only, decode-two-group, all-five-group, and selected-four-group experiments. The selected four groups reuse epilogue/control/decode while dispatch cleans up. Early gains were small and sensitive to serial drift; these are architecture history, not another headline speedup.

Do not confuse the September19 **input staging** 256-bit trial (spill-free yet unpromoted) with this September26 **combine payload** trial (initially spilling, then spill-free refinements unpromoted).

## Suggested blog paragraph

The extra workers also stay useful after the matrix multiplications finish. W4A16 launches 20 warps, compared with 12 or 16 in the W4A4 design depending on the token-return tactic. We reuse 16 of those retired warps for the final ordered combine while dispatch finishes cleanup, preserving the compute-phase allocation. But a persistent kernel's fixed worker pool is still more constrained than a standalone combine kernel, so instruction efficiency matters: the retained path uses 128-bit loads and packed FP32 arithmetic. We also tried Blackwell's 256-bit accesses. The first version reduced load instructions but spilled combine state; even after removing those spills, the tested refinements did not improve end-to-end timing. The 128-bit path stayed.
