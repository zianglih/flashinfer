# Initial K3 EP MXFP4x8 16K diagnosis

Both losses remain unresolved. All 800 timed samples and 32 observed clock quartiles are preserved; no sample filtering or clock normalization was applied.

| Variant | Full CAAC change | C spread | A spread | FC1 exposed extension delta | FC2 exposed extension delta | Combine extension delta |
|---|---:|---:|---:|---:|---:|---:|
| writer-r1 | -4.463% | 3.512% | 0.022% | +33.560 us | +11.456 us | +1.440 us |
| static-sf | -3.557% | 5.336% | 3.237% | +19.488 us | +15.537 us | +2.352 us |

The component deltas use arithmetic means of each arm's two phase component medians, for attribution only. The full CAAC ratio remains geometric. Component medians need not add to the median end-to-end duration, and raw overlapping kernel durations are not summed.

R1 changes the FC2 bulk epilogue only, but most of its measured loss appears in FC1's exposed extension. This is a useful inconsistency to diagnose, not proof the loss is harmless. The exact native FC1 cubin was not captured by the original gate; only its loaded resources and source specialization are established. The fresh diagnostic will capture both loaded native cubins.

Several passes ramp from roughly 0.95 ms in the first quartile to 1.1 ms in the last. Some phases have SM-clock reductions/power-limit reasons, while others show similar ramps with sampled SM clocks at 2032 MHz and reason 0. Therefore the available clock samples alone do not establish the cause.

## Every quartile

