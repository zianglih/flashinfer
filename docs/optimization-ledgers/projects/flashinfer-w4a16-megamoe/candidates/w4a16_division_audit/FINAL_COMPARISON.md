# Fast-divmod full comparison

Immediate BEFORE e470 versus candidate3da on hu-pdx-59; one complete 1–8192 sweep per arm. Saved reader and comparator each passed once. Cold latency is the median of 100 per-iteration rank maxima; hot scores are the printed maximum of per-rank medians, a separate measurement.

Retention 8–8192: candidate/before geometric ratio **1.008015069** (+0.801507% latency), lower on 5/11 rows. All14 secondary: -1.122209%, 8/14 lower. All selected tactics are unchanged.

| Tokens | BEFORE e470 ms | AFTER 3da ms | Latency change | Selected tactic (both) |
|---:|---:|---:|---:|---|
| 1 | 0.084801 | 0.069488 | -18.058% | N64/F4/direct |
| 2 | 0.104528 | 0.102033 | -2.387% | N64/F4/direct |
| 4 | 0.120817 | 0.118129 | -2.225% | N64/F4/direct |
| 8 | 0.138897 | 0.137745 | -0.829% | N64/F4/direct |
| 16 | 0.148577 | 0.150881 | +1.551% | N64/F4/direct |
| 32 | 0.180545 | 0.179346 | -0.664% | N64/F4/direct |
| 64 | 0.201537 | 0.197057 | -2.223% | N64/F4/direct |
| 128 | 0.203297 | 0.222610 | +9.500% | N64/F4/direct |
| 256 | 0.210081 | 0.209169 | -0.434% | N64/F4/direct |
| 512 | 0.215041 | 0.215234 | +0.090% | N64/F4/direct |
| 1024 | 0.229794 | 0.234546 | +2.068% | N64/F4/direct |
| 2048 | 0.312563 | 0.308452 | -1.315% | N128/F4/reuse |
| 4096 | 0.468308 | 0.469108 | +0.171% | N128/F4/reuse |
| 8192 | 0.775576 | 0.786245 | +1.376% | N128/F4/reuse |

Matched hot scores: 8–8192 has 22 lower / 3 equal / 19 higher out of 44; all14 has 30 / 5 / 21 out of 56. Most changes are below 1%; the retention-domain exception is N64/reuse at T8 (+2.625%).

The largest cold increase is T128 (+9.500%), while the matching selected N64/direct hot score moves 179.7→179.3 us (−0.223%). These are different measurement scopes; this single sweep does not establish the cause or statistical significance. Native instruction reductions and unchanged resources remain separate evidence for the source cleanup; no demonstrated general latency gain is claimed.

Full 56 fixed-tactic hot score pairs and saved arithmetic: [comparison README](../../logs/cu132-recovery0911c-division-fastdiv-vs-e470-comparison-001/README.md), [comparison JSON](../../logs/cu132-recovery0911c-division-fastdiv-vs-e470-comparison-001/comparison.json). The immutable comparator uses its inherited table labels ‘Retained’ and ‘Dispatch’; its explicit arm IDs mean e470 and 3da respectively.

Validation scope: native4; EP1 reference4; EP2 geometry/tails6 per rank×2; existing C1 routing2 per rank×2 with 7/1 rounds; all completed source/native/idle closures passed. AUTO wall421.426308s. Retention/publication decision remains with root.
