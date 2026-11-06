# Element/scale producer ownership: feasibility audit

Read-only audit of the kernel source retained at `4376662a9ddefb1f62f0f81f4453964dc1f5a307`. No source changes, compilation, GPU runs or benchmark claims. The current publication/test cleanup must finish before this experiment starts. Scope is both swap-AB and W4A16, FC1 and FC2; preserve FC1's four-warp input gather group and all existing PDL publication/runahead behavior.

## Conclusion

The ownership split is feasible, but a mechanical regrouping of copies is insufficient. W4A16 FC1 is the simple first leg: its idle control warp7 can issue weight scales while warp6 issues weight elements. Swap-AB FC1 has a real existing job in its second control warp: relaying gather/SFB completion to the MMA leader. Moving weight scales into that warp must preserve independent SFA prefetch ahead of that relay. FC2 is harder for both kernels: an elements warp responsible for both static weights and dependent activations must not execute the PDL wait before filling available weight stages, nor block on activation-stage reuse before allowing independent weight work.

Keep the existing storage/pipeline separation and one full-barrier announcer for the initial experiment. Change work ownership, not the consumers' lifetime contracts. No new autotune axis, public argument, dtype/shape whitelist, or fixed problem-specific prefetch count is needed. A bounded two-cursor producer design is required for the legs that also process dependent activation or relay work; benchmark its control/register cost before retention.

## Current roles and actual synchronization

| Kernel/leg | Elements and scales today | Completion/reuse contract |
|---|---|---|
| W4A16 FC1 | Warp6 loads packed weights A and SFA. Warp7 is idle. Warps16–19 Gather4 BF16 activations B. Warps8–15 dequantize. | A+SFA share `a_load2trans_pipeline`; transform warps release it after their reads. Gather B uses independent `b_load2mma_pipeline`. MMA releases B after use. |
| W4A16 FC2 | Warp6 loads A+SFA and runs ahead of input readiness. Warp7 waits for FC1 then loads BF16 B. No activation scale exists. | Same independent raw-weight, transform-to-MMA, and B rings. Raw weights can become reusable before B/MMA stages. |
| Swap-AB FC1 | Warp0 loads weights A+SFA. Warps8–11 gather B by TMA Gather4 and SFB by cp.async. Warp1 relays local gathered B/SFB completion to the MMA leader. | A+SFA use `operand_pipe`. B+SFB have local/cluster gather completion barriers, but reuse is tied to the same `operand_pipe` empty phase. MMA can issue SFA-to-TMEM copies before waiting for gather completion. |
| Swap-AB FC2 | Warp0 loads A+SFA ahead of FC1. Warp1 waits for FC1, then issues regular-TMA B+SFB. | A+B+SFA+SFB share one full/empty operand stage. Warp0 announces all transaction bytes; warp1 only waits for stage reuse. MMA releases after both logical channel tiles finish. |

Sources: [W4A16 roles/register allocation](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:352), [raw/transform/B pipelines](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:1190), [current producer loops](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:1715), [four-warp BF16 gather](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:2738), [swap roles](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:1593), [swap pipeline creation](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:2653), [producer and relay loops](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:2839), [MMA wait/release order](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:3181), [gather payload and SF copies](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:3403).

## Proposed ownership

| Kernel/leg | Elements control warp | Scales control warp | Existing gather group |
|---|---|---|---|
| W4A16 FC1 | Warp6: weight A | Warp7: weight SFA | Warps16–19: BF16 B, unchanged |
| W4A16 FC2 | Warp6: weight A and activation B, with independent producer cursors | Warp7: weight SFA, no payload-dependent work | Absent, unchanged |
| Swap-AB FC1 | Warp0: weight A | Warp1: weight SFA and existing gather-completion relay, using independent cursors | Warps8–11: B Gather4 and SFB cp.async, unchanged |
| Swap-AB FC2 | Warp0: weight A and regular-TMA B | Warp1: weight SFA and regular-TMA SFB | Absent, unchanged |

This does not move FC1's scattered activation SF to the control warp or replace its cp.async load with a less efficient mechanism. The proposed split is between the two existing TMA control warps; distributed input gathering remains a separate ownership domain. No S2T publication is moved into a producer as part of this experiment: current TMEM SF lifetime is controlled by the MMA warp and accumulator overlap, and changing that is a distinct synchronization change.

## Exact full-barrier accounting

Retain one announcer: the elements warp performs the existing `producer_acquire`, including the existing total expected-byte count. The scales warp waits on the corresponding empty stage and issues its copies against the same full barrier without another producer arrival. This is already the swap-AB FC2 pattern for its second producer. Both producers must advance their phase/index once per logical K stage, including padded and partial-K stages.

