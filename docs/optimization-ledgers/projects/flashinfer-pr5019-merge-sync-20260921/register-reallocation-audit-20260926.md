# Register redistribution timing audit — 2026-09-26

Read-only audit of FlashInfer PR5019 source b1eab683651680e1434321b3e0adf499be79447a. No kernel edits, GPU runs, or PR edits in this audit.

## Current behavior

- frontend.py352–354 requests initial96 registers/thread,640threads/CTA.
- megamoe_kernel.py1208–1211 preclaims first atomic scheduler work during prologue; first work publication remains gated on dispatch metadata.
- At1234 pipeline initialization wait completes;1235 allocatesTMEM;1236–1237 only warps0–4 and12–19 wait on its rendezvous.
- WG1 dec80 at1241 precedes its scheduler metadata wait and compute work; WG0 inc144 at1451 precedes epilogue setup/first scheduler wait; WG2 dec64 at1473 precedes local input staging/dispatch. WG3/4 stay96.
- Role branches are concurrent across warps. Source order does not serialize whole role loops. WG1 warp4 reaches donation only after TMEM rendezvous; other WG1 warps do not join that rendezvous. No extra CTA register barrier is added.
- Donors provide128*(16+32)=6144 registers, matching WG0 request128*48. PerCTA allocation pool is61440 32-bit registers. No further adjustment at tail.

## Existing overlap and limits

- Register acquisition can overlap independent dispatch/compute execution; no direct IKET scopes measure adjustment latency, so current traces do not prove it fully hidden.
- Transform groups prepare combine before final TMEM producer-tail wait (1603–1620). WG0/1 prepare while dispatch drains peer returns (1642–1658). Dispatch cleanup can overlap combine after the return barrier.
- Earlier donation before TMEM rendezvous is a possible experiment; lower prologue budget could introduce spills. Do not independently hoist WG0 increase across that rendezvous: its donors can still depend on WG0 reaching it.
- Merely delaying WG0 increase cannot lend more registers to donors whose limits remain80/64. A useful dynamic schedule requires coordinated budgets and validated synchronization/liveness.
- NVIDIA PTX setmaxnreg: CTA-private pool; inc blocks until registers available; each WG warp executes same adjustment, explicit WG synchronization before subsequent adjustments. https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#miscellaneous-instructions-setmaxnreg

## Prior experiment boundary

HashInfer ledger /Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/alignment256-20260926/FINAL_DECISION.md28–43 rejects LDG128 tail96 and late+96. These preserve original compute-phase budgets and change retired-tail allocation only; no whole-kernel96 or startup-placement benefit established. Original128 tail96 speedups atEP4 uniformT128/4096/8192/16384:0.9862/0.9960/0.9896/0.9901x. Do not attribute rejected dispatch-count/payload-overlap experiments to current code.
