# Scheduler investigation, frozen 7829fc00

This workspace contains isolated scheduler prototypes for the blockscaled
split core at `7829fc00dc7121341cc40cd4190660507e006490`. Production remains
unchanged while the experiments run. The native harness times FC1 only, using
actual native routing and shared output allocations for paired byte checks.

## Prior evidence and hypotheses

The local W4A16 ledger at
`/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md`
provides the prior controls:

- Lines 2471–2600: one-item CLC contracted the dense FC1 tail. Bundles of two or
  four hoarded too much work and regressed; a post-acquire CLC query constrained
  the number of future assignments held by each cluster.
- Lines 2600–2710: full-warp response consumption was better than a one-lane
  decode. One metadata stage was retained for CLC FC1, three for static FC2.
- Lines 4065–4130: N-major raster did not improve the prior end-to-end kernel;
  enabling FC2 CLC regressed. Neither is assumed transferable without evidence.

Current split-core producer, epilogue, and MMA roles independently walk a fixed
strided route-major tile sequence. Different valid-row counts therefore assign
unequal tensor-core and epilogue work permanently to resident clusters. CLC can
replace the assignment while preserving the payload, scale, and MMA pipelines.
A static N-major permutation is a cheap control for balancing versus locality.

The current SM100 MegaMoE `moe_persistent_scheduler.py` has a CLC implementation
and optional work bundles. Its `fc1_fc2_fuse_sched.py` explicitly reserves and
rejects CLC for the fused scheduler itself, so those are distinct capabilities.
The prototype uses the installed CUTLASS
`ClcDynamicPersistentTileScheduler` / `PipelineClcFetchAsync` APIs, following the
retained W4A16 protocol instead of importing MegaMoE scheduler dependencies.

## Prototype contracts

`build_variants.py` reads the frozen commit with `git show`, writes immutable
baseline/helpers plus derived modules, and records SHA256s in `manifest.json`.

- `clc1_core.py` / `clc2_core.py`: add one scheduler warp only to FC1. A one- or
  two-stage local metadata queue publishes tile, expert, valid-row count, and a
  final sentinel to every original consumer thread. Each CLC cancellation is
  one output work tile. Query ownership is CTA rank zero in the launch cluster;
  both CTAs consume the multicast response. Padded route capacity is skipped.
  Queries follow metadata-slot acquisition for live work.
- Existing producer, MMA, epilogue, PDL, per-token and scale arithmetic remain
  intact. FC2 keeps the static loop. The prototype has small metadata SMEM and
  one extra warp, but no additional activation/weight payload stage.
- `nmajor_core.py`: maps the existing finite linear work range to N-major order.
  The loop remains explicitly bounded, avoiding the old W4A16 termination bug.

## Environment and execution

Existing c1 devbox `fi-w4a4-dyn-n-1024`, namespace ziangli; B200,
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.7.1.
GPU0 owns CLC; GPU6 owns the independent static-raster control. Other GPU
investigations do not share these devices. Managed `/usr/local/bin/h` only.

Native FC1 timing: T16384/H7168/I2048, top-k 8, 32 local experts, native routing,
M256/two-CTA, N256 initially. Cold-L2 CUDA graphs, CUPTI, 10 warmups and 100 timed
iterations. Every process performs one native preparation, then runs paired
byte checks and adjacent arms from the same captured inputs/outputs. The
baseline is repeated at the end of each sequence to detect drift. The returned
zero placeholder prevents the native driver from timing the full pipeline.

Initial one-CTA NVFP4 N128 quantized/per-token-BF16 smoke: both CLC1 cases pass
bytewise (`logs/scheduler-clc1-smoke-7829-gpu0.log`). All 24 format/SF/topology/per-token/short-K cases subsequently passed
(`logs/scheduler-clc1-contract-7829-gpu6.log`).

