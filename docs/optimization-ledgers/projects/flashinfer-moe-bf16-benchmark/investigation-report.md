### BF16 performance investigation

**Finding:** the W4A16 advantage is present in GPU expert computation. TRTLLM BF16 tuning is active; exhaustive native-tactic checks on the actual inputs do not close the gap. Preparation, tuning, L2 flushing and host dispatch are outside the reported CUPTI GPU span. Independent single-call graph events reproduce the ordering. These diagnostics supplement the unchanged nine sweeps.

**Provenance:** profiles, actual-input tactic sweep and event controls use `2079fa00c4a2a0fb2e95bb284978a703653a4830` on the same retained B300/CUDA 13.2 image above. Nsight Systems 2026.2.1, GPU 0; tactic diagnostics GPU 1, serialized with GPU 0 work. Initial cache/default audit uses `a3fce87d5beec29775e9bc3917df99ba6bc4db9c`. Naming commit `d0caa842` and profiling-only commit `2079fa00` are separate; normal benchmark functions/timing remain unchanged from the refactor validation source.

**Autotuning:** 2,852 successful native candidate profiles across 21 token buckets, zero failures; all ten measured warmup/capture dispatches used nonfallback cache hits with tuning disabled. The selected tactic reaches the native launcher. At 32 tokens, all 352 actual-input candidates give a best 284.5635 µs versus 287.3155 µs for the selected baseline (about 1%, single sweep). At 4096, the selected `(128,0)` is also the exhaustive eight-candidate winner at 529.3520 µs. Default `-1` is ~15% slower there. The v1 tuner's synthetic routing activates 11/30 local experts at 32/4096, versus 21/32 on actual inputs; shorter synthetic probe times therefore are not the final benchmark latency. The exhaustive actual-input sweep checks this selection concern directly.

TRTLLM BF16 tuned/default controls (µs; each cell is a 100-iteration median; 3 alternating pairs):

```csv
tokens,tuned_tactic,repeat,tuned_us,default_us
32,8:92,1,286.9315,287.1400
32,8:92,2,287.1560,287.0915
32,8:92,3,287.0440,287.0440
4096,128:0,1,528.9665,609.1280
4096,128:0,2,530.0870,610.4075
4096,128:0,3,531.5110,611.6720
```

All actual-input native candidates (median of 100 iterations, µs; one sample each). Each CSV row lists latencies in ascending contiguous config-ID order; `(tileN, config)` is the native tactic. This includes every 352/8 enumerated candidate plus default.

