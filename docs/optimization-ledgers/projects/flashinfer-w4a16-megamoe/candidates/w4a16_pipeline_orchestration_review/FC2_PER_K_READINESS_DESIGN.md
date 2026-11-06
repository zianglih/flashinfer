# FC2 activation readiness by K256 region

Source-only feasibility review, 2026-09-11, during the exact-tail experiment. No production edits, compilation, profiling, or timing. Paths are relative to the project checkout `flashinfer/`; cited line numbers describe the inspected source.

**Conclusion:** a credible, distinct overlap candidate, with no identified source-level ownership blocker. It would let FC2 load an already completed feature region and begin its original ordered MMA while later FC1 regions finish. It does not enable missing weight/decode overlap: those roles already run independently. The useful window is unproven and may be small under the current assignment order and publication batching.

## Exact region mapping

- Owned `megamoe_kernel.py:155–186,670–704` admits M128/M256, N64/N128, K256, with I divisible by64. The inherited split helper `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:199–213` divides MMA M by its one/two-CTA thread layout: M256/TWO and M128/ONE both have **128 raw gate/up features per CTA**.
- Scheduler parameters swap M/N and cluster axes once (`kernel_src/cutedsl_megamoe/src/moe_nvfp4_swapab/moe_persistent_scheduler.py:322–340`). Owned `fc1_fc2_fuse_sched.py:906–933` returns `tile_m_idx = cluster_feature_idx * cluster_feature_ctas + feature_cta_rank`. Thus M128/C2 and M256/C2 each cover two consecutive CTA feature indices; M128/C1 covers one.
- Owned `epilogue.py:561–669` consumes gate16/up16 pairs within each CTA, applies the existing FP32 alpha/SwiGLU, and writes **64 contiguous post-SwiGLU I features**: `column = tile_m_idx*64 + warp_idx*16`. A FC2 K256 tile therefore depends on CTA indices `4*k ... 4*k+3`, not on four raw gate/up tiles or token subtiles.
- Let `G = ceil(I/256)`. Report bucket `k = tile_m_idx//4`; its terminal count is `min(4, ceil((I-256*k)/64))`. Final buckets with I%256=64/128/192 expect1/2/3 reports. The existing OOB-feature predicate (`epilogue.py:443–464`) must remain. All N64/N128 valid token subtiles finish before the single report; no per-token or per-subtile counters are required.
- FC2 B already views the BF16 output as `(pool_tokens,I,1)` with stride `(I,1,0)` (`megamoe_kernel.py:692–700`). Its existing K256 tiling, partial-I TMA bounds, dynamic-N/nonleader shift, destination layout and transaction bytes remain valid. No SF handoff or gate/up layout changes are needed.

## Minimal owned protocol

Replace the existing FC1 completion region by G Int32 counters per token-block slot, indexed `(cumulative_token_block_count + tile_n_idx)*G + k`. Change only owned workspace sizing, FC1 report addressing, the owned scheduler extension's FC2 peek, and FC2 activation readiness.

Keep the **existing publication location**: all BF16 stores, next-record consumption and epilogue barrier1/128 precede `signal_fc1_done` (`epilogue.py:226–272`). Accumulator release alone is too early; the final BF16 stores occur after it. Reuse the same GPU-release add and GPU-acquire polling (`src/src/flag_batch.py:111–121`; `moe_nvfp4_swapab/moe_utils.py:93–116`). This preserves the current multi-writer completion contract independently for each region.

The current FC2 peek and activation wait test the **whole feature count**, I/64 (`custom_ext.py:245–260`; `megamoe_kernel.py:1025–1031,1215–1243`). A replacement peek should certify **K0 only**; its bit must never skip K1+ waits. Inside the existing FC2 activation producer loop, acquire-wait each region before acquiring/filling that B stage. Keep raw-weight/decode loops, ordered K traversal, B/raw/decoded/ACC depths and phase/index advancement unchanged (`megamoe_kernel.py:926–982,1142–1188,1245–1353`). If G=1, there is no finer dependency to expose.

