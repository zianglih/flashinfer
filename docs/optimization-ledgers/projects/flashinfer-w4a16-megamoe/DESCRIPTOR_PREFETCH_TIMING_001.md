# Descriptor-prefetch timing comparison

The fresh adjacent comparison does not support promoting descriptor prefetch. Prefetch is 19.40% slower at T1, 4.35% slower at T8 and 2.54% slower at T64, with 0.69% lower latency at T4096. Source hashes isolate the kernel change, but these remain one prefetch process and one subsequent control process with independently tuned split choices. The small T4096 improvement is not stable across the earlier repeated controls, where prefetch lies slightly above their range.

## Sources and measurement

The artifact-only snapshot is `candidates/w4a16_descriptor_prefetch_timing/source`: a copy of `candidates/w4a16_fitted5_transform2/source` with only the kernel replaced by `candidates/w4a16_cache_hints/measured-prefetch-kernel.py`. Its manifest records every saved file hash. The prefetch kernel SHA256 is `1b827889d20de5c2d770d1f9b98ed0de79d78abc2d6b71cf043680ed6b2eeedc`; control kernel SHA256 is `58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`.

All 16 recorded repository source hashes per run and each tactic-capture entrypoint hash pass the existing load_run verifier. All four controls have identical recorded source hashes; the only recorded source change for prefetch is the W4A16 kernel. The recorded overlay hashes, rather than remote Git HEAD, define execution. No active repository or earlier candidate was modified.

All runs use real EP8 on eight B300 GPUs, H7168/I2048/E256/top-k8, global source tokens, BF16 activations/wire and NVFP4 expert weights. Three warmups precede 100 fixed CUPTI iterations with CUDA graphs and cold L2. The reported median aggregates per-iteration maximum-rank full-forward GPU activity spans; setup, compilation, tuning and cache flush are excluded. Split retains --no-fused-finalize. Numerical parity and codegen/resources are separate evidence.

Identical explicit Mega knobs: `{"epi_flag_batch": [2, 4], "flag_batch": 4, "group_hint": 512, "load_balance_mode": "atomic_counter", "token_back_mode": "epi_warps"}`. Shared benchmark source preserves per-case seeded inputs for matching shapes, but split retunes per process/rank. Actual tactics are recorded, not frozen.

| Label | Saved run | Start UTC | Start relative to prefetch |
| --- | --- | --- | --- |
| full13_control | tmem-fitted5-transform2-paired-001 | Tue Sep  8 04:57:16 UTC 2026 | 27 m 20 s before |
| repeat_control_1 | tmem-fitted5-transform2-repeat-001 | Tue Sep  8 05:07:45 UTC 2026 | 16 m 51 s before |
| repeat_control_2 | tmem-fitted5-transform2-repeat-002 | Tue Sep  8 05:10:58 UTC 2026 | 13 m 38 s before |
| prefetch | tmem-descriptor-prefetch-paired-001 | Tue Sep  8 05:24:36 UTC 2026 | candidate |
| adjacent_control | tmem-descriptor-control-paired-001 | Tue Sep  8 05:34:53 UTC 2026 | 10 m 17 s after |

The primary order is prefetch then fresh adjacent control, whose process start is 10 m 17 s later. It covers all four candidate shapes. The older full13 and two T64/T4096 repeat controls remain historical context. The repeats precede prefetch and do not bracket it. No confidence interval or statistical nonregression conclusion follows from this sampling.

## Primary adjacent prefetch/control result

Change is 100 * (prefetch/control − 1), so positive means slower. Split spread is max/min − 1 and captures independent tuner/process/order variation; it is not an error bar on Mega latency.

| Global tokens | Prefetch Mega ms | Adjacent control Mega ms | Prefetch change | Prefetch split ms | Control split ms | Split spread |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.109889 | 0.092033 | +19.40% | 0.080913 | 0.068736 | 17.72% |
| 8 | 0.167810 | 0.160818 | +4.35% | 0.147281 | 0.151345 | 2.76% |
| 64 | 0.233090 | 0.227314 | +2.54% | 0.220498 | 0.210402 | 4.80% |
| 4096 | 0.512468 | 0.516021 | -0.69% | 0.551587 | 0.550629 | 0.17% |

