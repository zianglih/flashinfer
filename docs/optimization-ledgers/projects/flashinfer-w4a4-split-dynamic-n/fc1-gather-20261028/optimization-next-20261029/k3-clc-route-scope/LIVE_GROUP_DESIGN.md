# Dynamic Gather4 group-loop design audit

Analysis only. No kernel, tactic, API, cache policy or source review clone has changed.

## Existing references and obstacle

- Rubin's gather epilogue-fused GEMM caches every row ID in a per-thread register tensor before K, then unrolls its Gather4 groups (`rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1973–2078`). It does not solve dynamic register indexing.
- SM100 MegaMoE loads interleaved eight-ID runs with256-bit loads before K, then unrolls runs and guards live runs (`moe_ep/kernel_src/sm100/next_cutedsl_megamoe/src/sources/kernel_src/blackwell/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:1150–1255`). This preserves mapping work outside K and spreads short groups across issuers, but copying its unrolled predicates would repeat the already rejected approach.
- Current retained gathered FC1 has one static `row_ids` tensor with four coordinates per group (`blackwell/moe_swap_ab_kernel.py:3524–3557`). Indexing this tensor by a runtime loop counter can become local memory or a large selection network. A dynamic loop alone is therefore insufficient.

## Lane-held coordinates avoid dynamic register-array indexing

Give each warp lane one decoded row ID, or two for the largest one-CTA tile. Keep those IDs distributed across lanes for the entire K loop. For each live group, broadcast the four desired lanes with four warp shuffles, then let the elected lane issue Gather4. The coordinate fetch/division remains outside K; only shuffles and simple shifts are repeated inside it.

Compile-time geometry:

```
b_rows = route_tile / cta_group
row_warps = min(4, b_rows / 4)
row_grain = 4 * row_warps
parallel_k = 4 / row_warps
id_banks = ceil_div(b_rows, 32 * row_warps)  # one or two for all current tactics
```

A lane's cached local row in bank `b` is
`((8*b + lane//4) * row_warps + warp%row_warps) * 4 + lane%4`.
Add the dynamic CTA row offset before looking up and dividing the token mapping.
Load only if that local row belongs to the live MMA extent and the global row is valid; otherwise retain the existing descriptor-OOB row sentinel.

Per-tile dynamic values, computed before K:

```
live_rows = round_up(valid_tokens, 8 * cta_group) / cta_group
live_groups = ceil_div(live_rows, row_grain)
copy_rows = live_groups * row_grain
```

Within each K stage, loop over `group=0..live_groups-1`. The coordinate bank is `group//8`, and four shuffle lanes are `(group%8)*4 + [0,1,2,3]`. For the two-bank case, select the bank with a predicated scalar select before shuffling; never dynamically index a register tensor. All lanes execute the shuffles before `elect_one`; returned coordinates are warp-uniform.

The smallest two-CTA tile has only8 B rows. `row_warps=2` handles this without writing16 rows into an8-row allocation; the other warp pair can own another K chunk when K-step8 is selected. All other geometries keep four row issuers. K chunk distribution remains compile-time integer arithmetic and a bounded eligibility test, not a new tactic or shape heuristic.

## Synchronization and storage obligations

- Announce `copy_rows * tile_k * activation_bits / 8` payload bytes on the existing local129-arrival gather barrier. The SFB cp.async work,128 completions, CTA-group publication and MMA stage release remain unchanged.
- `copy_rows` is rounded to a warpgroup issue grain but never exceeds physical B rows. It covers every dynamic-MMA row. Any extra gathered row uses the OOB sentinel, so correctness does not depend on stale shared contents.
- Keep the original physical shared stage/K strides; reducing transfer count must not compact the B layout.
- No new shared-memory metadata, named barrier, producer/consumer state, additional synchronization or dtype/model branch is required.
- `check_live_group_mapping.py` exhaustively verifies2,976 indexing cases: all five route widths,1/2CTA, every live count and1/2K chunks. This proves ownership/coverage/physical bounds only, not actual CUDA synchronization or performance.

## Likely tradeoffs and gate

The design removes per-group runtime branch expansion and the large warp-uniform ID set. It pays four SHFL instructions per Gather4 per K step plus one dynamic loop, which may lose on full tiles or short reductions. Two-bank selection must compile to compact scalar selects, not branch or local-memory indexing. It should not be retained solely for fewer padded transfers.

Before any timing: inspect actual SASS/local storage for K3 EP N128/N256, a largest one-CTA tile and the narrow two-CTA tile. Require no local-memory regression, a compact loop, constant bank accesses and warp-uniform TMA coordinates. Then an exact existing coverage gate must include one/twoCTA, narrow/full/partial N, both K steps and four formats. Only then measure fixed-winner real/balanced K3 and a broader EP/TP screen. No source implementation is authorized by this analysis note itself.

## Separate CLC capacity observation

The tight worst-case route capacity is `(tokens*top_k + (tile-1)*local_experts)//tile` (`moe_utils.py:145–176`). K3 EP8 T8192 with896 experts,112 local andtopK16 allocates1,135 N128 route slots versus185 live, and623 N256 slots versus112 live. For FC1's24 channel tiles, that means27,240 versus4,440 and14,952 versus2,688 logical cluster tickets:83.70% and82.02% are padding. FC2 has14 channel tiles and the same fractions.

The CLC launch uses capacity, while the scheduler tests device-known live routes and still drains canceled padded tickets (`kernel.py:2493–2522,2881–2925`). Early-rejecting initially padded clusters could reduce setup, but resident clusters still drain padded tickets. Cancellation order is unspecified; observing one invalid route does not prove that no valid ticket remains. No unsafe early stop or average-load launch bound is justified. This is an independent profiling direction, not a proposed fix in the Gather4 experiment.
