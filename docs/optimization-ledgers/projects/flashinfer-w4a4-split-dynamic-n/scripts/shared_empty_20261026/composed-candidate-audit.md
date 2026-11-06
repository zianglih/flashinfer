# Read-only audit of retained-policy composition

Reviewed `../../flashinfer-retained-policy-20261026` at base
`0def601d6603df828ea39679b41ccbce64f7f09e`: the resource-bounded per-token row grid,
live-row prefix, and shared operand empty ring. No source edits or additional
broad tests were performed. `git diff --check` passed.

## Result

No functional, API compatibility, cache identity or synchronization issue found
in the composition. The blockscaled core exactly matches the source-paired
shared-empty candidate; the helper differs only by the new ownership docstring.
The row-grid arithmetic and its bounded exact gates were independently traced
from the local source and `scripts/row_grid_quantizer_20261026` evidence.
Final combined native-AUTO performance/validation remains the parent task.

## Live prefix and allocation

`valid_rows` is an appended optional argument, preserving existing positional
calls. Metadata checks enforce int32/[1]/contiguous/same CUDA device without a
host read. Its `[0, M]` value range is a documented caller precondition; keeping
that check on the caller avoids a stream synchronization or graph-capture break.
The MoE caller supplies routing's existing device `total_num_padded_tokens`,
which covers the complete contiguous local expert-tile prefix, including each
expert's padding, and is bounded by the allocated worst-case permuted capacity.

The kernel reads the count after the PDL wait, then rounds only the SF row
extent to the selected 128/8/1-row atom. It quantizes every live row and zeros SF
padding through the final atom. The remaining capacity is intentionally
unspecified and is outside the GEMMs' active tile prefix. The no-local count of
zero skips all row bodies but still runs PDL startup publication. Tensor output
shapes and the downstream SF view conversion remain capacity-based and unchanged.
Rubin's localized path rejects per-token scales before this call; no localized
workflow is newly enabled. The generic per-token path uses the same routing
prefix contract on both architectures, with no new model/tiler branch.

## Initial quantizer and PDL

The public `fp4_quantize(..., per_token=True, backend='cute-dsl')` caller omits
`valid_rows`, so initial quantization still covers every input row. The bounded
grid applies to both initial and intermediate invocations. Grid size is the
minimum of padded capacity and SM count times the existing minimum residency
budget; it is runtime launch geometry, not a model-specific compiled policy.

The existing dependency wait, CTA0 ancestor publication and per-CTA startup
signal remain once per CTA before the row loop. The downstream dependency wait
continues to protect unfinished quantized output; signaling does not promise
that output is ready. The initial quantizer can therefore admit later startup
work as before, while the intermediate quantizer consumes the routed live count
only after its producer dependency completes.

`block_reduce` has a write-to-read CTA barrier but no read-to-next-write barrier.
The new unconditional end-of-row barrier supplies that missing protection before
the shared reduction scratch is reused. Row index and live/padding choice are
uniform within a CTA, so both real rows and SF-padding rows reach the same final
barrier. Register-resident and two-pass row arithmetic, 64-bit row addresses,
4over6 ordering, folded output scale and padding logic remain unchanged.

## Compilation and cache identity

The `functools.cache` entry includes `has_valid_rows`. Persistent kernel names
separate `per_token_validrows` from `per_token` and already encode dtype, K,
layout, PDL, fast-math, quantization recipe, folded output scale and CTA width.
The count value, input row count and grid size remain runtime arguments and do
not create shape-specific kernel specializations. The changed ordinary variant
ABI is safe against old persisted objects because `extra_key_files` includes
the quantizer source itself, and the persistent cache hashes/invalidate those
sources. Separate source-private caches used by the campaigns remain appropriate.

## Shared empty ownership

Both full barriers are retained; only their identical UMMA empty lifetime is
shared. The caller uses matching stage counts, state phases, consumer groups,
CTA groups and local/0b11 masks. All SF writers acquire the owner's empty phase;
warp zero keeps the TMA acquire and startup-prefetch bookkeeping. Local SF full
waits, async-proxy fence, two-CTA join and payload expected-byte counts remain
unchanged. The sole owner release follows both channel MMAs, and owner-only tail
waits every stage before the existing whole-CTA teardown barrier. This is
unchanged by the quantizer's live-row traversal because no GEMM routing count,
physical stage layout or producer/consumer policy changed in that component.

Bounded evidence is source-paired: the shared-empty gate now covers 126 exact
replays and 84 core variants per source, including M512/two-channel; the row-grid
gate separately covers 124 direct quantizer and 80 public-chain replays per
source. This audit does not substitute those separate component gates for the
parent's planned final combined run.
