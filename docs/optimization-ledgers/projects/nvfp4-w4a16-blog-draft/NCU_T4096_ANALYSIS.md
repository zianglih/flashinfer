# NCU tensor-pipe analysis — 2026-10-07

Source archive moved from Downloads to evidence/ncu-t4096/. Raw reports and derived exports stay outside the HAI checkout. Full archive retained, including the unextracted nested Archive.zip.

The supplied reports identify NVIDIA B200; the user requested no hardware label in the article profiling passage or caption. Article introduction now scopes B300 to its latency and serving benchmark campaigns. The screenshot matches W4A16 FC1 action3, name, launch512threads and281.312us.

The source-export metadata retains device identity. No new GPU run. Sourcecommit/command/fulltopology unrecovered. Screenshot uses the HMMA PM series, which matches the tensor-pipe PM series exactly for all four captured GEMMs.

| Path | Whole elapsed % | Main-phase mean % | Main-phase median % | Samples |
|---|---:|---:|---:|---:|
| W4A16 FC1 | 73.12 | 80.11 | 80.29 | 219 |
| W4A16 FC2 | 65.50 | 73.25 | 73.62 | 117 |
| W4A4 FC1 | 38.61 | 44.51 | 45.48 | 97 |
| W4A4 FC2 | 36.57 | 45.32 | 47.16 | 46 |

Main phase is central80% of first-to-last nonzero PM timestamp span; all values in the window retained, using integer comparisons. W4A16FC1 has217/219values in75–85%; FC2is~73% and must notinherit80% claim. Whole-kernel elapsed normalization differs fromactive-only counters and from PM aggregates including sampling margins.

Reproduce: `.plot-venv/bin/python analyze_ncu_t4096.py`. Source hashes and outputmetric definitions in evidence/ncu-t4096/PROVENANCE.json. Independent review matched allfour selected-action calculations.
