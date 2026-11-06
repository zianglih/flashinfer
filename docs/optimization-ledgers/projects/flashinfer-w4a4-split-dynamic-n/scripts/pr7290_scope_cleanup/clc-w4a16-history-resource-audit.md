# CLC queue-depth and resource audit

Read-only review of retained source `fca8462cbd9096059d0019a206aa760fb34ca8c4`, 2026-10-25. Companion JSON pins source and evidence hashes, independently parses historical native medians, and recomputes the selected historical geometric means. No source changes, GPU runs or PR edits.

## Transferable scheduler result

The most useful W4A16 precedent is **one route tile per cancellation, one CLC metadata slot, cancellation after metadata-slot acquisition**. Static scheduling retained three metadata slots. These are different tradeoffs: static metadata lookahead feeds the load/transform pipeline; dynamic lookahead also removes work from the global pool before a cluster is ready to execute it.

Source: `/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md`.

| Source lines | Historical finding | Consequence for this experiment |
|---|---|---|
| 1778–1838 | Static queue2→3 helped TP8 ~3.2–3.5% with EP8 near-neutral; queue4 regressed. | Do not infer that a deeper queue is always better. Queue depth is independent of operand stage depth. |
| 2523–2559,2644–2656 | CLC queue3→2 reduced work hoarding; queue2→1 added1.015828× EP8 and1.010503× TP8 full-grid gains; dense4096 was unchanged. | Start CLC with one metadata slot. Independently parsed raw logs reproduce these latter ratios. |
| 2546–2550 | Acquire an available metadata slot before issuing the next cancellation; invalid padding entries can continue querying without publishing. | A blocked producer must not reserve an extra valid tile outside the bounded queue. |
| 2506–2521 | Bundling2/4 route tiles per cancellation caused large losses. | Preserve one independently rebalanced route tile per cancellation initially. |
| 2603–2614 | Single-lane response decoding plus shuffles regressed dense4096 by8.41%. | Keep full-warp response consumption first. |
| 2694–2702 | Single elected metadata publisher was neutral and restored. | Avoid new participant-count complexity without evidence. |
| 2733–2749 | Exact logical-grid versus resident-cluster-wave condition retained; one-wave launches cannot steal pending work. | Use an explicit scheduler behavior knob and capacity-derived enablement, not a token threshold or an activation-type proxy. |
| 4099–4125 | Enabling FC2 CLC lost0.68% EP8 and8.99% simulatedTP8 overall. | FC1-first is the strongest historical prior; FC2 needs separate evidence. The present block-scaled core may differ, so this is not a prohibition. |

Historical measurements used an older W4A16 core with dequantization warps and a1–4096token grid. Their full-grid geomeans include1/2 and are **not** evidence under today's11-point retention aggregates. The raw logs exist locally and the parsed values/hashes are in the companion JSON; no historical ratio is a new-kernel performance claim.

CLC query ownership follows launch CTA rank0, including a two-CTA launch whose MMA is one-CTA. The W4A16 ledger also requires skipping padded route IDs above the runtime-valid compact prefix until hardware reports no more pending clusters (lines2482–2488).

## Current core resources and synchronization

Current source has288threads with dedicated epilogue overlap and160 without (line351), no explicit register cap/reconfiguration, and launch `min_blocks_per_mp=1` (line898). A final scheduler warp changes these to320/192 while retaining role IDs and TMEM lane mapping.

The Blackwell guide specifies64K32-bit registers/SM and255registers/thread. Simple uniform-register upper bounds therefore change227→204 for288→320threads;160→192 remains bounded by255. Allocation granularity or other resources can lower these arithmetic bounds. This is not a measured occupancy prediction. [NVIDIA Blackwell Tuning Guide](https://docs.nvidia.com/cuda/blackwell-tuning-guide/index.html#occupancy)

Earlier codegen/NSYS captures of this core, pinned in the companion JSON, used64–122registers/thread, no local memory, and roughly195–230KB dynamic shared memory; the two explicitly compiled FC2 controls reported one active CTA/SM. Those captures suggest register headroom, but do not establish the exact final-fca resource count. Compile the new candidate and inspect registers, spills, dynamicSMEM and active-cluster capacity before introducing a register policy.

Do not transplant the old W4A16 mixed-role `setmaxnreg` arrangement: that512thread core eventually required uniform control-warpgroup targets after mixed targets hung. Current9/5warp CTA shapes also include incomplete final warpgroups. PTX requires the same reconfiguration instruction across a warpgroup and may block an increment until its CTA pool has enough registers. [PTX setmaxnreg](https://docs.nvidia.com/cuda/parallel-thread-execution/#miscellaneous-instructions-setmaxnreg)

The new queue affects these concrete current contracts:

- `_metadata_bytes` (lines432–436) currently counts only operand/accumulator barriers, a TMEM handle and alignment gaps. Add scheduler metadata, CLC response storage and their barriers to the actual aligned footprint **before** `_configure_pipeline_storage` selects operand stages or epilogue bulk storage. The final `SharedStorage.size_in_bytes()` capacity check must stay authoritative.
- Whole-CTA TMEM retrieval and teardown barriers use `self.threads_per_cta` (lines992,1537). The scheduler must participate before diverging and rejoin after all consumers release metadata. Keep TMEM access warp IDs unchanged; adding a warp does not add TMEM lanes.
- A one-slot queue can serialize the next cancellation behind the slowest metadata consumer. Release metadata once the role has copied everything it needs into private state, without confusing this lifetime with asynchronous operand/SF/accumulator lifetimes. Avoid holding a slot through epilogue work unless it still needs that shared record.
- The resident-wave decision must use the candidate's resource/cluster contract. `min_blocks_per_mp=1` is a compiler launch bound, not an independent occupancy measurement.

Conservative first experiment: preserve existing producer/epilogue/MMA roles, add one scheduler warp, full-warp response consumption, one metadata slot, post-acquire cancellation and one route tile per cancellation. Keep queue depth explicit at compile time for a bounded1vs2 diagnostic if the first traces show starvation. Preserve static scheduling for capacity-limited one-wave launches and evaluate the whole chain on both models rather than relying on a kernel-only latency gain.
