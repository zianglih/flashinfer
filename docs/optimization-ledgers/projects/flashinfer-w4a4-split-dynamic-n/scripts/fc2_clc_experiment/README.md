# FC2-only one-CTA CLC experiment

- Source copy: `flashinfer-fc2-clc-review`, unstaged one-line change from clean `0c1e00fc3e4f913c8c241796c70a29673737c542`.
- Only FC2's public call requests `use_clc_scheduler=cluster_shape_mn == (1, 1)`; metadata depth remains 1. Existing full-device budget, work-count and grid-Y guards remain unchanged. FC1, MMA/core code, tactic list and epilogue-overlap policy are unchanged.
- Source/patch receipt: `evidence/fc2-clc-r1/source.json`; patch `382050d796e160f01d9a996a73b7fdb03f574c5542946b064f683ec35f8255ee`.
- Gate: 16 paired static/CLC exact BF16 scatter cases across NVFP4, MXFP8, and MXFP4×MXFP8; empty/padded routes, more live work than concurrent SM capacity, routed per-token scale, and explicit SM2 fallback. The cache lookup is observed to assert effective CLC admission. Full payload and unwritten rows compare byte-exactly. This task-local gate adds no repository test.
- Gate passed on C2 `fi-v41-gap-c2-1025`, B300, GPU2. Raw logs and source-unchanged receipt are in `evidence/fc2-clc-r1/`. Scoped pre-commit passed. No sanitizer or broad suite.
- Fixed diagnostic: V41 EP4, T32/128/512, original N16/M128 tactic for FC1/FC2, full C–A–A–C on same GPU per family (NV GPU2; MX GPU4), 10/100, cold-L2 CUPTI graphs, PDL on, fused finalize off. Existing fresh B300 route hashes and exact 13-tactic cache identities are reused, not old latency values.
- The fixed diagnostic uses the unchanged public benchmark and observer. It is not native AUTO retention evidence. Full native sweeps are conditional on the fixed diagnostic.
- Remote source: `/workspace/flashinfer-w4a4-split-dynamic-n/fc2-clc-r1`; source is immutable after deployment.

## Fixed diagnostic result

All four arms completed and all route/source/tactic checks passed. T32/T128/T512 paired speedups:

| Backend | T32 | T128 | T512 | Three-point geomean |
|---|---:|---:|---:|---:|
| NVFP4 W4A4 | 1.0050× | 1.0093× | 0.9901× | 1.00146× |
| MXFP8 | 1.0086× | 1.0113× | 1.0062× | 1.00872× |
| MXFP4×MXFP8 | 1.0071× | 1.0143× | 0.9865× | 1.00257× |

NVFP4 and mixed T512 regress in both repeats. Unaffected W4A16 is 0.99803× overall (0.9959× at T512). Full native AUTO sweeps are held pending the parent retention decision; no production changes or commits. Full exact medians and receipts: `evidence/fc2-clc-r1-fixed/summary.{json,md}` and `raw/`.
