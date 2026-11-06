# Partial W4 transform-group screen

Candidate b25dac versus retained49, V41F TP4 W4A16, all13 existing token counts. Same-GPU C-A-A-C with immutable recorded winners/routes,100 native CUPTI cold-L2 CUDA-graph samples and10 warmups per phase/cell. No retuning;1/2 are excluded only from retention.

| Band | Retention cells | Geomean speedup | Negative cells |
|---|---:|---:|---:|
| all | 11 | +0.217% | 3 |
| decode | 5 | +0.571% | 1 |
| middle | 3 | +0.752% | 0 |
| prefill | 3 | -0.898% | 2 |

Tokens8–512 improve consistently by0.43–0.98%; token4 is−0.097%. The8K/16K rows are−2.742%/−0.465%. All16 anomalous clock quartiles occur at8K/16K across both arms, including power-cap reason4; their magnitudes are not clean causal estimates. All208 quartiles are present, with no sample removal. The8K control/candidate repeat spreads are1.307%/1.087%. Decode/middle clocks are2032MHz with no throttle reasons.

All26 measured FC1/FC2 configurations join to actual loaded library resource receipts and remain identical/LOCAL0 across allfour phases.5200 raw samples,52 phase medians and36 compiled native function records are retained.

The source adds57 net lines and constexpr full/tail dispatch, with+120–180 static non-NOP in the affected representative kernels. Fourteen selected exact calls passed;13 of17 native pairs are byte-identical for unaffected/aligned/shared-Mega paths. Rejected after the independent root replay passed: the small aggregate benefit and mixed prefill evidence do not clearly justify the implementation complexity. No shape/tactic rescue, remeasurement, commit, or publication update is planned.

## All phase medians

| Model | EP/TP | Mode | Tokens | C1 µs | A1 µs | A2 µs | C2 µs | Speedup | C spread | A spread |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| v41-flash | TP4 | CuteDSL W4A16 | 1 | 23.904 | 24.033 | 24.032 | 24.000 | -0.335% | 0.402% | 0.004% |
| v41-flash | TP4 | CuteDSL W4A16 | 2 | 28.608 | 28.576 | 28.624 | 28.640 | +0.084% | 0.112% | 0.168% |
| v41-flash | TP4 | CuteDSL W4A16 | 4 | 41.008 | 41.120 | 41.072 | 41.104 | -0.097% | 0.233% | 0.118% |
| v41-flash | TP4 | CuteDSL W4A16 | 8 | 62.864 | 62.656 | 62.592 | 62.928 | +0.434% | 0.103% | 0.101% |
| v41-flash | TP4 | CuteDSL W4A16 | 16 | 99.392 | 98.817 | 98.753 | 99.345 | +0.591% | 0.048% | 0.065% |
| v41-flash | TP4 | CuteDSL W4A16 | 32 | 153.473 | 151.936 | 152.161 | 153.505 | +0.947% | 0.021% | 0.147% |
| v41-flash | TP4 | CuteDSL W4A16 | 64 | 226.561 | 224.417 | 224.449 | 226.721 | +0.984% | 0.071% | 0.014% |
| v41-flash | TP4 | CuteDSL W4A16 | 128 | 300.594 | 298.545 | 298.546 | 300.657 | +0.697% | 0.021% | 0.000% |
| v41-flash | TP4 | CuteDSL W4A16 | 256 | 341.218 | 338.337 | 338.498 | 340.994 | +0.794% | 0.066% | 0.048% |
| v41-flash | TP4 | CuteDSL W4A16 | 512 | 350.690 | 347.906 | 347.873 | 350.418 | +0.766% | 0.078% | 0.009% |
| v41-flash | TP4 | CuteDSL W4A16 | 4096 | 557.427 | 557.170 | 553.811 | 559.554 | +0.540% | 0.382% | 0.607% |
| v41-flash | TP4 | CuteDSL W4A16 | 8192 | 980.996 | 996.725 | 1007.556 | 968.341 | -2.742% | 1.307% | 1.087% |
| v41-flash | TP4 | CuteDSL W4A16 | 16384 | 1906.344 | 1918.169 | 1916.634 | 1910.634 | -0.465% | 0.225% | 0.080% |

## Evidence

- Raw: `evidence/w4-partial-group-screen/1793376993014148000/data`; standard source/tactic/route/CUPTI/component/clock report: `evidence/w4-partial-group-screen/1793376993014148000/report`.
- `qualification-summary.json`, `QUALIFICATION.md`, `source-proof.json`, `AFFECTED_SCOPE.md`, `final-gate.json` bind scope and exact/native evidence.
- Original legacy-layout intermediate352 and private M-major K16 retained-control failures remain in separate immutable qualification leaves; neither is hidden by the selected successful summary.
- Independent source/native gate: `audits/w4-partial-group-gate-peer.json`; independent performance replay passed at `audits/w4-partial-group-data-root.json`.
