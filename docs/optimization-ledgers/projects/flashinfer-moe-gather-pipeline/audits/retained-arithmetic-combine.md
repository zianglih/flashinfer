# Retained arithmetic and combine audit

Read-only pass at `49c91adf`. No source edit or GPU run.

- The default SwiGLU clamp is finite FP32 maximum, not infinity. Current V3 FC1 native SASS contains `FMNMX.NAN` with `0x7f7fffff`. These operations turn infinities into finite endpoints and preserve the specified NaN behavior. They cannot be removed as no-ops without changing the activation contract. Ordinary sigmoid arithmetic is already paired; no clamp bypass is proposed.
- Shared finalize uses packed FP32 multiply/FMA and 128-bit payload copies. Earlier actual 256-bit, metadata broadcast/prefetch, and geometry variants are documented under the prior project's `scripts/finalize_geometry_experiment/README.md`. A new wider load is not justified merely by current source width.
- The fresh V3 TP MXFP8 prefill profile (`profiling/v3-tp-mxfp8-16k/COMBINE_RESULTS.md`) reports 84.82% combine DRAM throughput. The unfused path necessarily writes and rereads BF16 expert outputs. These bytes are not an unnecessary transpose or synchronization. Eliminating that round trip by fused finalize would change the requested comparison contract.
- Removing the expanded-layout guard around the retained exact-divisor geometry looked like a possible simplification after gathered output switched to permuted order. Independent history audit found that the same seven-vector H7168 permuted geometry already lost in multiple measured proxies. It remains source-only; the agent's detailed caller/history audit will supply the evidence links.

This pass distinguishes required semantics and measured closed leads from removable work; it does not claim every shared-finalize policy is optimal.
