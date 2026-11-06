# Fresh K3 EP MXFP4x8 16K diagnostic

Four complete independent order blocks on second-node GPUs0/1, each variant source-paired on its own physical GPU; stock clocks unchanged. Initial first-node losses remain separate. All samples, phases, negative rows and clock exceptions retained. The needed native release libraries are retrospectively bound by filesystem hashes/mtimes and successful build/load records. Paused orchestration never interrupted measurement children.

| Variant / order | Phase0 | Phase1 | Phase2 | Phase3 | Change | C spread | A spread | FC1 extension delta | FC2 extension delta | Combine delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| writer-r1-caac | 0-control: 1019.306 | 1-candidate: 970.554 | 2-candidate: 949.482 | 3-control: 969.946 | +3.579% | 5.089% | 2.219% | -20.984 us | -12.296 us | -1.775 us |
| writer-r1-acca | 0-candidate: 1007.466 | 1-control: 993.786 | 2-control: 979.658 | 3-candidate: 990.633 | -1.233% | 1.442% | 1.699% | +8.808 us | +1.776 us | +0.208 us |
| static-sf-caac | 0-control: 1002.086 | 1-candidate: 999.687 | 2-candidate: 944.054 | 3-control: 1041.255 | +5.148% | 3.909% | 5.893% | -31.057 us | -14.736 us | -2.352 us |
| static-sf-acca | 0-candidate: 993.750 | 1-control: 993.222 | 2-control: 1022.358 | 3-candidate: 1011.446 | +0.511% | 2.933% | 1.781% | -3.488 us | -1.448 us | -0.240 us |

Positive percentages mean candidate faster. E2E uses the geometric mean of each arm’s two full100-sample phase medians. Component deltas use arithmetic means of component medians and do not sum overlapping kernels.

Writer-R1 native FC1 cubins are byte-identical across control/candidate and both order blocks. FC2 differs as intended. Static-SF changes both native FC cubins. Every returned main-kernel image is source/library-bound and all32 loaded main kernels have zero local bytes.

The original 3–4% losses do not reproduce consistently: fresh CAAC changes reverse sign, while reversedACCA is writer−1.23% and SF+0.51%. Repeat spreads remain1.44–5.89%. This does not establish a throughput win or eliminate a smaller regression. No clock-normalized or selected-quartile result replaces the complete phase medians.

## Every observed quartile