```bash
# From remote candidate checkout
CUDA_VISIBLE_DEVICES=0 PYTHONPATH=. TRTLLM_ENABLE_PDL=1 OMP_NUM_THREADS=1 \
 ../.venv/bin/python ../scripts/scheduler_experiment/profile_native_fc1.py \
 --repo . --tile 256 --variant baseline,clc1,clc2,baseline \
 --output ../logs/scheduler-clc-n256-7829-gpu0.json
CUDA_VISIBLE_DEVICES=6 PYTHONPATH=. TRTLLM_ENABLE_PDL=1 OMP_NUM_THREADS=1 \
 ../.venv/bin/python ../scripts/scheduler_experiment/profile_native_fc1.py \
 --repo . --tile 256 --variant baseline,nmajor,baseline \
 --output ../logs/scheduler-nmajor-n256-7829-gpu6.json
```

Helper files and all rejected experiments stay local to this workspace; only a
validated final retained implementation belongs in the source PR.

## Initial results

Times below are isolated native FC1 medians, in microseconds. Cross-GPU values
are not compared; each row uses its own adjacent control.

| GPU / sequence | N256 medians us | Finding |
| --- | --- | --- |
| GPU6 baseline / N-major / baseline | 324.496 / 335.344 / 324.288 | N-major regresses about 3.38%; rejected |
| GPU0 CLC1 / CLC2 / baseline | 318.271 / 321.679 / 327.6475 | One-stage CLC is about 2.86% faster; two-stage is less effective |
| GPU0 baseline / static metadata / wave rotation / CLC1 / baseline | 327.583 / 330.415 / 329.424 / 318.239 / 330.415 | CLC1 repeats its gain; metadata lookahead alone and wave rotation do not win |

Every completed native candidate passes paired output/SF byte comparison.
The static metadata control adds the same scheduler warp and one-stage metadata
queue but retains original assignments; this isolates the benefit of dynamic
claims from metadata prefetch. The wave-rotation control shifts a cluster's
assignment between resident waves without adding any warp or payload stage.
It also fails to reproduce the CLC benefit.

The first native CLC prototype stalled after timing its baseline at 326.527 us.
It was terminated, and no candidate timing from that run is valid. The revised
prototype returns metadata pipeline state explicitly from the next-work helper
and performs `mbarrier_init_fence` before cluster synchronization. Four bounded
NVFP4 topology/per-token smoke cases and the repeated native multi-wave cases
then complete. These fixes are part of the isolated prototype, not evidence of
a production defect. Failed and corrected logs are preserved.

Raw data: `../../logs/scheduler-*.json` contains every 100-sample timing vector
and harness hash; `.log` files contain exact-check results and failures.


## Scope checks and profile

- NVFP4 T16384/N128 CLC1: 338.031 / 365.263 / 339.6785 us control/candidate/control;
  CLC2 also regresses at 359.2155 versus 337.247 us. Both are rejected at N128.
- NVFP4 T4096/N256: 121.008 / 120.0795 / 120.944 us, below 1% and treated as neutral.
- NVFP4 T8192/N256: 192.849 / 190.384 / 192.7845 us, about 1.26% lower latency.
- MXFP8 T16384/N256: 456.111 / 462.3665 / 490.719 us. The 7.6% control drift
  prevents a reliable performance conclusion; exact output/SF bytes pass.
- W4A8 T16384/N256: 432.911 / 424.463 / 451.007 us. The 4.2% control drift
  prevents a reliable performance conclusion; exact output/SF bytes pass.

One NCU baseline/CLC1 capture on GPU6 measured:

| Metric | Static | CLC1 |
| --- | ---: | ---: |
| Threads/CTA | 288 | 320 |
| Registers/thread | 90 | 80 |
| Dynamic SMEM bytes | 195584 | 195584 |
| Active cycles average | 543969.290541 | 564537.851351 |
| Active cycles maximum | 581832 | 572649 |
| Active cycles minimum | 479778 | 556929 |
| Elapsed cycles average | 584252.432432 | 574926.054054 |
| Max/average active cycles | 1.0696 | 1.0144 |
| Max/min active-cycle spread | 21.27% | 2.82% |

