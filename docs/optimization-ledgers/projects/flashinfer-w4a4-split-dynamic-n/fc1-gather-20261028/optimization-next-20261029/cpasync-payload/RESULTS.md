# FC1 cp.async payload: reject

**Do not retain.** Across 36 affected cells, the speedup is −4.67% overall and −9.92% for prefill. Decode improves +1.68%, but all four dtypes regress overall. The largest prefill regression is −23.27%, substantially larger than the repeat spreads. Keep the retained Gather4 transport.

- Control: retained `c0c0bc41c70100c694ac55585990971aba8b7fb9` tree, kernel `3225acf2dfeba54df42481b3186267b1bde642da9887b98cb966d5383d8635af`. The immutable remote checkout is `7106faf` plus its measured metadata patch; all 513 source hashes were matched to c0c0 before the run.
- Candidate: c0c0 plus transport-only patch `6df4c0da36e7530a1bb200f697e67693c0c72cf389885a5b2a355bafc66f7ad1`; kernel `8baae0e09e8c6fc02900ae89404861026dcba50c14fa3fae48a31269d363703f`. FC2, 112/128/256 budgets, relay fences, SF order, stage capacity and frozen tactics unchanged. Four gather warps issue 16-byte cp.async vectors. The cp.async cache operation also replaces the Gather4 TMA cache policy, so this compares transport policies, not a single opcode.
- C3 B300, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2. GPUs0/3; each job C-A-A-C on one physical GPU. 100 strict CUPTI samples per cell per phase, no event fallback or AUTO, cold L2, unfused, NVFP4 input quantizer included. Fresh controls and candidates; 44 cells / 17,600 samples. W4A16 is unchanged and diagnostic only.
- 17 exact tests passed. 12 captured codegen variants have zero local bytes and no LDL/STL sites. During performance runs, all 128 loaded-kernel observations (66 FC1) passed register guards and reported zero local bytes. Source qualification and generated code are in `QUALIFICATION.md` and `qualification-evidence/`.
- Control repeat spread: median 0.08%, max 2.91%. Candidate: median 0.08%, max 4.48%. Spread is `max(phase median)/min(phase median) − 1`, not a confidence interval.
- Raw phase medians/spreads: `report/cells.csv`; samples and receipts: `perf-evidence/`. Archive SHA256 `e4c4085613ad26bd086dfd093f18bcabf73e8e0eb94ca790930bc329f16aa8cf` (279 files).

Positive means candidate faster: `100 × (sqrt(C1×C2) / sqrt(A1×A2) − 1)`.

| Model | Backend | 8 | 256 | 4,096 | 16,384 |
|:--|:--|--:|--:|--:|--:|
| N3U EP8 | W4A4 | -1.85% | +0.89% | -9.32% | -6.52% |
| N3U EP8 | PER-TOKEN | +0.31% | +0.14% | -2.00% | -2.24% |
| N3U EP8 | W4A16* | +0.00% | +0.73% | -0.06% | +1.38% |
| K3 EP8 | MXFP4x8 | +0.41% | -0.23% | -12.18% | -18.02% |
| V41F EP4 | MXFP4x8 | +10.36% | -0.27% | -10.75% | -8.48% |
| V41F EP4 | MXFP8 | +2.16% | -0.02% | -1.45% | -23.27% |
| V3 TP8 | MXFP4x8 | +2.22% | -0.05% | -15.37% | -19.85% |
| V3 TP8 | MXFP8 | +0.93% | +0.12% | -15.20% | -15.82% |
| V41F TP4 | W4A4 | +0.45% | +0.40% | -1.49% | -6.67% |
| V41F TP4 | PER-TOKEN | +0.55% | +0.15% | -1.32% | -3.89% |
| V41F TP4 | W4A16* | -0.14% | +0.03% | +1.33% | +0.06% |

*W4A16 is unchanged; its +0.42% aggregate is a diagnostic and excluded from the affected means.

The extra per-thread vector/address issue work is a plausible cause of the prefill loss, especially for the 8-bit payload dtypes; no NCU counters were collected for this candidate, so that mechanism is not established. The current repeatable result is sufficient to reject a transport replacement without adding shape-specific dispatch. Unused Gather4 host descriptor/helper cleanup was deliberately not mixed into this screen and is unnecessary after rejection.

The candidate source copy was retired after verifying its HEAD, kernel, and exact patch hashes; the helper scripts, patch, generated code, and evidence remain local. No code was committed or pushed. GPUs0/3/5 were released.
