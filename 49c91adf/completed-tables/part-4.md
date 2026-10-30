<!-- moe-gather-pipeline-completed-tables-49c91adf-part-4 -->
### Benchmark table output — K3 TP8 / N3U TP8 (4/4)

Printed by the unchanged benchmark table functions from saved records: 104 newly measured and 364 reused CuTe DSL final-pass records source-equivalent to `49c91adf`, plus the original TRTLLM final-pass records. TRTLLM is reused, not rerun; these are separate-run comparisons. Original records retain their measured base `82254e20`, `02de7785`, or `bf072d26` plus frozen patch identifiers. The heatmaps use two-pass aggregates. Missing or unsupported records remain N/A. [Original measurement logs](https://github.com/zianglih/flashinfer/raw/refs/heads/codex/moe-gather-pipeline-assets/49c91adf/moe-gather-pipeline-results.tar.xz).

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
     1 |   0.025     5.3 |     0.027     4.8 |   0.027     4.9 |   0.021     6.3 |              N/A |             N/A |        0.84x         0.78x             0.76x              N/A |   TRTLLM NVFP4    |      16 |   0/  1/   0.00
     2 |   0.032     8.2 |     0.037     7.1 |   0.038     6.9 |   0.030     8.9 |              N/A |             N/A |        0.92x         0.78x             0.80x              N/A |   TRTLLM NVFP4    |      32 |   0/  1/   0.00
     4 |   0.043    12.2 |     0.047    11.2 |   0.049    10.9 |   0.043    12.2 |              N/A |             N/A |        1.01x         0.90x             0.92x              N/A |   CuteDSL W4A4    |      63 |   0/  2/   0.00
     8 |   0.077    13.7 |     0.082    13.0 |   0.086    12.3 |   0.077    13.7 |              N/A |             N/A |        1.00x         0.90x             0.95x              N/A |   TRTLLM NVFP4    |     124 |   0/  2/   0.00
    16 |   0.113    18.8 |     0.120    17.7 |   0.124    17.0 |   0.115    18.4 |              N/A |             N/A |        1.02x         0.93x             0.96x              N/A |   CuteDSL W4A4    |     222 |   0/  3/   0.00
    32 |   0.168    25.2 |     0.176    24.0 |   0.182    23.2 |   0.173    24.4 |              N/A |             N/A |        1.03x         0.95x             0.98x              N/A |   CuteDSL W4A4    |     392 |   0/  4/   0.00
    64 |   0.239    35.4 |     0.248    34.1 |   0.264    32.0 |   0.246    34.4 |              N/A |             N/A |        1.03x         0.93x             0.99x              N/A |   CuteDSL W4A4    |     593 |   0/  5/   1.00
   128 |   0.308    54.9 |     0.316    53.6 |   0.335    50.5 |   0.317    53.3 |              N/A |             N/A |        1.03x         0.95x             1.01x              N/A |   CuteDSL W4A4    |     787 |   0/ 10/   2.00
   256 |   0.342    99.0 |     0.354    95.6 |   0.372    90.9 |   0.355    95.4 |              N/A |             N/A |        1.04x         0.95x             1.00x              N/A |   CuteDSL W4A4    |     883 |   0/ 15/   4.00
   512 |   0.358   188.9 |     0.375   180.4 |   0.395   171.4 |   0.371   182.3 |              N/A |             N/A |        1.04x         0.94x             0.99x              N/A |   CuteDSL W4A4    |     895 |   0/ 22/   9.00
  4096 |   0.556   973.3 |     0.665   814.4 |   0.686   788.8 |   0.546   991.9 |              N/A |             N/A |        0.98x         0.80x             0.82x              N/A |   TRTLLM NVFP4    |     896 |  21/175/  72.00
  8192 |   0.794  1363.2 |     1.054  1027.0 |   1.265   855.8 |   0.949  1140.2 |              N/A |             N/A |        1.20x         0.75x             0.90x              N/A |   CuteDSL W4A4    |     896 |  55/312/ 143.00
 16384 |   1.420  1524.4 |     1.955  1107.0 |   2.353   920.0 |   1.666  1299.2 |              N/A |             N/A |        1.17x         0.71x             0.85x              N/A |   CuteDSL W4A4    |     896 | 119/728/ 290.50
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
     1 |   0.024     5.5 |             N/A |   0.020     6.5 |             N/A |             N/A |    0.85x      N/A |      16 |   0/  1/   0.00
     2 |   0.030     8.7 |             N/A |   0.030     8.8 |             N/A |             N/A |    0.98x      N/A |      32 |   0/  1/   0.00
     4 |   0.043    12.3 |             N/A |   0.044    12.0 |             N/A |             N/A |    1.02x      N/A |      63 |   0/  2/   0.00
     8 |   0.078    13.5 |             N/A |   0.076    14.0 |             N/A |             N/A |    0.96x      N/A |     124 |   0/  2/   0.00
    16 |   0.121    17.4 |             N/A |   0.113    18.7 |             N/A |             N/A |    0.93x      N/A |     222 |   0/  3/   0.00
    32 |   0.162    26.0 |             N/A |   0.168    25.1 |             N/A |             N/A |    1.04x      N/A |     392 |   0/  4/   0.00
    64 |   0.228    37.1 |             N/A |   0.241    35.1 |             N/A |             N/A |    1.06x      N/A |     593 |   0/  5/   1.00
   128 |   0.291    58.0 |             N/A |   0.308    54.9 |             N/A |             N/A |    1.06x      N/A |     787 |   0/ 10/   2.00
   256 |   0.328   103.1 |             N/A |   0.346    97.7 |             N/A |             N/A |    1.06x      N/A |     883 |   0/ 15/   4.00
   512 |   0.351   192.8 |             N/A |   0.369   183.5 |             N/A |             N/A |    1.05x      N/A |     895 |   0/ 22/   9.00
  4096 |   0.546   991.2 |             N/A |   0.572   946.7 |             N/A |             N/A |    1.05x      N/A |     896 |  21/175/  72.00
  8192 |   0.893  1212.4 |             N/A |   0.952  1136.7 |             N/A |             N/A |    1.07x      N/A |     896 |  55/312/ 143.00
 16384 |   1.674  1293.4 |             N/A |   1.665  1300.0 |             N/A |             N/A |    0.99x      N/A |     896 | 119/728/ 290.50
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
     1 |   0.024     4.9 |     0.028     4.1 |   0.026     4.5 |   0.020     5.8 |    0.025     4.6 |             N/A |        0.84x         0.77x             0.70x            0.80x |   TRTLLM NVFP4    |      22 |   0/  1/   0.00
     2 |   0.029     8.1 |     0.034     6.7 |   0.033     7.0 |   0.028     8.2 |    0.032     7.2 |             N/A |        0.98x         0.85x             0.82x            0.88x |   TRTLLM NVFP4    |      44 |   0/  1/   0.00
     4 |   0.040    11.5 |     0.045    10.3 |   0.045    10.2 |   0.039    11.7 |    0.045    10.3 |             N/A |        0.98x         0.87x             0.88x            0.88x |   TRTLLM NVFP4    |      85 |   0/  2/   0.00
     8 |   0.059    15.7 |     0.064    14.5 |   0.063    14.7 |   0.059    15.6 |    0.064    14.3 |             N/A |        1.00x         0.94x             0.93x            0.92x |   CuteDSL W4A4    |     156 |   0/  3/   0.00
    16 |   0.082    22.4 |     0.089    20.8 |   0.091    20.3 |   0.083    22.2 |    0.089    20.7 |             N/A |        1.01x         0.91x             0.94x            0.93x |   CuteDSL W4A4    |     259 |   0/  4/   1.00
    32 |   0.115    32.0 |     0.124    29.9 |   0.123    30.1 |   0.118    31.2 |    0.128    28.9 |             N/A |        1.03x         0.97x             0.96x            0.93x |   CuteDSL W4A4    |     385 |   0/  7/   1.00
    64 |   0.137    53.9 |     0.147    50.3 |   0.146    50.5 |   0.139    53.1 |    0.150    49.2 |             N/A |        1.01x         0.95x             0.95x            0.93x |   CuteDSL W4A4    |     482 |   0/ 11/   3.00
   128 |   0.144   102.6 |     0.153    96.4 |   0.152    97.4 |   0.148    99.9 |    0.162    91.0 |             N/A |        1.03x         0.97x             0.96x            0.91x |   CuteDSL W4A4    |     510 |   0/ 14/   5.00
   256 |   0.149   197.6 |     0.163   181.1 |   0.159   185.8 |   0.161   183.6 |    0.180   164.1 |             N/A |        1.08x         1.01x             0.99x            0.89x |   CuteDSL W4A4    |     512 |   1/ 26/  11.00
   512 |   0.154   383.2 |     0.180   327.8 |   0.173   342.2 |   0.169   350.5 |    0.195   302.3 |             N/A |        1.09x         0.98x             0.94x            0.86x |   CuteDSL W4A4    |     512 |   7/ 41/  21.00
  4096 |   0.367  1286.4 |     0.554   852.9 |   0.545   866.9 |   0.364  1297.6 |    0.517   914.6 |             N/A |        0.99x         0.67x             0.66x            0.70x |   TRTLLM NVFP4    |     512 |  95/275/ 175.00
  8192 |   0.653  1446.4 |     0.980   964.2 |   0.957   987.5 |   0.601  1572.9 |    0.908  1040.9 |             N/A |        0.92x         0.63x             0.61x            0.66x |   TRTLLM NVFP4    |     512 | 188/656/ 350.00
 16384 |   1.132  1669.2 |     1.801  1049.0 |   1.965   961.6 |   1.067  1771.7 |    1.665  1135.0 |             N/A |        0.94x         0.54x             0.59x            0.64x |   TRTLLM NVFP4    |     512 | 381/1131/ 695.50
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
     1 |   0.024     4.9 |   0.027     4.3 |   0.019     6.2 |   0.023     4.9 |             N/A |    0.78x    0.88x |      22 |   0/  1/   0.00
     2 |   0.029     8.1 |   0.035     6.6 |   0.026     8.9 |   0.035     6.6 |             N/A |    0.90x    1.00x |      44 |   0/  1/   0.00
     4 |   0.040    11.5 |   0.053     8.7 |   0.038    12.2 |   0.056     8.2 |             N/A |    0.95x    1.06x |      85 |   0/  2/   0.00
     8 |   0.060    15.4 |   0.086    10.8 |   0.057    16.1 |   0.087    10.6 |             N/A |    0.95x    1.01x |     156 |   0/  3/   0.00
    16 |   0.087    21.2 |   0.125    14.8 |   0.081    22.8 |   0.128    14.4 |             N/A |    0.93x    1.02x |     259 |   0/  4/   1.00
    32 |   0.125    29.4 |   0.181    20.4 |   0.116    31.8 |   0.180    20.5 |             N/A |    0.92x    1.00x |     385 |   0/  7/   1.00
    64 |   0.132    56.0 |   0.218    33.8 |   0.137    53.9 |   0.218    33.9 |             N/A |    1.04x    1.00x |     482 |   0/ 11/   3.00
   128 |   0.138   107.0 |   0.228    64.6 |   0.143   103.4 |   0.231    63.8 |             N/A |    1.04x    1.01x |     510 |   0/ 14/   5.00
   256 |   0.144   204.9 |   0.240   122.8 |   0.155   190.8 |   0.246   120.2 |             N/A |    1.07x    1.02x |     512 |   1/ 26/  11.00
   512 |   0.150   394.6 |   0.244   242.3 |   0.164   359.2 |   0.254   232.7 |             N/A |    1.10x    1.04x |     512 |   7/ 41/  21.00
  4096 |   0.372  1270.6 |   0.423  1117.1 |   0.420  1124.8 |   0.432  1093.9 |             N/A |    1.13x    1.02x |     512 |  95/275/ 175.00
  8192 |   0.702  1345.5 |   0.733  1288.6 |   0.682  1385.9 |   0.739  1278.6 |             N/A |    0.97x    1.01x |     512 | 188/656/ 350.00
 16384 |   1.233  1533.2 |   1.237  1527.4 |   1.281  1475.0 |   1.336  1414.5 |             N/A |    1.04x    1.08x |     512 | 381/1131/ 695.50
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