```text
tokens=32; default(-1)=286.8350
tile=8; config=0..143
295.8595,286.0840,297.8440,285.7475,299.2360,285.5240,295.9080,297.4760,286.0515,299.2035,286.1795,285.4120,297.0920,287.0435,298.6920,286.5315,300.6760,286.2120,296.9640,298.5000,286.8360,300.1955,286.5155,286.3720,295.2840,285.3795,296.8685,285.3000,299.1075,284.6115,295.2520,296.9475,285.4115,299.1080,284.8520,284.5635,296.2920,286.4840,298.1160,286.3075,300.0350,285.9240,296.1640,298.5960,286.8840,300.0355,286.2435,285.6995,297.1560,286.8360,298.8200,286.7560,300.6760,286.3080,296.5795,298.5475,286.8035,300.8355,286.7235,286.1800,296.7555,286.9640,298.3240,287.0435,300.3080,286.3885,296.9475,297.9720,287.0115,300.1160,286.6915,286.4990,296.2600,285.9395,297.4600,285.8280,299.6360,285.6360,295.9720,297.3800,286.1155,299.5075,285.6360,285.3955,297.2680,287.2360,298.4360,286.8200,300.6600,286.3555,297.1070,298.7720,286.9630,301.0115,286.7235,286.4840,295.3160,285.2355,296.7560,285.2200,299.2040,284.9795,295.3315,296.9640,285.4600,299.2995,285.0440,284.5800,296.3880,286.6440,297.8755,286.3395,299.7320,285.7800,296.1955,297.9715,287.1240,300.1160,286.1960,285.9715,297.1395,287.0595,299.0280,286.9150,300.9635,286.3720,297.1560,298.4520,286.9155,300.9960,286.6755,286.5800,296.9000,287.0920,298.2125,287.1080,300.1795,286.5635,296.5800,298.5800,287.0280,300.3085,286.8520,286.2920
tile=16; config=0..143
292.6915,294.5480,285.8280,296.8680,285.6355,285.1880,292.8355,285.6040,294.7075,296.8840,285.6200,285.3160,293.3160,295.2365,286.3875,297.7965,286.3235,286.0680,293.0440,286.6600,295.0760,297.4760,286.4200,286.2920,291.9400,293.9885,285.0910,296.1645,285.0600,284.7080,292.0835,284.9640,293.8280,296.4360,285.1070,284.7230,292.6760,294.9800,285.9240,297.1880,286.2595,285.3320,292.7240,285.9880,294.7080,296.8680,286.0040,285.5075,293.7630,295.8605,287.0440,298.0835,287.0920,286.5960,293.5720,286.7880,295.6520,297.4760,287.0120,286.1800,293.2840,295.4600,286.8670,297.9560,286.6115,286.2115,293.0435,286.3720,295.3805,297.2840,286.9325,286.0675,292.2435,294.4520,285.6040,296.4360,285.8760,285.1560,292.7245,285.5240,294.7560,296.9000,285.7320,285.3005,293.2845,295.3000,286.3245,297.5245,286.4360,286.5000,293.1080,286.4680,295.2520,297.5875,286.7240,286.1480,291.8760,294.1960,285.1080,296.0360,284.9640,284.8200,291.6040,285.1235,294.0360,296.2920,285.3160,284.7555,292.6440,294.8200,285.8920,296.9640,286.0520,285.1880,292.7560,285.9550,294.5955,297.2520,286.0840,285.7315,293.7000,295.8920,286.8520,298.2760,286.9000,286.9320,293.7320,286.8520,295.3640,297.7485,287.1720,286.6755,293.3965,295.4440,286.3725,297.3800,286.9160,286.1795,293.5725,286.5480,295.1400,297.5710,286.5950,286.2915
tile=32; config=0..63
292.4360,286.0520,295.0600,285.7955,292.2285,295.1080,285.5555,286.2440,294.3400,287.7800,297.5880,287.7320,294.1960,297.2200,287.8120,287.8920,293.0760,286.9160,296.5960,286.7720,292.8675,296.4680,286.8035,286.7240,293.6680,287.7165,297.1715,287.5720,293.5565,296.9160,287.6040,287.4920,292.1795,286.2110,295.2680,285.7475,292.1635,295.4600,286.0200,286.0675,294.1480,288.0195,297.5405,287.7955,294.1480,297.2200,287.6845,288.0680,293.2840,286.9160,296.1320,286.7075,293.0920,296.3240,286.9320,286.9800,293.8600,287.7960,296.7075,287.4290,293.5720,296.9160,287.3000,287.6835
tokens=4096; default(-1)=609.7365
tile=64; config=0..3
611.4960,611.9765,610.2970,611.5760
tile=128; config=0..3
529.3520,529.5590,530.8710,530.3430
```

**Nsight Systems complete device breakdown (µs):** 20 cold-L2, one-call graph replays per case after tuning and three uncaptured replays. Every non-dash activity cell is the mean of 20 instances; both temporary-zero kernels are shown separately. All target kernels/memsets are accounted for inside synchronized `moe` NVTX ranges; each contains one `cudaGraphLaunch`. The 20 separately labeled L2 flushes are excluded. Kernel sums are diagnostic, not latency: [programmatic dependent launch](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html) allows dependent kernel intervals to overlap. GPU span measures the first activity start through last activity end; uncovered gaps use the union of intervals. Inference profiles cover both inference activation variants because those flags do not change W4A16 or TRTLLM BF16; RL is separately profiled.

