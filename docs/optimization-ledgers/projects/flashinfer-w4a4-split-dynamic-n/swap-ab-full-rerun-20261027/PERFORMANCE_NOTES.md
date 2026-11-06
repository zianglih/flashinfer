# Final fresh benchmark observations

Source: current `e2728a2908f38cbcfa997c031bea059e3724ccde`, with same-head
`swap_ab=False` controls except W4A16's pre-PR
`002529e17b22567a071091053c6c4dc2a55e050e` control. All figures below exclude tokens
1 and 2. Positive percentages mean faster swap-AB, using baseline latency divided
by swap-AB latency minus one. Ratios use paired geometric means of pass medians.

- Versus same-head non-swap blockscaled modes: all 112 supported decode cells
  improve; geometric mean +19.24%. Prefill is +5.43% across 42 cells, with 26
  positive cells.
- Versus matching TRTLLM modes: decode +3.97% across 112 cells, 97 positive;
  prefill +6.44% across 42 cells, 37 positive.
- W4A16 versus pre-PR: decode -0.10%, prefill +1.15%.

Remaining non-swap prefill gaps include V3 MXFP4x8 at 16384 tokens (-14.41%),
N3U W4A4 at 16384 (-12.83%) and 4096 (-10.59%), and V41F W4A4 at 16384 (-8.37%).
The largest TRTLLM decode gaps are K3 MXFP4x8 at 64 tokens (-1.98%), V41F MXFP8
at 128 (-1.36%), and K3 W4A4 at 64 (-1.24%). These measurements do not support
claiming that all performance gaps are closed.

Strict assembly verified all 69 phases, 676 AUTO medians and 1352 frozen medians,
each with 100 CUPTI samples. Summary comparisons use the 135200 frozen samples;
AUTO measurements are not included in ratios. Input hashes, clean current source,
pre-PR benchmark-only changes, native winner cache entries, matched routing, and
verbatim printed CSV values were checked. The independent audit recalculated all
352 visible numeric cells from raw phase results and verified all eight A2 CSV
blocks plus displayed raw medians. Unsupported K3 pairs account for the other
44 visible cells.

Artifacts: `assembled/summary-table.md`, `native-a2-output.md`,
`raw-pass-medians.md`, `summary-cells.csv`, `frozen-pass-medians.csv`,
`performance-summary.json`, and `provenance.json`. Original data and all 100
samples per measurement remain under `evidence/`; superseded attempts are not
used. This final campaign replaces the previous historical timing summaries.
