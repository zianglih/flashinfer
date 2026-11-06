# CuTe DSL NVFP4 MoE Optimization Experiment Ledger

Last updated: 2026-08-03

Scope: FlashInfer PR [#4048](https://github.com/flashinfer-ai/flashinfer/pull/4048),
branch `agent-cutedsl-moe-bf16-activation`, including the reverted W4A8
prototype that was developed on top of the W4A16 work.

This file intentionally lives in the wrapper workspace, outside the FlashInfer
repository. It records successful and unsuccessful experiments without adding
development notes to the upstream PR diff.

## Status Labels

- **Retained**: present in the branch.
- **Rejected**: measured or validated, then removed because it was slower,
  invalid, or added disproportionate complexity.
- **Reverted history**: preserved as a commit followed by a revert.
- **Diagnostic only**: useful for understanding the kernel, but not a candidate
  production change by itself.

## Current Retained Design

The W4A16 path accepts BF16 activations and NVFP4 weights. Both grouped GEMMs
decode each E2M1 x E4M3 weight block online to BF16 and execute BF16 tensor-core
MMA with FP32 accumulation. The per-expert FP32 weight scale is applied to the
FP32 accumulator. GEMM1 fuses SwiGLU or ReLU2 and writes the reduced BF16
intermediate directly for GEMM2.

The current kernel and launch design retains:

- A dedicated SM100 W4A16 kernel rather than adapting the SM120 W4A16 kernel.
- CUDA 13.2 direct-RN E2M1/E4M3-to-BF16 PTX and a pre-13.2 explicit-RN FP16
  decode/multiply plus exact widening compatibility path.
- One 16-value block decode helper, with one E4M3 scale decode per block.
- A 16-warp CTA: four 176-register epilogue warps, four 80-register
  role-control warps, and two four-warp transform warpgroups that retain the
  128-register launch allocation.
- 128-value transform fragments and no redundant post-copy transform barrier.
- Two narrow accumulator stages with release immediately after the final TMEM
  load, leaving more TMEM capacity and time for transformed-weight lookahead.
- Fused GEMM1 activation, reduced TMA store, and both one-CTA and two-CTA MMA
  topologies.
- Separate activation-TMA and weight-TMA warp roles.
- One routed-tile metadata stage for CLC GEMM1 and three stages for static
  GEMM2.
- PDL throughout permutation, GEMM1, and GEMM2, including early static-weight
  initialization before dependent activations are consumed.
- Activation TMA loads use an evict-last cache hint; packed weight loads use
  evict-first.
- Runtime autotuning over route tile and paired GEMM1/GEMM2 topologies with a
  fixed MMA K tile of 256.
- Explicit `quant_mode="w4a16"`, fused and deterministic finalize contracts,
  expert parallelism, stream-local reusable workspaces, and CUDA graph-safe
  wrapper caches.

After the 2026-07-22 tactic refresh, the search space is:

```text
route tiles: 8, 16, 32, 64, 128, 192
MMA K: 256
topology pairs:
  (GEMM1 M=128, cluster M=1) + (GEMM2 M=128, cluster M=1)
  (GEMM1 M=128, cluster M=2) + (GEMM2 M=128, cluster M=2)
  (GEMM1 M=256, cluster M=2) + (GEMM2 M=256, cluster M=2)
  (GEMM1 M=128, cluster M=2) + (GEMM2 M=256, cluster M=2)
  (GEMM1 M=256, cluster M=2) + (GEMM2 M=128, cluster M=2)
```

Route tile 8 keeps only the M=128/M=128 pairs because two-CTA M=256 tactics
require at least 16 routed rows. Route tile 192 keeps only M=256/M=256 because
the M=128 layout cannot retain both required load and transform stages. This
gives 23 tactics.

Relevant commit: `b2442579`.

## Benchmark Methodology Notes

- The main kernel sweeps use B200, CUDA 13.2, CuTe DSL compiler 13.3, CUPTI,
  CUDA graphs, and the 1, 2, 4, ..., 4096 token sweep.
- EP8 means 32 local experts from a 256-expert DeepSeek-style model. Simulated
  TP8 keeps all experts and divides intermediate size by eight.
- Distributed comparisons use real eight-GPU communication and start EP and TP
  from the same approximately `global_tokens / 8` distinct per-rank inputs.
- A previous heuristic/autotune comparison was invalid because the benchmark
  retained roughly 47-52 GiB of full-model allocations across rows. Explicit
  per-row allocator cleanup fixed the sweep-order dependency. Results from that
  invalid comparison must not be used.
- Small changes below about 1% are treated as noise unless they repeat or fix a
  clear shape-specific problem.
- `nsys` is the source of runtime breakdowns. CUDA-event/CUPTI timing is used
  for latency sweeps; hand-maintained kernel-name classification is avoided.

## Ongoing Optimization Workflow

For each new optimization, use the pushed cleanup commit `6ff56944` or the
latest retained optimization as the comparison baseline:

1. State one hardware or pipeline hypothesis and keep the code change isolated.
2. Run `pre-commit run --all-files` before syncing the tree to the devbox.
3. Monitor the initial compile and first kernel execution with process state,
   GPU utilization, and a bounded timeout. Do not infer a hang from compilation
   latency alone.
4. Benchmark `benchmarks/bench_moe_deepseek.py` with only CuTe DSL W4A16 over
   1, 2, 4, ..., 4096 tokens for both EP8 and simulated TP8. EP8 is the primary
   decision metric; a small TP8 regression is acceptable for a clear EP8 gain.
5. Use the distributed benchmark's `profile_nsys` and `profile_ncu` modes when
   latency alone cannot identify the limiting pipeline stage. Preserve profiler
   reports and command-traced logs under `logs/`.
6. Record the complete result here before retaining, revising, or reverting the
   experiment. Treat sub-1% changes as noise unless they reproduce or address a
   specific shape-level bottleneck.

For code-generation experiments, set `FLASHINFER_LOGGING_LEVEL=DEBUG` on a
small representative shape set and parse the autotuner's `profiling chosen
runner` records. This distinguishes a kernel change from a tactic-selection
shift before adding another autotune axis.

The candidate queue includes TMA L2 cache policy, weight/scale multicast,
shared-memory swizzling and bank behavior, PDL release points, and emitted
IR/PTX instruction scheduling. Avoid repeating rejected experiments unless a
later pipeline change invalidates the original conclusion.

## CUDA 13.2 Devbox Setup

Use a fresh exclusive eight-GPU B200 devbox for CUDA 13.2 optimization. Do not
pass `--queue hell`; leaving the queue unspecified lets the namespace select a
more stable queue. Run all `h` commands from `/Users/ziangli/rl/hai` and pipe
remote commands through stdin.

```bash
uv run h devbox -c c1 \
  --size exclusive \
  --gpu-type b200 \
  --gpus-per-pod 8 \
  --image pytorch/pytorch:2.13.0-cuda13.2-cudnn9-devel \
  --bare \
  w4a16-opt132
```

The bare image may not contain Git. Install it once, then clone the pushed
branch rather than syncing the full repository and submodules. A full `h sync`
of this checkout transfers hundreds of megabytes and has caused otherwise
healthy devboxes to disappear during setup.

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y git

rm -rf /root/flashinfer-src
git clone --recursive \
  -b agent-cutedsl-moe-bf16-activation \
  https://github.com/zianglih/flashinfer.git \
  /root/flashinfer-src
cd /root/flashinfer-src
git submodule update --init --recursive
git rev-parse HEAD
```

For an uncommitted kernel experiment, run `pre-commit run --all-files`
locally, upload only the edited files to shared storage, and copy them over the
cloned baseline. This preserves exact baseline lineage and avoids reinstalling
after Python-only CuTe DSL changes unless package metadata or source links have
changed.

```bash
# Remote: create the shared staging directory before `h warp`; otherwise the
# destination basename is created as a regular file.
mkdir -p /data/home/ziangli/agent/w4a16_candidate

# Local, from /Users/ziangli/rl/hai
uv run h warp \
  /Users/ziangli/playground/cute-dsl-nvfp4/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py \
  c1:/data/home/ziangli/agent/w4a16_candidate/moe_w4a16_utils.py

# Remote
cp /data/home/ziangli/agent/w4a16_candidate/moe_w4a16_utils.py \
  /root/flashinfer-src/flashinfer/fused_moe/cute_dsl/blackwell/
```

The image is PEP 668 managed. The three-package reset therefore requires
`--break-system-packages` on both uninstall and install. Do not install cubin
or JIT-cache packages for this CuTe DSL-only workflow.

```bash
python3 -m pip uninstall --break-system-packages -y \
  flashinfer-jit-cache flashinfer-python flashinfer-cubin

cd /root/flashinfer-src
export MAX_JOBS=200
export FLASHINFER_NVCC_THREADS=16
python3 -m pip install --break-system-packages \
  --no-build-isolation -e . -v

# The bare CUDA image does not include the test runner.
python3 -m pip install --break-system-packages pytest

# Match the Python timing bindings to the CUDA 13.2 image. Installing the
# unpinned latest package upgrades the CUPTI runtime to 13.3.
python3 -m pip install --break-system-packages \
  'cupti-python==13.2.0' 'nvidia-cuda-cupti==13.2.75'

flashinfer show-config
ldconfig -p | grep libcupti
```

Every test, benchmark, or profiler run uses command-traced logging, a bounded
timeout, and an independent GPU-utilization watchdog. Stage the complete log
directory under the shared home before downloading it locally:

```bash
mkdir -p /data/home/ziangli/agent/warp_logs
cp -a /sgl-workspace/logs/$RUN_ID /data/home/ziangli/agent/warp_logs/

# Local
uv run h warp \
  c1:/data/home/ziangli/agent/warp_logs/$RUN_ID \
  /Users/ziangli/playground/cute-dsl-nvfp4/logs/
```

If `h list -c c1` no longer shows the devbox while a create or SSH client is
still waiting, treat that as cluster-side devbox loss, stop the stale client,
and recreate the node. It is not evidence of a kernel hang. A kernel hang
requires a live devbox plus a bounded run that stops making progress while the
GPU remains active; preserve its watchdog and process-state logs before
terminating it.

## Retained Optimization Experiments

### Dedicated SM100 BF16-activation kernel

**Result: Retained.** The initial public path established the API contract, then
the implementation moved to a dedicated SM100 `tcgen05.mma` kernel. This made
online weight decode, warp specialization, fused activation, PDL, and launch
autotuning independently controllable.

Relevant commits: `bd46a929`, `9d340a0d`, `272a2150`.

### Direct and compatibility weight decode

**Result: Retained.** CUDA 13.2 directly converts packed E2M1 and E4M3 values to
BF16 with explicit RN PTX. The CUDA 13.0 compatibility path converts and
multiplies in FP16 with explicit RN, then widens the exactly representable
product through FP32 to BF16. The compiler version is resolved during kernel
generation, so there is no runtime device branch.

Bit-manipulation, packed-pair, x8, direct-scale, and compatibility decoders were
probed before settling on the current block helper. Evidence:

- `logs/w4a16_bit_decode_benchmark_20260719_054845/run.log`
- `logs/w4a16_bit_decode_packed_benchmark_20260719_055314/run.log`
- `logs/w4a16_bit_decode_x8_benchmark_20260719_055137/run.log`
- `logs/w4a16_direct_decode_benchmark_20260719_054223/run.log`
- `logs/w4a16_direct_sf_benchmark_20260719_062717/run.log`
- `logs/w4a16_compat_decode_benchmark_20260719_054128/run.log`

### Block decode and register rebalance

**Result: Retained.** Replacing pair-at-a-time decode with one 16-value block
helper improved the isolated W4A16 sweep by 1.039x geomean. Moving from the
192/208 epilogue/transform register split to 176/224 added 1.022x. Combined,
the two changes measured 1.061x geomean over 128-4096 tokens.

| Tokens | Pair decode 192/208 | Block decode 192/208 | Block decode 176/224 | Combined speedup |
|---:|---:|---:|---:|---:|
| 128 | 1.935 ms | 1.889 ms | 1.843 ms | 1.050x |
| 256 | 2.358 ms | 2.301 ms | 2.216 ms | 1.064x |
| 512 | 2.397 ms | 2.316 ms | 2.273 ms | 1.055x |
| 1024 | 2.396 ms | 2.305 ms | 2.259 ms | 1.061x |
| 2048 | 2.498 ms | 2.340 ms | 2.295 ms | 1.088x |
| 4096 | 3.670 ms | 3.527 ms | 3.502 ms | 1.048x |

Relevant commits: `2a1e14a5`. The register allocation is part of the current
kernel configuration.

### MMA K tile

**Result: Retained as an autotune axis.** Before online-decode optimization,
K=256 beat the original K=128 by 1.045x geomean over 128-4096 tokens. Later work
kept K=64, 128, and 256 in autotuning because the best value changes with route
density and TP/EP shape.

Relevant commit: `299d5a7a`.

### Transform-loop cleanup

**Result: Retained.** Removing a redundant transform-warp barrier and widening
the transform fragment from 64 to 128 values improved CUDA 13.2 by 1.018x
geomean and CUDA 13.0 by 1.027x in matched sweeps. The CUDA 13.2 2048-token row
was 0.995x, but the aggregate and compatibility-path gains justified keeping
the change.

Relevant commits: `24811dab`, `6dc21b83`.

### PDL

**Result: Retained.** The first PDL on/off sweep measured 1.006x geomean over
128-4096 tokens, with individual rows from 0.986x to 1.041x. This is close to
neutral, but keeping PDL aligns the path with the existing CuTe DSL MoE launch
contract and enables subsequent static-weight overlap work.

Later commits split activation and weight TMA roles and released dependent
kernels after static weight pipelines were initialized. Their end-to-end gain
is not independently large: against `127f2bd`, the raw geomean was 1.005x for
EP8 and 0.963x for TP8, while normalization by same-run W4A4 controls gave
1.007x EP8 and 1.014x TP8. The architecture was retained because it exposes the
correct dependency boundary and avoids forcing weight work to wait for input
activations.

Relevant commits: `1b52306a`, `e968d404`, `8f694964`.

### Retain routed activations in L2

**Result: Retained.** Each routed activation tile is reused across output-weight
M tiles, so activation-only TMA loads use the CUTLASS `EVICT_LAST` policy.
Weight and scale TMA policies remain at their defaults. The full sweep improved
by `1.0107x` EP8 and `1.0114x` simulated TP8 geomean. EP8 improved from 1
through 1024 tokens except for one noisy 2-token row, peaked at `1.0381x` for
64 tokens, and remained within 0.25% of baseline at 2048 and 4096 tokens.

| Tokens | EP8 speedup | simulated TP8 speedup |
|---:|---:|---:|
| 1 | 1.0141x | 1.0213x |
| 2 | 0.9881x | 1.0127x |
| 4 | 1.0151x | 0.9982x |
| 8 | 1.0139x | 1.0164x |
| 16 | 1.0149x | 1.0272x |
| 32 | 1.0112x | 1.0407x |
| 64 | 1.0381x | 1.0353x |
| 128 | 1.0201x | 1.0318x |
| 256 | 1.0203x | 1.0034x |
| 512 | 1.0035x | 0.9866x |
| 1024 | 1.0054x | 0.9915x |
| 2048 | 0.9975x | 0.9904x |
| 4096 | 0.9976x | 0.9945x |

Evidence: `logs/w4a16_activation_evict_last_bench_20260722_110831/run.log`.

### Sparse route and one-SM launch configurations

**Result: Retained.** Sparse N=32/N=64 route configurations and a one-SM MMA
topology improved the prior N=64/N=128 two-SM launcher by 1.019x geomean with
fused finalize and 1.024x with deterministic finalize. Gains concentrated in
128-512 token memory-bound cases; 2048-4096 tokens remained effectively neutral
and continued to select denser tactics.

Relevant commits: `116061db`, `4aabdeca`.

### Runtime autotuning

**Result: Retained.** Static route heuristics were replaced with the repository
`TunableRunner` pattern. Route tile, MMA K, and paired GEMM topology are included
in the compiled-kernel and workspace keys. Pairing GEMM1 and GEMM2 avoids a
large unconstrained Cartesian product while preserving the configurations that
were observed to matter.

Relevant commits: `ff5b757e`, `2466c215`, `300d76d8`, `043f09df`, `8c1a75c8`,
`9cf0fb3c`, `6a858a96`.

### Route tiles 8 and 16

**Result: Retained.** Expanding the route axis from 32/64/128 to
8/16/32/64/128 produced the following matched improvement against the original
36-tactic search:

| Tokens | EP8 speedup | Simulated TP8 speedup |
|---:|---:|---:|
| 1 | 1.0439x | 0.9959x |
| 2 | 1.0278x | 1.0182x |
| 4 | 1.0430x | 1.0483x |
| 8 | 1.0364x | 1.0682x |
| 16 | 1.0361x | 1.0861x |
| 32 | 1.0292x | 1.0971x |
| 64 | 1.0058x | 1.0923x |
| 128 | 1.0249x | 1.0863x |
| 256 | 1.0237x | 1.0615x |
| 512 | 1.0017x | 1.0029x |
| 1024 | 1.0042x | 1.0024x |
| 2048 | 1.0045x | 1.0018x |
| 4096 | 0.9999x | 0.9894x |
| **Geomean** | **1.0215x** | **1.0416x** |

The final 4096-token runs selected the same tactic as baseline, so the small
regressions there are measurement noise rather than a changed launch.

A route-16 ablation showed why both small tiles remain useful. Removing route 16
slightly improved/noised EP64 and EP128, but route 16 improved EP256 by 2.05%
and TP256 by 5.53%.

Evidence:

- `logs/w4a16_tactic_baseline_20260722_070456/run.log`
- `logs/w4a16_tactic_baseline_tp8_20260722_072201/run.log`
- `logs/w4a16_tactic_final_ep8_tp8_20260722_072924/run.log`
- `logs/w4a16_route16_ablation_20260722_074649/run.log`

### Fused GEMM1 activation

**Result: Retained after redesign.** The production design mirrors W4A4:
GEMM1 pairs gate/up rows through a logical full-M shared-memory exchange tile,
applies packed FP32 SwiGLU directly from accumulators, and TMA-stores only the
half-sized BF16 intermediate. ReLU2 follows the same fused-epilogue contract
without row pairing. This removes both the full GEMM1 output write/read and the
standalone activation launch.

Relevant commits: `bb14f22e`, `e8ec3854`, `0083a1f1`.

### Workspace, graph, finalize, and expert-parallel integration

**Result: Retained.** Stream-local workspace reuse, bounded route metadata,
explicit current-stream launches for utility kernels, fused finalize, and real
expert-parallel routing were needed to make performance optimizations usable in
serving and CUDA graph capture rather than only in isolated kernels.

Relevant commits: `2f960557`, `6f35b32f`, `c89ecd61`, `a0ed9747`, `8ea79347`.

## Rejected or Neutral W4A16 Experiments

### Reusing the SM120 implementation

**Result: Rejected.** It was useful for API and numerical bring-up, but it could
not express the intended SM100 tensor-core pipeline or online-decode overlap
cleanly. The dedicated SM100 kernel replaced it.

Evidence: `logs/sm100_w4a16_reuse_probe_20260718_122750/run.log` and
`logs/sm100_w4a16_accuracy_probe_20260718_122917/run.log`.

### Full prologue application of FP32 weight scale

**Result: Rejected.** Fully applying the per-expert FP32 scale while producing
BF16 weight operands moved scaling out of the accumulator epilogue, but it made
most EP8 and TP8 rows materially slower and introduced an extra BF16 rounding
point. Representative EP8 rows changed from 0.359 to 0.487 ms at 32 tokens,
0.413 to 0.549 ms at 128, and 0.768 to 0.875 ms at 4096. TP8 changed from
0.383 to 0.483 ms at 32, 0.446 to 0.593 ms at 128, and 1.196 to 1.320 ms at
4096. The FP32 accumulator scaling contract was retained.

Evidence:

- `logs/w4a16_scale_epilogue_cuda132_20260722_000455/run.log`
- `logs/w4a16_scale_prologue_cuda132_20260722_000941/run.log`

### First fused SwiGLU attempt as a separate kernel

**Result: Reverted history.** The first experiment wrote native up/gate rows and
launched a W4A16-only vectorized SwiGLU kernel. It reached only 0.986x geomean
and did not eliminate the full intermediate traffic. The attempt was committed
and reverted (`4ca05dd2`, `b3a1b6a4`). The later accumulator-epilogue fusion is
a different design and is retained.

Evidence:

- `logs/w4a16_swiglu_fused_benchmark_20260719_010753/run.log`
- `logs/w4a16_swiglu_unfused_benchmark_20260719_010953/run.log`

### Activation load alternatives

**Result: Rejected.** These were tested while trying to make sparse two-CTA
launches cheaper:

- Duplicate per-CTA `cp.async` activation loads were approximately neutral at
  N=32 and slower at N=64.
- A leader-CTA `cp.async` load followed by a swizzled DSM bulk copy was
  numerically correct but 27%-41% slower because peer transfer serialized after
  local load completion.
- A four-CTA TMA multicast cluster regressed memory-bound cases.
- Several mixed TMA/cp.async layouts were numerically validated, but none beat
  the retained TMA activation path over the full sweep.

Representative evidence:

- `logs/w4a16_mixed_full_cupti_20260719_202931/run.log`
- `logs/w4a16_mixed_tmawarp_sweep_20260719_205849/run.log`
- `logs/w4a16_mixed_dsm_gen_20260719_215345/run.log`
- `logs/w4a16_1sm_tma_mcast4_20260719_215853/run.log`
- `logs/w4a16_1sm_tma_final_cupti3_20260719_220751/run.log`

### More transform registers

**Result: Rejected.** Raising transform-warp registers to 224 or 240 without a
balanced role budget caused runtime stalls. A budget-neutral 160/240 split
trapped with an illegal instruction. A 168/232 probe also did not establish a
full-sweep win. The 176/224 split is the highest useful retained allocation
under the current CTA register budget.

Evidence: `logs/w4a16_cuda132_regs_168_232_20260719_105124/run.log` plus the
stalled/illegal configurations recorded in PR #4048 reviewer notes.

### Pipeline depth, transform width, and eager prefetch variants

**Result: Rejected.** Additional pipeline stages, x32/256-value transform
variants, and eager prefetch/try-wait arrangements were compiled and benchmarked
but did not improve the complete sweep. Some shifted cost between transform and
MMA while worsening occupancy or synchronization. The retained cleanup is the
128-value transform fragment with the redundant barrier removed.

Evidence:

- `logs/w4a16_cuda132_pipeline_baseline_20260719_102711/run.log`
- `logs/w4a16_cuda132_pipeline_prefetch_20260719_104151/run.log`
- `logs/w4a16_cuda132_pipeline_x32_20260719_103848/run.log`
- `logs/w4a16_cuda132_transform_fragment256_20260719_140002/run.log`
- `logs/w4a16_cuda132_two_stage_overlap_20260719_110819/run.log`
- `logs/w4a16_cuda132_two_stage_try_wait_20260719_111258/run.log`

### Reverse GEMM topology pair

**Result: Rejected.** Adding GEMM1 M=256/2-CTA plus GEMM2 M=128/2-CTA to the
paired topology list occasionally won autotuning, but measured only about 0.03%
at EP512 and 0.10% at TP512. That does not justify expanding every route/K
combination.

Evidence: `logs/w4a16_tactic_exhaustive_20260722_070747/run.log`.

### Fully independent GEMM1/GEMM2 topology and K Cartesian product

**Result: Rejected.** The exhaustive space was harder to understand and much
more expensive to tune. Most combinations were redundant. GEMM2 K=128 was
selected for a few larger TP profiles, but measured changes were only about
0.2%-0.4%. Shared K plus four curated topology pairs retained the meaningful
choices in a compact pattern.

Evidence:

- `logs/w4a16_tactic_exhaustive_20260722_070747/run.log`
- `logs/w4a16_mixed_k_validity_tp8_20260722_072400/run.log`
- `logs/w4a16_tactic_expanded_power_routes_tp8_20260722_072444/run.log`

### K=512

**Result: Rejected as unsupported.** All 25 K=512 candidates tested by the
expanded tactic probe were unsupported by the kernel configuration.

Evidence: `logs/w4a16_tactic_k512_20260722_071521/run.log`.

### Non-power-of-two route tiles

**Result: Rejected.** Route 24 aborted. Route 48 and 96 passed isolated validity
probes but had no demonstrated full-sweep benefit, and they would enlarge the
search space with irregular boundary behavior. The retained axis stays at
8/16/32/64/128.

Evidence:

- `logs/w4a16_tactic_route_grid_ep8_20260722_071758/run.log`
- `logs/w4a16_route_validity_20260722_071830/run.log`

### Invalid route-8 two-CTA tactics

**Result: Rejected as invalid.** Route tile 8 with an M=256 two-CTA GEMM does
not provide the minimum 16 routed rows required by that launch. Six invalid
combinations remained after the reverse topology was removed. Generation now
filters these combinations, and the test suite asserts the route-8 boundary.

Evidence: `logs/w4a16_tactic_failures_20260722_071309/run.log`.

### Launching GEMM1 dependents before the first tile-info wait

**Result: Rejected.** Moving `griddepcontrol_launch_dependents()` earlier was
neutral or noisy and often slightly slower across EP8 and simulated TP8. The
existing dependency release point was restored.

Evidence: `logs/w4a16_pdl_early_ep8_tp8_20260722_073245/run.log`.

### Acquiring the first activation-TMA stage before the PDL wait

**Result: Rejected.** Layered on the earlier launch experiment, pre-acquiring
the activation stage produced one 2.8% EP64 improvement but regressed TP2048 by
about 1.4%, TP4096 by about 1.1%, and several large EP rows. The broader result
did not justify the extra pipeline coupling.

Evidence: `logs/w4a16_pdl_preacquire_ep8_tp8_20260722_073622/run.log`.

### Pairing SwiGLU rows during NVFP4 decode

**Result: Retained.** The public group-64 gated weight layout remains unchanged,
but the transform composes a logical row layout that emits 16 up rows followed
by their 16 gate rows. Each epilogue warp can therefore load both operands from
its own 32 TMEM lanes. The epilogue evaluates SwiGLU directly in FP32 registers
and stores the reduced-M BF16 tile, removing the prior full-M BF16 shared-memory
exchange and its extra stages.

The full W4A16 test selection passed with both 1-CTA and 2-CTA tactics, gated
and ReLU2 activation, and fused and deterministic finalize:

```text
139 passed, 376 deselected
```

The CuTe-DSL-only `bench_moe_deepseek.py` workflow was neutral relative to both
the pre-remap baseline and the initial remap implementation:

| Configuration | Pre-remap / cleaned | Initial remap / cleaned |
|---|---:|---:|
| EP8 geomean | 0.9977x | 1.0023x |
| Simulated TP8 geomean | 0.9973x | 0.9998x |

The design was retained for the simpler lane-local pipeline and lower shared
memory traffic rather than for a claimed benchmark gain.

Evidence:

- `logs/w4a16_remap_bench_moe_cutedsl_20260722_100751/run.log`
- `logs/w4a16_cleanup_bench_moe_cutedsl_20260722_103004/run.log`
- `logs/w4a16_cleanup_final_test_20260722_102727/run.log`

### EVICT_LAST for scale TMA loads

**Result: Rejected.** NCU showed that the baseline emitted no explicit L2
eviction policy, so scale-only TMA loads were marked `EVICT_LAST` to reduce
pollution from the streaming E4M3 scale tensor. The full 1-4096-token sweep
measured only `1.0035x` EP8 and `1.0024x` TP8 geomean. EP8 regressed at
512-4096 tokens, including `0.9970x` at the profiled 4096-token shape, so the
hint did not improve the target bottleneck and was removed.

| Config | Geomean | Min | Max |
|---|---:|---:|---:|
| EP8 | 1.0035x | 0.9836x | 1.0231x |
| simulated TP8 | 1.0024x | 0.9820x | 1.0263x |

Evidence:

- Baseline: `logs/w4a16_cleanup_bench_moe_cutedsl_20260722_103004/run.log`
- Experiment: `logs/w4a16_scale_evict_last_bench_20260722_104245/run.log`

### Wider swizzles for the scale staging buffer

**Result: Rejected.** The baseline EP8-4096 NCU report localized the dominant
shared-memory excess to two scalar scale-fragment loads: GEMM1 issued them with
2-way bank conflicts and GEMM2 with 4-way conflicts. Applying a 32-byte
(`B=1`) swizzle to only the E4M3 scale staging buffer was numerically correct,
but measured `1.0036x` EP8 geomean and `1.0019x` TP8 geomean. A matching NCU
profile showed that both target instructions retained exactly the same N-way
conflicts and excessive-wavefront counts.

The 64-byte (`B=2`) swizzle was also numerically correct, but regressed EP8 to
`0.9946x` geomean and reached `0.9631x` at 2048 tokens. The original interleaved
layout was restored. Any future bank-conflict work should change the transform
fragment's lane-to-scale access pattern rather than the allocation swizzle.

| Layout | EP8 geomean | EP8 min | TP8 geomean | TP8 min |
|---|---:|---:|---:|---:|
| 32-byte swizzle | 1.0036x | 0.9808x | 1.0019x | 0.9720x |
| 64-byte swizzle | 0.9946x | 0.9631x | 1.0058x | 0.9851x |

Evidence:

- `logs/w4a16_scale_swizzle_b1_probe_20260722_105035/run.log`
- `logs/w4a16_scale_swizzle_b1_bench_20260722_105146/run.log`
- `logs/w4a16_scale_swizzle_b1_ncu_ep8_4096_20260722_105421/`
- `logs/w4a16_scale_swizzle_b2_probe_20260722_105756/run.log`
- `logs/w4a16_scale_swizzle_b2_bench_20260722_105844/run.log`

### EVICT_LAST for weight TMA loads

**Result: Rejected.** NVFP4 weight tiles are reused across routed N tiles, so
weight-only TMA loads were marked `EVICT_LAST`. The full sweep measured
`1.0020x` EP8 and `1.0005x` TP8 geomean, but EP8 regressed at 512-4096 tokens
and TP8 regressed at every 512-4096-token shape. The large-shape behavior did
not support retaining the hint.

| Config | Geomean | Min | Max |
|---|---:|---:|---:|
| EP8 | 1.0020x | 0.9824x | 1.0212x |
| simulated TP8 | 1.0005x | 0.9815x | 1.0408x |

Evidence: `logs/w4a16_weight_evict_last_bench_20260722_110442/run.log`.

### Account for the E4M3 scale type in shared-memory capacity

**Result: Rejected.** The stage-capacity calculation conservatively accounts
for the transformed scale tile at the MMA BF16 type even though the staged
scale buffer stores E4M3. Accounting for E4M3 directly did not change a useful
selected pipeline: EP8 measured `1.0002x` geomean (`0.9969x` minimum,
`1.0029x` maximum) and simulated TP8 measured `0.9994x` geomean (`0.9944x`
minimum, `1.0014x` maximum). The extra interface parameter was removed.

Evidence:
`logs/w4a16_scale_smem_accounting_bench_20260722_111837/run.log`.

### Increase the scale TMA pipeline from four to six stages

**Result: Retained.** The NVFP4 scale pipeline is independent of the larger
weight and activation pipelines. Increasing its depth from four to six keeps
more scale tiles in flight while the transform warpgroup decodes earlier
weight tiles. Two full sweeps reproduced the improvement:

| Sweep | EP8 geomean | simulated TP8 geomean |
|---|---:|---:|
| first | 1.0089x | 1.0091x |
| repeat | 1.0079x | 1.0140x |

EP8 improved broadly from 2 through 1024 tokens and remained effectively
neutral at 2048-4096 tokens. The one-token EP8 case regressed by 2.5-2.8%, but
EP8 throughput across the full workload is the priority. The route-64 2-CTA
hang/correctness probe passed before each sweep.

Evidence:

- `logs/w4a16_scale_stage6_probe_20260722_112554/run.log`
- `logs/w4a16_scale_stage6_bench_20260722_112619/run.log`
- `logs/w4a16_scale_stage6_repeat_bench_20260722_112859/run.log`
- `logs/w4a16_scale_stage6_ncu_ep8_4096_20260722_114514/`

The retained-stage NCU capture at EP8/4096 shows that this is not a large-GEMM
throughput optimization. GEMM1 measured 265.95 us versus 266.56 us before the
change, and GEMM2 measured 136.42 us versus 136.90 us. Tensor-pipe utilization,
occupancy, and the two-way/four-way scale-load bank conflicts were effectively
unchanged. The repeated full-sweep gain is concentrated in smaller and
mid-sized routes where deeper scale prefetching can hide latency.

The distributed Nsight Systems capture at 128 tokens measured W4A16 GEMM1 and
GEMM2 at 110.08 us and 72.05 us for EP8, and 111.01 us and 81.22 us for TP8.
Permute plus unpermute accounted for only 13.00 us in EP8. This keeps the next
optimization focus on the GEMM pipelines rather than the surrounding routing
or layout kernels.

Evidence: `logs/w4a16_stage6_nsys_t128_20260722_114954/`.

The EP8/128 NCU capture selected the two-CTA tactic and measured one 12-warp
CTA per SM (`18.43%` achieved occupancy). GEMM1 and GEMM2 spent about `80.3%`
and `70.7%` of cycles on the tensor/shared pipeline. TMA utilization was only
`1.29%` and `1.11%`, while each kernel had no eligible warp for roughly `48%`
of cycles and averaged `3.37` and `3.18` long-scoreboard-stalled warps. L2 hit
rates were `51.02%` and `52.22%`. This points to tensor/shared throughput and
the producer-consumer latency chain, rather than TMA issue bandwidth, as the
mid-shape constraint.

Evidence: `logs/w4a16_stage6_ncu_ep8_128_20260722_120052/`.

### Retain fused GEMM1 output with an EVICT_LAST TMA-store hint

**Result: Rejected.** GEMM1's fused activation output is consumed immediately
by GEMM2, so its TMA stores were marked `EVICT_LAST` to test whether explicit
producer-side L2 retention improves the roughly 52% GEMM2 L2 hit rate. The
complete EP8 sweep was neutral against both retained repeats, and simulated
TP8 regressed, including a `0.9761x` minimum and `0.9928x` geomean against the
second baseline. The hint was removed.

| Comparison baseline | EP8 geomean | EP8 min | TP8 geomean | TP8 min |
|---|---:|---:|---:|---:|
| retained sweep 1 | 0.9989x | 0.9822x | 0.9976x | 0.9832x |
| retained sweep 2 | 0.9999x | 0.9975x | 0.9928x | 0.9761x |

Evidence:
`logs/w4a16_store_evictlast_bench_20260722_120929/run.log`.

### Cluster-N weight and scale TMA multicast

**Result: Rejected.** The grouped scheduler was extended so one outer route
tile could be split across a two-CTA N cluster while weight and scale TMA loads
were multicast. Two numerical route-boundary cases passed, but the full
autotuned sweep was neutral for EP8 (`1.0000x` geomean) and regressed simulated
TP8 (`0.9983x` geomean, `0.9906x` minimum) against the retained baseline.

Fixed-tactic comparisons showed that the result was not an autotuner artifact.
At equal outer route granularity, cluster-N=2 was `1.83-1.95x` slower than
cluster-N=1 for the one-CTA MMA and `1.94-1.96x` slower for the two-CTA MMA at
128, 512, and 4096 tokens. Comparing equal per-CTA route widths reduced the
large-token gap, but cluster-N=2 remained slower in every case. Splitting N
adds CTAs and duplicates each CTA's full-M work; the multicast reduction in
static weight traffic does not recover that cost for these expert shapes.

Evidence:

- `logs/w4a16_cluster_n2_probe_20260722_122213/run.log`
- `logs/w4a16_cluster_n2_bench_20260722_122255/run.log`
- `logs/w4a16_cluster_n2_fixed_20260722_122939/run.log`

### Widen the packed-weight shared-to-register copy

**Result: Rejected.** The generic mixed-input transform uses a 32-bit copy atom
for packed 4-bit A. A 128-bit atom was tested to reduce shared-load instruction
count and alter the four-way-conflicted lane mapping, but it changed the weight
partition's leading dimension without a compatible scale partition and failed
the compile-time `tSrS`/`tArA` layout assertion. A 64-bit atom preserved the
paired layout and passed all four route-boundary numerical cases.

The full 64-bit sweep did not improve latency. Relative to the retained 32-bit
copy, EP8 measured `0.9976x` geomean (`0.9808x` minimum) and simulated TP8
measured `0.9982x` geomean (`0.9852x` minimum). A wider atom by itself does not
remove the shared-memory mapping constraint, so the 32-bit copy was restored.
A future revisit would require a co-designed weight and scale partition rather
than changing only the copy width.

Evidence:

- `logs/w4a16_copy128_probe_20260722_123605/run.log`
- `logs/w4a16_copy64_probe_20260722_123817/run.log`
- `logs/w4a16_copy64_bench_20260722_123859/run.log`

### Increase the scale TMA pipeline from six to eight stages

**Result: Rejected.** Eight stages over-carved shared memory without hiding
additional useful latency. Relative to the retained four-stage baseline, EP8
measured `0.9938x` geomean and simulated TP8 measured `0.9917x`; it was also
consistently slower than six stages. Restored six stages.

Evidence:

- `logs/w4a16_scale_stage8_probe_20260722_113238/run.log`
- `logs/w4a16_scale_stage8_bench_20260722_113257/run.log`

### Increase the scale TMA pipeline from six to seven stages

**Result: Rejected.** Seven stages passed all four route/topology numerical
cases but regressed the complete sweep. Against the two retained baselines,
EP8 measured `0.9769x`-`0.9775x` geomean and simulated TP8 measured
`0.9872x`-`0.9883x`. The seven-stage carveout therefore has the same direction
as the rejected eight-stage setting. Six stages remains the upper useful
depth; a five-stage follow-up brackets it from below.

Evidence:

- Correctness: `logs/w4a16_scale_stage7_test_20260722_161334/run.log`
- Full sweep: `logs/w4a16_scale_stage7_bench_20260722_161417/run.log`

### Decrease the scale TMA pipeline from six to five stages

**Result: Rejected.** Five stages passed the route/topology numerical matrix,
but the full sweep regressed to `0.9850x`-`0.9855x` EP8 geomean and
`0.9905x`-`0.9916x` simulated-TP8 geomean. Combined with the seven- and
eight-stage results, this brackets six stages as the measured optimum for the
current shared-memory carveout and transform pipeline.

Evidence:

- Correctness: `logs/w4a16_scale_stage5_test_20260722_161850/run.log`
- Full sweep: `logs/w4a16_scale_stage5_bench_20260722_161933/run.log`

### Add K=32 to W4A16 autotuning

**Result: Rejected at compile time.** A K=32 tactic could reduce the latency
between online weight decode and MMA consumption, and both DeepSeek GEMM K
dimensions are divisible by 32. The tactic enumeration was expanded and a
route-16, two-CTA numerical case was added before running a benchmark.

CuTe rejected the scale TMA descriptor while compiling the first K=32 kernel.
The 32-value scale shared layout and the two-CTA value map do not have
top-level shape equivalence. This establishes K=64 as the minimum supported
tile for the current TMA scale-layout contract. Reworking that contract solely
to admit K=32 is not justified when the smaller tile would also double MMA,
barrier, and persistent-loop iterations. The tactic space and temporary test
case were restored without benchmarking.

Evidence:

- Compile/numerical probe:
  `logs/w4a16_k32_test_20260722_163400/run.log`

### Raise transform warps from 224 to 232 registers

**Result: Rejected.** The retained CTA allocation leaves enough of the 64K
register file unused to raise all four transform warps by eight registers
without reducing any other role. This tests whether additional scheduler
freedom in the online decode and TMEM-store loop helps even though NCU reports
no local-memory spills. All four route/topology numerical cases passed without
hanging.

The complete sweep regressed. Against the two retained packed-weight-cache
runs, EP8 measured `0.9816x` and `0.9811x` geomean, with a roughly `8.1%`
minimum at 2048 tokens. Simulated TP8 measured `0.9912x` and `0.9923x`.
Increasing the ceiling therefore changes scheduling or occupancy allocation
unfavorably rather than exposing useful instruction-level parallelism. The
224-register transform allocation was restored.

Evidence:

- Correctness: `logs/w4a16_transform232_test_20260722_163745/run.log`
- Full sweep: `logs/w4a16_transform232_bench_20260722_163924/run.log`

### Lower transform warps from 224 to 216 registers

**Result: Rejected.** The midpoint between the earlier 208-register baseline
and the retained 224-register transform allocation was measured to complete
the local register sweep. It passed all route/topology numerical cases without
hanging.

EP8 measured `0.9900x` and `0.9895x` geomean against the retained runs, while
simulated TP8 measured `0.9764x` and `0.9774x`. The upper 232-register probe was
also slower, and the earlier 208-to-224 change was a retained win. These points
establish 224 registers as the measured local optimum for the current four-warp
online-decode pipeline. The 224-register allocation was restored.

Evidence:

- Correctness: `logs/w4a16_transform216_test_20260722_164637/run.log`
- Full sweep: `logs/w4a16_transform216_bench_20260722_164709/run.log`

### Preload packed A and release load stages before decode

**Result: Rejected.** CUTLASS's SM100 mixed-input collective copies the full A
and scale fragments into registers, releases its load-to-transform stage, and
only then performs dequantization and the transformed-operand store. W4A16 had
already tested full packed-fragment preload and earlier stage release
separately. This experiment combined them so the release had no final-fragment
predicate and exactly followed the CUTLASS lifetime ordering.

All route/topology numerical cases passed without hanging, but the large live
NVFP4 fragment dominated the additional producer overlap. EP8 measured
`0.9640x` and `0.9635x` geomean against the retained runs, with roughly `8.8%`
worst-point regressions. Simulated TP8 measured `0.9765x` and `0.9776x`.
Unlike the generic collective, this kernel benefits from block-local
load/decode/store scheduling that limits the packed fragment's live range. The
retained order and post-store release points were restored.

Evidence:

- Correctness: `logs/w4a16_preload_release_test_20260722_165151/run.log`
- Full sweep: `logs/w4a16_preload_release_bench_20260722_165228/run.log`

### Issue scale TMA before weight TMA

**Result: Rejected.** The scale and weight transfers share the static-data TMA
warp. Issuing each small scale transfer before its corresponding weight transfer
was numerically correct, but the asynchronous engine already hid the original
issue order. Relative to the retained six-stage sweep, EP8 was neutral at
`0.99995x` geomean while simulated TP8 regressed to `0.99656x`, including
`0.9806x` at 4096 tokens. The original weight-first sequence was restored.

Evidence:

- `logs/w4a16_scale_first_probe_20260722_115522/run.log`
- `logs/w4a16_scale_first_bench_20260722_115606/run.log`

### Deduplicate scale LDS operations with subgroup shuffles

**Result: Rejected at correctness gate.** NCU reports 2-way scale-load bank
conflicts for the selected 1-CTA GEMM and 4-way conflicts for the selected
2-CTA GEMM. Loading one packed scale word per 2-lane or 4-lane subgroup and
broadcasting it with `shfl.sync` passed every K-varying scale case but failed
all three row-varying scale cases. The conflicts are distinct row addresses
mapping to the same bank, not duplicate scale values, so subgroup broadcast is
not valid. No benchmark was run.

Evidence:
`logs/w4a16_scale_shuffle_correctness_20260722_114218/run.log`.

### Specializing the transform pipeline to NVFP4 scales

**Result: Retained.** W4A16 always consumes E2M1 weights with one E4M3 scale per
16 values. Removing the unreachable generic `ConvertOnly` path deleted
redundant optional tensors, pipeline branches, state, and constructor/tuner
arguments. It also removed unused kernel attributes and duplicate thread/block
index reads. This was source cleanup only; the benchmark table above shows no
material runtime change.

### More aggressive PDL control and asynchronous setup work

**Result: Diagnostic only / not retained.** Early-chain templates, moving
weight work between warp roles, and asynchronous memset/control experiments
helped establish dependency and warpgroup constraints but did not produce a
clean full-sweep win beyond the retained static-weight overlap design.

Evidence:

- `logs/pdl_early_chain_compile_20260722_044102/run.log`
- `logs/pdl_early_chain_template_20260722_044941/run.log`
- `logs/pdl_weight_warp_compile_20260722_040930/run.log`
- `logs/pdl_weight_warp_w4a16_suite_20260722_041951/run.log`
- `logs/pdl_async_memset_test_20260722_052135/run.log`
- `logs/cuda132_pdl_chain_benchmark_repeat3_20260722_054222/run.log`

## Reverted W4A8 Prototype

The W4A8 experiment dequantized NVFP4 weights through BF16, applied the FP32
global scale, requantized weights to MXFP8 online, fused GEMM1 activation plus
MXFP8 quantization, and used MXFP8 x MXFP8 tensor-core MMA. It explored
cp.async and TMA activation paths, one-CTA and two-CTA layouts, larger register
budgets for dequantization warps, scale TMA, mixed loading, and multiple pipeline
synchronization schemes.

**Result: Reverted history.** The implementation and its tests were committed
as `bf6f5a4b`, then reverted by `6dbe15e7`. The online NVFP4-to-MXFP8 transform
dominated both GEMMs, and the full 1-4096 sweep was not competitive:

| Comparison to W4A4 EP8 | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| W4A8 EP8 / W4A4 EP8 | 2.092x slower | 0.962x | 3.017x |
| W4A8 TP8 / W4A4 EP8 | 2.008x slower | 0.943x | 3.611x |

At 32 global tokens, staged GPU kernel time was 0.952 ms for W4A8 EP8 versus
0.257 ms for W4A4 EP8. At 4096 tokens it was 1.843 ms versus 0.490 ms. The
W4A8 GEMM1/GEMM2 rows, not communication, explained most of the gap.

Detailed results: `logs/w4a8_final_nsys_20260721_182318/summary.md`.

Representative failed or neutral sub-experiments:

- `logs/w4a8_cp_only_full_sweep_20260721_134257/run.log`
- `logs/w4a8_tma_full_sweep_20260721_133840/run.log`
- `logs/w4a8_mixed_probe_20260721_133533/run.log`
- `logs/w4a8_scale_tma_full_sweep_20260721_150704/run.log`
- `logs/w4a8_2cta_full_sweep_20260721_180306/run.log`
- `logs/w4a8_no2cta_full_sweep_20260721_180735/run.log`
- `logs/w4a8_reduced_tactics_full_sweep_20260721_135237/run.log`

## Streaming NVFP4 Weight Cache Policy

### Merge packed-weight and scale TMA barriers

**Result: Retained.** CUTLASS's SM100 mixed-input collective issues packed A
and its scale TMA against one transaction barrier and indexes both shared
buffers with one load-to-transform stage. W4A16 previously maintained a deep
A ring plus a separate fixed six-stage scale ring, paying independent
acquire/wait/release state and allowing the shallower scale ring to backpressure
the shared producer warp.

The two TMA copies now contribute their byte counts to one A+scale transaction,
share the A stage index and multicast mask, and become visible to transform
warps through one wait. Shared-memory capacity accounts for the scale bytes in
every A/B load stage. The transform remains block-local; the rejected full
fragment preload experiment showed that preserving its short packed-data live
range is important.

Two complete `bench_moe_deepseek.py` sweeps reproduced the improvement against
both retained packed-weight-cache baselines:

| Candidate | Configuration | Geomean range | Minimum range | Maximum range |
|---|---|---:|---:|---:|
| first | EP8 | `1.0194x`-`1.0200x` | `0.9870x`-`0.9874x` | `1.0520x`-`1.0536x` |
| repeat | EP8 | `1.0157x`-`1.0162x` | `0.9840x`-`0.9885x` | `1.0505x`-`1.0520x` |
| first | simulated TP8 | `1.0044x`-`1.0055x` | `0.9752x`-`0.9755x` | `1.0153x`-`1.0235x` |
| repeat | simulated TP8 | `1.0050x`-`1.0061x` | `0.9726x`-`0.9729x` | `1.0165x`-`1.0332x` |

The EP8 gain is broad from 32 through 2048 tokens. The full W4A16 class passed
`12` tests after cleanup. A fixed route-32 PTX dump confirms that this is a
real synchronization reduction: `mbarrier.init` sites fall from 149 to 129,
`arrive.expect_tx` from 3 to 2, `mbarrier.try_wait` from 105 to 89, and PTX size
from 93,010 to 85,216 bytes.

A post-merge EP8/128 NCU capture measured GEMM1 at `133.09 us` and GEMM2 at
`77.54 us`, down from approximately `145 us` and `82 us` in the retained
pre-merge profiles. Tensor-pipeline activity rose to `88.32%` and `74.78%`.
The remaining no-eligible-warp rates (`47.81%` and `49.25%`) and scale-load
shared replay (`458,752` and `688,128` excessive wavefronts) identify the
transform scale path as the next target rather than additional TMA depth.

Evidence:

- Initial correctness: `logs/w4a16_merged_tma_test_20260722_165901/run.log`
- Full tests: `logs/w4a16_merged_tma_full_test_20260722_170712/run.log`
- First sweep: `logs/w4a16_merged_tma_bench_20260722_165948/run.log`
- Repeat sweep: `logs/w4a16_merged_tma_repeat_20260722_170158/run.log`
- Generated PTX: `logs/w4a16_merged_tma_ir_ptx_20260722_170744/`
- NCU EP8/128: `logs/w4a16_merged_ncu_ep8_128_20260722_171911/`

### Mark packed weight TMA loads as `EVICT_FIRST`

**Result: Retained.** Packed NVFP4 weights are streamed by each routed tile,
while the BF16 activation operand is reused across experts and is already
marked `EVICT_LAST`. This matches CUTLASS's weight-prefetch GEMM policy of
evicting the streaming operand first and retaining the reused operand. The
change only sets the SM100 TMA L2 cache-policy descriptor; it does not alter
the load pipeline, layouts, or numerics.

Two independent full `bench_moe_deepseek.py` sweeps produced the following
speedups over the `74478ca0` stage-6 baseline:

| Configuration | Repeat | Geomean | Minimum | Maximum |
|---|---:|---:|---:|---:|
| EP8 | 1 | 1.0215x | 0.9786x | 1.0489x |
| EP8 | 2 | 1.0230x | 0.9962x | 1.0453x |
| simulated TP8 | 1 | 1.0173x | 0.9765x | 1.0418x |
| simulated TP8 | 2 | 1.0113x | 0.9680x | 1.0420x |

EP8 improved consistently from 1 through 1024 tokens. At 2048 and 4096 the
repeat was effectively neutral (0.9962x and 0.9983x), so the first run's
4096-token dip was measurement noise rather than a stable regression. The
largest TP8 cases regress slightly, which is acceptable for this EP8-focused
optimization.

The tuner diagnostic confirmed that sparse EP8 profiles select route-8 with
128x256 two-CTA GEMMs, while the dense endpoint selects route-128 with 256x256
two-CTA GEMMs. NCU at EP8/128 showed GEMM1 duration moving from 145.60 us to
144.93 us and L2 hit rate from 51.02% to 52.26%. GEMM2 was within profiler
noise (81.70 us versus 82.91 us), consistent with the cache policy primarily
protecting data reused across kernel boundaries.

Evidence:

- `logs/w4a16_weight_evict_first_bench_20260722_124723/run.log`
- `logs/w4a16_weight_evict_first_repeat_20260722_125124/run.log`
- `logs/w4a16_weight_evict_first_tactics_20260722_125440/run.log`
- `logs/w4a16_weight_evict_first_ncu_ep8_128_20260722_125647/`

### Mark E4M3 scale TMA loads as `EVICT_FIRST`

**Result: Rejected.** The scale tensor is also streamed, so its TMA loads were
given the same policy on top of the retained packed-weight hint. Relative to
the two packed-weight-only sweeps, EP8 measured `0.9987x` and `0.9982x`
geomean. The 128- and 256-token rows regressed by about 1.8% and 2.2% against
the repeat. Simulated TP8 improved by about 0.3-0.4%, but that does not justify
an EP8 regression. The scale load retains the default cache policy.

Evidence: `logs/w4a16_scale_evict_first_bench_20260722_130231/run.log`.

### Split scale TMA onto a thirteenth warp

**Result: Rejected at the hang gate.** The scale pipeline was moved from the
packed-weight TMA warp to a dedicated 80-register warp so six scale stages
could advance independently. The nominal CTA register sum remained below the
64K-register budget, but the first route-tile correctness probe pinned GPU 0
at 100% for more than 40 seconds with no compiler process and no completed
test. Killing the pytest process immediately returned the GPU to idle. No
benchmark was run. The 12-warp CTA and shared static-data TMA warp were
restored; any future split must preserve the existing complete warpgroup and
barrier participation contract.

Evidence: `logs/w4a16_dedicated_scale_tma_probe_20260722_130915/run.log`.

### Split scale TMA onto the scheduler warp

**Result: Rejected.** To avoid the thirteenth-warp barrier issue, the existing
scheduler warp published each tile's metadata and then issued that tile's scale
TMA loads while the weight warp issued packed-weight loads. The scheduler was
raised from 64 to 80 registers. All four route/topology numerical probes passed
without a hang, proving the pipeline ownership was valid, but the scheduler's
new back-pressure delayed sparse tile publication.

Against the two retained packed-weight `EVICT_FIRST` sweeps, EP8 measured
`0.9882x` and `0.9877x` geomean. The 2-16 token rows regressed by roughly 2-5%.
Simulated TP8 measured `0.9926x` and `0.9936x`. The scale pipeline therefore
remains colocated with packed-weight TMA on warp 6; keeping warp 5 dedicated to
routing is more important for sparse workloads.

Evidence:

- `logs/w4a16_schedule_scale_tma_probe_20260722_131546/run.log`
- `logs/w4a16_schedule_scale_tma_bench_20260722_131653/run.log`

### Decode four E4M3 scales in one PTX helper

**Result: Rejected.** The CUDA 13.2 direct path packed four E4M3 scales into
one operand, decoded them with two `cvt.rn.bf16x2.e4m3x2` instructions, and
broadcast the resulting BF16 values with `prmt` before decoding four adjacent
NVFP4 blocks. The existing CUDA 13.0 compatibility path was unchanged. All
four route/topology numerical probes passed bitwise.

The full sweep was substantially slower: `0.8385x`/`0.8380x` EP8 geomean and
`0.8980x`/`0.8989x` simulated-TP8 geomean versus the two retained
packed-weight-cache sweeps. The emitted PTX reduced E4M3 conversions from four
to two and reduced virtual B32/B64 register declarations, but the large opaque
inline-assembly region serialized four blocks behind the packed scale decode
instead of preserving block-local instruction scheduling. The original
one-scale-per-block helper was restored.

Evidence:

- `logs/w4a16_packed_scale_decode_probe_20260722_132600/run.log`
- `logs/w4a16_packed_scale_decode_bench_20260722_132653/run.log`
- `logs/w4a16_packed_scale_decode_ptx_20260722_132906/`
- Baseline PTX: `logs/w4a16_ir_ptx_route32_20260722_132155/`

### Apply a B128 swizzle to packed NVFP4 staging

**Result: Rejected.** The packed-weight transform load uses four shared-memory
wavefronts for each 128-bit per-thread request. A B128 swizzle was tested on
the packed E2M1 staging layout while leaving scale, BF16 transform, and
activation layouts unchanged. All route/topology numerical probes passed.

Most EP8 rows through 1024 tokens were neutral, but 2048 tokens repeated at
`0.2870` and `0.2868` ms versus the retained `0.2625-0.2627` ms. This is an
8.5% regression and reduced EP8 geomean to about `0.993x`. Simulated TP8 was
about `1.002-1.003x` geomean and improved its 4096-token row, which is not
enough to accept the stable EP8 regression. The generated B32 layout was
restored. On closer inspection, NCU reports no excess wavefronts for the
128-bit packed load; its four wavefronts are the expected transfer width, not
a four-way bank conflict. The excess wavefronts remain localized to the scale
load, so future work must target its lane-to-fragment mapping.

Evidence:

- `logs/w4a16_weight_swizzle_b3_probe_20260722_133437/run.log`
- `logs/w4a16_weight_swizzle_b3_bench_20260722_133548/run.log`
- `logs/w4a16_weight_swizzle_b3_repeat_20260722_133814/run.log`

### Transpose transform ownership for conflict-free scale words

**Result: Rejected at correctness gate.** The retained PTX computes each transform thread's
packed scale-word index as `4 * lane + transform_warp`. Its bank index is
therefore `4 * lane + transform_warp (mod 32)`, which uses eight banks per warp
and produces the measured four-way conflict. A lane-only permutation cannot
change that address multiset.

The next experiment transposes ownership across all four transform warps. For
physical warp `w` and lane `l`, it assigns logical transform thread
`32 * (l % 4) + 8 * w + l // 4`. Under the existing partition this maps the
scale word to `32 * w + l`, a conflict-free contiguous sequence, while still
covering every packed input and transformed output fragment exactly once.
The route32 1-CTA and route64 2-CTA probes passed, but route8 1-CTA reached only
96.35% within tolerance and the mixed route128 case reached 72.34%. This
confirms that the source/scale partition cannot be transposed independently of
the physical warp ownership required by the TMEM store path. The kernel did not
hang, and the retained mapping was restored without running a benchmark.

Evidence:
`logs/w4a16_scale_owner_transpose_probe_20260722_134559/run.log`.

### Transpose the scale atom in TMA shared storage

**Result: Rejected at descriptor contract.** The canonical block-scale atom
stores scale byte `(m0, m1, k1)` at `16*m0 + 4*m1 + k1`. A custom atom using
`4*m0 + 128*m1 + k1` would make each transform warp's packed scale words
contiguous without changing transform or TMEM ownership. The experiment applied
that atom consistently to the allocation and TMA destination views.

CuTe's tiled TMA construction requires top-level shape equivalence with its CTA
V-map. The route8 tactic was rejected during compilation with that explicit
layout-equivalence error. A route32 variant formed a descriptor but faulted with
`CUDA_ERROR_ILLEGAL_INSTRUCTION`, after which the CUDA context poisoned the
remaining cases. The canonical `make_smem_layout_sf` and
`make_smem_layout_sfa` helpers were restored. Fixing this conflict through a
TMA-side transpose would require a supported canonical descriptor mapping, not
an ad hoc scale atom.

Evidence:
`logs/w4a16_scale_atom_transpose_probe_20260722_135953/run.log`.

### Interleave direct E2M1 conversion and BF16 multiply in groups of four

**Result: Rejected as noise.** The CUDA 13.2 inline PTX helper originally
converts all eight E2M1 pairs before multiplying them by the decoded E4M3
scale. Converting and multiplying four pairs at a time preserved every explicit
`.rn` operation and passed all four route/topology numerical probes.

Two full sweeps measured `1.0025x`/`1.0014x` EP8 geomean against the first
retained baseline and `1.0019x`/`1.0009x` against its repeat. TP8 was neutral at
`0.9996x`/`0.9994x` and `1.0007x`/`1.0005x`, respectively. Against the faster
retained repeat, every EP8 row was within 0.32%; the larger aggregate delta came
from the other baseline's noisy 4096-token point. The original conversion group
followed by the multiply group was restored.

Evidence:

- `logs/w4a16_decode_group4_probe_20260722_140416/run.log`
- `logs/w4a16_decode_group4_bench_20260722_140625/run.log`
- `logs/w4a16_decode_group4_repeat_20260722_140911/run.log`

### Load transform scales directly from global memory

**Result: Rejected.** NCU localized a four-way shared-memory conflict to the
transform scale load, so the transform copy was also partitioned over the
corresponding global scale tile. The first version used the TMA-adapted tensor
and failed at compilation because its internal tuple element type is not a
legal source for a SIMT `autovec_copy`. Passing the original E4M3 tensor beside
the TMA view fixed the type contract. All route/topology numerical probes then
passed.

The conservative phase retained the existing scale TMA load and readiness
pipeline, but sourced the transform registers from global memory after that
barrier. This isolates the shared replay from shared-memory capacity and
pipeline effects. It was consistently slower: `0.8936x` EP8 geomean and
`0.9333x` simulated-TP8 geomean against the retained repeat. EP8 individual
speedups ranged from `0.8549x` to `0.9469x`; TP8 ranged from `0.8882x` to
`1.0133x`, with only the noisy 4096-token point above parity. The uncoalesced
per-transform global read costs substantially more than the shared replay even
when the scale tile is already cached by TMA. The retained staged scale path was
restored. A future scale-pipeline redesign should instead preserve coalesced
global transfer and change only the shared-to-register ownership or load form.

Evidence:

- Compile failure: `logs/w4a16_direct_global_scale_probe_20260722_141829/run.log`
- Correctness: `logs/w4a16_direct_global_scale_typed_probe_20260722_142101/run.log`
- Full sweep: `logs/w4a16_direct_global_scale_bench_20260722_142214/run.log`

### Preload the complete packed-weight transform fragment

**Result: Rejected.** The transform loop normally loads one 128-bit packed
weight chunk, decodes it, and stores its BF16 result before loading the next
chunk. Because the register tensor already describes the complete transform
fragment, a two-loop version first issued every shared load and then decoded
all chunks. This passed every route/topology numerical probe and did not hang.

The larger live range did not hide enough long-scoreboard latency. Relative to
the retained repeat, the sweep measured `0.9884x` EP8 geomean and `0.9829x`
simulated-TP8 geomean. EP8 ranged from `0.9650x` to `1.0118x`; TP8 ranged from
`0.9572x` to `1.0273x`. Improvements were isolated to a few large-token rows,
while the latency-sensitive rows regressed. The full preload was replaced by a
narrower one-fragment lookahead experiment.

Evidence:

- Correctness: `logs/w4a16_packed_preload_probe_20260722_142955/run.log`
- Full sweep: `logs/w4a16_packed_preload_bench_20260722_143053/run.log`

### Look ahead by one packed-weight transform fragment

**Result: Rejected.** A narrower follow-up kept only the next 128-bit shared
load live while decoding the current packed chunk. It also advanced and peeked
the activation pipeline at the original final-fragment boundary. All four
route/topology numerical probes passed, and two complete sweeps ran without a
hang.

The first and repeat sweeps measured `1.0001x` and `1.0019x` EP8 geomean
against the faster retained baseline repeat. Against the first retained run,
they measured `1.0007x` and `1.0024x`. Per-shape results crossed parity: the
repeat ranged from `0.9979x` to `1.0197x` against the retained repeat, with the
largest apparent gain again coming from a noisier large-token point. TP8 was
similarly neutral at `1.0024x` and `1.0018x` geomean. This does not establish a
repeatable EP8 win large enough to justify the additional loop state and live
range, so the serial load/decode/store order was restored.

Evidence:

- Correctness: `logs/w4a16_packed_lookahead_probe_20260722_143646/run.log`
- First sweep: `logs/w4a16_packed_lookahead_bench_20260722_143746/run.log`
- Repeat: `logs/w4a16_packed_lookahead_repeat_20260722_144041/run.log`

### Restrict the TMEM allocation barrier to TMEM consumers

**Result: Rejected.** The original W4A16 kernel allocates TMEM and waits on a
CTA-wide named barrier before any role-specific work. Only the four epilogue
warps, four transform warps, and MMA warp retrieve TMEM, so this experiment
reduced the barrier to those nine warps. Scheduler and static
activation/weight/scale TMA roles could then proceed without waiting for TMEM.

The supported form mirrored the W4A4 kernel: allocation occurred in the
epilogue branch, while each TMEM-consuming role waited before retrieving the
pointer. All route/topology probes passed. Two sweeps measured `1.0032x` and
`1.0023x` EP8 geomean against the faster retained baseline repeat, but the
latency-sensitive 1-token row consistently regressed by about 2.5%. Simulated
TP8 measured `0.9995x` and `0.9966x`. This is too small and uneven to retain.

Moving allocation globally before the role branches while keeping role-local
waits recovered the 1-token row, but every warp still executed the allocator
helper's internal allocator-warp predicate. It measured `0.9985x` EP8 and
`1.0025x` simulated-TP8 geomean against the retained repeat, including roughly
2% EP8 regressions at 128 and 256 tokens. A final attempt wrapped allocation in
an explicit epilogue-warp predicate. CuTe DSL rejected it because the allocator
object's compile-time column bookkeeping did not escape the dynamic region;
`free()` was generated with zero columns. This is an allocator API constraint,
not a runtime hang. The original CTA-wide allocation and wait were restored.

Evidence:

- Role-local correctness: `logs/w4a16_tmem_alloc_probe_20260722_145152/run.log`
- Role-local sweeps: `logs/w4a16_tmem_alloc_bench_20260722_145310/run.log`,
  `logs/w4a16_tmem_alloc_repeat_20260722_145544/run.log`
- Global-allocation correctness:
  `logs/w4a16_tmem_alloc_early_probe_20260722_150000/run.log`
- Global-allocation sweep:
  `logs/w4a16_tmem_alloc_early_bench_20260722_150049/run.log`
- Predicated-allocation compile failure:
  `logs/w4a16_tmem_alloc_epiw0_probe_20260722_150600/run.log`

### Release each scale stage after its shared-to-register copy

**Result: Rejected.** The transform warpgroup copies every E4M3 scale for the
current K tile into registers before decoding packed weights, but the original
pipeline holds that scale stage until the transformed BF16 tile has been
stored. Releasing the scale stage immediately after the synchronous register
copy passed all route/topology numerical probes and did not hang.

The complete sweep measured `1.0002x` to `1.0007x` EP8 geomean against the two
retained packed-weight-cache runs, while simulated TP8 measured `0.9958x` to
`0.9948x`. EP8 at 128, 256, 1024, and 2048 tokens regressed. The retained
six-stage scale pipeline already provides enough independent slots; shortening
the consumer lifetime does not improve the producer-consumer critical path.
The original release point was restored.

Evidence:

- Correctness: `logs/w4a16_scale_early_release_probe_20260722_151054/run.log`
- Full sweep: `logs/w4a16_scale_early_release_bench_20260722_151223/run.log`

### Release each packed-weight stage after its final fragment load

**Result: Rejected.** The original transform holds a packed-weight stage until
the complete transformed tile has been written to TMEM. A first lifetime
experiment released the stage inside the final decode iteration, immediately
after each transform warp loaded its last packed fragment. It passed all
route/topology correctness probes without hanging.

The additional consumer-group release on the innermost path was expensive.
EP8 measured `0.9633x` to `0.9638x` geomean against the retained runs, with a
`0.9206x` minimum at 2048 tokens. Simulated TP8 measured `0.9753x` to
`0.9764x`. The in-loop form was removed. A narrower follow-up moves the
existing release only across the transformed-A store, after the decode loop,
so it does not add a final-iteration predicate.

Evidence:

- Correctness: `logs/w4a16_weight_early_release_probe_20260722_151749/run.log`
- Full sweep: `logs/w4a16_weight_early_release_bench_20260722_151851/run.log`

### Release each packed-weight stage before the transformed-A store

**Result: Rejected.** To avoid the in-loop predicate above, the existing
packed-weight release was moved only across the transformed-A TMEM store. The
stage remained live through every decode, and the release still occurred once
per K tile. All route/topology probes passed without a hang.

This tradeoff favored simulated TP8 but not the target workload. EP8 measured
`0.9958x` to `0.9963x` geomean against the retained runs, including consistent
regressions at 128, 256, 1024, and 2048 tokens. Simulated TP8 measured
`1.0032x` to `1.0043x`. Because EP8 is the optimization priority, the original
post-store release order was restored.

Evidence:

- Correctness:
  `logs/w4a16_weight_release_before_store_probe_20260722_152323/run.log`
- Full sweep:
  `logs/w4a16_weight_release_before_store_bench_20260722_152411/run.log`

### Traverse routed N tiles before output M tiles

**Result: Rejected.** W4A16 originally relies on CUTLASS's default M-fast
persistent scheduler, while the existing W4A4 grouped MoE explicitly selects
N-fast traversal. N-fast traversal can reuse one packed weight and scale tile
across routed-token tiles before advancing output rows. The one-argument change
passed all route/topology numerical probes and two complete sweeps.

The scheduling orders were indistinguishable for this workload. Across both
candidate and both retained runs, EP8 geomeans ranged from `0.9995x` to
`1.0014x`; simulated TP8 ranged from `0.9998x` to `1.0019x`. Individual
outliers did not reproduce between repeats. The default M-fast order was
restored; a future scheduler experiment must change locality more materially,
for example through bounded cluster swizzling rather than only transposing the
linear traversal.

Evidence:

- Correctness: `logs/w4a16_raster_n_probe_20260722_153035/run.log`
- First sweep: `logs/w4a16_raster_n_bench_20260722_153133/run.log`
- Repeat: `logs/w4a16_raster_n_repeat_20260722_153424/run.log`

### Swizzle two routed N clusters within each output M block

**Result: Rejected.** CUTLASS's `swizzle_size=2` scheduler alternates two
routed-N clusters within each output-M block, providing bounded packed-weight
reuse without globally transposing the traversal. It passed all route/topology
probes. Nontrivial swizzling also disables the scheduler's fast-divmod path and
pads the swizzled dimension.

The locality did not recover those costs. EP8 measured `0.9991x` to `0.9996x`
geomean against the retained runs, with no consistent shape-level gain and a
large-token regression. Simulated TP8 measured `1.0013x` to `1.0023x`, below
the threshold for adding scheduler complexity. Swizzle size one was restored;
swizzle size four was not compiled because it would increase padding and retain
the same non-fast-divmod coordinate path without evidence of a useful trend.

Evidence:

- Correctness: `logs/w4a16_swizzle2_probe_20260722_153906/run.log`
- Full sweep: `logs/w4a16_swizzle2_bench_20260722_154000/run.log`

### Add route tile 256 to autotuning

**Result: Rejected.** W4A4 supports a 256-row sort/MMA tile, and the W4A16
sort workspace can represent the same route size. Route 256 was therefore
added as an autotune-only candidate to test whether dense EP8 rows benefit
from fewer persistent-scheduler tiles. Nine route-256 tactic combinations
compiled and ran. Three combinations containing the largest K=256 mixed
topology were rejected because the resulting fused GEMM exceeded SMEM or TMEM
capacity.

No route-256 tactic won a measured shape. The complete sweep was neutral
against both retained baselines: EP8 geomean ranged from `0.9995x` to
`1.0001x`, and simulated TP8 from `1.0012x` to `1.0023x`. The apparent EP8
4096-token gain against the first baseline disappeared against its repeat.
Keeping route 256 would therefore increase autotuning and compilation work
without changing the selected kernels, so the route list was restored.

Evidence:

- Full sweep: `logs/w4a16_route256_bench_20260722_154927/run.log`
- Debug tactic trace: `logs/w4a16_route256_debug_20260722_155232/run.log`

Workflow for this and later aggressive pipeline experiments:

1. Derive the expected generated address or instruction change before editing.
2. Run `pre-commit run --all-files`, sync, reinstall editable FlashInfer, and
   record `show-config` plus detailed module status.
3. Probe every selected W4A16 route/topology family with command-traced logs.
   While JIT is expected to use CPU heavily, treat sustained GPU saturation
   after compiler activity ends as a possible kernel hang and terminate early.
4. Only after correctness, run the exact 1-4096-token EP8 and simulated-TP8
   `bench_moe_deepseek.py` sweep. Prefer EP8 when a repeatable tradeoff is
   required, while recording any TP8 regression explicitly.
5. Use NCU, NSYS, emitted IR, and PTX to confirm that the intended hardware
   behavior changed. Retain only repeatable wins or clean structural changes;
   document and restore rejected candidates.
6. Pull every test, benchmark, and profile log into the local `logs/` tree.

### Increase the tile-info pipeline from two to four stages

The scheduler publishes four integers and one pair of pipeline barriers per
tile-info stage. Increasing the depth from two to four costs only 48 additional
shared-memory bytes and lets it run farther ahead of W4A16's longer
weight-scale transform pipeline. The route/topology numerical matrix passed all
four launch families without hanging.

Two complete benchmark sweeps showed a repeatable simulated-TP8 improvement:
`1.0222x`-`1.0247x` geomean against the two retained baselines, with the clearest
gains from 32 through 2048 tokens. EP8, however, ranged from `0.9993x` to
`0.9950x` geomean and therefore did not improve the prioritized execution mode.
The four-stage setting was rejected. A three-stage follow-up is evaluated
separately to determine whether a smaller scheduling window keeps the TP8
benefit without the EP8 cost.

Evidence:

- Correctness: `logs/w4a16_tile_info4_test_20260722_160027/run.log`
- First sweep: `logs/w4a16_tile_info4_bench_20260722_160106/run.log`
- Repeat sweep: `logs/w4a16_tile_info4_repeat_20260722_160353/run.log`

### Increase the tile-info pipeline from two to three stages

The intermediate three-stage depth also passed the four route/topology
correctness cases. It did not interpolate between the two- and four-stage
results: EP8 regressed to `0.9786x`-`0.9791x` geomean, including an approximately
`8%` worst-point regression, while simulated TP8 improved by only
`1.0118x`-`1.0129x`. This confirms that the established two-stage tile-info
pipeline is the right EP8 default. The source was restored to two stages.

Evidence:

- Correctness: `logs/w4a16_tile_info3_test_20260722_160736/run.log`
- Full sweep: `logs/w4a16_tile_info3_bench_20260722_160815/run.log`

## Current Validation

The final tactic search and route-8 boundary passed:

```bash
CUDA_VISIBLE_DEVICES=0 FLASHINFER_DISABLE_VERSION_CHECK=1 \
python3 -m pytest -q \
  tests/moe/test_cute_dsl_fused_moe.py::TestTacticEnumeration::test_w4a16_tactics_cover_launch_axes \
  tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16
```

Result: `13 passed, 301 warnings in 6.11s`.

Evidence: `logs/w4a16_tactic_validation_20260722_074348/run.log`.

`pre-commit run --all-files` also passed after the final edits.

## Practical Conclusions

1. Online decode is important, but the dedicated block helper already captures
   the useful instruction-level gain. Broader packed forms did not establish a
   better end-to-end result.
2. Sparse route granularity matters more than adding many GEMM topology pairs.
   Route 8/16 produced a clear 1.0215x EP8 and 1.0416x simulated-TP8 geomean
   improvement while the reverse topology and mixed-K expansion were negligible.
3. The weight path should start as early as dependencies permit, but moving the
   host/device PDL release point or activation pipeline acquisition earlier is
   not automatically beneficial. Register pressure and synchronization remain
   first-order constraints.
4. Fused activation is valuable when it removes global-memory traffic in the
   GEMM epilogue. A separate vectorized activation kernel did not help.
5. Applying the FP32 weight scale in the accumulator epilogue is both faster and
   avoids an additional BF16 rounding point compared with full prologue scaling.
6. Autotune spaces should contain materially distinct, valid pipeline choices.
   Exhaustive topology/K Cartesian products, K=512, irregular route tiles, and
   sub-percent topology variants made tuning slower without meaningful runtime
   benefit.
7. W4A8 needs a fundamentally cheaper online weight conversion pipeline before
   it is worth reviving; launch and loading adjustments alone did not close the
   gap.

## Post-merge A/scale Pipeline Experiments

### Account for E4M3 scale bytes at their physical width

**Result: Rejected.** After merging the packed NVFP4 weights and E4M3 scales
onto one TMA transaction barrier, the stage-capacity calculation was changed to
charge scale storage as E4M3 bytes instead of the widened BF16 MMA operand type.
The four route/topology numerical cases passed. The extra nominal stage
capacity did not produce a repeatable runtime win.

Against the two retained merged-pipeline sweeps, EP8 measured `0.9953x` and
`0.9990x` geomean, while simulated TP8 measured `0.9967x` and `0.9962x`.
The isolated EP8 4096-token improvement against one repetition did not appear
against the other, and the 1-token EP8 case regressed by roughly `2.6%` in both
comparisons. The conservative widened-type accounting was restored.

Evidence:

- Correctness: `logs/w4a16_scale_actual_test_20260722_171230/run.log`
- Full sweep: `logs/w4a16_scale_actual_bench_20260722_171448/run.log`

### Keep transform scale fragments compact

**Result: Retained.** The transform partition broadcasts each E4M3 block scale
over the 16 corresponding FP4 values. Loading that logical view caused the
decode helper to extract the unique bytes from a large broadcast vector. For a
64-value transform fragment, generated PTX unpacked one scale word with four
`prmt.b32` and four `cvt.u16.u32` instructions before entering the independent
per-block decode helpers.

The kernel now filters the zero-stride broadcast modes before loading the scale
fragment. The decode helper keeps each four-byte group packed as `Uint32` and
selects later scales with shifts while retaining one explicit `.rn` PTX decode
helper per NVFP4 block. This preserves the scheduler freedom that the rejected
monolithic packed-scale helper lost.

Two full EP8 and simulated-TP8 sweeps reproduced the improvement against both
merged-pipeline baselines:

| Candidate | Configuration | Geomean range | Minimum range | Maximum range |
|---|---|---:|---:|---:|
| first | EP8 | `1.0168x`-`1.0206x` | `1.0022x`-`1.0040x` | `1.0350x`-`1.0583x` |
| repeat | EP8 | `1.0147x`-`1.0184x` | `1.0007x`-`1.0029x` | `1.0229x`-`1.0513x` |
| first | simulated TP8 | `1.0042x`-`1.0047x` | `0.9881x`-`0.9974x` | `1.0107x`-`1.0111x` |
| repeat | simulated TP8 | `1.0049x`-`1.0054x` | `0.9885x`-`0.9978x` | `1.0099x`-`1.0103x` |

Every EP8 point was faster than both retained baselines. Fixed route-32 PTX
removes all four `prmt.b32` and four `cvt.u16.u32` scale-unpack instructions,
adds three `shr.u32` instructions, and reduces PTX size from 85,216 to 84,888
bytes without changing shared-load or E4M3 conversion counts. The full W4A16
test class passed all 12 cases.

Evidence:

- Initial correctness: `logs/w4a16_compact_scale_test_20260722_172706/run.log`
- First sweep: `logs/w4a16_compact_scale_bench_20260722_172731/run.log`
- Repeat sweep: `logs/w4a16_compact_scale_repeat_20260722_172952/run.log`
- Generated PTX: `logs/w4a16_compact_scale_ir_ptx_20260722_173158/`
- Full tests: `logs/w4a16_compact_scale_full_test_20260722_173234/run.log`

### Replace conflicting scale-word loads with redundant vector loads

**Result: Rejected.** NCU reports 458,752 and 688,128 excess shared-memory
wavefronts in the retained GEMM1 and GEMM2 kernels. Generated PTX showed that
each transform warp loaded a scale word at `16 * lane + 4 * transform_warp`, a
four-way bank-replay pattern. The experiment bypassed register staging and let
each lane load the aligned 16-byte group at `16 * lane` with
`ld.shared.v4.u32`, then select the word containing its scale bytes. This
trades replayed scalar loads for redundant vector traffic.

The first version exposed two useful implementation constraints. Directly
tiling the shared scale view must preserve its nested K coordinate; otherwise
CuTe rejects the slice as weakly incongruent. Also, deriving the aligned base
from a transform-warp index produced a misaligned-address fault. Aligning the
actual shared pointer down to 16 bytes and deriving the selected word from its
low address bits was robust across the route/topology cases. The focused test
then passed all four cases.

The complete 1-4096-token sweep was a clear regression against both retained
compact-scale runs:

| Baseline | Configuration | Geomean | Minimum | Maximum |
|---|---|---:|---:|---:|
| first compact-scale run | EP8 | `0.9680x` | `0.9553x` | `0.9987x` |
| repeat compact-scale run | EP8 | `0.9700x` | `0.9568x` | `0.9868x` |
| first compact-scale run | simulated TP8 | `0.9833x` | `0.9591x` | `1.0115x` |
| repeat compact-scale run | simulated TP8 | `0.9826x` | `0.9584x` | `1.0111x` |

The additional shared bytes, registers, and per-word selection cost more than
the scalar replay. The source was restored to the retained compact scalar-load
design without running NCU on the losing candidate.

Evidence:

- Initial coordinate failure: `logs/w4a16_vector_scale_test_20260722_104401/run.log`
- Scalar-index pointer failure: `logs/w4a16_vector_scale_test2_20260722_104617/run.log`
- Misaligned vector-load failure: `logs/w4a16_vector_scale_test3_20260722_104816/run.log`
- Partial topology pass and route-32 rank collapse: `logs/w4a16_vector_scale_test4_20260722_105151/run.log`
- Focused correctness: `logs/w4a16_vector_scale_test5_20260722_105347/run.log`
- Full sweep: `logs/w4a16_vector_scale_bench_20260722_105423/run.log`
- Generated PTX: `logs/w4a16_vector_scale_ptx_20260722_104856/`

### Overlap TMEM allocation with the initial producer work

**Result: Rejected.** W4A16 previously made all 12 warps wait for TMEM
allocation before tile scheduling or either TMA producer could start. The W4A4
kernels instead start allocation from the allocator warp and restrict the
retrieval barrier to roles that consume TMEM. The experiment mirrored that
ownership: the four epilogue warps, MMA warp, and four transform warps joined a
nine-warp retrieval barrier, while the scheduler and two TMA warps could run
without waiting for the TMEM pointer.

All four route/topology numerical cases passed without hanging. The complete
1-4096-token sweep did not show a repeatable gain against the two retained
compact-scale runs:

| Baseline | Configuration | Geomean | Minimum | Maximum |
|---|---|---:|---:|---:|
| first compact-scale run | EP8 | `0.9983x` | `0.9788x` | `1.0150x` |
| repeat compact-scale run | EP8 | `1.0004x` | `0.9894x` | `1.0165x` |
| first compact-scale run | simulated TP8 | `0.9991x` | `0.9951x` | `1.0018x` |
| repeat compact-scale run | simulated TP8 | `0.9984x` | `0.9958x` | `1.0009x` |

The allocator latency is therefore already hidden by pipeline initialization
and launch setup, or is too small to affect end-to-end kernel time. The simpler
CTA-wide allocation barrier was restored.

Evidence:

- Correctness: `logs/w4a16_tmem_overlap_test_20260722_180456/run.log`
- Full sweep: `logs/w4a16_tmem_overlap_bench_20260722_180535/run.log`
- GPU watchdog: `logs/w4a16_tmem_overlap_bench_20260722_180535/gpu_watch.log`

### Double the generic TMEM transform-store repetition

**Result: Rejected.** The generic TMEM-to-register transform path uses four
`tcgen05.st.32x32b.x8` instructions per warp. Replacing those with two
`.x16` stores preserved the specialized one-CTA K=64 path, passed all four
route/topology numerical probes, removed every `.x8` from the fixed-route PTX,
and reduced that PTX from 84,888 to 84,077 bytes.

The full 1-4096-token sweep was not a net win. Against the two retained
compact-scale runs, EP8 geomean was `0.9950x` and `0.9971x`; simulated TP8 was
`1.0004x` and `0.9997x`. EP8 improved by roughly 0.7-1.1% at 8-256 tokens but
regressed by 2.4-3.0% at 1-4 tokens and by up to 1.8% at 512-4096 tokens.

Autotuner diagnostics ruled out a clean tactic split. The same two-CTA
topologies select both winning and losing rows: route-8/16 tactics cover the
latency-sensitive regressions as well as the 8-256-token gains, while all
larger route tiles regress. Adding an `.x8`/`.x16` code-generation axis would
double this portion of the tactic space for a noisy sub-1% aggregate effect,
so the original `.x8` copy atom was restored.

Evidence:

- Correctness: `logs/w4a16_tmem_store_x16_test_20260722_181106/run.log`
- Generated PTX: `logs/w4a16_tmem_store_x16_ptx_20260722_181138/`
- Full sweep: `logs/w4a16_tmem_store_x16_bench_20260722_181157/run.log`
- Autotuner diagnostics:
  `logs/w4a16_tmem_store_x16_tactics_20260722_181531/run.log`

### Raise the MMA controller warp to 128 registers

**Result: Rejected due to a kernel stall.** NCU reported 46-51% of cycles with
no eligible warp in the retained 128-token kernels, while the 12-warp role
budget appeared to leave room above the MMA controller's 96-register
allocation. Raising only that warp to 128 registers compiled, but the first
route/topology numerical case entered a persistent GPU kernel: GPU 0 remained
at 100% utilization for more than 70 seconds, memory stayed at 750 MiB, and
pytest made no progress. The process was terminated rather than waiting for the
five-minute timeout. This is consistent with the prior transform-register
stalls and shows that the nominal CTA register sum is not a sufficient safety
test for the dynamic `setmaxnreg` exchange.

Evidence:

- Install and module state:
  `logs/w4a16_mma_regs128_setup_20260722_182044/run.log`
- Stalled test and watchdog:
  `logs/w4a16_mma_regs128_test_20260722_182140/`

A narrower 112-register follow-up produced the same persistent first-kernel
stall and was also terminated after the watchdog confirmed continuous 100% GPU
utilization without test progress.

- 112-register install:
  `logs/w4a16_mma_regs112_setup_20260722_182436/run.log`
- 112-register stalled test:
  `logs/w4a16_mma_regs112_test_20260722_182514/`

The smallest valid step, 104 registers, passed all four numerical probes but
did not improve the target workload. Against the two retained compact-scale
runs, EP8 geomean was `0.9978x` and `0.9999x`; the 1-token row regressed by
2.4-2.5%. Simulated TP8 improved by `1.0077x` and `1.0070x`, but that does not
justify moving closer to the demonstrated stall boundary while leaving EP8
unchanged. The original 96-register controller allocation was restored.

| Baseline | Configuration | Geomean | Minimum | Maximum |
|---|---|---:|---:|---:|
| first compact-scale run | EP8 | `0.9978x` | `0.9759x` | `1.0119x` |
| repeat compact-scale run | EP8 | `0.9999x` | `0.9751x` | `1.0089x` |
| first compact-scale run | simulated TP8 | `1.0077x` | `1.0006x` | `1.0226x` |
| repeat compact-scale run | simulated TP8 | `1.0070x` | `0.9986x` | `1.0233x` |

Evidence:

- 104-register install:
  `logs/w4a16_mma_regs104_setup_20260722_182738/run.log`
- 104-register correctness:
  `logs/w4a16_mma_regs104_test_20260722_182822/run.log`
- 104-register full sweep:
  `logs/w4a16_mma_regs104_bench_20260722_182849/run.log`

### Add a third routed-tile metadata stage

**Result: Retained.** Every non-scheduler warp role consumes the persistent
scheduler's routed-tile metadata. With two stages, the scheduler can fill only
the tile being processed and one following tile before waiting for the slowest
consumer to release a slot. A third stage lets it keep one additional routed
tile ready while the load, transform, MMA, and epilogue pipelines consume the
older stages. The extra stage costs only one four-int metadata record and one
full/empty barrier pair.

The focused route/topology numerical test passed all four cases. Two complete
1-4096-token sweeps reproduced a large simulated-TP8 improvement while leaving
the primary EP8 workload neutral to slightly faster:

| Candidate | Baseline | Configuration | Geomean | Minimum | Maximum |
|---|---|---|---:|---:|---:|
| first | first compact-scale run | EP8 | `1.0018x` | `0.9882x` | `1.0148x` |
| first | repeat compact-scale run | EP8 | `1.0040x` | `0.9940x` | `1.0149x` |
| repeat | first compact-scale run | EP8 | `1.0001x` | `0.9774x` | `1.0144x` |
| repeat | repeat compact-scale run | EP8 | `1.0022x` | `0.9920x` | `1.0100x` |
| first | first compact-scale run | simulated TP8 | `1.0354x` | `1.0071x` | `1.0524x` |
| first | repeat compact-scale run | simulated TP8 | `1.0346x` | `1.0064x` | `1.0495x` |
| repeat | first compact-scale run | simulated TP8 | `1.0328x` | `0.9981x` | `1.0566x` |
| repeat | repeat compact-scale run | simulated TP8 | `1.0321x` | `0.9976x` | `1.0537x` |

The improvement is especially relevant to TP-style shapes, where smaller
expert intermediate dimensions increase the relative persistent-scheduler and
metadata handoff cost. EP8 remains the primary retention criterion and showed
no repeatable aggregate regression.

Evidence:

- Install and module state:
  `logs/w4a16_tile_info_stage3_setup_20260722_183743/run.log`
- Focused correctness:
  `logs/w4a16_tile_info_stage3_test_20260722_183826/run.log`
- First full sweep:
  `logs/w4a16_tile_info_stage3_bench_20260722_183848/run.log`
- Repeat full sweep:
  `logs/w4a16_tile_info_stage3_repeat_20260722_184250/run.log`
- Full W4A16 test class (12 passed):
  `logs/w4a16_tile_info_stage3_full_test_20260722_184555/run.log`
- NCU report with CUDA/SASS correlation:
  `logs/w4a16_tile_info_stage3_ncu_ep8_128_20260722_184716/`

### Add a fourth routed-tile metadata stage

**Result: Rejected.** A fourth stage tested whether more scheduler lookahead
could extend the three-stage gain. It passed all four route/topology numerical
cases, but did not improve the primary EP8 workload and substantially regressed
several simulated-TP8 rows:

| Baseline | Configuration | Geomean | Minimum | Maximum |
|---|---|---:|---:|---:|
| first three-stage run | EP8 | `0.9979x` | `0.9764x` | `1.0055x` |
| repeat three-stage run | EP8 | `0.9996x` | `0.9746x` | `1.0074x` |
| first three-stage run | simulated TP8 | `0.9828x` | `0.9318x` | `1.0192x` |
| repeat three-stage run | simulated TP8 | `0.9853x` | `0.9297x` | `1.0151x` |

The 32-128-token TP rows regressed by 4.6-7.0%, showing that extra lookahead
beyond three stages adds pipeline overhead without useful overlap. The source
was restored to three stages.

Evidence:

- Install and module state:
  `logs/w4a16_tile_info_stage4_setup_20260722_185054/run.log`
- Focused correctness:
  `logs/w4a16_tile_info_stage4_test_20260722_185135/run.log`
- Full sweep:
  `logs/w4a16_tile_info_stage4_bench_20260722_185200/run.log`

### Prefetch the accumulator barrier before epilogue address setup

**Result: Rejected.** The epilogue issued `consumer_try_wait` for the current
accumulator stage before loading the expert scale and constructing output
addresses, then supplied the returned status to the blocking wait. This was
intended to overlap barrier polling with required per-tile setup. All four
route/topology numerical cases passed.

The full sweep was effectively noise on EP8 and mildly negative on simulated
TP8. Against the two retained three-stage runs, EP8 geomean was `1.0005x` and
`1.0022x`; simulated TP8 was `0.9964x` and `0.9989x`. The extra probe helped
the 4-8-token EP8 rows by about 0.7-1.6%, but the effect did not generalize and
the 2-token row was noisy. The original single blocking accumulator wait was
restored.

Evidence:

- Install and module state:
  `logs/w4a16_acc_trywait_setup_20260722_185730/run.log`
- Focused correctness:
  `logs/w4a16_acc_trywait_test_20260722_185808/run.log`
- Full sweep:
  `logs/w4a16_acc_trywait_bench_20260722_185827/run.log`

### Trade one narrow accumulator stage for transformed-A lookahead

**Result: Retained after narrowing the policy.** NCU source correlation showed
the epilogue blocked most often on the accumulator pipeline while the transform
and weight producers also accumulated long-scoreboard stalls. The original
TMEM policy reserved three accumulator stages when one stage used fewer than
128 columns, two stages below 256 columns, and one stage otherwise. Reducing
every configuration by one stage confirmed that extra transformed-A capacity
could help, but it also collapsed the existing two-stage configuration to one
and regressed the 4096-token EP8 row by about 7%.

The retained policy uses two accumulator stages for every configuration below
256 columns and preserves one stage for the wide case. This changes only the
previously three-stage configuration. Two complete 1-4096-token sweeps
reproduced the primary larger-shape gains against the two retained three-stage
metadata baselines:

| Configuration | Geomean | Minimum | Maximum | 1024 tokens | 2048 tokens | 4096 tokens |
|---|---:|---:|---:|---:|---:|---:|
| EP8 | `1.0033x` | `0.9922x` | `1.0265x` | `1.0265x` | `1.0185x` | `1.0036x` |
| simulated TP8 | `0.9994x` | `0.9928x` | `1.0034x` | `0.9992x` | `0.9971x` | `0.9990x` |

The small EP8 rows are mostly neutral; 64, 128, and 512 tokens regress by
0.6-0.8%, while the 1024-4096-token region improves. This is an acceptable
trade for the EP8-focused workload and avoids adding another autotune axis to
an already large tactic space. All 12 W4A16 tests pass with the retained rule.

Evidence:

- Broad decrement correctness:
  `logs/w4a16_reduced_acc_stages_test_20260722_190311/run.log`
- Broad decrement full sweep:
  `logs/w4a16_reduced_acc_stages_bench_20260722_190328/run.log`
- Retained policy install and module state:
  `logs/w4a16_acc_stage_cap2_setup_20260722_120759/run.log`
- Retained policy focused correctness:
  `logs/w4a16_acc_stage_cap2_test_20260722_120903/run.log`
- Retained policy first full sweep:
  `logs/w4a16_acc_stage_cap2_bench_20260722_120951/run.log`
- Retained policy repeat full sweep:
  `logs/w4a16_acc_stage_cap2_repeat_20260722_121216/run.log`
- Retained policy full W4A16 test class (12 passed):
  `logs/w4a16_acc_stage_cap2_full_test_20260722_121533/run.log`

The retained 2048-token EP8 NCU profile grouped the two W4A16 GEMMs at
85.25-145.50 us, with 168 registers per thread, 222.21 KiB dynamic shared
memory, 18.3% achieved occupancy, and no eligible warp on 51.2% of cycles.
Source correlation continued to place the accumulator consumer wait first,
followed by the weight-transform and activation-TMA producer/consumer waits.

- NCU report with CUDA/SASS correlation:
  `logs/w4a16_acc_stage_cap2_ncu_ep8_2048_20260722_121716/`

### Carry a nonblocking acquire across activation TMA stages

**Result: Rejected.** NCU attributed roughly 700 long-scoreboard samples across
GEMM1 and GEMM2 to the activation TMA producer's blocking stage acquire. The
experiment mirrored the weight producer by issuing `producer_try_acquire` for
the first and next activation stages and passing its status to the blocking
acquire. All four route/topology numerical cases passed.

The complete sweep regressed against the average of the two retained
accumulator-stage runs. EP8 geomean was `0.9934x` (minimum `0.9784x` at 1024
tokens), and simulated TP8 geomean was `0.9918x`. The apparent producer stall
is downstream backpressure rather than latency that can be hidden by an extra
poll; the original blocking acquire was restored.

Evidence:

- Install and module state:
  `logs/w4a16_activation_try_acquire_setup_20260722_122017/run.log`
- Focused correctness:
  `logs/w4a16_activation_try_acquire_test_20260722_122118/run.log`
- Full sweep:
  `logs/w4a16_activation_try_acquire_bench_20260722_122203/run.log`

### Release accumulators after their final TMEM load

**Result: Retained.** The W4A16 epilogue previously held each accumulator
pipeline stage until all post-load activation, scale, and output-store work had
finished. The established W4A4 epilogues release an accumulator as soon as its
last asynchronous TMEM-to-register load is fenced. W4A16 now follows the same
lifetime rule for both gated and non-gated epilogues, allowing the MMA producer
to recycle the stage while the epilogue continues processing register values.

Two complete sweeps against the average of the two retained accumulator-stage
baseline runs show a small but repeatable benefit across the primary mid-to-
large EP8 region:

| Configuration | Geomean | Minimum | Maximum | 128 tokens | 512 tokens | 2048 tokens |
|---|---:|---:|---:|---:|---:|---:|
| EP8 | `1.0008x` | `0.9907x` | `1.0052x` | `1.0052x` | `1.0045x` | `1.0033x` |
| simulated TP8 | `0.9985x` | `0.9833x` | `1.0015x` | `1.0012x` | `1.0013x` | `0.9980x` |

The aggregate effect is near the measurement floor, but the change removes an
unnecessary dependency and aligns W4A16 with the existing CuTe DSL MoE
epilogue pattern. The 2048-token NCU profile remains within profiling noise:
the two W4A16 kernels changed from 85.25/145.50 us to 85.76/145.54 us, and the
no-eligible-warp average changed from 51.21% to 51.15%. This confirms that the
optimization is a pipeline-lifetime cleanup rather than a tactic or resource-
usage change. All 12 W4A16 tests pass.

Evidence:

- Focused numerical test:
  `logs/w4a16_early_acc_release_test_20260722_122843/run.log`
- First full sweep:
  `logs/w4a16_early_acc_release_bench_20260722_122924/run.log`
- Repeat full sweep:
  `logs/w4a16_early_acc_release_repeat_20260722_123156/run.log`
- Full W4A16 test class (12 passed):
  `logs/w4a16_early_acc_release_full_test_20260722_123732/run.log`
- NCU report with source correlation:
  `logs/w4a16_early_acc_release_ncu_ep8_2048_20260722_123536/`

### Probe transformed weights and activations concurrently in the MMA warp

**Result: Rejected.** The MMA mainloop already issues a nonblocking readiness
probe for transformed weights before acquiring an accumulator stage, but waits
for the activation-B stage only after the transformed-weight wait. The
experiment mirrored W4A4's dual-probe structure by carrying independent
`consumer_try_wait` results for both operands across every K iteration. All
four route-tile/topology numerical cases passed and no kernel hung.

The additional activation probe substantially regressed the full sweep against
the average of the two retained early-accumulator-release runs:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `0.9468x` | `0.9271x` | `0.9977x` |
| simulated TP8 | `0.9790x` | `0.9379x` | `1.0046x` |

EP8 lost 4.9-7.3% from 2 through 2048 tokens. In this warp-specialized
pipeline the activation barrier is not a latency source worth polling early;
the extra control and barrier-probe instructions lengthen the MMA warp's hot
path. The original transformed-weight probe plus blocking activation wait was
restored.

Evidence:

- Install and module state:
  `logs/w4a16_dual_operand_peek_setup_20260722_124306/run.log`
- Focused numerical test:
  `logs/w4a16_dual_operand_peek_test_20260722_124416/run.log`
- Full sweep:
  `logs/w4a16_dual_operand_peek_bench_20260722_124453/run.log`

### Decode two adjacent NVFP4 scale blocks in one PTX helper

**Result: Rejected after a same-node CUPTI comparison.** The retained decoder
invokes the 16-value helper four times for each 64-value scale group. This
experiment introduced a 32-value helper that unpacked two adjacent E4M3 scales
with one `cvt.rn.bf16x2.e4m3x2`, duplicated both BF16 values, then decoded and
scaled 16 packed E2M1 pairs. The CUDA 13.0 compatibility path continued to call
the two existing 16-value helpers. Four route/topology numerical cases passed,
and no kernel hung.

The first complete sweep on the previous devbox appeared strongly positive:
EP8 geomean was `1.0389x` with every row above `1.001x`, while simulated TP8
was `1.0114x`. That result compared runs from different devbox lifetimes. The
replacement CUDA 13.2 image also initially lacked `cupti-python`, even though
`libcupti.so` was installed, causing the benchmark helper to fall back to CUDA
events. The environment was corrected with `cupti-python==13.2.0` and
`nvidia-cuda-cupti==13.2.75`, and candidate and baseline were then measured on
the same GPU and software stack.

The controlled result did not reproduce the apparent gain:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `0.9987x` | `0.9947x` | `1.0004x` |
| simulated TP8 | `1.0005x` | `0.9989x` | `1.0038x` |

EP8 regressed by 0.38% at 128 tokens, 0.18% at 2048, and 0.35% at 4096.
Packing two scale blocks into one inline-PTX region therefore reduces the
nominal E4M3 conversion count but does not shorten the kernel's critical path;
the larger register dependency region slightly hurts the primary workload.
The one-block decoder was restored.

Evidence:

- Initial compile failure and corrected focused test:
  `logs/w4a16_decode_pair_test2_20260722_135314/run.log`
- Initial cross-node full sweep:
  `logs/w4a16_decode_pair_bench_20260722_135339/run.log`
- Stable CUDA 13.2 devbox setup:
  `logs/w4a16_decode_pair_stable_setup_20260722_214013/run.log`
- CUDA-event fallback sweep, excluded from comparisons:
  `logs/w4a16_decode_pair_repeat2_20260722_214214/run.log`
- Version-aligned CUPTI Python setup:
  `logs/w4a16_cupti_python_pin_20260722_215436/run.log`
- Same-node CUPTI candidate sweep:
  `logs/w4a16_decode_pair_cupti_repeat_20260722_215510/run.log`
- Same-node CUPTI pushed-baseline sweep:
  `logs/w4a16_decode_pair_same_node_baseline_20260722_215710/run.log`

### Inspect the selected pipeline stage budget

**Result: Diagnostic only.** A compile-time probe wrapped
`Sm100W4A16GroupedGemmKernel._setup_attributes` and printed the stage and TMEM
allocation chosen for every autotune candidate at EP8/2048. The selected
tactic was route 128 with M256/N128/K256 two-CTA kernels for both GEMMs. Those
kernels already have four packed-weight/scale load stages but only two
transformed-weight TMEM stages:

```text
mma=(256, 128, 256) cluster=(2, 1)
a_load=4 a_transform=2 acc=2 tmem_acc=256 tmem_a=256
```

GEMM1 and GEMM2 differ only in their output shared-memory stages (`c=4` and
`c=2`). This rules out splitting or deepening the activation and packed-weight
TMA rings as the next optimization: transformed-A capacity and transform
throughput are the constraining side, while the retained two accumulator
stages already reflect the measured regression from reducing accumulator
buffering to one stage.

The diagnostic selected only W4A16 through `profile_backend`. The benchmark's
generic table printer then raised `KeyError: 'CuteDSL W4A4'` after tuning
because it expects the normal multi-backend row. Kernel profiling and stage
collection had completed before that reporting-only failure.

Evidence:

- `logs/w4a16_stage_budget_probe_20260722_221443/run.log`

### Split K256 online dequantization across two transform warpgroups

**Result: Rejected.** NCU source correlation showed that the four transform
warps remain on the critical path while the epilogue warpgroup is idle before
the accumulator becomes available. The experiment split each K256 transform
stage into two 128-value halves. A `tcgen05.St32x32b` x4 ownership layout
exposed a native size-two partition for both the packed input and transformed
TMEM destination. Each group decoded one half with the existing 128-value
decoder and loaded its corresponding eight compact E4M3 scales.

Several intermediate designs were useful for establishing the constraints:

- Reusing epilogue warps as the second transform group compiled and was
  accurate for a one-tile SwiGLU case, but was invalid for persistent work:
  those warps completed the whole transform loop before entering the epilogue.
  A multi-tile ReLU2 case consequently failed accuracy.
- A true second transform warpgroup in warps 12-15 required a 512-thread CTA.
  Assigning 128 registers with `setmaxregister_increase` stalled at 100% GPU;
  assigning 120 produced `CUDA_ERROR_ILLEGAL_INSTRUCTION`. CUTLASS's 16-warp
  mixed-input FMHA establishes that eight transform warps below the launch
  allocation must use `setmaxregister_decrease`; using `decrease(120)` made
  the launch healthy.
- The x4 ownership is correct for the M128/K256 gated SwiGLU topology. M256
  and non-gated ReLU2 require different TMEM/epilogue ownership and remained
  on the original x8/four-warp path for the performance measurement.

The final gated M128/K256 specialization passed all four route/topology
accuracy cases, but the complete same-node CUPTI sweep did not improve the
primary workload:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `0.9947x` | `0.9730x` | `1.0073x` |
| simulated TP8 | `0.9982x` | `0.9734x` | `1.0177x` |

EP8 improved by only 0.5-0.7% at 8, 128, 256, and 2048 tokens while losing
2.2-2.7% at 2 and 16 tokens. The extra four warps and 512-thread launch cost
more than the shortened dequantization work in this tensor-core-bound kernel,
so the 12-warp x8 transform was restored.

Evidence:

- x8/x4 layout and compile diagnostics:
  `logs/w4a16_dual_transform_probe2_20260722_222111/`,
  `logs/w4a16_dual_transform_probe3_20260722_222247/`,
  `logs/w4a16_dual_transform_layout_20260722_222509/`, and
  `logs/w4a16_dual_transform_x4_layout_20260722_222621/`
- Scale/fragment and topology diagnostics:
  `logs/w4a16_dual_transform_probe4_20260722_222914/` through
  `logs/w4a16_dual_transform_probe8_20260722_223532/`, and
  `logs/w4a16_dual_transform_layout2_20260722_223658/`
- 512-thread register-allocation failures and corrected launch:
  `logs/w4a16_transform_16warp_probe1_20260722_223849/` through
  `logs/w4a16_transform_16warp_probe4_20260722_224418/`
- Passing focused correctness:
  `logs/w4a16_transform_16warp_probe5_20260722_224537/run.log`
- Full same-node CUPTI sweep:
  `logs/w4a16_dual_transform_bench_20260722_224638/run.log`
- Same-node pushed baseline:
  `logs/w4a16_decode_pair_same_node_baseline_20260722_215710/run.log`

### Add route-160 and route-224 around the N192 optimum

**Result: Rejected.** N160 and N224 were added beside the retained N192
route tile to probe the reuse/TMEM tradeoff without changing kernel control
flow. Both M256/K128 numerical cases passed, and the full seven-case route
matrix completed without a hang.

Against the retained route-192 configuration, the complete same-node CUPTI
sweep regressed:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `0.9995x` | `0.9885x` | `1.0039x` |
| simulated TP8 | `0.9985x` | `0.9819x` | `1.0018x` |

The EP8 4096-token point lost `1.15%`, giving back the dense-shape benefit
that justified retaining N192. N160 and N224 were removed from the tactic
space and their dedicated numerical cases were dropped.

Evidence:

- Passing focused correctness:
  `logs/w4a16_route160_224_test_20260722_235005/run.log`
- Full same-node CUPTI sweep:
  `logs/w4a16_route160_224_bench_20260722_235056/run.log`
- Retained route-192 comparison:
  `logs/w4a16_route192_bench_20260722_234308/run.log`

### Profile retained route-192 and evaluate decoded-weight reuse

**Result: Diagnostic only; DSM reuse is not a viable first implementation.**
NCU profiled the retained EP8 4096-token tactic after route-192 was selected.
Both GEMMs used M256/N192/K256, cluster `(2, 1)`, 384 threads, 168 registers,
and 222.21 KiB dynamic SMEM. GEMM1 took `324.448 us` and GEMM2 took
`166.208 us`. The average kernel metrics were 64.77% compute throughput,
31.47% memory throughput, about 36.5% no-eligible cycles, and only about 0.5%
TMA-pipe activity. Route-192 also raised L2 hit rate to roughly 59.5% from the
older route-128 profile's 53.6%. This confirms that raw packed-weight traffic
is not the dominant remaining limiter.

The exact TMEM budget explains the observed optimum. At M256/N192/K256, TMEM
allocation rounds the 192-column FP32 accumulator fragment to 256 columns.
Only one accumulator stage fits beside two 128-column decoded-BF16 weight
stages, consuming all 512 TMEM columns. The decoded tile is released after
each K tile is consumed. Reusing it across another routed-N tile in the same
CTA therefore requires another live accumulator, while retaining all decoded
K tiles for a later sequential output tile is far beyond TMEM or SMEM capacity.
The rejected route-256 overlapping-accumulator experiment is the direct
same-CTA form of this reuse: making two physical accumulators overlap the
decoded-weight region forced K128 and lost more to doubled K-tile iterations
than it saved in decoding. Plain route-256/K256 remained valid with one
accumulator stage but never won an autotuned shape.

Cross-CTA reuse through distributed shared memory is also structurally
unfavorable. PTX `tcgen05.mma` shared-memory descriptors address the current
CTA's shared memory. A producer CTA cannot make remote DSM directly consumable
by another CTA's MMA; it must copy the expanded BF16 tile into each consumer's
local SMEM and synchronize publication. That moves four times as many bytes as
the packed NVFP4 representation and recreates the transformed-A SMEM pipeline
that measured only `0.7928x` EP8 and `0.8277x` simulated TP8. CUTLASS's DSM
examples use remote shared stores for reductions, while its Blackwell GEMMs
multicast the compact source operands and transform independently. The prior
cluster-N2 W4A16 experiment followed that pattern and was neutral to negative
because it still duplicated conversion work.

Other cache forms have the same contract cost. Predecoding all weights into a
persistent BF16 cache multiplies weight storage and traffic by four and needs
explicit invalidation for online RL weight updates. A per-call workspace adds
a launch and global-memory round trip. Neither preserves the memory advantage
or update semantics of online W4A16.

Evidence:

- NCU report with source and line information:
  `logs/w4a16_route192_ncu_ep8_4096_20260723_000430/reports/ep_w4a16_t4096.ncu-rep`
- NCU metric export:
  `logs/w4a16_route192_ncu_ep8_4096_20260723_000430/reports/details.txt`
- Exact stage-allocation probe:
  `logs/w4a16_route192_stage_probe_20260723_001125/run.log`
- Full retained route-192 sweep:
  `logs/w4a16_route192_bench_20260722_234308/run.log`
- Prior transformed-A SMEM experiment:
  `logs/w4a16_smem_transform_bench_20260722_230413/run.log`
- NVIDIA PTX ISA: `tcgen05.mma` shared-memory operand descriptors refer to
  shared memory in the current CTA.
- CUTLASS references: `examples/python/CuTeDSL/blackwell/reduce.py` for DSM
  remote stores, and examples 72a/92 for Blackwell clustered GEMM multicast.

### Pack the route-192 accumulator without allocation rounding

**Result: Rejected.** The generic TMEM sizing helper rounds the route-192
accumulator fragment from 192 physical columns to 256 columns. This experiment
kept the existing one-stage accumulator policy but placed transformed weights
immediately after the 192 physical columns. K128 then gained a fifth decoded
stage instead of four, and K64 gained ten instead of eight; K256 remained
double-buffered. All other route widths retained their existing rounded
allocation policy.

The first broad implementation exposed that the unrounded helper rejects
route-8's eight-column fragment because a standalone TMEM allocation must be
at least 32 columns. The experiment was narrowed to route-192, after which all
five route/topology numerical cases passed. The full same-node CUPTI sweep did
not produce a performance win:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `0.9983x` | `0.9853x` | `1.0006x` |
| simulated TP8 | `0.9993x` | `0.9816x` | `1.0128x` |

EP8 regressed by 1.47% at 2048 tokens, and no candidate changed the selected
schedule consistently enough to justify special physical-column accounting.
The rounded layout was restored.

Evidence:

- Initial helper-boundary failure:
  `logs/w4a16_tmem_pack_test_20260723_001543/run.log`
- Passing narrowed numerical matrix:
  `logs/w4a16_tmem_pack_test2_20260723_001725/run.log`
- Full EP8 and simulated-TP8 sweep:
  `logs/w4a16_tmem_pack_bench_20260723_001802/run.log`
- Retained route-192 baseline:
  `logs/w4a16_route192_bench_20260722_234308/run.log`

### Add route-192 to W4A16 autotuning

**Result: Retained.** N192 is already a supported Blackwell MMA/layout size
in the W4A4 kernels. For W4A16 it increases transformed-weight reuse by 1.5x
over N128 without requiring the partially overlapping accumulator contract
needed by N256. The implementation only extends the autotune route-tile axis
and adds a focused M256/K128 numerical case; the kernel itself remains
generic.

The five-case route/topology numerical matrix passed. In the complete
same-node CUPTI sweep, EP8 was neutral overall but improved at the densest
point, while simulated TP8 regressed at the two largest points:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `1.0002x` | `0.9935x` | `1.0043x` |
| simulated TP8 | `0.9983x` | `0.9787x` | `1.0101x` |

The debug tuner run provides the retention signal hidden by end-to-end
overhead. At the EP8 4096-token profile, route-192/M256/K256 for both GEMMs
measured `0.4350 ms` and was selected, while the equivalent route-128 tactic
measured `0.4774 ms`. That is a `1.0975x` improvement for the profiled MoE
operation and a measured `1.0043x` end-to-end benchmark improvement at the
same shape. EP8 is the optimization priority, so the small dense TP8
regression is accepted.

Evidence:

- Passing focused correctness:
  `logs/w4a16_route192_test_20260722_234235/run.log`
- Full same-node CUPTI sweep:
  `logs/w4a16_route192_bench_20260722_234308/run.log`
- Selected-tactic and per-tactic timings:
  `logs/w4a16_route192_debug_20260722_234605/run.log`
- Same-node pushed baseline:
  `logs/w4a16_decode_pair_same_node_baseline_20260722_215710/run.log`

### Partially overlap route-256 accumulator stages

**Result: Rejected.** Route tiles of 256 can reuse each transformed weight
tile across twice as many routed rows, but a full second FP32 accumulator
stage leaves no TMEM for double-buffered transformed BF16 weights. This
experiment adapted W4A4's overlapping-accumulator design to W4A16 for K64
and K128 tactics:

- Two physical N256 accumulator windows shared exactly two transformed-weight
  stages' worth of TMEM columns.
- A one-stage accumulator barrier alternated the physical windows by phase.
  This is required for correctness: a two-stage barrier would allow the MMA
  warp to overwrite the shared columns before the epilogue consumed them.
- The epilogue traversed stage 0 in reverse and stage 1 forward, then released
  the barrier immediately after loading the exact overlap region.
- K256 remained unsupported because its transformed-weight footprint leaves
  no useful partial second accumulator window.

The focused route/topology matrix passed all five numerical cases, including
route-256/M256/K128, without a hang. The complete same-node CUPTI sweep did
not improve aggregate performance:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `0.9979x` | `0.9647x` | `1.0152x` |
| simulated TP8 | `0.9975x` | `0.9691x` | `1.0032x` |

Debug-level tuning at 4096 tokens showed why. The best route-256 candidate,
M256/K128 for both GEMMs, measured about `0.559 ms`; the autotuner selected
route-128 M256/K256 at about `0.453 ms`. Route-256 halves the number of
weight transformations, but K128 doubles the tensor-core mainloop's K-tile
iterations and the larger routed tile reduces scheduling flexibility. The
valid route-256 tactics never won, so the extra tactic and overlap machinery
were removed.

Evidence:

- Passing focused correctness:
  `logs/w4a16_route256_overlap_test_20260722_233328/run.log`
- Full same-node CUPTI sweep:
  `logs/w4a16_route256_overlap_bench_20260722_233359/run.log`
- Selected-tactic and per-tactic timings:
  `logs/w4a16_route256_overlap_debug_20260722_233732/run.log`
- Same-node pushed baseline:
  `logs/w4a16_decode_pair_same_node_baseline_20260722_215710/run.log`

### Use weight-stationary `tcgen05.mma.ws`

**Result: Not applicable to the retained topology.** PTX ISA 9.3 exposes
BF16-capable `tcgen05.mma.ws`, but only with `.cta_group::1`. The selected
EP8 W4A16 kernels use M256 `.cta_group::2`, and PTX requires every `tcgen05`
instruction in a kernel to use the same CTA-group qualifier. Switching to
the weight-stationary instruction would therefore discard the measured
2-CTA tensor-core configuration rather than optimize it in place.

The retained SASS also shows that the compiler hoists the descriptors for all
16 K=16 slices before the `UTCHMMA.2CTA` sequence. Descriptor construction is
interleaved with asynchronously issued MMAs, not recomputed serially before
each tensor-core instruction, so there is no isolated descriptor-hoisting
change to test here.

Evidence:

- Retained M256/K256 PTX, MLIR, cubin, and SASS:
  `logs/w4a16_retained_codegen_m256k256_20260722_231310/`
- NVIDIA PTX ISA, `tcgen05.mma.ws`: only `.cta_group::1` is legal; the
  instruction is explicitly the weight-stationary convolution MMA form.

### Peek activation-load readiness from the MMA warp

**Result: Rejected.** W4A4 starts a `consumer_try_wait` for both operands
before acquiring its accumulator stage and peeks the following stages after
each MMA. W4A16 already did this for transformed weights, but used a direct
blocking wait for BF16 activations. This experiment mirrored the W4A4 B-side
schedule by carrying a prefetched full-status predicate for the activation
pipeline.

The four route/topology accuracy cases passed without a hang. The complete
same-node CUPTI sweep regressed almost uniformly:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `0.9848x` | `0.9634x` | `1.0035x` |
| simulated TP8 | `0.9947x` | `0.9887x` | `1.0024x` |

The activation TMA is normally complete before the transformed-weight path
unblocks MMA. Polling activation readiness earlier therefore adds uniform
control work without hiding a material dependency. The direct activation
wait was restored.

Evidence:

- Passing focused correctness:
  `logs/w4a16_bpeek_probe_20260722_231744/run.log`
- Full same-node CUPTI sweep:
  `logs/w4a16_bpeek_bench_20260722_231830/run.log`
- Same-node pushed baseline:
  `logs/w4a16_decode_pair_same_node_baseline_20260722_215710/run.log`

### Store transformed BF16 weights in SMEM to deepen the accumulator ring

**Result: Rejected.** The retained K-major mixed-input kernel stores decoded
BF16 weights in TMEM, which limits the selected M256/N128/K256 kernels to two
accumulator stages and two transformed-weight stages. CUTLASS also supports a
SMEM transformed-A source. This experiment forced that source so all 512 TMEM
columns could hold four accumulator stages.

The existing W4A16 transform loop had been specialized for its TMEM ownership.
Bringing up the SMEM path established the additional contracts:

- SMEM ownership gives each transform thread eight values rather than the
  64/128 values handled by the TMEM decoder. A dedicated x8 helper used the
  same explicit `.rn` E2M1/E4M3 conversions and BF16x2 multiply without
  decoding a dummy half-block.
- The compact scale fragment uses a flat `(value, subtile)` slice rather than
  the nested TMEM partition.
- All four transform warps must join a named barrier before publishing the
  shared-memory tile, matching CUTLASS's SMEM mixed-input path.
- The desired no-fused-finalize tactics cannot retain double buffering for
  both raw and transformed weights within the SM100 shared-memory capacity.
  The working variant therefore had one raw-load stage and one transformed-A
  stage, while retaining the existing output staging.

The four route/topology probes passed with no hang, including 1-CTA, 2-CTA,
SwiGLU, and ReLU2. The complete same-node CUPTI sweep was substantially slower:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `0.7928x` | `0.7429x` | `0.8461x` |
| simulated TP8 | `0.8277x` | `0.7541x` | `0.8908x` |

The extra accumulator depth did not compensate for serializing the raw TMA,
online decode, SMEM publication barrier, and MMA consumption through one
stage. The retained two-stage TMEM transform path is materially better for
every scanned shape, so the SMEM source and x8 decoder were restored.

Evidence:

- Capacity and layout bring-up:
  `logs/w4a16_smem_transform_probe1_20260722_225444/`,
  `logs/w4a16_smem_transform_probe2_20260722_225843/`, and
  `logs/w4a16_smem_transform_probe3_20260722_230033/`
- Passing focused correctness:
  `logs/w4a16_smem_transform_probe4_20260722_230254/run.log`
- Full same-node CUPTI sweep:
  `logs/w4a16_smem_transform_bench_20260722_230413/run.log`
- Same-node pushed baseline:
  `logs/w4a16_decode_pair_same_node_baseline_20260722_215710/run.log`

### Balance the persistent-kernel tail with CLC scheduling

**Result: Promising for dense EP; continue refining the scheduler before
exposing another tactic axis.** The
retained static scheduler launches exactly one resident cluster wave and assigns
each cluster a fixed strided sequence of output tiles. On the EP8 4096-token
profile, GEMM1 had a `14.34%` max/min spread in per-SM active cycles and a
`1.0902x` max/average ratio. CUTLASS's SM100 grouped input-transform GEMM uses
Cluster Launch Control (CLC) for dynamic persistent scheduling, so the prototype
replaced only the scheduler warp's work source while preserving the existing
three-stage routed-tile broadcast to every other warp.

The MoE launch capacity includes padded routes after the runtime-valid compact
prefix. Scheduler warps therefore discard CLC responses whose route index is at
or above `num_non_exiting_tiles` and continue querying until hardware reports
that no pending cluster remains. A two-CTA launch can also contain one-CTA MMA;
CLC query ownership must use CTA rank zero in the launch cluster rather than the
MMA-leader predicate.

Focused route/topology correctness passed. NCU shows that CLC contracts the
GEMM1 tail and kernel duration:

| Metric | Static | CLC |
|---|---:|---:|
| GEMM1 duration | `324.448 us` | `306.368 us` |
| GEMM1 max / average active cycles | `1.0902x` | `1.0428x` |
| GEMM1 max / min active-cycle spread | `14.34%` | `9.24%` |
| GEMM2 duration | `166.208 us` | `162.944 us` |

An unconditional CLC scheduler is not appropriate. Against the retained
route-192 sweep it improves EP8 from 64 through 4096 tokens, including `1.0381x`
at 64 and `1.0029x` at 4096, but query and full-grid launch overhead regress the
smallest shapes. Overall geomeans are `0.9235x` for EP8 and `0.9465x` for
simulated TP8.

A follow-up mirrored MegaMoE's bundled CLC work IDs by assigning four
consecutive route tiles to each canceled cluster. It reduced CLC queries and
the logical launch grid by `4x`, but made scheduling too coarse: one cluster
could not be rebalanced until all four routed tiles completed. Against one-item
CLC, bundle-four geomeans were only `0.7180x` for EP8 and `0.7206x` for
simulated TP8; EP8 4096 tokens regressed from `0.415648 ms` to `0.490192 ms`.
This rejects bundle-four and also shows that query throughput is not the main
CLC cost. A finer bundle and scheduler-pipeline changes remain worth testing,
without adding CLC as an autotune axis yet.

Bundle-two confirmed the granularity result. Its EP8 and simulated-TP8
geomeans versus one-item CLC were `0.8706x` and `0.9025x`; EP8 4096 tokens
regressed from `0.415648 ms` to `0.438991 ms`. Even two consecutive routed
tiles per cancellation unit are too coarse. The clean one-item scheduler was
restored, and subsequent CLC work should preserve that unit of balancing while
improving response handling or metadata publication.

The first pipeline refinement reduced the routed-metadata queue from three
stages to two. This keeps one future tile available to the TMA/transform roles,
but prevents each cluster from claiming a second future CLC assignment before
the current work retires. Against three-stage CLC, EP8 improved by `1.0292x`
geomean (`1.1032x` at 32 tokens); simulated TP8 was essentially neutral at
`0.9955x`. EP8 4096 moved from `0.415648 ms` to `0.418304 ms` in the CUPTI
sweep, within `0.6%`.

NCU confirms that the dense GEMM1 balance is preserved: duration changed from
`306.368 us` to `305.312 us`, max/average active cycles from `1.0428x` to
`1.0421x`, and max/min spread from `9.24%` to `9.28%`. GEMM2 duration regressed
from `162.944 us` to `166.272 us`, but its max/min active-cycle spread narrowed
from `7.11%` to `4.37%`. The two-stage queue is retained while the remaining
GEMM2 pipeline overhead is investigated.

Because the two kernels have different retirement costs, the retained design
uses two metadata stages only for fused-activation GEMM1 and keeps three for
plain-output GEMM2. This combines GEMM1's lower work hoarding with GEMM2's
deeper load lookahead. Relative to three-stage CLC for both kernels, the split
pipeline improves EP8 by `1.0196x` geomean and simulated TP8 by `1.0083x`.
EP8 4096 is unchanged (`0.415695 ms` versus `0.415648 ms`), while TP8 4096
improves `1.0161x`. The four route/topology accuracy cases remain green.

The next refinement moved CLC query issue behind metadata-slot acquisition for
real routed tiles. Previously, a cluster could issue one more cancellation and
claim work while blocked on a full metadata queue. The new order caps work
hoarding without shortening TMA/transform lookahead; the CLC query still runs
asynchronously while the scheduler publishes the acquired metadata slot.
Padded route entries continue to issue immediately because they publish no
work.

This ordering improves over the split-depth CLC path by `1.0143x` EP8 and
`1.0188x` simulated-TP8 geomean. Relative to the original three-stage CLC path,
the gains are `1.0341x` and `1.0272x`, with every shape non-regressive beyond
noise. Against the retained static scheduler, CLC now wins EP8 from 32 through
4096 tokens: `1.0198x` at 32, `1.0500x` at 64, and `1.0071x` at 4096. Small EP
shapes still lose to the static one-wave launch, so CLC is not yet an
unconditional end-to-end win.

Evidence:

- Initial alignment failure:
  `logs/w4a16_clc_test_20260723_002848/run.log`
- Cluster-leader diagnosis and one-CTA pass:
  `logs/w4a16_clc_test2_20260723_003000/run.log` and
  `logs/w4a16_clc_route32_debug_20260723_003113/run.log`
- Passing focused correctness:
  `logs/w4a16_clc_test3_20260723_003218/run.log`
- Full same-node CUPTI sweep:
  `logs/w4a16_clc_bench_20260723_003300/run.log`
- Bundle-four correctness and CUPTI sweep:
  `logs/w4a16_clc_bundle4_test_20260723_004414/run.log` and
  `logs/w4a16_clc_bundle4_bench_20260723_004453/run.log`
- Bundle-two correctness and CUPTI sweep:
  `logs/w4a16_clc_bundle2_test_20260723_004853/run.log` and
  `logs/w4a16_clc_bundle2_bench_20260723_004927/run.log`
- Two-stage metadata correctness, CUPTI sweep, and NCU report:
  `logs/w4a16_clc_tileinfo2_test_20260723_005434/run.log`,
  `logs/w4a16_clc_tileinfo2_bench_20260723_005511/run.log`, and
  `logs/w4a16_clc_tileinfo2_ncu_ep8_4096_20260723_005759/reports/ep_w4a16_t4096.ncu-rep`
- Split GEMM1/GEMM2 metadata-depth correctness and CUPTI sweep:
  `logs/w4a16_clc_split_tileinfo_test_20260723_010050/run.log` and
  `logs/w4a16_clc_split_tileinfo_bench_20260723_010121/run.log`
- Post-acquire CLC issue correctness and CUPTI sweep:
  `logs/w4a16_clc_post_acquire_test_20260723_010635/run.log` and
  `logs/w4a16_clc_post_acquire_bench_20260723_010700/run.log`
- Post-acquire CLC NCU profile:
  `logs/w4a16_clc_post_acquire_ncu_ep8_4096_20260723_011201/reports/ep_w4a16_t4096.ncu-rep`
- CLC NCU report:
  `logs/w4a16_clc_ncu_ep8_4096_20260723_003614/reports/ep_w4a16_t4096.ncu-rep`
- Static NCU baseline:
  `logs/w4a16_route192_ncu_ep8_4096_20260723_000430/reports/ep_w4a16_t4096.ncu-rep`

The post-acquire NCU run confirms that the refinement preserves CLC's dense
GEMM1 benefit. GEMM1 measures `305.504 us`, a `1.0620x` speedup over the
`324.448 us` static baseline. Its max/average active-cycle ratio is `1.0419x`
and its max/min spread is `9.24%`, versus `1.0902x` and `14.34%` without CLC.
GEMM2 is `163.264 us`, close to the original CLC result of `162.944 us` and
better than the two-stage-for-both-kernels result of `166.272 us`.

A one-lane CLC response consumer reduced the empty-barrier arrival count from
one warp per CTA to one lane per CTA and broadcast the decoded response with
four warp shuffles. Correctness passed, and fixed overhead improved at a few
tiny shapes, including EP8 one token from `0.054576 ms` to `0.048512 ms`.
However, serial response decode and broadcast reduced dense scheduling
throughput: EP8 regressed `2.33%` at 2048 tokens and `8.41%` at 4096 tokens;
simulated TP8 regressed across most dense shapes and by `1.84%` at 4096.
Geomeans versus the full-warp consumer were `1.0033x` EP8 and `0.9910x` TP8,
with the EP result dominated by the one-token outlier. The full-warp response
consumer was restored.

Evidence:

- One-lane response correctness:
  `logs/w4a16_clc_lane0_test_20260723_011554/run.log`
- One-lane response CUPTI sweep:
  `logs/w4a16_clc_lane0_bench_20260723_011627/run.log`

CLC was then limited to fused-activation GEMM1, while GEMM2 returned to the
existing static persistent scheduler. This reflects the measured workload
split: CLC improves EP8 4096-token GEMM1 by `1.0620x`, while its GEMM2 benefit
is only about `1.018x` and does not repay fixed scheduling overhead at small
shapes. The metadata depth now follows the explicit `use_clc_scheduler`
policy: two stages for dynamic GEMM1 and the original three stages for static
GEMM2.

Focused route/topology correctness passed. Relative to CLC in both GEMMs, the
split improves EP8 by `1.0432x` geomean and reaches `1.1856x` and `1.2777x` at
one and two tokens. Relative to no CLC, EP8 is nearly neutral over the full
sweep (`0.9964x` geomean) while retaining dense wins: `1.0184x` at 32,
`1.0390x` at 64, and `1.0089x` at 4096 tokens. Simulated TP8 is `0.9629x`
geomean versus no CLC, but returns to a `1.0039x` win at 4096. The role split
is retained while GEMM1's remaining small-workload CLC overhead is refined.

Evidence:

- GEMM1-only CLC correctness:
  `logs/w4a16_clc_gemm1_test_20260723_012407/run.log`
- GEMM1-only CLC CUPTI sweep:
  `logs/w4a16_clc_gemm1_bench_20260723_012548/run.log`

Reducing dynamic GEMM1's routed-metadata queue from two stages to one removes
the remaining work-hoarding outlier without starving the existing TMA and
transform pipelines. Focused correctness passed. Relative to the two-stage
GEMM1-only CLC design, EP8 improves `1.0158x` geomean, including `1.1454x` at
16 tokens, and simulated TP8 improves `1.0105x` geomean. The 4096-token EP8
latency is effectively unchanged (`0.413567 ms` versus `0.413168 ms`).

Against no CLC, the one-stage GEMM1-only design is now a `1.0121x` EP8
full-sweep geomean win. It is effectively neutral at one token (`0.9983x`) and
16 tokens (`0.9881x`), and wins every other EP8 shape: `1.0260x` at 32,
`1.0432x` at 64, `1.0413x` at 128, and `1.0080x` at 4096. Simulated TP8 is
still `0.9730x` geomean because of the 4- and 8-token cases, but reaches
`1.0076x` at 4096. The one-stage metadata queue is retained.

Evidence:

- One-stage GEMM1 CLC correctness:
  `logs/w4a16_clc_gemm1_stage1_test_20260723_013117/run.log`
- One-stage GEMM1 CLC CUPTI sweep:
  `logs/w4a16_clc_gemm1_stage1_bench_20260723_013149/run.log`

The one-stage role split also improves the dense GEMM1 profile rather than
merely shifting end-to-end timing noise. At EP8 4096 tokens, GEMM1 falls from
`324.448 us` without CLC to `301.792 us` (`1.0751x`), while static GEMM2 is
effectively unchanged at `165.408 us` versus `166.208 us`. GEMM1's slowest-CTA
max/min active-cycle spread drops from `14.34%` to `9.37%`; its max/average
ratio drops from `1.0902x` to `1.0428x`. Compared with the earlier CLC path in
both GEMMs, one-stage GEMM1 is another `1.0123x` faster and GEMM2 avoids dynamic
scheduling entirely.

Evidence:

- One-stage GEMM1 CLC NCU profile:
  `logs/w4a16_clc_gemm1_stage1_ncu_ep8_4096_20260723_013453/reports/ep_w4a16_t4096.ncu-rep`

Adding the missing reverse asymmetric topology, GEMM1 `M256` plus GEMM2
`M128`, did not improve the CLC role split. It was neutral across most shapes
and improved EP8 2048 tokens by `1.0051x`, but the selected 4096-token tactics
regressed to `0.9185x` EP8 and `0.9828x` simulated TP8. Full-sweep geomeans
were `0.9932x` EP8 and `0.9993x` simulated TP8 relative to the retained
one-stage GEMM1-only CLC design. The topology was removed to avoid expanding
the search space with an unstable option.

Evidence:

- Current autotuner selections before the experiment:
  `logs/w4a16_clc_gemm1_stage1_debug_20260723_014746/run.log`
- Reverse-topology CUPTI sweep:
  `logs/w4a16_clc_reverse_topology_bench_20260723_015306/run.log`

The dynamic scheduler's metadata publisher was also reduced from a full-warp
producer group to one elected producer. CLC response decoding remained
full-warp, so this isolated the cost of 31 redundant full-barrier arrivals and
the scheduler warp's named barrier. Focused correctness passed, but the full
sweep was indistinguishable from noise: `0.9994x` EP8 and `1.0009x` simulated
TP8 geomeans relative to the retained one-stage GEMM1-only CLC path, with every
shape within about `0.45%`. The full-warp producer was restored because the
conditional pipeline-participant contract added complexity without reducing
the measured critical path.

Evidence:

- Single-producer metadata correctness:
  `logs/w4a16_clc_single_producer_test_20260723_021511/run.log`
- Single-producer metadata CUPTI sweep:
  `logs/w4a16_clc_single_producer_bench_20260723_021649/run.log`

Increasing each epilogue warp's register allocation from 176 to 184 did not
produce a repeatable benefit. The full sweep was `0.9943x` EP8 and `0.9998x`
simulated TP8 relative to the retained 176-register design. Most shapes were
within noise, but the first sweep had isolated regressions at EP8 2048 tokens
(`0.9350x`) and TP8 4096 tokens (`0.9835x`). A targeted retune recovered EP8
2048 from `0.343552 ms` to `0.317871 ms`, but moved EP8 4096 in the opposite
direction from `0.413536 ms` to `0.448496 ms`; TP8 stayed effectively flat.
The selected large-shape topologies were unchanged, so the variation does not
support spending more registers on an epilogue that is not the measured
bottleneck. The 176-register allocation was restored.

Evidence:

- 184-register CUPTI sweep:
  `logs/w4a16_epilogue184_bench_20260723_022743/run.log`
- 184-register targeted autotuner trace:
  `logs/w4a16_epilogue184_debug_20260723_023042/run.log`
- Editable-install refresh after the whole-tree sync:
  `logs/w4a16_epilogue184_reinstall_20260723_022643/run.log`
- 184-register focused correctness:
  `logs/w4a16_epilogue184_test_20260723_022720/run.log`

CLC scheduling was then restricted to fused GEMM1 launches whose logical
problem grid exceeds one resident cluster wave. This is an exact capacity
condition derived from the MMA tile, CTA group, cluster shape, routed extent,
and `get_max_active_clusters`; it is not a token-count heuristic. A one-wave
launch has no pending clusters for CLC to cancel and rebalance, so the existing
static persistent scheduler is the simpler contract there. Multi-wave GEMM1
keeps the retained one-stage CLC scheduler, and GEMM2 remains static.

The route/topology numerical matrix passed all five cases and exercised the
new static fused-GEMM1 path. Relative to unconditional GEMM1 CLC, the complete
sweep is `0.9994x` EP8 and `1.0149x` simulated TP8 by geomean. EP8 4096 tokens
is unchanged (`0.413103 ms` versus `0.413567 ms`). Simulated TP8 at four tokens,
whose selected launch fits in one wave, improves from `0.078688 ms` to
`0.062768 ms` (`1.2536x`). Most other points are within noise; the isolated
TP8 4096-token result regressed `3.02%` despite retaining CLC and is treated as
autotuner/measurement variance. The capacity-based dispatch is retained for
its cleaner scheduler semantics and small-workload benefit.

Evidence:

- Capacity-dispatch CUPTI sweep:
  `logs/w4a16_clc_onewave_bench_20260723_023831/run.log`
- Static fused-GEMM1 correctness:
  `logs/w4a16_clc_onewave_test_20260723_024149/run.log`
- Editable-install refresh:
  `logs/w4a16_clc_onewave_reinstall_20260723_023721/run.log`

A decoded-weight-reuse prototype grouped 256 routed rows under one expert and
executed them as two serial N128 MMA subtiles in one CTA. Weight and scale TMA
loads plus the NVFP4-to-BF16 transform ran once per K tile, while activation
loads, MMA, accumulators, and epilogue remained distinct for the two N128
subtiles. This preserved the K256 online-decode path and passed the focused
route-256 numerical test.

The design was not competitive because halving transform work also halved the
available CTA-level route parallelism. The paired tactic was never selected by
the full EP8 autotune sweep. At 4096 tokens, its best cold-cache profile was
`0.539715 ms`, versus `0.436243 ms` for route 192. A forced steady-state
comparison measured route 128 at `0.460767 ms`, route 192 at `0.475967 ms`,
and paired route 256 at `0.597087 ms`. The ordinary route path initially
regressed because the paired epilogue introduced a runtime subtile-completion
branch; restoring a compile-time single-route branch recovered EP8 2048 from
`0.331856 ms` to `0.318816 ms`, but did not make the paired tactic viable.

The serial paired-route implementation was removed. Preserving parallel N128
CTAs would require replicating the expanded BF16 tile into each consumer's
local SMEM because `tcgen05.mma` cannot consume a peer CTA's shared-memory
descriptor directly. That is the already-rejected transformed-A SMEM/DSM
contract described above, so the current pipeline has no viable decoded-weight
reuse path without changing the hardware operand contract.

Evidence:

- Focused route-256 numerical test:
  `logs/w4a16_route_pair_probe_20260723_024939/run.log`
- Initial full CUPTI sweep:
  `logs/w4a16_route_pair_bench_20260723_025009/run.log`
- EP8 autotuner trace:
  `logs/w4a16_route_pair_debug_ep_20260723_025311/run.log`
- Static single-route epilogue CUPTI sweep:
  `logs/w4a16_route_pair_static_epi_bench_20260723_025943/run.log`
- Forced EP8 4096 route comparison:
  `logs/w4a16_route_pair_forced_ep4096_20260723_030354/run.log`

### Unroll the online transform across two K tiles

**Result: Rejected.** CUTLASS's grouped mixed-input accumulator-scale kernel
uses two cloned load-to-transform and transform-to-MMA pipeline states. It
waits for two input stages, loads the second packed fragment while decoding the
first, commits the first transformed tile, and then decodes and commits the
second. W4A16 did not previously test this exact scheduling pattern: the prior
full-fragment preload and one-fragment lookahead experiments remained within a
single K tile.

The W4A16 prototype mirrored the two-tile schedule with independent packed,
scale, and transformed register fragments and handled odd K-tile counts through
a single-tile tail. All five route/topology numerical cases passed, and the GPU
watchdog showed forward progress rather than a persistent-kernel stall.

The larger live range and two-stage startup wait outweighed the overlap. Against
the retained one-wave CLC dispatch, EP8 measured `0.9183x` geomean (range
`0.8907x`-`0.9456x`) and simulated TP8 measured `0.9522x` (range
`0.9200x`-`1.0069x`). EP8 regressed at every shape, including 4096 tokens from
`0.413103 ms` to `0.451696 ms`. Only simulated TP8 at 4096 tokens reached
parity. The serial one-K-tile transform loop was restored.

Evidence:

- Focused correctness and GPU watchdog:
  `logs/w4a16_transform_pair_test_20260723_031839/`
- Full CUPTI sweep and GPU watchdog:
  `logs/w4a16_transform_pair_bench_20260723_031903/`

### Reuse the epilogue warpgroup for K256 online transform

**Result: Retained.** NCU showed the four transform warps on the critical path
while the epilogue warpgroup waited for the accumulator. The earlier attempt to
reuse those warps was numerically valid for one tile but invalid for persistent
work because the epilogue warps completed the entire transform loop before
entering the entire epilogue loop. The retained design interleaves the roles:
for each persistent work tile, epilogue warps decode one K128 half of every
K256 weight stage, then immediately consume and store that same tile's
accumulator. The dedicated transform warpgroup decodes the other K128 half.

The specialization is deliberately limited to gated M128/K256 tactics, where
the previously validated `tcgen05.St32x32b` x4 ownership exposes two native
K128 partitions. It keeps the 12-warp CTA and current register allocations;
unlike the rejected 16-warp version, it adds no launch warps. Both warpgroups
call shared CuTe DSL helpers for partition setup and one-tile transform
execution, preventing the two decode paths from drifting.

All five route/topology numerical cases passed, including multi-tile
persistent work. Against the retained one-wave CLC baseline, the repeated full
same-node CUPTI sweep measured:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `1.0185x` | `0.9975x` | `1.0333x` |
| simulated TP8 | `1.0205x` | `1.0005x` | `1.0519x` |

The gain is concentrated at 1-512 tokens: EP8 improves by `1.0%`-`3.3%` and
simulated TP8 by `1.3%`-`5.2%`. Dense EP8 remains at parity (`0.9975x` at
4096 tokens). One first post-refactor 4096-token sample was `0.425791 ms`, but
an exact full-sweep repeat returned `0.414144 ms` versus the baseline's
`0.413103 ms`; the isolated sample was measurement variance rather than a
repeatable helper-inlining regression.

Evidence:

- Initial interleaved implementation correctness:
  `logs/w4a16_epi_transform_test_20260723_033601/run.log`
- Initial implementation CUPTI sweep:
  `logs/w4a16_epi_transform_bench_20260723_033644/run.log`
- Shared-helper refactor correctness:
  `logs/w4a16_epi_transform_refactor_test_20260723_034436/run.log`
- Shared-helper first CUPTI sweep:
  `logs/w4a16_epi_transform_refactor_bench_20260723_034509/run.log`
- Shared-helper repeated CUPTI sweep:
  `logs/w4a16_epi_transform_refactor_repeat_20260723_034956/run.log`
- Full W4A16 contract suite after cleanup (`13 passed`):
  `logs/w4a16_epi_transform_full_test_20260723_035940/run.log`
- Non-comparable isolated EP8 4096 diagnostic:
  `logs/w4a16_epi_transform_ep4096_repeat_20260723_034830/run.log`

### Dedicate two complete warpgroups to online transform

**Result: Retained as a structural checkpoint; performance needs follow-up.**
The epilogue-transform specialization above coupled online dequantization to
one M128/K256 SwiGLU tactic. The refactor instead gives warps 8-15 the transform
role for every tactic and restores warps 0-3 to a pure epilogue role. Each
transform warpgroup uses `tcgen05.st.32x32b.x4`; matching warp ranks in the two
groups write the same 32 TMEM lanes but disjoint four-column regions.

The first implementation incorrectly treated each group's packed register
fragment as complete 16-value NVFP4 blocks. CuTe's generated layout actually
gives group 0 and group 1 the first and second eight values from every block,
with the E4M3 scale broadcast across the group axis. The corrected decoder
therefore consumes four packed E2M1 bytes plus one E4M3 byte per iteration and
emits eight BF16 values. Each thread loops over K/16 half-blocks, then its warp
stores the accumulated 32, 64, or 128 BF16 values for K64, K128, or K256.

The complete route/topology matrix passed, followed by the full W4A16 class
(`13 passed`). Relative to the retained epilogue-transform implementation at
`2fd55dda`, however, the full CUPTI sweep regressed:

| Configuration | Geomean | Minimum | Maximum | Geomean slowdown |
|---|---:|---:|---:|---:|
| EP8 | `0.9377x` | `0.9196x` | `0.9593x` | `6.65%` |
| simulated TP8 | `0.9445x` | `0.9209x` | `0.9769x` | `5.88%` |

The slowdown is broad across 1-4096 tokens rather than isolated to one route
tactic. The design is retained as requested because it has uniform ownership,
cleanly separates transform and epilogue roles, and provides the intended
eight-warp substrate for subsequent scheduling and register tuning. It should
not yet be described as a performance improvement.

Evidence:

- Initial fixed-fragment numerical failures:
  `logs/w4a16_dedicated8_uniform_test_20260723_042732/run.log`
- Emitted source, scale, and TMEM layouts:
  `logs/w4a16_dedicated8_register_layout_20260723_044400/run.log`
- Correct half-block route/topology matrix (`5 passed`):
  `logs/w4a16_dedicated8_halfblock_v3_20260723_045440/run.log`
- Full W4A16 contract suite (`13 passed`):
  `logs/w4a16_dedicated8_full_test_20260723_045518/run.log`
- EP8 and simulated TP8 CUPTI sweep:
  `logs/w4a16_dedicated8_bench_20260723_045638/run.log`

### Stripe complete NVFP4 blocks across two transform warpgroups

**Result: Retained; first eight-warp design to exceed the four-warp baseline.**
The half-block design above makes both transform warpgroups convert the same
E4M3 scale because each group owns eight values from every 16-value NVFP4
block. An x8 TMEM store exposes one complete block per thread instead. The
revised mapping logically divides the complete-block mode by two and assigns
even blocks to transform warpgroup 0 and odd blocks to transform warpgroup 1.
Source, scale, and TMEM destination use the same dynamic parity slice, so each
scale is converted exactly once and each group writes disjoint TMEM columns.

The generated one-CTA K64 layouts demonstrate the mapping directly:

```text
source before:  ((16,1),1,1,4,stage):((1,0),0,0,16,...)
source striped: ((16,1),1,1,(2,2),stage):((1,0),0,0,(16,32),...)
scale before:   ((8,2),1,1,4,stage):((0,0),0,0,1,...)
scale striped:  ((8,2),1,1,(2,2),stage):((0,0),0,0,(1,2),...)
```

All five route/topology cases passed, followed by the full W4A16 class
(`13 passed`). Relative to the four-warp `2fd55dda` implementation, the exact
same-node CUPTI sweep measured:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `1.0182x` | `0.9430x` | `1.0541x` |
| simulated TP8 | `1.0167x` | `0.9587x` | `1.0484x` |

| Tokens | EP8 speedup | simulated TP8 speedup |
|---:|---:|---:|
| 1 | `1.0079x` | `1.0300x` |
| 2 | `0.9955x` | `1.0282x` |
| 4 | `1.0251x` | `1.0304x` |
| 8 | `1.0251x` | `1.0289x` |
| 16 | `1.0244x` | `1.0247x` |
| 32 | `1.0297x` | `1.0233x` |
| 64 | `1.0244x` | `1.0197x` |
| 128 | `1.0342x` | `1.0484x` |
| 256 | `1.0472x` | `1.0407x` |
| 512 | `1.0541x` | `1.0252x` |
| 1024 | `1.0278x` | `0.9859x` |
| 2048 | `1.0031x` | `0.9767x` |
| 4096 | `0.9430x` | `0.9587x` |

This removes the broad six-percent regression of the half-block implementation
and establishes an overall win, but it does not close the dense tail. The next
step is to profile EP8 4096 and determine whether the remaining loss comes from
the 512-thread CTA occupancy, transform issue width, or scheduler tail.

Evidence:

- x8 generated layout matrix:
  `logs/w4a16_x8_layout_probe_20260723_050400/run.log`
- parity-stride layout probe:
  `logs/w4a16_x8_stripe_probe_20260723_050625/run.log`
- route/topology matrix (`5 passed`):
  `logs/w4a16_x8_blockstripe_matrix_20260723_050921/run.log`
- full W4A16 class (`13 passed`):
  `logs/w4a16_x8_blockstripe_full_test_20260723_051358/run.log`
- EP8 and simulated TP8 CUPTI sweep:
  `logs/w4a16_x8_blockstripe_bench_20260723_051046/run.log`

### Assign contiguous complete-block ranges to transform warpgroups

**Result: Retained; exceeds the four-warp baseline and removes the EP8 dense
tail regression.** The parity-stripe checkpoint gives each transform warpgroup
complete NVFP4 blocks, but each group reads every other packed-weight block and
every other E4M3 scale byte. This revision divides the complete-block mode into
two contiguous ranges instead. A transform group therefore reads contiguous
packed E2M1 bytes, contiguous scale bytes, and contiguous TMEM columns.

Contiguous ownership also changes each thread's coalesced register fragment.
Depending on the autotuned K tile, one decoder call now handles 32, 64, or 128
BF16 outputs and consumes 2, 4, or 8 compact scale bytes. The data and scale
fragments must be tiled independently: the data tiler is measured in BF16
elements, while its scale tiler has `data_elements / 16` entries. The first
attempt retained the expanded scale view and incorrectly produced one scale
byte for 64- and 128-value fragments; the corrected path divides the compact
scale register tensor directly. The final decoder bitcasts the complete packed
fragment to `uint32` once and consumes two words per NVFP4 block, avoiding an
intermediate byte extraction and reconstruction sequence.

All five route/topology cases passed, followed by the full W4A16 class
(`13 passed`). Relative to the four-warp `2fd55dda` implementation, the exact
same-node CUPTI sweep measured:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `1.0264x` | `0.9895x` | `1.0501x` |
| simulated TP8 | `1.0133x` | `0.9688x` | `1.0538x` |

| Tokens | EP8 speedup | simulated TP8 speedup |
|---:|---:|---:|
| 1 | `1.0227x` | `1.0175x` |
| 2 | `1.0240x` | `1.0192x` |
| 4 | `1.0279x` | `1.0129x` |
| 8 | `1.0298x` | `1.0283x` |
| 16 | `1.0318x` | `1.0103x` |
| 32 | `1.0394x` | `1.0116x` |
| 64 | `1.0353x` | `1.0277x` |
| 128 | `1.0436x` | `1.0538x` |
| 256 | `1.0219x` | `1.0150x` |
| 512 | `1.0142x` | `1.0148x` |
| 1024 | `1.0501x` | `0.9990x` |
| 2048 | `0.9895x` | `0.9959x` |
| 4096 | `1.0141x` | `0.9688x` |

Relative to the parity-stripe checkpoint, EP8 geomean improves another
`1.0080x`; TP8 geomean is effectively neutral at `0.9967x`. Most importantly,
EP8 4096 improves `1.0754x`, changing the prior `0.9430x` four-warp ratio to
`1.0141x`. The remaining target is the TP8 dense tail.

Evidence:

- Initial expanded-scale tiling failure:
  `logs/w4a16_x8_contiguous_vector_matrix_20260723_053028/run.log`
- Correct compact-scale route/topology matrix (`5 passed`):
  `logs/w4a16_x8_contiguous_scale_tiling_matrix_20260723_053420/run.log`
- EP8 and simulated TP8 CUPTI sweep:
  `logs/w4a16_x8_contiguous_word_decoder_bench_20260723_054551/run.log`
- Full W4A16 class (`13 passed`):
  `logs/w4a16_x8_contiguous_word_decoder_test_20260723_054511/run.log`

### Raise transform warps to 128 registers

**Result: Retained after fixing the control-warpgroup protocol.** Exact use of
the documented 65,536-register CTA pool is valid. FlashInfer's FP8 MLA decode
kernel already uses four 160-register softmax/correction warpgroups and one
32-register MMA/load warpgroup for an exact 65,536-register allocation. CUTLASS
C++ input-transform kernels also compute 128 registers as the default for a
512-thread launch and omit `setmaxnreg` when a role keeps that allocation.

The first two 128-register transform variants retained mixed register targets
inside role-control warpgroup 1: MMA 96, scheduler 64, and TMA 80. Both hung on
hardware. Uniformizing all four warps in that warpgroup to 80 first passed the
five-case route/tactic probe with transform warps at 120. Keeping that uniform
80-register target while leaving both transform warpgroups at their
128-register launch default then passed the same probe and the full W4A16 test
class. Emitted PTX contains four `setmaxnreg.dec 80` instructions and one
`setmaxnreg.inc 176`, with no transform-side `setmaxnreg` instruction.

The retained allocation is:

| Warpgroup | Role | Registers/thread | CTA registers |
|---|---|---:|---:|
| 0 | Epilogue | 176 | 22,528 |
| 1 | MMA, scheduler, and TMA | 80 | 10,240 |
| 2-3 | Weight transform | 128 | 32,768 |
| | **Total** | | **65,536** |

Against the 120-register transform baseline, the exact-budget design is
roughly neutral overall and improves the dense tail:

| Topology | Geomean | Min | Max | 4096 tokens |
|---|---:|---:|---:|---:|
| EP8 | `1.0017x` | `0.9814x` | `1.0299x` | `1.0259x` |
| Simulated TP8 | `1.0114x` | `0.9980x` | `1.0290x` | `1.0268x` |

This isolates the previous deadlock to the mixed reallocation protocol at zero
slack, rather than the exact register budget itself.

Evidence:

- 128-register decrease benchmark hang:
  `logs/w4a16_x8_contiguous_regs128_bench_20260723_055659/run.log`
- 128-register transform path without a decrease, route-matrix hang:
  `logs/w4a16_x8_transform_retain128_matrix_20260723_060142/run.log`
- Uniform control warpgroup with 120-register transforms (`5 passed`):
  `logs/w4a16_uniform80_regs120_probe_20260723_061148/run.log`
- Exact-budget route/tactic probe and emitted PTX (`5 passed`):
  `logs/w4a16_uniform80_regs128_exact_probe_retry_20260723_061637/`
- Full W4A16 class (`13 passed`) and EP8/TP8 benchmark:
  `logs/w4a16_uniform80_regs128_full_validation_20260723_062747/`

### Replace the saturating C++ BF16 permute with a bounded Triton producer

**Result: Correct, but rejected as the final topology.** The shared C++ MoE
permute launches enough 256-thread CTAs to saturate all SMs. GEMM1 therefore
cannot become resident while the producer is active, even though PDL allows its
weight TMA and online dequantization pipeline to run before activation
permutation is complete. Commit `8aed1a35` first removed the ineffective
`launch_dependents_early` plumbing from this shared C++ path and restored its
single end-of-kernel PDL completion point.

The first W4A16-private Triton prototype used 74 eight-warp programs on the
148-SM B200. Every program:

1. waits for `moe_sort`, so GEMM1 CLC and static scheduling cannot race route
   metadata;
2. calls `gdc_launch_dependents()` before copying activations;
3. copies complete BF16 rows in 1024-element vectors with a grid-stride row
   loop.

GEMM1 retains its existing dependency wait only in the activation TMA warp.
Consequently, its weight and scale TMA plus transform warps may execute while
the Triton producer is still writing the permuted activation workspace. A
deterministic-finalize SwiGLU case passed, proving the PDL chain and memory
ordering do not deadlock.

The bounded grid did not provide enough copy throughput at larger route counts.
Against the exact same cached code and CUPTI/CUDA-graph benchmark, C++ latency
divided by Triton latency was:

| Configuration | Geomean | Minimum | Maximum |
|---|---:|---:|---:|
| EP8 | `0.9503x` | `0.7698x` | `1.0592x` |
| simulated TP8 | `0.8648x` | `0.6011x` | `1.0756x` |

| Tokens | EP8 speedup | simulated TP8 speedup |
|---:|---:|---:|
| 1 | `1.0592x` | `1.0756x` |
| 2 | `1.0285x` | `1.0643x` |
| 4 | `1.0058x` | `0.9977x` |
| 8 | `0.9967x` | `0.8539x` |
| 16 | `0.9978x` | `0.9667x` |
| 32 | `1.0029x` | `0.9618x` |
| 64 | `0.9943x` | `0.9324x` |
| 128 | `0.9863x` | `0.9043x` |
| 256 | `0.9650x` | `0.8532x` |
| 512 | `0.9353x` | `0.7875x` |
| 1024 | `0.8814x` | `0.7297x` |
| 2048 | `0.7698x` | `0.6712x` |
| 4096 | `0.7851x` | `0.6011x` |

The next experiments should preserve early PDL signaling but increase producer
parallelism and reduce per-program row-loop serialization. Nsight Systems must
first confirm whether the prototype actually establishes producer/GEMM1
overlap; otherwise topology tuning cannot recover the intended benefit.

Evidence:

- First environment failures from stale synced source links:
  `logs/triton_permute_probe_20260723_103036/run.log` and
  `logs/triton_permute_probe_20260723_103117/run.log`
- Deterministic-finalize W4A16 probe (`1 passed`):
  `logs/triton_permute_probe_20260723_103210/run.log`
- Exact C++ versus bounded-Triton EP8/TP8 sweep:
  `logs/triton_permute_ab_20260723_104310/run.log`

### Increase Triton producer occupancy and vector width

**Result: Promising; continue tuning around 32 warps and a near-full grid.**
Nsight Systems confirms that the bounded producer establishes the intended
dependency overlap. At both 32 and 4096 tokens, GEMM1 starts about 1.2 us after
the Triton permute starts and remains concurrent with nearly the entire
producer. The 74-program prototype is nevertheless too slow: at 4096 tokens
the permute lasts about 145-155 us and stretches concurrent GEMM1 to roughly
359-366 us. The PDL mechanism is working, but the producer leaves too much
memory bandwidth idle.

An EP8 sweep varied the number of resident producer CTAs, warps per CTA, and
the BF16 copy width. Every variant used the production AutoTuner, CUDA graph,
and CUPTI timing. Latencies are end-to-end W4A16 MoE milliseconds:

| Producer topology | 32 tokens | 512 tokens | 4096 tokens |
|---|---:|---:|---:|
| 74 CTAs, 8 warps, 1024 BF16 | `0.159904` | `0.247887` | `0.639103` |
| 112 CTAs, 16 warps, 2048 BF16 | `0.163728` | `0.236384` | `0.499952` |
| 128 CTAs, 16 warps, 2048 BF16 | `0.162912` | `0.238145` | `0.552496` |
| 136 CTAs, 16 warps, 2048 BF16 | `0.161200` | `0.234288` | `0.490336` |
| 136 CTAs, 32 warps, 4096 BF16 | **`0.159040`** | **`0.231456`** | **`0.469280`** |

The 136-CTA/32-warp design leaves 12 of 148 SMs available for dependent
two-CTA GEMM clusters while issuing one 8-byte vector load/store per thread for
each 4096-element chunk. It recovers nearly all of the prior C++ path at the
dense endpoint (`0.459744` ms), while slightly improving the prior C++ numbers
at 32 (`0.162048` ms) and 512 (`0.233360` ms) tokens. The remaining work is to
tune the 12-SM reserve and test a single 8192-element masked vector so the
producer needs only one static K iteration for hidden size 7168.

Evidence:

- PDL overlap profiles:
  `logs/triton_permute_nsys_candidate_20260723_111130/`
- EP8 producer topology sweep:
  `logs/triton_permute_topology_ep8_20260723_113757/run.log`

#### Use one 8192-element copy iteration

**Result: Retained for the prototype.** A second EP8 sweep held the producer at
32 warps while varying its SM reserve and changing the static copy extent from
4096 to 8192 BF16 elements. The wider extent covers DeepSeek's 7168-element
hidden row in one masked iteration and lets each thread move a 16-byte vector.

| Producer topology | 32 tokens | 512 tokens | 4096 tokens |
|---|---:|---:|---:|
| 128 CTAs, 32 warps, 4096 BF16 | `0.159312` | `0.231920` | `0.474720` |
| 132 CTAs, 32 warps, 4096 BF16 | `0.158192` | `0.232272` | `0.469823` |
| 140 CTAs, 32 warps, 4096 BF16 | `0.158224` | `0.231376` | `0.469408` |
| 144 CTAs, 32 warps, 4096 BF16 | `0.159920` | `0.231664` | `0.468080` |
| 148 CTAs, 32 warps, 4096 BF16 | `0.158448` | `0.231568` | `0.468384` |
| 136 CTAs, 32 warps, 8192 BF16 | `0.159552` | `0.230944` | **`0.458768`** |
| 140 CTAs, 32 warps, 8192 BF16 | `0.158368` | **`0.230736`** | `0.459344` |

The 136-CTA variant is `1.0021x` faster than the prior C++ path at 4096,
`1.0105x` faster at 512, and `1.0156x` faster at 32 tokens. The 12-SM reserve
remains preferable to a full-machine producer because it gives the dependent
two-CTA GEMM clusters immediate residency.

Simulated TP8 is close to, but does not yet consistently exceed, C++:

| Producer topology | 32 tokens | 512 tokens | 4096 tokens |
|---|---:|---:|---:|
| 132 CTAs, 32 warps, 8192 BF16 | **`0.184880`** | `0.375712` | `1.518304` |
| 136 CTAs, 32 warps, 8192 BF16 | `0.187984` | `0.375568` | `1.520800` |
| 140 CTAs, 32 warps, 8192 BF16 | `0.187440` | **`0.375440`** | **`1.516656`** |
| Prior C++ path | `0.188016` | `0.371904` | `1.503471` |

This is a major recovery from the first 74-CTA Triton prototype
(`0.195488`, `0.472271`, and `2.501181` ms respectively). Further work should
target the producer's generated memory instructions and the small residual
resource-contention cost rather than adding more CTAs.

Evidence:

- EP8 grid and vector-width sweep:
  `logs/triton_permute_grid_width_ep8_20260723_114202/run.log`
- Simulated TP8 grid sweep:
  `logs/triton_permute_grid_tp8_20260723_114502/run.log`

#### Batch multiple activation rows per Triton CTA

**Result: Rejected.** A 2D producer assigned 2, 4, or 8 rows to each
1024-thread CTA, intending to use its warps like multiple independent
256-thread permute blocks and amortize scalar route metadata. The
deterministic-finalize W4A16 SwiGLU probe passed, but larger row batches hurt
the dense endpoint:

| Rows per CTA | 32 tokens | 512 tokens | 4096 tokens |
|---:|---:|---:|---:|
| 1 | **`0.156303`** | `0.229455` | **`0.458624`** |
| 2 | `0.158768` | `0.229984` | `0.507744` |
| 4 | `0.158320` | `0.228721` | `0.505584` |
| 8 | `0.159489` | **`0.228528`** | `0.506241` |

Generated PTX exposes the cost. The one-row kernel declares approximately 23
`b32` and 13 `b64` registers, while the four-row form declares 58 and 22, and
the eight-row form declares 102 and 34. The larger 2D fragments and address
state reduce occupancy and interfere with the dependent GEMM. A sub-percent
512-token gain does not justify a roughly 10% dense-tail regression, so the
lean one-row vector copy is retained.

Evidence:

- Batched-row correctness probe (`1 passed`):
  `logs/triton_permute_batched_rows_probe_20260723_115236/run.log`
- EP8 row-batch sweep:
  `logs/triton_permute_row_batch_ep8_20260723_115306/run.log`

#### Tune memory policy, handoff point, and producer schedule

**Result: Retain the immediate handoff and default cache policy.** The
producer is a gather followed by a contiguous write. Explicit cache policies
did not improve the end-to-end path, and delaying
`gdc_launch_dependents()` until some rows had been copied removed useful
weight-load/dequantization overlap. Varying the handoff row count and producer
grid did not expose a delayed-handoff regime that beat signaling immediately
after the predecessor wait.

The following alternatives were measured and rejected:

- Explicit input/output cache modifiers. The default generated vector loads
  and stores were as good as or better than the forced policies.
- Compile-time and runtime delayed handoff points. Both made GEMM1 eligible
  later without materially reducing activation-TMA stalls.
- A fixed-work row assignment that eliminates the grid-stride loop. It adds
  masked work and loses load balance as routing density changes.
- Multiple `tl.range` pipeline stages. There is no useful producer/consumer
  pipeline within this copy kernel, and stages above one increased overhead.
- Launch-level `num_stages`. The emitted PTX was unchanged.

Evidence:

- Cache-policy sweep:
  `logs/triton_permute_cache_policy_ep8_20260723_115653/run.log`
- Handoff sweeps:
  `logs/triton_permute_handoff_sweep_20260723_120943/run.log`,
  `logs/triton_permute_grid_handoff_ep8_20260723_121733/run.log`, and
  `logs/triton_permute_runtime_handoff_probe_20260723_122448/run.log`
- Fixed-work schedule:
  `logs/triton_permute_fixed_work_rows_20260723_130720/run.log`
- Launch and loop pipeline-stage probes:
  `logs/triton_permute_num_stages_20260723_135336/run.log` and
  `logs/triton_permute_loop_pipeline_20260723_135906/run.log`

#### Try TMA for the BF16 activation gather

**Result: Rejected.** An in-kernel descriptor experiment did not compile
because of descriptor scratch requirements. A host-descriptor implementation
was made correct, but the irregular row gather plus one-row-at-a-time transfer
did not amortize TMA setup. It was slower than the vectorized global
load/store kernel. This agrees with the earlier W4A16 GEMM experiment: TMA is
valuable for regular activation tiles consumed by GEMM, but it is not
automatically a win for the routing permutation itself.

Evidence:

- In-kernel descriptor failure:
  `logs/triton_permute_tma_correctness_20260723_122939/run.log`
- Host-descriptor correctness and performance:
  `logs/triton_permute_tma_hostdesc_correctness_20260723_123120/run.log` and
  `logs/triton_permute_tma_sweep_20260723_123204/run.log`

#### Simplify indexing and inspect generated code

**Result: Retain unsigned route indexing and the 32-warp vector copy.**
Casting route indices and limits to unsigned values removes unnecessary signed
extension in the address path and remains correct for every valid route. Warp,
grid, and vector-width sweeps continued to favor a 1024-thread CTA and an
8192-BF16 static copy extent for the DeepSeek hidden size.

The generated PTX has the intended properties:

- `griddepcontrol.wait` and `griddepcontrol.launch_dependents` execute before
  activation loads;
- the copy lowers to vectorized `ld.global.v4.b32` and `st.global.v4.b32`;
- the kernel uses 26 registers per thread in the final measured form.

Correctness was checked for hidden sizes 7168, 12288, and 16384. The
compile-time K loop therefore preserves the fast single-iteration DeepSeek
case without limiting the helper to one model width.

Evidence:

- Warp/vector/grid sweep:
  `logs/triton_permute_vector_warp_grid_20260723_123643/run.log`
- Unsigned-index correctness and A/B:
  `logs/triton_permute_unsigned_correctness_20260723_124712/run.log`,
  `logs/triton_permute_index_ab_20260723_125406/run.log`, and
  `logs/triton_permute_unsigned_indices_test_20260723_130337/run.log`
- Wide-hidden correctness:
  `logs/triton_permute_correctness_20260723_142154/run.log`

#### Try tile-major and token-major source reuse

**Result: Rejected.** Tile-major scheduling did not improve route locality.
A more substantial token-major producer attempted to load each source token
once and scatter it to all selected local experts. It passed the focused
deterministic test, but the inverse-route construction and scattered stores
cost more than the saved BF16 reads. Relative to the route-major producer,
token-major reached only `0.9833x` geomean for EP8 and `0.8888x` for simulated
TP8, with the largest regressions at dense token counts. The route-major
contract also maps directly onto the already sorted GEMM1 rows and is easier
to synchronize with the GEMM consumer.

Evidence:

- Tile-major schedule:
  `logs/triton_permute_tile_schedule_20260723_124131/run.log`
- Token-major correctness, benchmark, and NSYS:
  `logs/triton_permute_token_major_correctness_20260723_131659/run.log`,
  `logs/triton_permute_token_major_cutedsl_20260723_132218/run.log`, and
  `logs/triton_permute_token_major_nsys_20260723_133548/`

#### Distinguish eager enqueueing from CUDA-graph PDL overlap

**Result: PDL overlap is confirmed in the serving-relevant CUDA-graph path.**
The distributed benchmark's eager local-MoE region shows the permute finishing
before GEMM1 begins. That is expected: Python/CuTe does not submit GEMM1 until
the producer launch returns, so no device mechanism can launch a child that is
not yet in the stream.

CUDA-graph replay changes this boundary condition because both nodes are
already instantiated. With `--cuda-graph-trace=node`, three EP8/4096 replays
showed:

| Producer duration | GEMM1 start after producer | Measured overlap |
|---:|---:|---:|
| `24.768 us` | `0.864 us` | `23.904 us` |
| `24.864 us` | `0.896 us` | `23.968 us` |
| `24.544 us` | `0.832 us` | `23.712 us` |

The activation consumer remains protected by GEMM1's dependency wait while
weight TMA and online dequantization become resident almost immediately. A
graph-level NSYS capture without node tracing hides child kernels and must not
be used to conclude that overlap is absent.

Evidence:

- Eager distributed profile:
  `logs/triton_permute_final_nsys_ep8_4096_20260723_141230/`
- Graph capture without node tracing:
  `logs/triton_permute_final_graph_nsys_ep8_4096_20260723_141641/`
- Graph-node profile and overlap extraction:
  `logs/triton_permute_final_graph_nodes_ep8_4096_20260723_141853/`

#### Correct the producer grid from measured occupancy

**Result: Use three quarters of the producer's two-CTA-per-SM capacity.**
The initial 136-CTA topology was described as reserving 12 B200 SMs, but NCU
showed the actual residency limit is two producer CTAs per SM:

- grid: 136 CTAs;
- block: 1024 threads;
- registers: 26 per thread;
- maximum residency: two CTAs per SM, limited by warp and register capacity;
- only 0.46 waves and 46.22% achieved occupancy;
- 21.98 us duration and approximately 1.58 TB/s DRAM bandwidth;
- long scoreboard was the dominant issue.

The corrected search therefore explored the 296-CTA machine capacity rather
than stopping near 148. A 224-CTA candidate improved EP8/4096 from
`0.463152 ms` to `0.454440 ms`; larger 256-296 CTA choices became less stable
because they left too little warp capacity for the dependent GEMM. The
portable choice is `3 * SM count / 2`, or 222 CTAs on B200: two producer CTAs
can reside per SM, and the grid consumes three quarters of that theoretical
capacity.

An exact 136-versus-222 full sweep was mostly neutral for EP8 and positive for
simulated TP8. Representative TP8 gains were `1.0089x` at 32 tokens,
`1.0138x` at 512, `1.0225x` at 2048, and `1.0232x` at 4096. EP8/4096 improved
`1.0309x`. One EP8/2048 sample was noisy and is not used as evidence for the
topology.

Evidence:

- NCU report and extracted details:
  `logs/triton_permute_final_ncu_ep8_4096_20260723_142256/`
- Grid-capacity sweep:
  `logs/triton_permute_two_cta_grid_ep8_20260723_142535/run.log`
- Exact 136-versus-222 full sweep:
  `logs/triton_permute_grid222_full_ab_20260723_142739/run.log`

#### Final correctness and measurement rules

The final implementation keeps the shared C++ permutation for non-PDL
execution and uses the W4A16-private Triton producer only when PDL is enabled.
This avoids changing the shared C++ MoE contract and limits the new scheduling
assumption to the BF16 activation path it was designed for.

Validation completed so far:

- direct route-copy checks at hidden sizes 7168, 12288, and 16384;
- all 13 `TestCuteDslMoeW4A16` cases;
- PTX inspection for entry-point grid dependency instructions and vectorized
  memory operations;
- NCU occupancy/resource inspection;
- eager and CUDA-graph-node NSYS captures.

For end-to-end A/B results, the producer must be selected before autotuning and
each producer must run in a separate process. Sharing one process lets the
first producer choose GEMM tactics that are then reused by the other producer;
this produced discontinuities at EP8/2048, EP8/4096, and simulated TP8/8.
Those results are useful for detecting interactions but are not a clean
production comparison.

Evidence:

- Full W4A16 correctness:
  `logs/triton_permute_correctness_20260723_142154/run.log`
- Shared-autotuner C++ versus final-Triton sweep:
  `logs/triton_permute_final_cxx_full_ab_20260723_143140/run.log`

#### Make route work tile-aware without retaining multiple vectors

**Result: Retain eight sequential rows per persistent work item.** The earlier
batched-row experiment retained several full vectors at once and increased
register pressure. The final schedule is different: one work item owns eight
consecutive rows from one routing tile, but loads and stores one row at a
time. It therefore amortizes tile metadata and persistent-loop arithmetic
without creating a multi-row tensor fragment.

This change fixed the sparse simulated-TP regression. At eight tokens it
improved latency from `0.10252 ms` to `0.08456 ms` (`1.2124x`). It also
improved EP8/4096 by `1.0201x`; the other representative points were within
about one percent. Groups of 16 and 32 rows reduced parallelism and were
rejected.

Evidence:

- Correctness (`13 passed`):
  `logs/triton_permute_row_group_correctness_20260723_145649/run.log`
- One-row versus eight-row schedule:
  `logs/triton_permute_sequential_row_groups_20260723_145741/run.log`
- Rejected 16- and 32-row groups:
  `logs/triton_permute_large_row_groups_20260723_150132/run.log`
- Independent C++ versus Triton sweep:
  `logs/triton_permute_final_independent_full_20260723_150420/run.log`

#### Co-design producer occupancy with the selected GEMM1 topology

**Result: Select the producer grid from GEMM1 M-cluster width.** A fixed 222
CTA grid is preferable for narrow simulated-TP GEMM1s because activation copy
throughput remains on the critical path. A 148 CTA grid is preferable for
wide EP8 GEMM1s because it leaves more scheduling capacity for the dependent
kernel.

Fixed-tactic measurements established the two regimes:

- EP8 with 148 CTAs: `0.332256 ms` at 2048 tokens and `0.415280 ms` at 4096;
  222 CTAs reached `0.333536 ms` and `0.424080 ms`.
- Simulated TP8 with 222 CTAs: `0.269376 ms` at 512 tokens,
  `0.351681 ms` at 1024, and `0.869824 ms` at 4096; 148 CTAs reached
  `0.283072 ms`, `0.357088 ms`, and `0.915776 ms`.

The implementation therefore computes the number of M clusters from the
already selected GEMM1 tactic. Eight or more M clusters use one producer CTA
per SM; narrower GEMM1s use three producer CTAs per two SMs. This derives the
choice from launch topology rather than naming EP or TP modes in the kernel.

Adding producer occupancy as an autotune axis was rejected. FlashInfer's
autotuner profiles eager stream execution, where GEMM1 has not been submitted
when the producer runs. It therefore cannot observe the CUDA-graph PDL
overlap and selected tactics that were slower during graph replay.

Evidence:

- EP8 grid sweep:
  `logs/triton_permute_rows8_grid_inprocess_20260723_152215/run.log`
- Simulated-TP8 grid sweep:
  `logs/triton_permute_rows8_tp_grid_ab_20260723_152400/run.log`
- Rejected autotune-axis sweep:
  `logs/triton_permute_autotuned_full_20260723_153008/run.log`
- Final topology-derived 1-4096 sweep:
  `logs/triton_permute_topology_grid_full_20260723_153539/run.log`

#### Final graph overlap and correctness

The final EP8/4096 CUDA-graph-node capture uses 148 producer CTAs, 1024
threads per CTA, and 30 registers per thread. Every replay launches GEMM1
before permutation completes:

| Producer duration | GEMM1 start after producer | Measured overlap |
|---:|---:|---:|
| `25.472 us` | `14.400 us` | `11.072 us` |
| `27.296 us` | `15.040 us` | `12.256 us` |
| `25.568 us` | `14.144 us` | `11.424 us` |

This confirms the intended PDL behavior without claiming that scheduling is
instantaneous. The dependent GEMM's activation wait protects correctness
while its independent weight load and online dequantization overlap the tail
of the producer.

Final validation:

- all 13 `TestCuteDslMoeW4A16` cases passed;
- the complete EP8 and simulated-TP8 token sweep ran from 1 through 4096;
- NSYS graph-node tracing confirmed producer/GEMM1 overlap.

Evidence:

- Final NSYS report and SQLite export:
  `logs/triton_permute_topology_graph_nodes_ep8_4096_20260723_154010/`
- Final W4A16 tests:
  `logs/triton_permute_final_correctness_20260723_154552/run.log`

#### Reverify the final producer after the PR cleanup

**Superseded result: remove the Triton PDL producer.** The first isolated
CUDA-graph benchmark suggested a `1.0147x` EP8 geomean gain and neutral
simulated TP8. That measurement omitted real distributed communication and
did not reproduce under the PR's layer-boundary benchmark, so it is not the
retention criterion.

The final comparison used `bench_cute_dsl_moe_distributed.py` with the exact
PR configuration: eight B200s, real EP8 and TP8 communication, per-token
NVFP4 4over6 MSE for W4A4, deterministic finalize, PDL enabled, 10 warmups,
100 cold-L2 timed iterations, and the complete 1-4096 global-token sweep.
Three independent processes were run per producer in interleaved order. Each
table entry is the median of the three run-level medians. `C++ / Triton`
below is shared-CUDA W4A16 latency divided by Triton W4A16 latency; values
below `1.0x` mean the shared C++ producer is faster.

EP8:

| Tokens | C++ W4A16 (ms) | Triton W4A16 (ms) | C++ / Triton |
|---:|---:|---:|---:|
| 1 | `0.254064` | `0.277808` | `0.9145x` |
| 2 | `0.261776` | `0.280848` | `0.9321x` |
| 4 | `0.296704` | `0.315200` | `0.9413x` |
| 8 | `0.324000` | `0.345968` | `0.9365x` |
| 16 | `0.355248` | `0.375776` | `0.9454x` |
| 32 | `0.390928` | `0.411936` | `0.9490x` |
| 64 | `0.420208` | `0.442800` | `0.9490x` |
| 128 | `0.434624` | `0.451904` | `0.9618x` |
| 256 | `0.443216` | `0.463424` | `0.9564x` |
| 512 | `0.453520` | `0.474736` | `0.9553x` |
| 1024 | `0.494960` | `0.520400` | `0.9511x` |
| 2048 | `0.628112` | `0.647392` | `0.9702x` |
| 4096 | `0.754112` | `0.794496` | `0.9492x` |
| **Geomean / min / max** | | | **`0.9470x / 0.9145x / 0.9702x`** |

TP8:

| Tokens | C++ W4A16 (ms) | Triton W4A16 (ms) | C++ / Triton |
|---:|---:|---:|---:|
| 1 | `0.252864` | `0.273888` | `0.9232x` |
| 2 | `0.255584` | `0.277008` | `0.9227x` |
| 4 | `0.257376` | `0.277008` | `0.9291x` |
| 8 | `0.289536` | `0.325296` | `0.8901x` |
| 16 | `0.326208` | `0.346832` | `0.9405x` |
| 32 | `0.380976` | `0.400176` | `0.9520x` |
| 64 | `0.419200` | `0.441744` | `0.9490x` |
| 128 | `0.451568` | `0.471216` | `0.9583x` |
| 256 | `0.475216` | `0.491520` | `0.9668x` |
| 512 | `0.492992` | `0.514016` | `0.9591x` |
| 1024 | `0.589648` | `0.629776` | `0.9363x` |
| 2048 | `0.782752` | `0.827232` | `0.9462x` |
| 4096 | `1.250368` | `1.251568` | `0.9990x` |
| **Geomean / min / max** | | | **`0.9437x / 0.8901x / 0.9990x`** |

Triton loses all 13 shapes in both real EP8 and real TP8. Its geomean
latency overhead is `5.6%` for EP8 and `6.0%` for TP8. W4A4 control
normalization preserves the conclusion: C++ / Triton is `0.9497x` for EP8
and `0.9396x` for TP8. Commit `0161de8e` is therefore reverted by
`ea0f446f`, restoring the original shared CUDA `moe_permute` path.

Evidence:

- Superseded isolated CUDA-graph A/B:
  `logs/pr4048_triton_pdl_permute_ab_20260723_235457/run.log`
- Real distributed A/B, per-run logs, parser, and full tables including W4A4
  controls:
  `logs/pr4048_distributed_permute_ab_20260724_001201/`

### Co-design deterministic W4A16 unpermute

#### Identify the apparent post-unpermute kernel

**Result: No MoE work to fuse.** The
`vectorized_elementwise_kernel<FillFunctor<signed char>>` after
`moeUnpermuteKernel` in the benchmark timeline is the benchmark's cold-L2
flush (`l2_flush.zero_()`), not an MoE operation. It must remain outside any
production-kernel co-design.

The shared deterministic W4A4/W4A16 reducer launches one 256-thread CTA per
token. Each thread repeatedly reloads the token's route mapping and scales
inside its hidden-vector loop. W4A4 writes GEMM2 output in expanded
token/top-k order and selects `input_is_expanded=True`; W4A16 preserves
expert-permuted rows so GEMM2 can use contiguous TMA stores. Copying W4A4's
expanded-order contract into W4A16 would trade away that store path, so the
first optimization keeps W4A16's existing GEMM2 layout.

#### Load route metadata once in a W4A16-private Triton reducer

**Result: Bitwise exact and faster.** A W4A16-private reducer loads the eight
route indices and FP32 scales once per token, waits on the PDL producer, then
accumulates each BF16 expert row in the original top-k order. It deliberately
does not parallel-reduce the top-k axis, preserving the exact FP32 expression
order and BF16 store contract.

The one-program-per-token, 32-warp kernel matched the shared C++ reducer
bitwise for `(17, 256)` and `(4096, 7168)`, including masked sparse routes.
Cold-L2 isolated speedups were:

| Routing | Tokens | C++ (ms) | Triton (ms) | Speedup |
|---|---:|---:|---:|---:|
| EP-like sparse | 32 | 0.011009 | 0.003808 | 2.891x |
| EP-like sparse | 512 | 0.015200 | 0.008352 | 1.820x |
| EP-like sparse | 4096 | 0.047488 | 0.046048 | 1.031x |
| TP-like dense | 32 | 0.019648 | 0.005024 | 3.911x |
| TP-like dense | 512 | 0.025664 | 0.016032 | 1.601x |
| TP-like dense | 4096 | 0.115952 | 0.091776 | 1.263x |

The complete W4A16 MoE sweep improved broadly versus the shared reducer,
including EP8/4096 from `0.448608 ms` to `0.437024 ms` and simulated
TP8/4096 from `0.905456 ms` to `0.838224 ms`. All 13 W4A16 numerical cases
passed.

Graph-node tracing exposed an important qualification: the 4096-CTA reducer
started only about `0.7 us` before GEMM2 completed, and its profiled EP8
duration was about `40 us` versus about `32 us` for the shared C++ reducer.
The end-to-end gain therefore cannot be attributed to more GEMM2 overlap and
must be evaluated as a complete graph, not from the isolated timing alone.

Evidence:

- Direct bitwise probe:
  `logs/w4a16_triton_unpermute_probe_20260723_171657/run.log`
- Isolated C++ versus Triton:
  `logs/w4a16_unpermute_isolated_ab_20260723_171751/run.log`
- Full W4A16 correctness:
  `logs/w4a16_triton_unpermute_correctness_20260723_172414/run.log`
- Full EP8 and simulated-TP8 sweep:
  `logs/w4a16_unpermute_e2e_candidate_full_20260723_172518/run.log`
- Warp-count sweep:
  `logs/w4a16_unpermute_warp_sweep_20260723_173005/run.log`
- CUDA-graph node profile:
  `logs/w4a16_unpermute_graph_nodes_ep8_4096_20260723_172756/`

#### Reject a two-CTA-per-SM persistent reducer

**Result: Smaller launch footprint did not improve the full chain.** A
persistent variant capped the grid at two 1024-thread CTAs per SM and assigned
tokens in grid-stride order. It remained bitwise exact, but serial token work
inside each CTA hurt sparse large-token execution. Isolated EP-like 4096-token
latency regressed from `0.043744 ms` for C++ to `0.050784 ms`; dense TP-like
execution still improved to `0.098992 ms` from `0.115872 ms`.

Against the one-program-per-token Triton candidate, the persistent full-MoE
sweep was about 1-5% slower across most simulated-TP8 points
(`0.862144 ms` versus `0.838224 ms` at 4096). EP8 was mostly 1-2% slower,
with only 2048 and 4096 tokens improving by roughly 1-2%. This is not a good
universal dispatch and is rejected. The next search should retain independent
per-token work while tuning CTA warp footprint for PDL coexistence.

Evidence:

- Persistent bitwise probe:
  `logs/w4a16_unpermute_persistent_probe_20260723_173415/run.log`
- Persistent isolated comparison:
  `logs/w4a16_unpermute_persistent_isolated_ab_20260723_173513/run.log`
- Persistent complete sweep:
  `logs/w4a16_unpermute_persistent_e2e_full_20260723_173718/run.log`

#### Co-design reducer CTA size with local route density

**Result: Use 16 warps only for the sparsest local partitions.** Although 32
warps minimized isolated reducer latency, 16 warps leave more scheduling
capacity for the producer GEMM2. On EP8, the 16-warp full-MoE path was neutral
at 32-512 tokens and improved 2048 from `0.323184 ms` to `0.317872 ms`
(`1.0167x`) and 4096 from `0.437024 ms` to `0.427920 ms` (`1.0213x`).

The same choice regressed dense simulated TP8, including 4096 from
`0.838224 ms` to `0.881552 ms`. EP4 also favored 32 warps at 4096
(`0.891520 ms` versus `0.946497 ms`). The implementation therefore uses 16
warps only when `top_k * num_local_experts <= num_experts`, which corresponds
to at most one expected local route per token under the static partition.
Denser configurations use 32 warps. This keeps the dispatch independent of
EP/TP names and token-count thresholds.

EP2 results were mixed: 32 warps improved 32 and 512 tokens, while 16 warps
improved 4096. Since EP2 is on the dense side of the selected boundary, it
uses 32 warps; adding token-count dispatch for one mixed regime is not
justified by this evidence.

Evidence:

- EP8 and simulated-TP8 16-warp subset:
  `logs/w4a16_unpermute_warps16_e2e_subset_20260723_174221/run.log`
- EP2/EP4 16-warp results:
  `logs/w4a16_unpermute_warps16_ep_density_20260723_174512/run.log`
- EP2/EP4 32-warp results:
  `logs/w4a16_unpermute_warps32_ep_density_20260723_174830/run.log`

#### Reject earlier GEMM2 dependent launch points

**Result: Keep the producer hint after GEMM2 completion.** Two earlier
`griddepcontrol.launch_dependents` positions were tested so the reducer could
load route metadata before GEMM2 completed:

1. after the weight TMA warp submitted its final load-to-transform stage;
2. after the transform warp finished its transform-to-MMA producer tail.

Both schedules were correct and did not hang, but both regressed EP8/4096
from about `0.428 ms` to `0.464 ms` (roughly 8%). Thousands of waiting
one-program-per-token reducer CTAs become eligible while GEMM2 still owns the
critical machine resources. Even the transform-tail point is too early to
recover useful overlap without slowing the producer.

The final implementation therefore retains GEMM2's existing late PDL hint.
The reducer still issues `griddepcontrol.wait` after loading route metadata,
so its contract remains valid if the producer scheduling changes later, but
this patch does not force early overlap that loses end-to-end performance.

Evidence:

- Weight-TMA-tail signal:
  `logs/w4a16_unpermute_early_signal_probe_20260723_175348/run.log`
- Transform-tail signal:
  `logs/w4a16_unpermute_transform_tail_signal_probe_20260723_175551/run.log`

#### Retain one 8192-element reduction fragment

**Result: Splitting the hidden vector is not worthwhile.** Reducing the
Triton block fragment from 8192 to 4096 elements makes each CTA process the
7168-wide output in two sequential passes. This lowers live vector state but
repeats route-selection work.

EP8 was neutral to slightly slower throughout. Dense simulated TP8 improved
by less than one percent through 2048 tokens, but regressed at 4096 from
`0.838224 ms` to `0.865856 ms` (`0.9681x`). The final kernel retains the
single 8192-element fragment; a token-count split is not justified.

Evidence:

- 4096-element fragment sweep:
  `logs/w4a16_unpermute_block4096_e2e_subset_20260723_175944/run.log`

#### Retain vectorized route metadata preload

**Result: The vector preload is faster than scalar route loads.** A cleaner
variant moved `griddepcontrol.wait` before metadata access and loaded one
mapping index and scale directly in each top-k iteration. It remained bitwise
exact, but EP8/4096 regressed from `0.427920 ms` to `0.442543 ms`. Dense
simulated TP8 was close at mid sizes but also regressed at 4096 from
`0.838224 ms` to `0.842800 ms`.

The final kernel therefore loads the small mapping and scale vectors together
before the PDL wait and selects each entry with `tl.gather`. Besides being
faster, this leaves useful independent work before the dependency barrier.

Evidence:

- Scalar metadata bitwise probe and sweep:
  `logs/w4a16_unpermute_scalar_metadata_probe_20260723_180332/run.log`

#### Reject L2-only loads for GEMM2 output

**Result: Preserve the default cache policy.** Adding Triton's `.cg` modifier
to the BF16 expert-row loads bypassed L1 for data that is read once by the
reducer. That intuition is wrong for this producer-consumer chain: GEMM2 has
just written the rows, and the default path preserves useful locality.

EP8/4096 regressed from `0.427920 ms` to `0.475072 ms`; simulated TP8/4096
also regressed to `0.846224 ms`. The final kernel uses the default load cache
policy.

Evidence:

- L2-only load sweep:
  `logs/w4a16_unpermute_cg_load_probe_20260723_180721/run.log`

#### Reject data-dependent sparse-route loops

**Result: Keep the fixed top-k loop.** Two variants attempted to exploit the
fact that an EP8 partition has one local route per token on average:

1. a dynamic loop that visited only valid local routes;
2. a narrower zero/one-route fast path with the fixed loop as its fallback.

Both variants matched the ordered C++ reducer bitwise for route counts from
zero through eight. The fully dynamic loop improved EP8/32 and EP8/512 by
about 1-1.4%, but regressed EP8/4096 from `0.427920 ms` to `0.445088 ms`.
The zero/one specialization was neutral at 32 and 512 tokens and regressed
4096 to `0.450112 ms`. Variable per-token control flow creates a long tail
that outweighs the skipped loads at large grids.

The final kernel uses a fixed compile-time `TOP_K` loop with masks for absent
routes. Route sparsity only controls the measured 16-versus-32-warp launch
choice; it does not alter accumulation control flow.

Evidence:

- Dynamic valid-route loop:
  `logs/w4a16_unpermute_sparse_route_loop_probe_20260723_181204/run.log`
- Zero/one-route bitwise coverage:
  `logs/w4a16_unpermute_sparse01_bitwise_20260723_183528/run.log`
- Zero/one-route EP8 sweep:
  `logs/w4a16_unpermute_sparse01_e2e_subset_20260723_183637/run.log`

#### Deterministic-finalize result and matched A/B correction

The retained reducer is one Triton program per output token with:

- route indices and scales loaded once before `griddepcontrol.wait`;
- a fixed compile-time top-k accumulation order in FP32;
- one 8192-element fragment for the 7168-wide DeepSeek hidden state;
- default cache policy for the BF16 GEMM2 rows;
- 16 warps for partitions with at most one expected local route per token,
  otherwise 32 warps.

An initial comparison between separate full sweeps appeared to improve 25 of
26 points, with `1.026x` EP8 and `1.091x` simulated-TP8 geometric means.
That comparison is not causal. Although `create_inputs` uses a fixed seed,
back-to-back measurements of the same implementation moved by roughly 4%,
which is larger than the claimed EP gain.

A subsequent interleaved A/B used identical tensors, one fixed autotuned GEMM
tactic per parallelism mode, 50 warmups, and 1000 measured graph replays per
sample. Its medians at 4096 tokens were:

| Mode | C++ reducer (ms) | Triton reducer (ms) | C++ / Triton |
|---|---:|---:|---:|
| EP8 | 0.490112 | 0.500624 | 0.9790x |
| simulated TP8 | 0.917201 | 0.894976 | 1.0248x |

The Triton reducer is therefore not a universal end-to-end win. It improves
the dense TP-like case by about 2.5%, where hoisting route metadata and using
a wider CTA amortizes eight valid-route loads. It regresses sparse EP8 by
about 2.1%, where most route loads are masked and the larger Triton CTA costs
more than the saved metadata work.

The matched EP8 NSYS traces confirm that PDL is not the source of the
difference: both reducers start about `0.7 us` before GEMM2 completes. The
C++ reducer takes `32.4-33.0 us`, while the Triton reducer takes
`45.2-47.3 us`. The complete profiled chain is correspondingly slower with
Triton. The apparent EP gain in the separate sweep was benchmark-state
variation, not overlap or a different GEMM topology.

Evidence:

- Final direct bitwise probe and 13-case W4A16 test class:
  `logs/w4a16_unpermute_final_correctness_20260723_183955/run.log`
- Final EP8 and simulated-TP8 sweep:
  `logs/w4a16_unpermute_final_e2e_full_20260723_184041/run.log`
- Final EP8/4096 graph-node trace:
  `logs/w4a16_unpermute_final_nsys_ep8_4096_20260723_184449/`
- Independently retuned matched A/B:
  `logs/w4a16_unpermute_matched_ab_20260723_190221/run.log`
- Fixed-tactic interleaved A/B:
  `logs/w4a16_unpermute_interleaved_ab_20260723_190625/run.log`

### C++ deterministic-finalize optimization

#### Reject block-wide route metadata caching

**Result: Preserve the existing per-vector route loads.** The first C++
experiment staged each token's route indices and FP32-converted scales in
dynamic shared memory before `cudaGridDependencySynchronize()`. This removed
redundant global metadata loads from the hidden-dimension loop and preserved
the strict route accumulation order, but required a block-wide synchronization.

The complete deterministic non-fused correctness subset passed:
`39 passed, 39 deselected`. Matched CUDA-graph measurements used the same
W4A16-only EP8 and simulated-TP8 setup, 50 warmups, and 1000 iterations. The
candidate regressed EP8/2048 from `0.340672 ms` to `0.349680 ms` (2.6%) and
regressed multiple small TP8 points. EP8/4096 improved by 0.9%, while
TP8/4096 was effectively flat, so the isolated endpoint gain does not justify
the broader regressions or extra synchronization.

The block-wide barrier costs more than the small route metadata cache saves.
The experiment was removed before trying launch-geometry and warp-local
alternatives.

Evidence:

- Correctness:
  `logs/cpp_unpermute_correctness_20260723_192102/run.log`
- Matched parent baseline:
  `logs/cpp_unpermute_baseline_matched_20260723_192844/run.log`
- Matched shared-memory candidate:
  `logs/cpp_unpermute_candidate_matched_20260723_193132/run.log`

#### Compact-row 512-thread launch

**Result: Useful only as a small-workload specialization.** The C++ reducer
normally launches 256 threads per token. A 512-thread specialization for the
compact permuted-input path leaves the shared expanded-input W4A4 path
unchanged and reduces the 7168-wide row loop from four vector iterations per
thread to two.

The focused W4A16 deterministic cases passed (`13 passed`). Against the
matched 256-thread baseline, 512 threads improved EP8 at 32, 512, and 1024
tokens by 0.9-1.0% and improved simulated TP8/32 by 2.4%. It was neutral
around TP8/512-2048, but regressed EP8/2048 by 2.0% and TP8/4096 by 1.1%.
The wider block is therefore not suitable as an unconditional replacement.
The result motivates a low-token launch specialization and a 1024-thread
probe rather than changing the large-grid path.

Evidence:

- Focused correctness:
  `logs/cpp_unpermute_512_correctness_20260723_193805/run.log`
- Matched subset:
  `logs/cpp_unpermute_512_matched_subset_20260723_193924/run.log`

#### Reject launch-geometry specialization

**Result: Restore the unmodified 256-thread C++ reducer.** A 1024-thread
compact-row launch passed the same focused W4A16 correctness cases and exposed
more parallelism within each token. Against the matched 256-thread baseline it
improved EP8 by 1.5-6.3% and simulated TP8 by 3.0-17.7% from 1 through 128
tokens. The benefit quickly disappeared: EP8/512 improved only 0.3%, while
TP8/512 regressed 0.9%. At 4096 tokens, EP8 regressed from `0.457248 ms` to
`0.510688 ms` and TP8 regressed from `0.917679 ms` to `0.972704 ms`.

A token-count dispatch could retain the small-grid gains, but it would add
another static model- and GPU-sensitive heuristic to a shared reducer for
limited end-to-end headroom. Together with the inconclusive 512-thread tier,
this does not justify production complexity. Keep the original 256-thread
implementation and revisit only if finalize becomes a larger fraction of the
complete MoE path.

Evidence:

- Focused correctness:
  `logs/cpp_unpermute_1024_correctness_20260723_194346/run.log`
- Matched launch probe:
  `logs/cpp_unpermute_1024_matched_probe_20260723_194418/run.log`

### W4A16-local Triton routing

#### Reject fused route assignment and BF16 permutation

**Result: Keep expert-contiguous permutation.** A W4A16-local Triton
prototype replaced the shared C++ `routingIndicesClusterKernel` without
editing its source. A one-CTA prefix kernel counted local routes and emitted
tile metadata. A persistent second kernel then atomically assigned each route
within its expert segment, wrote both route maps, and copied the corresponding
BF16 activation row. Both kernels used PDL, and the second kernel launched
GEMM1 dependents before starting its route work.

The route/map invariants passed, as did focused wrapper and EP numerical
tests. The fused path improved the complete MoE by about 0.7% at EP8/32 and
1.1% at simulated-TP8/32. It crossed over around 128-256 tokens and regressed
EP8/4096 from `0.458688 ms` to `0.499168 ms` (8.8%).

NSYS identifies the cause. At EP8/4096, the Triton prefix costs only
`11.7 us`, but the fused rank-and-copy kernel costs `76.6 us`. The retained
expert-contiguous Triton gather costs about `22.6 us`; combining atomic route
assignment with the copy scatters output rows and makes every persistent CTA
walk all global routes, including the seven-eighths filtered out by EP8.
Preserving expert-contiguous route maps is more important than removing the
map read or one logical traversal.

Evidence:

- Route/map invariant probe:
  `logs/w4a16_triton_fused_route_permute_invariants_20260723_203904/run.log`
- Focused numerical smoke:
  `logs/w4a16_triton_fused_route_permute_moe_smoke_20260723_203931/run.log`
- Matched EP8 and simulated-TP8 sweep:
  `logs/w4a16_triton_fused_route_permute_subset_20260723_204213/run.log`
- EP8/4096 graph-node trace:
  `logs/w4a16_triton_fused_route_permute_nsys_nodes_ep8_4096_20260723_204821/`

#### Reject one-CTA expert-contiguous sorting

**Result: The shared sorter remains substantially better.** A second
prototype preserved the existing expert-contiguous BF16 gather. One Triton
CTA counted routes for the 32 local EP8 experts, generated tile metadata, and
made a second pass over the routes to assign both maps with per-expert
cumsums. Simulated TP8 continued to use the existing C++ sorter.

The focused wrapper and EP numerical tests passed. The expert-by-route tensor
work in the second pass was much too expensive, however. EP8/32 regressed
from `0.157952 ms` to `0.160064 ms`; EP8/4096 regressed from `0.458688 ms`
to `1.024991 ms`. Simulated TP8 remained within baseline variation because
the fallback was unchanged.

This closes the two straightforward Triton replacements:

- assigning route ranks while copying loses the contiguous activation-copy
  contract;
- assigning all expert-contiguous ranks in one CTA creates excessive
  expert-by-route work.

A viable Triton replacement would need a parallel compact sort with the same
expert-contiguous output and no extra launch on the critical path. The
existing shared C++ routing kernel already provides that contract in about
`7.7 us` at EP8/4096, leaving very little headroom.

Evidence:

- Initial compile diagnostic:
  `logs/w4a16_triton_contiguous_sort_smoke_20260723_205508/run.log`
- Focused numerical smoke:
  `logs/w4a16_triton_contiguous_sort_smoke_fixed_20260723_205701/run.log`
- Matched EP8 and simulated-TP8 sweep:
  `logs/w4a16_triton_contiguous_sort_subset_20260723_205736/run.log`

### Static scheduler raster direction

#### Keep M-major tactics and fix N-major termination

**Result: Do not add raster direction to the W4A16 autotune space.** W4A4
defines 16 tactics. W4A16 currently defines 409 before runtime filtering, so
independently tuning GEMM1 and GEMM2 raster direction would expand that space
to 1,636 tactics.

A fixed-tactic sweep disabled GEMM1 CLC and evaluated all four GEMM1/GEMM2
M-major and N-major combinations. N-major GEMM1 materially regressed. N-major
GEMM2 produced a few isolated simulated-TP8 improvements, but no robust
end-to-end gain. The best static combination improved over static M-major by
only `1.0011x` geometric mean for EP8 and `1.0053x` for simulated TP8, with
maxima of `1.0095x` and `1.0264x`. The production CLC path remained faster
than the static oracle for EP8 and effectively tied it for simulated TP8.

The experiment exposed a real scheduler gap. The CUTLASS static persistent
scheduler leaves its outer mode unbounded. The previous loop terminated on
routed N, which is correct only when M is the inner mode. With N as the inner
mode, N wraps while M remains unbounded, so the kernel never terminated. The
fix retains explicit compile-time M-major and N-major loops: M-major preserves
the established path, while N-major terminates on the finite M extent, skips
padded routed-N tiles, and publishes one final sentinel.

Evidence:

- Initial hang:
  `logs/w4a16_static_raster_sweep_20260723_192101/run.log`
- Fixed raster sweep:
  `logs/w4a16_static_raster_fixed_sweep_20260723_194844/run.log`
- Final route-tile numerical validation:
  `logs/w4a16_raster_n_static_tests_20260724_032351/run.log`

### Enable CLC for GEMM2

**Result: Rejected; retain GEMM1-only CLC.** The prototype removed the
activation-type guard from the multiwave CLC threshold, allowing both GEMM1
and GEMM2 to use the dynamic persistent scheduler. This is compatible with
the PDL ordering: the GEMM2 scheduler and weight/dequantization warps can run
before GEMM1 completes, while GEMM2's activation-TMA warp remains the sole
role that executes `griddepcontrol_wait()`.

The PDL-on deterministic/fused-finalize, EP, and CUDA-graph cases all
completed without a hang and passed numerically (`16 passed`). Performance did
not justify the broader scheduler, however. Against a same-node GEMM1-only CLC
baseline, EP8 geometric-mean speedup was `0.9932x` (range
`0.9363x`-`1.0130x`) and simulated TP8 was `0.9101x` (range
`0.8475x`-`1.0057x`). EP8 had several 0.6%-1.3% midrange gains, but regressed
5.1% at 4096 tokens. TP8 regressed materially across nearly the entire sweep.
The dynamic claim overhead and changed locality outweigh any GEMM2 load
balancing benefit, so the activation-type guard was restored.

Evidence:

- Same-node GEMM1-only CLC baseline:
  `logs/w4a16_gemm2_clc_baseline_20260724_033255/run.log`
- PDL, finalize, EP, and CUDA-graph correctness:
  `logs/w4a16_gemm2_clc_correctness_20260724_034036/run.log`
- Same-node GEMM1+GEMM2 CLC candidate:
  `logs/w4a16_gemm2_clc_candidate_20260724_034121/run.log`

### Fix the W4A16 MMA K tile at 256

**Result: Promising; candidate left unstaged for review.** W4A4 has a fixed
effective K tile of 256. Restricting W4A16 to the same K tile removes K=64 and
K=128 from both GEMM tactic lists and changes the correctness fallback from
K=128 to K=256. This reduces the pre-filter autotune space from 409 tactics to
41.

The candidate was compared against the immediately preceding same-node
GEMM1-only CLC baseline. Both runs used a B200 with CUDA 13.2, CUDA graphs,
CUPTI, PDL, the wrapper API, deterministic non-fused finalize, 10 warmups, 100
iterations, and only the CuTe DSL W4A16 backend. Ratios below are
`K256-only / full-K`; positive percentages are slowdowns.

| Tokens | EP8 full K (ms) | EP8 K256 (ms) | EP8 slowdown | TP8 full K (ms) | TP8 K256 (ms) | TP8 slowdown |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.046225 | 0.045808 | -0.902% | 0.050464 | 0.050400 | -0.127% |
| 2 | 0.053184 | 0.053600 | +0.782% | 0.054480 | 0.054335 | -0.266% |
| 4 | 0.076640 | 0.076512 | -0.167% | 0.060192 | 0.060272 | +0.133% |
| 8 | 0.097344 | 0.097103 | -0.248% | 0.087120 | 0.086832 | -0.331% |
| 16 | 0.108527 | 0.108416 | -0.102% | 0.120912 | 0.120144 | -0.635% |
| 32 | 0.160224 | 0.160016 | -0.130% | 0.175343 | 0.175600 | +0.147% |
| 64 | 0.211968 | 0.211935 | -0.016% | 0.230256 | 0.229440 | -0.354% |
| 128 | 0.216736 | 0.217007 | +0.125% | 0.240623 | 0.240319 | -0.126% |
| 256 | 0.223503 | 0.223967 | +0.208% | 0.249792 | 0.249104 | -0.275% |
| 512 | 0.230608 | 0.230560 | -0.021% | 0.269039 | 0.269231 | +0.071% |
| 1024 | 0.246320 | 0.245647 | -0.273% | 0.346449 | 0.346927 | +0.138% |
| 2048 | 0.314337 | 0.314816 | +0.152% | 0.543488 | 0.541200 | -0.421% |
| 4096 | 0.409328 | 0.409471 | +0.035% | 0.892146 | 0.876143 | -1.794% |
| **Geomean** |  |  | **-0.043%** |  |  | **-0.297%** |

There is no measurable steady-state regression in this sweep. EP8 is at
parity, and simulated TP8 is slightly faster, although most point differences
remain within normal run-to-run variation. The substantially smaller tactic
space is the stronger reason to retain the candidate and repeat only if later
pipeline changes make K sensitivity visible again.

Evidence:

- Full K=64/128/256 baseline:
  `logs/w4a16_gemm2_clc_baseline_20260724_033255/run.log`
- K=256-only candidate and watchdog:
  `logs/w4a16_k256_only_20260724_043000/`

### Pair GEMM tactics at the MoE level

**Result: Keep.** The K=256-only search still formed the full Cartesian product
of three GEMM1 and three GEMM2 topologies. The implementation now has one
`get_w4a16_moe_valid_tactics` enumerator and stores only measured topology
pairs. A W4A16 MoE tactic is `(gemm1_tactic, gemm2_tactic)`; the shared routed
row tile is already the N dimension of both GEMM MMA tilers and is no longer
duplicated as a third tuple field.

An initial four-pair cut produced 19 tactics but regressed geometric-mean
latency by 0.47% for EP8 and 0.92% for simulated TP8. Debug autotuning with the
independent 41-tactic search showed that the missing
`(GEMM1 256/2CTA, GEMM2 128/2CTA)` pair was selected for most small and
midrange TP8 profiles and several EP8 profiles. Retaining that reverse mixed
pair produces 23 tactics and recovers the regression.

Both matched runs used a B200 with CUDA 13.2, CUDA graphs, CUPTI, PDL, the
wrapper API, deterministic non-fused finalize, 10 warmups, 100 iterations, and
only the CuTe DSL W4A16 backend. Deltas are `23-pair / 41-independent`;
negative values are improvements.

| Tokens | EP8 independent (ms) | EP8 paired (ms) | EP8 delta | TP8 independent (ms) | TP8 paired (ms) | TP8 delta |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.045808 | 0.046112 | +0.664% | 0.050400 | 0.050400 | +0.000% |
| 2 | 0.053600 | 0.053216 | -0.716% | 0.054335 | 0.054112 | -0.410% |
| 4 | 0.076512 | 0.076576 | +0.084% | 0.060272 | 0.060224 | -0.080% |
| 8 | 0.097103 | 0.097136 | +0.034% | 0.086832 | 0.086704 | -0.147% |
| 16 | 0.108416 | 0.108384 | -0.030% | 0.120144 | 0.120223 | +0.066% |
| 32 | 0.160016 | 0.160096 | +0.050% | 0.175600 | 0.175551 | -0.028% |
| 64 | 0.211935 | 0.212064 | +0.061% | 0.229440 | 0.229376 | -0.028% |
| 128 | 0.217007 | 0.217024 | +0.008% | 0.240319 | 0.240176 | -0.060% |
| 256 | 0.223967 | 0.224208 | +0.108% | 0.249104 | 0.249280 | +0.071% |
| 512 | 0.230560 | 0.230495 | -0.028% | 0.269231 | 0.269312 | +0.030% |
| 1024 | 0.245647 | 0.245664 | +0.007% | 0.346927 | 0.346672 | -0.074% |
| 2048 | 0.314816 | 0.314624 | -0.061% | 0.541200 | 0.540271 | -0.172% |
| 4096 | 0.409471 | 0.407199 | -0.555% | 0.876143 | 0.875535 | -0.069% |
| **Geomean** |  |  | **-0.029%** |  |  | **-0.069%** |

The common routed-row tile remains a real kernel constraint. `moe_sort`
produces one expert/tile metadata table using that tile size, and both GEMMs
consume the same table while deriving its length from their MMA N tile.
Caller-supplied tactics therefore reject mismatched GEMM N tiles.

Validation and evidence:

- Independent-tactic selection trace:
  `logs/w4a16_independent_k256_tactic_debug_20260724_045800/run.log`
- Pair-only structural and route-tile numerical tests:
  `logs/w4a16_pair_tactic_test_20260724_042226/run.log`
- Four-pair intermediate candidate:
  `logs/w4a16_curated_k256_20260724_045200/run.log`
- Final five-pair benchmark:
  `logs/w4a16_paired_k256_20260724_042350/run.log`

### Current-head GEMM2 optimization baseline

**Result: Diagnostic baseline.** Commit `b2442579` was measured on
`w4a16-opt132` before changing the GEMM2 pipeline. The run used CUDA 13.2,
CUPTI, CUDA graphs, PDL, deterministic non-fused finalize, 10 warmups, and 100
iterations. FP4 activation quantization and 4over6 were disabled; W4A16
consumed BF16 directly.

```bash
CUDA_VISIBLE_DEVICES=0 \
FLASHINFER_DISABLE_VERSION_CHECK=1 \
TRTLLM_ENABLE_PDL=1 \
python3 benchmarks/bench_moe_deepseek.py \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,1024,2048,4096 \
  --ep 8 \
  --no-fused-finalize

CUDA_VISIBLE_DEVICES=0 \
FLASHINFER_DISABLE_VERSION_CHECK=1 \
TRTLLM_ENABLE_PDL=1 \
python3 benchmarks/bench_moe_deepseek.py \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,1024,2048,4096 \
  --ep 1 \
  --tp 8 \
  --no-fused-finalize
```

| Tokens | EP8 W4A16 (ms) | Simulated TP8 W4A16 (ms) |
|---:|---:|---:|
| 1 | 0.046 | 0.050 |
| 2 | 0.054 | 0.054 |
| 4 | 0.078 | 0.060 |
| 8 | 0.098 | 0.088 |
| 16 | 0.109 | 0.120 |
| 32 | 0.160 | 0.175 |
| 64 | 0.213 | 0.230 |
| 128 | 0.216 | 0.240 |
| 256 | 0.224 | 0.250 |
| 512 | 0.231 | 0.269 |
| 1024 | 0.246 | 0.347 |
| 2048 | 0.313 | 0.544 |
| 4096 | 0.450 | 0.888 |

The latest EP8/4096 NCU report identifies GEMM1 as invocation 3 with grid
`(32, 287, 1)` and GEMM2 as invocation 4 with persistent grid `(2, 1, 74)`.
GEMM1 tensor-pipe activity is `77.82%` of active cycles; GEMM2 is `70.06%`.
GEMM2 takes `154.53 us`, has a `58.36%` L2 hit rate, and is dominated by
long-scoreboard sampling. Source attribution shows backpressure at both TMA
producer acquires, transform waits on packed-weight input, and epilogue waits
on accumulator completion. This makes GEMM2 feed scheduling and lookahead the
first optimization target; GEMM1 remains unchanged during initial experiments.

Evidence:

- Full traced baseline:
  `logs/w4a16_gemm2_opt_baseline_b2442579_20260724_100446/`
- Source-embedded NCU report:
  `logs/pr4048_cuda132_ncu_b2442579_20260724_022944/reports/ep_w4a16_t4096.ncu-rep`

### TMA L2 prefetch for GEMM2 weights and scales

**Result: Rejected in broad form.** The first GEMM2-only prototype mirrored
the CUTLASS CuTe DSL tutorial: it prefetched the first load-pipeline-depth K
tiles of both packed weights and E4M3 scales, then maintained the same rolling
prefetch distance. GEMM1 and activation TMA were unchanged. A 4096-token EP8
smoke completed without a compile error, illegal instruction, or pipeline
hang.

The complete matched sweep shows that the extra prefetch traffic and issue
work exceed the hidden latency. Speedup is baseline latency divided by
candidate latency.

| Tokens | EP8 baseline (ms) | EP8 prefetch (ms) | EP8 speedup | TP8 baseline (ms) | TP8 prefetch (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.046 | 0.046 | 1.0000x | 0.050 | 0.050 | 1.0000x |
| 2 | 0.054 | 0.054 | 1.0000x | 0.054 | 0.055 | 0.9818x |
| 4 | 0.078 | 0.078 | 1.0000x | 0.060 | 0.060 | 1.0000x |
| 8 | 0.098 | 0.098 | 1.0000x | 0.088 | 0.088 | 1.0000x |
| 16 | 0.109 | 0.110 | 0.9909x | 0.120 | 0.121 | 0.9917x |
| 32 | 0.160 | 0.162 | 0.9877x | 0.175 | 0.178 | 0.9831x |
| 64 | 0.213 | 0.214 | 0.9953x | 0.230 | 0.235 | 0.9787x |
| 128 | 0.216 | 0.217 | 0.9954x | 0.240 | 0.246 | 0.9756x |
| 256 | 0.224 | 0.225 | 0.9956x | 0.250 | 0.256 | 0.9766x |
| 512 | 0.231 | 0.231 | 1.0000x | 0.269 | 0.272 | 0.9890x |
| 1024 | 0.246 | 0.248 | 0.9919x | 0.347 | 0.347 | 1.0000x |
| 2048 | 0.313 | 0.317 | 0.9874x | 0.544 | 0.544 | 1.0000x |
| 4096 | 0.450 | 0.457 | 0.9847x | 0.888 | 0.865 | 1.0266x |
| **Geomean** |  |  | **0.9945x** |  |  | **0.9925x** |

The isolated TP8/4096 improvement is not enough to retain a design that
regresses the EP8 target broadly. The next refinement removes initial
prefetches and all scale prefetches, retaining only rolling packed-weight
lookahead before later TMA stages.

Evidence:

- Compile and hang smoke:
  `logs/w4a16_gemm2_l2_prefetch_smoke_20260724_1015/`
- Full EP8 and simulated-TP8 sweep:
  `logs/w4a16_gemm2_l2_prefetch_b1e32685_20260724_1017/`

### Rolling TMA L2 prefetch for GEMM2 packed weights only

**Result: Rejected.** This refinement removed the initial prefetch phase and
all scale prefetches. The weight TMA warp only issued a rolling
`cute.prefetch` for the packed-weight K tile one load-pipeline depth ahead.
The full matched sweep remained neutral at most sizes but regressed the primary
EP8/4096 case by 3.0%. Speedup is baseline latency divided by candidate
latency.

| Tokens | EP8 baseline (ms) | EP8 prefetch (ms) | EP8 speedup | TP8 baseline (ms) | TP8 prefetch (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.046 | 0.046 | 1.0000x | 0.050 | 0.050 | 1.0000x |
| 2 | 0.054 | 0.054 | 1.0000x | 0.054 | 0.054 | 1.0000x |
| 4 | 0.078 | 0.078 | 1.0000x | 0.060 | 0.060 | 1.0000x |
| 8 | 0.098 | 0.099 | 0.9899x | 0.088 | 0.088 | 1.0000x |
| 16 | 0.109 | 0.109 | 1.0000x | 0.120 | 0.120 | 1.0000x |
| 32 | 0.160 | 0.161 | 0.9938x | 0.175 | 0.176 | 0.9943x |
| 64 | 0.213 | 0.213 | 1.0000x | 0.230 | 0.231 | 0.9957x |
| 128 | 0.216 | 0.216 | 1.0000x | 0.240 | 0.241 | 0.9959x |
| 256 | 0.224 | 0.224 | 1.0000x | 0.250 | 0.250 | 1.0000x |
| 512 | 0.231 | 0.231 | 1.0000x | 0.269 | 0.270 | 0.9963x |
| 1024 | 0.246 | 0.249 | 0.9880x | 0.347 | 0.347 | 1.0000x |
| 2048 | 0.313 | 0.314 | 0.9968x | 0.544 | 0.544 | 1.0000x |
| 4096 | 0.450 | 0.464 | 0.9698x | 0.888 | 0.883 | 1.0057x |
| **Geomean** |  |  | **0.9952x** |  |  | **0.9991x** |

Evidence:

- Compile and hang smoke:
  `logs/w4a16_gemm2_rolling_weight_prefetch_smoke_20260724_1021/`
- Full EP8 and simulated-TP8 sweep:
  `logs/w4a16_gemm2_rolling_weight_prefetch_3b07ca6f_20260724_1022/`

### Existing L2-prefetch contracts

FlashInfer's direct `prefetch.global.L2` wrapper is used by
`include/flashinfer/concat_mla.cuh`. Each lane prefetches the address it will
load from the next logical row, one software-pipeline iteration ahead. This is
a non-blocking cache-line hint for a small sequential access, not a bulk TMA
transaction and not a completion-tracked pipeline stage.

The SM12x W4A16 helper module also defines `prefetch_global_l2`, but the
repository has no call site for that helper. Its neighboring `ld.global.nc`
helpers are used by direct-load microkernels; the unused prefetch wrapper is
therefore not evidence for applying the hint to a TMA operand.

The bundled CUB transform kernel applies the same PTX instruction to a larger
tile by assigning 128-byte cache lines across threads:
`threadIdx.x * 128`, then `blockDim.x * 128` strides. This is the closest
existing pattern for explicitly covering a packed-weight tile with the direct
PTX hint.

The bundled CUTLASS GEMM weight-prefetch example uses a different contract: a
dedicated warp issues TMA loads into throwaway shared memory before the
dependent-grid wait. CuTe DSL's `cute.prefetch` represents this bulk TMA
family. The two rejected experiments above already test that family for this
kernel.

W4A16 already calls `cpasync.prefetch_descriptor` for its weight, scale,
activation, and output TMA descriptors. Direct `prefetch.global.L2` can only
add cache-line traffic; it cannot shorten descriptor access or participate in
the transaction-barrier contract used by the actual loads.

The direct-PTX GEMM2 experiment therefore uses one weight-producer warp,
128-byte line ownership across its lanes, and rolling K-tile lookahead. It is
intended to test whether lighter cache-line hints avoid the overhead of bulk
TMA prefetch; it does not assume that the existing sequential MLA use case
transfers directly to MoE.

### Direct PTX L2 prefetch for GEMM2 packed weights

**Result: Rejected.** The first implementation attempted to derive raw
addresses from the TMA tensor and failed during JIT because the TMA iterator is
a descriptor/coordinate tuple rather than a raw pointer. The corrected
prototype kept the TMA tensor for the real transfer and separately threaded
the original logical packed-weight tensor to the kernel solely for address
generation.

The weight TMA warp assigned one 128-byte cache line to each lane and issued
`prefetch.global.L2` for a future K tile one load-pipeline depth ahead. GEMM1
was unchanged. A guarded EP8/4096 smoke completed at 0.452 ms without a hang;
the full sweep then exposed a 9.5% EP8 regression at 2048 tokens. Speedup is
baseline latency divided by candidate latency.

| Tokens | EP8 baseline (ms) | EP8 direct PTX (ms) | EP8 speedup | TP8 baseline (ms) | TP8 direct PTX (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.046 | 0.046 | 1.0000x | 0.050 | 0.050 | 1.0000x |
| 2 | 0.054 | 0.054 | 1.0000x | 0.054 | 0.054 | 1.0000x |
| 4 | 0.078 | 0.078 | 1.0000x | 0.060 | 0.060 | 1.0000x |
| 8 | 0.098 | 0.098 | 1.0000x | 0.088 | 0.088 | 1.0000x |
| 16 | 0.109 | 0.109 | 1.0000x | 0.120 | 0.120 | 1.0000x |
| 32 | 0.160 | 0.160 | 1.0000x | 0.175 | 0.176 | 0.9943x |
| 64 | 0.213 | 0.213 | 1.0000x | 0.230 | 0.231 | 0.9957x |
| 128 | 0.216 | 0.216 | 1.0000x | 0.240 | 0.241 | 0.9959x |
| 256 | 0.224 | 0.224 | 1.0000x | 0.250 | 0.251 | 0.9960x |
| 512 | 0.231 | 0.231 | 1.0000x | 0.269 | 0.270 | 0.9963x |
| 1024 | 0.246 | 0.246 | 1.0000x | 0.347 | 0.348 | 0.9971x |
| 2048 | 0.313 | 0.346 | 0.9046x | 0.544 | 0.546 | 0.9963x |
| 4096 | 0.450 | 0.457 | 0.9847x | 0.888 | 0.887 | 1.0011x |
| **Geomean** |  |  | **0.9911x** |  |  | **0.9979x** |

The existing FlashInfer use in `concat_mla.cuh` is the intended lightweight
case: each lane hints the next sequential row shortly before its own ordinary
global load. CUB broadens the same instruction to tile coverage, but distributes
the work across a full block. Here one producer warp must issue 128 hints plus
address arithmetic for each future packed-weight K tile, while the actual
transfer remains an asynchronous TMA operation with its own pipeline. The hint
neither advances that pipeline nor supplies completion semantics. The measured
overhead outweighs any L2-latency reduction, so direct PTX prefetch is not
appropriate for the current GEMM2 producer design.

Evidence:

- Initial descriptor-address compile failure:
  `logs/w4a16_gemm2_ptx_l2_prefetch_smoke_20260724_103030/`
- Corrected compile and hang smoke:
  `logs/w4a16_gemm2_ptx_l2_prefetch_smoke2_20260724_103343/`
- Full EP8 and simulated-TP8 sweep:
  `logs/w4a16_gemm2_ptx_l2_prefetch_4890890f_20260724_103533/`

### Trace the selected GEMM2 tactics

**Result: Diagnostic only.** A DEBUG autotuner run captured the selected
W4A16 tactic for each hybrid-profile bucket. GEMM1 generally retains M256,
while GEMM2 uses M128 through the medium buckets and switches to M256 for the
dense buckets. The routed-row tile grows with the workload:

| Profile tokens | GEMM1 topology | GEMM2 topology | Route tile |
|---:|---|---|---:|
| 1 | M256/2-CTA | M256/2-CTA | 16 |
| 2-256 | M256/2-CTA | M128/2-CTA | 16 |
| 512 | M256/2-CTA | M128/2-CTA | 32 |
| 768-1792 | M256/2-CTA | M128/2-CTA | 64 |
| 2048-3584 | M256/2-CTA | M256/2-CTA | 128 |
| 4096 | M256/2-CTA | M256/2-CTA | 192 |

At the 4096-token profile, the paired M256 route-192 tactic measured
`0.435763 ms`; paired M256 route-128 measured `0.470221 ms`, and
GEMM1-M256/GEMM2-M128 route-128 measured `0.475101 ms`. Route geometry is
therefore material: the dense route-192 choice is about 7.9% faster than the
otherwise equivalent route-128 pair.

GEMM2 has K=2048, or only eight K256 stages, while GEMM1 has K=7168, or 28
stages. Together with GEMM2's lower tensor-pipe utilization, this shifts the
next investigation toward short-K startup/drain overhead and persistent-tile
traversal. It does not support another broad prefetch experiment.

Evidence:

- Selected-tactic DEBUG trace:
  `logs/w4a16_gemm2_tactic_debug_b2442579_20260724_104415/run.log`

### Route-192 overlapping accumulator

**Result: Rejected.** The dense route-192 tactic normally allocates one
256-column accumulator stage alongside two 256-column decoded-weight stages.
This prototype mirrored the existing W4A4 overlapping-accumulator protocol:
two logical N192 accumulators shared a 256-column TMEM region with a 64-column
stage stride, the epilogue consumed the 128-column overlap first, and the
single accumulator barrier was released before consuming each disjoint
64-column tail. A focused route-192 numerical test passed and no benchmark
hung.

An isolated EP8/4096 smoke initially measured 0.425 ms against the 0.450 ms
baseline, but neither the full sweep nor matched Nsight Systems traces
reproduced that gain. Speedup is baseline latency divided by candidate
latency.

| Tokens | EP8 baseline (ms) | EP8 overlap (ms) | EP8 speedup | TP8 baseline (ms) | TP8 overlap (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.046 | 0.046 | 1.0000x | 0.050 | 0.050 | 1.0000x |
| 2 | 0.054 | 0.055 | 0.9818x | 0.054 | 0.054 | 1.0000x |
| 4 | 0.078 | 0.078 | 1.0000x | 0.060 | 0.060 | 1.0000x |
| 8 | 0.098 | 0.098 | 1.0000x | 0.088 | 0.088 | 1.0000x |
| 16 | 0.109 | 0.109 | 1.0000x | 0.120 | 0.120 | 1.0000x |
| 32 | 0.160 | 0.160 | 1.0000x | 0.175 | 0.175 | 1.0000x |
| 64 | 0.213 | 0.213 | 1.0000x | 0.230 | 0.230 | 1.0000x |
| 128 | 0.216 | 0.216 | 1.0000x | 0.240 | 0.240 | 1.0000x |
| 256 | 0.224 | 0.224 | 1.0000x | 0.250 | 0.249 | 1.0040x |
| 512 | 0.231 | 0.231 | 1.0000x | 0.269 | 0.269 | 1.0000x |
| 1024 | 0.246 | 0.246 | 1.0000x | 0.347 | 0.348 | 0.9971x |
| 2048 | 0.313 | 0.313 | 1.0000x | 0.544 | 0.543 | 1.0018x |
| 4096 | 0.450 | 0.459 | 0.9804x | 0.888 | 0.886 | 1.0023x |
| **Geomean** |  |  | **0.9971x** |  |  | **1.0004x** |

The matched 20-iteration graph trace separates the two W4A16 GEMMs by grid
shape. GEMM1 averaged 218.4077 us before and 218.8334 us after. GEMM2 averaged
171.3582 us before and 171.3965 us after. The overlap therefore did not shorten
GEMM2 or improve end-to-end overlap; the first smoke was measurement noise.

Evidence:

- Focused route-192 numerical test:
  `logs/w4a16_route192_overlap_test_20260724_110051/`
- Initial EP8/4096 smoke:
  `logs/w4a16_route192_overlap_smoke_20260724_110139/`
- Full EP8 and simulated-TP8 sweep:
  `logs/w4a16_route192_overlap_full_20260724_110334/`
- Candidate Nsight Systems trace:
  `logs/w4a16_route192_overlap_nsys_20260724_111037/`
- Matched baseline Nsight Systems trace:
  `logs/w4a16_route192_overlap_nsys_baseline_20260724_111212/`

### Compact route-192 accumulator with one decoded-weight stage

**Result: Rejected.** The dense route-192
GEMM2 normally has one rounded 256-column accumulator stage and two
128-column decoded-weight stages. This prototype instead packs two disjoint
N192 accumulator stages into 384 TMEM columns and leaves 128 columns for one
decoded-weight stage. It tests whether double-buffering the accumulator and
epilogue is more valuable than double-buffering the eight-stage GEMM2 weight
transform pipeline.

The focused route-192 numerical test passed. A guarded EP8/4096 smoke measured
0.411 ms, and the full sweep measured 0.407824 ms at EP8/4096. The table below
uses a fresh same-session baseline after fully restoring and reinstalling the
original source; speedup is baseline latency divided by candidate latency.

| Tokens | EP8 baseline (ms) | EP8 candidate (ms) | EP8 speedup | TP8 baseline (ms) | TP8 candidate (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.045983 | 0.045824 | 1.0035x | 0.050465 | 0.050496 | 0.9994x |
| 2 | 0.053248 | 0.053280 | 0.9994x | 0.054144 | 0.054384 | 0.9956x |
| 4 | 0.076656 | 0.076640 | 1.0002x | 0.060144 | 0.060112 | 1.0005x |
| 8 | 0.097104 | 0.097072 | 1.0003x | 0.086848 | 0.087184 | 0.9961x |
| 16 | 0.108480 | 0.108432 | 1.0004x | 0.120160 | 0.120496 | 0.9972x |
| 32 | 0.160127 | 0.160128 | 1.0000x | 0.175520 | 0.175712 | 0.9989x |
| 64 | 0.212240 | 0.212048 | 1.0009x | 0.229664 | 0.230368 | 0.9969x |
| 128 | 0.216848 | 0.217072 | 0.9990x | 0.240224 | 0.240576 | 0.9985x |
| 256 | 0.224016 | 0.224048 | 0.9999x | 0.248912 | 0.249439 | 0.9979x |
| 512 | 0.230511 | 0.230816 | 0.9987x | 0.269152 | 0.269088 | 1.0002x |
| 1024 | 0.246287 | 0.246096 | 1.0008x | 0.346960 | 0.347472 | 0.9985x |
| 2048 | 0.313648 | 0.313600 | 1.0002x | 0.542208 | 0.542032 | 1.0003x |
| 4096 | 0.415392 | 0.407824 | 1.0186x | 0.880287 | 0.877072 | 1.0037x |
| **Geomean** |  |  | **1.0017x** |  |  | **0.9988x** |

Nsight Systems initially appears to support the dense-shape result: GEMM2
averaged 152.1759 us versus 171.3582 us in the prior baseline trace. However,
the candidate GEMM1 grid changed from `(32, 202, 1)` to `(32, 287, 1)`.
The DEBUG autotuner trace explains why. The prior baseline selected paired
M256 route-192 at 0.435763 ms. With this prototype, paired M256 route-192
regressed to 0.480627 ms and paired M256 route-128 was selected at
0.469197 ms. The fresh restored baseline reproduced this ordering: route-192
measured 0.439091 ms and route-128 measured 0.469814 ms. The prototype
therefore gained only 1.9% at the primary EP8/4096 case by making its intended
route-192 tactic slower and displacing it with route-128. This is not a clean
or robust optimization; explicit route-selection behavior must be evaluated
separately.

Evidence:

- Focused route-192 numerical test:
  `logs/w4a16_route192_acc2_trans1_test_20260724_111934/`
- Guarded EP8/4096 smoke:
  `logs/w4a16_route192_acc2_trans1_ep4096_20260724_112105/`
- Failed filtered-harness invocation, before any kernel launch:
  `logs/w4a16_route192_acc2_trans1_full_20260724_112346/`
- Full EP8 and simulated-TP8 sweep:
  `logs/w4a16_route192_acc2_trans1_full_20260724_112429/`
- Candidate Nsight Systems trace:
  `logs/w4a16_route192_acc2_trans1_nsys_20260724_112613/`
- Candidate DEBUG autotuner trace:
  `logs/w4a16_route192_acc2_trans1_tactic_20260724_112901/`
- Fresh full EP8 and simulated-TP8 baseline:
  `logs/w4a16_route192_acc2_trans1_matched_baseline_20260724_113300/`
- Fresh baseline DEBUG autotuner trace:
  `logs/w4a16_route192_acc2_trans1_baseline_tactic_20260724_113442/`

### Remove route-192 from autotuning

**Result: Rejected after the dense-shape probe; no full sweep needed.** To
separate tactic selection from the compact-accumulator code generation, this
experiment restored the original kernel and removed only route-192 from the
autotune space. The resulting baseline route-128 kernel measured 0.427424 ms
at EP8/4096, versus 0.415392 ms for the fresh route-192 baseline
(`0.9718x`). The prior compact-accumulator result therefore does not justify
changing the tactic space. Route-192 was restored.

Evidence:

- EP8/4096 route-128-only probe:
  `logs/w4a16_route128_only_ep4096_20260724_113725/`

### GEMM2 aligned 16-byte scale loads

**Result: Rejected.** Nsight Compute localized every excessive
GEMM2 shared-load wavefront to the E4M3 scale fragment loaded immediately
before `decode_nvfp4_fragment_to_bf16`. The existing filtered copy loads eight
contiguous scale bytes per lane as two scalar shared loads. Both instructions
have a four-way bank conflict and together account for all 1,139,712 excessive
shared-load wavefronts in the EP8/4096 capture.

This prototype leaves GEMM1 unchanged. For GEMM2, each lane instead performs
one aligned 16-byte shared-to-register copy and aliases the first eight bytes
with the original compact scale-fragment layout. Decode order and arithmetic
remain unchanged; the extra eight bytes are not consumed. A focused route-192
numerical test passed.

The table uses the fresh same-harness baseline recorded above. Speedup is
baseline latency divided by candidate latency.

| Tokens | EP8 baseline (ms) | EP8 candidate (ms) | EP8 speedup | TP8 baseline (ms) | TP8 candidate (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.045983 | 0.046592 | 0.9869x | 0.050465 | 0.051232 | 0.9850x |
| 2 | 0.053248 | 0.053328 | 0.9985x | 0.054144 | 0.054080 | 1.0012x |
| 4 | 0.076656 | 0.076272 | 1.0050x | 0.060144 | 0.060128 | 1.0003x |
| 8 | 0.097104 | 0.097152 | 0.9995x | 0.086848 | 0.087552 | 0.9920x |
| 16 | 0.108480 | 0.108575 | 0.9991x | 0.120160 | 0.119728 | 1.0036x |
| 32 | 0.160127 | 0.160160 | 0.9998x | 0.175520 | 0.175200 | 1.0018x |
| 64 | 0.212240 | 0.212576 | 0.9984x | 0.229664 | 0.229023 | 1.0028x |
| 128 | 0.216848 | 0.217136 | 0.9987x | 0.240224 | 0.240479 | 0.9989x |
| 256 | 0.224016 | 0.224079 | 0.9997x | 0.248912 | 0.249184 | 0.9989x |
| 512 | 0.230511 | 0.230112 | 1.0017x | 0.269152 | 0.268415 | 1.0027x |
| 1024 | 0.246287 | 0.245280 | 1.0041x | 0.346960 | 0.346080 | 1.0025x |
| 2048 | 0.313648 | 0.314368 | 0.9977x | 0.542208 | 0.539488 | 1.0050x |
| 4096 | 0.415392 | 0.408927 | 1.0158x | 0.880287 | 0.864880 | 1.0178x |
| **Geomean** |  |  | **1.0004x** |  |  | **1.0009x** |

An initial full-script invocation was stopped after it began compiling
unneeded CUTLASS and TRT-LLM benchmark backends. The replacement harness calls
the same benchmark input and routing setup with
`profile_backend="cute-dsl-w4a16"`, so only the shared DeepSeek routing
extension and CuTe DSL W4A16 MoE are built and measured.

Nsight Compute showed that the dense GEMM2 grid remained `(2, 1, 74)`, but the
candidate still generated exactly 1,139,712 excessive shared-load wavefronts.
The two scalar scale loads remained in SASS because the compiler eliminated
the unused upper eight bytes. GEMM2 measured 156.896 us versus 154.528 us in
the baseline capture. The small dense-shape benchmark gains therefore are not
supported by the intended mechanism and are treated as noise. The prototype
was reverted.

Evidence:

- Baseline Nsight Compute report and parsed metrics:
  `logs/pr4048_cuda132_ncu_b2442579_20260724_022944/` and
  `logs/w4a16_gemm2_ncu_import_b2442579_retry_20260724_105217/`
- Compile-time and runtime scale-layout diagnostics:
  `logs/w4a16_scale_layout_diag_20260724_114546/`,
  `logs/w4a16_scale_addr_diag_20260724_115146/`, and
  `logs/w4a16_transform_copy_diag_20260724_115414/`
- Focused route-192 numerical test:
  `logs/w4a16_gemm2_scale_wide_route192_20260724_121028/`
- EP8/4096 smoke:
  `logs/w4a16_gemm2_scale_wide_ep4096_20260724_121142/`
- Aborted all-backend invocation:
  `logs/w4a16_gemm2_scale_wide_full_20260724_121339/`
- Full CuTe-only EP8 and simulated-TP8 sweep:
  `logs/w4a16_gemm2_scale_wide_cute_only_full_20260724_122442/`
- Candidate Nsight Compute report and parsed metrics:
  `logs/w4a16_gemm2_scale_wide_ncu_ep8_4096_20260724_123615/`

### Cooperative `ldmatrix` scale-load assessment

**Result: Diagnostic only; not implemented in the MoE kernel.** PTX
`ldmatrix.m16n16.x2.trans.b8` can load two 16x16 byte matrices cooperatively,
but its register ownership is a matrix fragment rather than each lane's
current compact eight-scale vector. CUTLASS's `SM100_U8x16_LDSM_T` immediately
permutes the four result registers to match its downstream matrix-store
ownership. The CuTe DSL mixed-input FMHA path likewise constructs its
`LdMatrix16x16x8bOp` copy directly from the destination TMEM-store layout.

The closest FlashInfer counterexample is
`include/flashinfer/mamba/kernel_checkpointing_ssu_common.cuh`. That kernel
records a 5-18% regression from replacing per-lane int8 shared loads with
`ldmatrix.b8`: the cooperative instruction still has inherent two-way bank
conflicts, and remapping its matrix fragment to the accumulator layout costs
eight shuffles plus byte extraction. W4A16's E4M3 scales are side operands to
the decoder rather than MMA fragments, so its consumer has the same mismatch.

The current W4A16 scale partition gives each transform warp a disjoint
four-byte quarter from each 16-byte row. Loading complete 16-byte rows with
`ldmatrix` would either duplicate data across four warps or require a
co-designed packed-weight and TMEM ownership change. Prior scale-only ownership
and shared-layout transposes already failed those contracts. A future
`ldmatrix` attempt is justified only as part of such a full transform-layout
redesign, not as a replacement for the two scalar scale loads.

A compile-time probe on the actual M256/K256 2-CTA GEMM2 specialization
confirmed the mismatch. Each lane's compact scale register has eight bytes,
split into four contiguous values and four values 512 bytes later; across a
warp this is a 32-row by 8-column ownership. `m16n16.x1.trans.b8` also returns
eight bytes per lane, but its destination ownership is four rows by two
columns. Composing that atom with either the BF16 TMEM store or the current
universal source copy therefore partitions the scale tensor as a repeated
logical MMA operand rather than the compact physical scale tile. The byte
counts match, but the lane coordinates do not.

The probe code was removed without changing the retained fragment-32 kernel.
No performance run was warranted because a correct integration would first
need to remap packed-weight and TMEM ownership across the four transform
warps.

Evidence:

- Existing compact scale ownership:
  `logs/w4a16_layout_probe_20260724_195944/`
- `ldmatrix` composed with the BF16 TMEM source ownership:
  `logs/w4a16_layout_probe_ldmatrix_20260724_200118/`
- `ldmatrix` composed with the universal-copy destination ownership:
  `logs/w4a16_layout_probe_ldmatrix_dst_20260724_200255/`

### Load GEMM2 scales before acquiring the transformed-weight slot

**Result: Rejected after the dense-shape gate.** The transform normally
acquires its destination TMEM pipeline stage before loading the compact E4M3
scale fragment. This GEMM2-only prototype moved the scale shared load before
that acquire, testing whether the four-way replay could overlap with
transform-to-MMA backpressure. GEMM1 retained its original schedule.

All six route/topology numerical cases passed, including route-192, and the
watchdog found no residual GPU process. EP8/4096 measured 0.432479 ms. An
immediately adjacent run after restoring the kernel measured 0.434335 ms,
making the candidate only `1.0043x` faster. The older 0.415392 ms baseline did
not reproduce on the node and is not used for this decision. The matched
sub-0.5% difference is noise rather than evidence that scale replay overlaps
with TMEM backpressure, so the original acquire-before-load order was retained
without a full sweep.

Evidence:

- Numerical route matrix:
  `logs/w4a16_gemm2_scale_preacquire_test_20260724_125236/`
- EP8/4096 performance gate:
  `logs/w4a16_gemm2_scale_preacquire_ep4096_20260724_125430/`
- Immediately restored EP8/4096 baseline:
  `logs/w4a16_gemm2_scale_preacquire_restored_ep4096_20260724_125614/`

### Rebalance registers from epilogue to transform warps

**Result: Rejected.** The retained 16-warp CTA uses four 176-register
epilogue warps, four 80-register control warps, and eight transform warps at
the 128-register launch default. This experiment kept the exact 65,536-register
CTA budget but assigned 160 registers to each epilogue warp and 136 registers
to each transform warp:

```
32 * (4 * 160 + 4 * 80 + 8 * 136) = 65,536
```

The transform warps used an explicit `setmaxregister_increase(136)`. All six
route/topology numerical cases passed. A first EP8/4096 comparison was
inconclusive because the node moved from 0.436144 ms for the candidate to
0.440096 ms for a restored baseline. The complete immediately adjacent
candidate/baseline sweeps instead show a consistent regression. Speedup is
baseline latency divided by candidate latency.

| Tokens | EP8 baseline (ms) | EP8 candidate (ms) | EP8 speedup | TP8 baseline (ms) | TP8 candidate (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.045856 | 0.046879 | 0.9782x | 0.050432 | 0.051456 | 0.9801x |
| 2 | 0.053184 | 0.053920 | 0.9864x | 0.054113 | 0.055728 | 0.9710x |
| 4 | 0.076544 | 0.076976 | 0.9944x | 0.060160 | 0.061247 | 0.9823x |
| 8 | 0.097056 | 0.097712 | 0.9933x | 0.086704 | 0.089328 | 0.9706x |
| 16 | 0.108480 | 0.110287 | 0.9836x | 0.120128 | 0.123504 | 0.9727x |
| 32 | 0.160160 | 0.160080 | 1.0005x | 0.175632 | 0.177487 | 0.9895x |
| 64 | 0.212480 | 0.211072 | 1.0067x | 0.229567 | 0.231248 | 0.9927x |
| 128 | 0.216944 | 0.215456 | 1.0069x | 0.240096 | 0.241760 | 0.9931x |
| 256 | 0.224047 | 0.231951 | 0.9659x | 0.249328 | 0.260143 | 0.9584x |
| 512 | 0.230096 | 0.238320 | 0.9655x | 0.269199 | 0.275679 | 0.9765x |
| 1024 | 0.245599 | 0.250991 | 0.9785x | 0.346943 | 0.349792 | 0.9919x |
| 2048 | 0.313456 | 0.315103 | 0.9948x | 0.541919 | 0.544976 | 0.9944x |
| 4096 | 0.408959 | 0.409967 | 0.9975x | 0.876879 | 0.876815 | 1.0001x |
| **Geomean** |  |  | **0.9885x** |  |  | **0.9825x** |

The additional transform registers do not improve the dense GEMM2 feed and
materially hurt the 256-512-token region. The original 176/80/128 allocation
was restored.

Evidence:

- Candidate setup:
  `logs/w4a16_regs160_136_full_setup_retry_20260724_062317/`
- Numerical route matrix:
  `logs/w4a16_regs160_136_test_20260724_061606/`
- Failed first smoke, before any kernel launch:
  `logs/w4a16_regs160_136_ep4096_20260724_061734/`
- Candidate EP8/4096 smoke:
  `logs/w4a16_regs160_136_ep4096_retry_20260724_061838/`
- Candidate full EP8 and simulated-TP8 sweep:
  `logs/w4a16_regs160_136_full_retry_20260724_062547/`
- Restored baseline full EP8 and simulated-TP8 sweep:
  `logs/w4a16_regs_baseline_full_20260724_062857/`

### Persistent scale-prepack contract assessment

**Result: Do not change the SM100 public weight-scale layout as a local kernel
optimization.** The SM100 W4A16 API, unified `MoEWeightPack` path, tests, and
benchmarks all pass the same six-dimensional view produced by
`convert_sf_to_mma_layout`. The low-level update test mutates that serving-owned
allocation in place and requires the next invocation to observe its current
contents. A private prepacked copy would therefore become stale after an RL
weight update unless every caller also maintained and updated the copy.

FlashInfer's SM120 W4A16 implementation is not a counterexample to that
constraint. It owns a distinct `b12x_w4a16` backend view and an explicit
prepare path that repacks both weights and scales for its kernel. The SM100
backend currently shares the canonical Cute DSL NVFP4 scale contract with
W4A4; changing it would be an API and integration change, not an internal
staging optimization.

A persistent SM100-specific prepack could still be revisited as a separately
designed backend view if its serving/update contract is changed deliberately.
For this optimization pass, scale-conflict work must keep the existing tensor
and either alter only the in-kernel staged representation or improve the
consumer access pattern.

### Mixed TMA and `cp.async.mbarrier` scale-staging contract

**Result: Rejected after the full sweep and profile; this is not an
L2-prefetch use.**
CUTLASS's SM100 block-scaled transform kernels put scale factors in a separate
`PipelineAsync`: every producer lane first arrives normally and then uses
`cp.async.mbarrier.arrive.noinc` so its outstanding global-to-shared copies
supply the second event. The full barrier is initialized for 64 producer
events, two for each of 32 lanes. The transform consumer can therefore wait on
scale completion without a producer-side `cp.async.wait_group`.

CUTLASS's SM120 block-scaled mainloop demonstrates the composite form that is
closer to W4A16. Its full barrier expects 33 events: one elected TMA
`arrive.expect_tx` plus one `cp.async.mbarrier.arrive.noinc` from every lane.
The TMA transaction byte count includes only the TMA operands; scale bytes are
tracked by the 32 asynchronous arrivals. The CuTe DSL pipeline implementation
exposes the same primitives through `PipelineCpAsync`,
`PipelineTmaAsync.producer_get_barrier`, and
`cute.arch.cp_async_mbarrier_arrive_noinc`.

This contract is intended for asynchronous global-to-shared data movement with
completion semantics. It does not merely hint future L2 residency. For W4A16,
it permits a scale-only LDGSTS path to retain the existing global scale tensor,
write a conflict-free shared layout, and overlap with the packed-weight TMA.
The prototype must account for 2-CTA execution explicitly: weight TMA may
multicast, while each CTA issues its own small scale copy into CTA-local shared
memory.

The prototype kept packed weights on TMA but staged the E4M3 scales with
per-lane 32-bit `cp.async` copies into a conflict-free shared layout. The
existing TMA full barrier used the SM120-style 33-event contract: one TMA
arrival plus one `cp.async.mbarrier.arrive.noinc` from each lane. The TMA
transaction count excluded the scale bytes. The public scale layout and
dequantization arithmetic were unchanged, and all six route/topology numerical
cases passed.

The full adjacent sweep initially appeared favorable for EP8 but unfavorable
for TP8. Speedup is baseline latency divided by candidate latency.

| Tokens | EP8 baseline (ms) | EP8 candidate (ms) | EP8 speedup | TP8 baseline (ms) | TP8 candidate (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.046016 | 0.045920 | 1.0021x | 0.050512 | 0.050528 | 0.9997x |
| 2 | 0.053152 | 0.053120 | 1.0006x | 0.054384 | 0.054735 | 0.9936x |
| 4 | 0.076415 | 0.076447 | 0.9996x | 0.060240 | 0.060736 | 0.9918x |
| 8 | 0.097824 | 0.097647 | 1.0018x | 0.086672 | 0.088224 | 0.9824x |
| 16 | 0.108640 | 0.108479 | 1.0015x | 0.120127 | 0.122304 | 0.9822x |
| 32 | 0.160048 | 0.159136 | 1.0057x | 0.175455 | 0.179136 | 0.9795x |
| 64 | 0.212591 | 0.210608 | 1.0094x | 0.229407 | 0.233935 | 0.9806x |
| 128 | 0.216895 | 0.215232 | 1.0077x | 0.239983 | 0.244416 | 0.9819x |
| 256 | 0.222960 | 0.223407 | 0.9980x | 0.249103 | 0.253200 | 0.9838x |
| 512 | 0.230559 | 0.229615 | 1.0041x | 0.269471 | 0.271215 | 0.9936x |
| 1024 | 0.245936 | 0.248463 | 0.9898x | 0.346879 | 0.350432 | 0.9899x |
| 2048 | 0.319311 | 0.313999 | 1.0169x | 0.542318 | 0.545920 | 0.9934x |
| 4096 | 0.419470 | 0.409200 | 1.0251x | 0.860829 | 0.882688 | 0.9752x |
| **Geomean** |  |  | **1.0048x** |  |  | **0.9867x** |

The profile did not support the apparent dense EP gain. For GEMM2, shared-load
bank conflicts fell from 1,553,130 to 432,446, but the replacement LDGSTS path
introduced 1,600,732 bank conflicts. Tensor-pipeline utilization fell from
65.50% to 39.39%, and the profiled kernel increased from 154.528 us to
243.424 us. A final same-tactic, immediately adjacent EP8/4096 comparison also
measured 0.432831 ms for the baseline and 0.434319 ms for the candidate
(`0.9966x`). The full-sweep EP result was therefore run drift, while the TP
regression and profile both show real added pressure from scale LDGSTS.

The direct L2-prefetch PTX remains appropriate for sequential ordinary global
loads, as used by FlashInfer's MLA concatenation kernel, while the mixed
TMA/LDGSTS contract is appropriate when asynchronous scale staging is itself
useful. Neither contract improves this W4A16 scale path. The original
scale-TMA implementation was restored.

Evidence:

- Candidate setup and numerical test:
  `logs/w4a16_cpasync_scale_setup_20260724_140014/` and
  `logs/w4a16_cpasync_scale_test_20260724_140115/`
- Adjacent full baseline and candidate sweeps:
  `logs/w4a16_cpasync_scale_full_baseline_20260724_140934/` and
  `logs/w4a16_cpasync_scale_full_candidate_20260724_141048/`
- Candidate Nsight Compute report and parsed metrics:
  `logs/w4a16_cpasync_scale_ncu_ep8_4096_20260724_141249/` and
  `logs/w4a16_cpasync_scale_ncu_import_20260724_141356/`
- Same-tactic EP8/4096 candidate and baseline:
  `logs/w4a16_cpasync_candidate_debug_ep4096_20260724_141557/` and
  `logs/w4a16_cpasync_baseline_debug_ep4096_20260724_141651/`

### Aligned compact-scale loads with direct SSA fragments

**Result: Rejected after correctness and profiler gates; no full sweep
needed.** This revisited the aligned-load idea without relying on an oversized
16-byte register tensor that the compiler could scalarize. GEMM2 loaded the
actual compact scale fragment directly from shared memory:

- two scale bytes with `ld.shared.u16`;
- four bytes from the selected word of an aligned `ld.shared.v2.u32`;
- eight bytes with aligned `ld.shared.v2.u32` plus a predicated tail word for
  lanes whose fragment begins at byte offset four.

The fragment must be selected from the per-iteration shared-memory view.
Taking a pointer from the register copy produced an invalid shared address.
The scale width also depends on the selected topology: some tactics decode 128
FP4 values per iteration and require eight scale bytes, so the initial
single-word implementation was incomplete even though one register allocation
happened to mask it. The corrected 2/4/8-byte implementation passed all six
route/topology numerical cases.

The aligned loads reduced GEMM2 shared-load bank conflicts, but keeping the
scale fragment in SSA increased transform-warp register pressure. Exact-budget
register splits moved that pressure between transform, epilogue, and control
warps without recovering the baseline pipeline:

| Epilogue/control/transform registers | GEMM2 (us) | Local spills | Shared spills | Load conflicts | Store conflicts | Tensor pipe |
|---|---:|---:|---:|---:|---:|---:|
| Baseline `176/80/128` | 154.528 | 0 | 0 | 1,553,130 | - | 42.02% |
| `176/64/136` | 226.976 | 24,756 | 190,396 | 1,148,547 | - | 27.15% |
| `160/64/144` | 237.120 | 5,484 | 0 | 1,247,707 | 5,818,823 | 29.73% |
| `144/64/152` | 224.544 | 0 | 0 | 959,719 | 6,237,201 | 31.83% |
| `160/48/152` | 222.816 | 0 | 0 | 949,559 | 6,271,295 | 28.98% |

At 152 transform registers the candidate is spill-free and removes about 39%
of baseline scale-load conflicts, proving that the vector access itself works.
However, excessive shared wavefronts remain at 5,223,680 and the reduced
epilogue/control allocation creates much larger shared-store pressure. The
best candidate is still 44% slower than the baseline GEMM2. The original
scalar compact-fragment load and `176/80/128` allocation were restored.

Evidence:

- Initial vector-load and register-allocation diagnostics:
  `logs/w4a16_scale_v2_gemm2_only_ncu_ep8_4096_20260724_151748/`,
  `logs/w4a16_scale_v2_selp_ncu_ep8_4096_20260724_152531/`, and
  `logs/w4a16_scale_v2_minregs_ncu_ep8_4096_20260724_152950/`
- Generated PTX/SASS:
  `logs/w4a16_scale_v2_regs136_route128_dump_20260724_154334/`
- Scalar control and vector/scalar diagnostic:
  `logs/w4a16_scalar_scale_gemm2_regs136_generic64_matrix_20260724_154531/`
  and `logs/w4a16_scale_v2_scalar_compare_route128_20260724_154728/`
- Correct 2/4/8-byte fragment route matrix:
  `logs/w4a16_scale_fragment_shared_view_matrix_20260724_155741/`
- Register-allocation profiles:
  `logs/w4a16_scale_fragment_ncu_ep8_4096_20260724_155900/`,
  `logs/w4a16_scale_fragment_regs144_ncu_ep8_4096_20260724_160324/`,
  `logs/w4a16_scale_fragment_regs152_ncu_ep8_4096_20260724_160836/`, and
  `logs/w4a16_scale_fragment_regs152_ep160_ncu_ep8_4096_20260724_161213/`
- Final route matrices:
  `logs/w4a16_scale_fragment_regs152_matrix_20260724_160754/` and
  `logs/w4a16_scale_fragment_regs152_ep160_matrix_20260724_161131/`

### Stage GEMM2 alpha with routed-tile metadata

**Result: Rejected after an adjacent same-workload comparison.** The baseline
Nsight Compute report attributed the largest GEMM2 long-scoreboard source
sample group to the per-expert FP32 `alpha[work_tile.group_idx]` load near the
epilogue. The W4A4 grouped-finalize kernel handles analogous metadata with a
dedicated loader warp, so the prototype reused W4A16's existing tile-info
scheduler warp to load one alpha value per pipeline stage into shared memory.
GEMM1 kept its original alpha load because its fused-activation epilogue has a
different access pattern.

The first shared-tensor form failed MLIR dominance verification because the
dynamic scheduler branches captured the full tensor value. A stage-local slice
fixed ownership, and a two-dimensional `(1, num_tile_info_stage)` layout made
the dynamic stage coordinate valid. The corrected implementation passed all
six route-tile/topology numerical cases.

The adjacent EP8/4096 benchmark did not show a gain:

| Version | Latency (ms) | Baseline / candidate |
|---|---:|---:|
| Staged alpha | 0.432319 | 0.9983x |
| Original global alpha load | 0.431600 | 1.0000x |

The alpha value is reused only for one routed tile, and the existing global
load is already cache-friendly. Adding another shared allocation, store,
fence-visible value, and shared read merely transfers the dependency into the
tile-info pipeline. The prototype was restored without a full sweep.

Evidence:

- Initial dominance and shared-coordinate failures:
  `logs/w4a16_gemm2_staged_alpha_matrix_20260724_162129/` and
  `logs/w4a16_gemm2_staged_alpha_slice_matrix_20260724_162343/`
- Six-case numerical matrix:
  `logs/w4a16_gemm2_staged_alpha_2d_matrix_20260724_162517/`
- Candidate EP8/4096:
  `logs/w4a16_gemm2_staged_alpha_ep4096_20260724_162605/`
- Adjacent clean baseline EP8/4096:
  `logs/w4a16_gemm2_staged_alpha_baseline_ep4096_retry_20260724_163119/`

### Shorten the GEMM2 decode-fragment live range

**Result: Promising for EP8; retained while testing the remaining fragment
size.** The transform loop previously decoded 128 FP4 values per lane at a
time for both GEMMs. GEMM2 now keeps GEMM1 unchanged and decodes two
64-value fragments instead. The numerical helper and instruction-level
arithmetic are unchanged. This halves each GEMM2 packed-weight, scale, and
decoded-output register fragment while preserving the total work.

All six route-tile/topology numerical cases passed. The full adjacent sweep
shows a consistent EP8 improvement and a simulated-TP8 regression. Speedup is
baseline latency divided by candidate latency.

| Tokens | EP8 baseline (ms) | EP8 candidate (ms) | EP8 speedup | TP8 baseline (ms) | TP8 candidate (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.045760 | 0.045632 | 1.0028x | 0.049632 | 0.050352 | 0.9857x |
| 2 | 0.053120 | 0.053104 | 1.0003x | 0.053120 | 0.053984 | 0.9840x |
| 4 | 0.076656 | 0.076192 | 1.0061x | 0.059168 | 0.060192 | 0.9830x |
| 8 | 0.097280 | 0.096591 | 1.0071x | 0.085984 | 0.087072 | 0.9875x |
| 16 | 0.108384 | 0.108368 | 1.0001x | 0.119200 | 0.120512 | 0.9891x |
| 32 | 0.160320 | 0.159007 | 1.0083x | 0.174319 | 0.176016 | 0.9904x |
| 64 | 0.211904 | 0.210352 | 1.0074x | 0.228512 | 0.230288 | 0.9923x |
| 128 | 0.216783 | 0.215039 | 1.0081x | 0.239152 | 0.240944 | 0.9926x |
| 256 | 0.223808 | 0.222239 | 1.0071x | 0.248704 | 0.249728 | 0.9959x |
| 512 | 0.230912 | 0.228160 | 1.0121x | 0.269680 | 0.270000 | 0.9988x |
| 1024 | 0.246432 | 0.245216 | 1.0050x | 0.346783 | 0.344048 | 1.0079x |
| 2048 | 0.313759 | 0.313360 | 1.0013x | 0.541759 | 0.537390 | 1.0081x |
| 4096 | 0.408400 | 0.405919 | 1.0061x | 0.871695 | 0.882943 | 0.9873x |
| **Geomean** |  |  | **1.0055x** |  |  | **0.9925x** |

The dense GEMM2 profile uses the same route-192, M256/N192/K256, 2-CTA
tactic on both sides. It improved from 154.528 to 153.952 us. Tensor-pipeline
utilization increased from 70.06% to 70.57% of active cycles and from 65.50%
to 66.29% of elapsed cycles, with no local or shared spills. The split did not
remove the scale-load replay: excessive shared wavefronts remained 1,139,712,
shared-load conflicts increased slightly from 1,553,130 to 1,560,216, and
eligible warps per scheduler fell from 1.19 to 1.12. The gain therefore comes
from the shorter transform-fragment schedule, but GEMM2 remains scoreboard
limited.

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_gemm2_fragment64_matrix_20260724_165335/`
- Adjacent dense-shape gates and tactic trace:
  `logs/w4a16_gemm2_fragment64_ep4096_20260724_165411/`,
  `logs/w4a16_gemm2_fragment64_baseline_ep4096_20260724_165618/`, and
  `logs/w4a16_gemm2_fragment64_repeat_debug_ep4096_20260724_165717/`
- Full candidate and adjacent baseline sweeps:
  `logs/w4a16_gemm2_fragment64_full_20260724_165817/` and
  `logs/w4a16_gemm2_fragment64_matched_baseline_full_20260724_165932/`
- Candidate Nsight Compute report and parsed metrics:
  `logs/w4a16_gemm2_fragment64_ncu_ep4096_20260724_170129/` and
  `logs/w4a16_gemm2_fragment64_ncu_import_20260724_170248/`

### Reduce the GEMM2 decode fragment from 64 to 32 values

**Result: Rejected after the dense-shape gate.** The decoder also supports a
32-value fragment, which reduces the packed-weight and output live ranges
again and uses its two-scale-byte path. All six route-tile/topology numerical
cases passed. EP8/4096 measured 0.433584 ms, versus 0.432287 ms for an
immediately adjacent 64-value run (`0.9970x`). The extra transform-loop and
copy instructions outweigh the smaller fragment, so 64 values remain the
GEMM2 scheduling candidate.

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_gemm2_fragment32_matrix_20260724_170600/`
- EP8/4096 candidate and adjacent 64-value comparison:
  `logs/w4a16_gemm2_fragment32_ep4096_20260724_170633/` and
  `logs/w4a16_gemm2_fragment64_matched_ep4096_20260724_170717/`

### Rebalance registers after shortening the GEMM2 decode fragment

**Result: Rejected as measurement noise; no full sweep needed.** The 64-value
GEMM2 fragment reduces the transform live range enough to revisit register
allocation without the spills seen by the earlier 128-value fragment. The
prototype used an exact 64K-register budget:

- four epilogue warps at 192 registers;
- four control warps at 80 registers;
- eight transform warps at 120 registers.

All six route-tile/topology numerical cases passed, and no GPU process
remained after the run. Two clean EP8/4096 measurements were 0.431215 and
0.431599 ms, versus an adjacent 0.432911 ms baseline. The 0.3-0.4% apparent
gain is below the acceptance threshold and does not justify an extra
`setmaxnreg` operation in all eight transform warps. The original
`176/80/128` split was restored.

An attempted API-log trace used the invalid string value `DEBUG` before being
rerun with the numeric log level. The numeric trace materially perturbed the
benchmark and was excluded from the comparison.

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_gemm2_reg192_120_matrix_20260724_171213/`
- Candidate, adjacent baseline, and clean candidate repeat:
  `logs/w4a16_gemm2_reg192_120_ep4096_20260724_171239/`,
  `logs/w4a16_gemm2_fragment64_reg_baseline_ep4096_20260724_171314/`, and
  `logs/w4a16_gemm2_reg192_120_repeat_clean_ep4096_20260724_171443/`
- Excluded API-log attempts:
  `logs/w4a16_gemm2_reg192_120_repeat_ep4096_20260724_171346/` and
  `logs/w4a16_gemm2_reg192_120_repeat_ep4096_20260724_171411/`

### Reserve one output stage before sizing the GEMM2 load ring

**Result: Rejected as a stage-fitting no-op for the selected tactic.** The
deterministic path initially reserves two shared-memory output stages before
fitting its input-load ring, then assigns leftover memory to more output
stages. The prototype started GEMM2 from one output stage to test whether the
fitter could buy another packed-weight/activation load stage. An initial broad
version also changed GEMM1; the corrected version passed `fuse_activation`
into the fitter and changed GEMM2 only.

Both the candidate and baseline route-192 stage probes reported the same final
allocation:

```text
mma=(256, 192, 256) load=3 transform=2 acc=1 c=2
```

The existing allocation already fits three load stages, and the leftover
memory restores the second output stage. The scoped candidate passed all six
route-tile/topology numerical cases but measured 0.432975 ms at EP8/4096,
versus the adjacent 0.432911 ms baseline. Nsight Compute likewise measured
GEMM2 at 154.02 us versus 153.95 us. Tensor-pipeline active-cycle utilization
was 70.69% versus 70.57%, elapsed-cycle utilization was 65.98% versus 66.29%,
and eligible warps per scheduler remained 1.12. The original fitter was
restored without a full sweep.

Evidence:

- Initial broad candidate:
  `logs/w4a16_gemm2_cstage1_matrix_20260724_172016/`,
  `logs/w4a16_gemm2_cstage1_ep4096_20260724_172039/`, and
  `logs/w4a16_gemm2_cstage1_stage_probe_20260724_172147/`
- Scoped numerical and dense-shape gates:
  `logs/w4a16_gemm2_cstage1_scoped_matrix_20260724_172311/` and
  `logs/w4a16_gemm2_cstage1_scoped_ep4096_20260724_172345/`
- Candidate profile and parsed metrics:
  `logs/w4a16_gemm2_cstage1_scoped_ncu_ep4096_20260724_172441/` and
  `logs/w4a16_gemm2_cstage1_scoped_ncu_import_20260724_172536/`
- Baseline stage probe:
  `logs/w4a16_gemm2_fragment64_stage_probe_20260724_172757/`

### Widen the GEMM2 transformed-weight TMEM store

**Result: Rejected as neutral.** The current two-transform-warpgroup design
stores decoded weights through `tcgen05.St32x32bOp` with repetition 8. A
GEMM2-only prototype used repetition 16 while leaving fused GEMM1 unchanged.
This revisited an older whole-kernel experiment after the transform-pipeline
refactor and the shorter 64-value GEMM2 fragment.

All six route-tile/topology numerical cases passed, and no GPU process
remained after the run. The adjacent EP8/4096 comparison measured
0.432415 ms with repetition 16 and 0.432335 ms with repetition 8
(`0.9998x`). The wider store therefore does not improve the end-to-end
GEMM2 feed, so repetition 8 was restored without a full sweep.

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_gemm2_x16_matrix_20260724_173303/`
- Candidate and adjacent baseline EP8/4096:
  `logs/w4a16_gemm2_x16_ep4096_20260724_173339/` and
  `logs/w4a16_gemm2_x8_adjacent_ep4096_20260724_173414/`

### Stream GEMM2 scale fragments through the decode loop

**Result: Rejected after the dense-shape gate.** With a 64-value decode
fragment, the baseline loads all eight E4M3 scale bytes before decoding two
fragments. The prototype split the same two scalar shared loads across the
decode loop, loading four scale bytes immediately before each fragment. This
preserved the scale addresses, compact register layout, and arithmetic while
shortening the first scale word's live range.

All six route-tile/topology numerical cases passed, and no GPU process
remained after the run. EP8/4096 measured 0.434335 ms, versus 0.432239 ms for
an immediately adjacent baseline (`0.9952x`). Splitting the loads adds loop
scheduling cost but does not remove their shared-memory replay, so the
single bulk scale copy was restored without a full sweep.

Evidence:

- First invocation stopped before compilation because the staged upload path
  was a file rather than a directory:
  `logs/w4a16_gemm2_scale_fragment_stream_matrix_20260724_173912/`
- Six-case numerical matrix:
  `logs/w4a16_gemm2_scale_fragment_stream_matrix_20260724_173939/`
- Candidate and adjacent baseline EP8/4096:
  `logs/w4a16_gemm2_scale_fragment_stream_ep4096_20260724_174013/` and
  `logs/w4a16_gemm2_scale_fragment_stream_baseline_ep4096_20260724_174046/`

### Cap the GEMM2 input-load ring at two stages

**Result: Rejected as neutral.** Dense GEMM2 has only eight K256 stages, while
the shared-memory fitter selects a three-stage packed-weight/scale plus
activation load ring. The prototype capped only GEMM2 at two load stages and
left the existing allocator free to reuse the released shared memory for
output buffering. GEMM1 and the two-stage transform-to-MMA ring were
unchanged.

All six route-tile/topology numerical cases passed, and no GPU process
remained after the run. EP8/4096 measured 0.433392 ms, versus 0.434207 ms for
an immediately adjacent baseline (`1.0019x`). This is below the retention
threshold and does not establish that reduced short-K startup cost outweighs
the lost load lookahead. The fitted three-stage ring was restored without a
full sweep.

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_gemm2_load2_matrix_20260724_174359/`
- Candidate and adjacent baseline EP8/4096:
  `logs/w4a16_gemm2_load2_ep4096_20260724_174428/` and
  `logs/w4a16_gemm2_load2_baseline_ep4096_20260724_174505/`

### Stripe GEMM2 K stages across the transform warpgroups

**Result: Numerically correct after a tail fix, but rejected by the dense
gate.** The retained pipeline makes both four-warp transform groups decode
disjoint halves of the same K stage. This prototype instead gave each group a
complete transformed tile and assigned alternating K stages to the two
groups. The load-to-transform and transform-to-MMA barriers were changed from
eight to four producer warps per stage, while MMA continued consuming stages
in order. GEMM1 kept the original same-stage split.

The first implementation hung with one GPU at 100% utilization and no active
compiler process. Both producer groups called `producer_tail()`, but only the
group whose stride-two state pointed at the next global stage owned the
barrier phase that tail must drain. The other group waited on a future empty
phase. Limiting the tail to the next-stage owner removed the deadlock. The
corrected implementation passed all six route-tile/topology numerical cases
and left no GPU process behind.

The corrected candidate measured 0.449775 ms at EP8/4096, versus approximately
0.4322-0.4342 ms for the adjacent retained design. Nsight Compute measured
GEMM2 at 169.088 us instead of 153.952 us. The candidate did not spill and
still used 128 registers per thread, but eligible warps per scheduler fell
from 1.12 to 0.76, tensor-pipeline elapsed utilization fell from 66.29% to
59.61%, and long-scoreboard stalls increased from 2.75 to 4.32 per issued
instruction. Assigning a full K stage to one four-warp group doubles that
group's source and transformed-tile work before the collective TMEM store.
Independent stage progress did not repay the longer per-stage schedule. This
version is not suitable for a full sweep.

Evidence:

- Deadlocked first implementation:
  `logs/w4a16_gemm2_striped_transform_matrix_20260724_175316/`
- Corrected six-case numerical matrix:
  `logs/w4a16_gemm2_striped_transform_v2_matrix_20260724_175726/`
- Corrected EP8/4096 dense gate:
  `logs/w4a16_gemm2_striped_transform_v2_ep4096_20260724_175754/`
- Corrected Nsight Compute report and parsed metrics:
  `logs/w4a16_gemm2_striped_transform_v2_ncu_ep4096_20260724_180138/` and
  `logs/w4a16_gemm2_striped_transform_v2_ncu_import_20260724_180254/`

### Reassign control-warp registers to the GEMM2 transform warps

**Result: Rejected after two dense-shape gates.** Shortening GEMM2's decode
fragment to 64 values reduces transform live ranges, so this prototype moved
the exact 64K-register CTA budget from the four scheduling/TMA/MMA warps to
the eight transform warps:

- four epilogue warps remained at 176 registers;
- four role-control warps changed from 80 to 64 registers;
- eight transform warps changed from the 128-register launch default to 136.

All six route-tile/topology numerical cases passed, and no GPU process
remained after any run. EP8/4096 measured 0.435248 and 0.435711 ms on two
runs, versus the retained design's approximately 0.4322-0.4342 ms range.
The profile of the preceding striped experiment showed long-scoreboard
latency rather than spills. Giving the decode warps eight more registers does
not address that latency, while reducing the role-control warps costs enough
to regress the dense case. The `176/80/128` allocation was restored.

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_gemm2_reg136_matrix_20260724_180608/`
- Two EP8/4096 measurements:
  `logs/w4a16_gemm2_reg136_ep4096_20260724_180641/` and
  `logs/w4a16_gemm2_reg136_repeat_ep4096_20260724_180726/`

### Pre-arm both GEMM2 input-readiness waits

**Result: Rejected after the full adjacent sweep.** GEMM2 already calls
`consumer_try_wait` for each transformed-weight stage before its MMA
`consumer_wait`, but waits for the independently loaded activation tile
without first probing its barrier. This prototype pre-armed both barriers
together and carried both statuses to the corresponding waits. It did not
change stage counts, layouts, arithmetic, or barrier ownership.

All six route-tile/topology numerical cases passed, and no GPU process
remained after any run. Because the candidate's first dense gate did not match
older node timing, the retained fragment-64 kernel was restored immediately
and rerun through the complete sweep. Speedup is adjacent baseline latency
divided by candidate latency.

| Tokens | EP8 baseline (ms) | EP8 candidate (ms) | EP8 speedup | TP8 baseline (ms) | TP8 candidate (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.045632 | 0.045872 | 0.9948x | 0.050432 | 0.051056 | 0.9878x |
| 2 | 0.053120 | 0.052800 | 1.0061x | 0.054016 | 0.054112 | 0.9982x |
| 4 | 0.076257 | 0.076224 | 1.0004x | 0.060319 | 0.059824 | 1.0083x |
| 8 | 0.096528 | 0.096736 | 0.9978x | 0.087136 | 0.088832 | 0.9809x |
| 16 | 0.107679 | 0.108576 | 0.9917x | 0.120448 | 0.120896 | 0.9963x |
| 32 | 0.158960 | 0.159647 | 0.9957x | 0.176080 | 0.177119 | 0.9941x |
| 64 | 0.210336 | 0.210319 | 1.0001x | 0.230175 | 0.231760 | 0.9932x |
| 128 | 0.214719 | 0.215807 | 0.9950x | 0.241056 | 0.243040 | 0.9918x |
| 256 | 0.222399 | 0.223712 | 0.9941x | 0.249616 | 0.251776 | 0.9914x |
| 512 | 0.228080 | 0.229135 | 0.9954x | 0.270016 | 0.268927 | 1.0040x |
| 1024 | 0.245152 | 0.246096 | 0.9962x | 0.343904 | 0.345232 | 0.9962x |
| 2048 | 0.313344 | 0.313007 | 1.0011x | 0.537583 | 0.539103 | 0.9972x |
| 4096 | 0.406271 | 0.413423 | 0.9827x | 0.878303 | 0.874031 | 1.0049x |
| **Geomean** |  |  | **0.9962x** |  |  | **0.9957x** |

The activation tile is normally ready by the time transformed weights reach
MMA. An extra probe therefore adds control instructions without removing the
dominant transformed-weight or accumulator wait. The regression is broad
enough, including `0.9827x` at the primary EP8/4096 case, that no profile is
needed. The original blocking activation wait was restored.

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_gemm2_dual_peek_matrix_20260724_181349/`
- Candidate EP8/4096 gate:
  `logs/w4a16_gemm2_dual_peek_ep4096_20260724_181416/`
- Candidate and immediately restored baseline sweeps:
  `logs/w4a16_gemm2_dual_peek_full_20260724_181503/` and
  `logs/w4a16_gemm2_fragment64_adjacent_full_20260724_181721/`

### Shorten the GEMM2 decode fragment from 64 to 32 values

**Result: Retained for the EP8 target.** The first fragment-size optimization
shortened only static GEMM2 from 128 to 64 decoded values while fused GEMM1
remained at 128. This follow-up uses the decoder's existing 32-value form for
GEMM2, leaving pipeline depths, layouts, register allocation, and GEMM1
unchanged.

All six route-tile/topology numerical cases passed, and no GPU process
remained after any run. A single dense-shape gate was neutral, so the decision
uses a complete candidate sweep followed immediately by the restored
fragment-64 baseline. Speedup is baseline latency divided by candidate
latency.

| Tokens | EP8 baseline (ms) | EP8 candidate (ms) | EP8 speedup | TP8 baseline (ms) | TP8 candidate (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.045823 | 0.045568 | 1.0056x | 0.050480 | 0.050416 | 1.0013x |
| 2 | 0.052879 | 0.052752 | 1.0024x | 0.054016 | 0.054144 | 0.9976x |
| 4 | 0.076208 | 0.075664 | 1.0072x | 0.060192 | 0.060448 | 0.9958x |
| 8 | 0.096575 | 0.096079 | 1.0052x | 0.087071 | 0.087264 | 0.9978x |
| 16 | 0.107584 | 0.107552 | 1.0003x | 0.120623 | 0.121136 | 0.9958x |
| 32 | 0.159008 | 0.157952 | 1.0067x | 0.175904 | 0.177375 | 0.9917x |
| 64 | 0.210335 | 0.208815 | 1.0073x | 0.230176 | 0.232160 | 0.9915x |
| 128 | 0.214719 | 0.213168 | 1.0073x | 0.240879 | 0.243167 | 0.9906x |
| 256 | 0.222432 | 0.220896 | 1.0070x | 0.249488 | 0.251136 | 0.9934x |
| 512 | 0.227792 | 0.226784 | 1.0044x | 0.270112 | 0.269568 | 1.0020x |
| 1024 | 0.244800 | 0.244863 | 0.9997x | 0.343856 | 0.346656 | 0.9919x |
| 2048 | 0.312335 | 0.310175 | 1.0070x | 0.539775 | 0.541023 | 0.9977x |
| 4096 | 0.406767 | 0.404879 | 1.0047x | 0.870239 | 0.873487 | 0.9963x |
| **Geomean** |  |  | **1.0050x** |  |  | **0.9956x** |

Nsight Compute isolates the intended GEMM2 improvement:

| Metric | 64 values | 32 values |
|---|---:|---:|
| GEMM2 duration | 153.952 us | 152.256 us |
| Tensor-pipeline active cycles | 70.57% | 72.03% |
| Eligible warps per scheduler | 1.12 | 1.16 |
| Long-scoreboard stalls per issued instruction | 2.75 | 2.71 |
| Registers per thread | 128 | 128 |
| Local/shared spills | 0 / 0 | 0 / 0 |

The smaller fragment shortens the decode dependency region enough to improve
GEMM2 by 1.1% and produces broad EP8 gains. Simulated TP8 loses 0.44%
geometric mean, which is acceptable under the stated EP8 priority. The
32-value GEMM2 fragment is retained as the new experiment baseline.

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_gemm2_fragment32_matrix_20260724_182115/`
- Candidate and adjacent-baseline EP8/4096 gates:
  `logs/w4a16_gemm2_fragment32_ep4096_20260724_182151/` and
  `logs/w4a16_gemm2_fragment64_adjacent_ep4096_20260724_182237/`
- Candidate Nsight Compute report and parsed metrics:
  `logs/w4a16_gemm2_fragment32_ncu_ep4096_20260724_182339/` and
  `logs/w4a16_gemm2_fragment32_ncu_import_20260724_182439/`
- Candidate and immediately restored baseline sweeps:
  `logs/w4a16_gemm2_fragment32_full_20260724_182551/` and
  `logs/w4a16_gemm2_fragment64_after_fragment32_full_20260724_182705/`

### Shorten the GEMM2 decode fragment from 32 to 16 values

**Result: Rejected after the dense-shape gate.** This prototype extended the
fragment wrapper to accept one E4M3 scale byte and made each GEMM2 decode
iteration call the existing x16 PTX helper exactly once. GEMM1, pipeline
depths, layouts, and register allocation were unchanged.

All six route-tile/topology numerical cases passed, and no GPU process
remained after either performance run. EP8/4096 measured 0.436639 ms, versus
0.432127 ms for the immediately restored 32-value implementation
(`0.9897x`). At 16 values the doubled loop, vector construction, and
transformed-fragment store scheduling outweigh any further shortening of the
decode dependency chain. The single-scale wrapper support and 16-value
selection were removed without a full sweep.

Evidence:

- Staging-path failure before compilation:
  `logs/w4a16_gemm2_fragment16_matrix_20260724_183021/`
- Six-case numerical matrix:
  `logs/w4a16_gemm2_fragment16_matrix_retry_20260724_183129/`
- Candidate and immediately restored baseline EP8/4096:
  `logs/w4a16_gemm2_fragment16_ep4096_20260724_183208/` and
  `logs/w4a16_gemm2_fragment32_after_fragment16_ep4096_20260724_183405/`

### Release the packed-weight input stage before the TMEM store

**Result: Rejected after the full adjacent sweep.** CUTLASS
`grouped_mixed_input_gemm_acc_scale.py` releases an input TMA stage after its
contents have been transformed into registers but before the collective
register-to-TMEM store. This prototype moved W4A16's input-stage release to
the same boundary. Arithmetic, layouts, pipeline depths, and register
allocation were unchanged.

All six route-tile/topology numerical cases passed, and no GPU process
remained after any run. Speedup is the immediately restored fragment-32
baseline latency divided by candidate latency.

| Tokens | EP8 baseline (ms) | EP8 candidate (ms) | EP8 speedup | TP8 baseline (ms) | TP8 candidate (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.045537 | 0.045760 | 0.9951x | 0.050383 | 0.050064 | 1.0064x |
| 2 | 0.052799 | 0.053312 | 0.9904x | 0.054112 | 0.053984 | 1.0024x |
| 4 | 0.075712 | 0.076256 | 0.9929x | 0.060448 | 0.060880 | 0.9929x |
| 8 | 0.096064 | 0.098255 | 0.9777x | 0.087248 | 0.087584 | 0.9962x |
| 16 | 0.107664 | 0.108656 | 0.9909x | 0.121088 | 0.121584 | 0.9959x |
| 32 | 0.158079 | 0.159488 | 0.9912x | 0.177440 | 0.179119 | 0.9906x |
| 64 | 0.208816 | 0.210815 | 0.9905x | 0.232255 | 0.232943 | 0.9970x |
| 128 | 0.213215 | 0.215311 | 0.9903x | 0.243183 | 0.243712 | 0.9978x |
| 256 | 0.220896 | 0.223824 | 0.9869x | 0.251184 | 0.252912 | 0.9932x |
| 512 | 0.226544 | 0.230303 | 0.9837x | 0.269823 | 0.270463 | 0.9976x |
| 1024 | 0.245056 | 0.246095 | 0.9958x | 0.346863 | 0.346656 | 1.0006x |
| 2048 | 0.312767 | 0.310304 | 1.0079x | 0.540799 | 0.540879 | 0.9999x |
| 4096 | 0.405759 | 0.403104 | 1.0066x | 0.873071 | 0.869535 | 1.0041x |
| **Geomean** |  |  | **0.9923x** |  |  | **0.9980x** |

The earlier release helps the two densest EP8 shapes, but regresses every EP8
case through 1024 tokens. The likely cause is that the earlier TMA refill
competes with the current transform and TMEM-store schedule. Holding the
stage through the store is better for the full target distribution, so the
original release point was restored.

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_gemm2_early_input_release_matrix_20260724_184124/`
- Candidate and immediately restored fragment-32 baseline sweeps:
  `logs/w4a16_gemm2_early_input_release_full_20260724_184201/` and
  `logs/w4a16_gemm2_fragment32_after_early_release_full_20260724_184307/`

### Defer GEMM2's transformed-stage acquire until after decode

**Result: Rejected after the dense-shape gate.** The transformed-weight
pipeline probes its output barrier before the K loop, but previously completed
the blocking acquire before loading scales and decoding packed weights. This
prototype let static GEMM2 decode into registers first and deferred the
blocking acquire until immediately before the collective TMEM store. Fused
GEMM1 was unchanged.

All six route-tile/topology numerical cases passed, and no GPU process
remained after either performance run. EP8/4096 measured 0.436751 ms versus
0.433487 ms for the immediately restored fragment-32 implementation
(`0.9925x`). Deferring the acquire holds the packed-input stage while decode
runs and disturbs the steady producer/consumer cadence; the output-stage wait
was not expensive enough to repay that change. The original acquire point was
restored without a full sweep.

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_gemm2_late_trans_acquire_matrix_20260724_184738/`
- Candidate and immediately restored baseline EP8/4096:
  `logs/w4a16_gemm2_late_trans_acquire_ep4096_20260724_184810/` and
  `logs/w4a16_gemm2_fragment32_after_late_acquire_ep4096_20260724_184906/`

### Look ahead by one 32-value GEMM2 transform fragment

**Result: Rejected after the dense-shape gate.** An earlier one-fragment
lookahead was neutral when each transform iteration decoded 128 FP4 values.
This follow-up retested the schedule after retaining the 32-value GEMM2
fragment: the next shared-memory load was only 16 packed bytes, so the added
live range was substantially smaller. GEMM1 and numerical operations were
unchanged.

All six route-tile/topology numerical cases passed, and no GPU process
remained after either performance run. EP8/4096 measured 0.443919 ms versus
0.440079 ms for the immediately restored serial fragment-32 implementation
(`0.9914x`). Even with the smaller fragment, issuing the next load before the
current decode worsens the transform schedule. The serial load/decode/store
order was restored without a full sweep.

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_gemm2_fragment32_lookahead_matrix_20260724_201014/`
- Candidate and immediately restored baseline EP8/4096:
  `logs/w4a16_gemm2_fragment32_lookahead_ep4096_20260724_201057/` and
  `logs/w4a16_gemm2_fragment32_after_lookahead_ep4096_20260724_201130/`

### Store each decoded fragment to TMEM immediately

**Result: Rejected after the dense-shape gate.** The retained implementation
decodes four 32-value GEMM2 fragments into one register tensor and performs a
single collective register-to-TMEM copy. This prototype copied each fragment
to TMEM immediately, while preserving the full-tile fence and transform-to-MMA
commit.

The first attempt incorrectly flattened the TMEM partition. CuTe rejected it
because the `St32x32b` tiled copy owns an extra 32-way lane mode that must not
be divided like the logical register fragment. A compile-time layout probe
showed the relevant route-192 layouts:

```text
source:      ((16,1),1,1,4):((1,0),0,0,16)
destination: (((16,32),1),1,1,4):(((1,131072),0),0,0,16)
```

The corrected version divided only the final contiguous mode, preserving the
tiled-copy lane mode. It passed all six route-tile/topology numerical cases.
EP8/4096 nevertheless measured 0.435007 ms versus 0.433471 ms for the
immediately restored whole-tile store (`0.9965x`). The additional TMEM store
instructions cost more than shortening the decoded-output live range, so the
single collective store was restored without a full sweep.

Evidence:

- Incorrect flattened partition and layout diagnostics:
  `logs/w4a16_gemm2_fragment_local_tmem_matrix_20260724_201942/`,
  `logs/w4a16_gemm2_fragment_local_tmem_layout_20260724_202140/`, and
  `logs/w4a16_gemm2_full_tmem_layout_20260724_202340/`
- Six-case numerical matrix for the corrected final-mode partition:
  `logs/w4a16_gemm2_fragment_local_tmem_finalmode_matrix_20260724_202527/`
- Candidate and immediately restored fragment-32 baseline EP8/4096:
  `logs/w4a16_gemm2_fragment_local_tmem_ep4096_20260724_202605/` and
  `logs/w4a16_gemm2_fragment32_after_fragment_local_tmem_ep4096_20260724_202644/`

### Use the full decode fragment for one-stage GEMM2

**Result: Retained.** A GEMM2 with one MMA K stage has no transform pipeline
depth to fill, so splitting its decode into 32-value fragments only adds loop
overhead. The launcher now compiles a 128-value decode fragment when
`K == mma_tiler_k`, while multi-stage GEMM2 retains the 32-value fragment.
Fused GEMM1 remains at 128 values.

All six route-tile/topology numerical cases passed. The full adjacent sweep
compares the specialization against the retained always-32 GEMM2 baseline.
Speedup is baseline latency divided by candidate latency.

| Tokens | EP8 baseline (ms) | EP8 candidate (ms) | EP8 speedup | TP8 baseline (ms) | TP8 candidate (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.045520 | 0.045600 | 0.9982x | 0.050416 | 0.050368 | 1.0010x |
| 2 | 0.052800 | 0.052736 | 1.0012x | 0.054112 | 0.054400 | 0.9947x |
| 4 | 0.075712 | 0.075648 | 1.0008x | 0.060416 | 0.060224 | 1.0032x |
| 8 | 0.096048 | 0.096032 | 1.0002x | 0.087264 | 0.086848 | 1.0048x |
| 16 | 0.107679 | 0.107680 | 1.0000x | 0.121104 | 0.120160 | 1.0079x |
| 32 | 0.158016 | 0.158143 | 0.9992x | 0.177376 | 0.175456 | 1.0109x |
| 64 | 0.208992 | 0.208896 | 1.0005x | 0.232224 | 0.229695 | 1.0110x |
| 128 | 0.213200 | 0.213199 | 1.0000x | 0.242943 | 0.240159 | 1.0116x |
| 256 | 0.220927 | 0.221039 | 0.9995x | 0.251440 | 0.248752 | 1.0108x |
| 512 | 0.226992 | 0.227008 | 0.9999x | 0.268784 | 0.269664 | 0.9967x |
| 1024 | 0.244431 | 0.244736 | 0.9988x | 0.346559 | 0.346530 | 1.0001x |
| 2048 | 0.310751 | 0.310959 | 0.9993x | 0.540783 | 0.541967 | 0.9978x |
| 4096 | 0.404624 | 0.405919 | 0.9968x | 0.873167 | 0.868927 | 1.0049x |
| **Geomean** |  |  | **0.9996x** |  |  | **1.0042x** |

EP8 always uses multiple K stages in this workload and therefore executes the
same fragment-32 kernel; its difference is measurement noise. Simulated TP8
uses K=256 and benefits by up to 1.16% when autotuning selects the one-stage
K=256 tactic. The structural specialization is retained because it improves
TP8 without changing the EP8 kernel.

### Defer the deterministic GEMM2 TMA-store wait until buffer reuse

**Result: Rejected as neutral.** `PipelineTmaStore.producer_acquire()` lowers
the number of outstanding TMA-store groups to `num_stages - 1`. The existing
epilogue follows the repository's standard pattern and performs that wait
immediately after each commit. This prototype moved the wait to immediately
before reusing the corresponding shared-memory output buffer, allowing the
next accumulator TMEM load, early accumulator release, FP32 scale multiply,
and BF16 conversion to overlap the preceding store. GEMM1 was unchanged.

All six route-tile/topology numerical cases passed, and no GPU process
remained after the runs. The isolated EP8/4096 gate measured 0.432416 ms
versus 0.432575 ms for the immediately restored baseline (`1.0004x`). The
complete adjacent sweep is below; speedup is baseline latency divided by
candidate latency.

| Tokens | EP8 baseline (ms) | EP8 candidate (ms) | EP8 speedup | TP8 baseline (ms) | TP8 candidate (ms) | TP8 speedup |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.045792 | 0.045536 | 1.0056x | 0.050431 | 0.050320 | 1.0022x |
| 2 | 0.052736 | 0.052800 | 0.9988x | 0.054064 | 0.054111 | 0.9991x |
| 4 | 0.075872 | 0.075680 | 1.0025x | 0.060176 | 0.060224 | 0.9992x |
| 8 | 0.096064 | 0.096016 | 1.0005x | 0.086848 | 0.086752 | 1.0011x |
| 16 | 0.107680 | 0.107616 | 1.0006x | 0.120128 | 0.120160 | 0.9997x |
| 32 | 0.157936 | 0.158064 | 0.9992x | 0.175440 | 0.175359 | 1.0005x |
| 64 | 0.209408 | 0.208831 | 1.0028x | 0.229583 | 0.229312 | 1.0012x |
| 128 | 0.213199 | 0.213120 | 1.0004x | 0.240192 | 0.240064 | 1.0005x |
| 256 | 0.220976 | 0.220928 | 1.0002x | 0.248928 | 0.248576 | 1.0014x |
| 512 | 0.226815 | 0.226784 | 1.0001x | 0.269744 | 0.269583 | 1.0006x |
| 1024 | 0.244896 | 0.245104 | 0.9992x | 0.346447 | 0.346879 | 0.9988x |
| 2048 | 0.310560 | 0.310335 | 1.0007x | 0.541295 | 0.543711 | 0.9956x |
| 4096 | 0.410543 | 0.404751 | 1.0143x | 0.877311 | 0.877279 | 1.0000x |
| **Geomean** |  |  | **1.0019x** |  |  | **1.0000x** |

The apparent full-sweep EP8/4096 gain came from a slow baseline row and did
not reproduce in the isolated adjacent gate or prior retained sweeps. The
geomeans are within noise, so the prototype was removed.

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_gemm2_deferred_cstore_wait_matrix_20260724_134108/`
- Isolated candidate and restored-baseline EP8/4096 gates:
  `logs/w4a16_gemm2_deferred_cstore_wait_ep4096_20260724_134242/` and
  `logs/w4a16_one_k_after_deferred_cstore_wait_ep4096_20260724_134336/`
- Complete candidate and restored-baseline sweeps:
  `logs/w4a16_gemm2_deferred_cstore_wait_full_20260724_134520/` and
  `logs/w4a16_one_k_after_deferred_cstore_wait_full_20260724_134605/`

Evidence:

- Six-case numerical matrix:
  `logs/w4a16_one_k_fragment_specialization_matrix_20260724_202933/`
- Candidate and immediately restored fragment-32 baseline sweeps:
  `logs/w4a16_one_k_fragment_specialization_full_20260724_202955/` and
  `logs/w4a16_fragment32_after_one_k_specialization_full_20260724_203145/`

## Post-SM12x-Sync Experiments

These experiments start from the live PR #4048 head
`23bfb509eea252ffed9c7220e740204eb0112632` on the local-only branch
`agent-w4a16-sm120-perf-experiments`. They evaluate techniques suggested by
the SM12x W4A16 update in PR #4255 without changing the PR branch, committing,
or pushing.

The comparison workload remains the ledger's CUDA 13.2 B200 workload:
CUPTI timing, CUDA graphs, PDL, deterministic non-fused finalize, 10 warmups,
100 iterations, and the full 1-4096-token EP8 and simulated-TP8 sweeps. This
workload does not execute the fused-finalize output memset, so memset overlap
is not part of these measurements.

### Explicit CuTe DSL optimizer level 3

**Result: Already the default; no code or timing A/B needed.** The restored
CUDA 13.2 environment installs `nvidia-cutlass-dsl==4.6.1`. Both the installed
runtime and the checkout's vendored `CompileOptions` initialize
`OptLevel(3)`, and `cute.compile` uses those options when the call supplies no
override. Rewriting the existing call as explicit O3 would therefore preserve
the same compiler configuration rather than reproduce the SM12x O2-to-O3
change.

The previously created devbox had expired before this experiment began:
`h list -c c1` returned no devboxes and direct SSH reported
`flashinfer-pr4048-cu132` not found. Recreate the same named 8xB200 devbox with
`pytorch/pytorch:2.13.0-cuda13.2-cudnn9-devel` before restoring the PR-head
checkout and pinned CUPTI packages.

The replacement environment is verified as 8x NVIDIA B200, driver
580.126.09, CUDA toolkit 13.2.78, Torch 2.13.0+cu132, `cupti-python==13.2.0`,
and `nvidia-cuda-cupti==13.2.75`. The remote checkout is the exact PR head
`23bfb509eea252ffed9c7220e740204eb0112632`.

Evidence:

- `logs/w4a16_sm12x_setup_20260803_161000/run.log`
- Excluded generic-CLI baseline attempt, stopped during first compilation after
  switching to the existing six-decimal W4A16-only harness:
  `logs/w4a16_sm12x_baseline_pr4048_20260803_161500/`

### Right-size one-wave static persistent launches

**Result: Rejected.** The existing launcher already detects when fused GEMM1
fits within one resident cluster wave and disables CLC, but the static path
still manually launches the full resident cluster count. The minimal prototype
replaced that manual grid with the repository's existing
`StaticPersistentTileScheduler.get_grid_shape(...)` call. This computed the
problem-size-limited grid from the runtime scheduler parameters while keeping
`max_active_clusters` as the compile-time hardware occupancy limit, so it
added no host plumbing, cache key, or shape-specific compilation.

The precise baseline uses the existing wrapper-workspace harness
`bench_w4a16_ep8_tp8.py`, which isolates CuTe DSL W4A16 and prints six-decimal
latencies while preserving the same 10/100, CUDA-graph, CUPTI, PDL,
deterministic-finalize, EP8/simulated-TP8 workload. Its run uses private CuTe
DSL and FlashInfer compilation caches and validates all 26 expected result
rows before completion.

The one-line scheduler prototype passes the existing six-case route-tile
boundary numerical matrix: `6 passed`. The matrix covers route tiles 8, 16,
32, 64, 128, and 192 across 1-CTA, 2-CTA, and mixed GEMM tactics. The two
baseline sweeps and the candidate sweep each produced and validated all 26
expected result rows.

A/B/A results in milliseconds follow. The last column is the arithmetic mean
of the two baseline latencies divided by the candidate latency; values above
one favor the candidate.

| Config | Tokens | Baseline 1 | Candidate | Restored baseline | Mean-baseline / candidate |
|:--|--:|--:|--:|--:|--:|
| EP8 | 1 | 0.045488 | 0.045696 | 0.045535 | 0.995962x |
| EP8 | 2 | 0.052223 | 0.052160 | 0.052128 | 1.000297x |
| EP8 | 4 | 0.074960 | 0.074912 | 0.074880 | 1.000107x |
| EP8 | 8 | 0.095344 | 0.096992 | 0.097024 | 0.991669x |
| EP8 | 16 | 0.108304 | 0.108352 | 0.108256 | 0.999335x |
| EP8 | 32 | 0.158624 | 0.158704 | 0.158369 | 0.998693x |
| EP8 | 64 | 0.210208 | 0.210240 | 0.209584 | 0.998364x |
| EP8 | 128 | 0.213376 | 0.213328 | 0.213408 | 1.000300x |
| EP8 | 256 | 0.221856 | 0.222144 | 0.222176 | 0.999424x |
| EP8 | 512 | 0.227216 | 0.227967 | 0.227760 | 0.997899x |
| EP8 | 1024 | 0.242895 | 0.242928 | 0.242944 | 0.999965x |
| EP8 | 2048 | 0.305872 | 0.305472 | 0.305648 | 1.000943x |
| EP8 | 4096 | 0.398368 | 0.398656 | 0.397952 | 0.998756x |
| simulated TP8 | 1 | 0.050272 | 0.050176 | 0.050368 | 1.002870x |
| simulated TP8 | 2 | 0.054064 | 0.053888 | 0.054176 | 1.004305x |
| simulated TP8 | 4 | 0.060368 | 0.059904 | 0.060448 | 1.008413x |
| simulated TP8 | 8 | 0.087008 | 0.086848 | 0.086833 | 1.000835x |
| simulated TP8 | 16 | 0.120832 | 0.120896 | 0.120832 | 0.999471x |
| simulated TP8 | 32 | 0.175936 | 0.175888 | 0.175984 | 1.000409x |
| simulated TP8 | 64 | 0.229953 | 0.228896 | 0.230144 | 1.005035x |
| simulated TP8 | 128 | 0.240815 | 0.240880 | 0.240608 | 0.999300x |
| simulated TP8 | 256 | 0.250401 | 0.250592 | 0.250656 | 0.999747x |
| simulated TP8 | 512 | 0.269375 | 0.269488 | 0.269359 | 0.999551x |
| simulated TP8 | 1024 | 0.345280 | 0.344656 | 0.344528 | 1.000720x |
| simulated TP8 | 2048 | 0.536048 | 0.535583 | 0.536240 | 1.001047x |
| simulated TP8 | 4096 | 0.850688 | 0.847888 | 0.849776 | 1.002765x |

Against the mean of the two baselines, the candidate geomeans are
`0.998591x` for EP8, `1.001879x` for simulated TP8, and `1.000233x` overall.
The approximately 0.19% TP8 improvement is too small to distinguish from run
noise and is offset by EP8. No individual simulated-TP8 row reaches 1%, and
the full workload improves by only 0.02%. The prototype was therefore removed;
both the local experiment branch and remote checkout are restored to the
exact PR head with no source diff.

An initial candidate command stopped during preflight on an informational
package-version print quoting error. The benchmark process had not started,
so it produced no timing data and is excluded.

Static validation before both candidate sync and final restoration:
`pre-commit run --all-files` passed.

Evidence:

- `logs/w4a16_sm12x_precise_baseline_20260803_161900/`
- `logs/w4a16_sm12x_rightsize_grid_matrix_20260803_163000/`
- `logs/w4a16_sm12x_rightsize_grid_candidate_20260803_163300/`
- `logs/w4a16_sm12x_rightsize_grid_restored_20260803_163600/`
