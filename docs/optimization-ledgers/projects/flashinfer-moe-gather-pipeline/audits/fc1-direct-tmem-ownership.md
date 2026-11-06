# Direct native TMEM ownership for FC1: close without another prototype

The general no-FP32-transpose approach was already implemented, numerically qualified, and rejected under the dedicated gather warpgroup. The specific `Ld32x32 + redux` mapping is different and has not been measured in the inspected FC1 history. It is legal, but it does not provide a demonstrated simpler way to satisfy the existing gate, scale, and output-store contracts. Do not reopen the broad mapping merely by substituting a reduction opcode.

This read-only audit binds retained `2b8eb9d8`, swap kernel SHA `482b636a1714486e2ffb34c8ae005da3cef26f25f0ce034ba1eb59c6198d6276`. [Source hashes and CPU ownership check](fc1-direct-tmem-ownership.json) cover the current source, CUTLASS copy traits, and historical evidence. No source change, compilation, or GPU run was made.

## What the current transpose buys

`moe_swap_ab_kernel.py:411–504` loads each 16-row ×32-token fragment and transposes it through the already-owned accumulator TMEM. Its result is **one token per lane, 16 adjacent channels per register fragment**. Uniform-alpha gated FC1 activates first, then transposes one fragment. Per-token gated FC1 transposes both up/gate fragments before applying the token-specific alpha. ReLU2 owns both consecutive channel halves after the transpose (`:858–1023`).

This makes SF16's maximum and output conversion local to one lane. Gated SF32 joins the maxima of adjacent warps through the existing shared scratch and two barriers (`:697–716`). Nongated SF32 has both halves locally and needs no cross-warp join. Current gated payload stores carry16 adjacent values; nongated stores join32 converted values using the retained integer carrier. Thus FP4/FP8 achieve useful vector stores; per-token BF16 keeps its token alpha and contiguous channels local. Accumulator release remains after the final relevant TMEM read/fence, including overlap boundaries.

## The previously tested direct-native design

Old-project evidence is under `../flashinfer-w4a4-split-dynamic-n/fc1-gather-20261028/optimization-next-20261029/`:

- `native-tmem-fc1-audit/PROPOSAL.md`, `rejected-native-kernel.py`, `QUALIFICATION.md`, and `CODEGEN.md` bind candidate `6a48e87c` against retained9037. The source predates later accumulator-release and integer-store changes; its timings are historical causal evidence, not a measurement of current2b8.
- It used two native `Ld16x256.x4` loads, retained up16/gate16 weights, performed activation/quantization in native ownership, then shuffled packed words into eight adjacent channels ×two tokens per lane. It removed the FP32 TMEM transpose without SMEM payload staging or a new public layout. The cost was reduction/scale broadcasts, packed-output exchanges, and twice as many payload-store sites.
- **It did not use `redux.sync.max.u32`.** `_native_absmax` at lines815–834 uses a seven-SHFL reduce-scatter with selectors, leaving one scale owner per lane. All11 captured FC1 PTX files contain no `redux.sync`. Both arms have two plain SASS `REDUX` sites in the final UTCATOMSWS teardown region; those are not SF maxima. This distinction matters when searching opcode summaries.
- All39 paired exact cases plus two extra MX ReLU2/SF32 pairs passed. Matched resource guards caught and preserved two pre-existing wide-MX local-memory cases; the candidate did not worsen them. This was not an unqualified numerical failure.
- The fixed-tactic14-cell CAAC screen rejected the design. N3U EP16K W4A4 went from585.383/585.031µs to697.207/696.871µs (**−16.044%**). Per-token BF16 went from916.775/915.591µs to1107.881/1107.848µs (**−17.302%**). Both have tight repeats. All other rows, including gains and noisy cases, remain in `native-tmem-fc1-screen/RESULTS.md`.

The BF16 loss is especially relevant: this path does **not generate output SF**, so a faster maximum reduction cannot repair its packing/ownership cost. A representative BF16 ReLU2 native case grew from1676 to1797 non-NOP instructions, with48 added butterfly shuffles. Quantized ReLU2 cases also grew: NV1785→1915, MXFP84092→4954. These are compiled static counts, not attribution of individual operation latency.

