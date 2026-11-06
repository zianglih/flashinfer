# Fixed-tactic NCU investigation

All four serial GPU 0 probes succeeded on retained devbox `flashinfer-moe-bf16-0904` (C2/ziangli). No devbox or cache was deleted. The target is inference per-token, EP8/TP1, 32/4096 global tokens, hidden 7168, intermediate 2048, top-k 8, 256 global/32 local experts. Source was `2079fa00c4a2a0fb2e95bb284978a703653a4830`; NCU is 2026.1.1.0 (build 37634170). The prior environment record identifies `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.1, Torch `2.12.0a0+5aff3928d8.nv26.05`, B300 SM103/148 SM.

## Provenance and scope

`fixed_tactic_benchmark.py` reads the actual chosen tactic from normal (pre-NCU) `artifacts/timed-control-inference.json`, checks that it was observed both inside normal tuning and outside tuning during graph capture, checks kernel-source identity, disables autotuning, and returns exactly that recorded tactic for the intended operation. Every intercepted call records shape, tactic, capture status, and `is_tuning_mode=false`. The NCU manifest records the helper hashes, reference hash, command, source, environment, and report hash. The same commit also has a public cache CLI; the helper was used to retain the exact tactics from the existing normal timing control.

`run_ncu_fixed_investigation.py --tokens 4096,32` collected 22 explicitly selected counters for FC1 and FC2 only. Each report has exactly two matching kernels, nine replay passes per kernel. `--profile-from-start off`, CUDA profiler API capture, NVTX `moe/`, and the GEMM regex exclude setup, warmup, routing, L2 flush, and finalization. `--graph-profiling node --replay-mode kernel --cache-control all --clock-control none` isolates individual nodes and does not preserve graph PDL overlap. Counter durations are not additive end-to-end measurements. The independent single-call CUDA-event/CUPTI and Nsight graph measurements remain the end-to-end evidence.

Fixed choices:

| Global tokens | TRTLLM BF16 | CuteDSL W4A16 (both GEMMs) |
| ---: | --- | --- |
| 32 | `(8, 37)` | `((128, 8, 256), (2, 1), True)` |
| 4096 | `(128, 1)` | `((256, 128, 256), (2, 1), True)` |

Both 4096 cases and W4A16 at 32 match the original Nsight kernel names, block dimensions, and grid dimensions. BF16 at 32 uses tile 8 from the independently tuned normal timing control; original Nsight used tile 16. See `artifacts/ncu-fixed/nsys-launch-comparison.json`. Earlier non-fixed NCU probes drifted under profiler injection and are supplemental only; these four probes supersede them for the main counter comparison.

## Findings

Full compact evidence is `artifacts/ncu-investigation/public-summary.md`. At 4096:

- TRTLLM BF16 FC1: 2,064,285,184 DRAM bytes read; 17,972,224 written; 323.040 us; 84.03% DRAM throughput; 40.83% tensor activity; 45.78% SM throughput. Effective read+write bandwidth is 6.446 TB/s.
- TRTLLM BF16 FC2: 960,271,104 DRAM bytes read; 50,072,064 written; 152.864 us; 86.17% DRAM throughput; 44.00% tensor activity; 48.40% SM throughput. Effective read+write bandwidth is 6.609 TB/s.
- W4A16 FC1: 637,545,728 bytes read; 13,989,120 written; 165.696 us; 51.26% DRAM throughput; 87.20% tensor activity; 87.81% SM throughput.
- W4A16 FC2: 322,100,992 bytes read; 7,225,344 written; 148.096 us; 28.99% DRAM throughput; 44.90% tensor activity; 46.44% SM throughput.

All eight kernels show **zero local-memory load and store sectors**. This is no evidence of local-memory spilling; it does not prove that every possible compiler spill mechanism is absent. BF16 uses 168 registers/thread in FC1 and 255 in FC2, with 187,032 and 219,800 shared bytes/block at 4096. W4A16 uses 128 registers/thread, 223,232 and 215,168 shared bytes/block. Both registers and shared memory limit every tested kernel to one resident block per SM. BF16 theoretical occupancy is 18.75%/12.50%, achieved 16.94%/10.91%; W4A16 theoretical occupancy is 25%, achieved 24.75%/23.53%. These values reflect different block/thread and pipeline designs; lower occupancy alone is not an avoidable defect, especially when DRAM throughput is already 84–86%.

The launch cluster occupancy fields are retained exactly as reported, but must not be presented as measured GPU utilization. Both 4096 backends use 2x1x1 clusters. All GEMMs report `launch__sm_count=148` in the full raw metadata; the routing reservation does not remove eight SMs from these GEMMs.

## Why global 4096 is still bandwidth-sensitive

The actual n4096 routing histogram from `artifacts/bf16-actual-tactic-sweep.json` contains 3715 local token-expert assignments across 32 active experts (min 81, max 147, mean 116.09375). Counts are `[123,118,141,125,145,102,101,147,120,106,116,110,115,82,104,134,111,132,105,123,95,133,118,119,135,116,95,97,118,144,81,104]`. Thus this is not a dense M=4096 GEMM per expert.

One expert has `3*7168*2048 = 44,040,192` weight elements across the two GEMMs. The active BF16 weights total 2,818,572,288 bytes; W4A16 packed weights plus one FP8 scale per 16 values total 792,723,456 bytes. Useful matrix multiplication work is `2*3715*44,040,192 = 327,218,626,560 FLOPs`, excluding nonlinear activation/finalization. Ideal BF16 intensity with each weight read once is only 116.09375 FLOP/byte before input/output traffic. Based on the measured read+write counters across both isolated GEMMs, useful intensity is 105.807 FLOP/byte for BF16 and 333.603 for W4A16.

Eight experts exceed 128 assignments, giving 40 token tiles and 5120 padded row slots at token tile 128 (72.5586% useful). A simplistic full weight reread for every tile would be 3,523,215,360 BF16 bytes before activation traffic; measured total reads are 3,024,556,288 bytes. Therefore the 206 MB above unique BF16 weight bytes is not proof of gratuitous redundant traffic: it includes activations/metadata and legitimate repeat token tiles, with cache reuse possible. Exact traffic attribution would require operand/cache-level measurements or a controlled kernel change. W4A16 reads 959,646,720 bytes total. The 3.152x measured read difference and high BF16 DRAM activity support bandwidth pressure; there is no measured register-spill or launch-overhead defect, and no concrete avoidable source-level issue established by these counters.

## Public cache recipe validation

Source at `2079fa00` was checked once. `bench_moe_deepseek.py:105-113` creates `autotune(False, cache=path)` with `--no-autotune --cache`, while normal `--cache` uses `autotune(True, cache=path)`. `flashinfer/autotuner/autotuner.py:954-963` loads the file on entry; 1024-1030 saves newly tuned results on tuning-context exit; loaded configs persist after the scope exits. `choose_one` at 2129-2133 uses the non-tuning lookup, and 1904-1922 returns matching config-file tactics. Therefore normal warmup followed by profiler execution with the same cache and `--no-autotune` is a public CLI equivalent. Missing/mismatched cache entries can fall back, so the reproduction requires a populated file and target-operation `Config cache hit` log, rather than assuming that merely supplying a path freezes choices.

A bounded GPU 0 smoke subsequently verified TRTLLM BF16 at 32 through the public CLI at the same clean `2079fa00` commit, benchmark SHA256 `179dba809d7b6c75990d322026519c163b9bbfa4a689ddd3bafa717f540fc815`. Normal tuning saved 21 configs, then a fresh process with `--no-autotune --cache` logged `Config cache hit for flashinfer::trtllm_bf16_moe`. Both processes exited zero. The second process did not start tuning and did not change cache SHA256 `7e69f0febb57a867f1379ea261b9495dc71d665fdb366d695593617e2f4ef0c5`. Artifacts are `artifacts/public-cache-bf16.{json,tune.log,load.log,smoke.json}` and the exact runner is `smoke_public_cache.py`. No NCU rerun was performed. This smoke cache contains a 4096 bucket as well; a second shape was not needed to verify the load mechanism. This fresh tune can choose different tactics from the prior timing-control run, so it does not replace the exact helper-frozen NCU measurement provenance.

`artifacts/ncu-investigation/public-reproduction.md` gives the compact public command. Its bash expansions were independently checked to produce exactly the same 22 metric names as the actual fixed-probe driver. The reproduction is explicitly distinguished from the helper-based measurements.

## Artifacts

- `artifacts/ncu-fixed/summary.json` and each `inference-*.json`: all 22 selected metric values/units/raw strings, full kernel names/configuration, commands, hashes, and fixed-tactic metadata.
- Each `inference-*.ncu-rep` and `.ncu.log`: original reports and full raw CSV; each `.fixed.json` and `.driver.log`: capture provenance and process output.
- `artifacts/ncu-fixed/all-raw-columns.json`: all 321 raw CSV columns plus units for each of eight kernels, including extra launch/device/replay fields automatically emitted by NCU.
- `artifacts/ncu-fixed/checksums.json`: report/data checksums; `nsys-launch-comparison.json`: exact name/grid/block comparisons.
- `artifacts/ncu-investigation/ncu-extended-capabilities.txt`: installed NCU metric/help queries before profiling.
- `build_ncu_public_summary.py`: reproducible report extraction/validation and compact public table generation.
