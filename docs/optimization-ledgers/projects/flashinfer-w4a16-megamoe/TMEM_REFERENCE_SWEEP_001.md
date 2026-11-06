# Reference scheduling sweep: tmem-reference-sweep-001

All 25 same-run comparisons regress against split W4A16. Scheduling changes improve MegaMoE itself at 8–4096 tokens, while every nondefault profile increases its one-token latency. These are one sequential set of five profiles, each with 100 timed iterations; they are not five independent repeated samples of one configuration.

## Source and measurement

- Declared tested commit `f952b398418932d52872a7ce13e6adebedbe33e2`. All 16 recorded repository source hashes match that commit and are identical across all five profiles. The remote Git HEAD remained `91bda04c66f7cb851e1ab3b78b9fecea644b9844`; execution used the verified source overlay, not that checkout HEAD.
- Eight B300 GPUs; real EP8; H=7168, I=2048, E=256, top-k=8; **global** source tokens. T1 has one nonempty source rank and seven empty ranks. Split all-gather pads T1 to eight rows; tactic input shapes are preserved in the JSON.
- BF16 activations, packed NVFP4 weights, E4M3 block scales, FP32 per-expert globals; BF16 communication and post-FC2 FP32 scores. Identical generated canonical weights/scales/routes feed both variants. Split uses `--no-fused-finalize` and its existing BF16 rank-local partial reduction; Mega applies external FP32 weighted top-k reduction over BF16 per-route FC2 outputs. Final output rounding differs, so these timing runs omit `--refcheck`; independent numerical/per-route validation is recorded separately.
- Three warmup calls, 100 fixed measured iterations, CUDA graph, cold L2, CUPTI13.2.0. Per iteration, CUPTI takes the earliest kernel start to latest kernel end for each rank, then maximum across ranks; the reported result is the median of those maxima. This is a full-forward GPU wall span, not summed kernel durations or host time. Compilation, tuning, weight preparation, and cache flush are outside that span.
- Five profile processes execute in the recorded order. Split autotuning is rerun independently per process/rank and can choose different tactics; the recorder observes actual returned setup choices without changing them. No frozen tactic replay or repeated-run uncertainty estimate was used.
- Common Mega geometry is M256/N128/K256 with cluster(2,1,1), two-CTA instructions, and dynamic routed-N issuance in 16-token increments. Default resolves `group_hint=None` to SM-count/cluster-size (74 here); load balance is static, flag_batch=1, epi_flag_batch=(1,1), token_back=epi_warps. All four named profiles use group_hint=512, atomic_counter, epi_flag_batch=(2,4), flag_batch4 or8, and the named return mode. This is a combined configuration change from default, not an isolated flag-size experiment.

## Complete raw pairs and derived ratios

All latencies are ms. Derived ratio is split/Mega from printed six-decimal latencies; >1 would favor Mega. The original logged speedup uses unrounded timings and can differ by a few parts per million; both are preserved in the JSON. Last column is the reduction in absolute Mega latency relative to its default run; negative means slower.

| Profile | Global tokens | Split W4A16 ms | Mega W4A16 ms | Split/Mega | Mega change from default |
| --- | --- | --- | --- | --- | --- |
| default | 1 | 0.075968 | 0.106640 | 0.712378 | +0.00% |
| default | 8 | 0.158785 | 0.305458 | 0.519826 | +0.00% |
| default | 32 | 0.196226 | 0.401124 | 0.489190 | +0.00% |
| default | 128 | 0.235602 | 0.469076 | 0.502268 | +0.00% |
| default | 4096 | 0.552118 | 0.715687 | 0.771452 | +0.00% |
| flag4-epi | 1 | 0.076496 | 0.110176 | 0.694307 | -3.32% |
| flag4-epi | 8 | 0.149713 | 0.226114 | 0.662113 | +25.98% |
| flag4-epi | 32 | 0.205713 | 0.298051 | 0.690194 | +25.70% |
| flag4-epi | 128 | 0.233314 | 0.346707 | 0.672943 | +26.09% |
| flag4-epi | 4096 | 0.555861 | 0.649222 | 0.856196 | +9.29% |
| flag4-reuse | 1 | 0.072976 | 0.123665 | 0.590110 | -15.96% |
| flag4-reuse | 8 | 0.151089 | 0.232690 | 0.649315 | +23.82% |
| flag4-reuse | 32 | 0.199074 | 0.316194 | 0.629594 | +21.17% |
| flag4-reuse | 128 | 0.232658 | 0.370691 | 0.627633 | +20.97% |
| flag4-reuse | 4096 | 0.552434 | 0.672419 | 0.821562 | +6.05% |
| flag8-epi | 1 | 0.096496 | 0.117216 | 0.823232 | -9.92% |
| flag8-epi | 8 | 0.159618 | 0.227074 | 0.702934 | +25.66% |
| flag8-epi | 32 | 0.199121 | 0.297889 | 0.668440 | +25.74% |
| flag8-epi | 128 | 0.216770 | 0.345442 | 0.627515 | +26.36% |
| flag8-epi | 4096 | 0.552679 | 0.674884 | 0.818924 | +5.70% |
| flag8-reuse | 1 | 0.083761 | 0.122609 | 0.683155 | -14.97% |
| flag8-reuse | 8 | 0.160273 | 0.224450 | 0.714070 | +26.52% |
| flag8-reuse | 32 | 0.201026 | 0.314787 | 0.638610 | +21.52% |
| flag8-reuse | 128 | 0.225073 | 0.369027 | 0.609909 | +21.33% |
| flag8-reuse | 4096 | 0.544019 | 0.701848 | 0.775124 | +1.93% |

