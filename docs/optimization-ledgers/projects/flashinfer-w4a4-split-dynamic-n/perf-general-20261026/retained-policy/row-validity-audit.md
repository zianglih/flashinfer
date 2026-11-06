# Read-only audit: skipping padded intermediate rows

The routing map's sign is **not** a valid padding predicate. `moe_utils.py:713` allocates `permuted_idx_to_expanded_idx` with `torch.empty`; `RoutingKernel.cuh:542` writes it only for actual local routes. Routing's `initRoutingTilePadding` helper (`RoutingKernel.cuh:172`, called at485/792/1174 and from the custom routing variants) initializes only `mPtrPermutedIdxToTokenIdx`. The CuTe `moe_sort` binding sets that pointer to nullptr (`csrc/moe_utils_binding.cu:394`) while supplying the expanded-index map. Therefore unused map rows can contain any value, including nonnegative stale entries.

The existing safe predicate is:

```python
row < total_num_padded_tokens[0] and row < tile_idx_to_mn_limit[row // tile_size]
```

Read the device count and limit only after the PDL wait, and never read a limit for a row beyond the active count. `blackwell/moe_prepare.py:121` already uses this exact live-row contract. Routing writes each limit as the minimum of the tile end and actual expert/route-window end (`RoutingKernel.cuh:474-485`). It covers small block/cluster routing and cooperative/contiguous route windows, including more than one padded tile per expert.

A generic optional device tensor of exclusive row limits, with an explicit compile-time rows-per-group parameter, can expose the same contract to the quantizer. The initial quantizer's absent specialization remains unchanged. The inter-FC call can pass its existing `tile_idx_to_mn_limit` and `tile_size`; no new routing buffer, sentinel initialization, host count synchronization, or sort change is needed. No model, dtype, or activation-specific condition is needed.

For an invalid interior row, skip the BF16/FP16 payload read, amax, 4over6 decisions and quantization; write zero to its scale factors. Preserve zero SF through the outer final128/8-row physical atom, using the existing layout offset helper and padded SF-column count. **Interior holes need zero SF for the linear layout too**; the current outer-padding branch omits linear SF stores only because linear layout has no outer padded rows. Packed FP4 payload can remain untouched: every E2M1 nibble is finite, and zero SF suppresses that lane. No valid row arithmetic changes.

FC2 computes `valid = min(route_tile, mn_limit[route_idx] - route_start)` in static scheduling (`blockscaled_contiguous_grouped_gemm_finalize_fusion.py:1583/1814/1948`); CLC publishes the equivalent `scheduled_valid`. The epilogue guards metadata/per-token-scale reads and output stores by this count (`blackwell/utils.py:1050-1076`, and the corresponding bulk path at810-818). Thus invalid interior-row per-token scales are not consumed. They may remain undefined under an explicitly documented invalid-row contract; writing zero from one lane is also safe but not required by current FC2. Both one/two CTA and dynamic MMA N can read rounded payload/SF lanes, so defining SF zero remains necessary even though epilogue output is masked.

Keep the existing end-row CTA barrier on invalid-row iterations as well: a CTA may alternate valid and invalid rows under grid stride, and shared amax scratch reuse must remain ordered. PDL launch publication stays once per CTA before traversal; all optional metadata reads follow the dependency wait. Changing routes/counts during graph replay must work without any compile-time assumptions about which groups are partial.

Recommended bounded gate before timing: fill all routing-map padding with a positive poison (to prove it is never used as validity), run sparse/partial/full/empty and changed graph routes across N16..256, one/two CTA, CLC/static and PDL on/off; compare only live quantizer rows plus final public MoE output exactly to the frozen control. Check SF zero at all interior invalid rows and through the final physical SF atom. Existing direct quantizer defaults should remain unchanged. No source edits or GPU launches were made for this audit.
