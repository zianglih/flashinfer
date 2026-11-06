# FC1 protected-prefix audit

A general deferred-store implementation is viable without a new tactic axis or model/dtype rules. Buffer only the first `overlap_activation_steps - 1` transformed slabs, then release ownership after the last protected slab's TMEM operations, before finishing the deferred slabs' absmax/quantization/stores. The current capacity policy limits this extra buffer to one slab: 16 FP32 values per lane for gated activations, or 32 for ReLU². This is an unimplemented source assessment, not a measured optimization.

The opportunity currently affects **10 of 208 selected model/format/token configurations**, all prefill NVFP4 configurations. Four standard NVFP4 and six per-token winners use two protected slabs. Fourteen MX winners use one protected slab and already release before their quantization/stores; 184 configurations do not use the overlapping FC1 path. In particular, this change would not address the selected standard-NVFP4 Nemo 16K slowdown directly.

## Actual selected coverage

The following table lists every active two-slab winner. All use K steps 4, K tile 256, 256 accumulator columns, 48 scale columns, and a 64-column protected prefix. The other tokens for these formats are inactive. `M` is logical channel tiling, `N` is route tiling.

| Model | Format | Tokens | M / N | CTA group | Extra FP32 values per lane |
|---|---|---|---|---|---|
| V3 | NVFP4 | 4096, 16384 | 256 / 256 | 2 | 16 |
| V3 | PER-TOKEN | 4096 | 256 / 256 | 2 | 16 |
| V4.1-Flash | NVFP4 | 8192 | 256 / 256 | 2 | 16 |
| V4.1-Flash | PER-TOKEN | 8192 | 256 / 256 | 2 | 16 |
| Kimi K3 | NVFP4 | 8192 | 256 / 256 | 2 | 16 |
| Kimi K3 | PER-TOKEN | 8192 | 128 / 256 | 1 | 16 |
| Nemo 3 Ultra | NVFP4 | None | — | — | 0 |
| Nemo 3 Ultra | PER-TOKEN | 4096, 16384 | 256 / 256 | 2 | 32 |
| Nemo 3 Ultra | PER-TOKEN | 8192 | 512 / 128 | 2 | 32 |

The Nemo PER-TOKEN 8192 winner has two channel tiles. A token-only prefix implementation would miss this existing case; the current virtual slab mapping across channel tiles must remain the source of slab addresses.

| Model | MXFP8: one protected slab | MXFP4x8: one protected slab |
|---|---|---|
| V3 | 4096, 8192, 16384 | 4096, 16384 |
| V4.1-Flash | 8192, 16384 | 8192 |
| Kimi K3 | 8192 | 8192 |
| Nemo 3 Ultra | 4096, 16384 | 4096, 16384 |

No selected MX winner has more than one protected slab. All unlisted MX cells are inactive. All decode cells are inactive. This coverage comes from the current arm of the completed native-winner campaign, not forced geometry or the historical all-CLC campaign.

## Concise implementation shape

1. Extract FC1's existing TMEM load/activation/transpose work and its post-transform absmax/quantization/store work into reusable helpers. Reuse these from the ordinary slab path and the overlapping prefix; do not duplicate `_run_token_group` or generalize FC2's separate packed-output contract unnecessarily.
2. For more than one protected slab, keep a statically indexed register buffer of `(protected_steps - 1) * values_per_slab`. `values_per_slab` follows the existing gated/non-gated activation contract: 16 or 32. A one-slab prefix takes the current direct path and creates no extra live buffer.
3. Transform the buffered prefix slabs first. Transform the last protected slab using the existing release locations, including the TMEM-load fence; then finish all protected output slabs before continuing the remaining virtual slab loop. This moves only the earlier protected slabs' post-transform work off the MMA ownership critical path.
4. Keep the existing reverse/forward traversal and virtual `channel_tile`, `token_start`, and `channel_start` formulas. Preserve the whole-slab validity condition when buffering and draining. Invalid slabs must not read uninitialized register slots, and an invalid last protected slab must still release exactly once as the current `elif` does.

