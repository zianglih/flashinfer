# Independent final screen review

**Recommendation: retain as synchronization and instruction cleanup.** The complete fixed-tactic screen is effectively neutral. Do not describe the 1.000965× aggregate as a meaningful end-to-end speedup. The worst measured prefill regression is +0.718% latency, and the worst decode regression is +0.0563%, consistent with the user’s explicit allowance for slight prefill regressions and cleanup without visible timing gains.

Candidate patch `b4fb9c7a20b216839f4e879b9b576df098d64a10ece2816bbd350f2dafb3223a` against fresh clean `9334cb34fe9c81653dc4748632f44449e9aecd8d` controls. The final source-bound gate passes 120 replay comparisons per source and 60 compiled core pairs, without spills. The codegen summary reports −1049 static instructions summed across compiled variants, not a dynamic instruction total; registers range from −8 to +3. This recommendation uses the synchronization proof and reduced redundant operations, not an isolated claimed contribution from any component.

## Independent checks

- Verified all 260 collected artifact hashes and the final gate’s source identity. Only the three reviewed source files differ.
- Verified all 36 CAAC processes are fresh, completed, and bound to the same GPU per model/family. There are 192 measurements and exactly 19,200 positive finite raw timing samples; every public latency equals its 100-sample median. The frozen observer enforces 10 warmups, cold L2, CUPTI and CUDA graphs.
- Routing tensors, route weights and expert histograms match across all four passes for every cell. Observed five-field shared-CLC tactics and cache keys match across passes and the saved cache entries; no search/admission occurs.
- The complete 3-model × 4-format × 4-token grid is present. V3/K3 use EP8; V41 uses EP4; all use TP1. NV includes initial quantization; MX uses prequantized input. Fused finalize, TRTLLM and W4A16 are not timed.
- Recomputed every cell as `sqrt(C0*C3/(A1*A2))` from raw medians and independently matched the published aggregation. No cells were dropped. Tokens 1 and 2 are absent from this diagnostic screen.

## Geometric speedup versus clean 9334

| Model | Format | Decode (32,128) | Prefill (4096,16384) | All four |
| --- | --- | ---: | ---: | ---: |
| v3 | W4A4 | 1.000628× | 1.000886× | 1.000757× |
| v3 | PER-TOKEN | 1.000247× | 1.003498× | 1.001871× |
| v3 | MXFP4x8 | 1.000775× | 0.997306× | 0.999039× |
| v3 | MXFP8 | 1.000534× | 1.006978× | 1.003751× |
| v41-flash | W4A4 | 1.000420× | 1.003674× | 1.002046× |
| v41-flash | PER-TOKEN | 1.000195× | 0.999673× | 0.999934× |
| v41-flash | MXFP4x8 | 1.000136× | 1.007737× | 1.003929× |
| v41-flash | MXFP8 | 1.000079× | 0.998728× | 0.999403× |
| kimi-k3 | W4A4 | 1.001578× | 0.997093× | 0.999333× |
| kimi-k3 | PER-TOKEN | 1.000387× | 1.001463× | 1.000925× |
| kimi-k3 | MXFP4x8 | 1.002758× | 0.999910× | 1.001333× |
| kimi-k3 | MXFP8 | 1.000166× | 0.998375× | 0.999270× |

All 48 cells: **1.000965×**; 24 decode cells: **1.000658×**; 24 prefill cells: **1.001271×**.

## Worst observed points

| Model | Format | Tokens | Speedup | Latency change | Control C0→C3 | Candidate A1→A2 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| v3 | MXFP4x8 | 16384 | 0.992868× | +0.718% | -0.803% | +3.758% |
| kimi-k3 | W4A4 | 16384 | 0.994914× | +0.511% | +1.853% | -4.166% |
| kimi-k3 | MXFP8 | 16384 | 0.996179× | +0.384% | -2.042% | -1.198% |
| v41-flash | MXFP8 | 16384 | 0.996506× | +0.351% | -0.538% | -0.139% |
| kimi-k3 | PER-TOKEN | 4096 | 0.997535× | +0.247% | +0.173% | +0.090% |

