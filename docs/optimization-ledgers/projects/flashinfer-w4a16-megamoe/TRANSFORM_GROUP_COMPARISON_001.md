# Saved transform-group comparison

The corrected historical two-group run is 5.12% faster at T8 and 5.03% faster at T128 than the newer preferred-five, uniform-control one-group run. T32 is 1.40% faster; T4096 is 0.71% slower (0.512611 versus 0.508981 ms), alongside 1.24% split-control spread. Treat T4096 as neutral pending repeated contextual evidence, not as a meaningful regression or a reason to reject two groups. The requested preference is two groups if there is no meaningful regression; the contextual two-group full13 run is the decisive next comparison and is excluded here.

## Provenance and scope

All three saved runs use eight B300 SXM6 GPUs, real EP8, H7168/I2048/E256/top-k8, BF16 activations/wire, NVFP4 weights and post-FC2 FP32 routing weights. Source token counts are global; T1 has one nonempty rank and seven empty ranks. The recorded driver is 590.48.01, torch CUDA13.2 and CUPTI13.2.0. These per-run provenance files do not record an exact image tag or the PyTorch package version; none is inferred here.

Three warmups precede 100 fixed CUPTI iterations with CUDA graphs and cold L2. The statistic is the median of per-iteration maximum-rank full-forward GPU activity spans; setup, compilation, tuning and cache flush are excluded. Split retains --no-fused-finalize and its existing BF16 rank-local partial reduction; these timings do not establish numerical parity with Mega's external weighted reduction. No GPU or remote operation was performed for this report.

All 16 recorded repository source hashes per run were verified using compare_raw_depth.load_run, plus the recorded tactic-capture entrypoint hash. The remote Git HEAD is not the executed source identity; the hashes and snapshots below define the overlays.

| Label | Saved run | Start UTC | Source behavior | Kernel SHA256 |
| --- | --- | --- | --- | --- |
| old_one_group | tmem-raw5-paired-001 | Tue Sep  8 04:01:26 UTC 2026 | Raw5 one group; separate control-release sites; launch512/128 | 3bf69b9526757dceb6db680429d1a9e6590365135f433d840a55eb804d921940 |
| corrected_two_groups | tmem-raw5-transform2-paired-002 | Tue Sep  8 04:18:44 UTC 2026 | Raw5 two groups; uniform control80 and transform80/80; launch640/96 | 8ca2c45217c9d07680adf3fb4f670eb8ec3acbd04be84c779253513be8f0b9d6 |
| fitted_one_group | tmem-fitted5-paired-001 | Tue Sep  8 04:40:51 UTC 2026 | Preferred5 fitter one group; uniform control80; launch512/128 | 0e58304685775bae9b141ad6b7e0e0c9cac5e4441fd4cf5b38553dfcff2aa56a |

All runs have identical explicit Mega knobs: `{"epi_flag_batch": [2, 4], "flag_batch": 4, "group_hint": 512, "load_balance_mode": "atomic_counter", "token_back_mode": "epi_warps"}`. The newer source's default profile was therefore not an additional timing variable in these commands. The old one-group run lacks the uniform control release; the newer fitted one-group is the better current control, although the historical corrected two-group still has fixed raw5 and older host/epilogue source. Recorded source differences are retained in JSON.

The common benchmark source has the same verified hash in all three runs. It constructs fresh generators per case: weights1000+rank, activations42+rank, routing137 and bias911. Consequently common shapes use the same generated inputs/weights/routes even though the newer sweep visits additional token counts. Split setup still retunes independently per process/rank; input equality does not freeze tactic choices.

## Common-shape comparisons

Change is 100*(two-group Mega / reference Mega - 1); negative favors two groups. Split spread is 100*(max paired split / min paired split - 1). It includes process/order/tuner variation and is not a confidence interval or an error bar on Mega. Each source has only one process run.

| Reference | Global tokens | Reference Mega ms | Two-group Mega ms | Two-group change | Reference/two-group | Split control spread |
| --- | --- | --- | --- | --- | --- | --- |
| old_one_group | 1 | 0.081969 | 0.075760 | -7.57% | 1.081956 | 22.64% |
| old_one_group | 8 | 0.163377 | 0.162097 | -0.78% | 1.007897 | 1.57% |
| old_one_group | 32 | 0.214993 | 0.210257 | -2.20% | 1.022525 | 2.67% |
| old_one_group | 128 | 0.235745 | 0.239906 | +1.77% | 0.982656 | 1.64% |
| old_one_group | 4096 | 0.515732 | 0.512611 | -0.61% | 1.006088 | 1.25% |
| fitted_one_group | 1 | 0.100464 | 0.075760 | -24.59% | 1.326082 | 16.51% |
| fitted_one_group | 8 | 0.170849 | 0.162097 | -5.12% | 1.053992 | 1.47% |
| fitted_one_group | 32 | 0.213249 | 0.210257 | -1.40% | 1.014230 | 2.60% |
| fitted_one_group | 128 | 0.252625 | 0.239906 | -5.03% | 1.053017 | 0.42% |
| fitted_one_group | 4096 | 0.508981 | 0.512611 | +0.71% | 0.992919 | 1.24% |

