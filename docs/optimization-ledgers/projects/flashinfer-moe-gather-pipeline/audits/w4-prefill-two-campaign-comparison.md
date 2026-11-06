# Two W4 prefill cells: isolated helper versus cumulative branch

Receipt and replayer: [JSON](w4-prefill-two-campaign-comparison.json), [compare_w4_prefill_campaigns.py](compare_w4_prefill_campaigns.py). All 1,600 selected raw spans were rechecked, along with hashes and raw telemetry; original campaigns remain separate.

| Cell / campaign | C1 µs | A1 µs | A2 µs | C2 µs | Paired speedup | Repeat C / A % | Clock flags |
|---|---:|---:|---:|---:|---:|---:|---:|
| ep-v41-flash T8192 / 822→02de | 686.6610 | 696.7730 | 727.0455 | 728.3095 | -0.642026% | 6.065 / 4.345 | 0/16 |
| ep-v41-flash T8192 / 822→c1ac | 708.7075 | 725.1235 | 754.4360 | 688.3875 | -5.565038% | 2.952 / 4.042 | 1/16 |
| tp-nemo3-ultra T16384 / 822→02de | 1957.8330 | 1940.5220 | 1960.7290 | 1966.6020 | +0.595369% | 0.448 / 1.041 | 10/16 |
| tp-nemo3-ultra T16384 / 822→c1ac | 1848.5470 | 1863.2360 | 1870.7395 | 1808.1670 | -2.074922% | 2.233 / 0.403 | 11/16 |

Actual choices, activation cache keys, routes/histograms, BF16-input contracts, native geometry and captured driver resource records are **identical in all eight phases per cell**. Both stages use 2-CTA clusters, raster-along-M and PDL; FC1 uses CLC and FC2 is static; max-active-clusters is 74. FC1/FC2 initial registers are 96/128, LOCAL is zero. No timed PTX/cubin/SASS image is present in either performance receipt.

| Cell | Activation and routing | Actual FC1 shape M,N,K | Actual FC2 shape M,N,K | FC1 and FC2 tactic |
|---|---|---|---|---|
| V41F EP4 T8192 | SwiGLU, limit10, alpha1/beta0; 384 experts,96 local,top6; BF16 input | 4608,67392,5120 | 5120,67392,2304 | Explicit [256,192,256], cluster[2,1] |
| N3U TP8 T16384 | ReLU²; 512 experts,top22; BF16 input | 640,425472,2048 | 2048,425472,640 | Recorded default−1 resolves to [256,128,256], cluster[2,1] |

V41F has aligned consumed K in both stages (5120 and2304 divisible by256), and its activation is not SiTU. The [owner’s separate specialization audit](w4-prefill-source-attribution.md) narrows the effective changed path to the FC1 selector; the regular FC2 uses fragment32 and the selector expression is unchanged at its byte index. N3U FC1 is alignedK2048 and its regular FC2 has partialK640, so FC2 includes the retained tail skip/cutoff changes. SiTU is inactive in both models. This source reasoning does not establish cross-source native binary identity; that would require actual matched code images.

V41F isolated02de has normal2032MHz/reason0 in all16 quartiles, but large repeat spreads and interleaved phase ordering. Current cumulative V41F has both candidate medians above both controls; its only flag is A2/Q4 (median1425MHz, reason0,11 samples). A1 is normal in every observed quartile and remains slower than both controls. Thus the current adverse signal remains; the single clock flag cannot dismiss it.

N3U isolated02de has10 flagged quartiles (phase counts2/2/4/2; minima1327/1320/1297/1320MHz). Current cumulative has11 (3/3/1/4; minima1372/1357/1357/1365MHz). Both current candidate medians exceed both current controls. The old nominal improvement and current loss cannot isolate which retained change caused the difference.

## Component deltas

Each entry is candidate minus control in µs, using the arithmetic mean of two phase component medians. Duration / exposed extension are separate; medians need not add to geometric-mean E2E.

| Cell / campaign | FC1 duration / extension | FC2 duration / extension | Combine duration / extension |
|---|---:|---:|---:|
| ep-v41-flash / 822→02de | +3.3845 / +3.3755 | -0.5920 / -0.0328 | -0.9682 / +0.1118 |
| ep-v41-flash / 822→c1ac | +26.4002 / +26.3682 | +8.5925 / +8.5760 | -3.2160 / +0.6800 |
| tp-nemo3-ultra / 822→02de | -10.5037 / -10.4958 | -0.1435 / +0.3680 | -0.0795 / -0.0958 |
| tp-nemo3-ultra / 822→c1ac | +14.7118 / +14.7277 | +22.7603 / +21.4640 | -0.7523 / +1.7120 |

The old campaign used routing94cd8afa/moe_utils91ef42f6; the current one uses routing88e6a970/moe_utils046552b8. V41F moved from physical GPU UUIDbab88130 toee4aef4a; N3U moved from14d73137 to4b2b2158. Each comparison is internally paired, but runtime cohort and devices differ between comparisons. **Do not add/subtract their ratios or label the difference a later-commit regression.**

Sources: [isolated02de evidence](../evidence/w4-initial-selector-prefill/1793388462716534000/data/), [cumulativec1ac evidence](../evidence/w4-cumulative-prefill/1793414097438305000/data/).

JSON SHA256: `dc79b2cff812ad291e19a6a652d0e5d619bfbf87173bb672fbc6358ee03cd4f8`.
