# W4A16 compile-time partial-K tail: source-paired screen

Audited **32 cells, 128 medians, 12,800 strict CUPTI samples** against `fd72759b15b8d417d6c791c0382f90d14262a8e4`, with unchanged 83df winners/routes. Eight model/topology jobs each run C1,A1,A2,C2; 10 warmups and 100 samples per pass. Source, managed cache, winner, routing, command, GPU UUID and raw sample medians independently verify.

Overall geometric-mean speedup **+0.6342%**; EP **+0.1527%** and TP **+1.1181%**. The 12 partial-K cells are TP V41F/K3/N3U: **+1.5006%**, decode **+0.6154%**, prefill **+2.3936%**. The 20 full-K cells measure **+0.1179%**.

Speedup = geometric mean(C1,C2) / geometric mean(A1,A2) − 1; positive favors candidate.

| Model/topology | T4 | T64 | T4096 | T16384 |
|---|---:|---:|---:|---:|
| V3 EP | -0.109% | -0.057% | +0.011% | +1.610% |
| V41F EP | +0.103% | +0.145% | -1.378% | -1.854% |
| K3 EP | -0.181% | -0.032% | -0.066% | -0.161% |
| N3U EP | -0.057% | +0.017% | -0.137% | +4.736% |
| V3 TP | +0.022% | -0.180% | -0.072% | +0.147% |
| V41F TP | +0.248% | +0.459% | +2.916% | +1.874% |
| K3 TP | +0.838% | +1.193% | +2.470% | +1.684% |
| N3U TP | +0.504% | +0.453% | +3.990% | +1.449% |

Worst measured cell: V41F EP T16384 -1.8544%. Its C1/A1/A2/C2 medians are 1.4859615000000002/1.5369385/1.557243/1.5514830000000002 ms. All raw pass medians and observed spreads are retained in `report/cells.csv`; no measured rows are discarded.

All 12 partial-K cells improved. The codegen gate confirms aligned kernels have identical instruction streams/resources, so full-K timing changes are not evidence of a code benefit. Three forced-static control-IR failures are excluded from the native exact gate; 32 native/public cases passed.

Archive SHA256 `2b15e488ed8fbb8f44b2b9012f4d684b9febb2ffc0652275617e1ec631cdb050`; 1,290 files verified. Candidate kernel SHA `cfbe0490282c1774a66df8d22d611cebd72eceb08e6db9b543a9c69b980c156a`. No retuning, external baseline rerun or public table replacement. The later requested `num_k_atoms` handoff cleanup is not part of this frozen measured source.