## Observed split-control variation across profiles

These ranges include independent tuner choices and process/order variation. They are observed cross-profile ranges, not error bars or confidence intervals.

| Global tokens | Min split ms | Median split ms | Max split ms | Max/min − 1 |
| --- | --- | --- | --- | --- |
| 1 | 0.072976 | 0.076496 | 0.096496 | 32.23% |
| 8 | 0.149713 | 0.158785 | 0.160273 | 7.05% |
| 32 | 0.196226 | 0.199121 | 0.205713 | 4.83% |
| 128 | 0.216770 | 0.232658 | 0.235602 | 8.69% |
| 4096 | 0.544019 | 0.552434 | 0.555861 | 2.18% |

## Best observed Mega latency per shape

This is retrospective selection over the five measurements, not a validated shape selector. The closest flag4/flag8 differences at T32 and T128 are small compared with observed split variation; do not assign significance without repeats.

| Global tokens | Profile | Mega ms | Paired split ms | Mega latency over paired split | Mega reduction from default |
| --- | --- | --- | --- | --- | --- |
| 1 | default | 0.106640 | 0.075968 | 40.37% | 0.00% |
| 8 | flag8-reuse | 0.224450 | 0.160273 | 40.04% | 26.52% |
| 32 | flag8-epi | 0.297889 | 0.199121 | 49.60% | 25.74% |
| 128 | flag8-epi | 0.345442 | 0.216770 | 59.36% | 26.36% |
| 4096 | flag4-epi | 0.649222 | 0.555861 | 16.80% | 9.29% |

## Actual split tactic choices

Each cell lists FC1 M×N×K / FC2 M×N×K in rank0…rank7 order. Every tuple also has cluster_shape_mn=(2,1) and raster_along_m=true. The boolean is **not** the two-CTA instruction flag; local W4A16 derives that flag from M==256. M128 choices use one-CTA instructions even with cluster(2,1). All 200 records have one setup selection call; full input shapes and original tuple values are in the JSON.

| Profile | Global tokens | Rank0…rank7 actual FC1/FC2 tactics |
| --- | --- | --- |
| default | 1 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| default | 8 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| default | 32 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256 |
| default | 128 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 256×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| default | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| flag4-epi | 1 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| flag4-epi | 8 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| flag4-epi | 32 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256 |
| flag4-epi | 128 | 128×16×256/128×16×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 256×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| flag4-epi | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| flag4-reuse | 1 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| flag4-reuse | 8 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| flag4-reuse | 32 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/256×16×256; 128×16×256/128×16×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/256×16×256 |
| flag4-reuse | 128 | 128×16×256/256×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| flag4-reuse | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| flag8-epi | 1 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256 |
| flag8-epi | 8 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256 |
| flag8-epi | 32 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/256×16×256; 128×8×256/128×8×256; 256×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| flag8-epi | 128 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256 |
| flag8-epi | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| flag8-reuse | 1 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| flag8-reuse | 8 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| flag8-reuse | 32 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 256×16×256/128×16×256; 128×16×256/256×16×256; 128×8×256/128×8×256 |
| flag8-reuse | 128 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| flag8-reuse | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |

At T4096, all five profiles choose M256/N128/K256 for both GEMMs on six ranks and M256/N192/K256 for both GEMMs on two ranks. Small-token selections vary both by rank and process. Historical pre-recorder baseline choices remain unavailable; these records describe only this fresh run.

## Reproduction and artifacts

```bash
python3 summarize_reference_sweep.py
```

- Launch recipe: `run_reference_schedule_sweep.sh`, invoking `run_benchmark_ep8.sh` and `capture_benchmark_tactics.py`; complete shell commands and source hashes are in each `.provenance.log`.
- Complete original raw 50 rows: `logs/tmem-reference-sweep-001.raw.csv`.
- All raw/derived values, source verification, 200 rank/shape tactic records, and hashes of 50 input artifacts: `logs/tmem-reference-sweep-001.comparison.json`.
- Original ten log/provenance files and forty tactic files remain under `logs/`.
- The observed scheduling gains do not establish a win over split W4A16 or serving throughput. Profiler samples and aggregate counters are separate mechanism evidence, and profiler kernel durations are not substituted for these timings.
