# SF coordinate-cache 56-cell screen: independent raw peer

**Factual audit passed; recommend rejecting this primary candidate.** The full matrix is neutral overall, with a tight normal-clock FC1 regression in N3U TP W4A4 at 16K. The added shared coordinate cache, loads and synchronization have not established a general benefit. No row, phase, clock observation or negative result was replaced.

Replayed 23 complete CAAC jobs, all 22,400 CUPTI spans, 224 phase medians, all component samples, 896 NVML quartiles and 448 loaded resource records. Frozen route identities, exact winning tactics, timer/quantization contracts, full source inventories and the adopted release cohort (`moe_utils` `046552b8`) join throughout. Source/native-cache no-op and eight-GPU idle closure pass. Prior-cohort pilot records are excluded.

| Group | Cells | Negative | Geometric-mean change |
|---|---:|---:|---:|
| band/all | 56 | 33 | -0.014834% |
| band/decode | 28 | 20 | -0.128760% |
| band/prefill | 28 | 13 | +0.099222% |
| mode/CuteDSL MXFP4x8 | 14 | 10 | -1.006288% |
| mode/CuteDSL PER-TOKEN | 16 | 8 | +0.903622% |
| mode/CuteDSL W4A4 | 16 | 9 | +0.193526% |
| mode/CuteDSL MXFP8 | 10 | 6 | -0.414918% |
| model_topology/kimi-k3/ep | 6 | 6 | -2.756057% |
| model_topology/nemo3-ultra/ep | 8 | 4 | +0.466346% |
| model_topology/v3/ep | 8 | 4 | +1.343749% |
| model_topology/v41-flash/ep | 8 | 4 | +1.201814% |
| model_topology/kimi-k3/tp | 6 | 5 | -0.752087% |
| model_topology/nemo3-ultra/tp | 8 | 5 | -0.898738% |
| model_topology/v3/tp | 8 | 4 | +0.046131% |
| model_topology/v41-flash/tp | 4 | 1 | +0.844306% |

All 33 negative cells remain; 21 have both repeat spreads at most 0.5%. There are 56 clock-exception quartiles and zero missing observations. Exceptions mean a quartile median SM clock differs from 2032 MHz or its reason codes include a nonzero value; full raw minima/maxima and reasons remain in the evidence. Small tight negatives are not automatically material; the strongest normal-clock loss is large and attributable to FC1 duration in this screen.

**N3U TP W4A4, 16K:** control phase medians 1136.3145 / 1136.0740 µs; candidate 1192.0590 / 1192.0900 µs. Speed change −4.687648%; repeat spreads 0.021169% / 0.002601%. Every one of its 16 clock windows has min/median/max 2032 MHz and reason 0. FC1 duration grows 55.6485 µs and exposed extension grows 55.7205 µs; FC2 extension changes −0.4075 µs and combine +0.01625 µs. These independently calculated component medians need not sum exactly to the E2E median.

Its FC1 remains N256 / logical stage K256 / native MMA K96 / one CTA / four stages / static / PDL on, with 168 registers, LOCAL0 and driver capacity one. Dynamic shared allocation rises 222,208→223,232 bytes. FC2 geometry and resources remain equal. This locates the adverse timing in FC1, but does not prove a particular LDS/bank mechanism without a separate diagnostic.

Across all 112 cross-arm stage pairs, registers, launch limits, LOCAL0, stage counts, native geometry and driver CTA capacity are equal. Exactly 34 FC1 pairs gain 128–1024 dynamic shared bytes; the other 78 pairs are unchanged. Every allocation increase was independently reconciled with the unchanged layout and operand alignment. Driver capacity is not a sampled residency trace. Representative native instruction reductions do not override this full runtime result.

Every negative row follows. Component entries are candidate minus control in microseconds; the JSON preserves full phase/component records and all resource joins.

