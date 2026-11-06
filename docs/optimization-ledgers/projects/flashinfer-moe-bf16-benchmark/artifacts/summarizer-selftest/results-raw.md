# Complete benchmark result tables

Source latency tables round to 0.001 ms. All latency values below preserve that display precision. Speedups use matching unrounded capture JSON when available; otherwise they are approximate ratios of the printed values. Each run identifies its source, and speedups display two decimal places. Per-token aggregate speedup is the median of each run's BF16/W4A16 latency ratio, not a ratio of medians. Speedup > 1 means CuTe DSL W4A16 is faster than TRTLLM BF16.

## inference run 1: inference-1.log

```text
DeepSeek-V3 MoE Performance Benchmark
GPU: SYNTHETIC PARSER FIXTURE
TRTLLM NVFP4/BF16 finalize: native
```

```text
===============================================================================================================================================================
DeepSeek-V3 MoE Benchmark: CuteDSL W4A4/W4A16 vs TRTLLM NVFP4/BF16 (EP=8, TP=1)
===============================================================================================================================================================
Model: hidden=7168, intermediate=2048, experts=256, top_k=8
EP Config: 32 local experts (simulating 8-way parallelism)
TP Config: intermediate size 2048 (simulating 1-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Timed initial activation quantization for FP4-activation backends: excluded; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: atomic fused
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
CUTLASS omitted: it does not consume the per-token activation scale.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   |  CuteDSL W4A16  |     TRTLLM      |   TRTLLM BF16   | Speedup vs TRTLLM  |  Speedup vs BF16   |  Winner  | Active  |     Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |     W4A4     W4A16 |     W4A4     W4A16 |          | experts | min/max/median
---------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.99x    1.50x |     3.98x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
     2 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.99x    1.50x |     3.98x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
     4 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.99x    1.50x |     3.98x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
     8 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.99x    1.50x |     3.98x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
    16 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.98x    1.50x |     3.98x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
    32 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.98x    1.50x |     3.98x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
    64 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.98x    1.50x |     3.97x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
   128 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.98x    1.50x |     3.97x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
   256 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.98x    1.50x |     3.97x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   512 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.95x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
  1024 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.95x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
  2048 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.92x    1.49x |     3.88x    1.98x |   W4A4   |       4 |   1/ 10/   2.00
  4096 |   0.019    10.0 |   0.036    10.0 |   0.054    10.0 |   0.072    10.0 |     2.86x    1.48x |     3.78x    1.96x |   W4A4   |       4 |   1/ 10/   2.00
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend
```

## inference run 2: inference-2.log

```text
DeepSeek-V3 MoE Performance Benchmark
GPU: SYNTHETIC PARSER FIXTURE
TRTLLM NVFP4/BF16 finalize: native
```

```text
===============================================================================================================================================================
DeepSeek-V3 MoE Benchmark: CuteDSL W4A4/W4A16 vs TRTLLM NVFP4/BF16 (EP=8, TP=1)
===============================================================================================================================================================
Model: hidden=7168, intermediate=2048, experts=256, top_k=8
EP Config: 32 local experts (simulating 8-way parallelism)
TP Config: intermediate size 2048 (simulating 1-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Timed initial activation quantization for FP4-activation backends: excluded; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: atomic fused
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
CUTLASS omitted: it does not consume the per-token activation scale.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   |  CuteDSL W4A16  |     TRTLLM      |   TRTLLM BF16   | Speedup vs TRTLLM  |  Speedup vs BF16   |  Winner  | Active  |     Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |     W4A4     W4A16 |     W4A4     W4A16 |          | experts | min/max/median
---------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.96x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
     2 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.96x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
     4 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.96x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
     8 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.96x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
    16 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.96x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
    32 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.95x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
    64 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.95x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   128 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.95x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   256 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.96x    1.50x |     3.94x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   512 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.95x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
  1024 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.94x    1.49x |     3.91x    1.98x |   W4A4   |       4 |   1/ 10/   2.00
  2048 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.91x    1.49x |     3.86x    1.98x |   W4A4   |       4 |   1/ 10/   2.00
  4096 |   0.019    10.0 |   0.037    10.0 |   0.054    10.0 |   0.072    10.0 |     2.84x    1.48x |     3.77x    1.96x |   W4A4   |       4 |   1/ 10/   2.00
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend
```