There is no new cross-work dependency: every prerequisite FC1 work precedes its FC2 work in each group's logical ordering. Existing per-CTA streams retain that order; FC1 batches flush on the transition to FC2 or terminal work. Beginning FC2 earlier does not place unfinished prerequisite FC1 work behind that FC2 on the same CTA. Nevertheless, implementation review must retain next-work consumption, phase flushing, pipeline tails and both static/atomic schedules exactly.

**Tracker correction:** the shared rotating-lane tracker does **not** flush on address changes. Each lane retains its own counter address; only batch threshold or phase change flushes (`src/src/flag_batch.py:46–90`). Therefore region counters need not add atomics or disable batching. Existing FC1 batch2 can defer a region's readiness until another local FC1 completion; manual batches up to32 can defer it further. Do not assume that changing the counter address publishes immediately.

## Storage and launch lifecycle

Owned `megamoe_kernel.py:1428–1502` allocates S completion slots in the accumulating local prefix. Expanding to S*G costs `4*S*(G-1)` extra global bytes, no shared memory or TMEM. For EP8/E256/topk8/cap512/I2048 with frontend padding=N, S is576 at N64 or320 at N128: extra16,128 or8,960 bytes, before later region alignment. Counter values themselves are bounded by4.

The kernel derives the first-launch zero requirement and tail zero view from the offset of the first data buffer (`megamoe_kernel.py:285–298,570–576`). Shared transport already clears that entire local prefix after its final peer barrier (`src/src/token_comm.py:1745–1782,1863–1873`). Resizing the owned region therefore reuses reset/graph replay/empty-rank lifecycle without a transport edit. Empty experts schedule no reports or waits; padding slots remain harmless. Do not retain a second aggregate counter merely to preserve the old peek: that adds a second release per report and obscures the experiment.

## Assignment limits, costs, and evidence

The scheduler lists all FC1 work of a group before FC2, with token block slow and feature block fast (`fc1_fc2_fuse_sched.py:747–765,808–869,889–904`). **Assignment is not completion:** another resident cluster can claim FC2 while earlier FC1 work is still computing or queued. Low feature indices tend to be assigned first, so a first-K-ready/last-K-not-ready interval is possible. But early token blocks in a large group may be completely ready before any FC2 claim; small groups launch many similar FC1 feature tiles concurrently, whose completions may cluster closely. Batch2 and next-record publication delay further narrow the interval.

Every FC2 hidden-output CTA now performs up to G acquire checks instead of one coarse check; the same bucket is checked by multiple hidden tiles/CTAs. Additional address/threshold arithmetic, counter cache lines and larger reset traffic can outweigh the overlap. With I2048, G=8. The change neither adds decoded capacity nor permits arbitrary out-of-order K execution, and an FC2 accumulator remains owned through all K tiles.

Bounded sibling/history review found no prior per-K completion design. Shared W4A4 `src/moe_nvfp4_swapab/kernel_fc12.py:2001–2040`, BF16 `src/moe_bf16_glu/kernel_bf16_glu_fc12.py:1396–1427`, and MXFP8 `src/moe_mxfp8_glu/kernel_mxfp8_glu_fc12.py:1740–1764` use whole-row readiness before the K loop. Ledger Entry040 and the held `w4a16_fc1_completion_batch1/INDEPENDENT_REVIEW.md:19` change peeking/batching, not readiness granularity; prior late-acquire/predecode trials do not test this design.

There is **no current measured benefit claim**. The historical T1024 PC audit (`candidates/w4a16_direct_epi_profiles/PC_WAIT_ATTRIBUTION_T1024.md:3–16`) found zero samples at the actual FC2 completion loads/poll loop on all ranks; that older sampled source is weak motivation, not proof the window cannot exist. The design is small enough for a separate owned experiment if selected, but existing full-AUTO tail results do not establish its value.
