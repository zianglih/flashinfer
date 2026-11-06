# Control warpgroup register budget: 112 → 120

Affected geomean: **+0.05%** across 52 cells; decode +0.03%, T256 -0.02%, prefill +0.10%.

- One-line general policy change from c0c0: 120 control / 128 gather / 256 epilogue registers. Candidate kernel `bb11f4d16ee3a4314102f99f076c8e0a0c6b8e8e1d2bcd82e0a05519b4346a64`, patch `2242b18cba4a472e50ed7e976e963edc1715e9284432a3855eda366385373b99`. Control kernel `3225acf2dfeba54df42481b3186267b1bde642da9887b98cb966d5383d8635af` is the c0c0 tree in its immutable 7106-plus-metadata checkout.
- Both arms use the same frozen tactic for every cell. N3U EP/TP MX at 4096/16384 uses the existing native c0c0 winners; all other cells use original frozen winners. These comparisons measure the budget change only, not the gain from retuning. `expected-winners-and-routes.json` and `winner-cache-overlay.json` record the separate provenance in the main and TP-follow-up evidence folders.
- Original-winner affected cells: +0.10% (44 cells). Native-prefill affected cells: -0.18% (8 cells). Unchanged W4A16: +0.36% (8 diagnostic cells, excluded).
- Fresh same-GPU C-A-A-C on replacement C3 `fi-gather-opt-1029`, GPUs0/5, B300, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2. 100 strict CUPTI samples/phase, no event fallback or AUTO, cold-L2 CUDA graphs, unfused, NVFP4 input quantizer included. 60 cells / 24,000 fresh samples. No old-node latency reuse.
- Existing 17 exact cases passed with explicit 120/128/256 guards. Selected wide N3U MX codegen loses 7 LDL / 1 STL sites and STACK8 → 0, while FC2 is unchanged. The 51 MOV.SPILL / 51 R2UR.FILL uniform-to-GPR move sites are unchanged and distinct from the removed local-stack accesses.
- Repeat spread median/max: control 0.09% / 7.42%; candidate 0.08% / 5.12%. These are phase-median repeat spreads, not confidence intervals.

Positive is faster: `100 × (sqrt(C1×C2) / sqrt(A1×A2) − 1)`.

| Model | Backend | 8 | 256 | 4,096 | 16,384 |
|:--|:--|--:|--:|--:|--:|
| N3U EP8 | W4A4 | +0.39% | +0.17% | -0.03% | -0.06% |
| N3U EP8 | PER-TOKEN | +0.11% | -0.03% | -0.07% | -0.09% |
| N3U EP8 | MXFP4x8 | +0.14% | -0.15% | +0.05%† | -0.90%† |
| N3U EP8 | MXFP8 | -0.06% | +0.07% | -0.11%† | -0.21%† |
| N3U EP8 | W4A16* | +0.02% | +0.37% | -0.09% | +4.72% |
| N3U TP8 | MXFP4x8 | -0.01% | +0.04% | -0.05%† | +0.87%† |
| N3U TP8 | MXFP8 | +0.04% | -0.03% | -0.03%† | -1.05%† |
| K3 EP8 | MXFP4x8 | +0.11% | +0.00% | -0.07% | +1.92% |
| V41F EP4 | MXFP4x8 | +0.02% | +0.04% | +0.05% | +0.66% |
| V41F EP4 | MXFP8 | -0.06% | -0.00% | -0.05% | +1.16% |
| V3 TP8 | MXFP4x8 | -0.01% | -0.01% | +0.04% | -0.47% |
| V3 TP8 | MXFP8 | -0.17% | -0.01% | -0.06% | +1.10% |
| V41F TP4 | W4A4 | -0.06% | -0.06% | +0.01% | +0.03% |
| V41F TP4 | PER-TOKEN | -0.00% | -0.28% | -0.06% | +0.06% |
| V41F TP4 | W4A16* | -0.12% | -0.07% | -1.74% | -0.09% |

* Unchanged W4A16 diagnostic. † Frozen native prefill winner used in both arms; all other cells use original winners.

Recommendation: retain the one-line policy for eliminating avoidable local-stack accesses while using the existing 64,512-register pool. This screen is performance-neutral; do not advertise the aggregate as a speedup.

Raw medians/spreads: `report/cells.csv`; raw 100-sample arrays, source/routing/cache/GPU UUID guards, and exact-test receipts: `evidence/`. Source remains a local unstaged candidate unless the parent explicitly retains it.
