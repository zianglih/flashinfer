# Fitted transform-group repeat bracket

The prior T64 slowdown did not repeat. Two groups measured 0.232978 and 0.234482 ms around the one-group control's 0.237953 ms. At T4096, two groups measured 0.508210 and 0.511861 ms around 0.513075 ms. Both two-group measurements are faster at both tested shapes. This supports retaining two groups under the preference for no meaningful regression, while one two/one/two bracket is not a statistical confidence interval or a proof of nonregression.

## Exact sources and method

Order: two groups, one group, two groups. Each saved run uses real EP8 on eight B300 GPUs, global tokens64/4096, H7168/I2048/E256/top-k8, BF16 activation/wire and NVFP4 expert weights. Three warmups and 100 fixed CUPTI iterations use CUDA graphs and cold L2. Latency is the median of per-iteration maximum-rank full-forward GPU activity spans. Compilation, tuning, setup and cache flush are excluded; split retains --no-fused-finalize. Numerical parity and codegen are separate evidence.

All 16 recorded repository source hashes per run and the tactic-capture entrypoint were verified. The indicated frozen snapshots matched directly; no current-checkout fallback, source mutation or inferred hash match was needed. The two bracketing runs have identical recorded source hashes. Both implementations retain preferred-five fitting and uniform control-register release; the two-group source uses640 threads/launch96 with epi176,control80,dispatch64,transform80/80. The one-group source uses512 threads/launch128.

| Run | Saved name | Start UTC | Frozen source | Kernel SHA256 |
| --- | --- | --- | --- | --- |
| two_before | tmem-fitted5-transform2-repeat-001 | Tue Sep  8 05:07:45 UTC 2026 | candidates/w4a16_fitted5_transform2/source | 58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7 |
| one_control | tmem-fitted5-transform1-repeat-001 | Tue Sep  8 05:09:21 UTC 2026 | candidates/w4a16_fitted5/source | 0e58304685775bae9b141ad6b7e0e0c9cac5e4441fd4cf5b38553dfcff2aa56a |
| two_after | tmem-fitted5-transform2-repeat-002 | Tue Sep  8 05:10:58 UTC 2026 | candidates/w4a16_fitted5_transform2/source | 58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7 |

Recorded source differences between groups: `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/frontend.py`, `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/kernel.py`. Full per-file hashes, declared sources and remote Git HEAD values are in JSON; remote HEAD is not the executed overlay identity.

Identical explicit knobs: `{"epi_flag_batch": [2, 4], "flag_batch": 4, "group_hint": 512, "load_balance_mode": "atomic_counter", "token_back_mode": "epi_warps"}`. Common benchmark source and per-case reset seeds preserve generated inputs/weights/routes for matching shapes. Each process/rank retunes split independently, so identical inputs do not imply identical tactics.

## Individual comparisons

Change is 100*(two-group Mega / one-group Mega - 1), so negative favors two groups. Split spread is max/min-1 for the indicated two-group run and middle one-group control; it includes tuner/process/order variation and is not an error bar on Mega.

| Two-group run | Global tokens | Two-group ms | One-group ms | Two-group change | One/two | Paired split spread |
| --- | --- | --- | --- | --- | --- | --- |
| two_before | 64 | 0.232978 | 0.237953 | -2.09% | 1.021354 | 0.52% |
| two_after | 64 | 0.234482 | 0.237953 | -1.46% | 1.014803 | 0.66% |
| two_before | 4096 | 0.508210 | 0.513075 | -0.95% | 1.009573 | 1.03% |
| two_after | 4096 | 0.511861 | 0.513075 | -0.24% | 1.002372 | 0.21% |

## Bracket variation

The midpoint is the arithmetic mean of the two bracketing run medians, not a pooled latency median or uncertainty estimate. There are only two two-group runs and one one-group control.

