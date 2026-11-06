# Three-arm retention assessment

Neither candidate is promoted. Fresh same-node decode GM (T4–512) is **0.995727× for B1** and **0.992369× for C1** versus d01/A1, with three of eight decode wins each. C1 versus B1 is 0.996627×, with four wins. The selected AUTO tactics differ at T1 for B1 and T4096 for both candidates; B1/C1 otherwise have identical selected tactics.

A1 is retained d01. B1 is full-row dispatch return plus readiness notifications, so its difference is not an isolated atomic-overhead experiment. C1 adds the finite early prefix. No timing result proves that nonzero early work occurred; the separately authorized continuation diagnostic addresses that question without making a timing claim.

| T | A1 µs | B1 µs | C1 µs | A1/B1 | A1/C1 | B1/C1 | A1 / B1 / C1 tactic |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 65.6640 | 63.6805 | 67.7440 | 1.031148 | 0.969296 | 0.940017 | N64 epi / N128 epi / N64 epi |
| 2 | 87.3285 | 80.8000 | 83.1200 | 1.080798 | 1.050632 | 0.972089 | N64 epi / N64 epi / N64 epi |
| 4 | 96.5285 | 97.4245 | 98.6560 | 0.990803 | 0.978435 | 0.987517 | N64 epi / N64 epi / N64 epi |
| 8 | 121.9200 | 121.8240 | 120.8965 | 1.000788 | 1.008466 | 1.007672 | N64 epi / N64 epi / N64 epi |
| 16 | 132.0170 | 131.7130 | 135.1215 | 1.002308 | 0.977024 | 0.974775 | N64 epi / N64 epi / N64 epi |
| 32 | 160.1920 | 161.0405 | 158.4970 | 0.994731 | 1.010694 | 1.016048 | N64 epi / N64 epi / N64 epi |
| 64 | 183.0565 | 183.8730 | 184.8010 | 0.995559 | 0.990560 | 0.994978 | N64 epi / N64 epi / N64 epi |
| 128 | 185.3935 | 188.6405 | 183.7610 | 0.982787 | 1.008884 | 1.026554 | N64 epi / N64 epi / N64 epi |
| 256 | 190.2565 | 191.4730 | 191.1690 | 0.993647 | 0.995227 | 1.001590 | N64 epi / N64 epi / N64 epi |
| 512 | 197.3120 | 196.2570 | 203.2970 | 1.005376 | 0.970560 | 0.965371 | N64 epi / N64 epi / N64 epi |
| 4096 | 464.8015 | 487.6810 | 488.0660 | 0.953085 | 0.952333 | 0.999211 | N128 dispatch / N128 epi / N128 epi |
| 8192 | 769.0255 | 783.1390 | 776.5795 | 0.981978 | 0.990273 | 1.008447 | N128 dispatch / N128 dispatch / N128 dispatch |
| 16384 | 1496.6120 | 1415.2840 | 1424.5165 | 1.057464 | 1.050611 | 0.993519 | N128 dispatch / N128 dispatch / N128 dispatch |

The T128 C1/B1 improvement is separated across quarters (B1 188.448–189.120µs, C1 183.393–184.321µs), but C1 regresses at T4, T16, T64 and T512 versus A1. T512 C1 is 203.297µs versus A1 197.312µs and B1 196.257µs. These mixed rows do not support retaining the implementation for decode.

T4096 regresses about 4.7% in both candidates and changes the AUTO tactic. T8192 is slower in both. The apparent T16384 gains (5.75% B1, 5.06% C1) coincide with substantial within-arm drift: A1 quarter medians are 1356.739/1392.771/1505.827/1540.388µs; B1 1330.180/1389.861/1418.725/1532.739µs; C1 1334.340/1410.371/1471.939/1478.820µs. Serial arms and these distributions do not isolate an overlap benefit.