| Global tokens | Ranks with different actual split tactics | Changed ranks out of 8 |
| --- | --- | --- |
| 1 | 0, 1, 4 | 3 |
| 8 | 0, 1, 4 | 3 |
| 64 | 4, 6 | 2 |
| 4096 | none | 0 |

T1 has 17.72% split spread and three changed rank tactics, so the 19.40% Mega slowdown magnitude is not a robust isolated estimate. T8 has 2.76% split spread; T64 has 4.80%. At T4096 every rank selected the same split tactic in both runs and split spread is 0.17%, while prefetch is 0.69% faster. This is the narrow favorable observation; one pair plus the historical repeat range is insufficient to claim a stable performance gain or justify retaining the added prefetch.

## Historical T64/T4096 repeated controls

Changes use 100 * (prefetch/control − 1), so positive means slower. The control ranges contain two process medians, not uncertainty intervals.

| Global tokens | Repeated control range ms | Prefetch ms | Vs fastest control | Vs slowest control | Inside range | All-three split spread |
| --- | --- | --- | --- | --- | --- | --- |
| 64 | 0.232978–0.234482 | 0.233090 | +0.05% | -0.59% | True | 4.44% |
| 4096 | 0.508210–0.511861 | 0.512468 | +0.84% | +0.12% | False | 1.24% |

The older full13 T64 control was 0.252721 ms, so using that observation alone suggests a gain. The later repeated control range shows that the apparent gain is not specific evidence for prefetch. At T4096, prefetch is 0.12–0.84% slower than the repeated controls; this small range is descriptive and supplies no positive gain signal.

## All matching-shape comparisons

Split spread is max/min − 1 for the indicated control and prefetch process. It includes independent tuning, process and order variation; it is not an error bar on Mega latency.

| Control | Global tokens | Control Mega ms | Prefetch Mega ms | Prefetch change | Split-control spread |
| --- | --- | --- | --- | --- | --- |
| adjacent_control | 1 | 0.092033 | 0.109889 | +19.40% | 17.72% |
| adjacent_control | 8 | 0.160818 | 0.167810 | +4.35% | 2.76% |
| adjacent_control | 64 | 0.227314 | 0.233090 | +2.54% | 4.80% |
| adjacent_control | 4096 | 0.516021 | 0.512468 | -0.69% | 0.17% |
| full13_control | 1 | 0.098720 | 0.109889 | +11.31% | 1.42% |
| full13_control | 8 | 0.159777 | 0.167810 | +5.03% | 5.24% |
| full13_control | 64 | 0.252721 | 0.233090 | -7.77% | 0.55% |
| full13_control | 4096 | 0.506356 | 0.512468 | +1.21% | 1.29% |
| repeat_control_1 | 64 | 0.232978 | 0.233090 | +0.05% | 4.44% |
| repeat_control_1 | 4096 | 0.508210 | 0.512468 | +0.84% | 1.18% |
| repeat_control_2 | 64 | 0.234482 | 0.233090 | -0.59% | 4.30% |
| repeat_control_2 | 4096 | 0.511861 | 0.512468 | +0.12% | 0.06% |

## Complete raw data

All 8 prefetch rows, 8 fresh adjacent-control rows and 34 historical control rows are included below and in CSV. The extra full13 shapes are retained without claiming a prefetch comparison. JSON preserves all 200 original tactic records: 32 prefetch, 32 adjacent control, 104 full13 and 16 for each repeat.

