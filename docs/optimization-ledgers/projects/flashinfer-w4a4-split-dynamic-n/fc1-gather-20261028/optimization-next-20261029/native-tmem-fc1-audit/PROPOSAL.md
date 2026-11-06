# Native-TMEM FC1 epilogue: feasibility proposal

Read-only against `9037f6d46fcb45eac04be04c182104336c8b1e7c`; no source clone/edit, GPU compilation, or timing. `source.json` binds the exact kernel, and `mapping-proof.json` records the CPU proof. FC2, prepared weights, API, tactics, stages, register budgets and scratch allocation remain unchanged.

## Prior evidence and distinct scope

The old `scripts/narrow_ld256_epilogue_experiment/README.md` candidate was an N16 gated FP4 dispatch: numerically exact in its bounded scope, decode ratio0.997577x, rejected. It already used native loads and packed bit transpose. Those mechanisms are not new. The `scripts/epilogue_codesign_audit/EPILOGUE_DESIGN.md` weight-permutation proposal is also excluded: this candidate must preserve the existing up16/gate16 contract.

The justified new experiment is one N32-slab FC1 epilogue for every existing activation/output format, under the current dedicated256-register epilogue group, with a reduce-scatter scale owner. Current trace evidence identifies load plus TMEM transpose scopes as a substantial epilogue component; instrumentation does not establish recoverable speedup. The new question is whether removing that traffic beats shuffle, selector and store-issue costs on prefill and all output widths.

## Coordinates and packed words

For `Ld16x256.x4`, lane `l` and register `i` in0..15 own:

```
token   = 2*(l&3) + (i&1) + 8*(i//4)
channel = l//4 + 8*((i//2)&1)
```

Load up16 and gate16 from row offsets0/16. ReLU2 uses the same two halves as independent consecutive channels. The same slab is used at every N; minimum physical allocation remains32 and invalid-token stores remain predicated.

After activation and unchanged output conversion, represent each16-value fragment in Uint32 words. Exchange index bits0/1/2 with lane bits2/3/4. For width `b`, each exchange is a bit-mask butterfly when `b<<axis <32`; otherwise exchange the corresponding register-word bit with the lane bit using a static peer-word shuffle and select. The final owner is:

```
token       = 2*(l&3) + ((l>>2)&1) + 8*((l>>4)&1) + 16*(i//8)
channel     = 8*((l>>3)&1) + i%8
```

Each lane writes eight contiguous channels for each of two tokens:32/64/128-bit stores for4/8/16-bit output. This doubles store sites versus the current16-channel/token layout, but preserves the per-instruction summed32-byte-sector footprint for aligned row/channel strides. There is no SMEM payload staging. The generic proof also covers32-bit output, though the requested public FC1 arms use4/8/16 bits.

## Scale ownership without eightfold duplication

A naive native epilogue has eight token maxima per lane, each duplicated across eight channel lanes. Computing all eight scales and fetching eight adjacent-warp maxima would be an avoidable regression.

Instead, construct eight local two-channel maxima, with exactly the current zero/NaN filtering. Reduce-scatter over lane bits2,3,4:

1. Keep token-index parity matching lane bit2; combine the peer's corresponding half: four SHFL/MAX pairs.
2. Keep token-index bit1 matching lane bit3: two pairs.
3. Keep token-index bit2 matching lane bit4: one pair.

Every stage uses constant register indices and two lane-dependent selects per result; no dynamic rmem indexing. Seven shuffles leave one16-channel maximum per lane. Its token is `2*(l&3)+((l>>2)&1)+8*(l>>3)`, a bijection over0..31.

For gated SF32, write this value at `shared[warp,lane]`, retain the existing two128-thread barriers, and read `shared[warp^1,lane]` once. Adjacent warps have exactly the same token owner and neighboring16-channel groups. Thus shared footprint, write/read count and barrier count match current `_gated_sf32_absmax` (`moe_swap_ab_kernel.py:674`). One existing `_quantization_params` invocation per lane produces the unique SF and inverse scale. Store SF once with the existing padded-row expression. Broadcast each owner's scale to native token slot `j` from lane `4*j+(l&3)` (eight SHFLs) before the exact current multiplication/conversion.

