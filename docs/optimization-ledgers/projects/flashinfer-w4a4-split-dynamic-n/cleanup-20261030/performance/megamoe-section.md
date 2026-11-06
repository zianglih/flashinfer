### Shared W4A16 dequantizer: GLM5 MegaMoE

Following [#6277](https://github.com/flashinfer-ai/flashinfer/pull/6277), this isolates the shared scale-duplication change: both arms use production `4376662a`; **before** restores only `moe_w4a16_utils.py` from the parent of `1e4b127a`, and **after** keeps the current helper. MegaMoE inherits this dequantizer through `_MegaMixedInput._transform_tile`.

- **Workload:** real EP8 on 8×B300 SXM6 AC, D6144/I2048, 256 experts, top8, SwiGLU, grouped routing 8/top4, scaling 2.5. Precomputed routes; PDL and fused deterministic combine enabled; in-kernel FC2 reduction disabled.
- **Measurement:** one control AUTO selection per token count, then the same frozen tactics/routes in four fresh process groups, C1→A1→A2→C2. Each uses 3 warmups and 100 untrimmed cold-L2 CUDA-graph CUPTI samples, aggregated by rank-MAX per iteration. Each reported latency is the median of 200 samples per arm; speedup=`before/after−1`. Tokens 1/2 are measured but excluded from aggregates.
- **Environment:** `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, driver 595.91.07, PyTorch `2.12.0a0+5aff3928d8.nv26.5.50603568`, CuTe DSL 4.8.0, CUPTI Python 13.2.0/library 13.2.86, NVSHMEM4Py 0.3.1/library 3.6.5. Native C++ compilation artifacts are retained outside timing.

Geomean speedup: **+1.54% overall**, **+1.79% decode (4–512)** and **+0.89% prefill (4096–16384)**. All three pooled prefill points improve. Decode is mixed: 4/8/32 tokens regress by 2.53%/1.21%/3.89%, while repeat-phase median spreads reach 11.37%; this does **not** establish uniform per-shape non-regression.

| Global tokens | Before (µs) | After (µs) | Speedup |
|---:|---:|---:|---:|
| 1 | 70.913 | 71.681 | -1.07% |
| 2 | 91.073 | 88.177 | +3.28% |
| 4 | 100.465 | 103.073 | -2.53% |
| 8 | 113.873 | 115.265 | -1.21% |
| 16 | 136.545 | 125.472 | +8.82% |
| 32 | 144.850 | 150.705 | -3.89% |
| 64 | 167.328 | 161.907 | +3.35% |
| 128 | 175.058 | 171.089 | +2.32% |
| 256 | 176.305 | 167.905 | +5.00% |
| 512 | 181.362 | 176.049 | +3.02% |
| 4096 | 404.210 | 403.027 | +0.29% |
| 8192 | 690.740 | 676.068 | +2.17% |
| 16384 | 1271.803 | 1269.000 | +0.22% |

For the representative 16384-token native MegaMoE specialization, SASS instruction count is 6400→6384 and PRMT count 197→181; all other opcode counts match. Both use 96 registers and zero stack/local memory. The audited sequence replaces 16 two-PRMT scale duplications with 16 single-PRMT duplications; this codegen statement is scoped to that specialization.

[All raw samples](https://raw.githubusercontent.com/zianglih/flashinfer/2402bcd61a7cc39f650f6b92dd1aa2293ee50518/pr7290/2026-10-29/glm5-helper-4376662a/raw-samples.csv), [per-phase statistics](https://raw.githubusercontent.com/zianglih/flashinfer/2402bcd61a7cc39f650f6b92dd1aa2293ee50518/pr7290/2026-10-29/glm5-helper-4376662a/summary.csv), [native timing output](https://raw.githubusercontent.com/zianglih/flashinfer/2402bcd61a7cc39f650f6b92dd1aa2293ee50518/pr7290/2026-10-29/glm5-helper-4376662a/native-timing-output.txt), [source/runtime provenance](https://raw.githubusercontent.com/zianglih/flashinfer/2402bcd61a7cc39f650f6b92dd1aa2293ee50518/pr7290/2026-10-29/glm5-helper-4376662a/provenance.json), [native codegen proof](https://raw.githubusercontent.com/zianglih/flashinfer/2402bcd61a7cc39f650f6b92dd1aa2293ee50518/pr7290/2026-10-29/glm5-helper-4376662a/codegen-proof.json).

**Raw phase medians and reproduction**

|Tokens|C1 µs|A1 µs|A2 µs|C2 µs|
|---:|---:|---:|---:|---:|
|1|75.857|73.841|70.160|64.433|
|2|85.473|90.785|84.737|94.801|
|4|100.401|98.849|105.744|100.817|
|8|109.297|109.648|122.113|119.377|
|16|140.450|126.849|124.049|132.769|
|32|140.657|149.762|151.761|151.826|
|64|171.150|161.154|163.105|164.034|
|128|174.610|166.545|174.497|175.538|
|256|175.953|168.305|167.266|176.642|
|512|181.953|176.577|175.857|180.802|
|4096|401.890|404.498|400.676|406.402|
|8192|696.260|669.108|677.204|681.299|
|16384|1281.896|1270.504|1267.499|1264.030|

The [local benchmark wrapper](https://raw.githubusercontent.com/zianglih/flashinfer/2402bcd61a7cc39f650f6b92dd1aa2293ee50518/pr7290/2026-10-29/glm5-helper-4376662a/native_frozen.py) only installs the [frozen per-token tactics](https://raw.githubusercontent.com/zianglih/flashinfer/2402bcd61a7cc39f650f6b92dd1aa2293ee50518/pr7290/2026-10-29/glm5-helper-4376662a/frozen-tactics.json) and records untimed route fingerprints; timed forwards use `benchmarks/bench_cute_dsl_moe_distributed.py` unchanged. For each source arm, point `MEGA_SOURCE`/`PYTHONPATH` at its checkout and `MEGA_FROZEN_TACTICS` at the downloaded JSON, then run:

```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export FLASHINFER_CUDA_ARCH_LIST=10.3a FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_NVFP4_4OVER6=1 FLASHINFER_NVFP4_4OVER6_E4M3_USE_256=1
export FLASHINFER_NVFP4_4OVER6_ERR_MODE=MSE FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH=1
export FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1
export PYTHONWARNINGS='error:CUPTI is not installed:UserWarning'
torchrun --master-addr=127.0.0.1 --master-port=29672 --nproc-per-node=8 \
  native_frozen.py --model glm5 --mode benchmark --parallel-modes ep \
  --num-gpus 8 --variants w4a16_megamoe \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 \
  --timing cupti --cuda-graph --precomputed-routing --no-fused-finalize \
  --warmup 3 --iters 100 --log-timing-samples --megamoe-knobs auto
```

The wrapper replaces `auto` with the same frozen knob dictionary before constructing each layer. All 52 timing records, 416 per-rank tactic records and 416 route fingerprints passed validation; no CUPTI fallback occurred. Benchmark results are a performance check of the shared helper, not a new numerical or sanitizer qualification.
