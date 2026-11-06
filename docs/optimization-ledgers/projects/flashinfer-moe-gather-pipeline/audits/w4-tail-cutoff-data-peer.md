# W4 tail-cutoff independent primary-data audit

Passed: 15,600 raw CUPTI spans, 156 phase medians,39 cells/33 retention cells. Retention excludes tokens1/2. Source `2b8eb9d8` versus sole W4 delta `cbef9186`; every recorded choice and route is preserved. Actual compiled-library joins match all78 cell-stage configurations across312 joins;144 loaded native functions have zero local memory. All5 recorded-default cells resolve identically in both arms (40 stage joins). Native release ELF/Ninja bytes match the current recovery cohort before/after.

| Scope | Geomean change |
|---|---:|
| Retention33 | +0.158546% |
| decode | +0.422361% |
| middle | +0.338798% |
| prefill | -0.458745% |
| tp-kimi-k3-w4a16 | -0.089643% |
| tp-nemo3-ultra-w4a16 | +0.478429% |
| tp-v41-flash-w4a16 | +0.087696% |

All11 raw negative rows are below;3 token1/2 rows are excluded from retention. All15 decode cells are positive. Prefill has7/9 negatives. There are 55/624 exceptional quartile windows and no missing windows. A clock flag means median SM clock differs from2032 MHz or the sampled clock-reason mask is nonzero; it is an observation, not a causal attribution.

| Model TP | Tokens | C1 / A1 / A2 / C2 (µs) | Change | C / A repeat spread | Clock flags |
|---|---:|---|---:|---|---|
| kimi-k3 | 1* | 26.3365 / 26.3680 / 26.4000 / 26.3040 | -0.2416% | 0.124% / 0.121% | None |
| kimi-k3 | 2* | 37.8240 / 37.9840 / 37.8885 / 37.7925 | -0.3373% | 0.083% / 0.252% | None |
| kimi-k3 | 256 | 372.4820 / 372.6260 / 372.8340 / 372.8180 | -0.0215% | 0.090% / 0.056% | None |
| kimi-k3 | 4096 | 690.9005 / 701.2830 / 684.2910 / 681.7630 | -0.9265% | 1.340% / 2.483% | 3 windows; 1-candidate,3-control; medians 1852–1987 MHz; masks 0 |
| kimi-k3 | 8192 | 1302.8085 / 1273.7665 / 1286.7905 / 1238.9660 | -0.7636% | 5.153% / 1.022% | 5 windows; 0-control,1-candidate,2-candidate,3-control; medians 1605–2032 MHz; masks 0,4 |
| kimi-k3 | 16384 | 2456.4015 / 2427.9795 / 2457.9320 / 2418.5085 | -0.2263% | 1.567% / 1.234% | 16 windows; 0-control,1-candidate,2-candidate,3-control; medians 1297–2032 MHz; masks 0,4 |
| nemo3-ultra | 4096 | 540.9160 / 541.0270 / 542.9950 / 541.1400 | -0.1812% | 0.041% / 0.364% | None |
| nemo3-ultra | 16384 | 1957.7280 / 1963.4990 / 1959.2120 / 1930.1240 | -0.8911% | 1.430% / 0.219% | 12 windows; 0-control,1-candidate,2-candidate,3-control; medians 1305–2032 MHz; masks 0,4 |
| v41-flash | 2* | 28.6240 / 28.6245 / 28.6730 / 28.6080 | -0.1143% | 0.056% / 0.169% | None |
| v41-flash | 4096 | 550.8190 / 572.8030 / 557.8590 / 552.9790 | -2.3676% | 0.392% / 2.679% | 1 windows; 0-control; medians 2032–2032 MHz; masks 0,4 |
| v41-flash | 8192 | 1022.9335 / 1014.3410 / 1005.5090 / 989.6530 | -0.3723% | 3.363% / 0.878% | 3 windows; 0-control,3-control; medians 1500–1560 MHz; masks 0,4 |

*Tokens1/2 excluded from retention. Repeat spread is100×(max phase median/min phase median−1). Change is100×(sqrt(C1×C2/A1/A2)−1); positive means faster. All100 samples per phase are kept. The primary39 remains unmodified; any later ACCA is separate diagnostic evidence and is not pooled or substituted.

V41F TP4096 and N3U TP16384 both have each candidate phase above each control phase. V41F has2.679% candidate repeat spread; N3U has1.430% control spread and12 flagged quartiles. These are negative primary observations with variation, not proven isolated math or clock regressions. The unchanged FC1 source/native specialization can still have shifted spans through overlap or clocks; the audit does not attribute that shift to a cause.

Evidence: `evidence/w4-tail-cutoff-screen/1793393742504067000/{data,report}`. Reproducible replay: `python3 audits/audit_w4_tail_cutoff_data.py evidence/w4-tail-cutoff-screen/1793393742504067000`. `w4-tail-cutoff-data-peer.json` preserves every cell, all clock exceptions and source/archive/config hashes. No GPU work or source/timing edits were performed by this audit.