## inference run 3: inference-3.log

```text
DeepSeek-V3 MoE Performance Benchmark
GPU: SYNTHETIC PARSER FIXTURE
TRTLLM NVFP4/BF16 finalize: native
```

```text
===============================================================================================================================================================
DeepSeek-V3 MoE Benchmark: CuteDSL W4A4/W4A16 vs TRTLLM NVFP4/BF16 (EP=8, TP=1)
===============================================================================================================================================================
Model: hidden=7168, intermediate=2048, experts=256, top_k=8
EP Config: 32 local experts (simulating 8-way parallelism)
TP Config: intermediate size 2048 (simulating 1-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Timed initial activation quantization for FP4-activation backends: excluded; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: atomic fused
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
CUTLASS omitted: it does not consume the per-token activation scale.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   |  CuteDSL W4A16  |     TRTLLM      |   TRTLLM BF16   | Speedup vs TRTLLM  |  Speedup vs BF16   |  Winner  | Active  |     Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |     W4A4     W4A16 |     W4A4     W4A16 |          | experts | min/max/median
---------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.96x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
     2 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.96x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
     4 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.96x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
     8 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.96x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
    16 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.96x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
    32 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.96x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
    64 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.95x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   128 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.95x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   256 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.95x    1.49x |     3.92x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   512 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.94x    1.49x |     3.91x    1.98x |   W4A4   |       4 |   1/ 10/   2.00
  1024 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.92x    1.49x |     3.89x    1.98x |   W4A4   |       4 |   1/ 10/   2.00
  2048 |   0.019    10.0 |   0.036    10.0 |   0.054    10.0 |   0.071    10.0 |     2.89x    1.49x |     3.84x    1.97x |   W4A4   |       4 |   1/ 10/   2.00
  4096 |   0.019    10.0 |   0.037    10.0 |   0.054    10.0 |   0.072    10.0 |     2.83x    1.48x |     3.75x    1.96x |   W4A4   |       4 |   1/ 10/   2.00
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend
```

## rl run 1: rl-1.log

```text
DeepSeek-V3 MoE Performance Benchmark
GPU: SYNTHETIC PARSER FIXTURE
TRTLLM NVFP4/BF16 finalize: native
```

```text
===============================================================================================================================================================
DeepSeek-V3 MoE Benchmark: CuteDSL W4A4/W4A16 vs TRTLLM NVFP4/BF16 (EP=8, TP=1)
===============================================================================================================================================================
Model: hidden=7168, intermediate=2048, experts=256, top_k=8
EP Config: 32 local experts (simulating 8-way parallelism)
TP Config: intermediate size 2048 (simulating 1-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Timed initial activation quantization for FP4-activation backends: excluded; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: atomic fused
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
CUTLASS omitted: it does not consume the per-token activation scale.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   |  CuteDSL W4A16  |     TRTLLM      |   TRTLLM BF16   | Speedup vs TRTLLM  |  Speedup vs BF16   |  Winner  | Active  |     Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |     W4A4     W4A16 |     W4A4     W4A16 |          | experts | min/max/median
---------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.99x    1.50x |     3.98x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
     2 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.99x    1.50x |     3.98x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
     4 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.99x    1.50x |     3.98x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
     8 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.99x    1.50x |     3.98x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
    16 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.98x    1.50x |     3.98x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
    32 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.98x    1.50x |     3.98x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
    64 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.98x    1.50x |     3.97x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
   128 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.98x    1.50x |     3.97x    2.00x |   W4A4   |       4 |   1/ 10/   2.00
   256 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.98x    1.50x |     3.97x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   512 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.95x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
  1024 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.95x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
  2048 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.92x    1.49x |     3.88x    1.98x |   W4A4   |       4 |   1/ 10/   2.00
  4096 |   0.019    10.0 |   0.036    10.0 |   0.054    10.0 |   0.072    10.0 |     2.86x    1.48x |     3.78x    1.96x |   W4A4   |       4 |   1/ 10/   2.00
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend
```

## rl run 2: rl-2.log