| Ring | Full arrivals | Expected TMA bytes per stage | Release owner |
|---|---:|---|---|
| W4A16 raw A+SFA | Existing1 | Existing `a_copy_size + a_scale_copy_size`, per current multicast/CTA contract | Existing transform consumers |
| W4A16 BF16 B | FC1 existing4; FC2 existing1 | Existing `b_copy_size * size(tiled_mma.thr_id.shape)`; FC1 each Gather4 issuer contributes one quarter via `expected_tx` | Existing MMA release |
| Swap FC1 operand | Existing1 in leader CTA | `G * C * (128*K*weight_bits/8 + SF_A)` | Existing leader MMA release |
| Swap FC2 operand | Existing1 in leader CTA | `G * (C*(128*K*weight_bits/8 + SF_A) + B_rows*K*activation_bits/8 + SF_B)` | Existing leader MMA release |

Here `G` is the existing CTA group size, `C` the logical channel-tile count, and all byte/row/K values come from the existing compile-time layouts. Preserve existing multicast masks, group-two TMA completion destinations and CTA-local/global SF duplication. In particular, group-two SFB remains full N in each CTA even though each CTA owns only half of B elements.

Proof obligation: a stage's full phase cannot complete until its single announcer arrives and the entire announced sum has completed. Every producer first observes the same empty phase, so neither overwrites a live stage. Moving SFA/B/SFB issue to another warp changes neither the sum nor the release condition. Do not change the producer count to2 while keeping one announcing acquire, and do not let both warps call the old total-byte acquire: either produces incorrect accounting. Byte completion before the single announcing acquire is already possible in current swap FC2; retain that established one-announcer pattern rather than adding a per-stage warp rendezvous.

`PipelineTmaUmma.producer_acquire` elects the leader-CTA arrival and supports `expected_tx`; `producer_commit` is a no-op. The local CUTLASS `PipelineTmaAsync.producer_acquire` used by W4A16 does **not** accept `expected_tx`. A two-arrival/role-specific-byte design would therefore require a separate API adaptation for W4A16; it is unnecessary for this ownership experiment. Sources: [byte totals](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:1032), [swap total announcement](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:2542), [CUTLASS TMA→UMMA acquire](../references/cutlass/python/CuTeDSL/cutlass/pipeline/sm100.py:343), [CUTLASS TMA→thread acquire](../references/cutlass/python/CuTeDSL/cutlass/pipeline/sm90.py:695).

The FC1 swap gather barriers are unchanged: local arrival count is `1 + min(route_tile,128)` (one Gather4-byte announcement plus participating SF-copy threads), and the cluster-visible relay receives one arrival per CTA (`G`). Keep the local-completion wait, async-shared fence, and peer arrival. SFA prefetch must be scheduled independently before any blocking relay wait. Do not make the weight full barrier depend on the relay: MMA's current SFA S2T overlap before the gather wait would disappear.

## CLC and ordinary scheduling

- W4A16 already uses the tile-info pipeline under both CLC and its ordinary scheduler. Activating warp7 in FC1 adds32 consumers: change `threads_per_cta - 32 - (32 if gather_input else 0)` to `threads_per_cta - 32`. FC2 already includes warp7 and needs no additional count. Every new active warp must consume/release the terminal sentinel as well as all real tiles.
- Swap-AB warp1 already consumes tile metadata for its relay in FC1 and TMA in FC2. Its current CLC consumer count does not change merely because SFA moves onto it. Ordinary scheduling derives the same tile sequence independently.
- Never give the new scale role its own CLC allocation/request stream. Both roles must observe exactly the scheduler's existing tile sequence. A role may advance its private producer cursor, but cannot replay an overwritten tile-info slot.
- A bounded prefetch queue that spans expert/work-tile boundaries must retain the exact existing CLC assignment. Derive its capacity from the current stage counts and compile-time K-tile count, not model IDs or dimensions. Preserve current metadata backpressure; do not count an extra logical consumer without also issuing the matching releases.

## PDL preservation and necessary producer state machines

The wrapper selects weight prefetch automatically for swap FC2 (`enable_pdl and not gather_input`), not FC1. Swap FC1 must first acquire routing from sort. W4A16 FC1 also waits for sort before any role reads routing; FC2's weight/scheduler/transform work can currently run ahead while its activation warp waits.

Sources: [swap wrapper configuration](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab.py:248), [swap startup wait/publication](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:2736), [swap producer-exit publication](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:2903), [W4 FC1 wait](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:1498), [W4 FC2 dependency/signal](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:1730), [W4 FC1 startup publication](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:1833).

Required general design:

