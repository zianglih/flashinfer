<!-- moe-gather-pipeline-completed-tables-02de7785-part-3 -->
### Benchmark table output — V3 TP8 / V41F TP4 (3/4)

Printed by the unchanged benchmark table functions from saved records: fresh CuTe DSL final-pass results source-equivalent to `02de7785` plus the original TRTLLM final-pass results. TRTLLM is reused, not rerun; these are separate-run comparisons. The original measurement records retain their actual base `82254e20` plus frozen patch identifiers. The heatmaps use two-pass aggregates. Missing or unsupported records remain N/A. [Original fresh-run logs](https://github.com/zianglih/flashinfer/raw/refs/heads/codex/moe-gather-pipeline-assets/02de7785/moe-gather-pipeline-results.tar.gz).

**V3 TP8 · NVFP4**

```text

=====================================================================================================================================================================================================================================
DeepSeek-V3 MoE Benchmark: CuteDSL W4A4 / PER-TOKEN / W4A16 vs TRTLLM NVFP4 / PER-TOKEN / BF16 (EP=1, TP=8)
=====================================================================================================================================================================================================================================
Model: hidden=7168, intermediate=256, experts=256, top_k=8
EP Config: 256 local experts (simulating 1-way parallelism)
TP Config: intermediate size 256 (simulating 8-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Timed initial activation quantization for FP4-activation backends: included; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4 / PER-TOKEN / BF16 finalize: native (unaffected by --no-fused-finalize).
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   | CuteDSL PER-TOKEN |  CuteDSL W4A16  |  TRTLLM NVFP4   | TRTLLM PER-TOKEN |   TRTLLM BF16   |                    Speedup vs TRTLLM NVFP4                    |      Winner       | Active  |      Stats     
       |      ms  TFLOPS |        ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |       ms  TFLOPS |      ms  TFLOPS | CuteDSL W4A4 CuteDSL W4A16 CuteDSL PER-TOKEN TRTLLM PER-TOKEN |                   | experts | min/max/median 
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.024     3.7 |     0.028     3.1 |   0.028     3.1 |   0.023     3.9 |    0.027     3.3 |             N/A |        0.95x         0.80x             0.81x            0.84x |   TRTLLM NVFP4    |       8 |   0/  1/   0.00
     2 |   0.028     6.2 |     0.032     5.5 |   0.032     5.6 |   0.027     6.5 |    0.031     5.7 |             N/A |        0.96x         0.86x             0.85x            0.87x |   TRTLLM NVFP4    |      16 |   0/  1/   0.00
     4 |   0.035    10.0 |     0.041     8.6 |   0.037     9.5 |   0.037     9.6 |    0.043     8.2 |             N/A |        1.04x         0.98x             0.90x            0.86x |   CuteDSL W4A4    |      31 |   0/  2/   0.00
     8 |   0.050    14.1 |     0.056    12.5 |   0.056    12.5 |   0.053    13.3 |    0.062    11.4 |             N/A |        1.06x         0.94x             0.94x            0.86x |   CuteDSL W4A4    |      58 |   0/  3/   0.00
    16 |   0.073    19.4 |     0.081    17.4 |   0.079    17.9 |   0.078    18.1 |    0.092    15.3 |             N/A |        1.07x         0.99x             0.97x            0.85x |   CuteDSL W4A4    |     103 |   0/  4/   0.00
    32 |   0.105    26.8 |     0.117    24.1 |   0.115    24.6 |   0.114    24.6 |    0.131    21.5 |             N/A |        1.09x         1.00x             0.98x            0.87x |   CuteDSL W4A4    |     165 |   0/  5/   1.00
    64 |   0.137    41.1 |     0.149    37.8 |   0.151    37.4 |   0.151    37.3 |    0.171    33.0 |             N/A |        1.10x         1.00x             1.01x            0.89x |   CuteDSL W4A4    |     226 |   0/  6/   2.00
   128 |   0.145    77.6 |     0.163    69.2 |   0.158    71.2 |   0.163    69.4 |    0.190    59.2 |             N/A |        1.12x         1.03x             1.00x            0.85x |   CuteDSL W4A4    |     248 |   0/ 10/   4.00
   256 |   0.156   144.9 |     0.171   132.2 |   0.167   134.9 |   0.174   129.4 |    0.214   105.4 |             N/A |        1.12x         1.04x             1.02x            0.81x |   CuteDSL W4A4    |     256 |   1/ 17/   8.00
   512 |   0.183   245.9 |     0.205   220.1 |   0.182   247.8 |   0.183   245.8 |    0.223   201.8 |             N/A |        1.00x         1.01x             0.90x            0.82x |   CuteDSL W4A16   |     256 |   4/ 30/  16.00
  4096 |   0.387   932.8 |     0.469   769.9 |   0.480   751.9 |   0.365   988.2 |    0.474   760.6 |             N/A |        0.94x         0.76x             0.78x            0.77x |   TRTLLM NVFP4    |     256 |  66/198/ 128.00
  8192 |   0.618  1166.8 |     0.783   921.5 |   0.887   813.8 |   0.595  1211.9 |    0.778   926.9 |             N/A |        0.96x         0.67x             0.76x            0.76x |   TRTLLM NVFP4    |     256 | 138/385/ 252.00
 16384 |   1.095  1317.6 |     1.396  1034.0 |   1.719   839.7 |   1.078  1338.5 |    1.431  1008.3 |             N/A |        0.98x         0.63x             0.77x            0.75x |   TRTLLM NVFP4    |     256 | 250/978/ 505.50
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

**V3 TP8 · MXFP**

```text

================================================================================================================================================
DeepSeek-V3 MoE Benchmark: CuteDSL MXFP4x8 / MXFP8 vs TRTLLM MXFP4x8 / MXFP8 / BF16 (EP=1, TP=8)
================================================================================================================================================
Model: hidden=7168, intermediate=256, experts=256, top_k=8
EP Config: 256 local experts (simulating 1-way parallelism)
TP Config: intermediate size 256 (simulating 8-way parallelism)
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
     1 |   0.024     3.6 |   0.027     3.3 |   0.021     4.2 |   0.025     3.5 |             N/A |    0.86x    0.94x |       8 |   0/  1/   0.00
     2 |   0.028     6.3 |   0.032     5.5 |   0.026     6.8 |   0.034     5.2 |             N/A |    0.93x    1.06x |      16 |   0/  1/   0.00
     4 |   0.036     9.7 |   0.045     7.8 |   0.036     9.8 |   0.049     7.2 |             N/A |    0.99x    1.09x |      31 |   0/  2/   0.00
     8 |   0.051    13.9 |   0.071     9.9 |   0.055    12.8 |   0.078     9.1 |             N/A |    1.08x    1.09x |      58 |   0/  3/   0.00
    16 |   0.070    20.1 |   0.110    12.8 |   0.080    17.7 |   0.116    12.2 |             N/A |    1.14x    1.05x |     103 |   0/  4/   0.00
    32 |   0.103    27.4 |   0.167    16.9 |   0.115    24.5 |   0.168    16.8 |             N/A |    1.12x    1.00x |     165 |   0/  5/   1.00
    64 |   0.135    41.7 |   0.222    25.4 |   0.150    37.6 |   0.223    25.3 |             N/A |    1.11x    1.01x |     226 |   0/  6/   2.00
   128 |   0.144    78.4 |   0.238    47.4 |   0.161    70.2 |   0.243    46.4 |             N/A |    1.12x    1.02x |     248 |   0/ 10/   4.00
   256 |   0.154   146.6 |   0.251    90.0 |   0.171   131.9 |   0.255    88.5 |             N/A |    1.11x    1.02x |     256 |   1/ 17/   8.00
   512 |   0.184   245.3 |   0.265   170.1 |   0.192   235.4 |   0.270   167.0 |             N/A |    1.04x    1.02x |     256 |   4/ 30/  16.00
  4096 |   0.385   937.3 |   0.456   792.0 |   0.395   912.3 |   0.457   790.0 |             N/A |    1.03x    1.00x |     256 |  66/198/ 128.00
  8192 |   0.686  1052.4 |   0.736   980.7 |   0.642  1123.9 |   0.693  1040.8 |             N/A |    0.94x    0.94x |     256 | 138/385/ 252.00
 16384 |   1.248  1156.3 |   1.343  1074.2 |   1.179  1223.8 |   1.260  1145.0 |             N/A |    0.94x    0.94x |     256 | 250/978/ 505.50
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

**V41F TP4 · NVFP4**

```text

=====================================================================================================================================================================================================================================
DeepSeek-V4.1-Flash MoE Benchmark: CuteDSL W4A4 / PER-TOKEN / W4A16 vs TRTLLM NVFP4 / PER-TOKEN / BF16 (EP=1, TP=4)
=====================================================================================================================================================================================================================================
Model: hidden=5120, intermediate=576, experts=384, top_k=6
EP Config: 384 local experts (simulating 1-way parallelism)
TP Config: intermediate size 576 (simulating 4-way parallelism)
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
     1 |   0.021     5.0 |     0.024     4.5 |   0.024     4.5 |   0.020     5.4 |    0.024     4.3 |             N/A |        0.92x         0.83x             0.83x            0.80x |   TRTLLM NVFP4    |       6 |   0/  1/   0.00
     2 |   0.026     8.3 |     0.029     7.3 |   0.029     7.4 |   0.026     8.2 |    0.030     7.1 |             N/A |        1.02x         0.90x             0.89x            0.86x |   CuteDSL W4A4    |      12 |   0/  1/   0.00
     4 |   0.034    12.4 |     0.040    10.5 |   0.041    10.4 |   0.038    11.1 |    0.044     9.8 |             N/A |        1.11x         0.93x             0.95x            0.88x |   CuteDSL W4A4    |      24 |   0/  1/   0.00
     8 |   0.053    16.1 |     0.057    14.8 |   0.063    13.4 |   0.058    14.6 |    0.064    13.3 |             N/A |        1.11x         0.92x             1.02x            0.92x |   CuteDSL W4A4    |      47 |   0/  2/   0.00
    16 |   0.088    19.4 |     0.094    18.1 |   0.100    17.0 |   0.093    18.3 |    0.100    17.1 |             N/A |        1.06x         0.93x             0.99x            0.93x |   CuteDSL W4A4    |      89 |   0/  2/   0.00
    32 |   0.139    24.4 |     0.145    23.4 |   0.154    22.1 |   0.142    23.8 |    0.150    22.6 |             N/A |        1.03x         0.93x             0.98x            0.95x |   CuteDSL W4A4    |     151 |   0/  4/   0.00
    64 |   0.207    32.9 |     0.210    32.3 |   0.229    29.7 |   0.214    31.7 |    0.225    30.2 |             N/A |        1.04x         0.94x             1.02x            0.95x |   CuteDSL W4A4    |     239 |   0/  5/   1.00
   128 |   0.274    49.6 |     0.277    49.0 |   0.304    44.7 |   0.278    49.0 |    0.288    47.2 |             N/A |        1.01x         0.91x             1.00x            0.96x |   CuteDSL W4A4    |     330 |   0/  7/   2.00
   256 |   0.314    86.5 |     0.319    85.3 |   0.346    78.5 |   0.316    85.9 |    0.332    81.9 |             N/A |        1.01x         0.91x             0.99x            0.95x |   CuteDSL W4A4    |     380 |   0/ 11/   4.00
   512 |   0.322   168.7 |     0.331   164.4 |   0.354   153.5 |   0.325   167.3 |    0.345   157.6 |             N/A |        1.01x         0.92x             0.98x            0.94x |   CuteDSL W4A4    |     384 |   1/ 17/   8.00
  4096 |   0.421  1032.4 |     0.536   811.5 |   0.572   760.3 |   0.432  1006.9 |    0.512   849.4 |             N/A |        1.03x         0.76x             0.81x            0.84x |   CuteDSL W4A4    |     384 |  38/ 89/  63.00
  8192 |   0.599  1453.1 |     0.770  1129.9 |   1.004   866.1 |   0.606  1435.8 |    0.734  1184.9 |             N/A |        1.01x         0.60x             0.79x            0.83x |   CuteDSL W4A4    |     384 |  86/167/ 128.00
 16384 |   1.041  1670.6 |     1.282  1357.3 |   1.895   918.1 |   1.028  1691.6 |    1.253  1388.4 |             N/A |        0.99x         0.54x             0.80x            0.82x |   TRTLLM NVFP4    |     384 | 196/341/ 254.00
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

**V41F TP4 · MXFP**

Not run: no supported baseline comparison.

