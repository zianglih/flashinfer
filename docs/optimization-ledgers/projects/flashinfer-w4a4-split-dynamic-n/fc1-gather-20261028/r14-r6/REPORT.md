# R14 versus R6 gathered-FC1 quick screen

**Measured control: R6, not PR head.** All four same-GPU C-A-A-C jobs completed.
The 32 cells contain 12,800 fresh CUPTI samples: 100 samples per pass, with frozen routes/tactics, 10 warmups and cold-L2 CUDA graphs. Positive percentages mean R14 is faster.

| Model | Backend | 8 | 256 | 4096 | 16384 |
| --- | --- | ---: | ---: | ---: | ---: |
| V3 EP8 | CuteDSL PER-TOKEN | -0.42% | +30.85% | +55.34% | +67.27% |
| V3 EP8 | CuteDSL W4A16 | -0.06% | -0.01% | -0.05% | +0.59% |
| V3 EP8 | CuteDSL W4A4 | +39.22% | +32.03% | +68.55% | +39.71% |
| V41F EP4 | CuteDSL MXFP4x8 | +164.94% | +223.11% | +218.25% | +90.34% |
| V41F EP4 | CuteDSL MXFP8 | +46.87% | -0.00% | +44.81% | +80.32% |
| K3 EP8 | CuteDSL MXFP4x8 | +150.55% | +220.97% | +204.47% | +170.42% |
| N3U TP8 | CuteDSL MXFP4x8 | +0.42% | -0.14% | +52.26% | +9.37% |
| N3U TP8 | CuteDSL MXFP8 | +31.07% | +103.37% | +51.76% | +11.44% |

The script also emitted four unchanged V3 W4A16 diagnostic cells. The following optimization aggregates exclude W4A16.

| Model | Decode (8) | Middle (256) | Prefill (4096/16384) | All sampled cells |
| --- | ---: | ---: | ---: | ---: |
| V3 EP8 | +17.74% | +31.44% | +57.28% | +39.88% |
| V41F EP4 | +97.27% | +79.75% | +99.43% | +93.79% |
| K3 EP8 | +150.55% | +220.97% | +186.94% | +185.26% |
| N3U TP8 | +14.72% | +42.51% | +29.55% | +28.70% |
| All sampled cells | +50.87% | +67.10% | +73.53% | +65.99% |

## Repeated-phase spread

- Maximum R6 control repeat spread: **2.77%**, V3 EP8 / CuteDSL W4A16 / 16384 tokens (1152.424 vs 1184.328 µs).
- Maximum R14 candidate repeat spread: **3.18%**, V41F EP4 / CuteDSL MXFP4x8 / 16384 tokens (803.591 vs 778.806 µs).

Spread is `100*(max(pass1,pass2)/min(pass1,pass2)-1)` within each role, not the candidate/control difference. Cell speedup uses the ratio of geometric means of the two control and two candidate pass medians.

## Provenance and checks

- R6 kernel: `deba8b639fba89e6f76381e8c6bf8bc323ccaf850b973c836f476f8144c4cc0a`.
- R14 kernel: `6605aeacc09dfe16232312d17bcf00d320f4e5065e8a5ed34514b9542f6cf372`.
- Both dirty source snapshots: all 513 source hashes, full patch hashes and persistent-cache links checked before/after phases. Source changed only through the separately frozen candidate.
- Every phase verified CUPTI with no event fallback, 100 finite positive samples per cell, zero autotuning, frozen cache identities, routing identities and output contracts.
- Candidate runtime guards verified loaded-kernel register reservation before launch; compiler options/caches remained normal. No TRTLLM/non-swap backend was rerun.
- Full pass medians and spreads: `analysis/cells.csv`. Raw samples, logs, guard receipts and source-pinned configuration: `evidence/`.
