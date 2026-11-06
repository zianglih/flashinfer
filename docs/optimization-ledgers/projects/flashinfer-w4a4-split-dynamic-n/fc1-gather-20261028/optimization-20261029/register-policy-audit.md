# Three-warpgroup register policy audit

Read-only source audit, 2026-10-29. This does not establish a current spill or
performance result and does not modify the review kernel.

The R6 gather kernel launches 384 threads: control WG0 (weight, SF relay, MMA,
scheduler), epilogue WG1, gather/SF WG2. It currently emits no explicit
`setmaxregister` operation. FC2 remains 256 threads and is outside this experiment.

## First decision: inspect actual resources

With a 65,536-register SM, a single 384-thread CTA has a nominal uniform ceiling
near 170 registers/thread, normally rounded down by allocation constraints. The
older register experiment emitted an initial168-register allocation. This is
not proof that the present compiler does the same, nor proof of spilling.

Collect the current FC1 cubin register count, local-memory/stack usage, and SASS
LDL/STL sites before changing policy. Attribute spills to startup, producer or
epilogue regions where possible. The old7829 controls used only80–118 registers
and no spills; reallocation then was neutral/slower. New code and384 threads make
reinspection justified, but do not reverse that historical finding by assumption.

## Uniform policy and budget

Let C, E, G be per-thread targets for control, epilogue, gather, and R0 the
actual emitted initial per-thread allocation. A conservative launch guard is:

```
required = 128 * (C + E + G)
available = 384 * R0
required <= available
C <= R0; G <= R0; E >= R0
```

All targets must be in24..256 and divisible by8. Do not substitute the SM's64K
capacity for the CTA's actual launch pool. The previous288-thread96/256 trial
hung because it requested50,432 registers from a48,384-register CTA pool even
though it fit within the physical SM register file.

First conservative resource candidate: **C80 / E256 / G128**. It needs59,392
registers, leaving5,120 if the actual initial allocation is168 (64,512 total).
It therefore requires an initial allocation of at least160 when rounded to8,
as well as correct increase/decrease directions. If the evidence only warrants
E224, C80/E224/G128 needs55,296. These are diagnostic policies, not extra
autotune axes or recommendations to launch before inspecting generated resources.

Do not start by forcing control and gather to32/40/48. The gather source retains
`4 * ceil(b_copy_rows /16)` route indices per thread across K, reaching64 indices
at one-CTA N256, plus64-bit SF offsets, stage state and address arithmetic.
Lower targets may create the producer spills/latency being investigated. A
low control target must accommodate the busiest of all four control roles, not
just the weight issuer. C80 follows the existing W4A16 control-WG precedent;
G128 deliberately preserves more room for the gather's routed-address state.

## Placement and synchronization

Use one warpgroup-uniform branch before role dispatch, under the FC1 gather
compile-time condition only:

```
if warp < 4: decrease(C)
elif warp < 8: increase(E)
else: decrease(G)
```

All four control warps execute the same target, including the follower CTA's
otherwise inactive MMA role. Do not place divergent targets in individual
weight/MMA/scheduler branches.

A simple placement is after existing common TMEM allocation/retrieval and before
the PDL wait/role dispatch (current kernel around2776–2784). This keeps existing
startup participation intact. An earlier placement may reduce startup spills but
also constrains common initialization; distinguish it from the first experiment.

The epilogue increase may wait for other WGs to donate. Donor WGs must reach their
decrease without waiting on the epilogue. No new CTA barrier is needed merely to
order donations: the register-pool operation blocks until satisfied. Existing
TMEM retrieval and final CTA joins retain384 participants. There must be no
later setmaxnreg without the explicit WG synchronization required by PTX.
With a single lifetime reconfiguration, there is no reason to restore budgets
at teardown. Preserve all existing payload/SF barriers and PDL behavior.

## Source precedents

- Current W4A16: `moe_w4a16_kernel.py:343–346` uses uniform control80,
  epilogue176, and two transform WGs at128; its512-thread policy balances64K.
  Reconfiguration follows TMEM allocation (`:1451–1460`, epilogue `:2012`).
- Hopper finalize: `hopper/contiguous_grouped_gemm_finalize_fusion.py:182–183`
  uses40/232, applied to complete DMA/consumer WGs (`:549–551`, `:664`).
  The Hopper role workload and CTA pool differ; the values are not a template
  for routed gather/SF state.
- Rubin gather: `rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:364–369`
  uses epilogue168, gather80, SFA gather80, SFA transform48, control128, with
  full-WG branches at1835/2093/2214/2902. Preserve its structural lesson but do
  not transfer Rubin register-file capacity assumptions to B300.
- `scripts/register_budget_experiment/README.md:14–24` and `launch_guard.py`
  preserve the actual-pool deadlock and guard. `README.md:48` records the old
  spill-free controls and failed performance rationale.
- [PTX setmaxnreg specification](https://docs.nvidia.com/cuda/parallel-thread-execution/#miscellaneous-instructions-setmaxnreg)
  checked2026-10-29: WG-uniform same instruction, CTA-local pool, blocking
  increases, target range/granularity, valid initial allocation and direction
  constraints, explicit synchronization before subsequent reconfiguration.

No source edits, GPU launches, benchmarks or sanitizer runs were performed by
this audit.

## R9 codegen result supersedes the initial placement recommendation

The guarded R9 capture subsequently verified an initial168-register allocation
and the intended decrease80/increase256/decrease128 instructions, but the three
branches reconverged before actual role dispatch. Its N3U TP8 T16384 MX kernels
worsened from208 to488 bytes of stack. SASS mapped all role bodies to approximately
R77: gather changed from zero to12/12 LDL/STL instructions; epilogue changed
from26/46 to102/100. This is consistent with the compiler propagating the minimum
budget across reconvergence. The source audit's pre-dispatch placement above was
therefore unsuccessful and must not be copied as a recommended implementation.

The next candidate should put the same WG-uniform targets inside the actual
non-reconverging role regions, including every warp of WG0, while preserving
the CTA launch-pool guard. This is a compiler/codegen hypothesis pending capture,
not a retained performance result. Detailed evidence is owned by the codegen
agent in `codegen/register-guard/spill-roles.json`.
