# Retained one-CTA register and role audit

CPU/read-only audit, 2026-10-25, production HEAD `aab93f854054de834447bdd8985b8bbd653fb3c8`. The core and epilogue have no working-tree diff from HEAD. No CUDA imports, compilation, GPU execution, or source edits. This audit does not propose increasing occupancy or reopening the closed register-budget experiment.

## Source identity

All production paths below are under this project's `flashinfer/` checkout.

|Source|SHA256|
|---|---|
|`flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py` (**core**)|`7c0fe69faab5acecafdd3d67a157f016836e149fafdc29942542d44ef4852c66`|
|`flashinfer/fused_moe/cute_dsl/blackwell/utils.py` (**epi**)|`9811c53e0faa4ab39bc8dd3b03152498958938ff17761fdad57a0afae6ede889`|
|`flashinfer/fused_moe/cute_dsl/blockscaled_contiguous_grouped_gemm_finalize_fusion.py` (**host**)|`2a8a4a3ad8e927cc8bccc8adf3fc3668e9b7b581eb4eb9d35d1416e21abc2ce0`|
|`scripts/register_budget_experiment/README.md`|`a923c05f923c584a3f97f5a91154ff6e2408540e7740c72188a5338547191f8e`|
|Archived narrow-epilogue control PTX `scripts/narrow_ld256_epilogue_experiment/raw/results/resources-r1/control-fc1-n16.ptx`|`4d38f7509eccf83d415cdf0358ae333fad2feaeb22e02fba47ee9a6894bea7ff`|
|Its `resources.json`|`a1404ad21416bb1a3036527bd7276b6f9552775da39a3bb07c65955250cf5e54`|

CUTLASS source below was read from `/Users/ziangli/playground/projects/flashinfer-w4a16/flashinfer/3rdparty/cutlass`, HEAD `b46b16d003484063bca4ed365e44095c4c6ed633`. This is a verified retained source identity, not a claim about the installed package used for a future candidate.

|CUTLASS source|SHA256|
|---|---|
|`python/CuTeDSL/cutlass/utils/tmem_allocator.py`|`a46c8379fd75dfa552483d97da9e2945bb0e3a3b7e26cdf8eff94fb699eb938b`|
|`python/CuTeDSL/cutlass/cute/arch/nvvm_wrappers.py`|`0087bbfc36f2e6123645d5db8facb209a58028ca0c3b6ee0004b0db798099581`|
|`include/cutlass/gemm/kernel/sm100_gemm_tma_warpspecialized_input_transform.hpp`|`5a88b2d2e1ce122db319508ea055162a95f28b4a31ce0f01fc86ba7b8c1fba61`|

## Roles and launch constraints

Native gated NVFP4 N16 uses `overlap_epilogue=True`: core `:349–355` launches 288 threads. The roles are:

|Physical warps|Threads|Responsibilities and source anchors|
|---|---:|---|
|0–3 / WG0|128|Producer loop `:1003–1238`. All 128 issue/commit SF cp.async when `!tma_sfb`; only warp0 acquires/launches A/SFA/B TMA `:1067–1127`. Calling this four TMA warps is inaccurate.|
|4–7 / WG1|128|Dedicated epilogue `:1239–1326`; logical `tidx-128` passed at `:1280,1316`; consumes accumulator, loads/transposes/quantizes/stores, then releases it.|
|8 / partial WG2|32|MMA branch `:1327–1523`; waits SF/TMA, publishes scales to TMEM, issues MMA, releases operands, commits accumulators.|

The five-warp, 160-thread non-overlap path instead runs the epilogue on warps0–3 after producing each tile (`:1191–1233`). It is a different lifetime regime; do not reuse a producer-donation policy there without separate analysis.

The launch is `block=threads_per_cta`, `min_blocks_per_mp=1`, and exact shared-storage size (core `:838–850`). Host `:201,257` supplies `num_sms`, and the grid rounds it down to a complete CTA group (`core:839–844`). `min_blocks_per_mp=1` is a compiler resource constraint, not an instruction to assign every SM register to this CTA. No explicit max-register option is passed by `cute.compile` (`host:259`) or the launch. There is **no setmaxnreg call or dynamic register-budget initialization in the retained core/epilogue**; this is not a missing setup step.

For N16, allocated N remains32 (`core:313–316`), four operand stages (`:343–344`), and two accumulator stages (`:360–361`). Archived 98fd narrow-epilogue control reports 288 threads, 197504 dynamic shared bytes, 128 TMEM columns, 64 registers/thread, zero local bytes, and one active CTA/SM. PTX has `.reqntid 288` and `.minnctapersm 1`, with no `.maxnreg`/setmaxnreg. Its epilogue bytes match current production, but its core SHA is `2ca679d3a87e412218e4d75e9e98f892dd3b2ccd1b3d777621d16ae8d03fa58e`, not current core's hash. These are archived resources, not fresh aab93f854 measurements.

