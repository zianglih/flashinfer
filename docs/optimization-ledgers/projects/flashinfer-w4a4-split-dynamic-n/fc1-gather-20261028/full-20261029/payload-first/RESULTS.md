# Payload-first gather screen vs clean fork head

Base: `fb66a27e6b40bdbbefd1b8bf0c0fc3f3ada8af90`. Candidate kernel: `bb9dc56eb993192e43ee3b1d2d2a2ed6742cd4e7b756b1c4d5f874378d300dcd`. One unstaged block relocation; FC2 unchanged.

**Do not retain:** 36 affected cells have -0.178% geometric mean. There is no broad gain and N3U EP W4A4 at4096 tokens is −2.017% with only0.11%/0.26% repeat spread.

All7 selected tests passed. All20 C-A-A-C phases completed;44 cells/17,600 strict-CUPTI cold-L2 samples verified with frozen routing/tactics, unchanged output capacity, exact sources and all candidate runtime register guards. NVFP4 includes input quantization. Controls freshly measured from clean fork head; no old PR-head timing reuse.

Positive means payload-first is faster. W4A16 is unchanged and shown only as a timing diagnostic.

| Topology/model | Backend | T8 | T256 | T4096 | T16384 |
|---|---|---:|---:|---:|---:|
| EP kimi-k3 | CuteDSL MXFP4x8 | +0.011% | -0.025% | +0.096% | -0.481% |
| EP nemo3-ultra | CuteDSL W4A4 | -0.083% | +0.143% | -2.017% | -0.189% |
| EP nemo3-ultra | CuteDSL PER-TOKEN | -0.343% | -0.064% | +0.057% | +0.021% |
| EP nemo3-ultra | CuteDSL W4A16 | +0.138% | -0.026% | -0.146% | -4.271% |
| EP v41-flash | CuteDSL MXFP8 | +0.077% | +0.021% | -0.075% | +0.989% |
| EP v41-flash | CuteDSL MXFP4x8 | +0.321% | -0.019% | -0.039% | -3.244% |
| TP v3 | CuteDSL MXFP8 | -0.124% | -0.257% | -0.137% | -0.693% |
| TP v3 | CuteDSL MXFP4x8 | +0.528% | -0.026% | -0.162% | -0.402% |
| TP v41-flash | CuteDSL W4A4 | -0.000% | +0.116% | -0.060% | -0.239% |
| TP v41-flash | CuteDSL PER-TOKEN | -0.139% | -0.032% | -0.130% | +0.264% |
| TP v41-flash | CuteDSL W4A16 | -0.026% | -0.013% | +0.061% | +2.451% |

Limitations: K3 EP and V41F EP at16384 have2–6% phase spread, so small deltas there are inconclusive. Unchanged W4A16 diagnostics also drift (N3U EP T16384−4.27%; V41F TP T16384+2.45%); these are not candidate gains/regressions. The stable N3U EP T4096 W4A4 regression and lack of consistent gains are sufficient to avoid retention.

Raw cells: `report/cells.csv`; verified receipts and samples: `evidence/perf/`; tests: `evidence/tests.xml`; all transfer hashes: `evidence/MANIFEST.json`.
