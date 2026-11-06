# Adjacent full-sweep comparison of fitted one and two transform groups

Two groups lower absolute MegaMoE latency at 12 of 13 global-token shapes in these single runs. T64 regresses 5.96% (0.238513→0.252721ms), compared with a 2.18% increase in its independently tuned split control. Repeat T64 before concluding that the two-group configuration avoids meaningful regressions. T4096 improves only 0.52% (0.508981→0.506356ms), while its split control shifts −1.76%; that row is effectively neutral at this evidence level.

## Scope and provenance

- Same preferred-five fitter and flag4/epi scheduling profile; M256/N128/K256, dynamic N, eight B300, H7168/I2048/E256/top-k8, global tokens 1…4096, EP8. The fitter selects five raw A+SF stages for this geometry; transformed A, activation and accumulator pipelines retain their existing depths.
- One group uses 512 threads and launch register cap 128. Two groups use 640 threads and cap 96, with role targets 176/80/64/80/80 totaling the launch CTA pool 61,440. Both groups decode disjoint halves of each K tile, preserving raw and transformed pipeline phases. Uniform control release and fitter/default source are shared.
- Exact knobs: `{"epi_flag_batch": [2, 4], "flag_batch": 4, "group_hint": 512, "load_balance_mode": "atomic_counter", "token_back_mode": "epi_warps"}`. The only differences among the 16 recorded repository source hashes are kernel.py and frontend.py. Frozen per-file hashes below and in JSON determine the executed source; Git HEAD alone does not describe an overlay.
- BF16 activations and communication, packed NVFP4 weights, unchanged FP32 global scales and post-FC2 route weights. Both variants receive matching packed weights, scales and routes. Per-case seeds are weights 1000+rank, inputs 42+rank, router logits 137 and bias 911.
- Three warmups, 100 fixed CUPTI iterations, CUDA graph, cold L2. The statistic is the median of per-iteration maximum-rank GPU wall spans, each from earliest kernel start to latest kernel end. Setup, compilation, tuning, cache flush and codegen capture timing are excluded. These are complete distributed MoE-forward GPU spans, not serving throughput or a sum of individual kernel durations.
- Both split controls rerun tuning during setup, with one recorded selection per rank/shape (104 each). Control spread includes process/order and tuner variation; it is not a confidence interval for Mega. Historical five-shape measurements are kept in TRANSFORM_GROUP_COMPARISON_001.md and are not substituted here.
- Numerical validation is separate. Strict crosscheck tolerance and split --no-fused-finalize behavior remain unchanged; Mega reduces FP32 weighted BF16 per-route FC2 outputs, whereas split combines BF16 rank-local partials. These timing runs omit the strict cross-implementation crosscheck and rely on independent public-path numerical validation.
- Runtime image: nvcr.io/nvidia/pytorch:26.05-py3; torch CUDA13.2, CUPTI13.2.0, toolkit nvcc13.2.78. The generated-code compiler is CuTe DSL4.7.1 bundled CUDA13.3.27, a separate version from the toolkit.

## Complete raw paired timings

All values are ms. Each row contains both raw variant outputs for one shape/run (52 raw outputs total).

