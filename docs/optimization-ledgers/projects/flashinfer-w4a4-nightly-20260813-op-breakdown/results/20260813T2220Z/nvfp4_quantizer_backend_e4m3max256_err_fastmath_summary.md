# NVFP4 quantizer backend comparison

Mode: `per-token, 4over6-mse, e4m3-256, err-fastmath`. This is BF16 per-token activation quantization in
`swizzled_128x4` layout with quantizer fast math disabled.

| Metric | Result |
|---|---:|
| Backend agreement (quant and scale) | 330/330 at 100% |
| CuTe DSL faster | 330/330 cases |
| Geometric-mean speedup | 2.37x |
| Median speedup | 2.66x |
| Minimum speedup | 1.01x (M=32768, K=16384) |
| Maximum speedup | 4.25x (M=2, K=384) |

Speedup is CUDA median time divided by CuTe-DSL median time. Each displayed
backend time is the benchmark's median of 30 CUPTI-measured iterations after
five dry runs, using cold L2 and no CUDA graph. The source log records rounded
per-shape medians and speedups; the benchmark does not retain individual timing
samples. For this per-token path, the upstream check compares CUDA and CuTe-DSL
quantized outputs and scales exactly; it does not run an independent reference
or dequantization roundtrip.
