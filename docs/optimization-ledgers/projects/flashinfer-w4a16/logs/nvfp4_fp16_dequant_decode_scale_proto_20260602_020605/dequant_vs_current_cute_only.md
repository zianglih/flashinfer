Comparison: FP16 dequant-scale prototype vs current encoded-domain FP16 scoring (CuTe-only).

`Prototype/current` > 1 means the dequant-scale prototype is slower.

| Mode | Layout | Cases | Current geo ms | Prototype geo ms | Prototype/current | Min | Max | >2% slower | >2% faster | Worst shape |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| MAE_FP16 | swizzled_128x4 | 330 | 0.018678 | 0.018675 | 1.000x | 0.769x | 1.321x | 16 | 20 | (256, 3072) (1.321x) |
| MAE_FP16 | swizzled_8x4 | 330 | 0.018678 | 0.018721 | 1.002x | 0.770x | 1.039x | 25 | 10 | (1536, 256) (1.039x) |
| MAE_FP16 | linear | 330 | 0.018701 | 0.018627 | 0.996x | 0.923x | 1.037x | 9 | 43 | (8, 3072) (1.037x) |
| MAE_FP16 | all | 990 | 0.018686 | 0.018674 | 0.999x | 0.769x | 1.321x | 50 | 73 | (256, 3072) (1.321x) |
| MSE_FP16 | swizzled_128x4 | 330 | 0.019318 | 0.019393 | 1.004x | 0.863x | 1.214x | 21 | 8 | (64, 6144) (1.214x) |
| MSE_FP16 | swizzled_8x4 | 330 | 0.019378 | 0.019490 | 1.006x | 0.785x | 1.074x | 50 | 8 | (4096, 8192) (1.074x) |
| MSE_FP16 | linear | 330 | 0.019371 | 0.019382 | 1.001x | 0.757x | 1.291x | 32 | 32 | (64, 5120) (1.291x) |
| MSE_FP16 | all | 990 | 0.019356 | 0.019421 | 1.003x | 0.757x | 1.291x | 103 | 48 | (64, 5120) (1.291x) |
