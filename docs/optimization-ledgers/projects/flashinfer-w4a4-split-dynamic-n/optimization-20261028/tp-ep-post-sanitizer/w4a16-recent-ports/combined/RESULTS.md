# W4A16 combined tail and packed FC2: source-paired screen

Audited **32 cells, 128 medians, 12,800 strict CUPTI samples** against `fd72759b15b8d417d6c791c0382f90d14262a8e4`, with unchanged 83df winners/routes. Eight model/topology jobs each run C1,A1,A2,C2; 10 warmups and 100 samples per pass. Source, managed cache, winner, routing, command, GPU UUID and raw sample medians independently verify.

Overall geometric-mean speedup **+0.3998%**; EP **-0.0623%** and TP **+0.8641%**. The 12 partial-K cells are TP V41F/K3/N3U: **+1.2728%**, decode **+0.4292%**, prefill **+2.1234%**. The 20 full-K cells measure **-0.1204%**.

Speedup = geometric mean(C1,C2) / geometric mean(A1,A2) − 1; positive favors candidate.

| Model/topology | T4 | T64 | T4096 | T16384 |
|---|---:|---:|---:|---:|
| V3 EP | -0.078% | +0.091% | -0.357% | -0.767% |
| V41F EP | +0.331% | +0.209% | -0.190% | -2.492% |
| K3 EP | -0.263% | -0.013% | +0.393% | +0.389% |
| N3U EP | +0.019% | +0.146% | -0.036% | +1.674% |
| V3 TP | -0.160% | +0.047% | -0.283% | -1.009% |
| V41F TP | +0.151% | +0.480% | +2.718% | +3.214% |
| K3 TP | +0.900% | +0.868% | +0.771% | +1.263% |
| N3U TP | +0.201% | -0.021% | +2.477% | +2.318% |

Worst measured cell: V41F EP T16384 -2.4922%. Its C1/A1/A2/C2 medians are 1.541981/1.5652135/1.548782/1.4947335000000002 ms. All raw pass medians and observed spreads are retained in `report/cells.csv`; no measured rows are discarded.

The combined source passed 16 exact cases, 112 graph replays, 4 old/new-layout public API tests and 24 compiled-kernel checks. FC1 matches tail-only, FC2 resources/MMA sites are unchanged, and no local/stack or uniform spill/fill instructions were observed. The standalone packed variant already used packed FP32 multiplication in the control; its benefit is reduced static full/tail code duplication, not a claim of halving executed multiply instructions.

Archive SHA256 `ff835f0d876fd84a0a9a8be78dad1473e8b25c721d96f93e20fc1e4fa65af7b4`; 1,291 files verified. Candidate kernel SHA `2caee0b467e9017bd53847a6401680810653eb4fdaff4573bc788cacb1a60126`. No retuning, external baseline rerun or public table replacement. The later requested `num_k_atoms` handoff cleanup is not part of this frozen measured source.
