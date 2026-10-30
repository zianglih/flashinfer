<!-- moe-gather-pipeline-completed-tables-c1ac8ce7-part-1 -->
### Benchmark table output — V3 EP8 / V41F EP4 (1/4)

Printed by the unchanged benchmark table functions from saved records: 39 newly measured W4A16 and 429 reused CuTe DSL final-pass records source-equivalent to `c1ac8ce7`, plus the original TRTLLM final-pass records. TRTLLM is reused, not rerun; these are separate-run comparisons. Original records retain their measured base `82254e20`, `02de7785`, `bf072d26`, `49c91adf`, or `2b8eb9d8` plus frozen patch identifiers. The 39 new records use the recovery-node native-library cohort; the separate ACCA diagnostic does not replace them. The heatmaps use two-pass aggregates. Missing or unsupported records remain N/A. [Original measurement logs](https://github.com/zianglih/flashinfer/raw/refs/heads/codex/moe-gather-pipeline-assets/c1ac8ce7/moe-gather-pipeline-results.tar.xz).

BF16 reuses the original `f7182d5c` measurements: the logs report CUPTI and CUDA Graphs, but these older records predate the per-record strict timing guards.

**V3 EP8 · NVFP4**

```text

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
     1 |   0.026     3.4 |     0.029     3.0 |   0.030     2.9 |   0.029     3.1 |    0.031     2.9 |   0.048     1.8 |        1.13x         0.95x             0.98x            0.94x |   CuteDSL W4A4    |       2 |   0/  1/   0.00
     2 |   0.034     5.2 |     0.038     4.7 |   0.035     5.0 |   0.039     4.5 |    0.042     4.2 |   0.076     2.3 |        1.14x         1.09x             1.03x            0.92x |   CuteDSL W4A4    |       4 |   0/  1/   0.00
     4 |   0.045     7.9 |     0.049     7.3 |   0.050     7.0 |   0.049     7.2 |    0.062     5.7 |   0.121     2.9 |        1.08x         0.97x             1.00x            0.78x |   CuteDSL W4A4    |       7 |   0/  1/   0.00
     8 |   0.058    12.1 |     0.062    11.3 |   0.069    10.2 |   0.064    11.0 |    0.070    10.1 |   0.155     4.5 |        1.09x         0.93x             1.03x            0.91x |   CuteDSL W4A4    |      10 |   0/  2/   0.00
    16 |   0.068    20.7 |     0.073    19.2 |   0.073    19.2 |   0.074    19.0 |    0.082    17.3 |   0.188     7.5 |        1.09x         1.01x             1.01x            0.91x |   CuteDSL W4A4    |      13 |   0/  2/   0.00
    32 |   0.100    28.2 |     0.106    26.5 |   0.107    26.4 |   0.105    27.0 |    0.112    25.1 |   0.286     9.9 |        1.05x         0.98x             0.98x            0.93x |   CuteDSL W4A4    |      21 |   0/  3/   1.00
    64 |   0.130    43.3 |     0.135    41.6 |   0.140    40.2 |   0.141    40.0 |    0.147    38.4 |   0.387    14.6 |        1.08x         1.01x             1.04x            0.96x |   CuteDSL W4A4    |      29 |   0/  5/   2.00
   128 |   0.134    84.0 |     0.140    80.7 |   0.143    78.6 |   0.142    79.5 |    0.150    75.2 |   0.399    28.3 |        1.06x         0.99x             1.02x            0.95x |   CuteDSL W4A4    |      30 |   0/  8/   3.00
   256 |   0.144   156.7 |     0.152   148.5 |   0.151   149.7 |   0.154   146.6 |    0.163   138.7 |   0.428    52.7 |        1.07x         1.02x             1.01x            0.95x |   CuteDSL W4A4    |      32 |   1/ 11/   7.00
   512 |   0.148   303.8 |     0.157   288.0 |   0.155   290.3 |   0.159   282.9 |    0.171   264.5 |   0.435   103.6 |        1.07x         1.03x             1.02x            0.93x |   CuteDSL W4A4    |      32 |   7/ 23/  14.00
  4096 |   0.197  1827.4 |     0.243  1487.6 |   0.287  1255.4 |   0.225  1606.8 |    0.269  1339.4 |   0.515   700.1 |        1.14x         0.78x             0.93x            0.83x |   CuteDSL W4A4    |      32 |  81/147/ 117.00
  8192 |   0.301  2398.5 |     0.362  1993.6 |   0.597  1208.9 |   0.362  1992.1 |    0.425  1698.9 |   0.803   898.6 |        1.20x         0.61x             1.00x            0.85x |   CuteDSL W4A4    |      32 | 174/347/ 251.50
 16384 |   0.519  2778.4 |     0.625  2310.2 |   1.077  1339.6 |   0.637  2264.9 |    0.762  1893.2 |   1.495   965.2 |        1.23x         0.59x             1.02x            0.84x |   CuteDSL W4A4    |      32 | 388/733/ 496.50
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

**V3 EP8 · MXFP**

```text

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
     1 |   0.026     3.4 |   0.030     2.9 |   0.028     3.1 |   0.038     2.3 |   0.049     1.8 |    1.09x    1.25x |       2 |   0/  1/   0.00
     2 |   0.032     5.5 |   0.043     4.1 |   0.038     4.6 |   0.051     3.4 |   0.077     2.3 |    1.19x    1.18x |       4 |   0/  1/   0.00
     4 |   0.045     7.9 |   0.070     5.0 |   0.058     6.1 |   0.075     4.7 |   0.120     2.9 |    1.29x    1.07x |       7 |   0/  1/   0.00
     8 |   0.056    12.5 |   0.089     7.9 |   0.063    11.1 |   0.099     7.1 |   0.154     4.6 |    1.12x    1.11x |      10 |   0/  2/   0.00
    16 |   0.066    21.4 |   0.108    13.1 |   0.076    18.7 |   0.116    12.1 |   0.188     7.5 |    1.15x    1.08x |      13 |   0/  2/   0.00
    32 |   0.097    29.0 |   0.163    17.2 |   0.105    27.0 |   0.167    16.9 |   0.285     9.9 |    1.08x    1.02x |      21 |   0/  3/   1.00
    64 |   0.128    44.0 |   0.219    25.7 |   0.138    40.9 |   0.225    25.1 |   0.386    14.6 |    1.08x    1.03x |      29 |   0/  5/   2.00
   128 |   0.131    85.9 |   0.225    50.0 |   0.140    80.5 |   0.233    48.5 |   0.400    28.2 |    1.07x    1.03x |      30 |   0/  8/   3.00
   256 |   0.141   160.4 |   0.243    92.7 |   0.147   153.0 |   0.246    91.5 |   0.427    52.8 |    1.05x    1.01x |      32 |   1/ 11/   7.00
   512 |   0.144   312.3 |   0.246   183.1 |   0.157   286.8 |   0.253   178.1 |   0.435   103.7 |    1.09x    1.03x |      32 |   7/ 23/  14.00
  4096 |   0.224  1614.1 |   0.292  1233.6 |   0.237  1521.7 |   0.316  1141.2 |   0.516   698.6 |    1.06x    1.08x |      32 |  81/147/ 117.00
  8192 |   0.349  2065.4 |   0.412  1749.6 |   0.399  1806.9 |   0.467  1545.6 |   0.815   885.2 |    1.14x    1.13x |      32 | 174/347/ 251.50
 16384 |   0.621  2322.4 |   0.718  2008.7 |   0.694  2080.1 |   0.771  1870.8 |   1.518   950.4 |    1.12x    1.07x |      32 | 388/733/ 496.50
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

**V41F EP4 · NVFP4**

```text

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
     1 |   0.009    11.3 |     0.012     9.0 |   0.010    11.2 |   0.011     9.5 |    0.013     8.4 |   0.009    12.1 |        1.19x         1.18x             0.94x            0.88x |    TRTLLM BF16    |       0 |   0/  0/   0.00
     2 |   0.018    11.9 |     0.023     9.4 |   0.021    10.0 |   0.018    12.0 |    0.023     9.2 |   0.029     7.3 |        0.99x         0.83x             0.78x            0.77x |   TRTLLM NVFP4    |       1 |   0/  1/   0.00
     4 |   0.032    13.2 |     0.038    11.2 |   0.038    11.3 |   0.037    11.4 |    0.044     9.7 |   0.086     4.9 |        1.15x         0.99x             0.98x            0.85x |   CuteDSL W4A4    |       6 |   0/  1/   0.00
     8 |   0.045    19.0 |     0.050    16.9 |   0.050    17.1 |   0.052    16.5 |    0.058    14.7 |   0.127     6.7 |        1.15x         1.04x             1.02x            0.89x |   CuteDSL W4A4    |      10 |   0/  2/   0.00
    16 |   0.062    27.6 |     0.067    25.2 |   0.068    25.1 |   0.069    24.7 |    0.076    22.3 |   0.176     9.6 |        1.12x         1.02x             1.02x            0.90x |   CuteDSL W4A4    |      15 |   0/  2/   0.00
    32 |   0.125    27.3 |     0.131    26.0 |   0.134    25.4 |   0.132    25.7 |    0.139    24.4 |   0.369     9.2 |        1.06x         0.99x             1.01x            0.95x |   CuteDSL W4A4    |      35 |   0/  4/   0.00
    64 |   0.201    33.9 |     0.207    32.8 |   0.215    31.6 |   0.210    32.3 |    0.219    31.0 |   0.624    10.9 |        1.05x         0.98x             1.01x            0.96x |   CuteDSL W4A4    |      61 |   0/  4/   1.00
   128 |   0.261    52.1 |     0.270    50.4 |   0.278    48.8 |   0.269    50.4 |    0.278    48.9 |   0.828    16.4 |        1.03x         0.97x             1.00x            0.97x |   CuteDSL W4A4    |      82 |   0/  6/   2.00
   256 |   0.300    90.7 |     0.310    87.7 |   0.318    85.4 |   0.308    88.1 |    0.319    85.3 |   0.957    28.4 |        1.03x         0.97x             1.00x            0.97x |   CuteDSL W4A4    |      95 |   0/ 11/   4.00
   512 |   0.304   178.8 |     0.320   169.9 |   0.317   171.4 |   0.315   172.8 |    0.329   165.5 |   0.975    55.8 |        1.03x         0.99x             0.98x            0.96x |   CuteDSL W4A4    |      96 |   2/ 16/   8.00
  4096 |   0.340  1277.9 |     0.400  1087.8 |   0.450   965.8 |   0.364  1193.3 |    0.416  1046.1 |   1.048   415.0 |        1.07x         0.81x             0.91x            0.88x |   CuteDSL W4A4    |      96 |  42/ 84/  63.00
  8192 |   0.409  2126.6 |     0.502  1732.6 |   0.683  1274.3 |   0.453  1921.7 |    0.528  1647.7 |   1.300   669.1 |        1.11x         0.66x             0.90x            0.86x |   CuteDSL W4A4    |      96 |  95/162/ 126.50
 16384 |   0.611  2847.1 |     0.771  2255.5 |   1.524  1141.5 |   0.688  2528.1 |    0.845  2059.1 |   2.055   846.4 |        1.13x         0.45x             0.89x            0.81x |   CuteDSL W4A4    |      96 | 198/337/ 254.00
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

**V41F EP4 · MXFP**

```text

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
     1 |   0.008    12.7 |   0.008    13.0 |   0.010    10.8 |   0.010    10.5 |   0.010    10.8 |    1.18x    1.24x |       0 |   0/  0/   0.00
     2 |   0.019    11.3 |   0.020    10.5 |   0.018    11.5 |   0.020    10.8 |   0.028     7.5 |    0.99x    0.98x |       1 |   0/  1/   0.00
     4 |   0.034    12.6 |   0.048     8.9 |   0.038    11.1 |   0.053     8.0 |   0.086     4.9 |    1.13x    1.10x |       6 |   0/  1/   0.00
     8 |   0.049    17.2 |   0.073    11.7 |   0.051    16.6 |   0.078    10.9 |   0.127     6.7 |    1.04x    1.07x |      10 |   0/  2/   0.00
    16 |   0.059    28.8 |   0.099    17.1 |   0.068    24.8 |   0.106    16.0 |   0.177     9.6 |    1.16x    1.07x |      15 |   0/  2/   0.00
    32 |   0.119    28.5 |   0.211    16.1 |   0.128    26.6 |   0.211    16.1 |   0.370     9.2 |    1.07x    1.00x |      35 |   0/  4/   0.00
    64 |   0.192    35.3 |   0.350    19.4 |   0.202    33.7 |   0.348    19.5 |   0.624    10.9 |    1.05x    0.99x |      61 |   0/  4/   1.00
   128 |   0.251    54.2 |   0.461    29.5 |   0.260    52.2 |   0.456    29.8 |   0.828    16.4 |    1.04x    0.99x |      82 |   0/  6/   2.00
   256 |   0.288    94.4 |   0.530    51.2 |   0.299    90.8 |   0.527    51.6 |   0.957    28.4 |    1.04x    0.99x |      95 |   0/ 11/   4.00
   512 |   0.293   185.5 |   0.539   100.9 |   0.304   178.8 |   0.537   101.2 |   0.975    55.8 |    1.04x    1.00x |      96 |   2/ 16/   8.00
  4096 |   0.349  1244.8 |   0.576   755.3 |   0.388  1122.0 |   0.589   738.8 |   1.049   414.6 |    1.11x    1.02x |      96 |  42/ 84/  63.00
  8192 |   0.496  1753.5 |   0.645  1348.0 |   0.524  1658.7 |   0.670  1299.1 |   1.286   676.5 |    1.06x    1.04x |      96 |  95/162/ 126.50
 16384 |   0.814  2138.0 |   0.978  1779.1 |   0.895  1942.6 |   1.066  1631.3 |   2.060   844.3 |    1.10x    1.09x |      96 | 198/337/ 254.00
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

