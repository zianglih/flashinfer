# K3 EP16K single reverse-order diagnostic

**The sign changed, leaving attribution unresolved.** Primary CAAC was −1.464026%; the one authorized same-GPU ACCA is +0.676962%. The positive repeat does not replace or erase the original adverse row, and the two blocks are not pooled into a preferred answer. No more repeats are planned.

Actual sources remain82254e20 versus the exact02de7785 snapshot. Same GPU1 UUID `GPU-b17ed232-0a73-13f0-fd86-db7534da7ea2`, same frozen recorded choice/route, normal persistent caches,100 strict CUPTI samples per phase,10 warmups,coldL2 CUDA Graphs. No clock manipulation, retuning, source changes, or new profiling. The separate GPU3 NCU metrics pass completed and released before this block started.

All400 raw spans, four phases, eight LOCAL0 loaded functions and two unchanged FC-stage resource configurations pass. Full source postflight and current native ELF/Ninja unchanged/no-op checks pass. GPU1 is idle/released. There are13/16 clock-exception quartiles and zero missing; both control and candidate show different clock trajectories. C/A repeated-phase spreads are0.690623/0.407117%.

| Order | E2E µs | FC1 duration µs | FC2 duration µs | Combine duration µs | FC1 extension µs | FC2 extension µs | Combine extension µs | Clock quartile medians MHz | Reason sets |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 0-candidate | 1996.591 | 1337.754 | 570.548 | 118.960 | 1337.386 | 569.541 | 79.137 | 2032/1815/1815/1297 | 0/0/0,4/4 |
| 1-control | 2012.943 | 1351.435 | 572.772 | 120.288 | 1351.082 | 571.685 | 79.361 | 1905/1905/1290/1290 | 0/0/0,4/4 |
| 2-control | 1999.137 | 1343.403 | 566.884 | 121.217 | 1343.067 | 565.732 | 79.072 | 2032/2032/1297/1297 | 0/0,4/4/4 |
| 3-candidate | 1988.496 | 1327.979 | 570.277 | 121.265 | 1327.627 | 569.237 | 79.088 | 2032/2032/1365/1365 | 0/0,4/4/4 |

Arithmetic mean-of-phase component deltas (candidate−control): FC1 −14.5525µs, FC2 +0.58475µs, combine −0.63975µs; corresponding critical extensions −14.568/+0.6805/−0.1045µs. These descriptive component medians are not additive E2E estimates. The primary block instead had FC1 +14.02375µs and FC2 +13.752µs. This reversal does not isolate a consistent FC1 selector penalty.

The original adverse block deserves preservation because both original candidate medians exceeded both controls. Conversely, both repeat candidates are below both repeat controls. Different phase/clock trajectories and opposite signs make a definitive claim about a small source-local regression unsupported; the broad historical 1–5% W4 prefill gaps are not reproduced by the complete fresh24 matrix (+0.433710%,7negative).

## Evidence

- [Fresh ACCA report](../../../evidence/w4-initial-selector-k3-ep16k-acca/1793389072726146000/report/table.md), [raw data](../../../evidence/w4-initial-selector-k3-ep16k-acca/1793389072726146000/data), and [all clock quartiles](../../../evidence/w4-initial-selector-k3-ep16k-acca/1793389072726146000/report/clock-quartiles.json).
- [Primary full24 result](../RESULTS.md) and [original K3 EP16K trajectory](../k3-ep16k.md) remain unchanged. Their no-follow-up statement describes the primary report before this separate diagnostic.
- [Config](perf-config.json), [launch](launch.json), [release postflight](gpu-release.json).

No production files or published results changed. No additional W4 timing will be run.