1. Maintain a weight-producer cursor independent of the dependent activation/relay cursor. Fill every currently usable weight/SFA stage before the first payload dependency wait. The existing depth is the bound; use `producer_try_acquire` to stop at real backpressure rather than blocking before dependent work can run.
2. Retain only bounded metadata needed to resume the activation/relay cursor. Do not assume `k_tiles >= num_stages`: small TP GEMMs can cross work-tile boundaries within the prefetch window. Conversely, do not synchronously fetch more CLC metadata than its ring can publish while activation consumers are paused. A fixed `for num_stages: next_work(); acquire()` prologue can deadlock.
3. After payload readiness, drain dependent work while opportunistically refilling available weight slots. Do not alternate `issue B(stage i); block waiting for A(stage i+depth)`; that can stall all remaining ready B work. Try the independent ring first and only block when the blocked dependency can actually progress without the same warp issuing another missing operand.
4. W4A16 specifically retains independent raw-weight and activation rings. Raw slots become free after dequantization, while B slots become free after MMA. Collapsing their acquire/release or stage cursors would serialize useful dequantization runahead and can form a cycle: a raw producer waits for transform/MMA, MMA waits for B, but the same producer has not issued B.
5. Swap FC1's scales warp must not wait for gather stage0 immediately after SFA stage0 if SFA stage1+ can run ahead. Use the same bounded independent-cursor idea. Preserve current weight-SFA completion → SFA S2T → gathered-B completion order.
6. Keep startup/producer-exit publication at the original semantic boundary. Swap FC1's old activation warp1 publishes ancestors at startup; after renaming, the scales warp can still own that event. Swap FC2's `producer_exit` means the weight cursor finished and ancestor dependency was acquired, not necessarily the new combined elements loop has drained all B work. W4 FC1 can retain warp6's first-work-item signal; W4 FC2's immediate-after-dependency signal moves with the B payload reader. Existing final dependency waits and teardown joins remain.

These are required constraints, not evidence that the extra cursor bookkeeping will pay for itself. The low-overhead implementation should be evaluated against a simple bounded prologue plus steady-state loop. Reject an implementation that adds a large metadata framework merely to preserve nominal ownership; the experiment must demonstrate either performance improvement or reduced work with comparable simplicity.

## Established references and inheritance boundary

- Rubin's grouped gather kernel already uses independent producers with a shared TMA barrier, explicit producer counts and per-producer byte expectations. It is a useful accounting reference; it is not a reason to copy its SM107-specific layout/path branches. [Merged TMA pipeline](../flashinfer/flashinfer/fused_moe/cute_dsl/rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1504), [producer loop/acquire](../flashinfer/flashinfer/fused_moe/cute_dsl/rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:2470).
- The newer Blackwell MegaMoE source distinguishes weight and token pipeline depth/lifetime, and describes why token Gather4 completion and scale expectations must be paired. This supports preserving independent readiness rather than merging by instruction category indiscriminately. [Separate weight/token pipelines](../flashinfer/flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/sources/kernel_src/blackwell/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:707), [FC1 SF/Gather4 publication](../flashinfer/flashinfer/moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/sources/kernel_src/blackwell/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:978). Do not edit the vendored implementation.
- Local BF16/NVFP4 MegaMoE inherits W4A16 layout/transform helpers through `_MegaMixedInput`, overrides its stage computation and transformation warp IDs, then invokes inherited `_transform_tile`. It constructs its own raw/activation pipelines and its own kernel; it does not execute the split kernel's role branches. Keep this experiment in split-kernel role/producer code. Avoid modifying `_transform_tile`, `_finish_transform_stage`, shared dequantization helpers, layout/stage arithmetic, or shared `PipelineTmaAsync` behavior merely to implement the ownership swap. If role attributes are renamed, audit inherited constructor/setup references and keep MegaMoE's separate ownership unchanged. [Inheritance](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:55), [mixed layout construction](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:330), [own pipelines](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1152), [inherited transform calls](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1596).

## Experiment acceptance checklist after the current work finishes

- Compile-time roles only; same tactics, stage budget calculation, layouts, K-tail policy and dtype coverage.
- Audit lowered per-role registers/spills: W4 control warpgroup currently has80 registers/thread; swap gather's control warpgroup has128. New descriptor/SF state must not silently spill or break warpgroup register-reconfiguration convergence.
- First validate deadlock/accounting boundaries with tiny K (fewer than ring stages), zero/one/many tiles, token tails, ordinary/CLC scheduling, one/two CTA, PDL on/off and partial K. Existing exact accuracy paths cover numerical behavior; no new standalone test file is required.
- Check IKET timeline for weight/SFA prefill before PDL waits, no premature FC1 relay blocking, and independent raw/B progress in W4 FC2. Observe producer/mma waits rather than inferring overlap from source ordering.
- Only then compare EP/TP end-to-end and FC1/FC2 timing across V3, V41F, K3 and N3U for all supported dtypes, reusing current valid baselines. Keep any experimental changes in a separate review workspace, unstaged until retained.