This supports reduced imbalance, while the repeated static-metadata control
rules out claiming that metadata prefetch alone caused the gain. NCU replay
elapsed cycles (~1.6% improvement) are diagnostic, distinct from CUPTI timing.
Source raw metrics are in `logs/scheduler-clc-n256-7829-gpu6-ncu-raw.csv`; the
`.ncu-rep` stays on the remote project. Metadata capture confirms 139008 row
capacity, 543 route-tile capacity, and only 77 live route tiles.

## Bounded physical CLC capacity

The original CLC launch uses 543*16=8688 output-work cancellation units for the
native N256 problem, of which 77*16=1232 contain live work. Every padded response
is skipped and followed by another query until hardware reports exhaustion.
No assumption about hardware cancellation order is used.

`clccap32` and `clccap16` cap the physical grid at 32 or 16 resident cluster
waves, bounded above by the original capacity. Every kernel computes
`chunk_size=ceil(live_output_tiles/physical_workgroups)` on device and maps each
claimed workgroup to `[id*chunk_size, min((id+1)*chunk_size, live_output_tiles))`.
These disjoint intervals cover every live output tile for any routing load.
Metadata publication and queries retain the post-acquire ordering. For the
native N256 case, cap32 uses 2368 physical units and one output tile per unit;
cap16 uses 1184 physical units and two output tiles per unit. This separates
reduced padding from the coarser scheduling previously rejected by the ledger.

The first bounded-grid invocation did not reach the new modules because the
helper upload exceeded Linux's per-argument size limit. The uploader now sends
bounded batches; no failed upload is counted as a kernel result. The mixed
benchmark helper also initially rejected an unhandled timing keyword in the
diagnostic callback; the corrected callback accepts that unused metadata.


Bounded-grid measured result, native N256 GPU0, same process:
CLC1 318.559 us; cap32 318.3195 us; cap16 329.551 us; static 326.2555 us.
Reducing the cancellation grid while preserving one-item granularity gains only
0.08%, so padded cancellation is not a material bottleneck in this case.
Coarsening to two output tiles loses 3.45% versus CLC1 and erases the win over
static. Both cap variants remain rejected local experiments.

### Strengthened coverage validation

Earlier paired checks reused the reference-filled output allocation to keep
unwritten padding identical. That can hide an erroneous skipped valid write.
The final checks restore the same sentinel bytes before *each* implementation,
so missing writes and incorrect writes are both observable. This supersedes the
earlier correctness boundary rather than changing any measured kernel code.

- Native NVFP4 T16384/N256: CLC1, cap32, and cap16 each pass after resetting all
  output and scale bytes to 77 before the candidate.
- Cap32 all 24 format/SF/topology/per-token cases pass with 521 routed rows,
  M8192 and one static resident group. Runtime chunk lengths exceed one for
  both N128 and N256, explicitly exercising coverage of multi-item intervals.
- CLC1 passes the larger 24-case matrix and eight zero-live-work/single-row
  cases spanning one-/two-CTA and per-token modes. Final logs are
  `scheduler-clc1-coverage-7829-gpu6.log` and `scheduler-clc1-edges-7829-gpu0.log`.

No production source changes have been made. Recommended retention boundary is
one-stage CLC as a candidate for large NVFP4 M256/N256 FC1 only; N128 and small
shapes retain static scheduling. A shape/format guard and combined screen are
required before integrating. Cross-format performance remains unproven due the
recorded control drift. No full-pipeline performance claim follows from these
isolated FC1 measurements.

## NB2 follow-up and handoff

The channel-pair activation-reuse follow-up is archived in [NB2.md](NB2.md).
It produces a logical M512/N128 FC1 tactic using two physical M256 instructions,
four native K steps, four SF16/five SF32 stages, and unchanged fused arithmetic.
The final composed logical geometry passes44 capability/tactic checks and36
GPU exact pairs; source/input hashes and root-review patch are preserved in
`integration_manifest.json`, `integration_base/`, `integration_snapshot/`, and
`integration.patch`. Root applied it and owns combined/full-AUTO retention.
CLC remains diagnostic; no CLC production change is included.
