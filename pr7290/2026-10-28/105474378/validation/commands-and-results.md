# PR7290 retained W4A16 and compile-time MMA K

PR source: `1054743780dda2919c1424124c1e3258248b8c19`; measured W4A16 source: `640877340375fee0169f659a329d08b660c33eca`. Other formats retain `83dfef8a656384f5cd10db847602593bb6f9b2c6` measurements. Both full heatmaps use explicit mixed-source captions; baselines are never relabeled or rerun.

Hardware/environment: NVIDIA B300 (SM103), eight independent benchmark workers, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.78, PyTorch2.12.0a0+5aff3928d8.nv26.05, CuTe DSL4.8.0. Native C++ compilation caches are retained on persistent cluster storage. Each compilation process uses a private working directory.

The benchmark uses `benchmarks/bench_moe_deepseek.py` through the existing project-local observer. `--w4a16-only` restricts measurement to the public W4A16 call; it does not alter kernel knobs. The saved83df native autotune winner/cache and route identities are frozen. Every A1/A2 pass has10 warmups and100 strict CUPTI cold-L2 CUDA-graph samples; CUDA-event fallback and retuning during timing are rejected. The table uses the geometric mean of the two pass medians. Tokens1/2 are recorded but excluded from tables/retention. Communication is excluded. W4A16 BF16 inputs require no activation quantization; the NV-family opt-in flag is preserved.

Raw counts:104 cells,208 medians,20,800 samples; archive SHA256 `88fbd2914db8a5befe33207b3c529abb59f4f3c326f4dc664e9fb961fcf46df9`,799 verified files. All832 non-W4 table rows and all936 baseline records are unchanged. Historical source comparisons are not a fresh paired experiment: three EP rows differ by more than3% from saved83df timing and remain visible; they are not labeled noise. The separately controlled32-cell W4 retention screen is recorded locally.

## Executed benchmark commands

Each command below ran twice with source-private output directories and the identical frozen winner cache. `$PROJECT` denotes the persistent project folder and `$PYTHON` its CUDA13.2 validation interpreter. The observer/helper source hashes, routes, cache manifests, per-pass GPU UUID and100 raw samples per median are stored with the source-bound receipts.

```bash
# ep-kimi-k3
$PYTHON $PROJECT/observer/observe_benchmark.py --repo $PROJECT/flashinfer --output $PROJECT/results/ep-kimi-k3/$phase --w4a16-only -- --functional-api --model kimi-k3 --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache $PROJECT/frozen-caches/ep-kimi-k3 --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
# ep-nemo3-ultra
$PYTHON $PROJECT/observer/observe_benchmark.py --repo $PROJECT/flashinfer --output $PROJECT/results/ep-nemo3-ultra/$phase --w4a16-only -- --functional-api --model nemo3-ultra --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache $PROJECT/frozen-caches/ep-nemo3-ultra --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
# ep-v3
$PYTHON $PROJECT/observer/observe_benchmark.py --repo $PROJECT/flashinfer --output $PROJECT/results/ep-v3/$phase --w4a16-only -- --functional-api --model v3 --ep 8 --tp 1 --quant-family nvfp4 --backends cutedsl --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache $PROJECT/frozen-caches/ep-v3 --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
# ep-v41-flash
$PYTHON $PROJECT/observer/observe_benchmark.py --repo $PROJECT/flashinfer --output $PROJECT/results/ep-v41-flash/$phase --w4a16-only -- --functional-api --model v41-flash --ep 4 --tp 1 --quant-family nvfp4 --backends cutedsl --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache $PROJECT/frozen-caches/ep-v41-flash --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
# tp-kimi-k3
$PYTHON $PROJECT/observer/observe_benchmark.py --repo $PROJECT/flashinfer --output $PROJECT/results/tp-kimi-k3/$phase --w4a16-only -- --functional-api --model kimi-k3 --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache $PROJECT/frozen-caches/tp-kimi-k3 --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
# tp-nemo3-ultra
$PYTHON $PROJECT/observer/observe_benchmark.py --repo $PROJECT/flashinfer --output $PROJECT/results/tp-nemo3-ultra/$phase --w4a16-only -- --functional-api --model nemo3-ultra --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache $PROJECT/frozen-caches/tp-nemo3-ultra --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
# tp-v3
$PYTHON $PROJECT/observer/observe_benchmark.py --repo $PROJECT/flashinfer --output $PROJECT/results/tp-v3/$phase --w4a16-only -- --functional-api --model v3 --ep 1 --tp 8 --quant-family nvfp4 --backends cutedsl --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache $PROJECT/frozen-caches/tp-v3 --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
# tp-v41-flash
$PYTHON $PROJECT/observer/observe_benchmark.py --repo $PROJECT/flashinfer --output $PROJECT/results/tp-v41-flash/$phase --w4a16-only -- --functional-api --model v41-flash --ep 1 --tp 4 --quant-family nvfp4 --backends cutedsl --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --cache $PROJECT/frozen-caches/tp-v41-flash --swap-ab --no-fused-finalize --warmup 10 --iters 100 --no-autotune --include-activation-quant
```

## Exact/code-generation qualification

B300 / CUDA 13.2, `nvcr.io/nvidia/pytorch:26.05-py3`:

- `105474378`: integer MMA-K and logical-stage handoff passed 24 exact changing-route replay comparisons; all 12 GEMM pairs have identical PTX, instruction streams and resource usage. Six matched combine specializations also agree. The broader handoff check passed 160 exact replays and 80 identical GEMM PTX pairs; two SASS differences are equivalent uniform-register renames. Existing MX uniform spill/fill counts are unchanged. Final constant selection is equivalent to the compiled snapshot; no runtime branch or tactic was added.
- `640877340`: W4A16 passed 18 exact cases / 136 graph replays and four old/new-layout API tests. All 26 cleanup PTX/cubin/SASS/resource pairs are byte-identical to the measured W4A16 port. Its fresh EP/TP results use 104 cells / 208 medians / 20,800 CUPTI samples; all external baselines and other-dtype rows are unchanged.
- Prior `83dfef8a6` validation remains: 95 pytest + 11 Linux cache tests passed; memcheck, synccheck and racecheck each passed 128 exact graph replays / 64 compiled GEMMs, with zero errors/warnings and assembled TMEM guards. Earlier shared-address/private-workspace follow-ups passed exact and code-generation checks. **Sanitizers were not rerun for these W4A16/MMA-K changes, per request.** Local pre-commit passed for both new commits.

```text
integer MMA K: exact replays 24/24; matched GEMM PTX/instructions/resources 12/12
W4A16: exact cases 18/18; graph replays 136/136; API tests 4 passed
W4A16 handoff: identical PTX/cubin/SASS/resource pairs 26/26
benchmark: 104 cells; 208 medians; 20,800 CUPTI samples
preserved: 832 non-W4 table rows; all external controls
```



The source-paired project harnesses reuse the existing storage-bit reference and public layout API tests; no new repository tests or reference arithmetic were added. The initial N192/K256 supplement failed the unchanged control resource planner before compilation; N192/K128 passed both CTA groups. An analyzer initially paired compact and expanded combine specializations; correcting that pairing preserved all raw captures. Existing uniform-register spills were compared for equality, not assumed absent.

No sanitizer process was launched for these follow-ups. Earlier sanitizer evidence remains bound to its recorded source.
