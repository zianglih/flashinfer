# Cumulative W4 prefill: independent raw peer

Passed: all 9,600 raw CUPTI spans / 96 phase medians / 24 cells. Config `618bb79894cf430386cd615874c1a2af27eed50a215f2a3637c032dca598b2f7`; archive `604ec58f3c3b9a11f0ca9c796f63a8c2f6e88e124b26c2c7a3e505bb7ed3eec9`. Replayer: [audit_w4_cumulative_prefill_data.py](audit_w4_cumulative_prefill_data.py); machine receipt: [w4-cumulative-prefill-data-peer.json](w4-cumulative-prefill-data-peer.json).

Fresh CAAC compares pre-PR9 `82254e20` with retained production-equivalent `c1ac8ce7` under the same current `moe_utils 046552b8` release cohort. The two complete 13,245-file inventories differ by exactly the four Git files in the source plan. No old timing phases or old native cohort were reused. This measures the cumulative branch effect; it does not attribute a particular commit or replace historical publication denominators.

Recomputed geometric mean **-0.461723%**, with **12 / 24 negative cells**. All 48 per-cell FC1/FC2 resource and resolved-geometry comparisons agree across all four phases; 120 loaded guard records have zero LOCAL and unchanged normal compile options. All 14 explicit choices and 10 recorded defaults match the frozen cache/routes; 80 default stage joins resolve to actual compiled libraries. This is the captured driver/resource boundary, not a new dynamic shared-memory or occupancy measurement.

All 384 clock quartiles were replayed from raw NVML records: **100 exceptions, zero missing**. Every original sample and negative row remains. Exceptions mean median SM clock differs from 2032 MHz or a nonzero clock reason occurs; they do not establish the cause of a latency change. Component duration, start/end, overlap extension and quartile medians were regenerated using the inherited analyzer and match the saved component samples exactly.

## All primary cells

Positive change means the candidate is faster. Phase columns are microseconds in C1/A1/A2/C2 order. Repeat spread is max/min−1 within each arm.

| Job | Tokens | Change % | C1 | A1 | A2 | C2 | Spread C/A % | Clock flags / 16 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ep-kimi-k3 | 4096 | -0.011818 | 561.3470 | 526.3875 | 566.5325 | 531.1245 | 5.690/7.627 | 0 |
| ep-kimi-k3 | 8192 | -4.229933 | 985.1420 | 986.8390 | 987.9910 | 907.7370 | 8.527/0.117 | 4 |
| ep-kimi-k3 | 16384 | +0.359797 | 1941.7090 | 1936.8930 | 1926.9890 | 1936.0665 | 0.291/0.514 | 13 |
| ep-nemo3-ultra | 4096 | +0.064574 | 398.9795 | 399.4270 | 397.3160 | 398.2755 | 0.177/0.531 | 0 |
| ep-nemo3-ultra | 8192 | +2.331483 | 764.0535 | 738.1980 | 783.9745 | 793.1760 | 3.812/6.201 | 1 |
| ep-nemo3-ultra | 16384 | +0.780310 | 1558.4125 | 1483.5320 | 1538.8445 | 1487.8550 | 4.742/3.728 | 9 |
| ep-v3 | 4096 | +0.144448 | 288.8015 | 288.2410 | 287.9370 | 288.2090 | 0.206/0.106 | 0 |
| ep-v3 | 8192 | -0.871762 | 572.9945 | 560.7865 | 587.4265 | 564.9310 | 1.427/4.750 | 0 |
| ep-v3 | 16384 | -0.700292 | 1148.0525 | 1137.0775 | 1147.4770 | 1120.6455 | 2.446/0.915 | 6 |
| ep-v41-flash | 4096 | +0.275050 | 449.9060 | 448.1620 | 447.2825 | 448.0030 | 0.425/0.197 | 0 |
| ep-v41-flash | 8192 | -5.565038 | 708.7075 | 725.1235 | 754.4360 | 688.3875 | 2.952/4.042 | 1 |
| ep-v41-flash | 16384 | -1.196297 | 1434.5995 | 1515.6720 | 1522.7280 | 1570.5195 | 9.474/0.466 | 10 |
| tp-kimi-k3 | 4096 | +0.720181 | 697.1255 | 697.6535 | 686.3580 | 696.8070 | 0.046/1.646 | 0 |
| tp-kimi-k3 | 8192 | -1.244135 | 1292.6820 | 1269.5470 | 1306.6510 | 1251.5335 | 3.288/2.923 | 5 |
| tp-kimi-k3 | 16384 | +1.564425 | 2476.4520 | 2442.3880 | 2451.3490 | 2493.8660 | 0.703/0.367 | 12 |
| tp-nemo3-ultra | 4096 | +0.208330 | 538.8220 | 537.7180 | 537.9730 | 539.1100 | 0.053/0.047 | 0 |
| tp-nemo3-ultra | 8192 | +0.930098 | 924.7935 | 906.4895 | 922.0100 | 920.6510 | 0.450/1.712 | 2 |
| tp-nemo3-ultra | 16384 | -2.074922 | 1848.5470 | 1863.2360 | 1870.7395 | 1808.1670 | 2.233/0.403 | 11 |
| tp-v3 | 4096 | +0.255930 | 476.0510 | 475.0265 | 475.3470 | 476.7550 | 0.148/0.067 | 0 |
| tp-v3 | 8192 | -0.153522 | 849.5890 | 834.6135 | 855.7820 | 838.1180 | 1.369/2.536 | 1 |
| tp-v3 | 16384 | +0.005474 | 1696.0110 | 1715.2760 | 1689.4030 | 1708.7800 | 0.753/1.531 | 8 |
| tp-v41-flash | 4096 | -0.357472 | 547.4440 | 554.9170 | 543.5880 | 547.0760 | 0.067/2.084 | 0 |
| tp-v41-flash | 8192 | -1.308890 | 908.4860 | 947.0630 | 958.8230 | 973.5430 | 7.161/1.242 | 9 |
| tp-v41-flash | 16384 | -0.674824 | 1823.1815 | 1856.9250 | 1840.3175 | 1849.1660 | 1.425/0.902 | 8 |

