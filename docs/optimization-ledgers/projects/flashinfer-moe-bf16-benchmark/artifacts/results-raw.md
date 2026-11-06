# Complete benchmark result tables

Source latency tables round to 0.001 ms. All latency values below preserve that display precision. Speedups use matching unrounded capture JSON when available; otherwise they are approximate ratios of the printed values. Each run identifies its source, and speedups display two decimal places. Per-token aggregate speedup is the median of each run's BF16/W4A16 latency ratio, not a ratio of medians. Speedup > 1 means CuTe DSL W4A16 is faster than TRTLLM BF16.

## inference run 1: inference-1.log

Command and recorded environment:

```sh
export CUDA_VISIBLE_DEVICES=0
export FLASHINFER_DISABLE_VERSION_CHECK=1
export MAX_JOBS=8
/usr/bin/python3 /workspace/flashinfer-moe-bf16-benchmark/capture_benchmark.py --repo /workspace/flashinfer-moe-bf16-benchmark/flashinfer --json-out /workspace/flashinfer-moe-bf16-benchmark/artifacts/inference-1.json --num-tokens 1,2,4,8,16,32,64,128,256,512,1024,2048,4096 --ep 8 --warmup 10 --iters 100 --routing-input-mode logits --use-per-token-activation --include-activation-quant
```

```text
DeepSeek-V3 MoE Performance Benchmark
GPU: NVIDIA B300 SXM6 AC
CuteDSL API: Wrapper
Per-token activation: True
Initial activation quantization: True
CuteDSL modes: W4A4 and W4A16; TRTLLM baselines: NVFP4 and BF16
Tensor parallelism simulation: TP=1
CUDA profiler capture: False
CuteDSL finalize: atomic fused
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
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
Timed initial activation quantization for FP4-activation backends: included; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: atomic fused
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
CUTLASS omitted: it does not consume the per-token activation scale.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   |  CuteDSL W4A16  |     TRTLLM      |   TRTLLM BF16   | Speedup vs TRTLLM  |  Speedup vs BF16   |  Winner  | Active  |     Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |     W4A4     W4A16 |     W4A4     W4A16 |          | experts | min/max/median
---------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.042     2.1 |   0.040     2.2 |   0.034     2.6 |   0.053     1.7 |     0.82x    0.87x |     1.26x    1.34x |  TRTLLM  |       2 |   0/  1/   0.00
     2 |   0.053     3.3 |   0.046     3.9 |   0.046     3.8 |   0.079     2.2 |     0.87x    1.01x |     1.49x    1.72x |  W4A16   |       4 |   0/  1/   0.00
     4 |   0.072     4.9 |   0.062     5.7 |   0.060     5.9 |   0.116     3.0 |     0.83x    0.97x |     1.61x    1.87x |  TRTLLM  |       7 |   0/  1/   0.00
     8 |   0.088     8.0 |   0.078     9.0 |   0.074     9.5 |   0.157     4.5 |     0.84x    0.95x |     1.79x    2.01x |  TRTLLM  |      10 |   0/  2/   0.00
    16 |   0.097    14.6 |   0.084    16.8 |   0.086    16.3 |   0.190     7.4 |     0.89x    1.03x |     1.97x    2.27x |  W4A16   |      13 |   0/  2/   0.00
    32 |   0.132    21.4 |   0.120    23.5 |   0.116    24.3 |   0.287     9.8 |     0.88x    0.97x |     2.18x    2.39x |  TRTLLM  |      21 |   0/  3/   1.00
    64 |   0.165    34.2 |   0.153    36.8 |   0.148    38.0 |   0.386    14.6 |     0.90x    0.97x |     2.34x    2.52x |  TRTLLM  |      29 |   0/  5/   2.00
   128 |   0.170    66.5 |   0.157    71.8 |   0.154    73.2 |   0.398    28.3 |     0.91x    0.98x |     2.34x    2.53x |  TRTLLM  |      30 |   0/  8/   3.00
   256 |   0.178   126.8 |   0.164   137.3 |   0.164   137.9 |   0.427    52.8 |     0.92x    1.00x |     2.40x    2.60x |  TRTLLM  |      32 |   1/ 11/   7.00
   512 |   0.182   247.3 |   0.169   267.6 |   0.174   259.3 |   0.436   103.5 |     0.95x    1.03x |     2.39x    2.58x |  W4A16   |      32 |   7/ 23/  14.00
  1024 |   0.192   470.5 |   0.190   475.4 |   0.316   285.6 |   0.443   203.8 |     1.65x    1.66x |     2.31x    2.33x |  W4A16   |      32 |  17/ 42/  28.50
  2048 |   0.213   848.8 |   0.233   774.5 |   0.326   553.7 |   0.477   378.2 |     1.53x    1.40x |     2.24x    2.05x |   W4A4   |      32 |  38/ 74/  57.50
  4096 |   0.268  1346.3 |   0.362   997.3 |   0.338  1066.3 |   0.529   681.8 |     1.26x    0.94x |     1.97x    1.46x |   W4A4   |      32 |  81/147/ 117.00
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend
```

