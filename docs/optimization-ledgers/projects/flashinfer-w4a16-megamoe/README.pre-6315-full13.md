# FlashInfer NVFP4 W4A16 MegaMoE

Authorized work: implement true fused expert-parallel W4A16 MegaMoE, extend
`benchmarks/bench_cute_dsl_moe_distributed.py`, validate numerics on C2 B300
CUDA 13.2, optimize 1-4096 tokens with CUPTI/nsys/ncu, and create an upstream
draft PR after the initial implementation. Keep pushing follow-up commits.

- Repository: `flashinfer/`, independent clone, branch `feat/w4a16-megamoe`.
- Initial upstream: `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.
- Managed HAI CLI: invoke `/usr/local/bin/h` directly; the local `hai/` clone
  is only a working directory, never the CLI/runtime source.
- Image: `nvcr.io/nvidia/pytorch:26.05-py3`, newest CUDA 13.2 image per live
  NGC catalog + NVIDIA release matrix checked 2026-09-07. CUDA 13.2.1.009.
- Devbox: C2 `fi-w4a16-mega-0907`, requested eight B300 GPUs. Initial default
  CPU/memory sizing could not schedule; retried with 64 CPUs/512 GiB.

Prior implementation: https://github.com/flashinfer-ai/flashinfer/pull/4048

Draft upstream PR: https://github.com/flashinfer-ai/flashinfer/pull/5019

Current PR head is `6315f94ceb279db53ec3149a7d81e19b332c8dd0`: curated12-tactic
Mega autotuning/cache, N64 geometry and derived decoded staging, always two
decode warpgroups. Numerical, lifecycle and CPU validation pass. All performance evidence
uses exact source overlays, never the stale remote Git HEAD.

Packed weights and scales are decoded directly into BF16 TMEM by the reused
local W4A16 converter. Two groups split each K tile; decoded TMEM, BF16
activation and FP32 accumulator rings retain two stages. The raw ring fits up
to five stages using actual shared-memory layouts. Geometry is M256/N128/K256,
physical cluster(2,1), dynamic routed N. BF16 weights are not materialized.

- Current full13 paired CUPTI run: `tmem-fitted5-transform2-paired-001`, 1–4096
  global tokens, EP8 B300, H7168/I2048/E256/topk8. 104 actual split selections
  and16 source hashes verified. 4096: split0.544547ms, Mega0.506356ms,
  1.0754x. Two groups improve12/13 Mega rows vs adjacent one-group; the64-token
  regression did not reproduce in a2/1/2 group repeat. See
  [full comparison](FITTED_TRANSFORM_GROUP_COMPARISON_001.md).
- Current GPU suite:10 EP1 pass(63.24s),10 perEP2 rank pass(89.71/89.76s),
  `logs/tmem-fitted5-transform2-public-001*`. The added H9216/I64/M257 case
  exercises36 FC1 K256 tiles with FC1 alphas normalized by1/sqrt(H).
  Existing nine cases and numerical tolerances are unchanged.
- Exact corrected diagnostic `logs/diagnostic-h9216-split-002`: Mega/split
  FC1, per-routeFC2 and final outputs are bitwise equal for raw and normalized
  fixtures. The raw fixture's midpoint-sensitive BF16 FC1 value yields the
  same oracle failure in both kernels; normalized fixtures both pass. Keep
  raw001/002 evidence and original failed test logs; do not relabel them.
- [Current codegen audit](FITTED5_TRANSFORM2_CODEGEN_REVIEW_001.md): all8ranks,
  REG96,640threads,61440 balanced CTA register pool, unchanged21SASS/40PTX
  local ops and no transform locals. Fitter is instruction-identical to the
  corrected constant-raw5 two-group predecessor at H7168.
- [Current two-group PC NCU audit](profiles/tmem-fitted5-transform2-ncu-pc-001/ANALYSIS.md)
  is complete; rank2 lacks useful compute samples. Current nsys software capture is complete on all eight devices; hardware tracing
  lost device2 timestamps. See `FITTED_NSYS_CAPTURE_AUDIT_001.md`.
  Instrumented durations are never CUPTI latency. SystemCUDA13.2 and bundled
  compiler13.3.27 are distinct.
- Current local candidate adds the three-geometry/12-tactic existing Mega auto
  lifecycle. Two decode groups stay fixed. N64 gets three decoded TMEM stages
  using remaining capacity; N128 retains two. Both N64 geometries passed
  EP1/EP2 oracle suites before the old box disappeared. Those old tracked-only
  numerical manifests have a disclosed source-inventory gap; see ledger016.
- Replacement `fi-w4a16-mega-0908` is running on C2 `hu-pdx-88`, eightB300,
  explicit26.05 image rechecked against the live NVIDIA matrix. The previous
  box disappeared during stage3 timing; unfetched timing/codegen is not evidence.
- Replacement current M256/N128 numerical run passed10EP1 (171.59s including
  first quantization JIT) and10perEP2 (89.61/89.78s), with unchanged v2 source
  attestation. H9472/I64 actually fits raw4; observed geometry proves the intended
  fallback and37FC1Ktiles. Public host105cases pass2.72s after correcting the new
  bootstrap test fixture. Auto lifecycle and fresh paired CUPTI are next.


The live [PR_BODY.md](PR_BODY.md) has one complete final13 timing table and
is updated whenever the current best changes. Detailed experiment history is
local in [w4a16_optimization_experiments.md](w4a16_optimization_experiments.md)
and [PERFORMANCE_LEDGER.md](PERFORMANCE_LEDGER.md), with immutable raw artifacts.
Prior expanded PR bodies are preserved as `PR_BODY.pre-final-table-c7713ba1.md`
and `PR_BODY.pre-tmem-16aa85bd.md`. Upstream GPU CI was authorization-gated;
local results do not establish its status. Keep PR5019 draft.

`remote.py` uses the managed HAI CLI for commands and explicit source overlays.
Use `remote.py run '<command>'`, `remote.py sync <repository-relative-files>`,
or `remote.py get <remote-project-relative-file> <local-destination>`.
The active remote GPU source is `/workspace/flashinfer-w4a16-megamoe/flashinfer`.
An independent `host-validation` source copy supports CPU checks during GPU
benchmarks. Do not change the active GPU source during a benchmark/profile run.
Use explicit localhost torchrun rendezvous; `--standalone` advertises a node
hostname this container cannot resolve.

Read-only historical evidence:
`/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md`
and sibling `logs/`.

Coordinate GPU ownership with the parent before any launch or active-source
overlay. CPU artifact reviews may run against `host-validation` concurrently.

## Numerical contract

Packed NVFP4 E2M1 times per-16 E4M3 scale decoded online to BF16, BF16 MMA
with FP32 accumulation, global weight alpha applied after accumulation, BF16
FC1 activation handoff, post-FC2 FP32 routing-weight application and BF16 output.
BF16 dispatch/combine. No activation or FC2-input quantization. Compare the
same packed weights, exact scales, routes and inputs to the existing W4A16
plus EP communication control, without relaxing numerical tolerance.
The split control rounds each rank's weighted partial to BF16 before rank
combine; Mega weights all per-route BF16 FC2 values in FP32 and converts once.
The isolated EP8 global8 diagnosis found all 458,752 per-route values bitwise
equal, but three final-tensor failures under the unchanged strict tolerance.
The optional cross-backend final `--refcheck` is therefore omitted from timing;
independent oracles and exact contract tests remain the correctness gate.

## Evidence rules

Keep scripts, logs, Nsight reports, experiment ledger and PR-body drafts here.
Record source SHA and candidate patch hash per run. Use full layer timing for
primary results; distinguish summed kernel durations from GPU span. Run ncu
on coordinated collectives rather than replaying a single participating rank
in isolation. Retain rejected experiment results and revert unhelpful changes.

The existing benchmark defines 1-4096 as global tokens. Preserve and label
that convention; EP8 low-token cells include zero-token ranks.
