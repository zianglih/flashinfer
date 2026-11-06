# Six final public outputs

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
[2026-10-27 04:13:40.676] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

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
     1 |   0.028     3.2 |     0.031     2.8 |   0.035     2.5 |   0.025     3.5 |    0.031     2.8 |   0.052     1.7 |        0.91x         0.73x             0.81x            0.81x |   TRTLLM NVFP4    |       2 |   0/  1/   0.00
     2 |   0.035     5.0 |     0.039     4.5 |   0.040     4.4 |   0.037     4.8 |    0.044     4.0 |   0.077     2.3 |        1.05x         0.92x             0.95x            0.85x |   CuteDSL W4A4    |       4 |   0/  1/   0.00
     4 |   0.047     7.5 |     0.052     6.7 |   0.055     6.4 |   0.050     7.1 |    0.056     6.2 |   0.119     3.0 |        1.05x         0.90x             0.95x            0.88x |   CuteDSL W4A4    |       7 |   0/  1/   0.00
     8 |   0.060    11.7 |     0.065    10.9 |   0.069    10.2 |   0.064    11.1 |    0.070    10.0 |   0.155     4.5 |        1.06x         0.92x             0.98x            0.91x |   CuteDSL W4A4    |      10 |   0/  2/   0.00
    16 |   0.070    20.0 |     0.074    18.9 |   0.077    18.3 |   0.075    18.9 |    0.083    17.1 |   0.188     7.5 |        1.06x         0.97x             1.00x            0.90x |   CuteDSL W4A4    |      13 |   0/  2/   0.00
    32 |   0.102    27.8 |     0.105    26.8 |   0.111    25.4 |   0.105    26.8 |    0.112    25.2 |   0.285     9.9 |        1.04x         0.95x             1.00x            0.94x |   CuteDSL W4A4    |      21 |   0/  3/   1.00
    64 |   0.132    42.6 |     0.137    41.2 |   0.145    38.8 |   0.142    39.6 |    0.147    38.3 |   0.385    14.6 |        1.08x         0.98x             1.04x            0.97x |   CuteDSL W4A4    |      29 |   0/  5/   2.00
   128 |   0.138    81.6 |     0.143    78.8 |   0.149    75.7 |   0.142    79.4 |    0.150    75.4 |   0.399    28.2 |        1.03x         0.95x             0.99x            0.95x |   CuteDSL W4A4    |      30 |   0/  8/   3.00
   256 |   0.149   151.2 |     0.155   145.6 |   0.155   145.3 |   0.153   147.2 |    0.163   138.6 |   0.428    52.7 |        1.03x         0.99x             0.99x            0.94x |   CuteDSL W4A4    |      32 |   1/ 11/   7.00
   512 |   0.151   297.9 |     0.160   282.3 |   0.160   281.5 |   0.160   282.2 |    0.171   264.2 |   0.437   103.3 |        1.06x         1.00x             1.00x            0.94x |   CuteDSL W4A4    |      32 |   7/ 23/  14.00
  4096 |   0.208  1733.7 |     0.252  1432.2 |   0.318  1134.5 |   0.226  1597.6 |    0.270  1337.3 |   0.516   699.5 |        1.09x         0.71x             0.90x            0.84x |   CuteDSL W4A4    |      32 |  81/147/ 117.00
  8192 |   0.325  2219.4 |     0.384  1879.9 |   0.606  1190.4 |   0.364  1982.3 |    0.423  1706.9 |   0.815   885.7 |        1.12x         0.60x             0.95x            0.86x |   CuteDSL W4A4    |      32 | 174/347/ 251.50
 16384 |   0.527  2736.2 |     0.677  2130.3 |   1.197  1205.9 |   0.637  2265.1 |    0.761  1897.3 |   1.493   966.3 |        1.21x         0.53x             0.94x            0.84x |   CuteDSL W4A4    |      32 | 388/733/ 496.50
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
[2026-10-27 04:10:32.308] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

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
     1 |   0.027     3.2 |   0.033     2.7 |   0.029     3.1 |   0.032     2.7 |   0.048     1.8 |    1.05x    0.98x |       2 |   0/  1/   0.00
     2 |   0.034     5.2 |   0.047     3.8 |   0.038     4.7 |   0.050     3.5 |   0.077     2.3 |    1.12x    1.08x |       4 |   0/  1/   0.00
     4 |   0.047     7.5 |   0.070     5.0 |   0.050     7.0 |   0.075     4.7 |   0.118     3.0 |    1.08x    1.07x |       7 |   0/  1/   0.00
     8 |   0.061    11.5 |   0.093     7.6 |   0.064    11.0 |   0.100     7.1 |   0.155     4.5 |    1.05x    1.08x |      10 |   0/  2/   0.00
    16 |   0.069    20.5 |   0.111    12.7 |   0.074    19.1 |   0.116    12.1 |   0.188     7.5 |    1.07x    1.05x |      13 |   0/  2/   0.00
    32 |   0.100    28.2 |   0.167    16.8 |   0.103    27.4 |   0.167    16.9 |   0.286     9.9 |    1.03x    1.00x |      21 |   0/  3/   1.00
    64 |   0.131    42.9 |   0.225    25.1 |   0.138    40.8 |   0.225    25.0 |   0.384    14.7 |    1.05x    1.00x |      29 |   0/  5/   2.00
   128 |   0.136    83.1 |   0.230    49.0 |   0.138    81.5 |   0.232    48.5 |   0.401    28.1 |    1.02x    1.01x |      30 |   0/  8/   3.00
   256 |   0.143   157.8 |   0.243    92.8 |   0.149   151.7 |   0.248    90.9 |   0.426    52.9 |    1.04x    1.02x |      32 |   1/ 11/   7.00
   512 |   0.146   307.9 |   0.247   182.9 |   0.157   287.9 |   0.253   178.0 |   0.436   103.4 |    1.07x    1.03x |      32 |   7/ 23/  14.00
  4096 |   0.226  1597.6 |   0.305  1181.7 |   0.237  1523.4 |   0.316  1140.2 |   0.516   698.8 |    1.05x    1.04x |      32 |  81/147/ 117.00
  8192 |   0.374  1929.1 |   0.439  1644.3 |   0.403  1789.1 |   0.463  1557.2 |   0.803   898.7 |    1.08x    1.06x |      32 | 174/347/ 251.50
 16384 |   0.662  2180.0 |   0.725  1991.0 |   0.691  2088.5 |   0.742  1945.6 |   1.450   995.0 |    1.04x    1.02x |      32 | 388/733/ 496.50
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
[2026-10-27 04:23:20.068] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

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
     1 |   0.011     9.3 |     0.014     7.8 |   0.011    10.0 |   0.012     8.9 |    0.015     7.3 |   0.010    11.0 |        1.05x         1.13x             0.88x            0.82x |    TRTLLM BF16    |       0 |   0/  0/   0.00
     2 |   0.021    10.2 |     0.024     8.9 |   0.026     8.3 |   0.017    12.5 |    0.024     8.8 |   0.029     7.3 |        0.82x         0.66x             0.71x            0.70x |   TRTLLM NVFP4    |       1 |   0/  1/   0.00
     4 |   0.035    12.2 |     0.040    10.6 |   0.042    10.1 |   0.037    11.6 |    0.044     9.7 |   0.087     4.9 |        1.06x         0.88x             0.92x            0.84x |   CuteDSL W4A4    |       6 |   0/  1/   0.00
     8 |   0.049    17.4 |     0.053    16.1 |   0.055    15.5 |   0.051    16.5 |    0.058    14.6 |   0.128     6.6 |        1.05x         0.94x             0.97x            0.88x |   CuteDSL W4A4    |      10 |   0/  2/   0.00
    16 |   0.065    25.9 |     0.070    24.4 |   0.072    23.6 |   0.069    24.7 |    0.076    22.2 |   0.176     9.6 |        1.05x         0.96x             0.99x            0.90x |   CuteDSL W4A4    |      15 |   0/  2/   0.00
    32 |   0.128    26.6 |     0.132    25.8 |   0.137    24.9 |   0.132    25.8 |    0.139    24.4 |   0.369     9.2 |        1.03x         0.96x             1.00x            0.94x |   CuteDSL W4A4    |      35 |   0/  4/   0.00
    64 |   0.205    33.2 |     0.210    32.4 |   0.219    31.1 |   0.211    32.2 |    0.219    31.0 |   0.625    10.9 |        1.03x         0.96x             1.00x            0.96x |   CuteDSL W4A4    |      61 |   0/  4/   1.00
   128 |   0.264    51.6 |     0.272    49.9 |   0.280    48.6 |   0.269    50.5 |    0.278    48.9 |   0.829    16.4 |        1.02x         0.96x             0.99x            0.97x |   CuteDSL W4A4    |      82 |   0/  6/   2.00
   256 |   0.302    90.1 |     0.313    86.7 |   0.320    85.0 |   0.308    88.3 |    0.319    85.2 |   0.958    28.4 |        1.02x         0.96x             0.98x            0.97x |   CuteDSL W4A4    |      95 |   0/ 11/   4.00
   512 |   0.307   177.0 |     0.324   167.8 |   0.324   167.6 |   0.315   172.4 |    0.329   165.3 |   0.975    55.8 |        1.03x         0.97x             0.97x            0.96x |   CuteDSL W4A4    |      96 |   2/ 16/   8.00
  4096 |   0.349  1245.0 |     0.402  1081.2 |   0.557   780.9 |   0.365  1189.9 |    0.414  1050.8 |   1.049   414.6 |        1.05x         0.66x             0.91x            0.88x |   CuteDSL W4A4    |      96 |  42/ 84/  63.00
  8192 |   0.424  2052.9 |     0.515  1689.6 |   0.872   997.0 |   0.458  1900.7 |    0.528  1647.5 |   1.296   671.2 |        1.08x         0.52x             0.89x            0.87x |   CuteDSL W4A4    |      96 |  95/162/ 126.50
 16384 |   0.650  2675.9 |     0.808  2153.0 |   1.616  1076.4 |   0.707  2460.7 |    0.846  2056.9 |   2.058   845.3 |        1.09x         0.44x             0.87x            0.84x |   CuteDSL W4A4    |      96 | 198/337/ 254.00
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
[2026-10-27 04:26:22.035] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

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
     1 |   0.010    10.6 |   0.010    10.7 |   0.011     9.9 |   0.010    10.2 |   0.010    10.7 |    1.07x    1.05x |       0 |   0/  0/   0.00
     2 |   0.021     9.9 |   0.024     9.0 |   0.019    11.0 |   0.020    10.6 |   0.029     7.4 |    0.90x    0.84x |       1 |   0/  1/   0.00
     4 |   0.036    11.8 |   0.050     8.4 |   0.038    11.2 |   0.054     7.9 |   0.087     4.9 |    1.05x    1.07x |       6 |   0/  1/   0.00
     8 |   0.048    17.9 |   0.074    11.5 |   0.052    16.4 |   0.077    11.0 |   0.128     6.6 |    1.09x    1.04x |      10 |   0/  2/   0.00
    16 |   0.065    26.2 |   0.103    16.5 |   0.069    24.6 |   0.106    16.0 |   0.177     9.6 |    1.07x    1.03x |      15 |   0/  2/   0.00
    32 |   0.123    27.5 |   0.213    15.9 |   0.128    26.6 |   0.212    16.0 |   0.369     9.2 |    1.04x    0.99x |      35 |   0/  4/   0.00
    64 |   0.196    34.7 |   0.352    19.3 |   0.202    33.7 |   0.348    19.5 |   0.624    10.9 |    1.03x    0.99x |      61 |   0/  4/   1.00
   128 |   0.255    53.3 |   0.462    29.4 |   0.260    52.4 |   0.455    29.9 |   0.829    16.4 |    1.02x    0.98x |      82 |   0/  6/   2.00
   256 |   0.294    92.5 |   0.530    51.3 |   0.298    91.1 |   0.526    51.7 |   0.958    28.4 |    1.02x    0.99x |      95 |   0/ 11/   4.00
   512 |   0.299   181.8 |   0.536   101.4 |   0.304   178.8 |   0.536   101.4 |   0.975    55.8 |    1.02x    1.00x |      96 |   2/ 16/   8.00
  4096 |   0.354  1227.8 |   0.586   741.6 |   0.387  1124.1 |   0.588   739.9 |   1.049   414.7 |    1.09x    1.00x |      96 |  42/ 84/  63.00
  8192 |   0.495  1756.8 |   0.671  1295.3 |   0.526  1653.7 |   0.684  1271.1 |   1.306   665.8 |    1.06x    1.02x |      96 |  95/162/ 126.50
 16384 |   0.850  2047.1 |   1.007  1727.5 |   0.866  2009.5 |   1.045  1664.1 |   2.058   845.4 |    1.02x    1.04x |      96 | 198/337/ 254.00
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
[2026-10-27 04:22:58.811] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

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
     1 |   0.014     9.6 |     0.015     8.7 |   0.013    10.3 |   0.014     9.5 |              N/A |             N/A |        1.02x         1.08x             0.92x              N/A |   CuteDSL W4A16   |       0 |   0/  0/   0.00
     2 |   0.027     9.7 |     0.031     8.6 |   0.031     8.6 |   0.025    10.5 |              N/A |             N/A |        0.92x         0.81x             0.81x              N/A |   TRTLLM NVFP4    |       3 |   0/  1/   0.00
     4 |   0.054     9.8 |     0.057     9.2 |   0.059     8.9 |   0.056     9.5 |              N/A |             N/A |        1.03x         0.94x             0.97x              N/A |   CuteDSL W4A4    |      12 |   0/  1/   0.00
     8 |   0.082    12.8 |     0.086    12.3 |   0.087    12.2 |   0.083    12.8 |              N/A |             N/A |        1.00x         0.95x             0.96x              N/A |   CuteDSL W4A4    |      18 |   0/  1/   0.00
    16 |   0.116    18.2 |     0.120    17.5 |   0.122    17.4 |   0.116    18.3 |              N/A |             N/A |        1.00x         0.95x             0.96x              N/A |   TRTLLM NVFP4    |      30 |   0/  2/   0.00
    32 |   0.178    23.8 |     0.182    23.2 |   0.188    22.5 |   0.177    23.9 |              N/A |             N/A |        1.00x         0.94x             0.97x              N/A |   TRTLLM NVFP4    |      54 |   0/  4/   0.00
    64 |   0.238    35.5 |     0.246    34.4 |   0.254    33.4 |   0.236    35.9 |              N/A |             N/A |        0.99x         0.93x             0.96x              N/A |   TRTLLM NVFP4    |      77 |   0/  5/   1.00
   128 |   0.297    57.0 |     0.307    55.1 |   0.316    53.5 |   0.299    56.5 |              N/A |             N/A |        1.01x         0.95x             0.97x              N/A |   CuteDSL W4A4    |      99 |   0/  7/   2.00
   256 |   0.331   102.3 |     0.340    99.4 |   0.358    94.6 |   0.332   102.0 |              N/A |             N/A |        1.00x         0.93x             0.97x              N/A |   CuteDSL W4A4    |     111 |   0/ 12/   4.00
   512 |   0.339   199.7 |     0.353   191.4 |   0.374   180.6 |   0.339   199.8 |              N/A |             N/A |        1.00x         0.90x             0.96x              N/A |   TRTLLM NVFP4    |     112 |   3/ 19/   9.00
  4096 |   0.388  1395.8 |     0.446  1212.3 |   0.610   887.6 |   0.411  1315.5 |              N/A |             N/A |        1.06x         0.67x             0.92x              N/A |   CuteDSL W4A4    |     112 |  35/127/  74.00
  8192 |   0.499  2168.9 |     0.650  1665.0 |   1.111   974.2 |   0.552  1961.2 |              N/A |             N/A |        1.11x         0.50x             0.85x              N/A |   CuteDSL W4A4    |     112 |  64/252/ 149.50
 16384 |   0.801  2702.8 |     1.106  1956.5 |   2.082  1039.5 |   0.852  2541.5 |              N/A |             N/A |        1.06x         0.41x             0.77x              N/A |   CuteDSL W4A4    |     112 | 148/550/ 298.50
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
[2026-10-27 04:25:21.813] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

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
     1 |   0.010    12.9 |   0.012    10.7 |   0.012    10.6 |             N/A |             N/A |    1.22x      N/A |       0 |   0/  0/   0.00
     2 |   0.026    10.0 |   0.034     7.8 |   0.028     9.6 |             N/A |             N/A |    1.05x      N/A |       3 |   0/  1/   0.00
     4 |   0.053    10.0 |   0.082     6.4 |   0.057     9.2 |             N/A |             N/A |    1.08x      N/A |      12 |   0/  1/   0.00
     8 |   0.078    13.6 |   0.122     8.7 |   0.080    13.2 |             N/A |             N/A |    1.03x      N/A |      18 |   0/  1/   0.00
    16 |   0.110    19.1 |   0.184    11.5 |   0.113    18.8 |             N/A |             N/A |    1.02x      N/A |      30 |   0/  2/   0.00
    32 |   0.173    24.5 |   0.301    14.1 |   0.169    25.0 |             N/A |             N/A |    0.98x      N/A |      54 |   0/  4/   0.00
    64 |   0.232    36.4 |   0.415    20.4 |   0.226    37.4 |             N/A |             N/A |    0.98x      N/A |      77 |   0/  5/   1.00
   128 |   0.292    57.9 |   0.522    32.4 |   0.288    58.8 |             N/A |             N/A |    0.98x      N/A |      99 |   0/  7/   2.00
   256 |   0.323   104.8 |   0.578    58.5 |   0.322   105.0 |             N/A |             N/A |    1.00x      N/A |     111 |   0/ 12/   4.00
   512 |   0.336   201.1 |   0.589   114.8 |   0.334   202.4 |             N/A |             N/A |    0.99x      N/A |     112 |   3/ 19/   9.00
  4096 |   0.399  1357.6 |   0.651   831.3 |   0.437  1238.0 |             N/A |             N/A |    1.10x      N/A |     112 |  35/127/  74.00
  8192 |   0.589  1837.9 |   0.769  1406.8 |   0.761  1422.6 |             N/A |             N/A |    1.29x      N/A |     112 |  64/252/ 149.50
 16384 |   1.162  1863.4 |   1.314  1647.6 |   1.215  1781.3 |             N/A |             N/A |    1.05x      N/A |     112 | 148/550/ 298.50
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```
