# MMA readiness peek: rejected

The +11/−1-line speculative MMA readiness probe is not retained. Across69 affected EP cells it is **0.361% slower** (geometric mean); decode39cells−0.190%, prefill30cells−0.582%. The unchanged W4A16 control is−0.027% across17cells. The extra probe/state has no broad performance benefit, so this experiment does not expand to TP. Canonical source remains d1767be1.

| Model | Affected cells | Speedup |
|---|---:|---:|
| kimi-k3 | 15 | -0.691% |
| nemo3-ultra | 16 | -0.032% |
| v3 | 16 | -0.483% |
| v41-flash | 22 | -0.285% |

| Dtype | Cells | Speedup |
|---|---:|---:|
| CuteDSL MXFP4x8 | 20 | -0.054% |
| CuteDSL MXFP8 | 15 | -0.118% |
| CuteDSL PER-TOKEN | 17 | -0.835% |
| CuteDSL W4A4 | 17 | -0.460% |

Material observed regressions include V3 MXFP8 T16384−4.111%, K3 per-token T4096−3.906%, and K3 per-token T16384−3.409%. These have control endpoint drift of−0.403%,−0.043%, and+0.729%, respectively. This bounded screen supports rejection; it is not a replacement for the full published matrix.

Protocol: same d1767be1 baseline source and sole candidate kernel diff; fixed saved winners; identical routes; each cell runs C-A-A-C on one GPU.86cells/344 accepted medians/34,400 positive CUPTI samples,100samples perphase,10warmups,coldL2 CUDAgraphs. NV includes input quantization. All cache lookups hit existing winners; zero profiling; source/config/helper/result/log hashes verified. Primary/secondary GPU5 lanes completed and are released.

Exact/codegen gate:160 paired output-byte comparisons across intermediate384/2304, including graph route mutation, PDL off/on, static/CLC, one/twoCTA and all four affected formats.80 FC1/FC2 codegen pairs retain identical registers, zero stack/local traffic and matching launch/storage geometry. Two initial control PTX dumps were corrupted by concurrent generic-filename dumps into a shared source CWD. Original output checks remain valid; control artifacts were recollected in private per-process CWD on secondaryGPU7. Final audit verifies PTX/SASS CTA/dtype identity and compares the recollection with original serialized candidate artifacts.

Evidence: `screen-cells.csv` contains all86 C-A-A-C rows; `screen-passes.csv` the344 raw pass medians. `screen-analysis.json` includes complete summaries. `audit_screen.py` independently verifies fetched source-bound timing, winner, route and artifact evidence. Original gate archive:676 hash-verified files, SHA256`890dbd89541c76069e56ec3f32f814d6184abd2333a90bae324ce43d55d97566`. Final archive:1,489 files, SHA256`7622ef8fd912ee7ec22be89b23aed96f2fdb39feac6e5fac76dd1023f2f2ee3d`. No publication or retained source change.
