# Conditional tail register redistribution — read-only assessment

2026-09-19. Source: selected `3de81245c1f484177b8ca50b47fd0464068d230e`; no kernel edits, GPU work, or queued experiment. This is a feasible handoff, but the available generated reduction code does not establish register pressure that justifies it.

## Legal handoff and source boundary

Under the existing compile-time deterministic-combine condition (`not self.in_kernel_fc2_reduce and reduced_output is not None`), the narrow site is immediately after the first common tail barrier and before `kernel_tail_drain`: all four epilogue warps would decrease 144→128; all four control warps would increase 80→96. Dispatch remains 64 and both dequant groups remain 96. Initial and final allocations are both `128*(144+80+64+96+96) = 128*(128+96+64+96+96) = 61440`; epilogue releases exactly the 2048 registers requested by control. The existing `-maxrregcount=96` allocation remains unchanged, as do 640 threads and one CTA/SM. This does not exploit unallocated physical registers.

Exact selected-source references, relative to `selected-counter-lifetime/hashinfer/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/`:

- `frontend.py:304–307`: 61440-register initial CTA pool and ptxas maximum 96.
- `megamoe_kernel.py:1174–1176,1331–1351`: control decrease80 and epilogue increase144; epilogue run, system fence, TMEM permit relinquish/free all precede the common tail.
- `megamoe_kernel.py:1232,1279,1329,1485`: producer tails finish before the first rendezvous; dequant prepares its first scores before its transform producer tail and retains that state across the handoff.
- `megamoe_kernel.py:1487–1516`: first 640-thread rendezvous, dispatch drain, epilogue/control score preparation, second common rendezvous.
- `megamoe_kernel.py:1517–1545`: common reducer executes only on epilogue/control/dequant; dispatch performs cleanup separately.
- `token_comm.py:113–151`: drain body is dispatch-only and does not depend on the proposed epilogue/control adjustments. Existing NCU padding/drain call counts are unchanged by this proposed site.

The first existing barrier synchronizes each affected warpgroup after its earlier register adjustment. Conditions `warp < 4` and `4 <= warp < 8` select whole four-warp groups, so every member executes its group's same new instruction. Both counts are valid multiples of eight; decrease128 is below144 and increase96 above80. A control group that arrives first may block on allocation, but epilogue reaches a nonblocking donation with no remaining control-dependent work. Dispatch and dequant do not wait for the allocation before progressing to their existing second barrier. There is no new dependency cycle, no need for another barrier, and no requirement to make the two groups execute their different instructions simultaneously. The existing second barrier synchronizes all roles before reduction. In-kernel-FC2 reduction and no-reduced-output paths would remain unchanged by the compile-time guard.

These conclusions follow the [CUDA 13.2 / PTX 9.2 setmaxnreg contract](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#miscellaneous-instructions-setmaxnreg): allocation is per CTA, increase may block, adjustments apply to whole warpgroups, and a group must explicitly synchronize between adjustments. Newly obtained registers have undefined contents; compiler-generated code must initialize them. The proposed site changes no output visibility or existing copy-wait requirement.

## Compiler opportunity is unproven

The reduction workers' runtime minimum allocation would rise from80 to96 (epilogue128/control96/dequant96). That permits, but does not guarantee, a different register allocation/schedule in the common reduction region. Dispatch64 still reaches common control-flow joins and barriers; whether ptxas can make use of the higher bound in the reducer branch must be checked in emitted code. Kernel-level `REG:96` is initial allocation metadata, not proof that the tail needs96 or that80 limits it. Nor do virtual PTX register counts measure simultaneous live state.

Available actual C1 selected T16384/tactic1 evidence is in `input-stage-pair-tail/codegen-selected/collected-codegen-candidate/evidence/candidate/h7168-t16384-k1/rank0/00-Sm100W4A16MegaMoEKernel-fused_int32_vector.{ptx,sass.txt,resources.txt}`. Its reducer is source-identical to selected3de, but the whole kernel includes C1 staging and is not a matched3de allocation proof:

- PTX lines6613/6745 and SASS addresses0x152f0/0x15b70 are the two common 640-thread barriers.
- PTX around6744–6757 separates dispatch cleanup from the common reducer. SASS 0x15bc0–0x16720 is its active-worker loop, with score preparation immediately before the second barrier.
- Observed scalar physical operands in score preparation, reducer, and continuation fit in R0–R51, including vector register groups. This is an operand-range observation, not a compiler liveness report. It gives no evidence that the current80 budget is tight.
- All32 captured C1 ABI resources report `STACK:0 LOCAL:0`, and the selected SASS has no LDL/STL. The compiler already issues seven route loads before the first packed FP32 multiply; lack of source-level prefetch is not the problem.

Extra register handoff instructions can add critical-path overhead, a blocked control allocation, or register moves/rematerialization around the epilogue decrease. They do not change occupancy, worker count, memory traffic, ordered FP32 recurrence, or inherently supply additional independent work. Reduced BF16 conversion instruction count in G1 could also reduce pressure; negative timing alone would not show that lack of registers caused it.

## Recommendation

Keep this as a conditional opportunity, not a queued optimization. First inspect the pending matched actual-tactic3de/G1 codegen for spills, a pressure-limited schedule, repeated rematerialization attributable to liveness, or a region approaching its actual register ceiling. If a later bounded source experiment is warranted, require same-tactic/same-capacity emitted-code evidence that the new handoff lets the reducer keep useful state or issue independent work earlier, with no new spill or synchronization path. A repeated-parameter load by itself is not causal proof. Then assess full13 timing against a fresh control, especially decode4–512 where handoff overhead may dominate, while guarding4096/8192/16384. No such gain or pressure diagnosis is established by this assessment.