| Global tokens | Two-group midpoint ms | Midpoint change | Two-group spread | All three split-control spread |
| --- | --- | --- | --- | --- |
| 64 | 0.2337300 | -1.77% | 0.65% | 0.66% |
| 4096 | 0.5100355 | -0.59% | 0.72% | 1.24% |

T64's earlier single-run regression is not supported by this bracket. T4096 also shows no observed regression here; the small differences remain descriptive. This bounded repeat does not establish a performance guarantee for untested shapes or serving workloads.

## All 12 raw latency rows

| Run | Variant | Global tokens | EP | Latency ms |
| --- | --- | --- | --- | --- |
| two_before | w4a16 | 64 | 8 | 0.211121 |
| two_before | w4a16_megamoe | 64 | 8 | 0.232978 |
| two_before | w4a16 | 4096 | 8 | 0.545139 |
| two_before | w4a16_megamoe | 4096 | 8 | 0.508210 |
| one_control | w4a16 | 64 | 8 | 0.210033 |
| one_control | w4a16_megamoe | 64 | 8 | 0.237953 |
| one_control | w4a16 | 4096 | 8 | 0.550773 |
| one_control | w4a16_megamoe | 4096 | 8 | 0.513075 |
| two_after | w4a16 | 64 | 8 | 0.211410 |
| two_after | w4a16_megamoe | 64 | 8 | 0.234482 |
| two_after | w4a16 | 4096 | 8 | 0.551924 |
| two_after | w4a16_megamoe | 4096 | 8 | 0.511861 |

## All 48 actual split selections

Each cell lists FC1 M×N×K / FC2 M×N×K in rank0 through rank7 order. Cluster(2,1) and raster_along_m=true accompany every tuple. M128 implies one-CTA instructions and M256 implies two-CTA; the boolean is the raster flag. JSON preserves all original48 records including input shapes, ranks, tuning status and selection counts. These selections were observed, not frozen.

| Run | Global tokens | Rank0 through rank7 FC1/FC2 |
| --- | --- | --- |
| two_before | 64 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| two_before | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| one_control | 64 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| one_control | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| two_after | 64 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| two_after | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/128×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |

## Original commands and reproduction

two_before: declared `Frozen candidates/w4a16_fitted5_transform2/source; kernelSHA256 58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`; remote HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=64,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":\ 512\,\ \"epi_flag_batch\":\ \[2\,\ 4\]\,\ \"load_balance_mode\":\ \"atomic_counter\"\,\ \"flag_batch\":\ 4\,\ \"token_back_mode\":\ \"epi_warps\"\}
```

one_control: declared `Frozen candidates/w4a16_fitted5/source; kernelSHA256 0e58304685775bae9b141ad6b7e0e0c9cac5e4441fd4cf5b38553dfcff2aa56a`; remote HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=64,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":\ 512\,\ \"epi_flag_batch\":\ \[2\,\ 4\]\,\ \"load_balance_mode\":\ \"atomic_counter\"\,\ \"flag_batch\":\ 4\,\ \"token_back_mode\":\ \"epi_warps\"\}
```

two_after: declared `Frozen candidates/w4a16_fitted5_transform2/source; kernelSHA256 58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`; remote HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=64,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":\ 512\,\ \"epi_flag_batch\":\ \[2\,\ 4\]\,\ \"load_balance_mode\":\ \"atomic_counter\"\,\ \"flag_batch\":\ 4\,\ \"token_back_mode\":\ \"epi_warps\"\}
```

Reproduce the CPU analysis: `PYTHONDONTWRITEBYTECODE=1 python3 compare_fitted_transform_repeats.py`.

Outputs: `FITTED_TRANSFORM_GROUP_REPEAT_001.md`, `FITTED_TRANSFORM_GROUP_REPEAT_001.json` and `FITTED_TRANSFORM_GROUP_REPEAT_001.csv`. All12 original printed latencies and all48 original tactic records are retained. No GPU query/launch, remote command, numerical test, active-source edit or existing-helper edit occurred.