**Inference:**

| Activity / metric | CuTe W4A16 / 32 | TRTLLM BF16 / 32 | CuTe W4A16 / 4096 | TRTLLM BF16 / 4096 |
| --- | ---: | ---: | ---: | ---: |
| Top-k routing | 3.150 | 3.346 | 9.635 | 9.214 |
| Temporary zero 1 | 0.587 | — | 0.672 | — |
| Temporary zero 2 | 0.628 | — | 0.702 | — |
| Route map | 3.709 | 3.171 | 6.832 | 6.339 |
| BF16 permute | 4.648 | — | 22.986 | — |
| GEMM1 + SwiGLU | 67.812 | 189.739 | 164.956 | 331.377 |
| Output zero | 0.906 | — | 9.722 | — |
| GEMM2 | 36.946 | 89.677 | 147.033 | 150.361 |
| Finalize | — | 5.779 | — | 38.018 |
| GPU activity sum | 118.386 | 291.712 | 362.538 | 535.309 |
| GPU span | 118.522 | 285.562 | 359.142 | 527.871 |
| Uncovered GPU gaps | 0.668 | 0.000 | 0.644 | 0.000 |
| Graph launch CPU API (excluded) | 9.867 | 8.062 | 7.405 | 8.048 |
| L2 flush (excluded) | 67.826 | 67.925 | 67.882 | 67.810 |

**Deterministic RL:**

| Activity / metric | CuTe W4A16 / 32 | TRTLLM BF16 / 32 | CuTe W4A16 / 4096 | TRTLLM BF16 / 4096 |
| --- | ---: | ---: | ---: | ---: |
| Top-k routing | 3.094 | 3.283 | 9.622 | 9.283 |
| Temporary zero 1 | 0.592 | — | 0.677 | — |
| Temporary zero 2 | 0.590 | — | 0.694 | — |
| Route map | 3.578 | 3.014 | 7.237 | 6.586 |
| BF16 permute | 4.526 | — | 23.088 | — |
| GEMM1 + SwiGLU | 68.505 | 188.811 | 165.900 | 331.810 |
| Output zero | — | — | — | — |
| GEMM2 | 43.343 | 89.194 | 110.439 | 150.190 |
| Finalize | 5.880 | 5.755 | 31.789 | 38.095 |
| GPU activity sum | 130.108 | 290.058 | 349.446 | 535.964 |
| GPU span | 114.262 | 284.682 | 326.137 | 528.484 |
| Uncovered GPU gaps | 0.365 | 0.000 | 0.329 | 0.000 |
| Graph launch CPU API (excluded) | 7.163 | 6.141 | 10.132 | 8.223 |
| L2 flush (excluded) | 67.928 | 67.817 | 67.880 | 67.842 |

Kernel mapping: top-k=`deepseek_v3_topk_kernel` / `routingMainKernel`; route map=`routingIndicesClusterKernel` / `routingIndicesCoopKernel`; temporary zeros=`vectorized_elementwise_kernel`; permute/unpermute=`moePermuteKernel` / `moeUnpermuteKernel`; CuTe GEMMs=`Sm100W4A16GroupedGemmKernel` in launch order; TRTLLM BF16 GEMMs=`bmm_Bfloat16_Bfloat16Bfloat16...` (FC1 has `swiGlu`); native finalize=`finalizeKernel` / `finalizeKernelVecLoad`. CuTe inference GEMM2 includes atomic finalize; RL uses the separate unpermute row. At 32 tokens both GEMMs explain the gap; at 4096 the largest difference is GEMM1, with native finalize also contributing. TRTLLM BF16 has no uncovered device gaps in these traces.