T1's apparent 24.59% gain over fitted one-group accompanies 16.51% paired split spread (22.64% across all three controls), so its magnitude is not robust. T8/T128 are encouraging, T32 is within its control spread, and T4096 is neutral. No aggregate winner or statistical significance is inferred from these single runs.

## Complete raw latency rows

All 46 original printed latency rows are retained without rounding changes in the CSV and below. JSON also records all 23 same-run split/Mega ratios. The 13-shape fitted one-group run has no historical two-group partner outside T1/8/32/128/4096.

| Run | Variant | Global tokens | EP | Latency ms |
| --- | --- | --- | --- | --- |
| old_one_group | w4a16 | 1 | 8 | 0.085473 |
| old_one_group | w4a16_megamoe | 1 | 8 | 0.081969 |
| old_one_group | w4a16 | 8 | 8 | 0.161122 |
| old_one_group | w4a16_megamoe | 8 | 8 | 0.163377 |
| old_one_group | w4a16 | 32 | 8 | 0.202977 |
| old_one_group | w4a16_megamoe | 32 | 8 | 0.214993 |
| old_one_group | w4a16 | 128 | 8 | 0.230752 |
| old_one_group | w4a16_megamoe | 128 | 8 | 0.235745 |
| old_one_group | w4a16 | 4096 | 8 | 0.554293 |
| old_one_group | w4a16_megamoe | 4096 | 8 | 0.515732 |
| corrected_two_groups | w4a16 | 1 | 8 | 0.069696 |
| corrected_two_groups | w4a16_megamoe | 1 | 8 | 0.075760 |
| corrected_two_groups | w4a16 | 8 | 8 | 0.158625 |
| corrected_two_groups | w4a16_megamoe | 8 | 8 | 0.162097 |
| corrected_two_groups | w4a16 | 32 | 8 | 0.197697 |
| corrected_two_groups | w4a16_megamoe | 32 | 8 | 0.210257 |
| corrected_two_groups | w4a16 | 128 | 8 | 0.234545 |
| corrected_two_groups | w4a16_megamoe | 128 | 8 | 0.239906 |
| corrected_two_groups | w4a16 | 4096 | 8 | 0.561222 |
| corrected_two_groups | w4a16_megamoe | 4096 | 8 | 0.512611 |
| fitted_one_group | w4a16 | 1 | 8 | 0.081200 |
| fitted_one_group | w4a16_megamoe | 1 | 8 | 0.100464 |
| fitted_one_group | w4a16 | 2 | 8 | 0.101633 |
| fitted_one_group | w4a16_megamoe | 2 | 8 | 0.122385 |
| fitted_one_group | w4a16 | 4 | 8 | 0.137296 |
| fitted_one_group | w4a16_megamoe | 4 | 8 | 0.138289 |
| fitted_one_group | w4a16 | 8 | 8 | 0.156322 |
| fitted_one_group | w4a16_megamoe | 8 | 8 | 0.170849 |
| fitted_one_group | w4a16 | 16 | 8 | 0.169010 |
| fitted_one_group | w4a16_megamoe | 16 | 8 | 0.183089 |
| fitted_one_group | w4a16 | 32 | 8 | 0.202833 |
| fitted_one_group | w4a16_megamoe | 32 | 8 | 0.213249 |
| fitted_one_group | w4a16 | 64 | 8 | 0.216993 |
| fitted_one_group | w4a16_megamoe | 64 | 8 | 0.238513 |
| fitted_one_group | w4a16 | 128 | 8 | 0.233571 |
| fitted_one_group | w4a16_megamoe | 128 | 8 | 0.252625 |
| fitted_one_group | w4a16 | 256 | 8 | 0.242513 |
| fitted_one_group | w4a16_megamoe | 256 | 8 | 0.254866 |
| fitted_one_group | w4a16 | 512 | 8 | 0.238993 |
| fitted_one_group | w4a16_megamoe | 512 | 8 | 0.259026 |
| fitted_one_group | w4a16 | 1024 | 8 | 0.260914 |
| fitted_one_group | w4a16_megamoe | 1024 | 8 | 0.274498 |
| fitted_one_group | w4a16 | 2048 | 8 | 0.350498 |
| fitted_one_group | w4a16_megamoe | 2048 | 8 | 0.347442 |
| fitted_one_group | w4a16 | 4096 | 8 | 0.554325 |
| fitted_one_group | w4a16_megamoe | 4096 | 8 | 0.508981 |

