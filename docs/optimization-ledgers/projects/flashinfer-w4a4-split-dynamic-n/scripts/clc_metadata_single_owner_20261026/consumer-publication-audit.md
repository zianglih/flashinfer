# Consumer metadata arrival audit — rejected without implementation

Source: retained `7f4e1703` plus the frozen single-owner producer patch
`e7de223d7458c7275b14162632f36e9da47e2c1aeb1115c06a2a3eb9c264f262`.
No source changes or additional GPU experiment were made for this idea.

The proposal was to make one lane per consumer warp load the three metadata
scalars and release the empty barrier, then broadcast those registers. This is
not a useful instruction simplification for the current converged consumer path.

## Existing source and actual codegen

`next_work` (kernel lines 1233–1247) waits for the full stage, reads three ordinary
shared values, releases the empty stage, and advances state. The roles are four
producer/inline-epilogue warps, optionally four separate epilogue warps, and one
MMA warp. Thus CLC has five or nine full consumer warps per CTA, matching the
current `threads_per_cta - 32` count of 160 or 288 lanes. The scheduler is the
remaining warp. Both CTA ranks execute their own complete role groups.

All six `next_work` call sites are at role entry or the bottom of a role loop;
none is nested in a lane predicate or the MMA leader-CTA check. Warp selection,
metadata index/phase, tile loop continuation and CTA rank are warp-uniform.
Lane-varying copy/store predicates finish before the next metadata call, and
there are no lane-specific kernel exits. The terminal ticket follows the same
release path before all roles join the final CTA barrier.

Actual candidate SASS for two-CTA MXFP4x8 FC1 with PDL enabled contains:

```text
0x1550 SYNCS.PHASECHK.TRANS64.TRYWAIT P0, [UR29+0x188], R2
0x1570 LDS.64 R2, [UR29+0x198]
0x15b0 LDS R5, [UR29+0x1a0]
0x15c0 SYNCS.ARRIVE.TRANS64.A1T0 RZ, [UR29+0x190], RZ
```

The loop repeats the same unpredicated arrival at 0x2210. The other role copies
use it at 0x2a10, 0x4ce0, 0x5450 and 0x6100. Each site has one issued arrival
instruction per converged warp, with a uniform address in `UR29`. There is no
generated per-lane loop or sequence of 32 distinct SASS arrivals. The two shared
load instructions likewise use the same addresses across the warp. The full
artifact is `results/gate/candidate/config3-fc1-pdl1.sass`; corresponding PTX and
the 16 source-paired codegen records are already preserved.

## Hardware contract and decision

NVIDIA's [asynchronous-barrier warp-entanglement documentation](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/async-barriers.html#warp-entanglement)
states that converged warp arrivals perform one barrier update; divergent groups
can perform multiple updates. The semantic arrival count still represents all
participating lanes. Its [shared-memory bank documentation](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#shared-memory-and-memory-banks)
also explains that same-address reads within a warp are broadcast. Both primary
sources were checked live on 2026-10-27 UTC.

A single reader/releaser could be made correct by having that owner finish all
three reads before releasing, then broadcasting its registers after release.
However, it would still issue an arrival and the same loads while adding owner
selection and three broadcasts. It would not remove the existing hardware warp
aggregation or shared-memory traffic. We therefore reject this idea without
implementation or timing. This differs from the producer change, which removes
an actual async-proxy fence and named barrier from generated code.
