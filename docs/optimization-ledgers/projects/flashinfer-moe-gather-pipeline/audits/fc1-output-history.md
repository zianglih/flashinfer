# FC1 payload-store history and current ownership

The earlier blanket FC1 payload-TMA policy is a closed, negative experiment. A much narrower possibility remains: nongated FC1 already owns two adjacent 16-channel fragments in each lane, but stores them separately. Joining only their converted payloads could remove a store instruction without changing ownership, scales, staging, or synchronization. This is a source/codegen hypothesis, not a measured optimization.

## Exact prior payload-TMA experiment

Old project: `flashinfer-w4a4-split-dynamic-n/optimization-20261028/swap-ab-hybrid-output/`.

- Base: `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8` plus padded-output R2. The FC1+FC2 candidate was `fc1-02`, kernel SHA256 `a813327258e82661070dc6ca9efff6e366282969d1459131a518907ba23723dc`. Its contemporaneous FC2-only control was `fc2-01`, SHA256 `aff286440591dec41bca64a78f27515dd5f6c1563f02c87b8702f89e03755b5a`.
- Complete FC1 slabs used shared-memory payload staging and TMA: up to 32 tokens by 64 gated or 128 nongated channels. Partial payload and all scale factors kept direct stores. FP4 used a byte-oriented TMA descriptor. The per-token arm still emitted BF16 for the existing standalone quantizer.
- The FC1 arm passed 384 exact graph replays; 48 captured GEMM compilations had no spills. This was not a full activation/output-dtype matrix or sanitizer run.
- The direct incremental comparison against FC2-only was **−0.5532% across 13 cells**, **−0.0579% decode**, and **−0.8615% prefill**. N3U EP MXFP8 T4096 was −2.69%; N3U TP per-token T4096 was −2.75%. Both N3U cases kept their MMA geometry and operand-stage counts, so their loss was not caused by reduced operand depth.
- Two six-phase screens used 100 strict CUPTI graph/cold-L2 samples and 10 warmups. Each arm's latency was the arithmetic mean of its two phase medians. This differs from the present compact screen's geometric aggregation. The percentages above were independently recomputed from the saved phase medians in `perf-summary.json`; this audit did not replay every historical raw sample.

This experiment predates the dedicated input-gather warpgroup. Adding that group does not change the output ownership, nor remove the additional payload scratch, stores, fences, and waits incurred by FC1 TMA staging. No fresh evidence currently supports rerunning the same blanket policy.

## Later, also closed, ownership experiments

The post-gather `fc1-gather-20261028/optimization-next-20261029/native-tmem-fc1-screen/RESULTS.md` tested a different route: native TMEM ownership, shuffle-based activation/quantization ownership exchange, and direct output. Each lane wrote eight channels for each of two tokens, doubling store sites relative to the current 16-channel/token fragment. All 14 declared cells completed; N3U EP T16384 regressed **16.04% W4A4** and **17.30% per-token**, with low repeat spread. The general native epilogue was rejected.

The same post-gather ledger also rejected a shared-FP32 transpose implementation. Neither is the proposed adjacent-half store combination: that would retain the current TMEM transpose and lane ownership, and introduce no payload SMEM stage or shuffle exchange. A bounded search of these experiment designs/results found no recorded test of combining the already-owned nongated halves. That is not a claim that every historical source snapshot was exhaustively searched.

## Current emitted stores and coalescing

Current source: `flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py`, `_store`, `_store_converted`, and `_run_token_group`.

- `_store` converts 16 contiguous output values once. `_store_converted` caps each copy at 256 bits. Thus a fragment is 8 bytes for FP4, 16 bytes for FP8, and 32 bytes for BF16/FP16.
- After the retained TMEM transpose, a lane owns a token row. A gated warp owns 16 output channels per token. A nongated warp already owns **32 adjacent channels**, represented by `top` and `bottom`, and calls `_store` separately for the two halves.
- In row-major output, lanes of a warp write different rows. With the observed N3U TP row stride, each 8-byte FP4 store touches a separate 32-byte sector per active lane. Its adjacent half and neighboring warp can reuse sectors later, but those are separate issued warp instructions. This is an address/coalescing statement; it does **not** establish four times the DRAM traffic or a bandwidth bottleneck.
- All four profiled N3U TP W4A4 T16384 native captures (`47643`, `47853`, `48051`, `48182`) have identical FC1 cubin SHA256 `62b0469c7e97409ae92e55d9a402e2d4533db1deb2765fe53f6bdc28c2592f68`. Each has **16 `STG.E.64` payload sites** and **16 `STG.E.U8` scale sites**, matching PTX `st.global.v2.b32` and `st.global.b8`. The first payload pair is at PCs `0x4310` / `0x4390`; the compiler has not already merged it. Native resources are 168 initial registers, 384 threads, and zero local bytes. Static site counts are not dynamic instruction counts or measured costs.

The hashes, all store PCs, saved historical phase arithmetic, and a CPU ownership/address check are in `fc1-output-history.json`.

## Smallest distinct candidate

Preserve each half's activation, FP32 scaling, conversion, and scale-factor write exactly. Retain the two converted halves in one contiguous 32-element register view and issue the payload copy once:

| Output | Existing per-lane payload | Candidate ideal payload |
|---|---|---|
| FP4 | 2 × 8-byte stores | 1 × 16-byte store |
| FP8 | 2 × 16-byte stores | 1 × 32-byte store |
| BF16/FP16 | 2 × 32-byte stores | Still 2 × 32-byte stores |

This is useful by ownership and element width, not by model name. It applies to the existing nongated branch; gated output has only 16 values per lane and cannot use it without additional work. SF16 keeps separate scales for each half; SF32 keeps its existing joint absmax and single scale. The token predicate remains unchanged. The public FC1 wrapper already requires the nongated output dimension to be a multiple of 128, while each warp's base channel is a multiple of 32. Consequently a legal final channel group is either all 32 channels or out of bounds; a new runtime tail branch is unnecessary. The independent `nongated-fc1-store-legality.md/json` audit passed 210,944 CPU checks and verified the existing 32-byte output-pointer alignment and compatible row/channel strides. If the copy helper is generalized, its fused-finalize branch must preserve the existing pairwise atomics.

Qualification, if authorized, should first check that the compiler emits the intended wider stores, does not add local memory or significant instruction/register overhead, and preserves exact payload/SF/output. Only then run a small frozen-tactic screen. A wider copy may extend the first converted half's lifetime or introduce packing moves, so source-level store reduction alone is not sufficient. No 64-token FP32 batch, new warp role, TMA output stage, or shared-memory transpose is proposed.

No repository source was changed and no GPU work was run for this audit.
