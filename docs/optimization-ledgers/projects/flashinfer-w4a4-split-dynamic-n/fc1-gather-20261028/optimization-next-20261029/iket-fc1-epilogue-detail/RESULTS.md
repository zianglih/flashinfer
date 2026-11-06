# N3U EP8 16K W4A4 FC1 epilogue detail

The nested scope covers the nongated FC1 initial TMEM loads and two existing ownership transposes. For the sampled epilogue warps, its summed scopes occupy **37–43% of the enclosing instrumented epilogue body**, about1.66–1.83µs per tile. This identifies substantial layout-conversion work worth studying, but does not imply that this time is removable: it includes data loads, transpose dependencies and marker overhead.

| Sampled group leader | Epilogue warp | Body mean, µs/tile | Nested load/transpose sum, µs/tile | Instrumented fraction |
|---|---:|---:|---:|---:|
| CTA0 | 4 | 4.067 | 1.766 | 43.4% |
| CTA0 | 5 | 4.051 | 1.701 | 42.0% |
| CTA0 | 6 | 4.178 | 1.805 | 43.2% |
| CTA0 | 7 | 3.972 | 1.659 | 41.8% |
| CTA2 | 4 | 4.524 | 1.774 | 39.2% |
| CTA2 | 5 | 4.505 | 1.715 | 38.1% |
| CTA2 | 6 | 4.555 | 1.826 | 40.1% |
| CTA2 | 7 | 4.483 | 1.674 | 37.3% |

- Source: frozen `d9dee2dae50fef5d14c609e277fbc29d48df08b4`; all514 source files match the committed source. Sampled module is AST-equivalent after removing marker calls. Native winner, route hashes, input quantizer and unfused-finalize contract are unchanged.
- Instrumentation samples physical CTAs0–3 only, with an explicit two-CTA compile assertion; full grid has148CTAs. Each sampled CTA processes51tiles and388 nested layout scopes per epilogue warp.
- Both tracker and real profile actual NativeDump CUBINs are identical (`1ccb42dcf68f5102002792a243a6f187724874f8b8561fcfb944879cf3f7aace`), REG168, STACK0, LOCAL0, no LDL/STL. Resource guards run before launch in both phases.
- The final cold-L2 graph replay (`graph_exec_2:3:0`) is analyzed; preceding regular/graph warmups remain in raw evidence. Both leaders overlap all50 adjacent tile pairs: the next tile MMA issues while the prior epilogue still runs.
- 32ns marker timestamp granularity; sampled warps and concurrent scopes are not additive end-to-end latency. No old-winner comparison or retention speedup claim.
- No clock/power changes, no sanitizer. The optional iKET CUDA compatibility warning remains in the complete log; trace collection and exports succeeded.

[Timeline](timeline.png) · [Full marker table](range-table.md) · `nested-layout-analysis.json` · `summary.json` · `independent-audit-receipt.json`

All21 semantic files verified; archive SHA256 `7d30180f9f1bae8af1502cd743adc2a821103fa16655dac4b311f2e96ec9a84e`. Previous broader trace and failed R0/R1 tool attempts remain separately preserved.
