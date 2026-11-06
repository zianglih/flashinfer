Baseline: /Users/ziangli/playground/cute-dsl-nvfp4/logs/nvfp4_fp16_error_mode_speedup_20260601_053027
Candidate: /Users/ziangli/playground/cute-dsl-nvfp4/logs/nvfp4_fp16_orig_diff_h2_proto_20260601_091352

| Mode | Layout | Cases | CuTe geomean speedup | Min | Max | Candidate min match |
|---|---|---:|---:|---:|---:|---:|
| MAE_FP16 | swizzled_128x4 | 330 | 0.994x | 0.909x | 1.100x | 99.7% |
| MAE_FP16 | swizzled_8x4 | 330 | 0.997x | 0.909x | 1.235x | 99.7% |
| MAE_FP16 | linear | 330 | 0.997x | 0.786x | 1.273x | 99.7% |
| MAE_FP16 | all | 990 | 0.996x | 0.786x | 1.273x | - |
| MSE_FP16 | swizzled_128x4 | 330 | 0.993x | 0.909x | 1.333x | 99.5% |
| MSE_FP16 | swizzled_8x4 | 330 | 0.991x | 0.750x | 1.091x | 99.5% |
| MSE_FP16 | linear | 330 | 0.996x | 0.828x | 1.273x | 99.5% |
| MSE_FP16 | all | 990 | 0.993x | 0.750x | 1.333x | - |

MAE_FP16: candidate faster than prior CuTe FP16 in 145/990 cases.
MSE_FP16: candidate faster than prior CuTe FP16 in 97/990 cases.