## inference run 2: inference-2.log

Command and recorded environment:

```sh
export CUDA_VISIBLE_DEVICES=0
export FLASHINFER_DISABLE_VERSION_CHECK=1
export MAX_JOBS=8
/usr/bin/python3 /workspace/flashinfer-moe-bf16-benchmark/capture_benchmark.py --repo /workspace/flashinfer-moe-bf16-benchmark/flashinfer --json-out /workspace/flashinfer-moe-bf16-benchmark/artifacts/inference-2.json --num-tokens 1,2,4,8,16,32,64,128,256,512,1024,2048,4096 --ep 8 --warmup 10 --iters 100 --routing-input-mode logits --use-per-token-activation --include-activation-quant
```

```text
DeepSeek-V3 MoE Performance Benchmark
GPU: NVIDIA B300 SXM6 AC
CuteDSL API: Wrapper
Per-token activation: True
Initial activation quantization: True
CuteDSL modes: W4A4 and W4A16; TRTLLM baselines: NVFP4 and BF16
Tensor parallelism simulation: TP=1
CUDA profiler capture: False
CuteDSL finalize: atomic fused
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
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
Timed initial activation quantization for FP4-activation backends: included; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: atomic fused
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
CUTLASS omitted: it does not consume the per-token activation scale.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   |  CuteDSL W4A16  |     TRTLLM      |   TRTLLM BF16   | Speedup vs TRTLLM  |  Speedup vs BF16   |  Winner  | Active  |     Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |     W4A4     W4A16 |     W4A4     W4A16 |          | experts | min/max/median
---------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.048     1.8 |   0.039     2.2 |   0.035     2.5 |   0.051     1.7 |     0.73x    0.88x |     1.06x    1.28x |  TRTLLM  |       2 |   0/  1/   0.00
     2 |   0.053     3.3 |   0.046     3.9 |   0.046     3.8 |   0.079     2.2 |     0.87x    1.01x |     1.49x    1.73x |  W4A16   |       4 |   0/  1/   0.00
     4 |   0.072     4.9 |   0.062     5.7 |   0.060     5.9 |   0.117     3.0 |     0.83x    0.97x |     1.62x    1.90x |  TRTLLM  |       7 |   0/  1/   0.00
     8 |   0.088     8.0 |   0.078     9.0 |   0.074     9.5 |   0.156     4.5 |     0.84x    0.95x |     1.78x    2.00x |  TRTLLM  |      10 |   0/  2/   0.00
    16 |   0.097    14.6 |   0.087    16.3 |   0.087    16.3 |   0.190     7.4 |     0.90x    1.00x |     1.96x    2.19x |  W4A16   |      13 |   0/  2/   0.00
    32 |   0.132    21.4 |   0.120    23.5 |   0.116    24.3 |   0.287     9.8 |     0.88x    0.97x |     2.18x    2.39x |  TRTLLM  |      21 |   0/  3/   1.00
    64 |   0.165    34.2 |   0.153    36.8 |   0.149    37.9 |   0.387    14.6 |     0.90x    0.97x |     2.34x    2.53x |  TRTLLM  |      29 |   0/  5/   2.00
   128 |   0.170    66.4 |   0.157    71.7 |   0.154    73.1 |   0.398    28.3 |     0.91x    0.98x |     2.34x    2.53x |  TRTLLM  |      30 |   0/  8/   3.00
   256 |   0.178   126.7 |   0.164   137.2 |   0.164   137.8 |   0.427    52.8 |     0.92x    1.00x |     2.40x    2.60x |  TRTLLM  |      32 |   1/ 11/   7.00
   512 |   0.183   247.1 |   0.169   267.4 |   0.174   259.2 |   0.436   103.5 |     0.95x    1.03x |     2.39x    2.58x |  W4A16   |      32 |   7/ 23/  14.00
  1024 |   0.191   471.0 |   0.190   475.1 |   0.317   284.7 |   0.442   203.9 |     1.65x    1.67x |     2.31x    2.33x |  W4A16   |      32 |  17/ 42/  28.50
  2048 |   0.213   848.6 |   0.233   774.4 |   0.326   553.2 |   0.477   378.4 |     1.53x    1.40x |     2.24x    2.05x |   W4A4   |      32 |  38/ 74/  57.50
  4096 |   0.268  1345.8 |   0.363   994.6 |   0.339  1065.5 |   0.528   683.5 |     1.26x    0.93x |     1.97x    1.46x |   W4A4   |      32 |  81/147/ 117.00
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend
```

