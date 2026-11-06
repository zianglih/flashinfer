# Native N16/SF16 epilogue ownership audit

CPU/read-only audit, 2026-10-25. Production HEAD is `aab93f854054de834447bdd8985b8bbd653fb3c8`. No source changes, CUDA imports, compilation, or GPU runs were performed. Paths below are relative to this project. The proposed change is a weight/epilogue layout co-design, not a claim of measured improvement.

## Source and binary identity

Published sources are the saved PR2917 snapshot `aleozlx/flashinfer@64ed071e23bf8d5d2d5af5c91577e5b8e036a1cf` in `scripts/trtllm_gen_decode_audit/sources/`; local hashes match `source-manifest.json`. The selected measured cubins come from artifact `8ee504560a86b6c72b8c941d3003e8fb1804b1b6/batched_gemm-fdba669-16ba8ed`, **not a demonstrated build of that published source**. See that audit's `README.md:7–9`, `profiles/selected-cubins.json`, and `profile-receipt.json`.

Aliases for long generated source names:

- **N16**: `sources/src/Bmm_E2m1_E2m1E2m1_Fp32_bA16_bB16_bC16_t128x16x512u2_s5_et128x16_m128x16x64_cga1x1x1_16dp256b_rM_TN_transOut_schPd2x1x2x3_biasM_bN_ldgsts_ldgstsSf_rgTma_clmp_swiGlu_dynB_sm100f.cu`.
- **N8**: `sources/src/Bmm_E2m1_E2m1E2m1_Fp32_bA16_bB16_bC16_t128x8x512_s5_et128x8_m128x8x64_cga1x1x1_16dp256b_rM_TN_transOut_schPd2x1x2x3_biasM_bN_tma_tmaSf_rgTma_clmp_swiGlu_dynB_sm100f.cu`.

|File / artifact|SHA256|
|---|---|
|N16 published source|`da1d7236c18eb97d72ff215f72659fc96a1b5b92d51e91a037bc1c86f3b14b2e`|
|N8 published source|`3ba19f7e99942ddd73fbc3fdcf19d98eadca72ec901952ff417933423f2673f3`|
|`sources/trtllm/dev/TmemTile.h`|`69d6e9ec9bfb70dba5cc3b178ab038cfadb3214ae8ebb1fabcd00f2500a48f62`|
|`sources/trtllm/dev/CutlassUtils.h`|`004ecf98ce7266fcc43c3a514ffc8807ceef491125d4bf915c1a60bd11a604a5`|
|Production `flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/utils.py`|`9811c53e0faa4ab39bc8dd3b03152498958938ff17761fdad57a0afae6ede889`|
|Production Blackwell `blockscaled_contiguous_grouped_gemm_finalize_fusion.py`|`7c0fe69faab5acecafdd3d67a157f016836e149fafdc29942542d44ef4852c66`|
|Production `flashinfer/flashinfer/utils.py`|`affbdae50486b23f5103efb1fe266a46953c3685b0b19c9b77a3bc47edf171c3`|
|Production `flashinfer/flashinfer/fused_moe/core.py`|`58ac4fb451361d79e395cd241dfaae0e2fc8d61f859e221fe571aff4d65c062a`|
|Production `flashinfer/flashinfer/fused_moe/prepare.py`|`d46e902d88b050e8fd9a8af661ec9503c2c1aade6e7f1e91ba8b39f404d30732`|
|Measured T32 FC1 cubin (manifest)|`2b3e9e7ae47da5b635a131064ef0551bdad1a195b17f3c9849af4af0b7f9528f`|
|`profiles/trt-t32-fc1.sass.txt` (locally verified)|`2abb29cf544af9fb6a429e2250f5555a74b5e1286b96bf0eb93573724399b405`|
|Measured T128 FC1 cubin (manifest)|`136753426c77774bb2a82f70312d43378d434857ba5d6dcc78aae8b158db09ba`|
|`profiles/trt-t128-fc1.sass.txt` (locally verified)|`b843a242a6b2cda6e8dc7c8d87b4a15f118c2f6b19b7b57d36daf812494bcd67`|

