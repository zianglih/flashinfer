# Retained FC1 gather index/address audit

**No new prototype is justified by this bounded review.** Retained `2b8eb9d8` already caches routed payload coordinates outside K, batches coalesced scalar mapping loads across lanes, and keeps SF addressing independent. The remaining visible address/transfer work is not evidence of a removable duplicate.

- **Election is already shared in native code.** The current, source-bound N3U TP8/T16384 FC1 emits 16 Gather4 calls and 16 `elect.sync` sites in PTX. The loaded SASS has **one ELECT for all 16 Gather4 instructions**, with no local-memory access in the gather issue region. Moving the Python election scope outward therefore does not remove 15 native elections. The older W4 scope-hoist experiment added four instructions and a branch; it is not a reason to repeat the same source reshaping here.
- **Route decode and shuffles are already outside K.** The current issue region contains zero SHFL instructions. The cached coordinates are needed by the unchanged four-row/row-K issuing pattern; uniform-register transfers feed distinct Gather4 coordinate tuples. Narrowing their lifetime by reloading or reshuffling each K stage trades away this existing amortization. No new ownership-preserving duplicate was found.
- **Full-group task checks already disappear.** Current wide native evidence and the older task-guard compile experiment show the redundant full-group bounds are eliminated. The one narrow N16/two-CTA case legitimately has fewer payload issuers than SF workers; suppressing its unused payload setup needs an additional runtime warp predicate, excluded by this audit's constraints.
- **Arithmetic spelling has already been tested.** The prior swap unsigned-warp cast passed exactness but added 18 native instructions/two branches and was near-neutral/slower over 12 cells. The preceding modulo rewrite and explicit full-group condition likewise provide no new lead. Source-level shifts/masks are not a new optimization without a distinct native omission.

## What the local references establish

The regular Rubin gather kernel caches Int32 row IDs before K (`rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1982–2078`). Its outer election is a source-structure difference, not evidence of fewer elections in our native kernel.

Current Blackwell and Rubin Local MegaMoE mainloops (`moe_ep/kernel_src/{sm100,sm107}/next_cutedsl_megamoe/.../block_scaled_swap_ab_fc12_mainloop_gen_specialized.py`, around 1169/1195) also cache indices before K. Their 256-bit mapping loads own **eight-row runs**, and their gather-index plane already contains decoded source rows. Adopting that load or removing our `token_mapping / top_k` would change ownership or the routing layout contract; neither is an instruction-only handoff. Both current Mega mainloops still elect individually around Gather4 calls. They offer no additional address-cache simplification absent from our retained path.

The shared SF/payload-coordinate proposals, deferred SF offsets, dynamic live-row issue, and the newly rejected coalesced-SF lanes are explicitly excluded. Repackaging them as a register-lifetime change would repeat closed mechanisms.

## Evidence

`native-proof.json` binds all five source files, the loaded TP PTX/cubin/SASS and the exact PC region. `native-issue-excerpt.txt` preserves the inspected instructions. The original profile remains under `profiling/n3u-tp-w4a4-16k/retained-2b8/`; no new profile or timing was run.

Prior evidence remains unchanged in the earlier project's `fc1-gather-20261028/optimization-next-20261029/`:

- `swap-gather-taskguard/RESULTS.md`: byte-identical generated bounds simplification.
- `swap-gather-unsigned/RESULTS.md`: 12-cell/native rejection.
- `sf-payload-ownership*`, `sf-payload-deferred-offsets`, `sf-payload-linear-guard-typed`: coordinate/lifetime attempts.
- `../full-20261029/lane-metadata/AUDIT.md`: retained lane decode and the eight-row Mega ownership distinction.
- `../full-20261029/w4a16-elected-issue/RESULTS.md`: scope-hoist native rejection, not a latency claim.
