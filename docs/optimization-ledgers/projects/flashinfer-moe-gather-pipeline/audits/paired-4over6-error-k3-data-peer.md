# Paired 4/6 error: K3 six-cell raw peer

Independent replay passed all 2,400 CUPTI spans, 24 phase medians, 96 clock quartiles, frozen routes/tactics/cache entries, 13,245-file source inventories and pre/post native cohort. All 48 actual GEMM resource records match across arms (LOCAL0). This subset does not include a per-cell quantizer native-image/resource join.

| Topology | Tokens | Speedup | Control repeat spread | Candidate repeat spread | Clock reasons |
|---|---:|---:|---:|---:|---|
| EP8 | 32 | -0.128400% | 0.115297% | 0.089055% | 0 |
| EP8 | 4096 | +0.031746% | 1.171350% | 1.128747% | 0 |
| EP8 | 16384 | -0.669546% | 0.860417% | 0.939722% | 0,4 |
| TP8 | 32 | +0.327599% | 0.036001% | 0.163633% | 0 |
| TP8 | 4096 | +0.286465% | 0.033748% | 0.046011% | 0 |
| TP8 | 16384 | +0.158706% | 0.063179% | 0.086345% | 0 |

EP16K is −0.669546% (+6.998 µs). The two clock exception windows are both control quartile 4: first control has minimum SM clock1912MHz and3 reason4 samples; last control has minimum2032MHz and13 reason4 samples. All96 quartile medians are2032MHz; no clock window is missing. No samples are removed.

Median-of-phase component deltas are initial quant +1.712µs, intermediate quant extension +4.704µs, FC1 extension +1.088µs, FC2 extension −0.048µs, combine +0.008µs. Component medians need not add exactly to the geometric E2E estimate. The apparent FC2 duration increase248.714→352.907µs accompanies activity start721.942→623.509µs; exposed FC2 extension225.634→225.586µs stays flat. It is not evidence of104µs additional GEMM compute.

Later quartiles drift upward in every phase. Both negative cells (EP32 and EP16K), all positive cells, all clock samples and full phase trajectories remain in the JSON receipt. The observed EP16K slowdown is concentrated in quantizer spans/extensions with a smaller untouched FC1 drift; the subset does not establish a microarchitectural cause. Await the other36 cells; no repeat or retention conclusion.

Receipt: `audits/paired-4over6-error-k3-data-peer.json`. Replayer: `audits/audit_paired_error_k3_data.py` (adapted existing auditor).