The helper should retain the current per-token release point after both transposes and before activation for the last protected slab. For an earlier buffered per-token slab, compute its activation before buffering to retain only 16 gated output values, rather than 32 raw up/gate values. ReLU² requires both 16-value halves, so its buffer is 32 FP32 values. Preserve the existing arithmetic order and FP32-to-output conversion; there is no need for a new packed-buffer/dtype policy.

This is a moderate extraction of the existing FC1 code, not a one-line change. It can be kept general and concise, but should not be bundled with a second transpose design or a larger TMEM-overlap allowance.

## Safety and resource boundaries

- **TMEM ownership:** `_blockscaled_transpose16x32` writes and reloads scratch within the accumulator slab. Keep ownership until every protected slab has completed that work. Buffering transformed register values is safe because later MMA writes cannot modify them. Moving the release before either transpose is unsafe.
- **Scale reductions:** gated SF32 absmax uses two named-barrier joins and shared scratch. Perform its reduction in the deferred store helper, with all four epilogue warps participating in each valid slab. Do not retain references to shared scratch or transpose scratch in the buffer. There is no new need to coalesce barriers across slabs.
- **Partial/reverse tiles:** the skipped-final-protected-slab release remains necessary. Buffer slot validity and the final release cannot be conditioned on every token lane being valid. The entire-slab predicate is CTA-uniform; lane validity belongs only to output stores and per-token metadata loads.
- **Two channel tiles:** preserve the virtual slab traversal; its prefix can address a different channel tile in reverse phase. Register slots need only values; output addresses are recomputed from constexpr slab indices, so no per-slab dynamic index or large metadata buffer is required.
- **Register cost:** the extra *logical live payload* is 16/32 FP32 values per lane, not a full additional tile. It does double the transformed-slab payload while processing the last protected slab, but does not double the complete kernel register footprint. Actual allocation, spills, scheduling, and code size still require a compiled-resource check. Neither a register-count claim nor a performance claim follows from this host audit.
- **Scope:** keep the current maximum two-slab overlap. Increasing it would expand the register cost and intersects FC2's distinct 64-column ownership contract. No tactic expansion, model predicates, dtype gates, or changes to single-slab/inactive kernels are needed.

## Evidence and source locations

Reviewed canonical head: `d02c487a15d0636e902c3f7a5e0bf7cf4a03156d`. Measured current head: `0b7fe90151340d4fca6a5ec41a91019dde743819`. All eight campaign receipts have exactly matching core/FC1/wrapper hashes against the reviewed source. The reviewed core SHA256 is `3a6331d78363ae0e97e12968d063dc5cfaa71d87f62ff72fee980c03651a9c01`.

In `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`:

- Lines 289–340: TMEM transpose scratch contract.
- Lines 540–550: gated SF32 absmax shared-scratch exchange.
- Lines 659–820: current slab transform, release, reduction and stores.
- Lines 823–877: virtual protected prefix and skipped-slab release.
- Lines 1471–1482 and 1511–1520: accumulator/scale allocation and capacity-derived overlap.
- Lines 2141–2153: scale-footprint rounding and protected-step assignment.
- Lines 2882–2917: overlapping FC1 epilogue dispatch.

The root wrapper passes `overlap_epilogue=True` at line 281. The FC1 wrapper passes `overlap_activation_accumulators=None` at line 976, so the capacity rule selects the path. No geometry is inferred from a backend label alone.

`analyze.py` uses actual per-cell FC1 dispatch fields and native cached tactics, verifies both current frozen passes (`n1` and `n2`) match in all 208 cases, and evaluates the exact AST-extracted `_accumulator_storage` method with the SM100 TMEM capacity. `coverage.csv` contains all 208 cells; `receipt.json` pins all 24 input receipts/results and the three reviewed source files.

The reconstructed `effective_protected_slabs=0` means the overlapping FC1 path is inactive. The raw epilogue attribute is assigned `64 / 32 = 2` even for inactive geometries; counting that attribute without checking `overlap_activation_accumulators` would misleadingly report two slabs for most kernels.

No GPU work, source edits, native AUTO, new performance samples, or modifications to the primary benchmark evidence were performed. The historical proposal remains in `scripts/pipeline_acc_overlap_audit_20261027/README.md`; this audit refreshes its relevance against all four models and formats.