| Job / backend | Tokens | Change % | Repeat C/A % | FC1 duration Δ | FC1 extension Δ | FC2 extension Δ | Combine extension Δ | Clock medians / reasons |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| ep-kimi-k3-mxfp / CuteDSL MXFP4x8 | 16384 | -8.445850 | 1.7369/6.2536 | +117.4163 | +117.3523 | -17.6890 | -2.4400 | 1777,2010,2032 / 0 |
| ep-nemo3-ultra-mxfp / CuteDSL MXFP8 | 16384 | -5.038125 | 7.2480/0.4433 | +39.4883 | +39.4803 | +3.8405 | +0.5437 | 2032 / 0 |
| tp-nemo3-ultra-w4a4 / CuteDSL W4A4 | 16384 | -4.687648 | 0.0212/0.0026 | +55.6485 | +55.7205 | -0.4075 | +0.0163 | 2032 / 0 |
| ep-kimi-k3-w4a4 / CuteDSL W4A4 | 16384 | -4.209884 | 2.2114/0.9216 | +25.8077 | +25.7917 | +6.8480 | +1.0482 | 1597,1702,2032 / 0,4 |
| tp-kimi-k3-mxfp / CuteDSL MXFP4x8 | 16384 | -3.823423 | 2.2868/1.8841 | +120.1293 | +120.1930 | -50.6723 | -2.3438 | 1485,1590,1642,1680,2025,2032 / 0,4 |
| ep-kimi-k3-per-token / CuteDSL PER-TOKEN | 16384 | -3.023414 | 3.6015/0.5085 | +26.1125 | +26.1360 | +2.0955 | +0.1837 | 1927,2032 / 0,4 |
| tp-nemo3-ultra-mxfp / CuteDSL MXFP4x8 | 16384 | -2.837042 | 0.1541/1.1691 | +53.1442 | +53.1442 | -13.8963 | -1.4405 | 1695,1732,1912,2032 / 0,4 |
| tp-kimi-k3-w4a4 / CuteDSL W4A4 | 16384 | -1.608823 | 0.0471/0.0836 | +24.3125 | +24.3445 | -2.4645 | +0.0792 | 2025,2032 / 0 |
| tp-nemo3-ultra-mxfp / CuteDSL MXFP8 | 16384 | -1.147105 | 0.0074/0.8396 | +43.5202 | +43.8240 | -23.4800 | -1.2482 | 1590,1635,1785,1995,2032 / 0,4 |
| tp-v3-mxfp / CuteDSL MXFP4x8 | 16384 | -1.076127 | 0.1695/0.6991 | +16.6233 | +16.6312 | -3.1842 | +0.1200 | 1957,1987,2032 / 0,4 |
| ep-v3-per-token / CuteDSL PER-TOKEN | 32 | -0.837605 | 0.0297/0.1198 | +0.8080 | +0.7995 | -0.0155 | +0.0000 | 2032 / 0 |
| ep-nemo3-ultra-mxfp / CuteDSL MXFP4x8 | 16384 | -0.785917 | 3.0229/3.5824 | +24.9768 | +24.7448 | -13.8485 | -1.6568 | 2032 / 0,4 |
| tp-nemo3-ultra-per-token / CuteDSL PER-TOKEN | 32 | -0.669917 | 0.2209/0.6085 | +0.4560 | +0.4483 | +0.3600 | -0.0480 | 2032 / 0 |
| tp-kimi-k3-per-token / CuteDSL PER-TOKEN | 32 | -0.639497 | 0.0181/0.1081 | +1.0962 | +1.0960 | +0.0078 | +0.0160 | 2032 / 0 |
| tp-kimi-k3-w4a4 / CuteDSL W4A4 | 32 | -0.500911 | 0.0095/0.0287 | +1.0562 | +1.0480 | -0.1195 | +0.0000 | 2032 / 0 |
| ep-v41-flash-mxfp / CuteDSL MXFP8 | 16384 | -0.479045 | 0.8159/0.0415 | +6.9203 | +6.9363 | -0.2248 | +0.9843 | 1447,1477,2002,2017,2032 / 0,4 |
| tp-kimi-k3-mxfp / CuteDSL MXFP4x8 | 32 | -0.386025 | 0.0096/0.2080 | +0.5840 | +0.5837 | +0.1275 | -0.0397 | 2032 / 0 |
| ep-kimi-k3-mxfp / CuteDSL MXFP4x8 | 32 | -0.380921 | 0.0771/0.0190 | +0.5357 | +0.5438 | +0.0477 | -0.0155 | 2032 / 0 |
| tp-v3-mxfp / CuteDSL MXFP8 | 16384 | -0.309348 | 0.8737/0.2884 | +12.2240 | +12.2565 | -3.4635 | -0.4000 | 1732,1747,1770,1957,2032 / 0,4 |
| ep-v41-flash-w4a4 / CuteDSL W4A4 | 32 | -0.280878 | 0.1015/0.0000 | +0.0880 | +0.0718 | -0.0563 | +0.0000 | 2032 / 0 |
| tp-nemo3-ultra-w4a4 / CuteDSL W4A4 | 32 | -0.199665 | 0.1931/0.1794 | +0.0720 | +0.0880 | -0.0872 | +0.0003 | 2032 / 0 |
| ep-kimi-k3-per-token / CuteDSL PER-TOKEN | 32 | -0.137017 | 0.0715/0.0091 | +0.0720 | +0.0640 | -0.0243 | +0.0002 | 2032 / 0 |
| tp-v3-per-token / CuteDSL PER-TOKEN | 32 | -0.124176 | 0.1511/0.0133 | +0.1930 | +0.1925 | +0.0483 | +0.0153 | 2032 / 0 |
| ep-v3-mxfp / CuteDSL MXFP4x8 | 32 | -0.065962 | 0.1646/0.0325 | +0.0160 | +0.0237 | +0.0080 | +0.0160 | 2032 / 0 |
| ep-kimi-k3-w4a4 / CuteDSL W4A4 | 32 | -0.054629 | 0.0730/0.1463 | +0.1840 | +0.1760 | -0.0560 | +0.0078 | 2032 / 0 |
| ep-v41-flash-mxfp / CuteDSL MXFP8 | 32 | -0.026413 | 0.0531/0.0306 | +0.1997 | +0.2158 | +0.2240 | -0.0078 | 2032 / 0 |
| ep-nemo3-ultra-w4a4 / CuteDSL W4A4 | 32 | -0.023158 | 0.0314/0.1087 | +0.0003 | -0.0002 | +0.0327 | +0.0083 | 2032 / 0 |
| tp-v41-flash-per-token / CuteDSL PER-TOKEN | 32 | -0.021613 | 0.0659/0.0886 | +0.0160 | +0.0163 | +0.1035 | +0.0245 | 2032 / 0 |
| ep-v3-mxfp / CuteDSL MXFP8 | 32 | -0.019873 | 0.0590/0.0193 | +0.0405 | +0.0562 | -0.0155 | +0.0000 | 2032 / 0 |
| ep-v41-flash-per-token / CuteDSL PER-TOKEN | 32 | -0.017812 | 0.0245/0.0609 | -0.0242 | -0.0480 | -0.0478 | +0.0000 | 2032 / 0 |
| tp-v3-mxfp / CuteDSL MXFP4x8 | 32 | -0.015863 | 0.0005/0.2169 | +0.1283 | +0.1360 | -0.1363 | -0.0080 | 2032 / 0 |
| ep-v3-w4a4 / CuteDSL W4A4 | 32 | -0.015822 | 0.0322/0.0005 | +0.0245 | +0.0247 | -0.1603 | +0.0157 | 2032 / 0 |
| ep-nemo3-ultra-mxfp / CuteDSL MXFP4x8 | 32 | -0.000010 | 0.0960/0.0323 | +0.0882 | +0.0958 | -0.0080 | -0.0160 | 2032 / 0 |

Sealed peer: [sf-coordinate-cache-data-peer.json](sf-coordinate-cache-data-peer.json), SHA `2fa029d41d008c9ab5bb6790a077d900e9aa52862b086d7abc71ac71ed68e3a9`. Replayer: [audit_sf_coordinate_cache_data.py](audit_sf_coordinate_cache_data.py). Raw archive SHA `c096d1bb95a7e93cda809306df897214532346ade97365dc37a162d854d7d422`. No source, GPU, cache or original evidence mutation by this audit.
