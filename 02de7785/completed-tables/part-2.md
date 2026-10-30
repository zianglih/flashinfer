<!-- moe-gather-pipeline-completed-tables-02de7785-part-2 -->
### Benchmark table output — K3 EP8 / N3U EP8 (2/4)

Printed by the unchanged benchmark table functions from saved records: fresh CuTe DSL final-pass results source-equivalent to `02de7785` plus the original TRTLLM final-pass results. TRTLLM is reused, not rerun; these are separate-run comparisons. The original measurement records retain their actual base `82254e20` plus frozen patch identifiers. The heatmaps use two-pass aggregates. Missing or unsupported records remain N/A. [Original fresh-run logs](https://github.com/zianglih/flashinfer/raw/refs/heads/codex/moe-gather-pipeline-assets/02de7785/moe-gather-pipeline-results.tar.gz).

**K3 EP8 · NVFP4**

```text

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
     1 |   0.010    13.4 |     0.012    10.6 |   0.010    13.0 |   0.014     9.3 |              N/A |             N/A |        1.43x         1.39x             1.14x              N/A |   CuteDSL W4A4    |       0 |   0/  0/   0.00
     2 |   0.026    10.3 |     0.028     9.3 |   0.027     9.6 |   0.025    10.7 |              N/A |             N/A |        0.96x         0.90x             0.87x              N/A |   TRTLLM NVFP4    |       3 |   0/  1/   0.00
     4 |   0.052    10.2 |     0.056     9.5 |   0.058     9.1 |   0.056     9.4 |              N/A |             N/A |        1.08x         0.97x             1.01x              N/A |   CuteDSL W4A4    |      12 |   0/  1/   0.00
     8 |   0.080    13.3 |     0.083    12.8 |   0.084    12.6 |   0.082    12.8 |              N/A |             N/A |        1.03x         0.98x             1.00x              N/A |   CuteDSL W4A4    |      18 |   0/  1/   0.00
    16 |   0.113    18.7 |     0.117    18.0 |   0.121    17.5 |   0.116    18.3 |              N/A |             N/A |        1.02x         0.96x             0.99x              N/A |   CuteDSL W4A4    |      30 |   0/  2/   0.00
    32 |   0.175    24.2 |     0.181    23.3 |   0.184    23.0 |   0.176    24.0 |              N/A |             N/A |        1.01x         0.96x             0.97x              N/A |   CuteDSL W4A4    |      54 |   0/  4/   0.00
    64 |   0.237    35.7 |     0.244    34.7 |   0.248    34.1 |   0.235    35.9 |              N/A |             N/A |        0.99x         0.95x             0.97x              N/A |   TRTLLM NVFP4    |      77 |   0/  5/   1.00
   128 |   0.295    57.3 |     0.304    55.7 |   0.309    54.7 |   0.300    56.3 |              N/A |             N/A |        1.02x         0.97x             0.99x              N/A |   CuteDSL W4A4    |      99 |   0/  7/   2.00
   256 |   0.327   103.5 |     0.339    99.9 |   0.345    97.9 |   0.333   101.6 |              N/A |             N/A |        1.02x         0.96x             0.98x              N/A |   CuteDSL W4A4    |     111 |   0/ 12/   4.00
   512 |   0.334   202.3 |     0.353   191.6 |   0.363   186.4 |   0.339   199.5 |              N/A |             N/A |        1.01x         0.93x             0.96x              N/A |   CuteDSL W4A4    |     112 |   3/ 19/   9.00
  4096 |   0.379  1427.3 |     0.451  1199.6 |   0.528  1025.1 |   0.412  1313.1 |              N/A |             N/A |        1.09x         0.78x             0.91x              N/A |   CuteDSL W4A4    |     112 |  35/127/  74.00
  8192 |   0.480  2253.3 |     0.638  1697.3 |   0.958  1130.0 |   0.543  1994.8 |              N/A |             N/A |        1.13x         0.57x             0.85x              N/A |   CuteDSL W4A4    |     112 |  64/252/ 149.50
 16384 |   0.822  2633.2 |     1.044  2073.9 |   1.930  1121.5 |   0.861  2512.8 |              N/A |             N/A |        1.05x         0.45x             0.83x              N/A |   CuteDSL W4A4    |     112 | 148/550/ 298.50
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

**K3 EP8 · MXFP**

```text

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
     1 |   0.010    12.8 |             N/A |   0.012    10.9 |             N/A |             N/A |    1.17x      N/A |       0 |   0/  0/   0.00
     2 |   0.026    10.3 |             N/A |   0.025    10.6 |             N/A |             N/A |    0.98x      N/A |       3 |   0/  1/   0.00
     4 |   0.056     9.4 |             N/A |   0.056     9.4 |             N/A |             N/A |    1.00x      N/A |      12 |   0/  1/   0.00
     8 |   0.075    14.1 |             N/A |   0.080    13.1 |             N/A |             N/A |    1.07x      N/A |      18 |   0/  1/   0.00
    16 |   0.108    19.6 |             N/A |   0.113    18.8 |             N/A |             N/A |    1.04x      N/A |      30 |   0/  2/   0.00
    32 |   0.168    25.2 |             N/A |   0.171    24.7 |             N/A |             N/A |    1.02x      N/A |      54 |   0/  4/   0.00
    64 |   0.227    37.2 |             N/A |   0.227    37.3 |             N/A |             N/A |    1.00x      N/A |      77 |   0/  5/   1.00
   128 |   0.286    59.1 |             N/A |   0.288    58.7 |             N/A |             N/A |    1.01x      N/A |      99 |   0/  7/   2.00
   256 |   0.317   106.7 |             N/A |   0.322   105.2 |             N/A |             N/A |    1.01x      N/A |     111 |   0/ 12/   4.00
   512 |   0.332   204.0 |             N/A |   0.335   202.0 |             N/A |             N/A |    1.01x      N/A |     112 |   3/ 19/   9.00
  4096 |   0.389  1389.6 |             N/A |   0.438  1235.6 |             N/A |             N/A |    1.12x      N/A |     112 |  35/127/  74.00
  8192 |   0.584  1852.4 |             N/A |   0.715  1514.1 |             N/A |             N/A |    1.22x      N/A |     112 |  64/252/ 149.50
 16384 |   1.023  2115.2 |             N/A |   1.209  1790.6 |             N/A |             N/A |    1.18x      N/A |     112 | 148/550/ 298.50
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

**N3U EP8 · NVFP4**

```text

=====================================================================================================================================================================================================================================
Nemotron-3-Ultra MoE Benchmark: CuteDSL W4A4 / PER-TOKEN / W4A16 vs TRTLLM NVFP4 / PER-TOKEN / BF16 (EP=8, TP=1)
=====================================================================================================================================================================================================================================
Model: hidden=2048, intermediate=5120, experts=512, top_k=22
EP Config: 64 local experts (simulating 8-way parallelism)
TP Config: intermediate size 5120 (simulating 1-way parallelism)
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
     1 |   0.020     5.7 |     0.025     4.6 |   0.025     4.6 |   0.020     5.7 |    0.026     4.4 |             N/A |        1.00x         0.81x             0.81x            0.77x |   CuteDSL W4A4    |       3 |   0/  1/   0.00
     2 |   0.027     8.6 |     0.030     7.6 |   0.030     7.7 |   0.028     8.2 |    0.034     6.8 |             N/A |        1.06x         0.94x             0.93x            0.83x |   CuteDSL W4A4    |       6 |   0/  1/   0.00
     4 |   0.034    13.6 |     0.040    11.6 |   0.041    11.3 |   0.038    12.2 |    0.045    10.2 |             N/A |        1.12x         0.93x             0.95x            0.84x |   CuteDSL W4A4    |      10 |   0/  1/   0.00
     8 |   0.047    19.4 |     0.052    17.9 |   0.051    18.1 |   0.052    17.8 |    0.059    15.7 |             N/A |        1.09x         1.02x             1.01x            0.88x |   CuteDSL W4A4    |      17 |   0/  2/   0.00
    16 |   0.083    22.3 |     0.087    21.2 |   0.089    20.8 |   0.089    20.8 |    0.097    19.1 |             N/A |        1.07x         1.00x             1.02x            0.92x |   CuteDSL W4A4    |      36 |   0/  2/   1.00
    32 |   0.103    35.9 |     0.110    33.5 |   0.111    33.2 |   0.110    33.4 |    0.118    31.2 |             N/A |        1.07x         0.99x             1.00x            0.93x |   CuteDSL W4A4    |      45 |   0/  4/   1.00
    64 |   0.130    56.6 |     0.137    53.9 |   0.140    52.6 |   0.136    54.4 |    0.145    51.0 |             N/A |        1.04x         0.97x             0.99x            0.94x |   CuteDSL W4A4    |      60 |   0/  7/   2.00
   128 |   0.136   108.3 |     0.143   102.9 |   0.145   101.6 |   0.142   104.3 |    0.151    97.6 |             N/A |        1.04x         0.97x             0.99x            0.94x |   CuteDSL W4A4    |      63 |   0/ 11/   5.00
   256 |   0.141   209.6 |     0.150   197.2 |   0.154   192.1 |   0.148   198.9 |    0.161   183.8 |             N/A |        1.05x         0.97x             0.99x            0.92x |   CuteDSL W4A4    |      64 |   2/ 21/  10.00
   512 |   0.139   423.5 |     0.157   376.1 |   0.162   364.7 |   0.155   381.7 |    0.172   343.4 |             N/A |        1.11x         0.96x             0.99x            0.90x |   CuteDSL W4A4    |      64 |  11/ 37/  22.00
  4096 |   0.222  2126.1 |     0.330  1430.5 |   0.399  1184.5 |   0.229  2067.3 |    0.313  1511.8 |             N/A |        1.03x         0.57x             0.69x            0.73x |   CuteDSL W4A4    |      64 | 117/252/ 180.50
  8192 |   0.369  2561.9 |     0.566  1669.1 |   0.761  1241.7 |   0.401  2357.4 |    0.562  1681.9 |             N/A |        1.09x         0.53x             0.71x            0.71x |   CuteDSL W4A4    |      64 | 274/511/ 352.00
 16384 |   0.587  3222.0 |     0.946  1996.9 |   1.491  1267.7 |   0.653  2893.5 |    0.963  1961.7 |             N/A |        1.11x         0.44x             0.69x            0.68x |   CuteDSL W4A4    |      64 | 501/1131/ 669.50
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

**N3U EP8 · MXFP**

```text

================================================================================================================================================
Nemotron-3-Ultra MoE Benchmark: CuteDSL MXFP4x8 / MXFP8 vs TRTLLM MXFP4x8 / MXFP8 / BF16 (EP=8, TP=1)
================================================================================================================================================
Model: hidden=2048, intermediate=5120, experts=512, top_k=22
EP Config: 64 local experts (simulating 8-way parallelism)
TP Config: intermediate size 5120 (simulating 1-way parallelism)
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
     1 |   0.021     5.5 |   0.025     4.7 |   0.021     5.5 |   0.024     4.7 |             N/A |    0.99x    1.00x |       3 |   0/  1/   0.00
     2 |   0.030     7.7 |   0.037     6.2 |   0.027     8.5 |   0.037     6.3 |             N/A |    0.91x    0.99x |       6 |   0/  1/   0.00
     4 |   0.037    12.3 |   0.048     9.6 |   0.039    11.9 |   0.056     8.2 |             N/A |    1.04x    1.17x |      10 |   0/  1/   0.00
     8 |   0.047    19.5 |   0.070    13.1 |   0.052    17.6 |   0.078    11.9 |             N/A |    1.11x    1.10x |      17 |   0/  2/   0.00
    16 |   0.082    22.6 |   0.134    13.7 |   0.086    21.6 |   0.139    13.2 |             N/A |    1.05x    1.04x |      36 |   0/  2/   1.00
    32 |   0.101    36.6 |   0.169    21.8 |   0.106    35.0 |   0.171    21.6 |             N/A |    1.05x    1.01x |      45 |   0/  4/   1.00
    64 |   0.128    57.7 |   0.216    34.1 |   0.132    55.9 |   0.218    33.8 |             N/A |    1.03x    1.01x |      60 |   0/  7/   2.00
   128 |   0.130   113.9 |   0.226    65.3 |   0.137   107.5 |   0.229    64.4 |             N/A |    1.06x    1.01x |      63 |   0/ 11/   5.00
   256 |   0.136   216.8 |   0.233   126.6 |   0.150   197.3 |   0.239   123.7 |             N/A |    1.10x    1.02x |      64 |   2/ 21/  10.00
   512 |   0.140   420.4 |   0.241   245.1 |   0.158   372.9 |   0.247   239.4 |             N/A |    1.13x    1.02x |      64 |  11/ 37/  22.00
  4096 |   0.259  1826.1 |   0.314  1505.4 |   0.307  1538.4 |   0.334  1416.3 |             N/A |    1.19x    1.06x |      64 | 117/252/ 180.50
  8192 |   0.436  2169.5 |   0.493  1916.1 |   0.501  1886.0 |   0.547  1728.9 |             N/A |    1.15x    1.11x |      64 | 274/511/ 352.00
 16384 |   0.826  2287.3 |   0.917  2061.6 |   0.854  2214.0 |   0.896  2109.9 |             N/A |    1.03x    0.98x |      64 | 501/1131/ 669.50
------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means the named comparison arm is faster than its TRTLLM baseline.
```