| Run | Variant | Global tokens | EP | Latency ms |
| --- | --- | --- | --- | --- |
| full13_control | w4a16 | 1 | 8 | 0.082065 |
| full13_control | w4a16_megamoe | 1 | 8 | 0.098720 |
| full13_control | w4a16 | 2 | 8 | 0.116321 |
| full13_control | w4a16_megamoe | 2 | 8 | 0.113489 |
| full13_control | w4a16 | 4 | 8 | 0.143713 |
| full13_control | w4a16_megamoe | 4 | 8 | 0.134864 |
| full13_control | w4a16 | 8 | 8 | 0.154993 |
| full13_control | w4a16_megamoe | 8 | 8 | 0.159777 |
| full13_control | w4a16 | 16 | 8 | 0.179522 |
| full13_control | w4a16_megamoe | 16 | 8 | 0.181090 |
| full13_control | w4a16 | 32 | 8 | 0.204194 |
| full13_control | w4a16_megamoe | 32 | 8 | 0.210721 |
| full13_control | w4a16 | 64 | 8 | 0.221715 |
| full13_control | w4a16_megamoe | 64 | 8 | 0.252721 |
| full13_control | w4a16 | 128 | 8 | 0.236673 |
| full13_control | w4a16_megamoe | 128 | 8 | 0.242498 |
| full13_control | w4a16 | 256 | 8 | 0.242978 |
| full13_control | w4a16_megamoe | 256 | 8 | 0.246594 |
| full13_control | w4a16 | 512 | 8 | 0.240290 |
| full13_control | w4a16_megamoe | 512 | 8 | 0.255026 |
| full13_control | w4a16 | 1024 | 8 | 0.262257 |
| full13_control | w4a16_megamoe | 1024 | 8 | 0.265906 |
| full13_control | w4a16 | 2048 | 8 | 0.350451 |
| full13_control | w4a16_megamoe | 2048 | 8 | 0.346882 |
| full13_control | w4a16 | 4096 | 8 | 0.544547 |
| full13_control | w4a16_megamoe | 4096 | 8 | 0.506356 |
| repeat_control_1 | w4a16 | 64 | 8 | 0.211121 |
| repeat_control_1 | w4a16_megamoe | 64 | 8 | 0.232978 |
| repeat_control_1 | w4a16 | 4096 | 8 | 0.545139 |
| repeat_control_1 | w4a16_megamoe | 4096 | 8 | 0.508210 |
| repeat_control_2 | w4a16 | 64 | 8 | 0.211410 |
| repeat_control_2 | w4a16_megamoe | 64 | 8 | 0.234482 |
| repeat_control_2 | w4a16 | 4096 | 8 | 0.551924 |
| repeat_control_2 | w4a16_megamoe | 4096 | 8 | 0.511861 |
| prefetch | w4a16 | 1 | 8 | 0.080913 |
| prefetch | w4a16_megamoe | 1 | 8 | 0.109889 |
| prefetch | w4a16 | 8 | 8 | 0.147281 |
| prefetch | w4a16_megamoe | 8 | 8 | 0.167810 |
| prefetch | w4a16 | 64 | 8 | 0.220498 |
| prefetch | w4a16_megamoe | 64 | 8 | 0.233090 |
| prefetch | w4a16 | 4096 | 8 | 0.551587 |
| prefetch | w4a16_megamoe | 4096 | 8 | 0.512468 |
| adjacent_control | w4a16 | 1 | 8 | 0.068736 |
| adjacent_control | w4a16_megamoe | 1 | 8 | 0.092033 |
| adjacent_control | w4a16 | 8 | 8 | 0.151345 |
| adjacent_control | w4a16_megamoe | 8 | 8 | 0.160818 |
| adjacent_control | w4a16 | 64 | 8 | 0.210402 |
| adjacent_control | w4a16_megamoe | 64 | 8 | 0.227314 |
| adjacent_control | w4a16 | 4096 | 8 | 0.550629 |
| adjacent_control | w4a16_megamoe | 4096 | 8 | 0.516021 |

## Actual split tactics

Every cell lists FC1 M×N×K / FC2 M×N×K for rank 0 through rank 7. All tuples have cluster (2, 1), raster_along_m=true and one setup selection call. M128 implies one-CTA instructions; M256 implies two-CTA. JSON retains every original record, including input shapes. No fixed tactic replay is claimed.

