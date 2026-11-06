# Two transform groups: failed warmup and register-pool diagnosis

The first raw5/two-transform-group candidate emitted all eight cubins but its warmup did not return. It has no successful numerical or timing result. The original capture remains `profiles/tmem-raw5-transform2-codegen-001`; the independently copied artifacts are `profiles/tmem-raw5-transform2-emitted-001`, with an explicit failure status. Root stopped the exact hung process tree after debugger inspection.

All eight emitted cubins report REG96/STACK112/LOCAL0, `.reqntid 640,1,1`, a 96-byte PTX local depot and the existing 21 static SASS local operations. No transform local operations appeared. The expected epilogue target 176, control80 and dispatch64 were emitted; both transform groups retained launch96. Successful compilation did not establish a valid runtime register budget.

The CTA launches with `640 × 96 = 61,440` registers. The desired five 128-thread warpgroup targets require `128 × (176+80+64+96+96) = 65,536`, exceeding that allocation by 4,096. The unallocated SM registers are not added to this CTA's pool: `setmaxnreg` redistributes the CTA's initial allocation. [NVIDIA Nsight explanation](https://forums.developer.nvidia.com/t/sm90-setmaxnreg-will-change-occupancy-dynamically/302068)

Control and dispatch release 6,144 registers; increasing the epilogue from 96 to 176 requires 10,240. Live debugger output in `logs/tmem-raw5-transform2-gdb-002.log:52` places the epilogue at `USETMAXREG.TRY_ALLOC.CTAPOOL UP0,0xb0`, function offset 36,768 (`0x8fa0`), confirming the allocation wait predicted by the budget.

A separate source-contract issue was also found: the four control warps executed separate decrease80 sites under individual `warp==4/5/6/7` conditions. The PTX contract requires warpgroup-uniform execution of the same `setmaxnreg` instruction. [PTX ISA §9.7.19.5](https://docs.nvidia.com/cuda/pdf/ptx_isa_9.1.pdf)

The corrected candidate uses one uniform control-group decrease80 and explicitly decreases both complete transform groups to80, yielding `128 × (176+80+64+80+80) = 61,440`. This balances the CTA allocation; fresh codegen, liveness and numerical validation remain required before performance measurement. The one-group retained implementation also needs the uniform control-site correction.

The source-correlated helper found transform-attributed GPRs only through R58 in the failed candidate, but shared/unresolved helper code reaches R95. These static references are not a register-liveness proof. The corrected capture must therefore be inspected for new LDL/STL or other local-storage changes after lowering the transform targets.

Detailed source snapshots, per-rank instruction sites and resource evidence are in `profiles/codegen-comparison/raw5-vs-transform2-emitted.json` and `.md`. The original candidate kernel SHA256 is `419b7097ab411b464c8a884b1cb678f4bed07a5f2450f6bc907ba322c95aa245`; its frontend is `f31fdfbaa510276f4278fe290c683f66a021bd2378e481d0003b3455d883524c`.