## inference run 3: inference-3.log

Command and recorded environment:

```sh
export CUDA_VISIBLE_DEVICES=0
export FLASHINFER_DISABLE_VERSION_CHECK=1
export MAX_JOBS=8
/usr/bin/python3 /workspace/flashinfer-moe-bf16-benchmark/capture_benchmark.py --repo /workspace/flashinfer-moe-bf16-benchmark/flashinfer --json-out /workspace/flashinfer-moe-bf16-benchmark/artifacts/inference-3.json --num-tokens 1,2,4,8,16,32,64,128,256,512,1024,2048,4096 --ep 8 --warmup 10 --iters 100 --routing-input-mode logits --use-per-token-activation --include-activation-quant
```

```text
DeepSeek-V3 MoE Performance Benchmark
GPU: NVIDIA B300 SXM6 AC
CuteDSL API: Wrapper
Per-token activation: True
Initial activation quantization: True
CuteDSL modes: W4A4 and W4A16; TRTLLM baselines: NVFP4 and BF16
Tensor parallelism simulation: TP=1
CUDA profiler capture: False
CuteDSL finalize: atomic fused
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
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
Timed initial activation quantization for FP4-activation backends: included; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: atomic fused
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
CUTLASS omitted: it does not consume the per-token activation scale.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   |  CuteDSL W4A16  |     TRTLLM      |   TRTLLM BF16   | Speedup vs TRTLLM  |  Speedup vs BF16   |  Winner  | Active  |     Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |     W4A4     W4A16 |     W4A4     W4A16 |          | experts | min/max/median
---------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.048     1.8 |   0.040     2.2 |   0.034     2.6 |   0.051     1.7 |     0.72x    0.87x |     1.06x    1.28x |  TRTLLM  |       2 |   0/  1/   0.00
     2 |   0.053     3.3 |   0.046     3.9 |   0.046     3.8 |   0.079     2.2 |     0.87x    1.01x |     1.49x    1.73x |  W4A16   |       4 |   0/  1/   0.00
     4 |   0.072     4.9 |   0.064     5.5 |   0.060     5.9 |   0.116     3.0 |     0.83x    0.94x |     1.61x    1.83x |  TRTLLM  |       7 |   0/  1/   0.00
     8 |   0.088     8.0 |   0.078     9.0 |   0.074     9.5 |   0.156     4.5 |     0.84x    0.95x |     1.78x    2.00x |  TRTLLM  |      10 |   0/  2/   0.00
    16 |   0.097    14.6 |   0.087    16.3 |   0.086    16.4 |   0.190     7.4 |     0.89x    0.99x |     1.97x    2.20x |  TRTLLM  |      13 |   0/  2/   0.00
    32 |   0.132    21.4 |   0.120    23.5 |   0.116    24.3 |   0.287     9.8 |     0.88x    0.97x |     2.18x    2.39x |  TRTLLM  |      21 |   0/  3/   1.00
    64 |   0.165    34.1 |   0.153    36.8 |   0.149    37.8 |   0.387    14.6 |     0.90x    0.97x |     2.34x    2.53x |  TRTLLM  |      29 |   0/  5/   2.00
   128 |   0.170    66.4 |   0.157    71.8 |   0.154    73.2 |   0.400    28.2 |     0.91x    0.98x |     2.36x    2.55x |  TRTLLM  |      30 |   0/  8/   3.00
   256 |   0.178   126.9 |   0.164   137.2 |   0.163   138.0 |   0.427    52.8 |     0.92x    0.99x |     2.40x    2.60x |  TRTLLM  |      32 |   1/ 11/   7.00
   512 |   0.182   247.7 |   0.168   267.7 |   0.174   258.9 |   0.436   103.4 |     0.96x    1.03x |     2.39x    2.59x |  W4A16   |      32 |   7/ 23/  14.00
  1024 |   0.192   470.6 |   0.190   475.5 |   0.316   285.5 |   0.443   203.8 |     1.65x    1.67x |     2.31x    2.33x |  W4A16   |      32 |  17/ 42/  28.50
  2048 |   0.212   848.9 |   0.233   774.4 |   0.326   554.0 |   0.477   378.1 |     1.53x    1.40x |     2.25x    2.05x |   W4A4   |      32 |  38/ 74/  57.50
  4096 |   0.268  1346.0 |   0.362   997.1 |   0.338  1066.0 |   0.529   682.3 |     1.26x    0.94x |     1.97x    1.46x |   W4A4   |      32 |  81/147/ 117.00
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend
```

