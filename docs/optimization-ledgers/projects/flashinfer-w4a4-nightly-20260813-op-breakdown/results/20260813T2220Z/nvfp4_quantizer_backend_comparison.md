# NVFP4 per-token quantizer backend comparison

Both configurations use BF16 input, `swizzled_128x4`, MSE 4over6, and disabled
general quantizer fast math. Each contains the same 330-shape M/K grid.

| Configuration | Backend agreement | CuTe DSL faster | Geomean CUDA/CuTe | Median CUDA/CuTe | Minimum | Maximum |
|---|---:|---:|---:|---:|---:|---:|
| E4M3 max 256, fast 4over6 error evaluation (operation-breakdown config) | 330/330 at 100% | 330/330 | 2.37x | 2.66x | 1.01x (M=32768, K=16384) | 4.25x (M=2, K=384) |
| E4M3 max 448, exact 4over6 error evaluation (supplemental) | 330/330 at 100% | 330/330 | 2.51x | 2.83x | 1.24x (M=32768, K=128) | 3.64x (M=2, K=512) |

Backend agreement means exact CUDA-vs-CuTe agreement within one configuration
for quantized outputs and scales. The per-token path does not perform an
independent reference or dequantization roundtrip.

Both sweeps ran sequentially on the same B200 using the same immutable image
and nightly package, deterministic per-shape seed, five dry runs, cold L2, and
a median of 30 CUPTI timings per backend. They were not interleaved or repeated,
and the benchmark did not retain individual samples. Cross-configuration
differences are descriptive: E4M3 max and 4over6 error evaluation both changed,
so their effects cannot be separated. Aggregate statistics are computed from
the rounded speedups printed by the upstream benchmark.
