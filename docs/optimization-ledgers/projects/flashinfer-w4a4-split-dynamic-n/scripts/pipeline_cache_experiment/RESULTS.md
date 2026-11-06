# Raw diagnostic median table

Each row uses its own same-process control and exact comparison. Cross-GPU absolute values are not paired. Full raw samples and error logs remain in `results/`.

| Run | Tokens | Phase | Variant | Median us |
|---|---:|---|---|---:|
| pipeline-cache-a-last-nvfp4-two256-01 | 16384 | fc1 | baseline | 324.7850 |
| pipeline-cache-a-last-nvfp4-two256-01 | 16384 | fc1 | cache_a | 329.5045 |
| pipeline-cache-a-last-nvfp4-two256-01 | 16384 | fc1 | cache_a_last | 324.2250 |
| pipeline-cache-a-last-nvfp4-two256-01 | 16384 | fc2 | baseline | 181.2485 |
| pipeline-cache-a-last-nvfp4-two256-01 | 16384 | fc2 | cache_a | 188.2085 |
| pipeline-cache-a-last-nvfp4-two256-01 | 16384 | fc2 | cache_a_last | 180.7205 |
| pipeline-cache-nvfp4-chain-small-01 | 128 | full fixed tactic | baseline | 168.2090 |
| pipeline-cache-nvfp4-chain-small-01 | 128 | full fixed tactic | cache_a | 167.3600 |
| pipeline-cache-nvfp4-chain-small-01 | 128 | full fixed tactic | cache_b | 167.5680 |
| pipeline-cache-nvfp4-chain-small-01 | 128 | full fixed tactic | cache_ab | 167.2000 |
| pipeline-cache-nvfp4-chain-small-01 | 128 | full fixed tactic | prefetch | 168.2880 |
| pipeline-cache-nvfp4-two256-02 | 16384 | fc1 | baseline | 324.7690 |
| pipeline-cache-nvfp4-two256-02 | 16384 | fc1 | cache_a | 329.4570 |
| pipeline-cache-nvfp4-two256-02 | 16384 | fc1 | cache_b | 328.5930 |
| pipeline-cache-nvfp4-two256-02 | 16384 | fc1 | cache_ab | 332.2090 |
| pipeline-cache-nvfp4-two256-02 | 16384 | fc1 | prefetch | 325.4405 |
| pipeline-cache-nvfp4-two256-02 | 16384 | fc1 | cache_prefetch | 332.8325 |
| pipeline-cache-nvfp4-two256-02 | 16384 | fc2 | baseline | 181.1210 |
| pipeline-cache-nvfp4-two256-02 | 16384 | fc2 | cache_a | 188.2725 |
| pipeline-cache-nvfp4-two256-02 | 16384 | fc2 | cache_b | 180.1610 |
| pipeline-cache-nvfp4-two256-02 | 16384 | fc2 | cache_ab | 186.4970 |
| pipeline-cache-nvfp4-two256-02 | 16384 | fc2 | prefetch | 181.2160 |
| pipeline-cache-nvfp4-two256-02 | 16384 | fc2 | cache_prefetch | 186.6730 |
| pipeline-composed-nvfp4-small-two128-01 | 4 | fc1 | baseline | 38.1120 |
| pipeline-composed-nvfp4-small-two128-01 | 4 | fc1 | composed | 37.2480 |
| pipeline-composed-nvfp4-small-two128-01 | 128 | fc1 | baseline | 99.6645 |
| pipeline-composed-nvfp4-small-two128-01 | 128 | fc1 | composed | 96.2560 |
| pipeline-composed-nvfp4-small-two128-01 | 1024 | fc1 | baseline | 103.1680 |
| pipeline-composed-nvfp4-small-two128-01 | 1024 | fc1 | composed | 99.5840 |
| pipeline-pdl-nvfp4-two256-03 | 128 | full fixed tactic | baseline | 165.2805 |
| pipeline-pdl-nvfp4-two256-03 | 128 | full fixed tactic | pdl_early | 164.6565 |
| pipeline-pdl-nvfp4-two256-03 | 16384 | full fixed tactic | baseline | 618.3220 |
| pipeline-pdl-nvfp4-two256-03 | 16384 | full fixed tactic | pdl_early | 622.0980 |
| pipeline-producer-balance-native-01 | 128 | fc1 | baseline | 108.3840 |
| pipeline-producer-balance-native-01 | 128 | fc1 | gather3 | 107.2800 |
| pipeline-producer-balance-native-01 | 128 | fc1 | weightslate | 110.2720 |
| pipeline-producer-balance-native-01 | 16384 | fc1 | baseline | 327.3280 |
| pipeline-producer-balance-native-01 | 16384 | fc1 | gather3 | 323.6800 |
| pipeline-producer-balance-native-01 | 16384 | fc1 | weightslate | 326.3200 |
| pipeline-sfcommitfirst-native-01 | 128 | fc1 | baseline | 108.5120 |
| pipeline-sfcommitfirst-native-01 | 128 | fc1 | sfcommitfirst | 108.5440 |
| pipeline-sfcommitfirst-native-01 | 16384 | fc1 | baseline | 326.1930 |
| pipeline-sfcommitfirst-native-01 | 16384 | fc1 | sfcommitfirst | 329.2165 |
| pipeline-stage-mixed-one128-01 | 16384 | fc1 | baseline | 633.5210 |
| pipeline-stage-mixed-one128-01 | 16384 | fc1 | stage5 | 605.5690 |
| pipeline-stage-mixed-one128-01 | 16384 | fc1 | stage6 | 605.0400 |
| pipeline-stage-mixed-one128-01 | 16384 | fc2 | baseline | 270.4160 |
| pipeline-stage-mixed-one128-01 | 16384 | fc2 | stage5 | 246.4960 |
| pipeline-stage-mixed-one128-01 | 16384 | fc2 | stage6 | 258.0005 |
| pipeline-stage-mixed-one128-reverse-01 | 16384 | fc2 | selected | 243.4240 |
| pipeline-stage-mixed-one128-reverse-01 | 16384 | fc2 | baseline | 268.5925 |
| pipeline-stage-mxfp8-one128-01 | 128 | fc1 | baseline | 198.4650 |
| pipeline-stage-mxfp8-one128-01 | 128 | fc1 | stage5 | 184.8965 |
| pipeline-stage-mxfp8-one128-01 | 128 | fc1 | stage6 | 176.4480 |
| pipeline-stage-mxfp8-one128-01 | 128 | fc2 | baseline | 93.9045 |
| pipeline-stage-mxfp8-one128-01 | 128 | fc2 | stage5 | 91.0405 |
| pipeline-stage-mxfp8-one128-01 | 128 | fc2 | stage6 | 88.5280 |
| pipeline-stage-mxfp8-one128-01 | 16384 | fc1 | baseline | 665.8725 |
| pipeline-stage-mxfp8-one128-01 | 16384 | fc1 | stage5 | 640.2510 |
| pipeline-stage-mxfp8-one128-01 | 16384 | fc1 | stage6 | 644.8810 |
| pipeline-stage-mxfp8-one128-01 | 16384 | fc2 | baseline | 290.4810 |
| pipeline-stage-mxfp8-one128-01 | 16384 | fc2 | stage5 | 267.5690 |
| pipeline-stage-mxfp8-one128-01 | 16384 | fc2 | stage6 | 272.7360 |
| pipeline-stage-mxfp8-one128-reverse-01 | 128 | fc2 | selected | 91.1850 |
| pipeline-stage-mxfp8-one128-reverse-01 | 128 | fc2 | baseline | 93.9840 |
| pipeline-stage-mxfp8-one128-reverse-01 | 16384 | fc2 | selected | 260.9290 |
| pipeline-stage-mxfp8-one128-reverse-01 | 16384 | fc2 | baseline | 286.5290 |
| pipeline-stage-mxfp8-two256-01 | 16384 | fc1 | baseline | 462.6400 |
| pipeline-stage-mxfp8-two256-01 | 16384 | fc1 | stage3 | 553.4570 |
| pipeline-stage-mxfp8-two256-01 | 16384 | fc1 | stage4 | 474.5130 |
| pipeline-stage-mxfp8-two256-01 | 16384 | fc1 | stage6 | 493.2645 |
| pipeline-stage-mxfp8-two256-01 | 16384 | fc2 | baseline | 260.2720 |
| pipeline-stage-mxfp8-two256-01 | 16384 | fc2 | stage3 | 309.7925 |
| pipeline-stage-mxfp8-two256-01 | 16384 | fc2 | stage4 | 273.4085 |
| pipeline-stage-mxfp8-two256-01 | 16384 | fc2 | stage6 | 264.2890 |
| pipeline-stage-nvfp4-one128-01 | 16384 | fc1 | baseline | 429.1520 |
| pipeline-stage-nvfp4-one128-01 | 16384 | fc1 | stage3 | 522.4010 |
| pipeline-stage-nvfp4-one128-01 | 16384 | fc1 | stage4 | 429.1045 |
| pipeline-stage-nvfp4-one128-01 | 16384 | fc1 | stage5 | 441.0880 |
| pipeline-stage-nvfp4-one128-01 | 16384 | fc1 | stage6 | 465.0725 |
| pipeline-stage-nvfp4-one128-01 | 16384 | fc2 | baseline | 182.2565 |
| pipeline-stage-nvfp4-one128-01 | 16384 | fc2 | stage3 | 200.6725 |
| pipeline-stage-nvfp4-one128-01 | 16384 | fc2 | stage4 | 182.2720 |
| pipeline-stage-nvfp4-one128-01 | 16384 | fc2 | stage5 | 176.1925 |
| pipeline-stage-nvfp4-one128-01 | 16384 | fc2 | stage6 | 186.6880 |
| pipeline-stage-nvfp4-one128-reverse-01 | 4 | fc1 | baseline | 52.6080 |
| pipeline-stage-nvfp4-one128-reverse-01 | 4 | fc1 | stage5 | 51.6640 |
| pipeline-stage-nvfp4-one128-reverse-01 | 4 | fc2 | baseline | 18.0480 |
| pipeline-stage-nvfp4-one128-reverse-01 | 4 | fc2 | stage5 | 17.5040 |
| pipeline-stage-nvfp4-one128-reverse-01 | 128 | fc1 | baseline | 122.7040 |
| pipeline-stage-nvfp4-one128-reverse-01 | 128 | fc1 | stage5 | 117.1365 |
| pipeline-stage-nvfp4-one128-reverse-01 | 128 | fc2 | baseline | 55.6800 |
| pipeline-stage-nvfp4-one128-reverse-01 | 128 | fc2 | stage5 | 54.6560 |
| pipeline-stage-nvfp4-one128-reverse-01 | 1024 | fc1 | baseline | 118.2880 |
| pipeline-stage-nvfp4-one128-reverse-01 | 1024 | fc1 | stage5 | 114.0480 |
| pipeline-stage-nvfp4-one128-reverse-01 | 1024 | fc2 | baseline | 60.3520 |
| pipeline-stage-nvfp4-one128-reverse-01 | 1024 | fc2 | stage5 | 58.7360 |
| pipeline-stage-nvfp4-one128-reverse-01 | 16384 | fc1 | baseline | 428.6725 |
| pipeline-stage-nvfp4-one128-reverse-01 | 16384 | fc1 | stage5 | 441.2005 |
| pipeline-stage-nvfp4-one128-reverse-01 | 16384 | fc2 | baseline | 182.1280 |
| pipeline-stage-nvfp4-one128-reverse-01 | 16384 | fc2 | stage5 | 175.9520 |
| pipeline-stage-nvfp4-small-one128-01 | 4 | fc1 | stage5 | 51.6800 |
| pipeline-stage-nvfp4-small-one128-01 | 4 | fc1 | stage3 | 54.1120 |
| pipeline-stage-nvfp4-small-one128-01 | 4 | fc1 | baseline | 52.6245 |
| pipeline-stage-nvfp4-small-one128-01 | 4 | fc2 | stage5 | 17.5040 |
| pipeline-stage-nvfp4-small-one128-01 | 4 | fc2 | stage3 | 19.6640 |
| pipeline-stage-nvfp4-small-one128-01 | 4 | fc2 | baseline | 18.0480 |
| pipeline-stage-nvfp4-small-one128-01 | 128 | fc1 | stage5 | 109.0880 |
| pipeline-stage-nvfp4-small-one128-01 | 128 | fc1 | stage3 | 125.7920 |
| pipeline-stage-nvfp4-small-one128-01 | 128 | fc1 | baseline | 114.0960 |
| pipeline-stage-nvfp4-small-one128-01 | 128 | fc2 | stage5 | 54.6400 |
| pipeline-stage-nvfp4-small-one128-01 | 128 | fc2 | stage3 | 61.1200 |
| pipeline-stage-nvfp4-small-one128-01 | 128 | fc2 | baseline | 55.9360 |
| pipeline-stage-nvfp4-small-one128-01 | 1024 | fc1 | stage5 | 116.1765 |
| pipeline-stage-nvfp4-small-one128-01 | 1024 | fc1 | stage3 | 132.4960 |
| pipeline-stage-nvfp4-small-one128-01 | 1024 | fc1 | baseline | 121.3765 |
| pipeline-stage-nvfp4-small-one128-01 | 1024 | fc2 | stage5 | 58.5440 |
| pipeline-stage-nvfp4-small-one128-01 | 1024 | fc2 | stage3 | 66.0480 |
| pipeline-stage-nvfp4-small-one128-01 | 1024 | fc2 | baseline | 60.5275 |
| pipeline-stage-nvfp4-two256-02 | 16384 | fc1 | baseline | 328.4640 |
| pipeline-stage-nvfp4-two256-02 | 16384 | fc1 | stage2 | 499.1525 |
| pipeline-stage-nvfp4-two256-02 | 16384 | fc1 | stage3 | 376.4480 |
| pipeline-stage-nvfp4-two256-02 | 16384 | fc1 | stage4 | 320.1920 |
| pipeline-stage-nvfp4-two256-02 | 16384 | fc2 | baseline | 180.8000 |
| pipeline-stage-nvfp4-two256-02 | 16384 | fc2 | stage2 | 243.9045 |
| pipeline-stage-nvfp4-two256-02 | 16384 | fc2 | stage3 | 206.3685 |
| pipeline-stage-nvfp4-two256-02 | 16384 | fc2 | stage4 | 185.9845 |
| pipeline-widek-mixed-two128-reverse-01 | 128 | fc1 | composed | 128.1925 |
| pipeline-widek-mixed-two128-reverse-01 | 128 | fc1 | baseline | 134.0480 |
| pipeline-widek-mixed-two128-reverse-01 | 1024 | fc1 | composed | 130.5765 |
| pipeline-widek-mixed-two128-reverse-01 | 1024 | fc1 | baseline | 136.8005 |
| pipeline-widek-mixed-two128-reverse-01 | 16384 | fc1 | composed | 512.4980 |
| pipeline-widek-mixed-two128-reverse-01 | 16384 | fc1 | baseline | 537.3930 |
| pipeline-widek-mxfp8-two128-01 | 16384 | fc1 | baseline | 575.3770 |
| pipeline-widek-mxfp8-two128-01 | 16384 | fc1 | widek3 | 497.8735 |
| pipeline-widek-mxfp8-two128-reverse-01 | 128 | fc1 | widek3 | 159.3600 |
| pipeline-widek-mxfp8-two128-reverse-01 | 128 | fc1 | baseline | 169.5360 |
| pipeline-widek-mxfp8-two128-reverse-01 | 1024 | fc1 | widek3 | 167.4560 |
| pipeline-widek-mxfp8-two128-reverse-01 | 1024 | fc1 | baseline | 177.1210 |
| pipeline-widek-mxfp8-two128-reverse-01 | 16384 | fc1 | widek3 | 508.4645 |
| pipeline-widek-mxfp8-two128-reverse-01 | 16384 | fc1 | baseline | 591.6805 |
| pipeline-widek-mxfp8-two256-01 | 16384 | fc1 | baseline | 445.3295 |
| pipeline-widek-mxfp8-two256-01 | 16384 | fc1 | widek2 | 512.3850 |
| pipeline-widek-mxfp8-two256-01 | 16384 | fc1 | widek3 | 439.6655 |
| pipeline-widek-mxfp8-two256-01 | 16384 | fc2 | baseline | 256.6720 |
| pipeline-widek-mxfp8-two256-01 | 16384 | fc2 | widek2 | 288.7365 |
| pipeline-widek-mxfp8-two256-01 | 16384 | fc2 | widek3 | 263.2330 |
| pipeline-widek-nvfp4-two128-01 | 16384 | fc1 | baseline | 334.3690 |
| pipeline-widek-nvfp4-two128-01 | 16384 | fc1 | stage6 | 342.4650 |
| pipeline-widek-nvfp4-two128-01 | 16384 | fc1 | stage7 | 349.3450 |
| pipeline-widek-nvfp4-two128-01 | 16384 | fc1 | widek3 | 322.7050 |
| pipeline-widek-nvfp4-two128-01 | 16384 | fc1 | widek4 | 344.6090 |
| pipeline-widek-nvfp4-two128-reverse-01 | 8192 | fc1 | widek3 | 185.2160 |
| pipeline-widek-nvfp4-two128-reverse-01 | 8192 | fc1 | baseline | 192.7525 |
| pipeline-widek-nvfp4-two128-reverse-01 | 16384 | fc1 | widek3 | 329.1200 |
| pipeline-widek-nvfp4-two128-reverse-01 | 16384 | fc1 | baseline | 338.2725 |
| pipeline-widek-nvfp4-two256-01 | 16384 | fc1 | baseline | 325.4090 |
| pipeline-widek-nvfp4-two256-01 | 16384 | fc1 | widek2 | 353.4405 |
| pipeline-widek-nvfp4-two256-01 | 16384 | fc2 | baseline | 181.3120 |
| pipeline-widek-nvfp4-two256-01 | 16384 | fc2 | widek2 | 196.8330 |
| pipeline-widek-w4a8-two128-01 | 16384 | fc1 | baseline | 539.2810 |
| pipeline-widek-w4a8-two128-01 | 16384 | fc1 | widek3 | 517.4245 |

## Failed diagnostic attempts

- pipeline-cache-nvfp4-two256.json: AttributeError: 'NoneType' object has no attribute 'zero_'
- pipeline-pdl-nvfp4-two256-01.json: AssertionError: Native pipeline byte mismatch: baseline fc1_0
- pipeline-pdl-nvfp4-two256-02.json: AssertionError: Native pipeline byte mismatch: baseline fc1_0
- pipeline-stage-nvfp4-two256.json: AttributeError: 'NoneType' object has no attribute 'zero_'
