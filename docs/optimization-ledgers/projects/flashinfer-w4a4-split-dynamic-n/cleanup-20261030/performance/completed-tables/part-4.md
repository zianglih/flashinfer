<!-- pr7290-completed-tables-326c4a79-part-4 -->
### Benchmark table output — K3 TP8 / N3U TP8 (4/4)

Printed by the unchanged benchmark table functions from saved records: fresh CuTe DSL final-pass results at `326c4a79` plus the original TRTLLM final-pass results. TRTLLM is reused, not rerun; these are separate-run comparisons. The heatmaps use two-pass aggregates. Missing or unsupported records remain N/A. [Original fresh-run logs](https://raw.githubusercontent.com/zianglih/flashinfer/9390a1a47d03def09be35f3b2be5be4b39f06d55/pr7290/2026-10-30/326c4a79-cleanup/native-stdout.tar.gz).

**K3 TP8 · NVFP4**

```text

=====================================================================================================================================================================================================================================
Kimi-K3 MoE Benchmark: CuteDSL W4A4 / PER-TOKEN / W4A16 vs TRTLLM NVFP4 / PER-TOKEN / BF16 (EP=1, TP=8)
=====================================================================================================================================================================================================================================
Model: hidden=3584, intermediate=384, experts=896, top_k=16
EP Config: 896 local experts (simulating 1-way parallelism)
TP Config: intermediate size 384 (simulating 8-way parallelism)
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
     1 |   0.025     5.4 |     0.028     4.8 |   0.027     4.8 |   0.021     6.3 |              N/A |             N/A |        0.85x         0.77x             0.76x              N/A |   TRTLLM NVFP4    |      16 |   0/  1/   0.00
     2 |   0.032     8.2 |     0.037     7.1 |   0.038     6.9 |   0.030     8.9 |              N/A |             N/A |        0.93x         0.77x             0.80x              N/A |   TRTLLM NVFP4    |      32 |   0/  1/   0.00
     4 |   0.042    12.5 |     0.047    11.2 |   0.050    10.6 |   0.043    12.2 |              N/A |             N/A |        1.03x         0.88x             0.92x              N/A |   CuteDSL W4A4    |      63 |   0/  2/   0.00
     8 |   0.077    13.8 |     0.082    13.0 |   0.088    12.1 |   0.077    13.7 |              N/A |             N/A |        1.00x         0.88x             0.95x              N/A |   CuteDSL W4A4    |     124 |   0/  2/   0.00
    16 |   0.112    18.9 |     0.120    17.7 |   0.128    16.6 |   0.115    18.4 |              N/A |             N/A |        1.03x         0.90x             0.96x              N/A |   CuteDSL W4A4    |     222 |   0/  3/   0.00
    32 |   0.167    25.4 |     0.177    23.9 |   0.187    22.6 |   0.173    24.4 |              N/A |             N/A |        1.04x         0.93x             0.98x              N/A |   CuteDSL W4A4    |     392 |   0/  4/   0.00
    64 |   0.237    35.7 |     0.249    33.9 |   0.272    31.1 |   0.246    34.4 |              N/A |             N/A |        1.04x         0.90x             0.99x              N/A |   CuteDSL W4A4    |     593 |   0/  5/   1.00
   128 |   0.306    55.3 |     0.317    53.4 |   0.346    48.9 |   0.317    53.3 |              N/A |             N/A |        1.04x         0.92x             1.00x              N/A |   CuteDSL W4A4    |     787 |   0/ 10/   2.00
   256 |   0.342    99.0 |     0.354    95.6 |   0.382    88.5 |   0.355    95.4 |              N/A |             N/A |        1.04x         0.93x             1.00x              N/A |   CuteDSL W4A4    |     883 |   0/ 15/   4.00
   512 |   0.358   188.8 |     0.375   180.5 |   0.409   165.4 |   0.371   182.3 |              N/A |             N/A |        1.04x         0.91x             0.99x              N/A |   CuteDSL W4A4    |     895 |   0/ 22/   9.00
  4096 |   0.554   976.6 |     0.663   816.2 |   0.679   797.6 |   0.546   991.9 |              N/A |             N/A |        0.98x         0.80x             0.82x              N/A |   TRTLLM NVFP4    |     896 |  21/175/  72.00
  8192 |   0.794  1363.4 |     1.048  1033.0 |   1.258   860.4 |   0.949  1140.2 |              N/A |             N/A |        1.20x         0.75x             0.91x              N/A |   CuteDSL W4A4    |     896 |  55/312/ 143.00
 16384 |   1.396  1550.1 |     1.954  1107.9 |   2.357   918.3 |   1.666  1299.2 |              N/A |             N/A |        1.19x         0.71x             0.85x              N/A |   CuteDSL W4A4    |     896 | 119/728/ 290.50
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

**K3 TP8 · MXFP**

```text

================================================================================================================================================
Kimi-K3 MoE Benchmark: CuteDSL MXFP4x8 / MXFP8 vs TRTLLM MXFP4x8 / MXFP8 / BF16 (EP=1, TP=8)
================================================================================================================================================
Model: hidden=3584, intermediate=384, experts=896, top_k=16
EP Config: 896 local experts (simulating 1-way parallelism)
TP Config: intermediate size 384 (simulating 8-way parallelism)
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
     1 |   0.024     5.6 |             N/A |   0.020     6.5 |             N/A |             N/A |    0.86x      N/A |      16 |   0/  1/   0.00
     2 |   0.031     8.6 |             N/A |   0.030     8.8 |             N/A |             N/A |    0.97x      N/A |      32 |   0/  1/   0.00
     4 |   0.042    12.5 |             N/A |   0.044    12.0 |             N/A |             N/A |    1.04x      N/A |      63 |   0/  2/   0.00
     8 |   0.079    13.4 |             N/A |   0.076    14.0 |             N/A |             N/A |    0.96x      N/A |     124 |   0/  2/   0.00
    16 |   0.120    17.6 |             N/A |   0.113    18.7 |             N/A |             N/A |    0.94x      N/A |     222 |   0/  3/   0.00
    32 |   0.166    25.5 |             N/A |   0.168    25.1 |             N/A |             N/A |    1.01x      N/A |     392 |   0/  4/   0.00
    64 |   0.230    36.8 |             N/A |   0.241    35.1 |             N/A |             N/A |    1.05x      N/A |     593 |   0/  5/   1.00
   128 |   0.293    57.7 |             N/A |   0.308    54.9 |             N/A |             N/A |    1.05x      N/A |     787 |   0/ 10/   2.00
   256 |   0.326   103.8 |             N/A |   0.346    97.7 |             N/A |             N/A |    1.06x      N/A |     883 |   0/ 15/   4.00
   512 |   0.348   194.2 |             N/A |   0.369   183.5 |             N/A |             N/A |    1.06x      N/A |     895 |   0/ 22/   9.00
  4096 |   0.548   988.2 |             N/A |   0.572   946.7 |             N/A |             N/A |    1.04x      N/A |     896 |  21/175/  72.00
  8192 |   0.881  1228.3 |             N/A |   0.952  1136.7 |             N/A |             N/A |    1.08x      N/A |     896 |  55/312/ 143.00
 16384 |   1.584  1366.5 |             N/A |   1.665  1300.0 |             N/A |             N/A |    1.05x      N/A |     896 | 119/728/ 290.50
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

**N3U TP8 · NVFP4**

```text

=====================================================================================================================================================================================================================================
Nemotron-3-Ultra MoE Benchmark: CuteDSL W4A4 / PER-TOKEN / W4A16 vs TRTLLM NVFP4 / PER-TOKEN / BF16 (EP=1, TP=8)
=====================================================================================================================================================================================================================================
Model: hidden=2048, intermediate=640, experts=512, top_k=22
EP Config: 512 local experts (simulating 1-way parallelism)
TP Config: intermediate size 640 (simulating 8-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Routing: shared precomputed sigmoid(logits), bias selects only, top-22 normalized then scaled by 5.0; routing excluded from every backend's timing.
Activation: ReLU2 (non-gated squared ReLU).
Scope: routed latent experts only; latent projections, RMSNorm, shared experts, router GEMM and communication excluded.
Timed initial activation quantization for FP4-activation backends: included; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4 / PER-TOKEN / BF16 finalize: native (unaffected by --no-fused-finalize).
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   | CuteDSL PER-TOKEN |  CuteDSL W4A16  |  TRTLLM NVFP4   | TRTLLM PER-TOKEN |   TRTLLM BF16   |                    Speedup vs TRTLLM NVFP4                    |      Winner       | Active  |      Stats
       |      ms  TFLOPS |        ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |       ms  TFLOPS |      ms  TFLOPS | CuteDSL W4A4 CuteDSL W4A16 CuteDSL PER-TOKEN TRTLLM PER-TOKEN |                   | experts | min/max/median
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.023     4.9 |     0.028     4.1 |   0.026     4.5 |   0.020     5.8 |    0.025     4.6 |             N/A |        0.85x         0.77x             0.71x            0.80x |   TRTLLM NVFP4    |      22 |   0/  1/   0.00
     2 |   0.029     8.1 |     0.034     6.8 |   0.033     6.9 |   0.028     8.2 |    0.032     7.2 |             N/A |        0.98x         0.84x             0.82x            0.88x |   TRTLLM NVFP4    |      44 |   0/  1/   0.00
     4 |   0.040    11.5 |     0.045    10.3 |   0.046     9.9 |   0.039    11.7 |    0.045    10.3 |             N/A |        0.98x         0.85x             0.88x            0.88x |   TRTLLM NVFP4    |      85 |   0/  2/   0.00
     8 |   0.059    15.5 |     0.064    14.5 |   0.066    14.1 |   0.059    15.6 |    0.064    14.3 |             N/A |        0.99x         0.90x             0.93x            0.92x |   TRTLLM NVFP4    |     156 |   0/  3/   0.00
    16 |   0.083    22.2 |     0.089    20.8 |   0.092    20.0 |   0.083    22.2 |    0.089    20.7 |             N/A |        1.00x         0.90x             0.94x            0.93x |   CuteDSL W4A4    |     259 |   0/  4/   1.00
    32 |   0.117    31.5 |     0.124    29.8 |   0.125    29.5 |   0.118    31.2 |    0.128    28.9 |             N/A |        1.01x         0.95x             0.96x            0.93x |   CuteDSL W4A4    |     385 |   0/  7/   1.00
    64 |   0.138    53.5 |     0.147    50.2 |   0.148    49.7 |   0.139    53.1 |    0.150    49.2 |             N/A |        1.01x         0.94x             0.95x            0.93x |   CuteDSL W4A4    |     482 |   0/ 11/   3.00
   128 |   0.146   101.1 |     0.153    96.2 |   0.154    95.8 |   0.148    99.9 |    0.162    91.0 |             N/A |        1.01x         0.96x             0.96x            0.91x |   CuteDSL W4A4    |     510 |   0/ 14/   5.00
   256 |   0.150   197.4 |     0.163   181.3 |   0.163   181.2 |   0.161   183.6 |    0.180   164.1 |             N/A |        1.08x         0.99x             0.99x            0.89x |   CuteDSL W4A4    |     512 |   1/ 26/  11.00
   512 |   0.155   381.9 |     0.180   327.4 |   0.177   334.1 |   0.169   350.5 |    0.195   302.3 |             N/A |        1.09x         0.95x             0.93x            0.86x |   CuteDSL W4A4    |     512 |   7/ 41/  21.00
  4096 |   0.379  1247.5 |     0.555   851.1 |   0.541   873.9 |   0.364  1297.6 |    0.517   914.6 |             N/A |        0.96x         0.67x             0.66x            0.70x |   TRTLLM NVFP4    |     512 |  95/275/ 175.00
  8192 |   0.668  1413.5 |     0.981   963.7 |   0.935  1010.1 |   0.601  1572.9 |    0.908  1040.9 |             N/A |        0.90x         0.64x             0.61x            0.66x |   TRTLLM NVFP4    |     512 | 188/656/ 350.00
 16384 |   1.184  1596.8 |     1.803  1048.0 |   1.913   988.1 |   1.067  1771.7 |    1.665  1135.0 |             N/A |        0.90x         0.56x             0.59x            0.64x |   TRTLLM NVFP4    |     512 | 381/1131/ 695.50
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

**N3U TP8 · MXFP**

```text

================================================================================================================================================
Nemotron-3-Ultra MoE Benchmark: CuteDSL MXFP4x8 / MXFP8 vs TRTLLM MXFP4x8 / MXFP8 / BF16 (EP=1, TP=8)
================================================================================================================================================
Model: hidden=2048, intermediate=640, experts=512, top_k=22
EP Config: 512 local experts (simulating 1-way parallelism)
TP Config: intermediate size 640 (simulating 8-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Routing: shared precomputed sigmoid(logits), bias selects only, top-22 normalized then scaled by 5.0; routing excluded from every backend's timing.
Activation: ReLU2 (non-gated squared ReLU).
Scope: routed latent experts only; latent projections, RMSNorm, shared experts, router GEMM and communication excluded.
MXFP8 activations: native UE8M0 scale per 32 elements along K.
Timed initial activation quantization: excluded; weight preparation and tuning excluded. TRTLLM BF16 consumes BF16 directly.
CuteDSL finalize: deterministic two-stage
TRTLLM MXFP4x8 / MXFP8 / BF16 finalize: native (unaffected by --no-fused-finalize).
------------------------------------------------------------------------------------------------------------------------------------------------
Tokens | CuteDSL MXFP4x8 |  CuteDSL MXFP8  | TRTLLM MXFP4x8  |  TRTLLM MXFP8   |   TRTLLM BF16   | Speedup vs TRTLLM | Active  |      Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |  MXFP4x8    MXFP8 | experts | min/max/median
------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.023     4.9 |   0.027     4.3 |   0.019     6.2 |   0.023     4.9 |             N/A |    0.80x    0.88x |      22 |   0/  1/   0.00
     2 |   0.029     8.1 |   0.035     6.7 |   0.026     8.9 |   0.035     6.6 |             N/A |    0.91x    1.01x |      44 |   0/  1/   0.00
     4 |   0.040    11.5 |   0.053     8.7 |   0.038    12.2 |   0.056     8.2 |             N/A |    0.95x    1.06x |      85 |   0/  2/   0.00
     8 |   0.060    15.4 |   0.085    10.8 |   0.057    16.1 |   0.087    10.6 |             N/A |    0.95x    1.02x |     156 |   0/  3/   0.00
    16 |   0.086    21.3 |   0.125    14.8 |   0.081    22.8 |   0.128    14.4 |             N/A |    0.94x    1.02x |     259 |   0/  4/   1.00
    32 |   0.125    29.5 |   0.181    20.4 |   0.116    31.8 |   0.180    20.5 |             N/A |    0.93x    1.00x |     385 |   0/  7/   1.00
    64 |   0.132    56.0 |   0.218    33.9 |   0.137    53.9 |   0.218    33.9 |             N/A |    1.04x    1.00x |     482 |   0/ 11/   3.00
   128 |   0.137   107.6 |   0.228    64.7 |   0.143   103.4 |   0.231    63.8 |             N/A |    1.04x    1.02x |     510 |   0/ 14/   5.00
   256 |   0.144   204.7 |   0.241   122.4 |   0.155   190.8 |   0.246   120.2 |             N/A |    1.07x    1.02x |     512 |   1/ 26/  11.00
   512 |   0.149   395.5 |   0.243   243.0 |   0.164   359.2 |   0.254   232.7 |             N/A |    1.10x    1.04x |     512 |   7/ 41/  21.00
  4096 |   0.382  1236.1 |   0.428  1103.5 |   0.420  1124.8 |   0.432  1093.9 |             N/A |    1.10x    1.01x |     512 |  95/275/ 175.00
  8192 |   0.690  1369.0 |   0.747  1265.2 |   0.682  1385.9 |   0.739  1278.6 |             N/A |    0.99x    0.99x |     512 | 188/656/ 350.00
 16384 |   1.180  1601.8 |   1.272  1485.7 |   1.281  1475.0 |   1.336  1414.5 |             N/A |    1.09x    1.05x |     512 | 381/1131/ 695.50
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```
