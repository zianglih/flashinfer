# Pipeline-polish retention decision

Candidate kernel `b668b2736ea9770e0ca2d45a91f461601953bfaa20f8f807731a641fa20d93d8` over retained `61c2c367`. Only the swap-AB kernel changes (+54/-31); W4A16, APIs, layouts, tactics, ring sizes and transaction counts are unchanged.

## Rationale

- SF prefix: copy only compile-time live four-scale words from SMEM to TMEM. The 31 affected screen cells average +0.115%; the 81 aligned controls average +0.064%. The V41F TP per-token4096 loss of0.5925% is consistently separated and accepted. Three independent-gate variants have uniform spill growth; none exactly matches a timed geometry. Do not claim universal spill reduction.
- CLC terminal: move one terminal publication after the valid-work loop, preserving acquire-before-cancel, padding-ticket draining and final tail. The50 affected cells average +0.086%; N3U EP MXFP4x8 T64 is consistently0.459% slower. Ten to fourteen recurring static instructions are removed; whole-kernel static sites can increase due to the one-time exit block.
- FC2 drain: skip wait_group/read and transpose join when no full TMA slab was issued. Exact/resource qualification passed. Overall timing is neutral; initial large-prefill negative points reversed in same-GPU confirmation, and both sets remain recorded. No outstanding store is allowed to cross the guarded drain.

These are instruction/synchronization simplifications, not a broad end-to-end speedup. The user explicitly values instruction sanity with neutral timing. No new shape/dtype/model branch or tactic axis is added.

## Full refresh

All15 jobs passed,468 cases,936 fresh medians/93,600 CUPTI samples. Compare two fresh candidate passes to the saved source-identical61c2 candidate passes1/2 on matching physical GPUs. Do not use previous campaign controls0/3, and do not call this full refresh a fresh CAAC experiment. Each independent screen was fresh same-GPU CAAC. External controls are reused unchanged.

| Topology | Decode | Middle | Prefill | All displayed scaled cells |
|---|---:|---:|---:|---:|
| EP | +0.056% | +0.067% | -0.022% | +0.038% |
| TP | +0.004% | +0.083% | +0.282% | +0.101% |

Ratios are100×(retained/candidate−1), geometric means. Tokens1/2 and unchanged W4A16 are excluded above. The unchanged W4A16 controls move +0.238%EP/+0.098%TP, illustrating variation at this scale.

Largest full-refresh scaled loss is N3U EP MXFP8 T8192 −2.280%, with a4.46% candidate-pass spread. Preserve also N3U EP MXFP4x8 T8192 −1.620% (both candidate passes slower) and N3U TP MXFP8 T16384 −1.118%. Small prefill costs are accepted; no blanket noise waiver. Fresh same-GPU K3 CAAC confirmations passed: TP per-token T8 +0.0096% and T16 −0.0395%; EP W4A4 T128 +0.0217%; EP per-token T8192 +0.0823%. The separated historical losses did not reproduce. All12 confirmation cells and4,800 raw CUPTI samples remain under `confirm-k3/`; the full-refresh table is not cherry-picked or replaced by these repeats.

## Validation boundary

Combined gate:256 paired exact graph replays/32 GEMM pairs across four scaled formats, static/CLC, PDL off/on, one/two CTA, changing/empty/reactivated routes. Resources and local/uniform spills unchanged in this bounded matrix. Independent SF gate:532 paired replays/152 GEMM pairs, partial K64/K128/K192 and24 aligned PTX identities, with the three spill exceptions above. Scoped hooks passed and all348 canonical working-source hashes still match measured bytes. Sanitizer skipped as requested.

All commands, raw outputs, source manifests, plots and profiler evidence remain within the project ledger. C++ compilation cache remains on persistent cluster storage.
