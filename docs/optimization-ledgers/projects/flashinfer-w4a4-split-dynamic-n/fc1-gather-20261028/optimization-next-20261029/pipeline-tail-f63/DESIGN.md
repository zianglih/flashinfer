# Fixed physical-slot terminal pipeline drain

Source: f63e9485, isolated unstaged `flashinfer-pipeline-tail-review`; three changed files are pinned by local-source.json and candidate.patch.

The SDK PipelineAsync producer_tail waits all N empty barriers by advancing the dynamic ring index after each wait. Source-bound retained MXFP8 FC2 SASS (`../composed-w4/validation/evidence/codegen/candidate/001-fc2.sass`, N=5) contains repeated UIADD3/UISETP/USEL/ULOP3/ULEA between tail waits. The candidate unrolls physical slots 0..N−1 and computes each expected phase as `state.phase XOR (slot < state.index)`. All N barriers and all expected phases remain unchanged. phase-proof.json exhaustively verifies the same (slot,phase) set for stages1–64, all next-write indices, both phases (4160 states).

The accumulator and CLC/scheduler protocols are explicitly excluded. PipelineUmmaAsync overrides the SDK all-slot drain: it advances to the last slot and waits only on the leader CTA. The first exploratory revision wrongly replaced this override; it was stopped and preserved under r0-stopped, before any performance measurement. Both accumulator call sites are now restored.

All changed call sites are after the producer's last work tile, with no subsequent copies or full-barrier publication. Consumers can finish every published stage independently of tail-wait order; no tail wait issues consumer work or releases another resource. Thus waiting a different empty slot first cannot prevent the consumer release needed for that slot. Final CTA/cluster join and resource deallocation remain after the complete drain. This proof does not authorize reordering steady-state acquires or removing a wait.

Preserved: stage capacity, cross-work-tile prefetch, all steady-state acquire/release/advance operations, PDL, metadata/CLC scheduler drains, TMA-store completion. W4 transform and MMA lifetimes stay separate. The helper does not mutate an otherwise dead terminal state.

K/tile/stage counts are already compile time; default PipelineState.advance uses equality/select, not division, and unused count arithmetic is eliminated. Clamping capacity to one work tile would destroy cross-tile latency hiding. Rubin/MegaMoE maintain the same persistent-state principle. Prior live-row, predicated, election, unsigned, buffer-cap, and producer-readiness experiments are not repeated.

Next gate: exact existing tests plus fresh source-paired diagnostic CUBIN/PTX/SASS, one/two CTA, swap NVFP4/MXFP8/MXFP4x8 and W4A16 old/new layouts. Diagnostic keep/no-cache compilation is excluded from performance claims. GPU6 only; persistent native and DSL caches preserved. No performance result yet.

## Audit conclusions

- Swap operand capacity is compile-time SMEM accounting, not a per-problem lookup. K extent is static and its short final stage is peeled. The one-iteration `PipelineState.advance()` lowers to increment, comparison/select, and phase toggle; it has no runtime division. The generalized multi-step API can divide, but none of these operand progression sites call it with a dynamic step.
- Both swap and W4A16 keep index/phase across successive scheduler work tiles. A stage may therefore hold an operand for the next work tile while the MMA consumes the current tile. `Ktiles < capacity` alone does not establish dead storage. Capping the ring at Ktiles would remove this overlap, especially PDL weight startup, and is not proposed.
- W4A16 resets only the per-tile count used by readiness lookahead and addressing. Its load-to-transform and transform-to-MMA rings have different resource lifetimes; neither can be merged merely because both advance once per K stage.
- Rubin uses persistent producer/consumer states, count reset, and readiness lookahead. MegaMoE likewise pipelines across work tiles. Neither provides support for a blanket per-tile stage clamp.
- The low-risk instruction opportunity is terminal all-slot draining, where dynamic ring advancement is unnecessary. This is once per persistent CTA, not per MMA stage. Any expected end-to-end benefit should therefore be modest and workload-dependent; instruction reduction is the primary sanity target.
- Runtime method identity (method-audit-v2.json) proves that only SDK `PipelineTmaAsync`, `PipelineTmaUmma`, and `PipelineAsyncUmma` are changed. Both custom and SDK `PipelineUmmaAsync` accumulator tail overrides stay intact, as do CLC/metadata and TMA-store protocols.
