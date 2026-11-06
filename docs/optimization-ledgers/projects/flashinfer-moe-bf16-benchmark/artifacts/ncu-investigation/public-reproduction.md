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