## Actual split tactics

All 184 actual setup records (40/40/104) are preserved in JSON with their original rank, input shapes and tactic data. Below each cell lists FC1 M×N×K / FC2 M×N×K in rank0 through rank7 order. Every tuple has cluster(2,1), raster_along_m=true and one selection call. M128 uses one-CTA instructions and M256 uses two-CTA; the boolean is the raster flag. These are observed tuner choices, not frozen replay tactics.

| Run | Global tokens | Rank0 through rank7 FC1/FC2 |
| --- | --- | --- |
| old_one_group | 1 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| old_one_group | 8 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| old_one_group | 32 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256 |
| old_one_group | 128 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| old_one_group | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| corrected_two_groups | 1 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| corrected_two_groups | 8 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| corrected_two_groups | 32 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/256×16×256; 128×16×256/256×16×256; 128×8×256/128×8×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256 |
| corrected_two_groups | 128 | 128×16×256/128×16×256; 128×16×256/256×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| corrected_two_groups | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| fitted_one_group | 1 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| fitted_one_group | 2 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| fitted_one_group | 4 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| fitted_one_group | 8 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| fitted_one_group | 16 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/256×16×256; 128×16×256/256×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| fitted_one_group | 32 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256 |
| fitted_one_group | 64 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 256×16×256/128×16×256; 128×16×256/256×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| fitted_one_group | 128 | 128×16×256/256×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| fitted_one_group | 256 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/256×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×32×256/256×32×256; 256×16×256/128×16×256; 128×16×256/128×16×256 |
| fitted_one_group | 512 | 128×32×256/256×32×256; 128×32×256/256×32×256; 128×32×256/256×32×256; 128×32×256/128×32×256; 256×32×256/128×32×256; 128×32×256/128×32×256; 256×32×256/256×32×256; 128×32×256/256×32×256 |
| fitted_one_group | 1024 | 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×64×256/256×64×256 |
| fitted_one_group | 2048 | 256×64×256/128×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256; 256×128×256/256×128×256 |
| fitted_one_group | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |

## Exact saved commands and reproduction

The following are the original logged launch commands, preserved as evidence; they are not run by the comparison helper. Source overlays and per-run provenance remain necessary to reproduce execution.

old_one_group: declared `c7713ba1+raw5`; remote HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=1,8,32,128,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":512\,\"epi_flag_batch\":\[2\,4\]\,\"load_balance_mode\":\"atomic_counter\"\,\"flag_batch\":4\,\"token_back_mode\":\"epi_warps\"\}
```

corrected_two_groups: declared `c7713ba1+raw5+transform2-cta-pool-fixed`; remote HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=1,8,32,128,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":512\,\"epi_flag_batch\":\[2\,4\]\,\"load_balance_mode\":\"atomic_counter\"\,\"flag_batch\":4\,\"token_back_mode\":\"epi_warps\"\}
```

fitted_one_group: declared `c7713ba1 + preferred5 fitter/default/uniform control; kernel SHA256 0e58304685775bae9b141ad6b7e0e0c9cac5e4441fd4cf5b38553dfcff2aa56a`; remote HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=1,2,4,8,16,32,64,128,256,512,1024,2048,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":\ 512\,\ \"epi_flag_batch\":\ \[2\,\ 4\]\,\ \"load_balance_mode\":\ \"atomic_counter\"\,\ \"flag_batch\":\ 4\,\ \"token_back_mode\":\ \"epi_warps\"\}
```

Reproduce this CPU-only analysis: `PYTHONDONTWRITEBYTECODE=1 python3 compare_transform_groups.py`.

Artifacts: `TRANSFORM_GROUP_COMPARISON_001.md`, `TRANSFORM_GROUP_COMPARISON_001.json` (46 raw rows, 184 original tactics, derived comparisons and hashes), `TRANSFORM_GROUP_COMPARISON_001.csv` (46 raw latency rows). Original logs, provenance and per-rank tactic files remain unchanged.

Contextual two-group codegen, correctness, full13 timing and repeated-run evidence are kept separate from this historical timing report. Historical corrected-two-group results are not relabeled as measurements of that newer source.