## rl run 1: rl-1.log

Command and recorded environment:

```sh
export CUDA_VISIBLE_DEVICES=0
export FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1
export FLASHINFER_DISABLE_VERSION_CHECK=1
export FLASHINFER_NVFP4_4OVER6=1
export FLASHINFER_NVFP4_4OVER6_E4M3_USE_256=1
export FLASHINFER_NVFP4_4OVER6_ERR_MODE=MSE
export FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH=1
export MAX_JOBS=8
/usr/bin/python3 /workspace/flashinfer-moe-bf16-benchmark/capture_benchmark.py --repo /workspace/flashinfer-moe-bf16-benchmark/flashinfer --json-out /workspace/flashinfer-moe-bf16-benchmark/artifacts/rl-1.json --num-tokens 1,2,4,8,16,32,64,128,256,512,1024,2048,4096 --ep 8 --warmup 10 --iters 100 --routing-input-mode logits --use-per-token-activation --include-activation-quant --no-fused-finalize
```

```text
DeepSeek-V3 MoE Performance Benchmark
GPU: NVIDIA B300 SXM6 AC
CuteDSL API: Wrapper
Per-token activation: True
Initial activation quantization: True
CuteDSL modes: W4A4 and W4A16; TRTLLM baselines: NVFP4 and BF16
Tensor parallelism simulation: TP=1
CUDA profiler capture: False
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
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
Timed initial activation quantization for FP4-activation backends: included; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
CUTLASS omitted: it does not consume the per-token activation scale.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   |  CuteDSL W4A16  |     TRTLLM      |   TRTLLM BF16   | Speedup vs TRTLLM  |  Speedup vs BF16   |  Winner  | Active  |     Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |     W4A4     W4A16 |     W4A4     W4A16 |          | experts | min/max/median
---------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.048     1.8 |   0.039     2.2 |   0.036     2.5 |   0.051     1.7 |     0.74x    0.91x |     1.05x    1.29x |  TRTLLM  |       2 |   0/  1/   0.00
     2 |   0.059     3.0 |   0.046     3.8 |   0.047     3.7 |   0.078     2.3 |     0.80x    1.03x |     1.32x    1.70x |  W4A16   |       4 |   0/  1/   0.00
     4 |   0.078     4.5 |   0.061     5.8 |   0.061     5.7 |   0.117     3.0 |     0.79x    1.01x |     1.51x    1.93x |  W4A16   |       7 |   0/  1/   0.00
     8 |   0.093     7.6 |   0.076     9.3 |   0.076     9.3 |   0.157     4.5 |     0.82x    1.00x |     1.69x    2.07x |  TRTLLM  |      10 |   0/  2/   0.00
    16 |   0.104    13.6 |   0.084    16.9 |   0.087    16.3 |   0.191     7.4 |     0.83x    1.04x |     1.83x    2.28x |  W4A16   |      13 |   0/  2/   0.00
    32 |   0.138    20.4 |   0.117    24.1 |   0.117    24.0 |   0.286     9.9 |     0.85x    1.01x |     2.07x    2.45x |  W4A16   |      21 |   0/  3/   1.00
    64 |   0.175    32.3 |   0.150    37.5 |   0.150    37.5 |   0.386    14.6 |     0.86x    1.00x |     2.21x    2.57x |  W4A16   |      29 |   0/  5/   2.00
   128 |   0.180    62.8 |   0.155    72.9 |   0.156    72.1 |   0.398    28.3 |     0.87x    1.01x |     2.21x    2.57x |  W4A16   |      30 |   0/  8/   3.00
   256 |   0.188   119.6 |   0.167   134.7 |   0.166   136.0 |   0.427    52.8 |     0.88x    0.99x |     2.26x    2.55x |  TRTLLM  |      32 |   1/ 11/   7.00
   512 |   0.194   232.1 |   0.167   270.1 |   0.177   254.2 |   0.435   103.6 |     0.91x    1.06x |     2.24x    2.61x |  W4A16   |      32 |   7/ 23/  14.00
  1024 |   0.208   433.7 |   0.185   487.7 |   0.319   282.7 |   0.443   203.7 |     1.53x    1.73x |     2.13x    2.39x |  W4A16   |      32 |  17/ 42/  28.50
  2048 |   0.238   758.6 |   0.224   807.1 |   0.334   540.8 |   0.477   378.0 |     1.40x    1.49x |     2.01x    2.14x |  W4A16   |      32 |  38/ 74/  57.50
  4096 |   0.311  1160.4 |   0.328  1098.6 |   0.350  1030.2 |   0.529   681.9 |     1.13x    1.07x |     1.70x    1.61x |   W4A4   |      32 |  81/147/ 117.00
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend
```