## TRT mapping, including its different gated-weight ordering

Let `l` be the lane, `g=l//4`, and `b=2*(l%4)`. A native N16 load has eight registers with token `b+(i&1)+8*(i//4)` and physical channel offset `g+8*((i//2)%2)`. `TmemTile.h:51–89` supplies these row/column rules; N16 `:3066–3082` loads row offsets 0 and 16 using two native 16dp256bit operations. N8 `:2290–2294` has four registers per half and only tokens `b,b+1`.

TRT's gated weight order is **not** our up16/gate16 order: N16 `:3283–3310` activates raw register pair `[0/1]` with `[2/3]`, so physical rows `g` and `g+8` are an up/gate pair. The +16-row load supplies the neighboring output channel, and `:3410–3413` compacts its activated results into slots 2/3 and 6/7. Post-activation ownership is therefore:

|Activated register pair|Token|Two logical output channels within this warp|
|---|---:|---|
|0,2|b|2g, 2g+1|
|1,3|b+1|2g, 2g+1|
|4,6|b+8|2g, 2g+1|
|5,7|b+9|2g, 2g+1|

The output-address constructor uses `mBaseRowIdx=16*warp+2*g` (N16 `:2910–2918`). Current TRT weight preparation independently corroborates a row-shuffle contract: production `flashinfer/utils.py:1043–1071,1097–1107` defines/inverts the 16-/32-row maps; `fused_moe/core.py:484–518` composes gated reorder with MMA shuffle; `prepare.py:600–620` applies matching permutations to W1 and its SF rows. These current host sources do not establish the exact host revision used to build the archived cubin.

For SF16, each lane first takes the max of its two channels for each token, then N16 `:3425–3461` calls `reduce_group_max_abs_f32<8,4>` four times. `CutlassUtils.h:833–872` deliberately selects the shuffle path for group size 8: XOR16, XOR8, XOR4, with an absolute-value/zero guard that filters NaNs. The fixed `l%4` subgroup spans all 16 output channels of one token. N8 `:2489–2493` performs two such reductions. The four epilogue warps together own 64 post-gate channels; an SF16 group does not cross warps. The `m128x16x64` MMA reduction-K shape is distinct from this 64-output-channel epilogue ownership.

N16 `:3469–3500` scales maxima, converts four SF values to packed E4M3, then decodes them. `:3506–3559` derives reciprocal scales. `:3565–3612` chooses one SF writer per token/group and stores TRT's SF layout. `:3639–3647,3664–3672,3689–3697,3714–3722` converts each adjacent-channel pair and writes four U8 values per lane into **swizzled shared memory**. `:3725–3751` fences, synchronizes 128 epilogue threads, and has one elected thread issue the TMA store. This avoids a floating-point TMEM transpose, but retains quantized SMEM staging and its lifetime protocol. Do not copy TRT's arithmetic placement, SF layout, or tail descriptors into our path without separate equivalence work.

Measured T32 N16 SASS corroborates the mechanism: native `LDTM.16dp256bit.x2` at PCs `0x4b30/0x4b40`; twelve `SHFL.BFLY` at `0x53f0–0x5540`; packed E4M3 conversion at `0x55b0/0x55e0`; four packed E2M1 conversions at `0x5a40/0x5a80/0x5aa0/0x5b00`; four `STS.U8` at `0x5c20–0x5c50`; `UTMASTG.4D` at `0x5d50`. There is no epilogue STTM in this region. Earlier STTM PCs `0x2710–0x2780` belong to a different phase and must not be described as an epilogue transpose. Measured T128 N8 uses native loads at `0x42b0/0x42c0`; its selected cubin is LDGSTS, whereas the N8 source alias above is TMA, so only the epilogue ownership analogy is claimed.

## Current path and closed alternatives

