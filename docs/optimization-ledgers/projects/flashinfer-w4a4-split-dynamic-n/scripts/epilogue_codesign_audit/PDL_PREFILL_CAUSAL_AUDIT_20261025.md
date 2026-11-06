# PDL prefill causal audit, 2026-10-25

CPU-only source/trace review of the frozen `bbb04823` core and `a3b0042e`
preparation against corrected `aab93f854`. No new GPU work, source edits, or
benchmark reruns. The component harness review is
`PDL_COMPONENT_REVIEW_5c2499db.json`; independent SQLite extraction and input
hashes are in `PDL_PREFILL_TIMELINE_REVIEW_20261025.json`.

## What the measurements can distinguish

`scripts/pdl_startup_experiment/probe_native_v2.py:160–185` times
`original_fc1` and `original_fc2` separately. The former enters the shared
host wrapper, whose `blockscaled_contiguous_grouped_gemm_finalize_fusion.py:139–158`
executes preparation before FC1. It contains no FC2 or combine. The latter
contains FC2 only. The CUPTI timer captures exactly one `call_fn()` in its
graph (`flashinfer/testing/utils.py:1195–1199`); cold-L2 flushing is outside
that graph. Consequently:

- The approximately 25% isolated preparation+FC1 regression cannot be
  explained by FC1→FC2 or FC2→combine competition.
- The approximately 3.6% isolated FC2 regression is additional evidence
  of a changed standalone kernel cost. It cannot be dismissed as the
  longer FC1 predecessor wait seen in the full-chain trace.
- The phase numbers are not additive full-chain predictions. Programmatic
  dependencies change scheduling only when a relevant successor exists.

The new trace is one warmed replay per arm, not a replacement for the
10/100 cold-L2 benchmark samples. Times below are relative to each arm's
first routing kernel.

| Kernel | Control start/end (us) | Early start/end (us) | Registers control→early | Dynamic SMEM |
|---|---:|---:|---:|---:|
| Prepare | 33.568 / 58.976 | 33.760 / 59.296 | 32→32 | 0 |
| FC1 N256 | 58.752 / 259.457 | 55.872 / 319.616 | 80→88 | 195584 |
| FC2 N256 | 258.881 / 403.777 | 286.304 / 464.032 | 120→122 | 229888 |
| Combine | 403.201 / 484.129 | 320.672 / 551.616 | 80→80 | 0 |

Both GEMMs retain 148 blocks, 288 threads/block, two-CTA clusters and
74 maximum active clusters. `localMemoryPerThread` is zero for each;
this metadata does not replace inspection of executed spill instructions.
Nsight's process-wide `localMemoryTotal` is not per-kernel spill evidence.

Prepare duration is 25.408→25.536 us. Early FC1 begins only 2.880 us earlier,
yet its duration grows 200.705→263.744 us. Before candidate FC2 starts,
candidate FC1 has already run 230.432 us, exceeding the entire control FC1
duration. This makes downstream contention an insufficient explanation for
the main loss. Candidate FC2 duration grows 32.832 us while its overlap
with unfinished FC1 is 33.312 us; that full-chain duration increase largely
contains predecessor waiting. Combine similarly includes a long FC2 wait.

## Code generation is a live confounder

The prior equal-resource receipt covered N16 only. N256's 80→88 and
120→122 register counts establish a different compiled allocation.
Both still have one GEMM CTA per SM, so these counts do not establish an
occupancy cliff. They also do not prove that registers caused the slowdown;
instruction ordering, register lifetimes and generated control flow remain
to be compared in N256 PTX/SASS.

The source delta is more than trigger location: the former all-thread tail
trigger becomes a warp-0/elected-thread block near the start of the
kernel (`core:1003–1015`). The FC1 specialization has no new release fence,
but does have the new runtime branch and election. FC2 additionally emits
a device release before its sole early trigger. Those constructs can
affect whole-kernel code generation even though the mathematical body is
unchanged. Do not claim a scheduling-only experiment or automatically
restrict N256 based on the current comparison.

## Smallest causal comparison and next source delta

First use the already reviewed frozen-source component harness
`probe_components.py` (SHA256
`5c2499dbda88d8e1c1767698e65b5cdb018554ca2b63e57b1bdeb9b679dd6021`):

1. Candidate preparation plus original core: isolates preparation's
   earlier scheduling signal without changing GEMM code generation.
2. Original preparation plus candidate core: isolates core signals and
   their code generation, keeping preparation's original schedule.

The harness keeps separate actual modules/caches, records every executed
component path/hash, and preserves the v2 diagnostic/capture/timing ASTs.
No new source or token/model-dependent eligibility is needed.

If the core-only arm retains the FC1 loss, the next minimal source
experiment is **FC1 only: retain the early location but restore the original
all-thread trigger organization**, eliminating the new warp/election
branch for that static specialization. Keep FC2's elected
wait→release→trigger block unchanged. Compile the two already selected
N16/N256 geometries first and inspect N256 registers, local operations,
branch structure and mainloop instruction scheduling before timing.
This tests an actual code-generation difference without changing stages,
grid, tile size, arithmetic or public API.

Do not move an unfenced all-thread FC2 trigger ahead of the elected release.
The finalizer reads routing metadata before its own output wait, so its
publication proof must remain intact. Every CTA, including zero-work CTAs,
must retain a trigger or complete normally.

## Static policy boundary

A stage-specific decision is more defensible than a token threshold:
preparation's signal only hides FC1 startup; FC2's signal can hide combine
metadata work. The existing generic geometry/resource facts (cluster size,
GEMM SMEM, threads, TMEM and available successor startup work) can explain
limits, but they do not yet justify a permanent N256 prohibition. The
timeline demonstrates real graph overlap. The remaining question is
whether its benefit survives otherwise comparable generated code.

Official semantics remain those recorded in `PDL_AUDIT_20261025.md`:
[PTX griddepcontrol](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-griddepcontrol)
requires all CTAs to trigger or complete before dependent eligibility;
[CUDA PDL graph behavior](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html#use-in-cuda-graphs)
is opportunistic and does not guarantee co-residency. No new synchronization
or eligibility mechanism is proposed here.