| Run | Global tokens | Split W4A16 ms | Mega W4A16 ms | Split/Mega |
| --- | --- | --- | --- | --- |
| one_group | 1 | 0.081200 | 0.100464 | 0.808250 |
| one_group | 2 | 0.101633 | 0.122385 | 0.830437 |
| one_group | 4 | 0.137296 | 0.138289 | 0.992819 |
| one_group | 8 | 0.156322 | 0.170849 | 0.914972 |
| one_group | 16 | 0.169010 | 0.183089 | 0.923103 |
| one_group | 32 | 0.202833 | 0.213249 | 0.951156 |
| one_group | 64 | 0.216993 | 0.238513 | 0.909774 |
| one_group | 128 | 0.233571 | 0.252625 | 0.924576 |
| one_group | 256 | 0.242513 | 0.254866 | 0.951531 |
| one_group | 512 | 0.238993 | 0.259026 | 0.922660 |
| one_group | 1024 | 0.260914 | 0.274498 | 0.950513 |
| one_group | 2048 | 0.350498 | 0.347442 | 1.008796 |
| one_group | 4096 | 0.554325 | 0.508981 | 1.089088 |
| two_groups | 1 | 0.082065 | 0.098720 | 0.831291 |
| two_groups | 2 | 0.116321 | 0.113489 | 1.024954 |
| two_groups | 4 | 0.143713 | 0.134864 | 1.065614 |
| two_groups | 8 | 0.154993 | 0.159777 | 0.970058 |
| two_groups | 16 | 0.179522 | 0.181090 | 0.991341 |
| two_groups | 32 | 0.204194 | 0.210721 | 0.969025 |
| two_groups | 64 | 0.221715 | 0.252721 | 0.877311 |
| two_groups | 128 | 0.236673 | 0.242498 | 0.975979 |
| two_groups | 256 | 0.242978 | 0.246594 | 0.985336 |
| two_groups | 512 | 0.240290 | 0.255026 | 0.942218 |
| two_groups | 1024 | 0.262257 | 0.265906 | 0.986277 |
| two_groups | 2048 | 0.350451 | 0.346882 | 1.010289 |
| two_groups | 4096 | 0.544547 | 0.506356 | 1.075423 |

## Adjacent comparisons

Negative Mega change means faster with two groups. Split shifts retain their sign; spread is max/min−1. These are derived from six-decimal printed latencies.

| Global tokens | Mega change | Split change | Split spread | Ranks with different split tactics |
| --- | --- | --- | --- | --- |
| 1 | -1.74% | +1.07% | 1.07% | [0, 5] |
| 2 | -7.27% | +14.45% | 14.45% | [0, 5] |
| 4 | -2.48% | +4.67% | 4.67% | [0, 5] |
| 8 | -6.48% | -0.85% | 0.86% | [0, 5] |
| 16 | -1.09% | +6.22% | 6.22% | [1, 3, 4] |
| 32 | -1.19% | +0.67% | 0.67% | [0, 1, 2, 5, 6, 7] |
| 64 | +5.96% | +2.18% | 2.18% | [1, 3, 4] |
| 128 | -4.01% | +1.33% | 1.33% | [0, 1, 3] |
| 256 | -3.25% | +0.19% | 0.19% | [2, 6] |
| 512 | -1.54% | +0.54% | 0.54% | [2, 4, 5, 6] |
| 1024 | -3.13% | +0.51% | 0.51% | [0, 1, 2, 4, 7] |
| 2048 | -0.16% | -0.01% | 0.01% | [1, 4, 5] |
| 4096 | -0.52% | -1.76% | 1.80% | [] |

The T64 split tactics differ on ranks 1, 3 and 4; this records control variation and does not explain away the Mega regression. In the two-group run, Mega remains slower than paired split at T1/8/16/32/64/128/256/512/1024. Small-token apparent wins at T2/4 coincide with large split-control shifts, so they are weak evidence of stable wins. At T4096, split/Mega is 1.0754× in this run; the one-versus-two-group difference itself is much smaller.

## Actual split selections

Each cell lists FC1 M×N×K / FC2 M×N×K in rank0…rank7 order. Every tuple also has cluster(2,1) and raster_along_m=true. M128/M256 determines one/two-CTA instructions; that boolean is not a CTA-mode flag. All 208 original records, shapes and call counts are preserved in JSON.

