# Deferred GLM5 EP8 AUTO profiling

Prepared locally; **no profiler, GPU operation, remote sync, installation, or live metric query has been run**. Use only if the current micro-optimization screens remain flat. Capture global T4096 with pristine baseline AUTO16 (`all`) and the retained optimized mixed catalog (`mixed-only`, currently12;18 if group256 is adopted). Keep these diagnostic captures separate from CUPTI timing comparisons.

## Worker policy and launch path

Calling `policy_driver.py` directly with `--mode profile_ncu` is insufficient: the native parent computes its worker script from its own `__file__` and launches that file in a new interpreter, losing the parent's candidate override. [`profile_ncu_policy.py`](../harness/profile_ncu_policy.py) instead imports the frozen native parent and changes only its process-launch boundary:

```text
parent adapter
  → native _run_ncu_profiles
  → torchrun --no-python (8 processes, static127.0.0.1 rendezvous)
  → one NCU process per rank, TCP communicator, strict/grid application replay
  → python policy_driver.py --native-driver <frozen driver> --tactic-policy all|mixed-only
  → unchanged native worker, --megamoe-knobs auto
```

Each replay restarts the policy wrapper, so its `MEGAMOE_POLICY_JSON` receipt and native AUTO selection occur inside every actual worker. The adapter preserves communicator, lockstep, NVTX, kernel filter, cache-flush, warmup and profiler-range logic. It forces the existing parent launch helper to static `--master-addr=127.0.0.1` with an explicit port; no `--standalone` hostname discovery is used. The frozen driver already supports that helper and is not edited.

Pinned native driver SHA256 is `90502a5eb9f8f402b3f8959b7065d319bc106d14de623c860a23610d3ac119d9`; existing policy wrapper SHA256 is `debc1f10711482235ecf152ffc5747a5fc4b1de2bf2275c9f9788bfeb7f048ef`. The adapter writes its hashes, original and rewritten child commands, native argv and process outcome to `policy-launch.json` in the new output directory.

## First capture: PC sampling and launch metadata

Default `--metrics pc` requests the established three PC entries plus five launch fields:

```text
smsp__pcsamp_sample_count
group:smsp__pcsamp_warp_stall_reasons
group:smsp__pcsamp_warp_stall_reasons_not_issued
launch__registers_per_thread
launch__block_size
launch__grid_size
launch__shared_mem_per_block_dynamic
launch__shared_mem_per_block_static
```

