# K3 fresh-control confirmation

All three flagged regressions in the full refresh do **not reproduce** under fresh same-GPU C-A-A-C. Preserve the original full-refresh numbers; this bounded diagnostic provides separate evidence that their historical pass separation is not a stable effect of the new source. It does not identify a specific hardware cause of the drift.

| Point | Earlier full refresh | Fresh C-A-A-C | First25 / last25 / last50 | Applicable source change |
|---|---:|---:|---|---|
| K3 TP T8 CuteDSL PER-TOKEN | -1.0524% | +0.0096% | +0.3272% / +0.2294% / +0.0862% | SF-prefix |
| K3 EP T128 CuteDSL W4A4 | -0.7905% | +0.0217% | +0.0543% / +0.0433% / +0.0271% | CLC-terminal |
| K3 EP T8192 CuteDSL PER-TOKEN | -0.9894% | +0.0823% | +0.0262% / +0.1569% / +0.0705% | FC2-drain |

Positive is faster: geometric mean of the two all-100-sample control medians divided by geometric mean of the two candidate medians, minus one. The sample strata are diagnostic only; they do not replace any standard median.

314 archived files and all 348 frozen source hashes per role verified. Two jobs, eight fresh passes, 12 cells including unchanged W4A16 controls, and 4,800 strict CUPTI samples. Same physical GPUs 3/4 as the earlier K3 runs; unchanged public API, winners, routes and managed cache contents; cold-L2 CUDA graphs, 10 warmups, 100 samples, input quantization included. No AUTO, source changes, extra numerical tests or sanitizer.

- Candidate kernel: `b668b2736ea9770e0ca2d45a91f461601953bfaa20f8f807731a641fa20d93d8` on 61c2.
- Control: source bytes equal retained `61c2c367009340ca0ed218511ed9382512860f1b`; its physical checkout remains Git HEAD 61249 plus the recorded retained patch.
- Native compilation caches reused; every pass retains a private compiler working directory.

## Source applicability and drift

- TP per-token T8/T16 selects static N16 and FC2 K384 with tile K512. CLC-terminal and bulk-drain paths are absent; SF-prefix is the applicable change. T8 goes from −1.0524% to +0.0096%; T16 is −0.0395% with mixed strata. The new data does not establish a meaningful decode regression.
- EP W4A4 T128 selects CLC with aligned K and route32, so only terminal peeling applies. Its −0.7905% old comparison becomes +0.0217%.
- EP per-token T8192 selects static scheduling with aligned K and route128. Only FC2 bulk-drain applies, conditionally on each tile’s valid-row count. Its −0.9894% old comparison becomes +0.0823%.
- TP T8 fresh control is 0.9279% slower than historical control, while the candidate changes −0.1438%. EP T128 control is nearly unchanged (+0.0246%), but the candidate is 0.7876% faster than its earlier pass. EP T8192 control changes −0.1685%, candidate −1.2376%. Thus the earlier differences are not a single common shift and should not be assigned to a source change from old medians alone.
- Applicability is derived from frozen selected tactics and source branches. This confirmation did not dump new per-winner SASS. W4A16 remains an unchanged-source timing control, not an optimization result.

## Complete fresh output

| Topology | Tokens | Backend | C1 us | A1 us | A2 us | C2 us | Speedup | Control / candidate spread |
|---|---:|---|---:|---:|---:|---:|---:|---|
| TP | 8 | CuteDSL W4A4 | 77.9840 | 77.8405 | 77.9840 | 78.0010 | +0.1030% | 0.0218% / 0.1844% |
| TP | 8 | CuteDSL PER-TOKEN | 83.4085 | 83.5200 | 83.4245 | 83.5520 | +0.0096% | 0.1720% / 0.1145% |
| TP | 8 | CuteDSL W4A16 | 87.2805 | 86.8800 | 86.7680 | 87.3930 | +0.5906% | 0.1289% / 0.1291% |
| TP | 16 | CuteDSL W4A4 | 113.4410 | 113.2010 | 113.2010 | 113.2010 | +0.1060% | 0.2120% / 0.0000% |
| TP | 16 | CuteDSL PER-TOKEN | 120.2090 | 120.2880 | 120.2410 | 120.2250 | -0.0395% | 0.0133% / 0.0391% |
| TP | 16 | CuteDSL W4A16 | 128.4010 | 128.4810 | 128.4170 | 128.2250 | -0.1059% | 0.1373% / 0.0498% |
| EP | 128 | CuteDSL W4A4 | 295.3795 | 295.1880 | 295.3790 | 295.3155 | +0.0217% | 0.0217% / 0.0647% |
| EP | 128 | CuteDSL PER-TOKEN | 305.0750 | 305.1710 | 305.8920 | 305.1870 | -0.1310% | 0.0367% / 0.2363% |
| EP | 128 | CuteDSL W4A16 | 310.5795 | 310.9160 | 310.8515 | 311.0115 | -0.0284% | 0.1391% / 0.0207% |
| EP | 8192 | CuteDSL W4A4 | 469.1255 | 466.6930 | 468.4850 | 467.7810 | +0.1849% | 0.2874% / 0.3840% |
| EP | 8192 | CuteDSL PER-TOKEN | 611.3985 | 611.6545 | 611.6070 | 612.8705 | +0.0823% | 0.2408% / 0.0078% |
| EP | 8192 | CuteDSL W4A16 | 1007.5150 | 1013.9480 | 1015.1475 | 1015.5310 | -0.2989% | 0.7956% / 0.1183% |

Raw commands, environment, source manifests, managed caches, per-pass GPU clock/temperature snapshots and every sample remain under `evidence/raw/`. `report/audit.json` binds the full-refresh/earlier-control evidence without replacing it. GPUs 3/4 were explicitly released after the completed lane receipts and a fresh idle check.
