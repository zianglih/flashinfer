# Nemotron EP critical-path diagnostic

Clean source `1054743780dda2919c1424124c1e3258248b8c19`, primary C3 B300 GPU3, Nsight Systems2026.2.1.210, image `nvcr.io/nvidia/pytorch:26.05-py3`. Reused the83df A2 winning tactics and exact routing identities; no autotuning. The unmodified public benchmark profile mode runs3 warmup and20 cold-L2 graph replays. This is stage diagnosis, not retention timing. NVFP4 includes its input quantizer.

All136 raw artifacts are hash verified, including both `.nsys-rep`, SQLite exports, exact commands, source/runtime receipts, cache manifests and winner/route checks. Source and GPU UUID are in `evidence/receipt.json`; its optional box label is null because the managed primary transport did not set that label. The deployment command, GPU UUID and source path establish the primary devbox. Native compiler caches remain persistent.

| N3U EP8 | Graph us | Prepare | FC1 | FC2 | Combine |
|---|---:|---:|---:|---:|---:|
| W4A4 T4096 |233.393|7.712 /7.392|115.857 /114.385|101.089 /71.088|18.112 /14.912|
| MXFP4x8 T16384 |728.853|30.977 /30.737|334.178 /329.922|321.026 /296.930|62.817 /59.233|

Stage cells are median duration / critical extension in microseconds. Overlapping kernels are not added; individual medians need not sum exactly to the graph median. W4A4 additionally spends6.272us in input quantization and18.417us critical extension in routing. MXFP4x8 routing contributes11.472us.

- W4A4 uses route256, FC1 M128/one CTA, FC2 M256/two CTA, Ksteps4/4, static scheduling. FC1 contributes49.0%of critical span and FC2 contributes30.5%. FC2 overlaps its predecessor by29.5us.
- MXFP4x8 uses route256, M256/two CTA for both GEMMs, Ksteps4/4, static scheduling. FC1+FC2 contribute86.0%of critical span. FC2 overlaps by24.0us. FC1 uses234 registers/thread, FC2 uses110; each allocates206,592 bytes of shared memory.
- Both profiles reinforce GEMM investigation rather than a new prepare/combine geometry policy. NSYS duration and register count do not establish whether tensor work, scale publication, epilogue or memory is limiting; per-stage counters are needed before a structural change.
- Earlier N3U evidence was W4A4 T16384 at d1767. Neither new cell has the same token/dtype pair, so no before/after speedup is inferred.

`analysis.json` records every replay interval and source-bound trace hash. `evidence-verification.json` binds the downloaded archive. No source changes or sanitizer.