| Run | Global tokens | Rank0…rank7 actual FC1/FC2 tactics |
| --- | --- | --- |
| one_group | 1 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| one_group | 2 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| one_group | 4 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| one_group | 8 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| one_group | 16 | 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/256×16×256; 128×16×256/256×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| one_group | 32 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 256×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256 |
| one_group | 64 | 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 256×16×256/128×16×256; 128×16×256/256×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| one_group | 128 | 128×16×256/256×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| one_group | 256 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/256×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×32×256/256×32×256; 256×16×256/128×16×256; 128×16×256/128×16×256 |
| one_group | 512 | 128×32×256/256×32×256; 128×32×256/256×32×256; 128×32×256/256×32×256; 128×32×256/128×32×256; 256×32×256/128×32×256; 128×32×256/128×32×256; 256×32×256/256×32×256; 128×32×256/256×32×256 |
| one_group | 1024 | 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×64×256/256×64×256 |
| one_group | 2048 | 256×64×256/128×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256; 256×128×256/256×128×256 |
| one_group | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |
| two_groups | 1 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| two_groups | 2 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| two_groups | 4 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| two_groups | 8 | 128×16×256/256×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| two_groups | 16 | 128×8×256/128×8×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×8×256/128×8×256 |
| two_groups | 32 | 128×16×256/256×16×256; 128×16×256/256×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/256×16×256; 128×8×256/128×8×256; 256×16×256/128×16×256 |
| two_groups | 64 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 256×16×256/256×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256 |
| two_groups | 128 | 128×16×256/128×16×256; 128×16×256/256×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×8×256/128×8×256; 128×8×256/128×8×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| two_groups | 256 | 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×16×256/128×16×256; 128×32×256/256×32×256; 128×16×256/128×16×256; 128×16×256/128×16×256 |
| two_groups | 512 | 128×32×256/256×32×256; 128×32×256/256×32×256; 128×32×256/128×32×256; 128×32×256/128×32×256; 128×32×256/128×32×256; 128×32×256/256×32×256; 128×32×256/256×32×256; 128×32×256/256×32×256 |
| two_groups | 1024 | 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×64×256/128×64×256 |
| two_groups | 2048 | 256×64×256/128×64×256; 256×64×256/128×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/256×64×256; 256×64×256/128×64×256; 256×128×256/256×128×256 |
| two_groups | 4096 | 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×128×256/256×128×256; 256×192×256/256×192×256 |

## Exact executed source and commands

| Recorded path | One-group SHA256 | Two-group SHA256 |
| --- | --- | --- |
| benchmarks/bench_cute_dsl_moe_distributed.py | 681cb0f8f4b2819068a69b3b69aabb0db697d8b2e6b0e18612a154adf2741f21 | 681cb0f8f4b2819068a69b3b69aabb0db697d8b2e6b0e18612a154adf2741f21 |
| flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/__init__.py | 49cdd58ee38716d1e9be73a239650f877a2d73ec44681f97199db3e7c5d7a773 | 49cdd58ee38716d1e9be73a239650f877a2d73ec44681f97199db3e7c5d7a773 |
| flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/dynamic_mainloop.py | aac315c47a2667577cdb59b58e0e02f6c4482a9c18d1c82bc6f17ba473ab0994 | aac315c47a2667577cdb59b58e0e02f6c4482a9c18d1c82bc6f17ba473ab0994 |
| flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/epilogue.py | 0f6b614b0488ee79d17b3d0cff30715546f54504d687f3be08628a94a7ed86cd | 0f6b614b0488ee79d17b3d0cff30715546f54504d687f3be08628a94a7ed86cd |
| flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/frontend.py | dc334bd90272b604f61c4564113341ccf7b7a3b520678da394085e43d3339252 | d15098fde1977b84b883b08dbd5e7cbb04ee83988f2fc7c28d3159e98e5ac586 |
| flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/kernel.py | 0e58304685775bae9b141ad6b7e0e0c9cac5e4441fd4cf5b38553dfcff2aa56a | 58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7 |
| flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/__init__.py | da80ff434d9e5daea26e7bae355ba4a90779b7d9e4d2af7a8ff38fc0a7457a1b | da80ff434d9e5daea26e7bae355ba4a90779b7d9e4d2af7a8ff38fc0a7457a1b |
| flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/backend.py | 215316b332af406a17740917fa6d41c735369de5434f055f20bccb253b556374 | 215316b332af406a17740917fa6d41c735369de5434f055f20bccb253b556374 |
| flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/config.py | b66f8ab94c2aa8a410d90c0811ca1b849d90c271751f2030e3d905f16bd25ca3 | b66f8ab94c2aa8a410d90c0811ca1b849d90c271751f2030e3d905f16bd25ca3 |
| flashinfer/moe_ep/backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/weights.py | ed5b6614909f911bd25efbefe92328f4ee3a681394f89b992199610a972c7fd5 | ed5b6614909f911bd25efbefe92328f4ee3a681394f89b992199610a972c7fd5 |
| flashinfer/moe_ep/weights.py | 248d38f33d48225c201ca12e9c4df2b1c2ded883e73586a2ad616b96c19aefff | 248d38f33d48225c201ca12e9c4df2b1c2ded883e73586a2ad616b96c19aefff |
| flashinfer/moe_ep/modes/mega_layer.py | ae4eb4e27032e849d3a8fbb9effc760fc5a83fb6b1e51efc36ace262f225f1ea | ae4eb4e27032e849d3a8fbb9effc760fc5a83fb6b1e51efc36ace262f225f1ea |
| flashinfer/moe_ep/core/validation/common.py | eb9698890d043c132f6cbfdf98112f7d1391666233e682f3492df1c2125aef7c | eb9698890d043c132f6cbfdf98112f7d1391666233e682f3492df1c2125aef7c |
| flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py | cd11e0c1c37653b0a58403de04fa31ea20ae75a6ebab1b8330e7091e32d729f7 | cd11e0c1c37653b0a58403de04fa31ea20ae75a6ebab1b8330e7091e32d729f7 |
| flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py | 4a870648549397c4ef8d4db52b4bfe3dde3ff09feed94abd942ea945f3185866 | 4a870648549397c4ef8d4db52b4bfe3dde3ff09feed94abd942ea945f3185866 |
| flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py | c36c5fce4e8132dd19f1928fbc72100a1d7ddc8d90cc8db88cfe24b8d3e722c9 | c36c5fce4e8132dd19f1928fbc72100a1d7ddc8d90cc8db88cfe24b8d3e722c9 |

