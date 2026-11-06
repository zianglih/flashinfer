# Nsight Compute: grouped 4over6 BF16 specialization

- Date: 2026-08-24
- Hardware: one NVIDIA B300 SXM6 AC, physical GPU 5 (logical `cuda:0` under `CUDA_VISIBLE_DEVICES=5`), 148 SMs, CC 10.3
- Image: `radixark/miles:dev-202608230022`
- Nsight Compute: 2025.3.1.0, build 36398880
- Workload: one grouped input `[8, 4096, 6144]`, BF16, 4over6 MAE, E4M3 max 448, current FP16-error contract
- Target source: commit `2f84fe497a737af174379fed8b2af865647ad851`, kernel-file SHA-256 `988e18bb6ebf192688e0f413802864b8ce72a9ef24782ff84d34f459d6a16e50`
- Candidate source: the target source with only `_4OVER6_MIN_BLOCKS_PER_SM = 8` changed to `10`, kernel-file SHA-256 `aa9c9a19556f9c952446fa6a1b251e027853c527e8324dacb5022f333d2d50e3`
- Collection: one filtered QDQ launch, 22 replay passes, identical sections for both variants. Compilation was warmed in an unprofiled process first.

## Result

| Metric | `min_blocks=8` baseline | `min_blocks=10` candidate |
|---|---:|---:|
| Launch dimensions | `(8, 1184, 1) x (128, 1, 1)` | `(8, 1184, 1) x (128, 1, 1)` |
| Grid blocks | 9,472 | 9,472 |
| Registers/thread | 64 | 48 |
| Register-limited resident CTAs/SM | 8 | 10 |
| Theoretical occupancy | 50.00% | 62.50% |
| Achieved occupancy | 46.49% | 56.48% |
| Achieved active warps/SM | 29.75 | 36.15 |
| Active warps/scheduler | 7.43 | 9.06 |
| Eligible warps/scheduler | 3.74 | 4.58 |
| One or more eligible | 90.05% | 86.91% |
| Issued warp/scheduler | 0.90 | 0.87 |
| Executed IPC, active | 3.59 | 3.46 |
| Issue slots busy | 87.31% | 84.33% |
| Compute throughput | 87.31% | 84.33% |
| DRAM throughput | 32.61% | 31.37% |
| Instructions executed | 171,711,488 | 172,142,592 |
| Local-memory spilling requests | 0 | 0 |
| L2 theoretical local sectors | 0 | 0 |
| NCU-replayed launch duration | 304.90 us | 316.77 us |

The extra occupancy does not pay for its forced register reduction. It raises active and eligible warp counts, but scheduler issue efficiency falls: issue-slot utilization drops 2.98 percentage points and active IPC drops from 3.59 to 3.46. There are no local-memory spills in either variant and the instruction count rises only 0.25%. The likely mechanism is reduced per-warp instruction-level parallelism and scheduling freedom under the 48-register cap, not spill traffic. This is consistent with the benchmark regression and with the increased math-pipe and dispatch stall values below.

The existing source comment saying the largest 4over6 specialization uses 56 registers/thread is stale for this target specialization: Nsight Compute reports 64 registers/thread at the retained `min_blocks=8` setting.

## Warp stalls

Values are average warp cycles per issued instruction from Nsight Compute's Warp State Statistics. `Not Selected` mainly reflects eligible-warps competing for an issue slot; the latency-bearing leaders are long scoreboard and math-pipe throttle.

| Stall reason | `min_blocks=8` | `min_blocks=10` |
|---|---:|---:|
| Not selected | 3.15 | 4.26 |
| Long scoreboard | 1.70 | 1.68 |
| Math pipe throttle | 1.37 | 2.07 |
| Wait | 0.59 | 0.67 |
| Dispatch stall | 0.19 | 0.49 |
| Branch resolving | 0.10 | 0.10 |
| No instruction | 0.08 | 0.06 |
| Short scoreboard | 0.06 | 0.08 |
| Total warp cycles/issued instruction | 8.26 | 10.42 |

Among sampled not-issued cycles, the baseline's leaders were long scoreboard (245 samples), math-pipe throttle (212), and wait (171). For `min_blocks=10`, they were math-pipe throttle (284), long scoreboard (230), and wait (126).

## Commands

Warm compilation:

```bash
/usr/local/bin/h ssh nvfp4-qdq-cute -c c2 -n infra -- \
  env CUDA_VISIBLE_DEVICES=5 PYTHONPATH=/root/Megatron-LM-ncu-2f84 \
  python /root/ncu_2f84_4over6_profile.py

/usr/local/bin/h ssh nvfp4-qdq-cute -c c2 -n infra -- \
  env CUDA_VISIBLE_DEVICES=5 PYTHONPATH=/root/Megatron-LM-ncu-minblocks10 \
  python /root/ncu_2f84_4over6_profile.py
```

Profile command, with `PYTHONPATH` and output stem changed between variants:

```bash
/usr/local/bin/h ssh nvfp4-qdq-cute -c c2 -n infra -- \
  env CUDA_VISIBLE_DEVICES=5 PYTHONPATH=/root/Megatron-LM-ncu-2f84 \
  ncu --force-overwrite --target-processes all \
  --kernel-name 'regex:.*fused_nvfp4_qdq.*' --launch-count 1 \
  --section LaunchStats --section Occupancy --section WarpStateStats \
  --section MemoryWorkloadAnalysis --section SchedulerStats \
  --section ComputeWorkloadAnalysis --section InstructionStats \
  --section SourceCounters --section SpeedOfLight \
  -o /root/nvfp4_qdq_2f84fe497_g8_4096x6144_4over6_mae_e448_fp16err_bf16_gpu5 \
  python /root/ncu_2f84_4over6_profile.py
```

## Reports

- Baseline remote: `/root/nvfp4_qdq_2f84fe497_g8_4096x6144_4over6_mae_e448_fp16err_bf16_gpu5.ncu-rep`
- Candidate remote: `/root/nvfp4_qdq_minblocks10_g8_4096x6144_4over6_mae_e448_fp16err_bf16_gpu5.ncu-rep`
- Baseline local SHA-256: `503bf73f18fae35dece038c468ffd53c090288bfd7c2ee0a4d0a9b0d85e9dc35`
- Candidate local SHA-256: `ef1be1eb5e64f87b665760ea2f0cf4f1bf76cf085c0f7e6ced799de4fb7e26fc`

NCU launch durations are diagnostic values from replay collection, not replacements for the full benchmark's same-run medians.