## rl run 2: rl-2.log

Command and recorded environment:

```sh
export CUDA_VISIBLE_DEVICES=0
export FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1
export FLASHINFER_DISABLE_VERSION_CHECK=1
export FLASHINFER_NVFP4_4OVER6=1
export FLASHINFER_NVFP4_4OVER6_E4M3_USE_256=1
export FLASHINFER_NVFP4_4OVER6_ERR_MODE=MSE
export FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH=1
export MAX_JOBS=8
/usr/bin/python3 /workspace/flashinfer-moe-bf16-benchmark/capture_benchmark.py --repo /workspace/flashinfer-moe-bf16-benchmark/flashinfer --json-out /workspace/flashinfer-moe-bf16-benchmark/artifacts/rl-2.json --num-tokens 1,2,4,8,16,32,64,128,256,512,1024,2048,4096 --ep 8 --warmup 10 --iters 100 --routing-input-mode logits --use-per-token-activation --include-activation-quant --no-fused-finalize
```

```text
DeepSeek-V3 MoE Performance Benchmark
GPU: NVIDIA B300 SXM6 AC
CuteDSL API: Wrapper
Per-token activation: True
Initial activation quantization: True
CuteDSL modes: W4A4 and W4A16; TRTLLM baselines: NVFP4 and BF16
Tensor parallelism simulation: TP=1
CUDA profiler capture: False
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
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
Timed initial activation quantization for FP4-activation backends: included; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
CUTLASS omitted: it does not consume the per-token activation scale.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   |  CuteDSL W4A16  |     TRTLLM      |   TRTLLM BF16   | Speedup vs TRTLLM  |  Speedup vs BF16   |  Winner  | Active  |     Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |     W4A4     W4A16 |     W4A4     W4A16 |          | experts | min/max/median
---------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.048     1.8 |   0.039     2.2 |   0.036     2.5 |   0.053     1.7 |     0.74x    0.91x |     1.10x    1.35x |  TRTLLM  |       2 |   0/  1/   0.00
     2 |   0.059     3.0 |   0.046     3.8 |   0.047     3.7 |   0.079     2.2 |     0.80x    1.03x |     1.34x    1.71x |  W4A16   |       4 |   0/  1/   0.00
     4 |   0.077     4.5 |   0.060     5.8 |   0.061     5.7 |   0.116     3.0 |     0.79x    1.02x |     1.50x    1.92x |  W4A16   |       7 |   0/  1/   0.00
     8 |   0.093     7.6 |   0.075     9.4 |   0.075     9.4 |   0.160     4.4 |     0.81x    1.00x |     1.72x    2.13x |  TRTLLM  |      10 |   0/  2/   0.00
    16 |   0.104    13.5 |   0.083    16.9 |   0.087    16.3 |   0.190     7.4 |     0.83x    1.04x |     1.83x    2.28x |  W4A16   |      13 |   0/  2/   0.00
    32 |   0.138    20.4 |   0.115    24.5 |   0.117    24.1 |   0.287     9.8 |     0.85x    1.02x |     2.08x    2.49x |  W4A16   |      21 |   0/  3/   1.00
    64 |   0.175    32.3 |   0.150    37.5 |   0.150    37.6 |   0.386    14.6 |     0.86x    1.00x |     2.21x    2.57x |  TRTLLM  |      29 |   0/  5/   2.00
   128 |   0.180    62.8 |   0.153    73.5 |   0.156    72.1 |   0.400    28.2 |     0.87x    1.02x |     2.23x    2.61x |  W4A16   |      30 |   0/  8/   3.00
   256 |   0.189   119.6 |   0.167   134.7 |   0.165   136.3 |   0.427    52.8 |     0.88x    0.99x |     2.26x    2.55x |  TRTLLM  |      32 |   1/ 11/   7.00
   512 |   0.194   232.2 |   0.167   270.2 |   0.177   254.4 |   0.436   103.5 |     0.91x    1.06x |     2.24x    2.61x |  W4A16   |      32 |   7/ 23/  14.00
  1024 |   0.208   433.7 |   0.185   487.9 |   0.320   282.2 |   0.443   203.5 |     1.54x    1.73x |     2.13x    2.40x |  W4A16   |      32 |  17/ 42/  28.50
  2048 |   0.238   759.1 |   0.224   807.1 |   0.333   542.0 |   0.477   378.2 |     1.40x    1.49x |     2.01x    2.13x |  W4A16   |      32 |  38/ 74/  57.50
  4096 |   0.311  1160.6 |   0.328  1098.4 |   0.350  1029.4 |   0.528   682.8 |     1.13x    1.07x |     1.70x    1.61x |   W4A4   |      32 |  81/147/ 117.00
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend
```

