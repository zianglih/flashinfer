Baseline prior FP16: /Users/ziangli/playground/cute-dsl-nvfp4/logs/nvfp4_fp16_error_mode_speedup_20260601_053027
Diff-only proto: /Users/ziangli/playground/cute-dsl-nvfp4/logs/nvfp4_fp16_orig_diff_h2_proto_20260601_091352
Full-h2 proto: /Users/ziangli/playground/cute-dsl-nvfp4/logs/nvfp4_fp16_full_h2_error_proto_20260601_092131

### Full-h2 vs prior FP16 baseline
| Mode | Layout | Cases | CuTe geomean speedup | Min | Max | Candidate min match |
|---|---|---:|---:|---:|---:|---:|
| MAE_FP16 | swizzled_128x4 | 330 | 1.001x | 0.909x | 1.100x | 99.7% |
| MAE_FP16 | swizzled_8x4 | 330 | 1.015x | 0.722x | 1.235x | 99.7% |
| MAE_FP16 | linear | 330 | 1.018x | 0.909x | 1.273x | 99.7% |
| MAE_FP16 | all | 990 | 1.011x | 0.722x | 1.273x | 99.7% |
MAE_FP16: candidate faster in 306/990 cases.
| MSE_FP16 | swizzled_128x4 | 330 | 1.022x | 0.800x | 1.333x | 87.5% |
| MSE_FP16 | swizzled_8x4 | 330 | 1.017x | 0.714x | 1.130x | 87.5% |
| MSE_FP16 | linear | 330 | 1.020x | 0.786x | 1.170x | 87.5% |
| MSE_FP16 | all | 990 | 1.020x | 0.714x | 1.333x | 87.5% |
MSE_FP16: candidate faster in 350/990 cases.

### Full-h2 vs diff-only prototype
| Mode | Layout | Cases | CuTe geomean speedup | Min | Max | Candidate min match |
|---|---|---:|---:|---:|---:|---:|
| MAE_FP16 | swizzled_128x4 | 330 | 1.007x | 0.909x | 1.100x | 99.7% |
| MAE_FP16 | swizzled_8x4 | 330 | 1.018x | 0.722x | 1.100x | 99.7% |
| MAE_FP16 | linear | 330 | 1.020x | 0.929x | 1.273x | 99.7% |
| MAE_FP16 | all | 990 | 1.015x | 0.722x | 1.273x | 99.7% |
MAE_FP16: candidate faster in 346/990 cases.
| MSE_FP16 | swizzled_128x4 | 330 | 1.029x | 0.800x | 1.107x | 87.5% |
| MSE_FP16 | swizzled_8x4 | 330 | 1.027x | 0.786x | 1.455x | 87.5% |
| MSE_FP16 | linear | 330 | 1.024x | 0.786x | 1.261x | 87.5% |
| MSE_FP16 | all | 990 | 1.026x | 0.786x | 1.455x | 87.5% |
MSE_FP16: candidate faster in 422/990 cases.
