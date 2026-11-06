# Halfguard v2 compared with the complete C1 sweep

Fixed-to-fixed uses identical requested and all 104 actual configurations, gates and compiled geometry; only the epilogue source changes. This is sequential, unrepeated evidence, not an isolated randomized timing trial.
Nine of thirteen automatic choices change; their cross-run differences combine the epilogue change and online host-timer selection. Online host rankings are not CUPTI rankings.
The fixed series shows no broad gain or clear full-tile regression: tokens 4 through 4096 are between -3.06% and +2.12%. Tokens 1/2 improve but their split baselines also move substantially.
Unchanged auto choices at 256/512/1024/4096 change +2.08/+0.12/+0.25/-0.75%. These single observations do not establish a useful general improvement.
Global 4096 is not a guarantee that every expert tile is full. No captured branch-frequency data justifies labeling it a pure full-tile control.
Keep v2 unpromoted while preserving its functional/codegen evidence. A branch-first constexpr helper is a separate implementation to evaluate, not a row substitute.

Both complete sweeps pass the unchanged analyzer again. Each has 52 raw rows, 208 split selections, 208 compiled records and 104 returned auto winners; all 13 online rankings contain exactly 16 candidates. Full 1572-source manifests differ only in the epilogue; 337 required paths, image/node, compiler/runtime metadata and frozen timing helpers agree. All 104 fixed actual configs/compiled records/gates are identical. All raw values remain in the original full13 tables; no row substitution.

Negative change means v2 is faster. Split retunes independently; its movement is context, not a confidence interval.

| Global T | C1 fixed Mega | v2 fixed Mega | Change | Fixed split change | C1 auto Mega | v2 auto Mega | Change | Auto split change | Same auto choice |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 0.106224 | 0.097936 | -7.80% | +11.83% | 0.078849 | 0.102640 | +30.17% | +27.70% | no |
| 2 | 0.121569 | 0.114913 | -5.48% | +27.99% | 0.111169 | 0.111473 | +0.27% | -0.40% | no |
| 4 | 0.135649 | 0.136545 | +0.66% | -11.43% | 0.117873 | 0.116625 | -1.06% | +7.76% | no |
| 8 | 0.154481 | 0.156033 | +1.00% | +4.38% | 0.156593 | 0.168450 | +7.57% | +0.08% | no |
| 16 | 0.176593 | 0.179233 | +1.49% | +1.17% | 0.168001 | 0.176801 | +5.24% | -0.42% | no |
| 32 | 0.210290 | 0.203856 | -3.06% | +2.22% | 0.208241 | 0.209570 | +0.64% | +1.07% | no |
| 64 | 0.242753 | 0.236337 | -2.64% | +1.06% | 0.226865 | 0.230178 | +1.46% | +2.71% | no |
| 128 | 0.239921 | 0.239282 | -0.27% | +0.79% | 0.223873 | 0.234642 | +4.81% | -4.02% | no |
| 256 | 0.247745 | 0.246289 | -0.59% | +0.14% | 0.230241 | 0.235025 | +2.08% | +0.94% | yes |
| 512 | 0.252577 | 0.254833 | +0.89% | +0.13% | 0.234833 | 0.235105 | +0.12% | -0.21% | yes |
| 1024 | 0.271026 | 0.264689 | -2.34% | -0.46% | 0.248578 | 0.249202 | +0.25% | -0.03% | yes |
| 2048 | 0.345426 | 0.352753 | +2.12% | -0.59% | 0.334978 | 0.339139 | +1.24% | -1.73% | no |
| 4096 | 0.513715 | 0.512723 | -0.19% | +1.06% | 0.501842 | 0.498100 | -0.75% | -1.84% | yes |

| T | C1 automatic choice | v2 automatic choice | v2 online first/second margin us | Changed split ranks fixed / auto |
|---:|---|---|---:|---|
| 1 | M256/N64, C2, F8, epi | M128/N64, C2, F4, reuse | 2.3 | [0, 3, 4] / [1, 3, 4, 5, 6] |
| 2 | M256/N64, C2, F4, epi | M128/N64, C2, F8, epi | 0.9 | [0, 3, 4] / [1, 3, 4, 5, 6] |
| 4 | M128/N64, C1, F4, reuse | M128/N64, C2, F4, epi | 0.1 | [0, 3, 4] / [1, 3, 4, 5, 6] |
| 8 | M128/N64, C1, F8, reuse | M256/N128, C2, F4, reuse | 0.6 | [0, 3, 4] / [1, 3, 4, 5, 6] |
| 16 | M256/N64, C2, F8, reuse | M128/N64, C2, F4, reuse | 0.3 | [3] / [3] |
| 32 | M128/N64, C1, F4, epi | M128/N64, C2, F4, reuse | 0.9 | [0, 1, 2, 3, 4, 6] / [0, 4, 6, 7] |
| 64 | M128/N64, C1, F8, epi | M128/N64, C2, F4, epi | 0.2 | [4, 6] / [0, 1, 3, 6, 7] |
| 128 | M256/N64, C2, F4, epi | M128/N64, C1, F8, epi | 1.1 | [1, 3, 6] / [5, 6] |
| 256 | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi | 0.0 | [0, 5] / [1, 4, 5, 6] |
| 512 | M256/N64, C2, F8, epi | M256/N64, C2, F8, epi | 0.5 | [1, 5, 6, 7] / [0, 3, 4, 5, 7] |
| 1024 | M256/N64, C2, F4, epi | M256/N64, C2, F4, epi | 3.1 | [1, 2, 6] / [1, 3, 4, 6] |
| 2048 | M256/N128, C2, F4, reuse | M256/N128, C2, F8, reuse | 1.6 | [4] / [6] |
| 4096 | M256/N128, C2, F4, reuse | M256/N128, C2, F4, reuse | 18.7 | [] / [] |

The v2 same-source auto run is slower than its fixed control at 1(+4.80%), 8(+7.96%), 32(+2.80%). Only T128 selects C1; its online first/second margin is 1.1 us. T256 is tied at displayed 0.1 us precision; the rank0 returned winner is consistent with the complete ranking and all 8 returned choices. The source preserves unrounded timing for selection, while stdout is rounded. A printed tie does not imply an inconsistent winner.

Raw 52-row and actual-choice tables: [fixed/auto](fixed-versus-auto16-full13.md), [complete auto13](auto16-full13.md). Exact per-rank cross-run split tactic deltas, all source/hash checks and recorded runtime identity: [JSON](c1-versus-v2.json). Source-correlated codegen evidence is separate; no profiler duration is used here.
