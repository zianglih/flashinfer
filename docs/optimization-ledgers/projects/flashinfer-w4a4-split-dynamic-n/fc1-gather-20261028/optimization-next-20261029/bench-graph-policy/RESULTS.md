# Benchmark graph-policy result

The one-line benchmark cleanup passes the bounded capture check but produces no performance gain: both K3 graph searches select exactly the same slower tactics as the fresh eager searches. It remains an unstaged review candidate for consistency, not a retained performance optimization.

| Case | Old winner us | Fresh eager winner us | Graph winner us | Graph vs eager | Graph vs old |
|---|---:|---:|---:|---:|---:|
| ep-kimi-k3-w4a4 | 480.212 | 514.379 | 514.804 | -0.082% | -6.719% |
| tp-kimi-k3-per-token | 2019.359 | 2098.655 | 2098.872 | -0.010% | -3.788% |

Native graph AUTO uses cold-L2 CUDA events, not CUPTI. All final comparisons use fresh same-GPU old/eager/graph/graph/eager/old strict CUPTI graph replay. Each K3 search has 321 finite profiles (320 admitted tactics plus baseline).

- ep-kimi-k3-w4a4: native graph score of old winner 511.856 us; selected winner 499.696 us. Final public timing reverses this ranking.
- tp-kimi-k3-per-token: native graph score of old winner 2103.744 us; selected winner 2081.792 us. Final public timing reverses this ranking.

V3 EP8 W4A16 T8 graph-AUTO smoke passed 24/24 finite profiles and a 100-sample frozen graph replay. This establishes bounded capture support only. The swap-kernel runtime register observer has no W4 observations, so it is not W4 register validation. Six K3 runtime guard processes (236 compilation observations) passed. All 90 archive files verified, SHA `a4aeccff46fbcea9cf773260cd9c284352019fc05225602fb7819790411a8697`.

See the following `k3-route-scope/RESULTS.md` for the controlled proof that route distribution alone is sufficient to reverse the EP N128/N256 ranking. No fresh eager crosscheck was needed because graph and existing fresh eager winners already match. No kernel, public API, production defaults, cache contents, or PR table were changed.