## rl run 3: rl-3.log

Command and recorded environment:

```sh
export CUDA_VISIBLE_DEVICES=0
export FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1
export FLASHINFER_DISABLE_VERSION_CHECK=1
export FLASHINFER_NVFP4_4OVER6=1
export FLASHINFER_NVFP4_4OVER6_E4M3_USE_256=1
export FLASHINFER_NVFP4_4OVER6_ERR_MODE=MSE
export FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH=1
export MAX_JOBS=8
/usr/bin/python3 /workspace/flashinfer-moe-bf16-benchmark/capture_benchmark.py --repo /workspace/flashinfer-moe-bf16-benchmark/flashinfer --json-out /workspace/flashinfer-moe-bf16-benchmark/artifacts/rl-3.json --num-tokens 1,2,4,8,16,32,64,128,256,512,1024,2048,4096 --ep 8 --warmup 10 --iters 100 --routing-input-mode logits --use-per-token-activation --include-activation-quant --no-fused-finalize
```

```text
DeepSeek-V3 MoE Performance Benchmark
GPU: NVIDIA B300 SXM6 AC
CuteDSL API: Wrapper
Per-token activation: True
Initial activation quantization: True
CuteDSL modes: W4A4 and W4A16; TRTLLM baselines: NVFP4 and BF16
Tensor parallelism simulation: TP=1
CUDA profiler capture: False
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
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
Timed initial activation quantization for FP4-activation backends: included; W4A16 and TRTLLM BF16 consume BF16 directly
CuteDSL finalize: deterministic two-stage
TRTLLM NVFP4/BF16 finalize: native (unaffected by --no-fused-finalize).
CUTLASS omitted: it does not consume the per-token activation scale.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Tokens |  CuteDSL W4A4   |  CuteDSL W4A16  |     TRTLLM      |   TRTLLM BF16   | Speedup vs TRTLLM  |  Speedup vs BF16   |  Winner  | Active  |     Stats
       |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |      ms  TFLOPS |     W4A4     W4A16 |     W4A4     W4A16 |          | experts | min/max/median
---------------------------------------------------------------------------------------------------------------------------------------------------------------
     1 |   0.048     1.8 |   0.040     2.2 |   0.036     2.4 |   0.053     1.7 |     0.75x    0.90x |     1.09x    1.31x |  TRTLLM  |       2 |   0/  1/   0.00
     2 |   0.059     3.0 |   0.046     3.8 |   0.047     3.7 |   0.079     2.2 |     0.81x    1.03x |     1.34x    1.71x |  W4A16   |       4 |   0/  1/   0.00
     4 |   0.077     4.6 |   0.060     5.8 |   0.061     5.7 |   0.117     3.0 |     0.79x    1.01x |     1.51x    1.93x |  W4A16   |       7 |   0/  1/   0.00
     8 |   0.093     7.6 |   0.075     9.4 |   0.075     9.4 |   0.157     4.5 |     0.81x    1.00x |     1.68x    2.09x |  W4A16   |      10 |   0/  2/   0.00
    16 |   0.104    13.6 |   0.083    16.9 |   0.087    16.3 |   0.190     7.4 |     0.84x    1.04x |     1.83x    2.28x |  W4A16   |      13 |   0/  2/   0.00
    32 |   0.139    20.3 |   0.117    24.1 |   0.117    24.1 |   0.287     9.8 |     0.84x    1.00x |     2.07x    2.46x |  W4A16   |      21 |   0/  3/   1.00
    64 |   0.175    32.3 |   0.152    37.0 |   0.150    37.5 |   0.386    14.6 |     0.86x    0.99x |     2.21x    2.54x |  TRTLLM  |      29 |   0/  5/   2.00
   128 |   0.180    62.8 |   0.155    72.8 |   0.156    72.2 |   0.398    28.4 |     0.87x    1.01x |     2.21x    2.57x |  W4A16   |      30 |   0/  8/   3.00
   256 |   0.189   119.5 |   0.162   139.1 |   0.166   136.0 |   0.427    52.8 |     0.88x    1.02x |     2.26x    2.63x |  W4A16   |      32 |   1/ 11/   7.00
   512 |   0.194   232.3 |   0.167   270.1 |   0.177   254.3 |   0.436   103.3 |     0.91x    1.06x |     2.25x    2.61x |  W4A16   |      32 |   7/ 23/  14.00
  1024 |   0.208   433.5 |   0.185   487.5 |   0.322   280.3 |   0.443   203.4 |     1.55x    1.74x |     2.13x    2.40x |  W4A16   |      32 |  17/ 42/  28.50
  2048 |   0.238   759.5 |   0.223   807.2 |   0.333   542.3 |   0.477   378.1 |     1.40x    1.49x |     2.01x    2.14x |  W4A16   |      32 |  38/ 74/  57.50
  4096 |   0.311  1159.4 |   0.329  1097.9 |   0.351  1029.3 |   0.528   683.4 |     1.13x    1.07x |     1.70x    1.61x |   W4A4   |      32 |  81/147/ 117.00
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Speedup > 1.0 means that CuTe DSL mode is faster than the comparison backend
```
