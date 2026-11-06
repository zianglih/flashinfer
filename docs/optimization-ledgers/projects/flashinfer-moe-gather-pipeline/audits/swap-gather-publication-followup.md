# Swap FC1 gather, SF publication and CLC follow-up

Retained source `02de7785c10847b3528340840bed40bd405d85b4` (full source receipt below). Read-only, using existing native captures and profiles. No edit or new GPU work. No additional low-complexity candidate is supported by this pass; the parent's integer-carried output-store investigation is separate and was not duplicated.

## Publication is two different completion domains

In `flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py`:

1. `:3470–3491` waits for the common operand stage to become reusable and registers Gather4 payload bytes in a CTA-local barrier. That barrier has `1 + min(route_tile, 128)` expected arrivals (`:2713–2717`): one transaction announcer plus each SF-copy participant.
2. `:3492–3519` places linear input SF words directly into canonical shared layout, skips rows outside rounded MMA N, zero-fills required padded rows/K, then attaches each participating thread's asynchronous SF completion to that local barrier. `:3521–3551` issues the payload Gather4 tasks against the same barrier. Thus local completion covers both the TMA transactions and every participating cp.async stream; it is not just payload-ready.
3. The activation control warp acquires local completion, crosses the async/shared proxy, and publishes one arrival per physical CTA (`:2997–3025`). In two-CTA mode `_gather_mbarrier_arrive:118–139` release-publishes each CTA's shared state to the leader, while `_gather_mbarrier_wait:143–169` acquires both CTAs. The one-CTA path already uses the simpler native local acquire/release. Replacing this with direct payload arrival would omit SF completion; replacing it with a gather-warpgroup rendezvous adds blocking and instruction work.
4. MMA first waits for independently loaded weights and copies SFA (`:3178–3204`), then waits for gathered B/SFB (`:3205–3221`), copies SFB and issues MMA. These are not duplicate waits: they let SFA work run while gather finishes. Moving SFA copies to the weight producer would make its prefetch cursor wait on TMA completion and change its progress contract, or require another role/queue. The rejected producer-ownership variants already measured that complexity tradeoff.

The public FC1 scale layout is the limiting contract, not a missed TMA invocation. For one token, four consecutive scale words must land 512 bytes apart in canonical shared storage. Current four-byte cp.async simultaneously transports and permutes them. The previous `sf-transport-audit/AUDIT.md` proves the sub-16-byte mismatch with direct TMA/S2T descriptors. Wider contiguous loads require additional scatter/transform work or a different input layout.

## What the newer references do differently

- Rubin split's `fused_moe/cute_dsl/rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:2092–2334` widens SF copies into a linear shared buffer, then dedicates another transform warpgroup and pipeline to reshape SF into TMEM. This is a different staged dataflow, not a lower-overhead replacement for one of the current barriers. Its pre-acquire SF LDS placement has a direct stage-lifetime reason, but does not establish that the current fused word placement needs the extra stage.
- New Rubin Mega `moe_ep/kernel_src/sm107/next_cutedsl_megamoe/src/sources/kernel_src/rubin/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:1000–1086` waits for per-expert canonical SF readiness, has TMA-SFB register transaction bytes, then synchronizes that issuer with four gather warps before payload issue. The canonical SF data was prepared by the communication/refine pipeline. Importing only the TMA call would drop that prerequisite layout conversion and its publication contract.
- Mega's optional live-row Gather4 adjusts expected bytes and payload issue count. The same general mechanism was already tested locally (`optimization-next-20261029/live-rows/RESULTS.md`): affected GM +0.014%, prefill −0.620%, with stable N3U EP W4A4 4K −6.834%. The later row-outer variant also regressed. The same code in a newer reference is not new evidence for retention.

## Native signal and its limit

The source-bound N3U TP W4A4 16K capture (`profiling/n3u-tp-w4a4-16k/RESULTS.md`) shows SF cp.async plus completion contributing 1,986 of 2,934 MIO samples, versus 227 at Gather4 issue. This identifies scale-transport issue pressure, but it does not make wider copies cheaper under the current layout. A 16-byte global load followed by four scattered shared stores is five memory instructions in place of four cp.async word copies, with more register lifetime and a new completion path. The existing payload-before-SF reorder and ownership-sharing attempts are closed.

In that same capture, the blocking MMA operand/gather slow-wait paths have zero sampled instructions, while the gathered-input empty-stage and epilogue accumulator probes have substantial samples. These protect real lifetimes; the data supplies no reason for an additional readiness cursor. Final-join barrier samples are distinguished from steady-state stage waits. The V3 TP MXFP8 profile reaches the same wait-removal boundary. Neither profile claims to characterize all CLC tactics.

## CLC metadata is already pruned by use

The current producer publishes tile/expert/valid once per work item (`:2798–2815`), and `next_work:2490–2505` copies fields before releasing exactly one metadata consumer phase. The consumer count at `:2677–2683` includes all active roles and excludes the follower CTA's inactive MMA warp. Gather, relay, weight, MMA and epilogue must independently retire their copy before the ring can be reused; their later operand progress does not substitute for metadata retirement.

A current retained native CLC FC1 capture is available at `validation/terminal-pdl/full-evidence/control-mxfp8-13/codegen/00-Sm100BlockScaledGroupedGemmKernel.ptx` (MXFP8, N16, one CTA, ordinary FC2, PDL on). It shows compiler pruning, not three mandatory scalar loads in every role:

- Weight role loads tile and expert together with `ld.shared.v2.b32` at PTX lines 327/455.
- Relay loads only tile using `ld.shared.b32` at 650/719; the unused expert and valid values are eliminated.
- Gather uses one 16-byte load with `.pragma "used_bytes_mask 0xf0f"` at 1596–1597 for nonadjacent tile/valid fields. The padded vector includes unused fields but remains one memory instruction. A separate helper or explicit lane shuffle would not simply remove a load.

The current all-thread release issues one warp instruction with per-thread arrival semantics, not 32 independently issued instructions. A one-lane release needs a warp join after all shared loads plus election/predication. The existing audit `clc-consumer-arrivals.md` already rejects assuming that logical arrival count measures instruction cost. New Mega's scheduler (`.../kernel_src/schedulers/base.py:75–89`) likewise copies the record before per-consumer retirement and an explicit fence; it does not offer a free elected-release pattern.

No stage-count change, transport/layout extension, new role, public knob or policy branch is proposed. A further SF optimization would need a demonstrated reduction in actual transport/permutation instructions without spilling or replacing the existing completion contract, rather than another barrier deletion.
