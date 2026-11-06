# Epilogue ownership co-design

Read-only proposal against retained `aab93f854`, with source hashes and a symbolic proof in [ownership_receipt.json](ownership_receipt.json). No source mutation, GPU compilation, or new performance result. [TRT_MAPPING.md](TRT_MAPPING.md) contains exact published-source/measured-cubin boundaries and native-load coordinates.

The current up16/gate16 epilogue changes ownership from native TMEM lanes to lane=token/register=16 contiguous channels. `utils.py:203–279` uses two initial loads followed by three TMEM stores and five reloads for one gated, non-per-token transpose; per-token activation transposes up and gate separately before scaling. The resulting local16-value max and contiguous64-bit FP4 store are cheap, but the intermediate ownership conversion touches TMEM repeatedly. No independent stage is allocated: it overwrites the consumed accumulator rectangle, so physicalN must remain32 while this path exists.

The previous physicalN16 `e14d3300` path already removed all epilogue TMEM stores. It used two `Ld16x256.x2`,12 reduction shuffles and three packed-nibble shuffles. Its whole-kernel static instructions grew1144→1224 and full-chain results were mixed/sub-percent. Thus native TMEM loads alone are a closed optimization, not the proposed change.

## New ownership contract

Within **each** up16 and gate16 half, prepare physical row `r` from logical channel `phi(r)=2*(r%8)+r//8`, and permute the corresponding SFA rows identically. With native lane `L` and register `i`:

```
token    = 2*(L&3) + (i&1) + 8*(i//4)
physical = L//4 + 8*((i//2)%2)
logical  = 2*(L//4) + ((i//2)%2)
```

For group `g`, registers `j=4*(g//2)+(g%2)` and `j+2` now hold adjacent channels for **the same token**. Activation, scale multiplication and FP4 pair conversion can operate on that pair. Store its one byte directly to the canonical output channel address; no FP32 transpose or cross-lane nibble permutation remains. Output stays canonical, so FC2 weights/layout remain unchanged. The native output transaction footprint is unchanged: fourU8 stores issue four token rows×8 adjacent bytes each, versus oneU32 store for16 rows×8 bytes. Both are16 aligned32B sector requests per warp/N16 slab. More store issues may erase the packing savings; codegen and timing must decide.

This is an explicit experimental prepared-weight layout, not a transparent narrow-N dispatch. Existing W4A16, large-N, and other consumers expect the old row order. Do not change the public preparation helper globally or reuse old cache identities. A narrow prototype can prepare tagged private weight/SFA copies once outside graph timing, then test a corresponding explicit kernel. Any retention needs all consumers of that prepared layout or a distinct declared layout/API identity.

## Remove work beyond the transpose

1. **One SF writer site per slab.** Every lane already owns all fourN16 (eightN32) token SF values. Let `owner_group=lane//4`; admit groups below`slabN/4`, locally select that group's SF, and store for `token=2*(lane&3)+(owner_group%2)+8*(owner_group//2)`. This assigns all16/32 token SFs uniquely without a shuffle. The olde14 code emits four long address/branch regions ending in U8 stores at0x25c0/0x2840/0x2ac0/0x2d60. Replacing them with one selected-SF store can remove repeated canonical-address construction. SF32 retains only the even channel-group writer.
2. **Pack the scale conversion.** The olde14 SASS converts eachE4M3 SF with duplicated operands at0x2000/2030/20e0/2130. TRT converts four scale values in two packed conversion instructions at0x55b0/55e0. Build the four scale values in registers, preserve the exact `(absmax*(1/6))*norm` FP32 rounding order, then use elementwise packed conversion. Do not import TRT's reciprocal/arithmetic rearrangement. E8M0 retains the existing round-up/code-zero helper rather than substituting anE4M3 cast.
3. **Reduction is a separate codegen gate.** The8 same-token lanes have mask`0x11111111 << (lane&3)`. A subgroup `redux.sync.max.f32` could replace each three-shuffle/three-max reduction. First filter local two-channel absolute maxima with zero, preserving the current all-NaN→zero and +0 conventions. Official [PTX redux](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-redux-sync) supportsFP32 onSM100a fromPTX8.6 and requires every mask participant to execute with the same mask. Noncontiguous subgroup lowering/throughput is unverified; TRT's actual8×stride4 helper deliberately uses shuffles. Do not assume one cheap hardware instruction from PTX syntax or make this a required first variant.

The parent-selected first screen **preserves the current prepared weights** and combines nativeN16 loads, the single SF-writer site, and proven earlier accumulator release. The within16 `phi` permutation/direct-pair stores above are a future coordinated direction, because their prepared-weight identity affects all consumers and four byte-store sites may offset the packing savings. SubgroupREDUX is also a separate unverified codegen lead. Avoid a large Cartesian product of load/reduction/store choices.

## N16/32/64 and numerical boundaries

- N16 uses16-token native loads; N32 uses32-token native loads; N64 uses two32-token slabs. This preserves the current SF32 cross-warp exchange count forN32/64 instead of doubling barriers through16-token subdivision. TMEM physicalN16 is possible only after every epilogue read and lifetime calculation stops requiring32 columns.
- Within16 row permutation preserves the members of everySF16 block and every adjacentSF32 block. SF32 still needs the existing shared cross-warp maximum exchange; no extra handshake is introduced.
- All six supported input/SF families accumulateFP32 and share the coordinate argument. FP4 output stores an adjacent pair in8bits; FP8 in16bits; BF16/FP16 in32bits. The first performance experiment may useNVFP4/SF16, but that does not establish the other format branches.
- Per-token alpha must index `token_mapping[route_start+token]//top_k` for each native token pair before activation. Do not use the physical lane as token, apply alpha after activation, or change metadata rounding. Per-tokenBF16 bypasses generatedSF but retains canonical output ownership.
- Keep exact SiLU/GEGLU/SiTU/clamp ordering, signed-zero/subnormal behavior and current NaN conventions. Pairing changes which elements share packed arithmetic, not their scalar formula. ReLU2 has no up/gate halves and requires its own declared row mapping; it is excluded from a gated-only first prototype.
- Gate invalid-token stores independently; reductions must never mix tokens. Keep all lanes participating in collectives even for partialN. No SF groups may cross a token or a channel tail.
- Direct loads allow accumulator release after the final TMEM read, before activation/quantization/store, but that lifetime change must preserve the normal completion wait and overlapping-window protocol. It is a separate proven boundary, not permission to remove SF proxy ordering.

The [CPU proof](prove_ownership.py) checksN16/32/64,1,260 partial-route/address cases,1,792 uniquely owned symbolic elements, uniqueSF writers, within-token reduction groups, and canonical per-token identity. It does not prove floating arithmetic, CuTe lowering, resource use, or performance.