Production Blackwell `utils.py:553–575` loads up16/gate16. Uniform-alpha activation precedes one TMEM transpose; per-token scaling transposes both halves first. Afterward each lane owns one token and all 16 contiguous channels: local absmax `:455–459,585–586`, one SF and one 64-bit FP4 payload store `:475–529,587–598`. The transpose `:219–270` has three TMEM stores and five loads per fragment. It buys both local reduction and contiguous packing. `:576–580` releases overlapping accumulator/scratch ownership only after the final read and TMEM load fence.

The native-load/no-TMEM-transpose route is already closed: `scripts/narrow_ld256_epilogue_experiment/README.md:7–21` and `implement.py:19–35,70–138` preserve existing weight order, perform 12 scale-reduction SHFL plus 3 packed-nibble exchanges, and issue one U32 payload store per lane. T32 FC1 control/candidate ratio was 0.997577x. Its baseline utils SHA is identical to current production's hash above; this is not merely an obsolete epilogue. `scripts/physical_n16_experiment/README.md:5,21–24` additionally shrank physical N and was not retained. `scripts/epilogue_experiment/README.md:30` closes prior scalar-store, permuted-lane transpose, MOVM, and bulk-store variants; those are not producer weight-row permutation.

## Distinct producer/epilogue ownership proposal

Within each of **our** up16 and gate16 halves, map physical row `r` to logical channel `phi(r)=2*(r%8)+r//8`. Apply the same row permutation to W1 payload and all its SFA rows. The native pair at physical rows `g,g+8` then represents adjacent logical channels `2g,2g+1`. Both halves still pair correctly for activation; each SF16 group is unchanged as a set. This adapts TRT's adjacent-pair ownership without adopting its up8/gate8 ordering.

For each lane, retain four token values as the table above; directly pack each local adjacent-channel pair and store one byte at `(route+token, channel_base+2*g)`. Writing canonical logical channel order keeps the FC2 activation layout and W2 unchanged. Local permutation cannot eliminate the eight-lane SF16 reduction: it only removes the three packed-nibble cross-lane exchanges. Per-token alpha must still be looked up separately for `b,b+1,b+8,b+9` using the original token mapping, with the existing validity guard and arithmetic order. Keep the scalar `fmax(...,0)` guard so all-NaN blocks reduce to zero as current `_absmax` does.

This needs an explicit prepared-weight layout identity or backend-private preparation. Existing prepared weights are shared by other N values, dtypes, and W4A16 paths. Silently interpreting their bytes differently is invalid; any fallback needs the matching inverse ownership. SF row permutation operates before/through its canonical swizzle, not by assuming adjacent physical SF bytes are adjacent rows. No cache key, API, or source change is proposed in this audit.

**Store tradeoff, not a bandwidth claim:** per warp/N16, the prior route has one U32 store site over 16 token rows × 8 bytes = 128 useful bytes. The proposed direct route has four U8 sites, each covering 4 rows × 8 bytes = 32 useful bytes. With native aligned row strides at least 32 bytes and each eight-byte group contained in a sector, both sum to 16 per-instruction 32-byte sector requests per warp: one×16 versus four×4. Cross-warp/cache merging and partial valid rows need separate accounting. The proposal removes three SHFL plus their bitfield mixing but adds three store sites and potentially more address/predicate work. TRT instead uses shared-byte stores and TMA; its staging is not evidence that direct U8 global stores will win.

One optional reduction co-design is four subgroup `redux.sync.max` operations, one per token, with mask `0x11111111 << (lane&3)` and guarded nonnegative inputs. This is **not TRT precedent**: its helper explicitly chooses SHFL for `<8,4>`. Installed compiler lowering, subgroup participation, instruction cost, NaN behavior, and exact numerical equivalence remain unverified here. Packed SF conversion is a separate instruction-level option; it does not change the ownership proof.

The bounded next candidate, if authorized, should target native N16/SF16, preserve current arithmetic and canonical output, and measure the complete producer/prepack/epilogue contract. CPU address proofs, compile/SASS, bitwise active/tail/per-token checks, and matched full-chain timing are still required. This audit establishes a distinct ownership mechanism; it establishes no speedup.
