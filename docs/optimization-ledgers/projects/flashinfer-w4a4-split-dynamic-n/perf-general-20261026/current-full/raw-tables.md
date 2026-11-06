# Six current-source public outputs

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
[2026-10-27 02:27:13.357] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

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
     1 |   0.028     3.1 |     0.032     2.8 |   0.035     2.5 |   0.026     3.4 |    0.032     2.7 |   0.052     1.7 |        0.92x         0.75x             0.82x            0.81x |   TRTLLM NVFP4    |       2 |   0/  1/   0.00
     2 |   0.036     5.0 |     0.039     4.6 |   0.040     4.4 |   0.036     5.0 |    0.043     4.1 |   0.076     2.3 |        1.00x         0.88x             0.92x            0.83x |   TRTLLM NVFP4    |       4 |   0/  1/   0.00
     4 |   0.047     7.5 |     0.051     7.0 |   0.055     6.4 |   0.053     6.6 |    0.056     6.3 |   0.119     3.0 |        1.13x         0.96x             1.05x            0.96x |   CuteDSL W4A4    |       7 |   0/  1/   0.00
     8 |   0.060    11.7 |     0.064    10.9 |   0.069    10.2 |   0.064    11.0 |    0.070    10.1 |   0.155     4.5 |        1.06x         0.92x             0.99x            0.91x |   CuteDSL W4A4    |      10 |   0/  2/   0.00
    16 |   0.071    20.0 |     0.076    18.6 |   0.079    17.9 |   0.074    18.9 |    0.082    17.2 |   0.188     7.5 |        1.05x         0.95x             0.98x            0.91x |   CuteDSL W4A4    |      13 |   0/  2/   0.00
    32 |   0.103    27.3 |     0.106    26.5 |   0.111    25.4 |   0.104    27.0 |    0.111    25.3 |   0.286     9.9 |        1.01x         0.94x             0.98x            0.94x |   CuteDSL W4A4    |      21 |   0/  3/   1.00
    64 |   0.133    42.3 |     0.138    40.9 |   0.145    39.0 |   0.141    40.0 |    0.147    38.4 |   0.385    14.6 |        1.06x         0.97x             1.02x            0.96x |   CuteDSL W4A4    |      29 |   0/  5/   2.00
   128 |   0.139    81.1 |     0.145    77.6 |   0.148    76.1 |   0.142    79.3 |    0.151    74.8 |   0.399    28.3 |        1.02x         0.96x             0.98x            0.94x |   CuteDSL W4A4    |      30 |   0/  8/   3.00
   256 |   0.149   151.3 |     0.157   143.7 |   0.155   145.0 |   0.154   146.7 |    0.162   139.0 |   0.428    52.7 |        1.03x         0.99x             0.98x            0.95x |   CuteDSL W4A4    |      32 |   1/ 11/   7.00
   512 |   0.151   298.4 |     0.167   269.3 |   0.160   281.7 |   0.160   282.2 |    0.171   263.3 |   0.436   103.4 |        1.06x         1.00x             0.95x            0.93x |   CuteDSL W4A4    |      32 |   7/ 23/  14.00
  4096 |   0.209  1730.1 |     0.296  1217.5 |   0.316  1142.8 |   0.225  1606.0 |    0.275  1311.3 |   0.515   700.2 |        1.08x         0.71x             0.76x            0.82x |   CuteDSL W4A4    |      32 |  81/147/ 117.00
  8192 |   0.326  2213.6 |     0.449  1608.0 |   0.605  1193.1 |   0.362  1992.3 |    0.421  1714.4 |   0.796   906.8 |        1.11x         0.60x             0.81x            0.86x |   CuteDSL W4A4    |      32 | 174/347/ 251.50
 16384 |   0.526  2742.7 |     0.801  1802.7 |   1.207  1195.8 |   0.636  2269.4 |    0.759  1900.9 |   1.498   963.7 |        1.21x         0.53x             0.79x            0.84x |   CuteDSL W4A4    |      32 | 388/733/ 496.50
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
[2026-10-27 02:36:15.387] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

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
     1 |   0.028     3.1 |   0.034     2.6 |   0.027     3.3 |   0.033     2.7 |   0.052     1.7 |    0.95x    0.96x |       2 |   0/  1/   0.00
     2 |   0.034     5.1 |   0.048     3.7 |   0.037     4.8 |   0.050     3.5 |   0.078     2.3 |    1.07x    1.05x |       4 |   0/  1/   0.00
     4 |   0.047     7.5 |   0.069     5.1 |   0.051     6.9 |   0.077     4.6 |   0.121     2.9 |    1.08x    1.12x |       7 |   0/  1/   0.00
     8 |   0.062    11.4 |   0.096     7.4 |   0.065    10.9 |   0.100     7.1 |   0.155     4.5 |    1.05x    1.04x |      10 |   0/  2/   0.00
    16 |   0.070    20.2 |   0.112    12.6 |   0.076    18.6 |   0.117    12.1 |   0.188     7.5 |    1.09x    1.04x |      13 |   0/  2/   0.00
    32 |   0.101    28.0 |   0.168    16.8 |   0.103    27.4 |   0.167    16.9 |   0.284     9.9 |    1.02x    1.00x |      21 |   0/  3/   1.00
    64 |   0.133    42.5 |   0.224    25.1 |   0.138    40.8 |   0.224    25.1 |   0.386    14.6 |    1.04x    1.00x |      29 |   0/  5/   2.00
   128 |   0.136    83.1 |   0.231    48.8 |   0.139    81.2 |   0.232    48.6 |   0.401    28.1 |    1.02x    1.00x |      30 |   0/  8/   3.00
   256 |   0.145   156.0 |   0.246    91.7 |   0.147   153.0 |   0.250    90.3 |   0.428    52.7 |    1.02x    1.02x |      32 |   1/ 11/   7.00
   512 |   0.147   306.3 |   0.247   182.2 |   0.157   288.1 |   0.256   176.1 |   0.437   103.3 |    1.06x    1.03x |      32 |   7/ 23/  14.00
  4096 |   0.227  1591.5 |   0.306  1177.9 |   0.238  1517.2 |   0.316  1141.2 |   0.515   700.0 |    1.05x    1.03x |      32 |  81/147/ 117.00
  8192 |   0.380  1899.8 |   0.447  1612.8 |   0.403  1789.1 |   0.464  1555.5 |   0.803   898.5 |    1.06x    1.04x |      32 | 174/347/ 251.50
 16384 |   0.664  2174.0 |   0.739  1952.4 |   0.706  2043.1 |   0.790  1826.6 |   1.534   940.8 |    1.06x    1.07x |      32 | 388/733/ 496.50
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
[2026-10-27 02:33:47.559] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

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
     1 |   0.011     9.3 |     0.015     7.3 |   0.011     9.8 |   0.012     9.1 |    0.014     7.5 |   0.012     8.9 |        1.03x         1.09x             0.81x            0.83x |   CuteDSL W4A16   |       0 |   0/  0/   0.00
     2 |   0.021    10.0 |     0.024     8.7 |   0.026     8.3 |   0.018    12.1 |    0.023     9.3 |   0.029     7.4 |        0.83x         0.69x             0.72x            0.77x |   TRTLLM NVFP4    |       1 |   0/  1/   0.00
     4 |   0.036    11.8 |     0.039    10.8 |   0.042    10.0 |   0.036    11.7 |    0.044     9.6 |   0.086     4.9 |        1.01x         0.86x             0.92x            0.83x |   CuteDSL W4A4    |       6 |   0/  1/   0.00
     8 |   0.049    17.3 |     0.053    15.9 |   0.056    15.1 |   0.051    16.6 |    0.058    14.6 |   0.127     6.7 |        1.04x         0.91x             0.96x            0.88x |   CuteDSL W4A4    |      10 |   0/  2/   0.00
    16 |   0.066    25.6 |     0.073    23.2 |   0.072    23.7 |   0.069    24.7 |    0.076    22.3 |   0.177     9.6 |        1.03x         0.96x             0.94x            0.90x |   CuteDSL W4A4    |      15 |   0/  2/   0.00
    32 |   0.128    26.6 |     0.137    24.9 |   0.137    24.9 |   0.132    25.7 |    0.139    24.4 |   0.369     9.2 |        1.03x         0.97x             0.97x            0.95x |   CuteDSL W4A4    |      35 |   0/  4/   0.00
    64 |   0.206    33.0 |     0.217    31.4 |   0.217    31.2 |   0.209    32.4 |    0.219    31.1 |   0.625    10.9 |        1.02x         0.96x             0.97x            0.96x |   CuteDSL W4A4    |      61 |   0/  4/   1.00
   128 |   0.267    50.8 |     0.279    48.6 |   0.280    48.5 |   0.269    50.4 |    0.278    48.8 |   0.828    16.4 |        1.01x         0.96x             0.96x            0.97x |   CuteDSL W4A4    |      82 |   0/  6/   2.00
   256 |   0.305    89.1 |     0.321    84.8 |   0.319    85.2 |   0.309    88.1 |    0.319    85.2 |   0.957    28.4 |        1.01x         0.97x             0.96x            0.97x |   CuteDSL W4A4    |      95 |   0/ 11/   4.00
   512 |   0.310   175.3 |     0.328   165.8 |   0.323   168.1 |   0.315   172.7 |    0.330   164.8 |   0.975    55.8 |        1.02x         0.97x             0.96x            0.95x |   CuteDSL W4A4    |      96 |   2/ 16/   8.00
  4096 |   0.349  1247.2 |     0.448   970.3 |   0.569   763.7 |   0.367  1185.9 |    0.425  1022.6 |   1.047   415.3 |        1.05x         0.64x             0.82x            0.86x |   CuteDSL W4A4    |      96 |  42/ 84/  63.00
  8192 |   0.422  2062.8 |     0.598  1455.4 |   0.921   944.1 |   0.462  1883.6 |    0.530  1641.3 |   1.291   673.8 |        1.10x         0.50x             0.77x            0.87x |   CuteDSL W4A4    |      96 |  95/162/ 126.50
 16384 |   0.653  2662.6 |     0.930  1871.1 |   1.668  1043.0 |   0.700  2485.9 |    0.848  2050.8 |   2.046   850.2 |        1.07x         0.42x             0.75x            0.82x |   CuteDSL W4A4    |      96 | 198/337/ 254.00
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
[2026-10-27 02:49:03.133] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

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
     1 |   0.010    10.7 |   0.010    10.3 |   0.010    10.5 |   0.011    10.0 |   0.010    11.1 |    1.02x    1.03x |       0 |   0/  0/   0.00
     2 |   0.022     9.7 |   0.025     8.6 |   0.019    11.2 |   0.020    10.6 |   0.029     7.4 |    0.87x    0.81x |       1 |   0/  1/   0.00
     4 |   0.036    11.7 |   0.053     8.1 |   0.038    11.1 |   0.053     7.9 |   0.087     4.9 |    1.06x    1.02x |       6 |   0/  1/   0.00
     8 |   0.048    17.7 |   0.074    11.4 |   0.052    16.3 |   0.078    10.9 |   0.128     6.6 |    1.08x    1.05x |      10 |   0/  2/   0.00
    16 |   0.065    26.3 |   0.103    16.4 |   0.068    24.9 |   0.106    16.0 |   0.177     9.6 |    1.06x    1.03x |      15 |   0/  2/   0.00
    32 |   0.124    27.5 |   0.215    15.8 |   0.128    26.5 |   0.212    16.1 |   0.369     9.2 |    1.04x    0.99x |      35 |   0/  4/   0.00
    64 |   0.198    34.3 |   0.356    19.1 |   0.202    33.7 |   0.348    19.5 |   0.623    10.9 |    1.02x    0.98x |      61 |   0/  4/   1.00
   128 |   0.258    52.6 |   0.468    29.1 |   0.259    52.4 |   0.455    29.9 |   0.828    16.4 |    1.00x    0.97x |      82 |   0/  6/   2.00
   256 |   0.297    91.4 |   0.539    50.5 |   0.299    90.8 |   0.526    51.6 |   0.957    28.4 |    1.01x    0.98x |      95 |   0/ 11/   4.00
   512 |   0.302   180.2 |   0.545    99.7 |   0.304   178.9 |   0.536   101.4 |   0.974    55.8 |    1.01x    0.98x |      96 |   2/ 16/   8.00
  4096 |   0.355  1225.5 |   0.587   740.3 |   0.388  1121.1 |   0.589   738.2 |   1.049   414.4 |    1.09x    1.00x |      96 |  42/ 84/  63.00
  8192 |   0.495  1758.5 |   0.674  1290.2 |   0.517  1683.0 |   0.679  1280.3 |   1.297   670.7 |    1.04x    1.01x |      96 |  95/162/ 126.50
 16384 |   0.864  2012.4 |   0.966  1800.1 |   0.910  1910.9 |   1.062  1638.5 |   2.042   851.8 |    1.05x    1.10x |      96 | 198/337/ 254.00
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
[2026-10-27 02:31:39.734] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

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
     1 |   0.013    10.2 |     0.015     8.7 |   0.013    10.3 |   0.014     9.3 |              N/A |             N/A |        1.10x         1.11x             0.93x              N/A |   CuteDSL W4A16   |       0 |   0/  0/   0.00
     2 |   0.027     9.8 |     0.031     8.5 |   0.031     8.6 |   0.025    10.6 |              N/A |             N/A |        0.92x         0.81x             0.81x              N/A |   TRTLLM NVFP4    |       3 |   0/  1/   0.00
     4 |   0.054     9.7 |     0.061     8.7 |   0.060     8.9 |   0.055     9.5 |              N/A |             N/A |        1.02x         0.93x             0.92x              N/A |   CuteDSL W4A4    |      12 |   0/  1/   0.00
     8 |   0.081    13.0 |     0.091    11.7 |   0.085    12.5 |   0.083    12.7 |              N/A |             N/A |        1.02x         0.98x             0.92x              N/A |   CuteDSL W4A4    |      18 |   0/  1/   0.00
    16 |   0.116    18.2 |     0.125    16.9 |   0.122    17.4 |   0.115    18.3 |              N/A |             N/A |        1.00x         0.95x             0.92x              N/A |   TRTLLM NVFP4    |      30 |   0/  2/   0.00
    32 |   0.178    23.8 |     0.188    22.4 |   0.187    22.6 |   0.176    24.0 |              N/A |             N/A |        0.99x         0.94x             0.93x              N/A |   TRTLLM NVFP4    |      54 |   0/  4/   0.00
    64 |   0.242    35.0 |     0.253    33.4 |   0.253    33.4 |   0.236    35.9 |              N/A |             N/A |        0.97x         0.93x             0.93x              N/A |   TRTLLM NVFP4    |      77 |   0/  5/   1.00
   128 |   0.300    56.4 |     0.316    53.4 |   0.315    53.7 |   0.300    56.3 |              N/A |             N/A |        1.00x         0.95x             0.95x              N/A |   CuteDSL W4A4    |      99 |   0/  7/   2.00
   256 |   0.335   101.1 |     0.356    95.1 |   0.357    94.8 |   0.332   101.9 |              N/A |             N/A |        0.99x         0.93x             0.93x              N/A |   TRTLLM NVFP4    |     111 |   0/ 12/   4.00
   512 |   0.344   196.8 |     0.378   179.0 |   0.373   181.3 |   0.339   199.7 |              N/A |             N/A |        0.99x         0.91x             0.90x              N/A |   TRTLLM NVFP4    |     112 |   3/ 19/   9.00
  4096 |   0.387  1398.4 |     0.557   971.5 |   0.661   818.3 |   0.410  1318.8 |              N/A |             N/A |        1.06x         0.62x             0.74x              N/A |   CuteDSL W4A4    |     112 |  35/127/  74.00
  8192 |   0.500  2166.5 |     0.877  1234.0 |   1.075  1006.9 |   0.542  1995.5 |              N/A |             N/A |        1.09x         0.50x             0.62x              N/A |   CuteDSL W4A4    |     112 |  64/252/ 149.50
 16384 |   0.797  2715.0 |     1.438  1505.0 |   2.096  1032.9 |   0.841  2574.6 |              N/A |             N/A |        1.05x         0.40x             0.58x              N/A |   CuteDSL W4A4    |     112 | 148/550/ 298.50
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
[2026-10-27 02:45:38.832] [info] TRT-LLM fused MoE cooperative launch SM allocation: 140 SMs used for MoE, 8 SMs reserved for overlapping kernels (total SMs: 148)

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
     1 |   0.010    12.6 |   0.012    11.5 |   0.012    10.6 |             N/A |             N/A |    1.19x      N/A |       0 |   0/  0/   0.00
     2 |   0.027     9.9 |   0.034     7.8 |   0.028     9.6 |             N/A |             N/A |    1.03x      N/A |       3 |   0/  1/   0.00
     4 |   0.053     9.9 |   0.082     6.4 |   0.056     9.5 |             N/A |             N/A |    1.05x      N/A |      12 |   0/  1/   0.00
     8 |   0.079    13.4 |   0.123     8.6 |   0.080    13.2 |             N/A |             N/A |    1.01x      N/A |      18 |   0/  1/   0.00
    16 |   0.112    18.9 |   0.186    11.4 |   0.112    18.8 |             N/A |             N/A |    1.00x      N/A |      30 |   0/  2/   0.00
    32 |   0.174    24.4 |   0.302    14.0 |   0.170    24.9 |             N/A |             N/A |    0.98x      N/A |      54 |   0/  4/   0.00
    64 |   0.234    36.1 |   0.419    20.2 |   0.227    37.3 |             N/A |             N/A |    0.97x      N/A |      77 |   0/  5/   1.00
   128 |   0.295    57.4 |   0.526    32.1 |   0.288    58.7 |             N/A |             N/A |    0.98x      N/A |      99 |   0/  7/   2.00
   256 |   0.325   104.1 |   0.583    58.0 |   0.321   105.3 |             N/A |             N/A |    0.99x      N/A |     111 |   0/ 12/   4.00
   512 |   0.338   200.2 |   0.596   113.5 |   0.335   202.1 |             N/A |             N/A |    0.99x      N/A |     112 |   3/ 19/   9.00
  4096 |   0.399  1357.6 |   0.651   831.5 |   0.437  1237.2 |             N/A |             N/A |    1.10x      N/A |     112 |  35/127/  74.00
  8192 |   0.597  1812.6 |   0.767  1412.0 |   0.710  1524.6 |             N/A |             N/A |    1.19x      N/A |     112 |  64/252/ 149.50
 16384 |   1.138  1901.7 |   1.361  1591.1 |   1.272  1701.7 |             N/A |             N/A |    1.12x      N/A |     112 | 148/550/ 298.50
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```
