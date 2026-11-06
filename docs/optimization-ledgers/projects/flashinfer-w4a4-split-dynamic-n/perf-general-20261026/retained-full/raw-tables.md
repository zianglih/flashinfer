# Six final A public outputs

## v3 / nvfp4

```text

DeepSeek-V3 MoE Performance Benchmark
GPU: NVIDIA B300 SXM6 AC
CuteDSL API: Wrapper
PER-TOKEN activation recipe (initial and FC2): 4over6, MSE, E4M3 max=256, 4over6 error fast math enabled; base FP4 quantization fast math disabled. Weights retain standard NVFP4 quantization.
Initial activation quantization: True
Expert parallelism simulation: EP=8
Routing input mode: logits
CuteDSL modes: W4A4 / PER-TOKEN / W4A16; TRTLLM: NVFP4 / PER-TOKEN / BF16
Tensor parallelism simulation: TP=1
CUDA profiler capture: False
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4 / PER-TOKEN / BF16 finalize: native (unaffected by --no-fused-finalize).
[2026-10-27 03:22:23.577] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

=====================================================================================================================================================================================================================================
DeepSeek-V3 MoE Benchmark: CuteDSL W4A4 / PER-TOKEN / W4A16 vs TRTLLM NVFP4 / PER-TOKEN / BF16 (EP=8, TP=1)
=====================================================================================================================================================================================================================================
Model: hidden=7168, intermediate=2048, experts=256, top_k=8
EP Config: 32 local experts (simulating 8-way parallelism)
TP Config: intermediate size 2048 (simulating 1-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Timed initial activation quantization for FP4-activation backends: included; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4 / PER-TOKEN / BF16 finalize: native (unaffected by --no-fused-finalize).
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   | CuteDSL PER-TOKEN |  CuteDSL W4A16  |  TRTLLM NVFP4   | TRTLLM PER-TOKEN |   TRTLLM BF16   |                    Speedup vs TRTLLM NVFP4                    |      Winner       | Active  |      Stats
       |      ms  TFLOPS |        ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |       ms  TFLOPS |      ms  TFLOPS | CuteDSL W4A4 CuteDSL W4A16 CuteDSL PER-TOKEN TRTLLM PER-TOKEN |                   | experts | min/max/median
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.027     3.2 |     0.031     2.8 |   0.034     2.6 |   0.026     3.3 |    0.032     2.8 |   0.048     1.8 |        0.97x         0.77x             0.85x            0.84x |   TRTLLM NVFP4    |       2 |   0/  1/   0.00
     2 |   0.036     4.9 |     0.039     4.6 |   0.041     4.3 |   0.036     4.9 |    0.043     4.1 |   0.077     2.3 |        0.99x         0.88x             0.93x            0.84x |   TRTLLM NVFP4    |       4 |   0/  1/   0.00
     4 |   0.046     7.6 |     0.051     6.9 |   0.055     6.4 |   0.050     7.1 |    0.059     5.9 |   0.119     3.0 |        1.07x         0.91x             0.97x            0.84x |   CuteDSL W4A4    |       7 |   0/  1/   0.00
     8 |   0.060    11.7 |     0.064    11.1 |   0.069    10.2 |   0.063    11.2 |    0.070    10.0 |   0.155     4.5 |        1.05x         0.92x             0.99x            0.90x |   CuteDSL W4A4    |      10 |   0/  2/   0.00
    16 |   0.069    20.5 |     0.074    19.0 |   0.077    18.3 |   0.074    19.1 |    0.081    17.3 |   0.190     7.4 |        1.07x         0.96x             1.00x            0.91x |   CuteDSL W4A4    |      13 |   0/  2/   0.00
    32 |   0.103    27.5 |     0.107    26.4 |   0.111    25.4 |   0.105    26.8 |    0.112    25.2 |   0.286     9.9 |        1.02x         0.95x             0.98x            0.94x |   CuteDSL W4A4    |      21 |   0/  3/   1.00
    64 |   0.133    42.4 |     0.138    40.9 |   0.145    38.8 |   0.143    39.5 |    0.148    38.2 |   0.385    14.7 |        1.07x         0.98x             1.04x            0.97x |   CuteDSL W4A4    |      29 |   0/  5/   2.00
   128 |   0.138    81.7 |     0.143    78.7 |   0.148    76.2 |   0.142    79.4 |    0.150    75.1 |   0.398    28.3 |        1.03x         0.96x             0.99x            0.95x |   CuteDSL W4A4    |      30 |   0/  8/   3.00
   256 |   0.149   151.5 |     0.156   145.0 |   0.157   143.9 |   0.152   148.1 |    0.161   140.1 |   0.427    52.8 |        1.02x         0.97x             0.98x            0.95x |   CuteDSL W4A4    |      32 |   1/ 11/   7.00
   512 |   0.152   297.4 |     0.161   280.3 |   0.160   281.5 |   0.160   281.9 |    0.170   265.9 |   0.436   103.4 |        1.05x         1.00x             0.99x            0.94x |   CuteDSL W4A4    |      32 |   7/ 23/  14.00
  4096 |   0.208  1738.2 |     0.254  1422.8 |   0.312  1155.0 |   0.225  1604.4 |    0.269  1340.1 |   0.516   698.8 |        1.08x         0.72x             0.89x            0.84x |   CuteDSL W4A4    |      32 |  81/147/ 117.00
  8192 |   0.324  2224.7 |     0.392  1842.2 |   0.618  1166.7 |   0.360  2005.6 |    0.430  1679.6 |   0.793   910.3 |        1.11x         0.58x             0.92x            0.84x |   CuteDSL W4A4    |      32 | 174/347/ 251.50
 16384 |   0.526  2743.5 |     0.693  2081.4 |   1.184  1218.4 |   0.636  2270.5 |    0.773  1866.2 |   1.474   978.9 |        1.21x         0.54x             0.92x            0.82x |   CuteDSL W4A4    |      32 | 388/733/ 496.50
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

## v3 / mxfp

```text

