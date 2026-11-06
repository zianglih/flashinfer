# One-warp per-token reduction bypass

Retained and pushed as374ed4c0. The change keeps the retained CTA-width policy and removes the redundant shared reduction and row-reuse barrier when the CTA contains one warp. Multiwarp compiled code is unchanged. Final formatted source is AST-equivalent to measured source; see format-equivalence.json.

Qualification:80 existing tests,52 direct cases,208 changing-live-count graph replays,4 routed-hole cases pass. The ordinary benchmark recipe is spill-free in inspected default-width captures. Eight precise-error configurations add8B to existing local stacks; all24 precise-error CAAC measurements are faster (+0.13..4.47%, geometric mean+1.685%) with identical outputs; see PRECISE_STACK.md. See AUDIT.md for complete codegen scope.

Source-paired end-to-end screen:24 C-A-A-C cells,9,600 strict CUPTI samples, frozen native tactics and routing, initial quantization included. TP prefill+0.241% geometric mean, EP+0.003%, decode+0.011%. All TP prefill repeat spreads≤0.076%. All phase-quartile median SM clocks2032MHz; some EP samples carry power-cap reason4. No normalization or filtering.

| Workload | Tokens | C1 μs | A1 μs | A2 μs | C2 μs | Change | Repeat C/A |
|---|---:|---:|---:|---:|---:|---:|---:|
| ep-kimi-k3-per-token | 32 | 180.913 | 180.962 | 181.057 | 180.769 | -0.093% | 0.080% / 0.052% |
| ep-kimi-k3-per-token | 4096 | 448.787 | 449.779 | 450.500 | 450.515 | -0.109% | 0.385% / 0.160% |
| ep-kimi-k3-per-token | 16384 | 1020.056 | 1017.641 | 1017.480 | 1017.208 | +0.105% | 0.280% / 0.016% |
| ep-nemo3-ultra-per-token | 32 | 110.145 | 109.856 | 110.113 | 109.633 | -0.087% | 0.467% / 0.233% |
| ep-nemo3-ultra-per-token | 4096 | 324.818 | 324.419 | 324.692 | 324.420 | +0.020% | 0.123% / 0.084% |
| ep-nemo3-ultra-per-token | 16384 | 918.056 | 918.089 | 917.498 | 917.977 | +0.024% | 0.009% / 0.064% |
| ep-v3-per-token | 32 | 106.304 | 106.448 | 106.304 | 106.608 | +0.075% | 0.286% / 0.135% |
| ep-v3-per-token | 4096 | 244.562 | 244.625 | 244.193 | 244.737 | +0.098% | 0.072% / 0.177% |
| ep-v3-per-token | 16384 | 623.556 | 623.396 | 623.635 | 623.539 | +0.005% | 0.003% / 0.038% |
| ep-v41-flash-per-token | 32 | 130.816 | 130.738 | 130.817 | 130.753 | +0.006% | 0.049% / 0.061% |
| ep-v41-flash-per-token | 4096 | 399.106 | 399.187 | 399.170 | 399.171 | -0.010% | 0.016% / 0.004% |
| ep-v41-flash-per-token | 16384 | 744.005 | 745.269 | 741.957 | 743.318 | +0.007% | 0.092% / 0.446% |
| tp-kimi-k3-per-token | 32 | 175.938 | 175.921 | 175.889 | 176.065 | +0.055% | 0.072% / 0.018% |
| tp-kimi-k3-per-token | 4096 | 659.239 | 656.534 | 656.037 | 659.110 | +0.440% | 0.020% / 0.076% |
| tp-kimi-k3-per-token | 16384 | 1913.923 | 1901.632 | 1902.448 | 1912.480 | +0.587% | 0.075% / 0.043% |
| tp-nemo3-ultra-per-token | 32 | 123.875 | 123.058 | 123.329 | 123.329 | +0.332% | 0.443% / 0.221% |
| tp-nemo3-ultra-per-token | 4096 | 553.124 | 553.061 | 552.741 | 553.188 | +0.046% | 0.012% / 0.058% |
| tp-nemo3-ultra-per-token | 16384 | 1763.072 | 1762.334 | 1762.287 | 1762.383 | +0.024% | 0.039% / 0.003% |
| tp-v3-per-token | 32 | 115.362 | 114.977 | 115.425 | 114.977 | -0.027% | 0.334% / 0.390% |
| tp-v3-per-token | 4096 | 466.356 | 464.962 | 464.819 | 466.147 | +0.293% | 0.045% / 0.031% |
| tp-v3-per-token | 16384 | 1360.618 | 1354.264 | 1353.976 | 1360.072 | +0.460% | 0.040% / 0.021% |
| tp-v41-flash-per-token | 32 | 145.905 | 146.176 | 146.081 | 145.857 | -0.170% | 0.033% / 0.065% |
| tp-v41-flash-per-token | 4096 | 536.435 | 536.051 | 536.148 | 536.420 | +0.061% | 0.003% / 0.018% |
| tp-v41-flash-per-token | 16384 | 1267.287 | 1266.535 | 1267.338 | 1267.128 | +0.021% | 0.013% / 0.063% |

The eight32-thread micro cases have+4.317% geometric mean; two unchanged64-thread controls−0.021%. Small microkernel gains do not translate directly to the complete overlapping MoE chain.

Broad raw archive SHA3300151bb6e9f7c1ac2c6ed54ff6585ea36d4b965d750eae7c714932b9898efb;289file hashes verified. Source/runtime/route/cache guards and sample-count checks pass. No sanitizer.