The largest negative points also exhibit inter-pass variation: V3 MXFP4x8 T16384 has +3.758% candidate pass drift, and K3 W4A4 T16384 has −4.166%. This limits causal interpretation of sub-percent point changes; it does not justify dropping them. All remain in aggregation. Small raw-sample distributions are repeated graph measurements, not independent full-campaign replicates, so no statistical significance is claimed.

## All paired medians

Times are milliseconds; columns retain actual C–A–A–C order.

| Model | Format | Tokens | C0 | A1 | A2 | C3 | Speedup |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v3 | W4A4 | 32 | 0.1014405 | 0.1013285 | 0.1014570 | 0.1015050 | 1.000789× |
| v3 | W4A4 | 128 | 0.1380330 | 0.1380965 | 0.1380165 | 0.1382090 | 1.000467× |
| v3 | W4A4 | 4096 | 0.2075210 | 0.2079215 | 0.2082095 | 0.2080810 | 0.998728× |
| v3 | W4A4 | 16384 | 0.5252990 | 0.5248675 | 0.5241795 | 0.5269470 | 1.003048× |
| v3 | PER-TOKEN | 32 | 0.1058885 | 0.1057290 | 0.1057605 | 0.1058245 | 1.001057× |
| v3 | PER-TOKEN | 128 | 0.1427525 | 0.1426890 | 0.1427210 | 0.1424970 | 0.999437× |
| v3 | PER-TOKEN | 4096 | 0.2506250 | 0.2514415 | 0.2509450 | 0.2515695 | 0.999617× |
| v3 | PER-TOKEN | 16384 | 0.6789635 | 0.6730760 | 0.6724845 | 0.6765485 | 1.007394× |
| v3 | MXFP8 | 32 | 0.1656650 | 0.1653935 | 0.1654890 | 0.1656170 | 1.001207× |
| v3 | MXFP4x8 | 32 | 0.1001285 | 0.0999850 | 0.1002090 | 0.1000805 | 1.000076× |
| v3 | MXFP8 | 128 | 0.2263540 | 0.2263370 | 0.2263215 | 0.2262420 | 0.999862× |
| v3 | MXFP4x8 | 128 | 0.1359050 | 0.1356650 | 0.1356970 | 0.1358570 | 1.001474× |
| v3 | MXFP8 | 4096 | 0.3053940 | 0.3048185 | 0.3049460 | 0.3053305 | 1.001574× |
| v3 | MXFP4x8 | 4096 | 0.2271210 | 0.2268815 | 0.2265935 | 0.2271535 | 1.001763× |
| v3 | MXFP8 | 16384 | 0.7451565 | 0.7811400 | 0.7429480 | 0.7982765 | 1.012411× |
| v3 | MXFP4x8 | 16384 | 0.7051565 | 0.6944365 | 0.7205315 | 0.6994930 | 0.992868× |
| v41-flash | W4A4 | 32 | 0.1261935 | 0.1260165 | 0.1262410 | 0.1261610 | 1.000385× |
| v41-flash | W4A4 | 128 | 0.2633135 | 0.2630260 | 0.2630740 | 0.2630260 | 1.000455× |
| v41-flash | W4A4 | 4096 | 0.3517625 | 0.3524180 | 0.3524820 | 0.3517780 | 0.998071× |
| v41-flash | W4A4 | 16384 | 0.6566440 | 0.6514285 | 0.6529490 | 0.6598770 | 1.009307× |
| v41-flash | PER-TOKEN | 32 | 0.1322885 | 0.1323685 | 0.1321455 | 0.1323050 | 1.000301× |
| v41-flash | PER-TOKEN | 128 | 0.2731540 | 0.2732175 | 0.2733620 | 0.2734740 | 1.000089× |
| v41-flash | PER-TOKEN | 4096 | 0.4062910 | 0.4067555 | 0.4066915 | 0.4062110 | 0.998838× |
| v41-flash | PER-TOKEN | 16384 | 0.8000375 | 0.7998455 | 0.8040065 | 0.8046305 | 1.000508× |
| v41-flash | MXFP8 | 32 | 0.2135535 | 0.2133610 | 0.2137615 | 0.2133930 | 0.999588× |
| v41-flash | MXFP4x8 | 32 | 0.1226405 | 0.1226250 | 0.1226250 | 0.1227530 | 1.000585× |
| v41-flash | MXFP8 | 128 | 0.4624990 | 0.4624190 | 0.4624670 | 0.4629150 | 1.000571× |
| v41-flash | MXFP4x8 | 128 | 0.2552810 | 0.2553450 | 0.2554260 | 0.2553300 | 0.999687× |
| v41-flash | MXFP8 | 4096 | 0.5871400 | 0.5865480 | 0.5866755 | 0.5872040 | 1.000955× |
| v41-flash | MXFP4x8 | 4096 | 0.3569305 | 0.3570905 | 0.3569620 | 0.3570105 | 0.999844× |
| v41-flash | MXFP8 | 16384 | 1.0030790 | 1.0045830 | 1.0031905 | 0.9976860 | 0.996506× |
| v41-flash | MXFP4x8 | 16384 | 0.8900540 | 0.8620695 | 0.8754940 | 0.8747900 | 1.015693× |
| kimi-k3 | W4A4 | 32 | 0.1771530 | 0.1763850 | 0.1766560 | 0.1768330 | 1.002677× |
| kimi-k3 | W4A4 | 128 | 0.2971045 | 0.2969135 | 0.2970100 | 0.2971050 | 1.000482× |
| kimi-k3 | W4A4 | 4096 | 0.3870090 | 0.3873460 | 0.3874890 | 0.3872655 | 0.999277× |
| kimi-k3 | W4A4 | 16384 | 0.7961790 | 0.8249960 | 0.7906275 | 0.8109315 | 0.994914× |
| kimi-k3 | PER-TOKEN | 32 | 0.1822570 | 0.1819690 | 0.1821285 | 0.1821610 | 1.000880× |
| kimi-k3 | PER-TOKEN | 128 | 0.3066090 | 0.3066570 | 0.3068020 | 0.3067850 | 0.999894× |
| kimi-k3 | PER-TOKEN | 4096 | 0.4435530 | 0.4448340 | 0.4452340 | 0.4443210 | 0.997535× |
| kimi-k3 | PER-TOKEN | 16384 | 1.0997160 | 1.0906610 | 1.1060680 | 1.1088525 | 1.005406× |
| kimi-k3 | MXFP8 | 32 | 0.3001600 | 0.3009445 | 0.3001930 | 0.3009920 | 1.000024× |
| kimi-k3 | MXFP4x8 | 32 | 0.1722405 | 0.1716485 | 0.1716965 | 0.1722250 | 1.003263× |
| kimi-k3 | MXFP8 | 128 | 0.5212175 | 0.5211700 | 0.5210730 | 0.5213460 | 1.000308× |
| kimi-k3 | MXFP4x8 | 128 | 0.2921610 | 0.2916325 | 0.2913930 | 0.2921775 | 1.002252× |
| kimi-k3 | MXFP8 | 4096 | 0.6511695 | 0.6515540 | 0.6511695 | 0.6523060 | 1.000577× |
| kimi-k3 | MXFP4x8 | 4096 | 0.3992485 | 0.3981450 | 0.3995695 | 0.3986420 | 1.000222× |
| kimi-k3 | MXFP8 | 16384 | 1.3805320 | 1.3798920 | 1.3633650 | 1.3523385 | 0.996179× |
| kimi-k3 | MXFP4x8 | 16384 | 1.1658590 | 1.1434120 | 1.1016670 | 1.0795870 | 0.999598× |

This is a fixed-policy diagnostic, not a new AUTO search or refreshed TRTLLM comparison. No additional GPU run was launched during this independent review. [Machine-readable review](independent-screen-review.json) pins provenance and per-pass raw-sample ranges. Reproduce with `python3 scripts/sync_audit_20261027/composed/independent_screen_review.py`.

Final emitted-code cross-check also passes all 60 cores: barrier2 is removed exactly once; barrier1 participant counts, TMEM completion fences, permit/deallocation, UMMA commit, CLC query and bulk-read wait site counts are preserved. The representative final guard directly tests the warp index and exits nonzero warps after the full-CTA completion join. All four wide standard/per-token PDL combinations retain the delayed reuse join after both TMEM loads; their per-issuer DEPBAR stays early. Details: [terminal/bulk codegen receipt](independent-terminal-bulk-codegen.json).