## Negative-cell components

Candidate minus control, µs. These are differences of the arithmetic mean of two phase component medians. Component medians are not additive and need not sum to the geometric-mean E2E difference. Duration and exposed extension are shown separately.

| Job | Tokens | FC1 duration / extension | FC2 duration / extension | Combine duration / extension | Both A medians > both C |
|---|---:|---:|---:|---:|---|
| ep-kimi-k3 | 4096 | -2.216 / -2.224 | +2.456 / +2.543 | +0.215 / +0.152 | no |
| ep-kimi-k3 | 8192 | +27.679 / +27.679 | +10.224 / +10.240 | +1.832 / +0.496 | yes |
| ep-v3 | 8192 | +0.224 / +0.216 | +2.632 / +3.824 | +1.496 / +0.096 | no |
| ep-v3 | 16384 | +3.553 / +3.553 | +5.160 / +3.080 | +1.040 / +0.424 | no |
| ep-v41-flash | 8192 | +26.400 / +26.368 | +8.593 / +8.576 | -3.216 / +0.680 | yes |
| ep-v41-flash | 16384 | +12.536 / +12.520 | +7.312 / +7.312 | +0.616 / +0.504 | no |
| tp-kimi-k3 | 8192 | +3.616 / +3.575 | +5.183 / +5.176 | +3.152 / +1.175 | no |
| tp-nemo3-ultra | 16384 | +14.712 / +14.728 | +22.760 / +21.464 | -0.752 / +1.712 | yes |
| tp-v3 | 8192 | -0.256 / -0.232 | -0.672 / +0.952 | -0.655 / +0.488 | no |
| tp-v41-flash | 4096 | +1.024 / +0.856 | -0.184 / -0.288 | +0.952 / +0.336 | no |
| tp-v41-flash | 8192 | +2.008 / +1.929 | +6.017 / +6.256 | +0.056 / +1.648 | no |
| tp-v41-flash | 16384 | +3.968 / +3.984 | +10.000 / +9.513 | +2.928 / +0.825 | no |

All twelve negatives have a repeat spread above 0.5% in at least one arm. That is a limitation, not a rule that discards an observed loss. K3 EP8K, V41F EP8K and N3U TP16K have both candidate medians above both controls and retain adverse cumulative signals.

V41F EP8K is the largest observed loss (−5.565038%). C1/C2 are 708.7075/688.3875 µs; A1/A2 are 725.1235/754.4360 µs. Its only flagged quartile is A2/Q4, median 1425 MHz with reason 0 (11 telemetry samples). A1 has normal clocks in all four observed quartiles and still exceeds both control medians. FC1 and FC2 exposed extensions increase by 26.3683 and 8.5760 µs. Clock variation and phase spread limit a precise stable magnitude, but do not explain away the entire observation.

K3 EP8K (−4.229933%) has a large 8.527% control spread and four clock flags; N3U TP16K (−2.074922%) has 2.233%/0.403% control/candidate spread and eleven flags. Their adverse phase ordering is preserved. No further repeats, rescue selection, source change or GPU work were performed by this peer.

## Group totals

| Group | Cells | GM change % | Negative cells |
|---|---:|---:|---:|
| model: kimi-k3 | 6 | -0.491570 | 3 |
| model: nemo3-ultra | 6 | +0.364616 | 1 |
| model: v3 | 6 | -0.220849 | 3 |
| model: v41-flash | 6 | -1.490033 | 5 |
| topology: ep | 12 | -0.740315 | 6 |
| topology: tp | 12 | -0.182349 | 6 |
| tokens: 4096 | 8 | +0.162000 | 2 |
| tokens: 8192 | 8 | -1.293568 | 6 |
| tokens: 16384 | 8 | -0.247931 | 4 |

Peer JSON SHA256: `b929e4045664d3501096020a7d3ad78a7584bafd753862b1e8a049adc1ae00b1`.
Raw evidence: [data](../evidence/w4-cumulative-prefill/1793414097438305000/data/). Complete native script report: [report](../evidence/w4-cumulative-prefill/1793414097438305000/report/).