| T | A1 MAD µs; quarter medians µs | B1 MAD µs; quarter medians µs | C1 MAD µs; quarter medians µs |
|---:|---|---|---|
| 1 | 0.9605; 66.8480/65.6320/65.5680/65.4400 | 0.8320; 64.2250/63.6160/63.4570/63.6490 | 0.6395; 67.3920/67.7770/67.7440/68.0950 |
| 2 | 0.7685; 87.3920/87.5850/87.0720/87.3600 | 1.1510; 80.5450/81.1210/81.0890/80.1930 | 0.7360; 83.6800/82.6560/83.2640/83.3280 |
| 4 | 0.6395; 96.8330/96.2240/96.6090/96.2570 | 0.7200; 97.7920/97.3760/97.0880/97.5050 | 0.6080; 98.8160/98.2080/98.7520/98.9120 |
| 8 | 0.8485; 122.3680/122.0160/120.8970/121.9840 | 0.7990; 122.4650/121.8240/122.0480/121.0880 | 1.1360; 121.6330/120.4800/120.5130/121.8880 |
| 16 | 0.9120; 131.7140/131.9370/131.8100/132.1930 | 0.8960; 132.3530/131.4890/131.3290/131.8080 | 0.9925; 134.2420/134.9460/135.9700/134.9450 |
| 32 | 0.8325; 159.7130/159.3610/160.4810/160.8320 | 0.7685; 161.6010/161.1210/160.4810/161.1850 | 0.9280; 158.5290/158.6880/158.0490/158.8180 |
| 64 | 0.7680; 183.0720/183.5850/183.1690/182.7850 | 0.6555; 183.7450/183.8730/184.1290/183.8730 | 0.7510; 185.0240/184.7360/184.8320/184.8650 |
| 128 | 0.9115; 185.7290/185.6330/185.2180/185.0570 | 1.0395; 188.5450/188.8640/189.1200/188.4480 | 0.8800; 184.0330/184.3210/183.7130/183.3930 |
| 256 | 0.9280; 190.4960/190.4330/190.0810/190.0480 | 0.9755; 191.6810/191.2330/192.0010/191.3930 | 0.7690; 191.3930/191.4570/190.5280/191.4240 |
| 512 | 1.6160; 197.3130/198.8810/196.6410/196.1920 | 1.4720; 195.6810/197.8570/196.8330/194.8490 | 1.4085; 204.7050/203.0740/203.1690/203.2020 |
| 4096 | 3.1685; 462.5290/464.2250/464.8330/465.7930 | 2.0320; 487.4570/487.3930/487.8410/488.0330 | 2.0485; 487.8100/490.1140/487.0740/487.7780 |
| 8192 | 5.9200; 764.0980/763.4580/771.0410/811.0100 | 14.6400; 772.8350/770.2750/798.5310/809.4750 | 15.1685; 767.5860/765.5390/792.7090/808.5460 |
| 16384 | 49.4715; 1356.7390/1392.7710/1505.8270/1540.3880 | 80.7525; 1330.1800/1389.8610/1418.7250/1532.7390 | 51.3125; 1334.3400/1410.3710/1471.9390/1478.8200 |

Validation: independent terminal audit passed once with unchanged raw-sample, finite/repeat, fixture and exact-output validators. Each of A1/B1, A1/C1 and B1/C1 has 104 exact cross-arm rank outputs. All 438 original member files, including 312 source files, immutable runtime, native/codegen prerequisites, environment and source/process/GPU closure, were verified. Twenty-four serialized outputs were reconstructed solely from matching SHA256 cache bytes. The original gzip archive remains remote and its byte hash was not locally verified.

Native compile coverage and execution remain distinct: the actual int32-vector cases had zero stack/local resources; B1 N64 int64-generic compile-only variants have STACK8 (rank0 one STL/five LDL). The generated-order gate passed publication and acquire-before-load checks; this is not proof of successful early reductions.

Audit: `performance/independent-file-timing-audit.json`, SHA256 `46f51e7d566258fd9465f1aea004c63495efa46f641413f85dbf947442081667`. Original archive seal reference: `f5fbd595248eef83215b069b83895dcef81bbb895b701baf4f334106226f75a5`.
