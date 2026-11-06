# FlashMLA CLC comparison

Audited 2026-10-26. FlashMLA official upstream was verified at <https://github.com/deepseek-ai/FlashMLA> and cloned once under `references/flashmla`, pinned to `395cb3afbb331fef7b1b21e9340861b9436b42d8`. FlashInfer is clean `9b4721b08057d0a488c1f0236467acb75c48cd00`. `flashmla-source-receipt.json` records source hashes. This is source analysis, not a measured performance comparison; no GPU work or production edits were performed.

The most useful transferable experiment is one elected CLC owner per CTA, with explicit per-CTA full-barrier publication. Keep the current metadata handoff and acquire-before-cancel order initially. FlashMLA does not establish that deeper queues or earlier cancellation will help our MoE kernel.

## Source facts

Short names below resolve to exact pinned sources:

- **MLA kernel**: [fused attention core kernel](https://github.com/deepseek-ai/FlashMLA/blob/395cb3afbb331fef7b1b21e9340861b9436b42d8/csrc/cuda_kernels/sm100/prefill/sparse/fused_norm_rope_attn_rope_cast_fwd/core_attn/kernel.cuh).
- **MLA config**: [fused attention core config](https://github.com/deepseek-ai/FlashMLA/blob/395cb3afbb331fef7b1b21e9340861b9436b42d8/csrc/cuda_kernels/sm100/prefill/sparse/fused_norm_rope_attn_rope_cast_fwd/core_attn/config.h).
- **MLA intrinsics**: [SM100 intrinsics](https://github.com/deepseek-ai/FlashMLA/blob/395cb3afbb331fef7b1b21e9340861b9436b42d8/csrc/3rdparty/kerutils/include/kerutils/device/cuda/sm100/intrinsics.cuh).
- **FI kernel**: [retained shared MoE kernel](https://github.com/zianglih/flashinfer/blob/9b4721b08057d0a488c1f0236467acb75c48cd00/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py).
- **SDK captures**: `sdk-*.py` in this directory, captured from the actual benchmark environment's CUTLASS 4.7.1. The current CUTLASS reference checkout is a separate source and must not substitute for these captures.

| Concern | FlashMLA | Current FlashInfer |
|---|---|---|
| Work unit / grid | One query token per job; 1 or 2 CTAs, 512 threads per CTA; grid `(s_q * CLUSTER_SIZE,1,1)` (MLA config 38–50; kernel 1665–1673). | One channel tile × routed-token tile; 1 or 2 CTAs. CLC grid includes the allocated route capacity, and scheduler filters routes beyond the live count (FI 1164–1175, 2107–2109). |
| CLC ownership | Entire fused-core CLC loop runs on one elected thread of warp 9 in each CTA (MLA 1188–1205). | Whole scheduler warp executes the loop and consumes the response. Only request issuance and metadata stores/commit are elected (FI 2091–2147; SDK scheduler 274–286). |
| Response transport | One aligned 16-byte response, one full barrier, one empty barrier (MLA config 287–294). CTA0 issues multicast; each CTA owner publishes its own `arrive_and_expect_tx(16)` (MLA 1192–1199). | One raw-response slot plus a separate decoded metadata ring (FI 1395–1414). Public FC1/FC2 calls currently both use one metadata stage (`blockscaled_contiguous_gather_grouped_gemm_act_fusion.py:992`, `blockscaled_contiguous_grouped_gemm_finalize_fusion.py:993`). |
| Consumers / metadata | Workers read the raw CLC response and calculate their query metadata themselves, then release CTA0's empty barrier (MLA 451–484, 500–512). | Scheduler loads expert/valid-row metadata once per CTA and publishes it to all worker threads; workers read three integers from the info slot, then release it (FI 1232–1247, 2121–2138). This avoids repeating route-metadata loads in all worker roles. |
| Lookahead / backpressure | CTA0 waits for all consumers to release the response before issuing the next query (MLA 1192–1194). It can issue the following query while workers process their current job. | Acquire the current metadata slot before requesting the next cancellation; request overlaps current metadata decode/publication (FI 2109–2143). Both designs use backpressure before response reuse; FlashMLA is not evidence for unbounded ahead-of-consumer requests. |
| First job | Workers derive first work directly from `blockIdx.x`; no CLC response handoff for first job (MLA 497–499). | Initial coordinate is also derived directly, but first work is published through the info ring; startup weight prefetch already uses the direct first coordinate (FI 1476–1518, 1574–1576). |
| Coordinate decode | Query index is `ctaid.x / CLUSTER_SIZE`; raw x/y/z query instructions are separated so unused coordinates can be eliminated (MLA 451–452; intrinsics 148–176). | Retains CUTLASS mapping; its default M-major unswizzled path is identity. The published tile integer is subsequently divided/remaindered by channel-tile count in worker roles (FI 1578–1582, 1813–1817). A previously rejected decoded-route metadata experiment already covers this tradeoff. |
| End of life | In 2-CTA mode CTA0 waits for all working threads' terminal empty arrivals and signals CTA1 before either can exit, explicitly avoiding a remote target disappearing (MLA 1206–1212; config 190–202). | Raw-response `producer_tail` remains before final CTA join; redundant local info producer-tail has already been removed (FI 2148–2159). The cluster response tail and TMEM lifetime protocol are not interchangeable with that removed local tail. |
| PDL | Inspected fused core has no grid-dependency instructions and uses a regular cluster launch (MLA 1665–1673). A generic PDL-capable host helper elsewhere does not make this core a PDL example. | Routing publication permits the scheduler warp to run before payload dependency completion; it waits before final join (FI 1521–1533, 2151–2155). Preserve this stronger cross-kernel contract. |

FlashMLA is not uniformly a dedicated scheduler warp design. Its simpler head64 sparse prefill shares a warp between validity-mask lanes and one CLC producer lane: [phase1.cuh 562–589](https://github.com/deepseek-ai/FlashMLA/blob/395cb3afbb331fef7b1b21e9340861b9436b42d8/csrc/cuda_kernels/sm100/prefill/sparse/fwd/head64/phase1.cuh#L562-L589). Its small-topk 2-CTA path also mixes CLC and producer work in the elected lane: [phase1.cuh 692–735](https://github.com/deepseek-ai/FlashMLA/blob/395cb3afbb331fef7b1b21e9340861b9436b42d8/csrc/cuda_kernels/sm100/prefill/sparse/fwd_for_small_topk/head128/phase1.cuh#L692-L735). This demonstrates ownership flexibility, not proof that sharing a warp helps our already busy TMA producers.

## Elected-owner feasibility and required changes

A naive `with elect_one()` around our existing scheduler loop is **incorrect for two CTAs**:

1. Exact SDK `PipelineClcFetchAsync` maps CTA0 lane 0 to CTA0's full barrier and CTA0 lane 1 to CTA1's full barrier (`sdk-PipelineClcFetchAsync.py:24–37,108–119,137–167`). Suppressing lane 1 omits CTA1's transaction expectation.
2. Its raw-response empty barrier currently expects `32 * cta_group_size` consumer arrivals (FI 1409–1411). One owner per CTA requires `cta_group_size` arrivals instead; local info-barrier consumer counts stay unchanged.
3. `advance_to_next_work` contains an internal `elect_one` (`sdk-ClcDynamicPersistentTileScheduler.py:274–286`). An already elected loop should issue through raw `cute.arch.issue_clc_query`; its exact SDK helper has no additional election or sync (`sdk-issue_clc_query.py:22–38`). The execution counter is unused by this kernel.
4. Exact SDK `clc_response` is a plain 128-bit shared load plus query operations, without warp synchronization (`sdk-clc_response.py:21–77`). `get_current_work` then inserts the generic→async response-reuse fence (`sdk-ClcDynamicPersistentTileScheduler.py:227–238`). Keep that fence. FlashMLA instead explicitly loads with `ld.acquire.cta.shared.b128`; the different implementation is not permission to delete our fence.

A general owner protocol can match FlashMLA while retaining our metadata ring:

- Elect once at the scheduler branch, one owner in every CTA. Preserve the same current work and metadata-slot backpressure.
- Only CTA0's owner waits for the raw-response empty phase and issues the multicast query. Each CTA owner publishes the 16-byte expectation to **its local full barrier**. All owners then wait for their full phase, decode with the existing mapping/fence, and release **CTA0's empty barrier once**.
- Publish the current decoded metadata through the existing single-owner info producer. Do not change worker membership, number of info stages, route filtering, or phase progression. Keep the terminal raw-response drain and final CTA/TMEM join.
- Keep the delayed PDL wait outside the elected region so the scheduler warp follows the existing teardown structure. Do not move any payload access ahead of dependency completion.

This requires a small explicit owner-aware CLC pipeline implementation or adaptation; merely changing the consumer count is insufficient. There is no dtype/shape-specific policy and no extra autotune axis.

**Expected benefit is a hypothesis:** fewer participating barrier arrivals and simpler ownership. SIMT already executes a common instruction once for a warp, so election does not divide instruction count by 32 and does not automatically reduce allocated registers. Check generated PTX/SASS, arrivals, register count and end-to-end timing before retaining it. Minimal validation is existing 1-/2-CTA probes with live/empty/padded/terminal routing, plus the current model × format retention grid.

## Follow-up priority

1. **First:** elected per-CTA raw-response ownership, leaving the decoded metadata handoff intact. This is the smallest new idea relative to our retained single info publisher.
2. **Second, only if traces show first-tile scheduler stalls:** bypass the initial info handoff using direct first-work coordinates, as FlashMLA does. It trades a publication/wait for repeated initial route-metadata loads, needs careful phase accounting and padded-route handling, and may lose rather than win on MoE. Treat as a separate experiment, not a default assumption.
3. **Do not copy wholesale:** direct raw-response consumption removes our metadata ring but repeats expert/valid decoding and changes worker coupling. FlashMLA's job contains many KV blocks and different worker dependencies; our short MoE tiles can expose a different balance.
4. **Do not repeat rejected knobs:** the local ledger already rejects request-before-slot-acquire and deeper metadata default policies for decode regressions. FlashMLA's one-slot backpressure does not overturn that evidence. No queue-depth tuning axis.

The shared FC1/FC2 CLC flag experiment remains a separate host-policy comparison. This audit adds no tactic dimension and changes none of its frozen sources or GPU runs.