one_group: declared `c7713ba1 + preferred5 fitter/default/uniform control; kernel SHA256 0e58304685775bae9b141ad6b7e0e0c9cac5e4441fd4cf5b38553dfcff2aa56a`, timestamp `Tue Sep  8 04:40:51 UTC 2026`, remote Git HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=1,2,4,8,16,32,64,128,256,512,1024,2048,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":\ 512\,\ \"epi_flag_batch\":\ \[2\,\ 4\]\,\ \"load_balance_mode\":\ \"atomic_counter\"\,\ \"flag_batch\":\ 4\,\ \"token_back_mode\":\ \"epi_warps\"\}
```

two_groups: declared `c7713ba1 + preferred5 fitter/default/corrected2WG; kernel SHA256 58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`, timestamp `Tue Sep  8 04:57:16 UTC 2026`, remote Git HEAD `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.

```bash
timeout --kill-after=30s 1800s torchrun --nnodes=1 --nproc-per-node=8 --master-addr=127.0.0.1 --master-port=29541 /workspace/flashinfer-w4a16-megamoe/capture_benchmark_tactics.py --num-gpus=8 --parallel-modes=ep --variants=w4a16,w4a16_megamoe --num-tokens=1,2,4,8,16,32,64,128,256,512,1024,2048,4096 --warmup=3 --iters=100 --timing=cupti --cuda-graph --no-fused-finalize --verbose --megamoe-knobs \{\"group_hint\":\ 512\,\ \"epi_flag_batch\":\ \[2\,\ 4\]\,\ \"load_balance_mode\":\ \"atomic_counter\"\,\ \"flag_batch\":\ 4\,\ \"token_back_mode\":\ \"epi_warps\"\}
```

## Codegen and reproduction

FITTED5_TRANSFORM2_CODEGEN_REVIEW_001.md verifies all eight new two-group captures: REG96/640 threads, balanced register targets, unchanged explicit FC2 router local storage, no transform-attributed local accesses. The entire 5,672-instruction SASS sequence matches corrected constant-raw5 two-group capture002 at T4096. This establishes the absence of a new static local-storage footprint; it does not rule out runtime contention at T64 or other shapes.

```bash
python3 compare_fitted_transform_groups.py
```

Complete raw 52 rows: `FITTED_TRANSFORM_GROUP_COMPARISON_001.csv`; raw/derived values, 208 setup selections, all source hashes and 20 input artifact hashes: `FITTED_TRANSFORM_GROUP_COMPARISON_001.json`. Original logs/provenance and rank tactic JSON files remain under logs/ with the two run names above.
