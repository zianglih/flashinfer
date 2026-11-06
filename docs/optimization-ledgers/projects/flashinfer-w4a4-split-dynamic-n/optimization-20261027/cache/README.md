# Uniform normal weight-cache screen

Fixed native winners; 10 warmups and100 cold-L2 CUDA-graph CUPTI samples; matched C-A-A-C. Candidate changes only weight payload cache policy from EVICT_FIRST to normal. No tactic axis, shape policy, scale policy, or activation policy changes.

| Tokens | Nemo W4A4 | V3 MXFP4x8 |
|---:|---:|---:|
| 4 | -7.30% | -13.21% |
| 128 | -4.93% | -4.73% |
| 4096 | -2.94% | -2.31% |
| 16384 | +9.51% | +4.16% |

Do not retain: repeatable decode regressions outweigh the large-prefill benefit. This confirms a reuse-versus-interference tradeoff rather than a universally better cache hint. Both repeats agree on decode direction. V3 T16384 baseline drift is visible in the raw pass medians, so treat its exact gain cautiously.

Raw receipts and all100-sample measurements are in `evidence/runs`. Archive SHA256 `fd5096e9ab760a77f0957f9647f177344fee7fac143486f032ac7ac643b85e67`. Candidate source remains uncommitted; no production changes are retained by this screen.