## What changes with Ld32x32 and hardware reduction

CUTLASS `copy_traits_sm100.hpp:1624–1641` describes `32dp32b32x`: lane owns one raw row, register owns one token column. The CPU check enumerates all1024 values. This genuinely differs from the tested16dp256 ownership, where each lane owned two channels across eight token slots.

| Contract | Consequence of direct32dp32 ownership |
|---|---|
| Gated up16/gate16 | Paired operands occupy lanes separated by16. Activation needs a lane exchange or redistribution; simply using only the up half wastes the other half's arithmetic lanes. Assigning different token subsets to the halves is possible but needs that ownership handling. |
| SF16 | After correct gate pairing, a contiguous16-lane group can legally reduce one token. Nongated SF16 likewise uses separate half-warp groups. This is a simpler reduction mask than the old stride4 subgroup, not a free complete epilogue. |
| Gated SF32 | One warp's32 raw rows produce only16 gated channels. The other16 channels remain in the neighboring warp, so the SF32 exchange still needs cross-warp publication/reuse ordering. Changing the TMEM load atom or token count does not expand its row domain. |
| Nongated SF32 | All32 channels are in one warp, so a full-warp reduction is legal. |
| FP4 output | Neighboring channels now belong to different lanes. Nibble packing requires inter-lane communication; a nibble cannot independently update its shared output byte. Wider vector stores require further channel gathering. |
| FP8/BF16 output | Scalar channel stores can be coalesced, but consecutive registers are different token rows, not contiguous output addresses. Matching the retained vector-store widths requires redistribution or SMEM staging; avoiding that implies more store/address instructions. BF16 has no SF reduction to offset this cost. |
| Per-token alpha | Lanes hold many tokens. A token scale must be supplied per token slot before activation, using repeated/duplicated loads or broadcasts. The current one-token-per-lane alpha contract is no longer naturally local. |

`redux.sync.max.u32` is mathematically suitable **after** constructing nonnegative, NaN-filtered, +0-normalized FP32 maxima: their unsigned bit ordering matches numeric ordering, including+Inf. Reinterpreting raw `abs` bits without filtering NaNs would violate current `_absmax` behavior. All participating lanes must execute with the same mask. It returns the maximum to every participating lane, not one distinct token maximum to each lane, so unique SF storage/scale ownership still needs organization. It also does not do packed activation, conversion, or cross-lane payload packing. [Official PTX redux and TMEM access rules](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-redux-sync).

Packed FP32x2 activation remains elementwise, so pairing different token slots is possible only with their correct individual alphas and unchanged operation order. It does not remove the gate exchange. A full32-token native load names32 FP32 registers per lane before pairing; staging smaller subsets may shorten lifetimes but adds traversal/issue decisions. There is no compiled register or instruction advantage established for this unimplemented mapping.

## TRTLLM precedent and current profile boundary

The historical `scripts/epilogue_codesign_audit/TRT_MAPPING.md` traces TRT native16dp256 loads, up8/gate8 ownership, shuffle reductions, quantized U8 stores into swizzled shared memory, and TMA output. It is not a direct canonical global-store design and not the current up16/gate16 weight contract. Its optional redux suggestion was explicitly unqualified. Its archived source is also not proven to build every selected current TRT cubin; it is an ownership precedent only. The earlier same-layout N16 native packing experiment was exact but neutral/slower (control/candidate0.997577×).

The fresh retained N3U EP16K PC capture, `profiling/n3u-ep-w4a4-16k/held-retained-2b8/pc-analysis.json`, binds4088 PCs to loaded ELF `19296983…`, with168 registers and LOCAL0. Its epilogue TMEM loads/stores have wait samples, but these are not a prediction that deleting them accelerates the end-to-end chain. The profile owner reports no contrary evidence to the previous tight losses. A large sampled wait, especially when later issue/memory work must replace it, is insufficient to reopen this ownership redesign.

Decision: retain the existing general epilogue. ExactLd32+redux is an unmeasured distinct mapping, not a previously failed exact binary, but no source/native evidence establishes a simpler complete replacement under the current contracts. Any renewed attempt would need a new concrete output-packing/ownership mechanism, not just a different reduction opcode or another dtype fallback.
