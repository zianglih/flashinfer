CuTe-only FP16 dequant-scale scoring prototype

| Mode | Layout | Cases | Geomean ms | Min ms | Max ms |
|---|---|---:|---:|---:|---:|
| MAE_FP16 | swizzled_128x4 | 330 | 0.018675 | 0.010032 | 0.412320 |
| MAE_FP16 | swizzled_8x4 | 330 | 0.018721 | 0.010048 | 0.411296 |
| MAE_FP16 | linear | 330 | 0.018627 | 0.010192 | 0.411697 |
| MAE_FP16 | all | 990 | 0.018674 | 0.010032 | 0.412320 |
| MSE_FP16 | swizzled_128x4 | 330 | 0.019393 | 0.010400 | 0.438928 |
| MSE_FP16 | swizzled_8x4 | 330 | 0.019490 | 0.010576 | 0.438353 |
| MSE_FP16 | linear | 330 | 0.019382 | 0.010576 | 0.439839 |
| MSE_FP16 | all | 990 | 0.019421 | 0.010400 | 0.439839 |
