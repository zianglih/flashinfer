# Regular-TMA grid16 AUTO A1 screen

Original B1 is reused unchanged. This is one new A1 screen, not experimental ABBA retention evidence. Tokens1/2 are measured and excluded from every aggregate. Each token value is the unchanged primary helper's median of100 cold-L2 graph CUPTI samples; individual samples are not persisted by that helper.

| Mode | B1/A1 decode | B1/A1 prefill | B1/A1 overall |
|---|---:|---:|---:|
| nvfp4 | 1.052735x | 0.985046x | 1.033826x |
| mxfp8 | 1.086995x | 1.073196x | 1.083214x |
| mxfp4 | 1.182668x | 1.038259x | 1.141401x |

## Complete raw medians

All latencies are µs.442 comparisons below are nonadjacent diagnostics, not paired measurements.

| Mode | Tokens | B1 | Experiment A1 | B1/A1 |442 A1 |442 A2 |442 geometric center / new A1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| nvfp4 | 1 | 27.4395 | 27.7120 | 0.990167x | 25.1520 | 25.3595 | 0.911357x |
| nvfp4 | 2 | 37.1840 | 35.8720 | 1.036574x | 33.0880 | 32.9280 | 0.920158x |
| nvfp4 | 4 | 52.5120 | 49.0880 | 1.069752x | 47.4080 | 47.3920 | 0.965613x |
| nvfp4 | 8 | 69.7920 | 63.5675 | 1.097920x | 63.2960 | 63.4400 | 0.996861x |
| nvfp4 | 16 | 79.2000 | 73.0560 | 1.084100x | 73.6960 | 73.6800 | 1.008651x |
| nvfp4 | 32 | 111.1200 | 105.4240 | 1.054029x | 110.8150 | 111.1680 | 1.052809x |
| nvfp4 | 64 | 143.9990 | 138.9755 | 1.036147x | 139.4400 | 141.3440 | 1.010169x |
| nvfp4 | 128 | 147.6480 | 142.3515 | 1.037207x | 139.5995 | 139.9680 | 0.981961x |
| nvfp4 | 256 | 154.9280 | 151.3280 | 1.023789x | 148.7195 | 148.4630 | 0.981915x |
| nvfp4 | 512 | 157.4080 | 154.0800 | 1.021599x | 150.5280 | 150.6555 | 0.977361x |
| nvfp4 | 4096 | 208.4630 | 205.5035 | 1.014401x | 206.2720 | 205.9515 | 1.002960x |
| nvfp4 | 8192 | 297.4560 | 306.4955 | 0.970507x | 305.3120 | 304.8310 | 0.995354x |
| nvfp4 | 16384 | 472.4635 | 486.6390 | 0.970871x | 532.3510 | 535.3270 | 1.096988x |
| mxfp8 | 1 | 43.5200 | 34.9440 | 1.245421x | 31.7440 | 31.7765 | 0.908890x |
| mxfp8 | 2 | 55.5205 | 49.6640 | 1.117922x | 47.1680 | 47.4560 | 0.952637x |
| mxfp8 | 4 | 81.5840 | 72.0645 | 1.132097x | 70.8800 | 70.9760 | 0.984229x |
| mxfp8 | 8 | 110.2085 | 96.9600 | 1.136639x | 97.6005 | 97.6960 | 1.007098x |
| mxfp8 | 16 | 126.0480 | 113.9525 | 1.106145x | 117.9520 | 118.0000 | 1.035309x |
| mxfp8 | 32 | 182.9450 | 170.7520 | 1.071408x | 167.4245 | 167.5840 | 0.980980x |
| mxfp8 | 64 | 241.7600 | 228.1125 | 1.059828x | 225.4560 | 225.8560 | 0.989231x |
| mxfp8 | 128 | 250.2890 | 234.7040 | 1.066403x | 231.7605 | 231.9370 | 0.987835x |
| mxfp8 | 256 | 266.8810 | 250.2240 | 1.066568x | 245.9365 | 245.7280 | 0.982449x |
| mxfp8 | 512 | 268.4000 | 253.1520 | 1.060233x | 248.8645 | 249.1530 | 0.983633x |
| mxfp8 | 4096 | 359.6170 | 326.8320 | 1.100311x | 320.8325 | 323.2165 | 0.985284x |
| mxfp8 | 8192 | 536.5930 | 492.4810 | 1.089571x | 478.2885 | 466.7210 | 0.959366x |
| mxfp8 | 16384 | 857.8740 | 832.0660 | 1.031017x | 827.4730 | 830.1460 | 0.996085x |
| mxfp4 | 1 | 40.8960 | 31.7760 | 1.287009x | 28.0960 | 28.1600 | 0.885196x |
| mxfp4 | 2 | 51.2000 | 37.0240 | 1.382887x | 37.1520 | 37.3120 | 1.005616x |
| mxfp4 | 4 | 65.4400 | 52.6720 | 1.242406x | 56.0320 | 55.9680 | 1.063183x |
| mxfp4 | 8 | 85.7280 | 69.3600 | 1.235986x | 74.6560 | 74.6560 | 1.076355x |
| mxfp4 | 16 | 90.6410 | 76.4645 | 1.185400x | 84.6405 | 84.5760 | 1.106504x |
| mxfp4 | 32 | 133.8725 | 112.6725 | 1.188156x | 112.0640 | 111.9040 | 0.993889x |
| mxfp4 | 64 | 169.4725 | 149.4085 | 1.134290x | 149.1685 | 149.2160 | 0.998553x |
| mxfp4 | 128 | 177.8250 | 153.0250 | 1.162065x | 153.0080 | 153.0560 | 1.000046x |
| mxfp4 | 256 | 185.6490 | 159.8565 | 1.161348x | 159.8880 | 160.4645 | 1.001999x |
| mxfp4 | 512 | 188.3690 | 162.9440 | 1.156035x | 162.7685 | 162.8005 | 0.999021x |
| mxfp4 | 4096 | 303.2810 | 267.6170 | 1.133265x | 270.4970 | 270.5290 | 1.010821x |
| mxfp4 | 8192 | 461.1210 | 439.9040 | 1.048231x | 437.7770 | 438.9290 | 0.996473x |
| mxfp4 | 16384 | 776.0020 | 823.6335 | 0.942169x | 816.4815 | 780.3530 | 0.969136x |

## Nonadjacent442 diagnostic aggregates

| Mode | Decode | Prefill | Overall |
|---|---:|---:|---:|
| nvfp4 | 0.996594x | 1.030752x | 1.005796x |
| mxfp8 | 0.993694x | 0.980123x | 0.989975x |
| mxfp4 | 1.029108x | 0.991992x | 1.018850x |

Ratios greater than1 favor the experiment. Aggregates are geometric means over decode4–512, prefill4096/8192/16384, and overall all11 included token points. The442 center is the geometric mean of its saved A1/A2 median for each token. Its A1/new and A2/new ratios are also retained separately in summary.json.

## Provenance

`fetch-receipt.json` pins all62 fetched files and the archive bytes; raw.tar.gz preserves them. The actual three source files, full11,665-source manifest, unchanged-loop proof, observer scripts, launchscript, preflight, postflight, complete raw logs and all39 AUTO caches are included. The final independent review is in local-evidence. Original B1/B2 files were neither rerun nor changed; no experimental A2 has been launched.