## Synchronization and TMEM ownership that a register-only change must preserve

- Operand TMA full completion uses one producer arrival and the aggregate byte count (`core:908–922`). The SF cp.async producer group has 128 participants (`:924–932`); changing their register caps does not reduce arrival requirements. N16/one-CTA does not instantiate the two-CTA relay (`:936–944`).
- Accumulator completion has 128 consumer participants per CTA (`:945–953`). The epilogue's final TMEM read fence precedes its release (`:1321–1323`; overlapping helper's early-release point is `epi:576–580`). Removing scratch does not authorize releasing before the native up/gate loads complete.
- All threads construct the allocator with **physical warp0** as issuer, and execute allocate/wait/retrieve (`core:954–970`). Retrieval barrier3 has `threads_per_cta` participants. CUTLASS `tmem_allocator.py:203–214` guards the actual hardware allocation to allocator warp0; it is not a 128-thread hardware allocation instruction.
- Final barrier1 joins all 288 threads (`core:1524–1526`). Warps0–3 then relinquish, join barrier2 with128 participants, and free (`:1527–1530`). CUTLASS `:254–261,270–287` again guards the hardware operations to allocator warp0. The surrounding 128-thread barrier remains mandatory in this source, even though only warp0 issues the hardware operation.
- Epi barrier6 has128 participants (`epi:381`), used by SF32 and other epilogue branches. Keep physical epilogue warps4–7 aligned as WG1; logical renumbering does not by itself move fixed TMEM datapaths to arbitrary warps1–4.
- SF SMEM and its TMEM destination have different lifetimes. MMA copies both SF tensors then issues MMA (`core:1442–1470`); operand releases follow the final channel-tile MMA (`:1504–1512`). Producer empty-stage waits and tails (`:1234–1238`) must remain unchanged in a register-only policy.

## Dynamic registers: useful constraints, no current bottleneck claim

The saved register-budget audit cites the [PTX setmaxnreg contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#miscellaneous-instructions-setmaxnreg): uniform instructions across a complete four-warp group, valid absolute counts divisible by8 in24..256, and synchronization between reconfigurations. The retained CuTe wrappers `nvvm_wrappers.py:849–867` simply lower increase/decrease to NVVM; they do not enforce those rules. A structurally compatible placement would therefore apply one uniform policy to WG0 and one to WG1, leaving lone MMA warp8 unreconfigured. Distinct warp0 versus warps1–3 caps are not a valid shortcut under that documented contract. This is a constraint, not a recommendation to add the policy.

CUTLASS's input-transform kernel `:392–406` computes an initial reference budget as `floor8(512/ceil(threads/128))`, and skips reconfiguration when the requested budget equals that reference. For nine warps the reference is168; **this must not be substituted for the emitted resource count of a different kernel**. The prior register experiment emitted168 initial registers/thread after reconfiguration was introduced, while its unreconfigured native controls used80–118.

Use the emitted CTA allocation, not the SM's64K capacity. For the earlier 288-thread/168-register build, nominal CTA pool was48384 registers. Producer96 + epilogue256 + unchanged MMA168 requested50432 and hung; producer96/epilogue224 requested46336 and was exact but slower/neutral. `scripts/register_budget_experiment/launch_guard.py:25–40` checks emitted resources and the condition `128*(Rproducer+Repi)+32*Rinitial <= 288*Rinitial` before launch, plus increase/decrease direction. An increased cap can block waiting for registers; one resident CTA does not make its pool unlimited. Hardware allocation granularity and compiler policy still require inspecting emitted artifacts.

TRT is precedent for explicit budgets, not proof they help here: published N16 source `:2948` increases the full epilogue WG to160, while control tasks decrease to48/72; `:3854` declares `__launch_bounds__(512,1)`. The archived T32 SASS has `USETMAXREG.DEALLOC.CTAPOOL 0x30/0x48` and `USETMAXREG.TRY_ALLOC.CTAPOOL ... 0xa0` at0x42f0. That source and binary have different provenance, as documented in `TRT_MAPPING.md`; neither specifies a valid budget for our nine-warp CTA.

The previous budget-only axis is closed: 270 paired exact cases plus native phase checks showed no material gain, and inspected native controls had zero local storage/LDL/STL. A new ownership epilogue can change liveness, but the efficient first candidate should retain current roles, launch, barriers, and compiler allocation. Inspect its resource/SASS output for spills or a concrete register-pressure change before spending the one-candidate compile budget on redistribution. There is no evidence here for an occupancy increase or for a missing register setup bug.