DeepSeek-V3 MoE Performance Benchmark
GPU: NVIDIA B300 SXM6 AC
CuteDSL API: Wrapper
Initial activation quantization: False
Expert parallelism simulation: EP=8
Routing input mode: logits
CuteDSL modes: MXFP4x8 and MXFP8; baselines: matching TRTLLM modes and BF16
Tensor parallelism simulation: TP=1
CUDA profiler capture: False
CuteDSL finalize: deterministic two-stage
TRTLLM MXFP4x8 / MXFP8 / BF16 finalize: native (unaffected by --no-fused-finalize).
[2026-10-27 03:29:47.697] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

================================================================================================================================================
DeepSeek-V3 MoE Benchmark: CuteDSL MXFP4x8 / MXFP8 vs TRTLLM MXFP4x8 / MXFP8 / BF16 (EP=8, TP=1)
================================================================================================================================================
Model: hidden=7168, intermediate=2048, experts=256, top_k=8
EP Config: 32 local experts (simulating 8-way parallelism)
TP Config: intermediate size 2048 (simulating 1-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
MXFP8 activations: native UE8M0 scale per 32 elements along K.
Timed initial activation quantization: excluded; weight preparation and tuning excluded. TRTLLM BF16 consumes BF16 directly.
CuteDSL finalize: deterministic two-stage
TRTLLM MXFP4x8 / MXFP8 / BF16 finalize: native (unaffected by --no-fused-finalize).
------------------------------------------------------------------------------------------------------------------------------------------------
Tokens | CuteDSL MXFP4x8 |  CuteDSL MXFP8  | TRTLLM MXFP4x8  |  TRTLLM MXFP8   |   TRTLLM BF16   | Speedup vs TRTLLM | Active  |      Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |  MXFP4x8    MXFP8 | experts | min/max/median
------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.027     3.3 |   0.033     2.7 |   0.029     3.0 |   0.032     2.7 |   0.051     1.7 |    1.09x    0.99x |       2 |   0/  1/   0.00
     2 |   0.034     5.2 |   0.047     3.8 |   0.036     4.9 |   0.050     3.5 |   0.077     2.3 |    1.07x    1.08x |       4 |   0/  1/   0.00
     4 |   0.046     7.6 |   0.069     5.1 |   0.050     7.0 |   0.075     4.7 |   0.117     3.0 |    1.09x    1.08x |       7 |   0/  1/   0.00
     8 |   0.060    11.7 |   0.092     7.7 |   0.066    10.7 |   0.098     7.2 |   0.155     4.6 |    1.09x    1.06x |      10 |   0/  2/   0.00
    16 |   0.069    20.5 |   0.112    12.6 |   0.074    19.0 |   0.116    12.1 |   0.188     7.5 |    1.08x    1.04x |      13 |   0/  2/   0.00
    32 |   0.100    28.1 |   0.168    16.8 |   0.104    27.2 |   0.168    16.8 |   0.286     9.9 |    1.03x    1.00x |      21 |   0/  3/   1.00
    64 |   0.132    42.6 |   0.225    25.0 |   0.139    40.4 |   0.225    25.1 |   0.385    14.6 |    1.05x    1.00x |      29 |   0/  5/   2.00
   128 |   0.135    83.6 |   0.228    49.5 |   0.139    81.4 |   0.233    48.5 |   0.400    28.2 |    1.03x    1.02x |      30 |   0/  8/   3.00
   256 |   0.145   155.1 |   0.247    91.4 |   0.149   151.2 |   0.248    91.0 |   0.428    52.7 |    1.03x    1.00x |      32 |   1/ 11/   7.00
   512 |   0.147   306.5 |   0.248   182.1 |   0.155   290.2 |   0.254   177.5 |   0.435   103.7 |    1.06x    1.03x |      32 |   7/ 23/  14.00
  4096 |   0.225  1600.2 |   0.306  1179.8 |   0.237  1519.4 |   0.316  1141.7 |   0.516   699.5 |    1.05x    1.03x |      32 |  81/147/ 117.00
  8192 |   0.375  1926.4 |   0.448  1611.8 |   0.401  1797.8 |   0.463  1557.1 |   0.804   897.8 |    1.07x    1.04x |      32 | 174/347/ 251.50
 16384 |   0.694  2079.2 |   0.762  1893.2 |   0.743  1942.7 |   0.802  1798.9 |   1.530   943.3 |    1.07x    1.05x |      32 | 388/733/ 496.50
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

## v41-flash / nvfp4

```text

DeepSeek-V4.1-Flash MoE Performance Benchmark
GPU: NVIDIA B300 SXM6 AC
CuteDSL API: Wrapper
PER-TOKEN activation recipe (initial and FC2): 4over6, MSE, E4M3 max=256, 4over6 error fast math enabled; base FP4 quantization fast math disabled. Weights retain standard NVFP4 quantization.
Initial activation quantization: True
Expert parallelism simulation: EP=4
Routing: model sqrtsoftplus routes precomputed and shared by all backends; routing excluded from timing, TRTLLM uses routed APIs.
CuteDSL modes: W4A4 / PER-TOKEN / W4A16; TRTLLM: NVFP4 / PER-TOKEN / BF16
Tensor parallelism simulation: TP=1
CUDA profiler capture: False
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4 / PER-TOKEN / BF16 finalize: native (unaffected by --no-fused-finalize).
[2026-10-27 03:27:48.063] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

=====================================================================================================================================================================================================================================
DeepSeek-V4.1-Flash MoE Benchmark: CuteDSL W4A4 / PER-TOKEN / W4A16 vs TRTLLM NVFP4 / PER-TOKEN / BF16 (EP=4, TP=1)
=====================================================================================================================================================================================================================================
Model: hidden=5120, intermediate=2304, experts=384, top_k=6
EP Config: 96 local experts (simulating 4-way parallelism)
TP Config: intermediate size 2304 (simulating 1-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Routing: shared precomputed sqrt(softplus(logits)), bias selects only, top-6 normalized then scaled by 1.5; routing excluded from every backend's timing.
Activation: SwiGLU, gate clamped above 10, up clamped to [-10, 10].
Timed initial activation quantization for FP4-activation backends: included; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4 / PER-TOKEN / BF16 finalize: native (unaffected by --no-fused-finalize).
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   | CuteDSL PER-TOKEN |  CuteDSL W4A16  |  TRTLLM NVFP4   | TRTLLM PER-TOKEN |   TRTLLM BF16   |                    Speedup vs TRTLLM NVFP4                    |      Winner       | Active  |      Stats
       |      ms  TFLOPS |        ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |       ms  TFLOPS |      ms  TFLOPS | CuteDSL W4A4 CuteDSL W4A16 CuteDSL PER-TOKEN TRTLLM PER-TOKEN |                   | experts | min/max/median
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.011     9.4 |     0.014     7.7 |   0.011     9.8 |   0.012     8.8 |    0.014     7.6 |   0.009    11.2 |        1.07x         1.12x             0.88x            0.87x |    TRTLLM BF16    |       0 |   0/  0/   0.00
     2 |   0.021    10.1 |     0.024     8.9 |   0.026     8.3 |   0.017    12.3 |    0.024     8.8 |   0.029     7.3 |        0.83x         0.68x             0.73x            0.72x |   TRTLLM NVFP4    |       1 |   0/  1/   0.00
     4 |   0.035    12.1 |     0.039    10.8 |   0.042    10.2 |   0.036    11.8 |    0.044     9.6 |   0.087     4.9 |        1.03x         0.87x             0.92x            0.82x |   CuteDSL W4A4    |       6 |   0/  1/   0.00
     8 |   0.048    17.5 |     0.053    16.1 |   0.055    15.4 |   0.051    16.5 |    0.058    14.6 |   0.128     6.6 |        1.06x         0.93x             0.98x            0.88x |   CuteDSL W4A4    |      10 |   0/  2/   0.00
    16 |   0.066    25.8 |     0.070    24.3 |   0.072    23.4 |   0.069    24.6 |    0.077    22.0 |   0.177     9.6 |        1.05x         0.95x             0.99x            0.90x |   CuteDSL W4A4    |      15 |   0/  2/   0.00
    32 |   0.128    26.5 |     0.134    25.3 |   0.136    25.0 |   0.131    25.9 |    0.139    24.4 |   0.371     9.2 |        1.02x         0.97x             0.98x            0.94x |   CuteDSL W4A4    |      35 |   0/  4/   0.00
    64 |   0.206    33.0 |     0.214    31.7 |   0.217    31.4 |   0.210    32.3 |    0.219    31.1 |   0.624    10.9 |        1.02x         0.97x             0.98x            0.96x |   CuteDSL W4A4    |      61 |   0/  4/   1.00
   128 |   0.267    51.0 |     0.278    49.0 |   0.279    48.7 |   0.270    50.4 |    0.278    48.8 |   0.827    16.4 |        1.01x         0.97x             0.97x            0.97x |   CuteDSL W4A4    |      82 |   0/  6/   2.00
   256 |   0.306    88.8 |     0.319    85.3 |   0.318    85.3 |   0.309    88.1 |    0.319    85.2 |   0.958    28.4 |        1.01x         0.97x             0.97x            0.97x |   CuteDSL W4A4    |      95 |   0/ 11/   4.00
   512 |   0.311   174.6 |     0.327   166.4 |   0.323   168.3 |   0.315   172.7 |    0.329   165.4 |   0.976    55.7 |        1.01x         0.97x             0.96x            0.96x |   CuteDSL W4A4    |      96 |   2/ 16/   8.00
  4096 |   0.349  1246.0 |     0.417  1042.3 |   0.555   784.0 |   0.366  1187.1 |    0.420  1034.7 |   1.049   414.7 |        1.05x         0.66x             0.88x            0.87x |   CuteDSL W4A4    |      96 |  42/ 84/  63.00
  8192 |   0.421  2063.9 |     0.541  1606.9 |   0.877   991.7 |   0.453  1920.6 |    0.531  1636.5 |   1.289   675.0 |        1.07x         0.52x             0.84x            0.85x |   CuteDSL W4A4    |      96 |  95/162/ 126.50
 16384 |   0.650  2676.0 |     0.842  2065.7 |   1.660  1047.8 |   0.698  2490.8 |    0.853  2039.5 |   2.016   862.9 |        1.07x         0.42x             0.83x            0.82x |   CuteDSL W4A4    |      96 | 198/337/ 254.00
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

## v41-flash / mxfp

```text

DeepSeek-V4.1-Flash MoE Performance Benchmark
GPU: NVIDIA B300 SXM6 AC
CuteDSL API: Wrapper
Initial activation quantization: False
Expert parallelism simulation: EP=4
Routing: model sqrtsoftplus routes precomputed and shared by all backends; routing excluded from timing, TRTLLM uses routed APIs.
CuteDSL modes: MXFP4x8 and MXFP8; baselines: matching TRTLLM modes and BF16
Tensor parallelism simulation: TP=1
CUDA profiler capture: False
CuteDSL finalize: deterministic two-stage
TRTLLM MXFP4x8 / MXFP8 / BF16 finalize: native (unaffected by --no-fused-finalize).
[2026-10-27 03:41:33.145] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

================================================================================================================================================
DeepSeek-V4.1-Flash MoE Benchmark: CuteDSL MXFP4x8 / MXFP8 vs TRTLLM MXFP4x8 / MXFP8 / BF16 (EP=4, TP=1)
================================================================================================================================================
Model: hidden=5120, intermediate=2304, experts=384, top_k=6
EP Config: 96 local experts (simulating 4-way parallelism)
TP Config: intermediate size 2304 (simulating 1-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Routing: shared precomputed sqrt(softplus(logits)), bias selects only, top-6 normalized then scaled by 1.5; routing excluded from every backend's timing.
Activation: SwiGLU, gate clamped above 10, up clamped to [-10, 10].
MXFP8 activations: native UE8M0 scale per 32 elements along K.
Timed initial activation quantization: excluded; weight preparation and tuning excluded. TRTLLM BF16 consumes BF16 directly.
CuteDSL finalize: deterministic two-stage
TRTLLM MXFP4x8 / MXFP8 / BF16 finalize: native (unaffected by --no-fused-finalize).
------------------------------------------------------------------------------------------------------------------------------------------------
Tokens | CuteDSL MXFP4x8 |  CuteDSL MXFP8  | TRTLLM MXFP4x8  |  TRTLLM MXFP8   |   TRTLLM BF16   | Speedup vs TRTLLM | Active  |      Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |  MXFP4x8    MXFP8 | experts | min/max/median
------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.010    10.6 |   0.010    10.5 |   0.010    10.1 |   0.011    10.0 |   0.009    11.3 |    1.04x    1.04x |       0 |   0/  0/   0.00
     2 |   0.022     9.9 |   0.025     8.6 |   0.019    11.3 |   0.019    11.0 |   0.029     7.4 |    0.87x    0.79x |       1 |   0/  1/   0.00
     4 |   0.036    11.9 |   0.051     8.3 |   0.038    11.1 |   0.054     7.9 |   0.086     4.9 |    1.07x    1.05x |       6 |   0/  1/   0.00
     8 |   0.048    17.8 |   0.074    11.5 |   0.053    16.1 |   0.079    10.8 |   0.128     6.7 |    1.10x    1.07x |      10 |   0/  2/   0.00
    16 |   0.064    26.5 |   0.103    16.5 |   0.069    24.6 |   0.106    16.0 |   0.177     9.6 |    1.08x    1.03x |      15 |   0/  2/   0.00
    32 |   0.125    27.2 |   0.215    15.8 |   0.128    26.5 |   0.211    16.1 |   0.370     9.2 |    1.03x    0.98x |      35 |   0/  4/   0.00
    64 |   0.198    34.3 |   0.355    19.1 |   0.202    33.7 |   0.349    19.5 |   0.624    10.9 |    1.02x    0.98x |      61 |   0/  4/   1.00
   128 |   0.257    52.8 |   0.466    29.2 |   0.260    52.3 |   0.456    29.8 |   0.829    16.4 |    1.01x    0.98x |      82 |   0/  6/   2.00
   256 |   0.296    91.7 |   0.537    50.6 |   0.299    90.9 |   0.528    51.4 |   0.958    28.4 |    1.01x    0.98x |      95 |   0/ 11/   4.00
   512 |   0.301   180.9 |   0.545    99.7 |   0.304   179.1 |   0.536   101.5 |   0.975    55.7 |    1.01x    0.98x |      96 |   2/ 16/   8.00
  4096 |   0.354  1227.4 |   0.587   741.1 |   0.386  1126.5 |   0.588   739.4 |   1.047   415.2 |    1.09x    1.00x |      96 |  42/ 84/  63.00
  8192 |   0.494  1760.5 |   0.671  1295.8 |   0.536  1621.7 |   0.672  1293.4 |   1.291   673.6 |    1.09x    1.00x |      96 |  95/162/ 126.50
 16384 |   0.883  1969.3 |   0.997  1745.1 |   0.848  2051.8 |   1.053  1651.8 |   2.041   852.2 |    0.96x    1.06x |      96 | 198/337/ 254.00
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

## kimi-k3 / nvfp4

```text

Kimi-K3 MoE Performance Benchmark
GPU: NVIDIA B300 SXM6 AC
CuteDSL API: Wrapper
PER-TOKEN activation recipe (initial and FC2): 4over6, MSE, E4M3 max=256, 4over6 error fast math enabled; base FP4 quantization fast math disabled. Weights retain standard NVFP4 quantization.
Initial activation quantization: True
Expert parallelism simulation: EP=8
Routing: model sigmoid routes precomputed and shared by all backends; routing excluded from timing, TRTLLM uses routed APIs.
CuteDSL modes: W4A4 / PER-TOKEN / W4A16; TRTLLM: NVFP4 / PER-TOKEN / BF16
Tensor parallelism simulation: TP=1
CUDA profiler capture: False
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4 / PER-TOKEN / BF16 finalize: native (unaffected by --no-fused-finalize).
[2026-10-27 03:26:30.080] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

=====================================================================================================================================================================================================================================
Kimi-K3 MoE Benchmark: CuteDSL W4A4 / PER-TOKEN / W4A16 vs TRTLLM NVFP4 / PER-TOKEN / BF16 (EP=8, TP=1)
=====================================================================================================================================================================================================================================
Model: hidden=3584, intermediate=3072, experts=896, top_k=16
EP Config: 112 local experts (simulating 8-way parallelism)
TP Config: intermediate size 3072 (simulating 1-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Routing: shared precomputed sigmoid(logits), bias selects only, top-16 normalized then scaled by 1.0; routing excluded from every backend's timing.
Activation: SiTU(4, 25).
Scope: routed latent experts only; latent projections, RMSNorm, shared experts, router GEMM and communication excluded.
N/A: TRTLLM PER-TOKEN has no per-token SiTU kernel; skipped before preparation and timing.
N/A: TRTLLM BF16 has no SiTU kernel; skipped before preparation and timing.
Timed initial activation quantization for FP4-activation backends: included; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4 / PER-TOKEN / BF16 finalize: native (unaffected by --no-fused-finalize).
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   | CuteDSL PER-TOKEN |  CuteDSL W4A16  |  TRTLLM NVFP4   | TRTLLM PER-TOKEN |   TRTLLM BF16   |                    Speedup vs TRTLLM NVFP4                    |      Winner       | Active  |      Stats
       |      ms  TFLOPS |        ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |       ms  TFLOPS |      ms  TFLOPS | CuteDSL W4A4 CuteDSL W4A16 CuteDSL PER-TOKEN TRTLLM PER-TOKEN |                   | experts | min/max/median
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.013    10.6 |     0.014     9.2 |   0.013    10.3 |   0.015     9.1 |              N/A |             N/A |        1.17x         1.14x             1.01x              N/A |   CuteDSL W4A4    |       0 |   0/  0/   0.00
     2 |   0.028     9.5 |     0.031     8.4 |   0.031     8.6 |   0.025    10.6 |              N/A |             N/A |        0.90x         0.81x             0.80x              N/A |   TRTLLM NVFP4    |       3 |   0/  1/   0.00
     4 |   0.054     9.8 |     0.058     9.1 |   0.060     8.7 |   0.056     9.4 |              N/A |             N/A |        1.03x         0.93x             0.96x              N/A |   CuteDSL W4A4    |      12 |   0/  1/   0.00
     8 |   0.082    12.8 |     0.085    12.4 |   0.086    12.2 |   0.083    12.7 |              N/A |             N/A |        1.01x         0.96x             0.97x              N/A |   CuteDSL W4A4    |      18 |   0/  1/   0.00
    16 |   0.116    18.2 |     0.120    17.6 |   0.123    17.2 |   0.115    18.4 |              N/A |             N/A |        0.99x         0.94x             0.96x              N/A |   TRTLLM NVFP4    |      30 |   0/  2/   0.00
    32 |   0.177    23.8 |     0.186    22.8 |   0.187    22.6 |   0.176    24.0 |              N/A |             N/A |        0.99x         0.94x             0.95x              N/A |   TRTLLM NVFP4    |      54 |   0/  4/   0.00
    64 |   0.241    35.1 |     0.250    33.8 |   0.253    33.4 |   0.236    35.9 |              N/A |             N/A |        0.98x         0.93x             0.94x              N/A |   TRTLLM NVFP4    |      77 |   0/  5/   1.00
   128 |   0.300    56.3 |     0.311    54.3 |   0.316    53.5 |   0.300    56.4 |              N/A |             N/A |        1.00x         0.95x             0.96x              N/A |   TRTLLM NVFP4    |      99 |   0/  7/   2.00
   256 |   0.334   101.2 |     0.351    96.3 |   0.357    94.6 |   0.332   102.0 |              N/A |             N/A |        0.99x         0.93x             0.94x              N/A |   TRTLLM NVFP4    |     111 |   0/ 12/   4.00
   512 |   0.344   196.9 |     0.365   185.3 |   0.374   180.9 |   0.338   199.9 |              N/A |             N/A |        0.98x         0.90x             0.93x              N/A |   TRTLLM NVFP4    |     112 |   3/ 19/   9.00
  4096 |   0.388  1396.0 |     0.458  1181.9 |   0.618   875.5 |   0.412  1314.7 |              N/A |             N/A |        1.06x         0.67x             0.90x              N/A |   CuteDSL W4A4    |     112 |  35/127/  74.00
  8192 |   0.501  2159.5 |     0.672  1611.1 |   1.081  1001.4 |   0.555  1950.7 |              N/A |             N/A |        1.11x         0.51x             0.83x              N/A |   CuteDSL W4A4    |     112 |  64/252/ 149.50
 16384 |   0.818  2645.7 |     1.126  1922.0 |   2.083  1039.3 |   0.841  2574.2 |              N/A |             N/A |        1.03x         0.40x             0.75x              N/A |   CuteDSL W4A4    |     112 | 148/550/ 298.50
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

## kimi-k3 / mxfp

```text

Kimi-K3 MoE Performance Benchmark
GPU: NVIDIA B300 SXM6 AC
CuteDSL API: Wrapper
Initial activation quantization: False
Expert parallelism simulation: EP=8
Routing: model sigmoid routes precomputed and shared by all backends; routing excluded from timing, TRTLLM uses routed APIs.
CuteDSL modes: MXFP4x8 and MXFP8; baselines: matching TRTLLM modes and BF16
Tensor parallelism simulation: TP=1
CUDA profiler capture: False
CuteDSL finalize: deterministic two-stage
TRTLLM MXFP4x8 / MXFP8 / BF16 finalize: native (unaffected by --no-fused-finalize).
[2026-10-27 03:37:59.007] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

================================================================================================================================================
Kimi-K3 MoE Benchmark: CuteDSL MXFP4x8 / MXFP8 vs TRTLLM MXFP4x8 / MXFP8 / BF16 (EP=8, TP=1)
================================================================================================================================================
Model: hidden=3584, intermediate=3072, experts=896, top_k=16
EP Config: 112 local experts (simulating 8-way parallelism)
TP Config: intermediate size 3072 (simulating 1-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Routing: shared precomputed sigmoid(logits), bias selects only, top-16 normalized then scaled by 1.0; routing excluded from every backend's timing.
Activation: SiTU(4, 25).
Scope: routed latent experts only; latent projections, RMSNorm, shared experts, router GEMM and communication excluded.
N/A: TRTLLM MXFP8 has no SiTU kernel; skipped before preparation and timing.
N/A: TRTLLM BF16 has no SiTU kernel; skipped before preparation and timing.
MXFP8 activations: native UE8M0 scale per 32 elements along K.
Timed initial activation quantization: excluded; weight preparation and tuning excluded. TRTLLM BF16 consumes BF16 directly.
CuteDSL finalize: deterministic two-stage
TRTLLM MXFP4x8 / MXFP8 / BF16 finalize: native (unaffected by --no-fused-finalize).
------------------------------------------------------------------------------------------------------------------------------------------------
Tokens | CuteDSL MXFP4x8 |  CuteDSL MXFP8  | TRTLLM MXFP4x8  |  TRTLLM MXFP8   |   TRTLLM BF16   | Speedup vs TRTLLM | Active  |      Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |  MXFP4x8    MXFP8 | experts | min/max/median
------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.010    12.8 |   0.011    11.9 |   0.012    10.7 |             N/A |             N/A |    1.20x      N/A |       0 |   0/  0/   0.00
     2 |   0.027    10.0 |   0.034     7.8 |   0.028     9.5 |             N/A |             N/A |    1.05x      N/A |       3 |   0/  1/   0.00
     4 |   0.053    10.0 |   0.083     6.4 |   0.056     9.4 |             N/A |             N/A |    1.07x      N/A |      12 |   0/  1/   0.00
     8 |   0.078    13.5 |   0.123     8.6 |   0.079    13.3 |             N/A |             N/A |    1.02x      N/A |      18 |   0/  1/   0.00
    16 |   0.111    19.0 |   0.186    11.4 |   0.112    18.9 |             N/A |             N/A |    1.00x      N/A |      30 |   0/  2/   0.00
    32 |   0.172    24.6 |   0.301    14.0 |   0.169    24.9 |             N/A |             N/A |    0.99x      N/A |      54 |   0/  4/   0.00
    64 |   0.232    36.4 |   0.417    20.3 |   0.227    37.3 |             N/A |             N/A |    0.98x      N/A |      77 |   0/  5/   1.00
   128 |   0.293    57.8 |   0.526    32.1 |   0.288    58.7 |             N/A |             N/A |    0.98x      N/A |      99 |   0/  7/   2.00
   256 |   0.324   104.3 |   0.583    58.0 |   0.321   105.2 |             N/A |             N/A |    0.99x      N/A |     111 |   0/ 12/   4.00
   512 |   0.336   201.2 |   0.595   113.7 |   0.336   201.5 |             N/A |             N/A |    1.00x      N/A |     112 |   3/ 19/   9.00
  4096 |   0.399  1357.6 |   0.651   831.2 |   0.438  1236.8 |             N/A |             N/A |    1.10x      N/A |     112 |  35/127/  74.00
  8192 |   0.589  1836.1 |   0.769  1406.7 |   0.708  1528.4 |             N/A |             N/A |    1.20x      N/A |     112 |  64/252/ 149.50
 16384 |   1.085  1995.0 |   1.319  1640.7 |   1.259  1719.9 |             N/A |             N/A |    1.16x      N/A |     112 | 148/550/ 298.50
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```