**Independent timer control:** same tuned callable, one call per graph, 100 samples after 10 warmups; zero a 2×L2 byte buffer and synchronize before each start event, then `start.record(); graph.replay(); end.record(); end.synchronize()`. CUPTI separately measures the same prepared callable. Every case passed with finite outputs. Table contains every case's median in µs. Event intervals add roughly 4–6 µs but retain the gap; host submission cannot explain the BF16 slowdown. Warm-cache results are sequential diagnostics, not an isolated cache speedup claim. Ordinary `--no-cupti` is not this control: it uses ten-call graphs and rotates only input kwargs, leaving closure-held weights unrotated.

| Config | Tokens | Backend | Cold CUPTI | Cold events | Warm events |
| --- | ---: | --- | ---: | ---: | ---: |
| inference | 1 | CuTe W4A16 | 38.9440 | 42.9440 | 39.8240 |
| inference | 1 | TRTLLM BF16 | 50.7525 | 56.8640 | 46.5280 |
| inference | 32 | CuTe W4A16 | 118.9450 | 124.4480 | 113.4080 |
| inference | 32 | TRTLLM BF16 | 286.0665 | 292.3360 | 276.1920 |
| inference | 4096 | CuTe W4A16 | 361.9550 | 366.7200 | 378.1440 |
| inference | 4096 | TRTLLM BF16 | 528.9640 | 533.6480 | 543.2800 |
| rl | 1 | CuTe W4A16 | 40.1280 | 45.8080 | 42.1760 |
| rl | 1 | TRTLLM BF16 | 53.0885 | 58.8960 | 48.0480 |
| rl | 32 | CuTe W4A16 | 115.0410 | 120.3360 | 112.3520 |
| rl | 32 | TRTLLM BF16 | 286.5785 | 292.5920 | 276.2240 |
| rl | 4096 | CuTe W4A16 | 327.4590 | 333.0560 | 355.2640 |
| rl | 4096 | TRTLLM BF16 | 528.6275 | 533.4560 | 542.9120 |

### Nsight Compute: fixed normal-tuned tactics

- **Scope:** inference per-token, EP8/TP1, B300 GPU 0, NCU 2026.1.1, source `2079fa00`. Tactics were recorded during normal tuning before NCU injection, then fixed by a diagnostic helper; all captured calls had tuning disabled. Each report contains exactly FC1 (with SwiGLU) and FC2, nine replay passes each. Node replay flushes caches and isolates PDL kernels: these durations are diagnostics, not additive end-to-end latency.
- **Tactics:** TRTLLM BF16: `(8, 37)` at 32; `(128, 1)` at 4096. CuteDSL W4A16 uses the same tactic for both GEMMs: `((128, 8, 256), (2, 1), True)` at 32; `((256, 128, 256), (2, 1), True)` at 4096.

Raw counters below: R/W = DRAM bytes; D/T/S = DRAM throughput / tensor-pipe activity / SM throughput (% of sustained elapsed peak); LD/ST = local-memory sectors; warps = active warps per active SM cycle; A/T = achieved/theoretical occupancy (%).

