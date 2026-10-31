# Merged PR7290 fresh validation and performance

Source `a620ce7790b32f7f0ae524a811417d2c6cee1152` passed seven existing exact smoke calls, with 21 captured native kernels at LOCAL0. The full 31-job/two-pass campaign completed in 8.35 minutes.

- Fresh 468 cells / 396 retention cells / 93,600 strict CUPTI samples; both raw phase medians are preserved.
- All 1,088 loaded resource records pass existing LOCAL0/pool/compiler checks; 40 recorded-default W4 stage joins pass.
- Full 13,245-file source pre/post and current046 release ELF/Ninja/no-op checks pass. All 8 GPUs are idle.
- 98 clock-exception quartiles and 1 missing quartile remain recorded out of 3,744; maximum repeat spread 8.620823%. No row was dropped.

Raw: `evidence/pr7290-retained-refresh/1793416383526763000/data`. Report: `evidence/pr7290-retained-refresh/1793416383526763000/report`. Archive SHA256 `caa296c41a1b79402882224ff7806e7a4d71253e7ef2c26a7662df22d82f7e88`.

The candidate is fresh at the actual merge commit. Comparisons against reused TRTLLM, legacy and pre-PR W4 baselines have a historical-runtime boundary; this AA run is not a paired causal comparison. No source optimization, retuning, baseline rerun or rescue repeat was performed.

Largest repeat spreads:

| Job | Backend | Tokens | A1 us | A2 us | Spread % |
|---|---|---:|---:|---:|---:|
|tp-kimi-k3-w4a16|CuteDSL W4A16|8192|1201.927|1305.543|8.620823|
|ep-kimi-k3-mxfp|CuteDSL MXFP4x8|16384|1027.860|950.375|8.153150|
|ep-kimi-k3-w4a16|CuteDSL W4A16|8192|933.810|1004.549|7.575367|
|ep-v3-w4a16|CuteDSL W4A16|8192|564.243|601.667|6.632698|
|ep-v41-flash-mxfp|CuteDSL MXFP4x8|16384|839.208|789.399|6.309737|
|ep-v3-mxfp|CuteDSL MXFP8|16384|690.037|732.070|6.091412|
|ep-v41-flash-mxfp|CuteDSL MXFP8|16384|1012.953|962.393|5.253571|
|ep-kimi-k3-w4a16|CuteDSL W4A16|4096|553.169|579.251|4.714920|

The complete raw matrix, phases, component extensions, resource records and clock windows are in the report; publication owns historical denominator joins.
