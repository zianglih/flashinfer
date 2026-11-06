# Native primary A1 screen: 442d2aa5

Candidate: `442d2aa53f68b4640c3ab5118a76f1599ff60d34`.
Baseline B1: `a65d5b09e7e4c4c5c160b0161c48becd100b3970`, reused unchanged.
Previous candidate screen: `13ca1475d96839f3bf3c46699cc63204b4d3b409`.

- [Full 39-row raw median table](raw-medians.md)
- [Screen ratios and protocol](summary.md), [machine-readable results](summary.json)
- [Selected native AUTO tactics](selected-tactics.md), [exact bucket/history audit](tactic-audit.json)
- [Previous candidate comparison](delta-13ca1475.md)
- [Source/log/provenance receipt](verification.json)
- [All archived file hashes](sha256.json), [raw archive](raw.tar.gz)

Image `nvcr.io/nvidia/pytorch:26.05-py3`; B200 GPU0 for NVFP4, GPU1 for
MXFP8 then mixed MXFP4 × MXFP8. All13 token sizes; native AUTO, unfused finalize,
per-tensor activation scales, 10 warmups/100 cold-L2 CUDA-graph CUPTI samples.
Tokens 1 and 2 are reported and excluded from aggregates. No baseline rerun,
A2 or B2 occurred; these are single-screen ratios, not ABBA retention results.

All39 rows and78 cache hashes verified, along with unchanged timing/routing/
quantization setup, exact frozen helpers, runtime environment, source hashes,
AUTO bucket history and current host/native-readiness logs. The authorized
finalizer change is measured production with explicit old/new hashes and diff.

Current host checks:56 passed/four warnings. Root separately archives72 paired
phase cases and15 native exact configurations from the AST-equivalent composed
overlay. Broad numerical and sanitizer checks remain deferred.

Raw archive:96 files,1,565,238 bytes; SHA256
`6f4ffcf8bfd00449008b9e2d8cf133ec02d66f726f0825ceb1f447f6c95d48b4`.