| Tokens | Backend | GEMM | R bytes | W bytes | ns | D/T/S % | LD/ST | Warps | Occupancy A/T % | Registers/thread | Shared bytes/block |
| ---: | --- | --- | ---: | ---: | ---: | --- | --- | ---: | --- | ---: | ---: |
| 32 | TRTLLM BF16 | FC1 | 1233656832 | 3507200 | 176896 | 91.17/2.42/25.37 | 0/0 | 11.33 | 17.70/18.75 | 168 | 181904 |
| 32 | TRTLLM BF16 | FC2 | 616784896 | 4100096 | 93760 | 86.35/2.27/23.87 | 0/0 | 7.95 | 12.42/12.50 | 255 | 216720 |
| 4096 | TRTLLM BF16 | FC1 | 2064285184 | 17972224 | 323040 | 84.03/40.83/45.78 | 0/0 | 10.84 | 16.94/18.75 | 168 | 187032 |
| 4096 | TRTLLM BF16 | FC2 | 960271104 | 50072064 | 152864 | 86.17/44.00/48.40 | 0/0 | 6.98 | 10.91/12.50 | 255 | 219800 |
| 32 | CuteDSL W4A16 | FC1 | 349258752 | 3499264 | 65632 | 70.11/6.61/53.35 | 0/0 | 15.86 | 24.77/25.00 | 128 | 215040 |
| 32 | CuteDSL W4A16 | FC2 | 174409728 | 3022592 | 37504 | 61.78/5.74/49.50 | 0/0 | 15.61 | 24.39/25.00 | 128 | 206880 |
| 4096 | CuteDSL W4A16 | FC1 | 637545728 | 13989120 | 165696 | 51.26/87.20/87.81 | 0/0 | 15.84 | 24.75/25.00 | 128 | 223232 |
| 4096 | CuteDSL W4A16 | FC2 | 322100992 | 7225344 | 148096 | 28.99/44.90/46.44 | 0/0 | 15.06 | 23.53/25.00 | 128 | 215168 |

Remaining launch counters (all eight kernels): occupancy limits = 32 blocks, 1 block by registers, 1 by shared memory; warp limit = 5/8 blocks for BF16 FC1/FC2 and 4 for W4A16. Cluster dimensions = `(2,1,1)`, except BF16 at 32 uses `(1,1,1)`. `occupancy_cluster_pct` = 3.12%; `occupancy_cluster_gpu_pct` = 0.59/0.39% for BF16 FC1/FC2 and 0.78% for both W4A16 kernels (launch estimates, not measured GPU activity). Full raw CSV/report metadata is retained.

**Interpretation:** at 4096, BF16 still reaches 84–86% DRAM throughput with 41–44% tensor activity; W4A16 FC1 reaches 87% tensor activity. BF16 reads 3.025 GB versus W4A16's 0.960 GB. EP8 leaves 3715 local assignments across 32 experts (116/expert); 4096 is not each expert's GEMM M. No local load/store traffic was measured in any kernel. Registers and shared memory both limit residency to one block/SM; low occupancy alone does not establish an avoidable defect. These counters support a bandwidth explanation and do not demonstrate a spilling or launch-overhead bug.

Public CLI equivalent on `2079fa00`: TRTLLM BF16 at 32 passed normal cache save then fresh-process `--no-autotune` load (both exit 0, target cache hit, no retuning, unchanged cache hash). The measured counters above used the helper-frozen tactics, not this smoke cache. Run in the same inference environment with NVFP4 overrides unset. Require a target-operation `Config cache hit`; missing/incompatible caches can otherwise fall back.

```bash
export CUDA_VISIBLE_DEVICES=0 FLASHINFER_DISABLE_VERSION_CHECK=1 MAX_JOBS=8 FLASHINFER_LOGGING_LEVEL=info
m=(dram__bytes_{read,write}.sum {dram__throughput,sm__throughput,sm__pipe_tensor_cycles_active}.avg.pct_of_peak_sustained_elapsed gpu__time_duration.sum l1tex__t_sectors_pipe_lsu_mem_local_op_{ld,st}.sum sm__warps_active.avg.{per_cycle_active,pct_of_peak_sustained_active} sm__maximum_warps_per_active_cycle_pct launch__{registers_per_thread,shared_mem_per_block,occupancy_limit_{blocks,registers,shared_mem,warps},cluster_dim_{x,y,z},occupancy_cluster_pct,occupancy_cluster_gpu_pct})
for n in 32 4096; do
  for b in cute-dsl-w4a16 trtllm-bf16; do
    a=(benchmarks/bench_moe_deepseek.py --num-tokens "$n" --ep 8 --tp 1 --routing-input-mode logits --use-per-token-activation --include-activation-quant --profile-cuda --profile-backend "$b" --profile-iters 1 --cache "$b-$n.json")
    python "${a[@]}"
    test -s "$b-$n.json" || exit 1
    ncu --profile-from-start off --replay-mode kernel --graph-profiling node --nvtx --nvtx-include moe/ --kernel-name-base demangled --rename-kernels off --kernel-name 'regex:.*(Sm100W4A16GroupedGemmKernel|bmm_Bfloat16_Bfloat16Bfloat16_).*' --launch-count 2 --cache-control all --clock-control none --metrics "$(IFS=,; echo "${m[*]}")" --csv --page raw --print-units base --export "$b-$n" python "${a[@]}" --no-autotune
  done
done
```

