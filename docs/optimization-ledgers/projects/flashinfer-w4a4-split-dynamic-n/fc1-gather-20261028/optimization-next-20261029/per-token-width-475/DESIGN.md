# Compile-time CTA width for narrow per-token quantization

One unstaged file in `flashinfer-per-token-width-review`, based on retained475cae6b. No MoE kernel, PDL, arithmetic, scale layout, native tactics, test oracle, or public interface changes.

The quantizer owns one16-element block per lane in a register-resident load/reduce/quantize sequence. Its existing minimum128-thread CTA is unnecessarily wide when K<2048. For K640,40 lanes own real blocks while88 lanes reload the last block only to participate in amax reduction. Compute the initial width as `min(128, round_up(K/16, 32))`; then preserve the existing small-M width growth and large-M register-budget calculations. K≥2048 remains unchanged. The allowed width is any full-warp count from32 through the existing512 maximum.

This enables32/64/96-thread CTAs according to useful SF blocks, without new tactics or model-specific thresholds. The existing grid cap and occupancy hint both derive from `1024 // threads`; the row traversal, valid-row/group limits and scale-padding policy remain intact. At K640, the grid changes1184→2368 CTAs on148SMs, and active-prefix rows perCTA approximately halve. At K1536,96 useful threads avoid a completely idle fourth warp.

`block_reduce` supports arbitrary1–16 warp counts: each warp publishes one value, the CTA barrier orders publication, lanes below `warps_per_row` load real values and remaining lanes contribute the identity before a warp-wide reduction. Amax is order-independent for the finite inputs tested. Both the write→read barrier and end-of-row read→next-write barrier remain; the prior row-grid ledger specifically requires the latter. Single-warp reduction could be simplified later, but it is outside this isolated candidate.

Prior bounded-row-grid optimization (`scripts/row_grid_quantizer_20261026/README.md`) retained the same traversal with strong prefill gains. This candidate does not undo it. No previous short-row CTA-width experiment was found in the relevant quantizer ledger. Wide combine/vector-outer variants are unrelated and remain rejected.

Qualification:80 existing bit-exact quantizer/MoE cases, plus a private source-local128-thread-vs-default comparison across BF16/FP16, K16/80/512/528/640/1024/1040/1536/1552/2048/7168, all SF layouts, PDL on/off, changing live counts and routed holes. Fresh diagnostic cubins must show zero stack/local instructions. Diagnostic compile flags are isolated from performance: normal production compiler/cache settings are used for fixed-tactic CUPTI end-to-end timing.
