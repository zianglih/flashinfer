# Reuse bulk epilogue token-scale shuffles

Rejected source experiment based on `e2728a290`. The owned inactive review clone was removed after confirming its only modification matched `source.patch`; local harnesses, source identity and raw evidence remain. This was isolated from the concurrent scatter-metadata preload experiment.

In the existing bulk FC2 per-token path, consecutive pairs `i` and `i+2` share the same token pair and scale register: both use `(i//4)*8 + (lane%4)*2` and `scales[group*(tokens//32) + i//16]`. The prior inline shuffle operations were emitted twice in PTX. The candidate steps the outer compile-time loop by four values, computes the scale pair once, and applies the same two original packed multiplications in a nested compile-time loop. The row/lane ownership, arithmetic rounding, TMEM loads, conversion, output ordering, resource allocation and synchronization are unchanged. It adds no shape policy or autotune axis.

The change is one source line net (+5/-4). The bounded public-wrapper source-pair gate exercises per-token output at N128/one CTA, N128/two CTA and N256/two CTA with PDL on/off and changing/empty/reactivated routing. PTX/SASS and allocation receipts distinguish actual instruction reduction from source expressions. No dedicated upstream tests or sanitizer runs are added. Native public timing uses the saved source-bound winners and the established ten-warmup/100-sample cold-L2 CUPTI C-A-A-C comparison, including the NVFP4 input quantizer.

## Final result

Rejected: ptxas already common-subexpression-eliminates the duplicate scale shuffles. PTX expressions fall, but SASS SHFL counts remain 34 for N128 and 136 for N256. N128 registers grow by zero to two; N256 registers fall 144→128 (PDL off) and 146→131 (PDL on). No spills. All FC1 SASS is byte-identical. The 48 paired exact replays passed.

The four-model, eight-cell frozen-tactic C-A-A-C screen is effectively neutral: geometric mean 0.999386× (−0.061%). V3 per-token T16384 is −0.402%; the other cells range −0.140% to +0.069%. That result does not justify additional source structure for an optimization already performed by ptxas. No production source, tactics or public benchmark result was changed.

`timing-summary-final.json` contains all medians/drift; `timing-evidence/` retains all sixteen frozen phase receipts and 3,200 original CUPTI samples. Archive SHA256: `f3a68f5db446d2c975721f1c09e559a0d7c0d04dad3a23d3ad4e9d5c3e606aaa`. `codegen-summary.json` and `evidence/` retain codegen and gate evidence.