| Variant | Phase | Q | E2E us | FC1 extension us | FC2 extension us | SM min/median/max MHz | Power min/median/max W | Temp min/median/max C | Reasons |
|---|---|---:|---:|---:|---:|---|---|---|---|
| writer-r1 | 0-control | 0 | 943.943 | 574.820 | 293.762 | 2032/2032/2032 | 241.9/241.9/278.4 | 35/35/41 | `{"0": 13}` |
| writer-r1 | 0-control | 1 | 993.160 | 599.716 | 313.474 | 2032/2032/2032 | 278.4/278.4/278.4 | 41/41/41 | `{"0": 14}` |
| writer-r1 | 0-control | 2 | 1052.455 | 638.820 | 330.979 | 2032/2032/2032 | 278.4/278.4/278.4 | 41/41/41 | `{"0": 15}` |
| writer-r1 | 0-control | 3 | 1121.896 | 686.149 | 349.218 | 2032/2032/2032 | 278.4/278.4/278.4 | 41/41/41 | `{"0": 15}` |
| writer-r1 | 1-candidate | 0 | 946.343 | 576.228 | 294.146 | 2032/2032/2032 | 243.7/243.7/243.7 | 37/37/37 | `{"0": 13}` |
| writer-r1 | 1-candidate | 1 | 1014.823 | 612.900 | 318.786 | 2032/2032/2032 | 243.7/243.7/243.7 | 37/37/37 | `{"0": 14}` |
| writer-r1 | 1-candidate | 2 | 1085.127 | 661.444 | 340.131 | 1530/2032/2032 | 243.7/243.7/328.4 | 37/37/46 | `{"0": 12, "4": 3}` |
| writer-r1 | 1-candidate | 3 | 1108.584 | 677.253 | 345.603 | 1530/1530/1530 | 328.4/328.4/328.4 | 46/46/46 | `{"4": 16}` |
| writer-r1 | 2-candidate | 0 | 944.775 | 575.140 | 292.803 | 2032/2032/2032 | 242.0/242.0/242.0 | 36/36/36 | `{"0": 13}` |
| writer-r1 | 2-candidate | 1 | 947.975 | 574.596 | 294.915 | 2032/2032/2032 | 242.0/285.8/285.8 | 36/42/42 | `{"0": 13}` |
| writer-r1 | 2-candidate | 2 | 1083.080 | 661.221 | 337.762 | 2032/2032/2032 | 285.8/285.8/285.8 | 42/42/42 | `{"0": 15}` |
| writer-r1 | 2-candidate | 3 | 1112.968 | 681.029 | 346.179 | 2032/2032/2032 | 285.8/285.8/285.8 | 42/42/42 | `{"0": 16}` |
| writer-r1 | 3-control | 0 | 943.751 | 573.988 | 293.442 | 2032/2032/2032 | 241.6/241.6/241.6 | 37/37/37 | `{"0": 13}` |
| writer-r1 | 3-control | 1 | 1019.143 | 614.532 | 321.954 | 2032/2032/2032 | 241.6/241.6/241.6 | 37/37/37 | `{"0": 14}` |
| writer-r1 | 3-control | 2 | 1013.544 | 612.165 | 319.714 | 1485/2032/2032 | 241.6/241.6/241.6 | 37/37/37 | `{"0": 15}` |
| writer-r1 | 3-control | 3 | 1121.480 | 686.533 | 348.291 | 1485/1485/1485 | 348.6/348.6/348.6 | 37/46/46 | `{"0": 1, "4": 14}` |
| static-sf | 0-control | 0 | 949.130 | 579.750 | 293.059 | 2032/2032/2032 | 239.4/239.4/239.4 | 36/36/36 | `{"0": 13}` |
| static-sf | 0-control | 1 | 963.306 | 588.294 | 294.307 | 2032/2032/2032 | 239.4/239.4/296.4 | 36/36/39 | `{"0": 9, "4": 4}` |
| static-sf | 0-control | 2 | 1045.707 | 634.791 | 328.867 | 2032/2032/2032 | 296.4/296.4/296.4 | 39/39/39 | `{"4": 14}` |
| static-sf | 0-control | 3 | 1090.731 | 667.335 | 340.324 | 2032/2032/2032 | 296.4/296.4/296.4 | 39/39/39 | `{"4": 15}` |
| static-sf | 1-candidate | 0 | 949.322 | 580.230 | 293.667 | 2032/2032/2032 | 240.3/240.3/240.3 | 36/36/36 | `{"0": 13}` |
| static-sf | 1-candidate | 1 | 954.570 | 583.046 | 294.787 | 2032/2032/2032 | 240.3/293.4/293.4 | 36/37/37 | `{"0": 13}` |
| static-sf | 1-candidate | 2 | 1080.971 | 658.407 | 337.444 | 2032/2032/2032 | 293.4/293.4/293.4 | 37/37/37 | `{"0": 15}` |
| static-sf | 1-candidate | 3 | 1126.860 | 690.343 | 349.988 | 2032/2032/2032 | 293.4/293.4/293.4 | 37/37/37 | `{"0": 15}` |
| static-sf | 2-candidate | 0 | 947.179 | 577.830 | 293.412 | 2032/2032/2032 | 235.6/262.8/262.8 | 36/37/37 | `{"0": 13}` |
| static-sf | 2-candidate | 1 | 1018.924 | 616.999 | 320.899 | 2032/2032/2032 | 262.8/262.8/262.8 | 37/37/37 | `{"0": 14}` |
| static-sf | 2-candidate | 2 | 1008.395 | 608.007 | 318.724 | 2032/2032/2032 | 262.8/262.8/262.8 | 37/37/37 | `{"0": 14}` |
| static-sf | 2-candidate | 3 | 1109.388 | 678.408 | 344.739 | 1327/2032/2032 | 262.8/262.8/364.0 | 37/37/46 | `{"0": 15, "4": 1}` |
| static-sf | 3-control | 0 | 948.458 | 578.790 | 293.795 | 2032/2032/2032 | 242.4/242.4/242.4 | 37/37/37 | `{"0": 14}` |
| static-sf | 3-control | 1 | 1007.659 | 608.359 | 318.180 | 2032/2032/2032 | 242.4/287.4/287.4 | 37/45/45 | `{"0": 13}` |
| static-sf | 3-control | 2 | 1080.268 | 658.343 | 337.091 | 2032/2032/2032 | 287.4/287.4/287.4 | 45/45/45 | `{"0": 15}` |
| static-sf | 3-control | 3 | 1119.084 | 685.159 | 348.036 | 2032/2032/2032 | 287.4/287.4/287.4 | 45/45/45 | `{"0": 16}` |