```text
DeepSeek-V3 MoE Performance Benchmark
GPU: SYNTHETIC PARSER FIXTURE
TRTLLM NVFP4/BF16 finalize: native
```

```text
===============================================================================================================================================================
DeepSeek-V3 MoE Benchmark: CuteDSL W4A4/W4A16 vs TRTLLM NVFP4/BF16 (EP=8, TP=1)
===============================================================================================================================================================
Model: hidden=7168, intermediate=2048, experts=256, top_k=8
EP Config: 32 local experts (simulating 8-way parallelism)
TP Config: intermediate size 2048 (simulating 1-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Timed initial activation quantization for FP4-activation backends: excluded; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: atomic fused
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
CUTLASS omitted: it does not consume the per-token activation scale.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   |  CuteDSL W4A16  |     TRTLLM      |   TRTLLM BF16   | Speedup vs TRTLLM  |  Speedup vs BF16   |  Winner  | Active  |     Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |     W4A4     W4A16 |     W4A4     W4A16 |          | experts | min/max/median
---------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.96x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
     2 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.96x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
     4 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.96x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
     8 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.96x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
    16 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.96x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
    32 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.95x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
    64 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.95x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   128 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.97x    1.50x |     3.95x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   256 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.070    10.0 |     2.96x    1.50x |     3.94x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   512 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.95x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
  1024 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.94x    1.49x |     3.91x    1.98x |   W4A4   |       4 |   1/ 10/   2.00
  2048 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.91x    1.49x |     3.86x    1.98x |   W4A4   |       4 |   1/ 10/   2.00
  4096 |   0.019    10.0 |   0.037    10.0 |   0.054    10.0 |   0.072    10.0 |     2.84x    1.48x |     3.77x    1.96x |   W4A4   |       4 |   1/ 10/   2.00
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend
```

## rl run 3: rl-3.log

```text
DeepSeek-V3 MoE Performance Benchmark
GPU: SYNTHETIC PARSER FIXTURE
TRTLLM NVFP4/BF16 finalize: native
```

```text
===============================================================================================================================================================
DeepSeek-V3 MoE Benchmark: CuteDSL W4A4/W4A16 vs TRTLLM NVFP4/BF16 (EP=8, TP=1)
===============================================================================================================================================================
Model: hidden=7168, intermediate=2048, experts=256, top_k=8
EP Config: 32 local experts (simulating 8-way parallelism)
TP Config: intermediate size 2048 (simulating 1-way parallelism)
CUDA Graph: enabled, CUPTI: enabled
Routing bias scale: 0.01 (larger values tend to create expert imbalance)
Timed initial activation quantization for FP4-activation backends: excluded; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: atomic fused
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
CUTLASS omitted: it does not consume the per-token activation scale.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   |  CuteDSL W4A16  |     TRTLLM      |   TRTLLM BF16   | Speedup vs TRTLLM  |  Speedup vs BF16   |  Winner  | Active  |     Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |     W4A4     W4A16 |     W4A4     W4A16 |          | experts | min/max/median
---------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.96x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
     2 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.96x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
     4 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.96x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
     8 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.96x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
    16 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.96x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
    32 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.96x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
    64 |   0.018    10.0 |   0.035    10.0 |   0.053    10.0 |   0.071    10.0 |     2.95x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   128 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.95x    1.49x |     3.93x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   256 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.95x    1.49x |     3.92x    1.99x |   W4A4   |       4 |   1/ 10/   2.00
   512 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.94x    1.49x |     3.91x    1.98x |   W4A4   |       4 |   1/ 10/   2.00
  1024 |   0.018    10.0 |   0.036    10.0 |   0.053    10.0 |   0.071    10.0 |     2.92x    1.49x |     3.89x    1.98x |   W4A4   |       4 |   1/ 10/   2.00
  2048 |   0.019    10.0 |   0.036    10.0 |   0.054    10.0 |   0.071    10.0 |     2.89x    1.49x |     3.84x    1.97x |   W4A4   |       4 |   1/ 10/   2.00
  4096 |   0.019    10.0 |   0.037    10.0 |   0.054    10.0 |   0.072    10.0 |     2.83x    1.48x |     3.75x    1.96x |   W4A4   |       4 |   1/ 10/   2.00
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend
```