For ReLU2 SF32, merge both local16-row halves before reduce-scatter: the complete32-channel group is in one warp, so there is no shared exchange. SF16 reduces the halves separately. These are existing semantic scale-group distinctions, not shape/dtype optimization dispatch.

## Exact arithmetic and lifetime

- Preserve `_quantization_params` (`:687`) byte-for-byte: NVFP4 standalone helper, E8M0 round-up/code-zero, MXFP4 rounding and saturation remain unchanged.
- Refactor activation into the same packed pair operation, pairing `i` and `i+2` (same token, channels separated by8). The scalar ordering of alpha, clamp, SiTU/SwiGLU/GeGLU/ReLU2 and final multiply is unchanged. Packed pairs are independent operations; exact device tests still required.
- For per-token alpha, retain one valid-guarded metadata load per lane in lane=token ownership, then broadcast to the eight native token slots before activation. Do not multiply alpha after activation. Reuse each broadcast across up/gate or the two ReLU2 halves.
- Keep all128 epilogue threads in the SF32 collectives even for partial tokens. Invalid tokens never mix into another token's reduction. Channel groups stay aligned to16/32 under the existing shape contract.
- Keep cyclic overlapping-accumulator traversal and its protected-slab boundary (`:980–1023`) unchanged. At the selected release slab, complete both native TMEM loads and `fence_view_async_tmem_load` before the same consumer release; activation/quantization/store can follow because they use registers/SMEM only. No release merely after the first half; no change to FC2 or final join/free.

## Static cost estimate per warp/N32 slab

These are algorithmic instruction sites, not compiled SASS or latency predictions.

| Work | Current | Native proposal |
|---|---:|---:|
| Gated uniform-alpha TMEM loads/stores |7/3|2/0|
| Gated per-token or ReLU2 TMEM loads/stores |12/6|2/0|
| SF16 gated reduction shuffles |0|7|
| SF32 gated shared writes/reads/barriers per lane |1/1/2|1/1/2|
| Scale calculations per lane |1|1|
| Scale broadcast shuffles |0|8|
| Packed transpose shuffles4/8/16-bit |0|6/12/24|
| Contiguous elements/store |16|8|
| Store sites per16-channel fragment |1|2|

Reduce-scatter adds up to14 selectors and7 maxima; naive replicated reduction would instead add24 shuffles/MAX sites and duplicate scale computations. Per-token alpha adds eight shuffles. ReLU2 SF16 performs reductions/scales for two fragments; ReLU2 SF32 shares one scale. BF16/FP16 bypass scale generation entirely but pay24 packed-word shuffles per16-channel fragment. This last width is a real risk; do not hide it behind fallback dispatch.

Raw operands need32 FP32 registers per lane; activation/reduction/conversion can be sequenced so only one output fragment's packed words remain live. The256-register quota is ample relative to these named fragments, but compiler liveness/activation temporaries are unproven. No quota change is proposed. N32, all widths, per-token SiTU and the widest overlap tactics need SASS/local-storage gates before timing.

## Proof and proposed next gate

`prove_mapping.py` exhaustively checks512 native coordinates, symbolic individual bits for4/8/16/32-bit packed output, reduce-scatter membership/unique SF writers, exact SF32 neighboring groups, canonical partial-token ownership for N16/32/64/128/192/256 (1,388 cases), padded SF rows, and affine M128/M256/M512 one/two-CTA channel coverage. It does not validate CuTe lowering, floating-point implementation or performance.

Feasibility: justified for one general isolated prototype. First compile representative FP4, MXFP8, MXFP4x8, BF16 per-token and ReLU2/gated SiTU, N16/N128/N256/M512 and overlap/CLC variants. Require no spills and unchanged FC2 binaries; inspect that scale computation/shared reads remain one per lane. Then existing bit-exact cases and focused prefill/decode CAAC across formats/models, with no sanitizer or new tactic axes. If the general packed/scale ownership is not concise or wide-output SASS is materially worse, reject rather than add dispatch exceptions.
