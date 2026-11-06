CuTe-only current FP16 scoring baseline

| Mode | Layout | Cases | Geomean ms | Min ms | Max ms |
|---|---|---:|---:|---:|---:|
| MAE_FP16 | swizzled_128x4 | 330 | 0.018678 | 0.010096 | 0.422449 |
| MAE_FP16 | swizzled_8x4 | 330 | 0.018678 | 0.010096 | 0.419088 |
| MAE_FP16 | linear | 330 | 0.018701 | 0.010128 | 0.413585 |
| MAE_FP16 | all | 990 | 0.018686 | 0.010096 | 0.422449 |
| MSE_FP16 | swizzled_128x4 | 330 | 0.019318 | 0.010432 | 0.447665 |
| MSE_FP16 | swizzled_8x4 | 330 | 0.019378 | 0.010560 | 0.444752 |
| MSE_FP16 | linear | 330 | 0.019371 | 0.010496 | 0.435393 |
| MSE_FP16 | all | 990 | 0.019356 | 0.010432 | 0.447665 |
