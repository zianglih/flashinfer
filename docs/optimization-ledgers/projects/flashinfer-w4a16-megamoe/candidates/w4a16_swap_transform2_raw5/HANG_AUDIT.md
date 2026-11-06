# Source audit of the 640-thread production warmup hang

The original transform2 CPU budget argument is invalid. Its arithmetic tested
against the SM's65,536-register capacity rather than the registers allocated
to this CTA at launch. This source audit made no GPU queries, launches or
active-source edits.

## Confirmed blocking condition

The combined frontend launches640 threads at96 registers/thread, so its CTA
initial allocation is61,440. Control warps release2,048 registers by reducing
96→80, and dispatch releases4,096 by reducing96→64. Epilogue requests10,240
by increasing96→176. The two transform groups retain96. This leaves a4,096
register shortfall, even though the proposed steady65,536 total fits an SM.

Registers outside the CTA's launch allocation cannot be acquired by its
`setmaxnreg.inc`. NVIDIA's explanation states: “The total number of registers
allocated to the CTA does not change.” See
[NVIDIA Nsight engineer explanation](https://forums.developer.nvidia.com/t/sm90-setmaxnreg-will-change-occupancy-dynamically/302068)
and the [PTX setmaxnreg contract](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#miscellaneous-instructions-setmaxnreg).

Root's live CUDA-GDB session confirmed the CTA register-pool allocation loop.
Independently inspected cubins have REG96, per the performance agent, so this
is not an accidentally lower entry register cap. The original failed arm and
its combined.patch remain preserved unchanged.

Root then applied the separate cta-pool-corrected.patch: one uniform control
dec80 site, plus dec80 for both transform groups. The corrected targets
176/80/64/80/80 consume exactly61,440 registers, matching the launch allocation.
Corrected production warmup002 completed on all eight ranks and the parent
process exited0. Numerical tests are now running; corrected SASS/spill analysis
and timing remain pending. This successful warmup is not a numerical or
performance result.

Relevant combined source locations:

- `shim/w4a16/frontend.py:251–254`: maxrregcount96.
- `shim/w4a16/kernel.py:969,982,1026,1153`: control decreases80.
- `shim/w4a16/kernel.py:1072–1075`: both transform groups retain96.
- `shim/w4a16/kernel.py:1201`: epilogue increase176.
- `shim/w4a16/kernel.py:1227`: dispatch decrease64.

Two arithmetic-feasible budgets exist at the same launch cap: keep
epilogue176 and reduce both transform groups to80, or reduce epilogue to144
while keeping transforms96. Neither is source-only evidence of performance
or safe generated live-register usage; fresh codegen and correctness are
required. Keeping the prior epilogue bound and lowering the two groups is the
smallest isolated resource test.

## Separate inherited register-contract issue

PTX requires all four warps in a warpgroup to execute the same `setmaxnreg`
instruction under a warpgroup-uniform condition. The four separate control
branches currently contain distinct dec80 sites. This was inherited from the
working512-thread source, so it alone does not explain the new regression,
but it violates the documented condition. A future correction should use one
common control-warpgroup decrease site before entering individual control
roles, remove the four per-role decreases, and retain a uniform target per
whole group. Root incorporated that uniform control site in cta-pool-corrected.patch;
this source-only audit did not edit kernel/frontend files.

## Source eliminations

- Installed `PipelineTmaAsync.init_empty_barrier_arrive_signal` reduces the
  supplied transform thread index modulo32. Every one of the8 transform
  warps emits the expected empty-barrier arrival per multicast partner;
  there is no first128-thread or512-CTA-thread cutoff.
- Installed `PipelineAsyncUmma` routes producer arrivals from every transform
  thread in both CTAs to the leader's barrier. Its512 producer arrivals match
  the two256-thread transform groups per two-CTA cluster.
- The two transform groups reuse the retained local W4A16 same-K split.
  Both packed and scale views and TMEM destinations are divided by the same
  group index; local indices0–127 per group are appropriate. Both groups
  advance the same raw/transform ring phases. Raw5 does not alter the
  two-stage activation or transformed-weight rings.
- Installed `TmemAllocator.allocate` elects only allocator warp0; retrieval
  uses the caller-provided named barrier. The guard has exactly416 threads
  (epilogue128 + MMA32 + transforms256), matching the supplied count.
  No512-thread restriction exists in those helper bodies.
- The current persistent scheduler constructs its broadcast pipeline from
  the passed480 consumer threads. Consumer release is executed per thread;
  it does not cap the physical warp index at15.
- `token_comm` derives its tail count from dispatch128 + other512 =640.
  The dispatch-to-scheduler barrier correctly stays160; only dispatch8–11
  plus scheduler7 participate. Dispatch-local warp IDs and both return modes
  are unchanged.

These eliminations concern the inspected source paths. They do not substitute
for a passing numerical replay after the corrected budget.