Use this as the first diagnostic pair. Native `--warp-sampling-max-passes=1` limits sampling passes; it does not cap hardware-counter passes. The explicit list avoids both `--set=full` and the implicit basic set. NVIDIA documents that `launch__*` fields require no extra replay pass, while application replay repeats host setup on every pass. This supports a one-pass target with source-correlated waits and launch resources, without adding traffic counters. Verify the actual pass count; it is not guaranteed by the metric-list length. [CLI sampling flags](https://docs.nvidia.com/nsight-compute/NsightComputeCli/#warp-sampling), [launch metrics and application replay](https://docs.nvidia.com/nsight-compute/ProfilingGuide/).

There is primary B300 precedent: the prior [N64 PC audit](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/profiles/tmem-n64-stage3-current-ncu-pc-001/independent-audit/ANALYSIS.md:14) recorded all eight reports with `profiler__replayer_passes=1`, source attribution, launch registers/SMEM, zero overflow and zero dropped bytes. It also recorded `smsp__pcsamp_aggregated_passes=2`; that sampler statistic must not be equated with application replay count. That earlier workload used a fixed tactic, so it establishes the profiler collection path only; this recipe still runs AUTO in every worker.

PC samples can locate scheduler publication, pipeline and collective wait instructions. They do not establish HBM bandwidth saturation, activation-B traffic savings, elapsed stall percentages or a steady-state critical path. Preserve per-rank distributions and source/SASS correlation: historical collective captures showed substantial startup skew. Launch register count does not expose warp-specific dynamic register redistribution or prove spills. The not-issued group narrows samples to cycles without scheduler issue, but still attributes the waiting consumer instruction. [NVIDIA sampling interpretation](https://docs.nvidia.com/nsight-compute/ProfilingGuide/#warp-stall-reasons).

Require `profiler__replayer_passes=1` in each report and retain worker-incarnation receipts, sampler interval, aggregated passes, sample count, overflow, dropped bytes and unmapped samples. One sampling pass can provide sparse or biased evidence; zero samples at a site do not prove it is free. Keep native adaptive interval and its pass cap unchanged initially. Do not silently add replay passes to improve coverage.

## Deferred traffic capture

Only if the PC/source evidence leaves a concrete traffic question, `--metrics traffic` requests nine metrics:

- `gpu__time_duration.sum`: instrumented duration for context only.
- `dram__bytes_read.sum`, `dram__bytes_write.sum`: total DRAM payload.
- `lts__t_sectors_lookup_hit.sum`, `lts__t_sectors_lookup_miss.sum`: L2 activity.
- `l1tex__m_xbar2l1tex_read_bytes_mem_global_op_tma_ld.sum`: TMA load payload at the crossbar/L1TEX interface.
- `sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed`, `smsp__issue_active.avg.pct_of_peak_sustained_active`, `sm__warps_active.avg.pct_of_peak_sustained_active`: broad compute/issue/occupancy context.

All PC, launch and traffic spellings occur in the saved B300 NCU2026.1.1 primary [report index](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/profiles/current-best-0909e-ncu-full-t4096-001/full-report-verification/summary.json). They have **not** been checked against this devbox's installed NCU. Traffic9 can require multiple hardware passes and repeat full AUTO/setup each time. No defensible one-pass traffic combination is established for the current installation, so do not use it for the first attempt or combine it with PC sampling. No unsupported section flags are introduced; the native driver accepts an explicit metric list.

## Command recipe after selection

First synchronize only the new project helper between runs. Confirm idle GPUs and retain the usual source/runtime manifests. The existing image is `nvcr.io/nvidia/pytorch:26.05-py3`, eight B300s, CuTe DSL4.7.1/CUDA13.2. Before capture, record `ncu --version`, check `ncu --help` for TCP peer/lockstep/application-replay support, and verify metric spellings with `ncu --query-metrics --query-metrics-mode all`. Counter permissions and communicator readiness are still unverified.

Run this parent directly, without wrapping it in torchrun. Execute one arm at a time, using a fresh output name and an available port:

```bash
set -euo pipefail
PROFILE_PROJECT=/data/home/ziangli/flashinfer-w4a16-mixed-clusters
PROFILE_SOURCE="$PROFILE_PROJECT/baseline"
PROFILE_POLICY=all
PROFILE_OUTPUT="$PROFILE_PROJECT/profiles/glm5-baseline-auto16-pc-t4096-a1"
PROFILE_CACHE="$PROFILE_PROJECT/compile-cache/baseline"
cd "$PROFILE_SOURCE"
exec 9>"$PROFILE_PROJECT/.gpu.lock"
flock -n 9
exec 8>"$PROFILE_PROJECT/.mixed-cluster-perf.lock"
flock -n 8
[[ -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]]
unset RANK LOCAL_RANK WORLD_SIZE LOCAL_WORLD_SIZE GROUP_RANK ROLE_RANK MASTER_ADDR MASTER_PORT
unset FLASHINFER_CUTE_DSL_MOE_PROFILE_CASE MEGA_USE_NCU MEGA_NO_DIST MEGA_SINGLE_GPU_GLOO
unset CUTE_DSL_LINEINFO CUTE_DSL_DUMP_DIR CUTE_DSL_KEEP CUTE_DSL_KEEP_PTX CUTE_DSL_KEEP_CUBIN
export PYTHONPATH="$PROFILE_SOURCE" PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 CUDA_HOME=/usr/local/cuda CUDA_MODULE_LOADING=LAZY
export BUILD_NVEP=0 BUILD_NIXL_EP=0 BUILD_NCCL_EP=0 FLASHINFER_BUILD_NO_PIP=1 MAX_JOBS=8
export FLASHINFER_MOE_EP_KNOB_CACHE=0 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_NVFP4_4OVER6=1 FLASHINFER_NVFP4_4OVER6_E4M3_USE_256=1
export FLASHINFER_NVFP4_4OVER6_ERR_MODE=MSE FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH=1
export FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1
export CUTE_DSL_NO_CACHE=0 FLASHINFER_CUTE_DSL_DISABLE_CACHE=0 CUDA_CACHE_DISABLE=0
export FLASHINFER_WORKSPACE_BASE="$PROFILE_CACHE/flashinfer"
export CUDA_CACHE_PATH="$PROFILE_CACHE/cuda-driver" TRITON_CACHE_DIR="$PROFILE_CACHE/triton"
python3 "$PROFILE_PROJECT/harness/profile_ncu_policy.py" \
  --native-driver "$PROFILE_PROJECT/flashinfer/benchmarks/bench_cute_dsl_moe_distributed.py" \
  --tactic-policy "$PROFILE_POLICY" --master-port 29691 \
  --metrics pc --output "$PROFILE_OUTPUT"
```

For the optimized arm, set `PROFILE_SOURCE="$PROFILE_PROJECT/flashinfer"`, `PROFILE_POLICY=mixed-only`, use a fresh candidate output name and another available port. The adapter fixes GLM5/EP8/T4096, `--megamoe-knobs=auto`, three warmups, one profiled invocation, precomputed routing, deterministic combine, default PDL, and native application replay. Its generated child command must retain `--megamoe-knobs auto`. The native parent creates a fresh per-output lineinfo CuTe cache; unchanged support-JIT caches remain shared. Expect first-use lineinfo compilation and repeated AUTO selection outside the profiler range.

## Evidence required and interpretation limits

- The current check is CPU-only: the actual native command-building functions ran with mocked subprocesses for both policies, proving worker injection, AUTO propagation, concurrent flags and localhost rendezvous. AST/Ruff passed. The original traffic-preset receipt is preserved in [`ncu-policy-command-validation.json`](ncu-policy-command-validation.json); the current PC/launch preset is checked in [`ncu-pc-launch-validation.json`](ncu-pc-launch-validation.json). No live import of the native GPU runtime or NCU application replay was tested.
- Require all eight nonempty rank reports, successful process exit, no replay/communicator warnings, unchanged source/driver hashes, and `MEGAMOE_POLICY_JSON` plus `MEGAMOE_TACTIC_JSON` for every rank and replay incarnation. Inspect catalog counts/hashes: baseline16, optimized12 or18, all ranks equal. The native parent only checks that at least one report exists; its success/adapter `completed` flag alone is insufficient.
- AUTO reruns on each application replay. A changed winner can change the kernel/grid and violate strict replay matching; retain per-rank/per-pass receipts and reject an unstable capture. Do not silently pin a fixed tactic or relax concurrent matching to force completion. T4096 supplies nonempty source ranks, satisfying the native application-replay restriction.
- The captured invocation is eager and instrumented, not the CUPTI graph benchmark. Profiler interception can also change the AUTO winner. Compare selected tactics before interpreting differences; no instrumented duration goes into a speedup table.
- DRAM/L2/TMA counters cover the whole fused kernel, including packed weights and transport. They do not isolate activation-B traffic or prove that a reduced traffic counter is on the critical path. Historical multiprocess captures had startup skew and invalid derived throughput percentages; inspect raw values per rank and preserve failures. PC long-scoreboard samples on barrier/control paths are not automatically HBM stalls.

If any readiness item fails, stop the profile attempt and preserve its partial output. This recipe does not authorize replacing the native concurrent EP8 path with isolated-rank profiling or altering the frozen measured driver.