**Why 4096 remains bandwidth-sensitive:** the actual EP8 routing has 3715/32 = 116.09 rows per expert. Useful BF16 GEMM FLOPs divided by unique weight bytes give 116.09 FLOP/byte; including minimum activation traffic gives about 108–112. The advertised dense BF16 rate is 36 PFLOPS/node ÷ 2 ÷ 8 = 2.25 PFLOPS/GPU ([NVIDIA HGX specifications](https://www.nvidia.com/en-us/data-center/hgx/)); with [8 TB/s HBM](https://docs.nvidia.com/enterprise-reference-architectures/hgx-ai-factory/latest/components.html), the ideal crossover is about 281 FLOP/byte. These are analytical peak bounds, supported here by the measured DRAM counters. Tile128 pads to 40 tiles/5120 slots (72.56% useful rows). The 3.025 GB measured BF16 reads are close to 2.819 GB unique weights and below 3.523 GB if every token tile reread them. Compression moves W4A16 GEMM1 toward compute saturation; equal tensor-core input precision does not give equal memory traffic.

**Reproduce the eight Nsight traces** from the implementation checkout and image above. Output files remain on the retained devbox; no compilation caches are removed.

```bash
git checkout 2079fa00c4a2a0fb2e95bb284978a703653a4830
export CUDA_VISIBLE_DEVICES=0 FLASHINFER_DISABLE_VERSION_CHECK=1 MAX_JOBS=8
for mode in inference rl; do
  unset FLASHINFER_NVFP4_4OVER6 FLASHINFER_NVFP4_4OVER6_E4M3_USE_256
  unset FLASHINFER_NVFP4_4OVER6_ERR_MODE FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH
  unset FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH
  extra=()
  if [[ $mode == rl ]]; then
    export FLASHINFER_NVFP4_4OVER6=1 FLASHINFER_NVFP4_4OVER6_E4M3_USE_256=1
    export FLASHINFER_NVFP4_4OVER6_ERR_MODE=MSE FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH=1
    export FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1
    extra=(--no-fused-finalize)
  fi
  for n in 32 4096; do
    for backend in cute-dsl-w4a16 trtllm-bf16; do
      nsys profile --sample=none --cpuctxsw=none --trace=cuda,nvtx \
        --cuda-graph-trace=node --capture-range=cudaProfilerApi \
        --capture-range-end=stop -o "$mode-$backend-t$n" \
        python3 benchmarks/bench_moe_deepseek.py --num-tokens "$n" --ep 8 \
        --warmup 10 --iters 100 --use-per-token-activation --include-activation-quant \
        --profile-cuda --profile-backend "$backend" --profile-iters 20 "${extra[@]}"
      nsys export --type=sqlite -o "$mode-$backend-t$n.sqlite" "$mode-$backend-t$n.nsys-rep"
    done
  done
done
```

Aggregate all GPU activities contained by each synchronized `moe` NVTX range, including target memsets; verify 20 ranges and one graph launch per range. Report per-kernel `sum(end-start)/20`, per-range GPU `max(end)-min(start)`, and CPU graph-launch duration separately. Exclude `l2_flush`; do not sum kernel durations as wall-clock latency. These are single-GPU local-expert diagnostics, not distributed or full-model speedups.