| Variant | Phase | Q | E2E us | FC1 extension us | FC2 extension us | SM min/median/max MHz | Power min/median/max W | Reasons |
|---|---|---:|---:|---:|---:|---|---|---|
| writer-r1-caac | 0-control | 0 | 928.073 | 563.718 | 287.139 | 2032/2032/2032 | 239.5/239.5/277.7 | `{"0": 13}` |
| writer-r1-caac | 0-control | 1 | 953.162 | 575.526 | 299.747 | 2032/2032/2032 | 277.7/277.7/277.7 | `{"0": 14}` |
| writer-r1-caac | 0-control | 2 | 1021.067 | 616.903 | 322.852 | 2032/2032/2032 | 277.7/277.7/277.7 | `{"0": 14}` |
| writer-r1-caac | 0-control | 3 | 1092.716 | 665.959 | 340.324 | 2032/2032/2032 | 277.7/277.7/277.7 | `{"0": 15}` |
| writer-r1-caac | 1-candidate | 0 | 927.914 | 563.174 | 287.619 | 2032/2032/2032 | 254.9/254.9/254.9 | `{"0": 13}` |
| writer-r1-caac | 1-candidate | 1 | 964.362 | 579.814 | 305.219 | 2032/2032/2032 | 254.9/254.9/254.9 | `{"0": 13}` |
| writer-r1-caac | 1-candidate | 2 | 1060.171 | 642.886 | 332.387 | 1642/2032/2032 | 254.9/254.9/254.9 | `{"0": 14}` |
| writer-r1-caac | 1-candidate | 3 | 1072.010 | 652.870 | 334.660 | 1642/1642/1642 | 341.4/341.4/341.4 | `{"0": 1, "4": 14}` |
| writer-r1-caac | 2-candidate | 0 | 927.338 | 562.118 | 287.266 | 2032/2032/2032 | 240.3/240.3/240.3 | `{"0": 12}` |
| writer-r1-caac | 2-candidate | 1 | 928.778 | 564.901 | 287.779 | 2032/2032/2032 | 240.3/240.3/303.1 | `{"0": 14}` |
| writer-r1-caac | 2-candidate | 2 | 951.530 | 574.790 | 299.427 | 2032/2032/2032 | 303.1/303.1/303.1 | `{"0": 13}` |
| writer-r1-caac | 2-candidate | 3 | 1074.987 | 652.838 | 335.812 | 2032/2032/2032 | 303.1/303.1/303.1 | `{"0": 15}` |
| writer-r1-caac | 3-control | 0 | 927.722 | 563.430 | 287.619 | 2032/2032/2032 | 238.0/238.0/278.3 | `{"0": 11, "4": 2}` |
| writer-r1-caac | 3-control | 1 | 961.322 | 576.838 | 303.587 | 2032/2032/2032 | 278.3/278.3/278.3 | `{"4": 13}` |
| writer-r1-caac | 3-control | 2 | 1081.836 | 658.375 | 336.995 | 2032/2032/2032 | 278.3/278.3/278.3 | `{"4": 15}` |
| writer-r1-caac | 3-control | 3 | 1088.332 | 664.359 | 339.843 | 2032/2032/2032 | 278.3/278.3/278.3 | `{"4": 15}` |
| writer-r1-acca | 0-candidate | 0 | 925.193 | 561.957 | 286.562 | 2032/2032/2032 | 239.4/239.4/239.4 | `{"0": 13}` |
| writer-r1-acca | 0-candidate | 1 | 956.713 | 575.622 | 300.514 | 2032/2032/2032 | 239.4/239.4/297.8 | `{"0": 14}` |
| writer-r1-acca | 0-candidate | 2 | 1010.474 | 607.494 | 319.972 | 2032/2032/2032 | 297.8/297.8/297.8 | `{"0": 14}` |
| writer-r1-acca | 0-candidate | 3 | 1083.019 | 658.950 | 337.796 | 2032/2032/2032 | 297.8/297.8/297.8 | `{"0": 15}` |
| writer-r1-acca | 1-control | 0 | 925.834 | 562.214 | 287.107 | 2032/2032/2032 | 241.6/241.6/241.6 | `{"0": 13}` |
| writer-r1-acca | 1-control | 1 | 929.610 | 566.790 | 286.434 | 2032/2032/2032 | 241.6/241.6/304.8 | `{"0": 13}` |
| writer-r1-acca | 1-control | 2 | 1055.243 | 639.687 | 330.436 | 2032/2032/2032 | 304.8/304.8/304.8 | `{"0": 14}` |
| writer-r1-acca | 1-control | 3 | 1100.875 | 670.598 | 342.531 | 2032/2032/2032 | 304.8/304.8/304.8 | `{"0": 15}` |
| writer-r1-acca | 2-control | 0 | 926.378 | 561.957 | 287.427 | 2032/2032/2032 | 237.3/237.3/279.0 | `{"0": 13}` |
| writer-r1-acca | 2-control | 1 | 989.546 | 594.054 | 313.155 | 2032/2032/2032 | 279.0/279.0/279.0 | `{"0": 13}` |
| writer-r1-acca | 2-control | 2 | 978.314 | 585.703 | 310.723 | 2032/2032/2032 | 279.0/279.0/279.0 | `{"0": 14}` |
| writer-r1-acca | 2-control | 3 | 1075.499 | 655.303 | 335.555 | 2032/2032/2032 | 279.0/279.0/279.0 | `{"0": 15}` |
| writer-r1-acca | 3-candidate | 0 | 924.458 | 561.062 | 286.659 | 2032/2032/2032 | 238.4/260.0/260.0 | `{"0": 12}` |
| writer-r1-acca | 3-candidate | 1 | 929.065 | 563.430 | 289.059 | 2032/2032/2032 | 260.0/260.0/260.0 | `{"0": 13}` |
| writer-r1-acca | 3-candidate | 2 | 998.185 | 598.085 | 315.267 | 2032/2032/2032 | 260.0/260.0/260.0 | `{"0": 14}` |
| writer-r1-acca | 3-candidate | 3 | 1098.506 | 670.822 | 341.380 | 1357/2032/2032 | 260.0/260.0/260.0 | `{"0": 15}` |
| static-sf-caac | 0-control | 0 | 917.734 | 552.772 | 288.067 | 2032/2032/2032 | 245.5/245.5/245.5 | `{"0": 12}` |
| static-sf-caac | 0-control | 1 | 920.454 | 554.532 | 289.762 | 2032/2032/2032 | 245.5/245.5/245.5 | `{"0": 13}` |
| static-sf-caac | 0-control | 2 | 1058.791 | 641.284 | 332.482 | 1552/2032/2032 | 245.5/245.5/331.1 | `{"0": 15}` |
| static-sf-caac | 0-control | 3 | 1097.607 | 668.389 | 341.603 | 1552/1552/1552 | 331.1/331.1/331.1 | `{"0": 15}` |
| static-sf-caac | 1-candidate | 0 | 918.278 | 552.772 | 288.385 | 2032/2032/2032 | 242.4/242.4/242.4 | `{"0": 12}` |
| static-sf-caac | 1-candidate | 1 | 920.678 | 555.076 | 289.217 | 2032/2032/2032 | 242.4/242.4/242.4 | `{"0": 13}` |
| static-sf-caac | 1-candidate | 2 | 1053.127 | 637.957 | 330.402 | 1552/1552/1552 | 242.4/306.5/306.5 | `{"0": 14}` |
| static-sf-caac | 1-candidate | 3 | 1098.824 | 669.988 | 342.274 | 1552/1552/1552 | 306.5/306.5/306.5 | `{"0": 15}` |
| static-sf-caac | 2-candidate | 0 | 924.582 | 558.724 | 288.929 | 2032/2032/2032 | 246.6/265.4/265.4 | `{"0": 13}` |
| static-sf-caac | 2-candidate | 1 | 926.054 | 561.443 | 288.067 | 2032/2032/2032 | 265.4/265.4/265.4 | `{"0": 13}` |
| static-sf-caac | 2-candidate | 2 | 951.526 | 575.140 | 298.690 | 2032/2032/2032 | 265.4/265.4/265.4 | `{"0": 13}` |
| static-sf-caac | 2-candidate | 3 | 1071.207 | 650.692 | 335.234 | 1867/2032/2032 | 265.4/265.4/368.0 | `{"0": 15}` |
| static-sf-caac | 3-control | 0 | 924.390 | 557.284 | 289.314 | 2032/2032/2032 | 243.2/260.8/260.8 | `{"0": 13}` |
| static-sf-caac | 3-control | 1 | 922.599 | 556.004 | 289.570 | 2032/2032/2032 | 260.8/260.8/260.8 | `{"0": 14}` |
| static-sf-caac | 3-control | 2 | 1046.855 | 633.732 | 329.026 | 2032/2032/2032 | 260.8/260.8/260.8 | `{"0": 14}` |
| static-sf-caac | 3-control | 3 | 1082.215 | 660.548 | 338.082 | 1372/2032/2032 | 260.8/260.8/359.7 | `{"0": 14, "4": 1}` |
| static-sf-acca | 0-candidate | 0 | 924.486 | 557.540 | 289.954 | 2032/2032/2032 | 253.4/253.4/253.4 | `{"0": 13}` |
| static-sf-acca | 0-candidate | 1 | 933.574 | 565.892 | 289.921 | 2032/2032/2032 | 253.4/253.4/253.4 | `{"0": 14}` |
| static-sf-acca | 0-candidate | 2 | 1003.815 | 601.988 | 318.658 | 1515/2032/2032 | 253.4/253.4/339.7 | `{"0": 13, "4": 2}` |
| static-sf-acca | 0-candidate | 3 | 1088.007 | 661.924 | 338.402 | 1515/1515/1515 | 339.7/339.7/339.7 | `{"4": 15}` |
| static-sf-acca | 1-control | 0 | 924.741 | 558.340 | 289.410 | 2032/2032/2032 | 245.4/245.4/245.4 | `{"0": 13}` |
| static-sf-acca | 1-control | 1 | 992.391 | 597.315 | 313.858 | 2032/2032/2032 | 245.4/245.4/245.4 | `{"0": 14}` |
| static-sf-acca | 1-control | 2 | 993.671 | 597.092 | 315.938 | 2010/2010/2032 | 245.4/320.8/320.8 | `{"0": 6, "4": 8}` |
| static-sf-acca | 1-control | 3 | 1080.071 | 656.933 | 337.058 | 2010/2010/2010 | 320.8/320.8/320.8 | `{"4": 15}` |
| static-sf-acca | 2-control | 0 | 923.814 | 559.587 | 287.585 | 2032/2032/2032 | 241.2/241.2/241.2 | `{"0": 13}` |
| static-sf-acca | 2-control | 1 | 920.262 | 555.139 | 289.794 | 2032/2032/2032 | 285.8/285.8/285.8 | `{"0": 13}` |
| static-sf-acca | 2-control | 2 | 1058.727 | 640.997 | 332.866 | 2032/2032/2032 | 285.8/285.8/285.8 | `{"0": 15}` |
| static-sf-acca | 2-control | 3 | 1097.479 | 669.060 | 341.986 | 2032/2032/2032 | 285.8/285.8/285.8 | `{"0": 17}` |
| static-sf-acca | 3-candidate | 0 | 923.302 | 556.964 | 289.602 | 2032/2032/2032 | 261.0/261.0/261.0 | `{"0": 13}` |
| static-sf-acca | 3-candidate | 1 | 921.637 | 556.675 | 289.314 | 2032/2032/2032 | 261.0/261.0/261.0 | `{"0": 13}` |
| static-sf-acca | 3-candidate | 2 | 1018.118 | 612.420 | 321.986 | 2025/2032/2032 | 261.0/261.0/261.0 | `{"0": 14}` |
| static-sf-acca | 3-candidate | 3 | 1076.487 | 654.403 | 336.194 | 2025/2025/2025 | 333.6/333.6/333.6 | `{"0": 15}` |