| Run | Global tokens | Rank 0 through rank 7 FC1/FC2 |
| --- | --- | --- |
| full13_control | 1 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| full13_control | 2 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| full13_control | 4 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| full13_control | 8 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| full13_control | 16 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| full13_control | 32 | 128×16×256/256×16×256; 128×16×256/256×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/256×16×256; 128×8×256/128×8×256; 256×16×256/128×16×256 |
| full13_control | 64 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 256×16×256/256×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| full13_control | 128 | 128×16×256/128×16×256; 128×16×256/256×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| full13_control | 256 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×32×256/256×32×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| full13_control | 512 | 128×32×256/256×32×256; 128×32×256/256×32×256; 128×32×256/128×32×256; 128×32×256/128×32×256; 128×32×256/128×32×256; 128×32×256/256×32×256; 128×32×256/256×32×256; 128×32×256/256×32×256 |
| full13_control | 1024 | 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256 |
| full13_control | 2048 | 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×128×256/256×128×256 |
| full13_control | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| repeat_control_1 | 64 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| repeat_control_1 | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| repeat_control_2 | 64 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| repeat_control_2 | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/128×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| prefetch | 1 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| prefetch | 8 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| prefetch | 64 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/256×16×256; 128×16×256/128×16×256 |
| prefetch | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| adjacent_control | 1 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| adjacent_control | 8 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| adjacent_control | 64 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 256×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| adjacent_control | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |

## Original commands and reproduction

full13_control: declared `c7713ba1 + preferred5 fitter/default/corrected2WG; kernel SHA256 58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`; remote HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=1,2,4,8,16,32,64,128,256,512,1024,2048,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":\ 512\,\ \"epi_flag_batch\":\ \[2\,\ 4\]\,\ \"load_balance_mode\":\ \"atomic_counter\"\,\ \"flag_batch\":\ 4\,\ \"token_back_mode\":\ \"epi_warps\"\}
```

repeat_control_1: declared `Frozen candidates/w4a16_fitted5_transform2/source; kernelSHA256 58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`; remote HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=64,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":\ 512\,\ \"epi_flag_batch\":\ \[2\,\ 4\]\,\ \"load_balance_mode\":\ \"atomic_counter\"\,\ \"flag_batch\":\ 4\,\ \"token_back_mode\":\ \"epi_warps\"\}
```

repeat_control_2: declared `Frozen candidates/w4a16_fitted5_transform2/source; kernelSHA256 58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`; remote HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=64,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":\ 512\,\ \"epi_flag_batch\":\ \[2\,\ 4\]\,\ \"load_balance_mode\":\ \"atomic_counter\"\,\ \"flag_batch\":\ 4\,\ \"token_back_mode\":\ \"epi_warps\"\}
```

prefetch: declared `fe4f8132 + descriptor prefetch; kernel SHA256 1b827889d20de5c2d770d1f9b98ed0de79d78abc2d6b71cf043680ed6b2eeedc`; remote HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=1,8,64,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":\ 512\,\ \"epi_flag_batch\":\ \[2\,\ 4\]\,\ \"load_balance_mode\":\ \"atomic_counter\"\,\ \"flag_batch\":\ 4\,\ \"token_back_mode\":\ \"epi_warps\"\}
```

adjacent_control: declared `fe4f8132439df1b812f77279e7d033a5128f1ed4`; remote HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=1,8,64,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":\ 512\,\ \"epi_flag_batch\":\ \[2\,\ 4\]\,\ \"load_balance_mode\":\ \"atomic_counter\"\,\ \"flag_batch\":\ 4\,\ \"token_back_mode\":\ \"epi_warps\"\}
```

Reproduce this CPU-only analysis: `PYTHONDONTWRITEBYTECODE=1 python3 compare_descriptor_prefetch.py`.

Outputs: `DESCRIPTOR_PREFETCH_TIMING_001.md`, `DESCRIPTOR_PREFETCH_TIMING_001.json` and `DESCRIPTOR_PREFETCH_TIMING_001.csv`. The recorded snapshot manifest is under `candidates/w4a16_descriptor_prefetch_timing/`. No GPU query/launch, remote operation, source edit or existing-helper edit was performed.
