# Early deterministic-reduction preparation audit

Source: frozen HashInfer `04c51ad94738877e67045ece949ed16cd12c6f82`; device evidence is the qualified H6144/T128/tactic0/O3/EP8 pair against measured `14a9e720d02472ae602ca3ed3ba121f273de4573`. All eight paired stage/core CUBINs are byte-identical. This audit proposes scheduling changes; it establishes neither a candidate implementation nor a speedup.

## Readiness boundaries

- `modes/mega_layer.py:429–437` stages inputs before calling compute. Backend `stage_inputs` copies routing into `workspace.topk_weights`; the fused stager writes each live FP32 score unchanged (`backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/staging_kernel.py:69–78`). The torch fallback also copies only the live score prefix (`common/bf16_staging.py:21–26`). Inactive score rows may contain old data.
- Public forward passes that local symmetric score buffer into `MegaMoEBf16Nvfp4Inputs` (`cute_dsl/megamoe/bf16_nvfp4/frontend.py:664–676`); the kernel binds it directly as `input_topk_weights_buffer` (`megamoe_kernel.py:559–566`). This is the original source-token routing matrix, not the remote expert-pool score buffer. Local reduction does not need remote score pulls or expert scheduling metadata.
- Current PR8 launches neither staging nor MegaMoE with PDL (`staging_kernel.py:28–30`, `megamoe_kernel.py:802–809`). Captured stage and core PTX both contain zero `griddepcontrol` instructions. Both are launched on the current stream, so live scores are ready before this kernel executes and remain immutable throughout it. PR7's separate PDL experiment is not the contract of this source. If PDL is introduced later, any early score loads must follow the score producer's dependency completion; a different warp's wait cannot silently substitute for a proven cross-warp handoff.
- FC2 BF16 terms have a different dependency. `token_comm.py:24–81` first rendezvous all 640 CTA threads, then dispatch warps perform the inter-CTA/inter-rank drain. `megamoe_kernel.py:1356–1364` hands completed drain to all threads via a second 640-thread barrier. Only after this handoff may reduction read `combine_output`. Preserve outgoing-copy completion, epilogue system fence and both communication barriers.

## Concrete overlap placement

The earliest correctness-safe score-preparation point is after a non-dispatch role retires, even before the first tail rendezvous. The preferred first candidate places preparation **after the existing first CTA rendezvous, alongside dispatch-only global drain, before the second handoff**. This lets the dispatch WG start draining without waiting for score preparation. The existing `kernel_tail_drain` already returns immediately for non-dispatch warps after the first rendezvous while dispatch warps remain inside the drain. Place guarded preparation directly after that call and before the second handoff. No tail-method split, new barriers, raw shared-src edits or new synchronization counters are needed; a function return does not create a CTA-wide rendezvous.

The four retired WGs are warps0–7 and12–19 (512 threads). Preserve the existing bijective assignment:

```
reduce_thread = tidx if warp < 8 else tidx - 128
worker = ((reduce_thread // 128) * sm_count + cta_linear_id) * 128 + reduce_thread % 128
stride = sm_count * 512
valid = worker < active_local_rows * (hidden // 8)
token = worker // (hidden // 8)
hidden_tile = worker % (hidden // 8)
```

For each valid initial worker, prepare token/hidden mapping, term/destination addresses, and FP32 routing-score registers during drain. Address construction is safe; dereferencing BF16 FC2 terms is not. After the handoff, feed prepared scores into the same ordered reducer and then continue the existing strided loop. Keep compile-time deterministic/IKR and optional-output dispatch: this applies only to the deterministic integrated branch. For `top_k <= 16`, retaining the existing score-prefetch policy requires K FP32 registers (eight in current model shapes). Avoid accidentally forcing a large score-prefetch policy for K>16; mapping preparation can still be general.

Preparing one initial worker per thread limits register lifetime. It covers all work in small cases but only the first strided iteration for large cases. Prefetching every future iteration would grow storage and should not be folded into this bounded candidate. The owned helper can separate metadata/score preparation from the first actual term load while retaining all packed mul/FMA and final BF16 conversion statements unchanged.

## Empty ranks, unequal rows and graph reuse

- Guard all score loads with `worker < active_local_rows * hidden_tiles`, using the actual dynamic `reduced_output.shape[0]`, never workspace capacity. Zero-row ranks and the zero-row raw thunk load no scores, terms or destination. Threads with no valid worker must still execute every required CTA rendezvous.
- Unequal local row counts change only each rank's local work bound. Keep all dispatch drain/cleanup and participation counts unchanged; a rank with no local output can still have experts to compute and peer traffic to drain.
- Keep the prefetch register-local to this invocation. No persistent score cache, shared scratch state or host memo is needed. Back-to-back same-stream graph replays rerun staging before the next core; prior core completion includes both dispatch cleanup and all reducer stores. Independent streams concurrently reusing one mutable workspace are not newly supported by this proposal.
- Preserve worker ownership, ascending top-k order, initial FP32 multiply, subsequent packed FP32 FMA and final BF16 cast. Earlier loads of immutable FP32 scores change neither arithmetic nor combine order. No atomic/TMA reduction is introduced.

## Existing compiler placement: not already hoisted

See hash-bound `baseline-tail.ptx.txt` and `baseline-tail.sass.txt`, extracted from the qualified candidate first-pair artifact (identical core CUBIN to old14).

- PTX: first tail barrier line6180; post-drain handoff6273. Full worker mapping begins6549, token/hidden split6578, score loads6602–6603, first BF16 term load6604.
- SASS: first tail `BAR.SYNC ... 0x8,0x280` at0x138d0; handoff at0x13f00. Worker mapping starts0x152d0; live-row metadata is loaded at0x15300; score base at0x15450; score loads at0x15580 and0x155b0. The first BF16 term load is0x15550: ptxas interleaves term and score loads, but all remain after the handoff.
- Non-dispatch WGs branch around dispatch cleanup; the later textual offsets do not mean they wait for cleanup. They already overlap reduction with cleanup. What remains unhidden is their mapping/score preparation while waiting for global drain.
- Some parameter loads and common CTA/thread identifiers are already available earlier. Merely relocating declarations is therefore insufficient evidence. A compiled candidate must visibly move the actual worker-bound/address calculations and score global loads before the second handoff, while every combine global load stays after it. Preserve all resource and spill diagnostics; source movement alone is not success.

The observed placement gives a concrete scheduling opportunity. Its magnitude and any register-pressure tradeoff still require the planned matched candidate benchmark and numerical/sanitizer validation.
