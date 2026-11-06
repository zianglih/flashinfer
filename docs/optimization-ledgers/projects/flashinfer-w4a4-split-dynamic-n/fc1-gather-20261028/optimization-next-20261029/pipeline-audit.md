# Gather pipeline synchronization audit, 2026-10-29

Source inspected: swap-AB retained7106faf3 (kernel SHA2560d44e4d71465b29a565995febdad42ef168060d1ae2858df5b2611ca998f70ee); W4A16 direct-TMA prototype/cleanup remains unstaged and separately source-bound in its campaign. This is a design audit, not another correctness claim.

| Resource | Owner/completion | Necessary dependency |
|---|---|---|
| FC1 routing | Sort; FC1 dependency wait before metadata reads | Removing prepare also removes its ancestor acquire/publication. Static descriptor, barrier and TMEM setup may run first; tile selection and routed input reads cannot. |
| FC2 routing/weights | FC1 startup release publishes acquired routing; FC2 scheduler and weight producer run ahead | Activation consumers wait for FC1 payload completion. Weight TMA must not be tied to that wait. Non-reader roles still honor the grid dependency before exit. |
| Swap weight+SF stage | One elected weight producer accounts transaction bytes; hardware completion | Reuse waits on MMA release. Weight SF can copy to TMEM before gathered activation/SFB is ready;7106 retains this independent ordering. |
| Swap gathered payload+SF | Four warp Gather4 issuers plus128 per-thread cp.async SF completions | Local barrier count129 includes one transaction-byte arrival and128 SF arrivals. A relay acquires local completion, fences async visibility and publishes to the MMA leader. Dropping it is not justified while the two memory mechanisms remain mixed. |
| W4 gathered BF16 | Four elected TMA producers; hardware completes directly to B pipeline | No scale-copy dependency, so no swap-style relay or local cp.async ring is needed. Each stage waits only for UMMA reuse; all four producers may run ahead to stage capacity. |
| W4 raw weights+SF | TMA-to-transform pipeline | Decoder waits for raw bytes and decoded destination availability. The decoded TMEM/SMEM stage releases independently after MMA consumption. |
| Accumulators/output | MMA-to-epilogue pipeline | Accumulator reuse follows epilogue reads; output-store reuse follows TMA completion. Existing overlapping accumulator ownership is unchanged by the gather experiment. |
| CLC metadata | Scheduler publishes, each participating role consumes once | Swap count is11 consumer warps in leader CTA and10 in nonleader CTA for gathered FC1. W4 gathered FC1 count is18 warps: excludes scheduler and the unused old activation-TMA warp. These counts follow role participation, not dtype/model shapes. |

## Instruction and register findings

- Increasing the swap control-WG quota80→112 removed captured local-memory traffic; the full468-cell campaign observed zero local bytes in all430 gathered-kernel instances. The whole-CTA launch quota remains168; no new tactic or model selector.
- Live-row payload issue reduced work but increased generated branches and hurt stable N3U prefill. Predicate PTX did not avoid those branches. Both variants were rejected; do not carry a dormant issue-predicate API into the shared Gather4 primitive.
- Lane-owned route decoding replaces full-vector/scalar-tail branching and redundant warp-uniform divisions. Seven exact cases and the44-cell screen passed; final full composition is being measured.
- W4 gather is the last/fifth WG. A32-register gather quota compiles safely after register reallocation, but redistributing the saved registers to either dequant or epilogue regressed performance. Keep the established144/80/96/96/64 policy. Check executable control flow and implicit vector-register widths rather than a linear highest-register scan.
- W4 multicast partitions K chunks between contributing CTAs and retains the full destination byte expectation. Every CTA loading the entire tile and then multicasting would over-complete the transaction barrier.

## Remaining evidence-driven work

The existing N3U EP16K trace points to delivery/mainloop waiting, not startup (roughly5ns measured startup wait in that instrumented capture). NCU hangs on independent trivial allocation, so there is no hardware-counter evidence. Source-bound CUPTI and executable resource inspection decide retention.

The full existing-tactic retune exposed8-byte local storage for selected N3U EP MXFP8/MXFP4x8 FC1 tactics: N256, two CTA, K256. Those tactics were outside the earlier fixed-winner430-instance zero-local set. Inspect SASS and compare the general112/120 control allocation on this source; do not extend the earlier zero-local claim to the entire tactic set.

W4 single-arrival B accounting was rejected after33 exact cases and32 timing points: EP prefill−0.69%, TP prefill−0.50%, decode neutral. Four arrivals remain independent. Their expected byte counts can still share the same compile-time total/4 accounting because pending transaction bytes belong to the barrier phase, not to an individual issuing warp.
