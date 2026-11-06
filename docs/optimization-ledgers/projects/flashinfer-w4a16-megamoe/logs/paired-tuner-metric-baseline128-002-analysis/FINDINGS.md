# T128 scorer findings and follow-up

All384 rank/visit records and7,680 raw samples pass the independent audit. Every scorer value is recomputed as the maximum of eight local ten-sample medians, and every rank0 gathered sample equals its originating rank record. All eight ranks agree on each global winner. Local rankings below describe rank-local preferences, not divergent collective decisions.

The preserved source is exact C1/250553:1,572 source files,337 required paths, unchanged worker85d3e18b and timer/helper hashes before/after, actual DSL4.7.1/compiler13.3/direct conversion and CUDA13.2 image Torch identity, and matching loaded NVSHMEM3.6.5/NCCL2.30.4/native compiler hashes. All48 visits/rank complete, input/weight/routing bytes and addresses are equal before/after, output bit-exact/finite gates succeed, graph reset count is one before each next candidate, and no tactic cache is written. Output bytes themselves were not saved, so the exact-output gate is source-attested rather than independently rehashed.

These are hot prestaged full-forward diagnostic scores including the reducer; they exclude public routing/staging and are not the cold-L2 CUPTI benchmark. Graph utility warmups/estimate replays and scorer-order reversal remain as disclosed.

| Pass | Eager global winner | Eager margin us | Graph global winner | Graph margin us | Eager local winners rank0..7 | Graph local winners rank0..7 |
|---:|---:|---:|---:|---:|---|---|
| 0 | 4 | 2.801 | 4 | 0.608 | [4, 4, 4, 6, 4, 6, 6, 4] | [4, 6, 6, 4, 6, 4, 4, 4] |
| 1 | 6 | 1.945 | 6 | 0.416 | [6, 6, 6, 6, 6, 6, 6, 6] | [6, 6, 6, 6, 6, 6, 6, 6] |
| 2 | 4 | 0.823 | 6 | 0.288 | [4, 4, 4, 10, 4, 4, 4, 10] | [6, 4, 6, 6, 4, 6, 4, 6] |

Candidate4 is M256/N64/C2/F4/epi;6 is the same geometry withF8;10 is M128/N64/C2/F8/epi. Pass0/1 global winners agree between scorers, while pass2 eager picks4 and graph picks6. Pairwise candidate ordering disagrees on13/120,15/120 and23/119 non-tied pairs across the three passes. Graph top margins are0.288–0.608us (0.15–0.32%); they are too small to identify a robustF4/F8 policy from this one shape.

The difference extends beyond which near-tied winner is first: candidate6 is tenth in pass2 eager ordering but first in graph ordering. Its eager score moves306.863–316.653us across passes (+3.19% max/min), while graph stays191.600–191.648us (+0.025%). Candidate0 eager moves310.901–332.333us, while graph moves206.448–208.480us. These observations support testing whether host overhead/order effects influence the current scorer; they do not identify their cause or establish a production gain.

| Candidate | Eager pass0 us | Eager pass1 us | Eager pass2 us | Graph pass0 us | Graph pass1 us | Graph pass2 us |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 332.333 | 311.589 | 310.901 | 208.480 | 206.448 | 208.352 |
| 1 | 324.185 | 322.427 | 325.328 | 219.520 | 218.592 | 218.416 |
| 2 | 319.174 | 313.884 | 313.337 | 206.864 | 208.544 | 208.352 |
| 3 | 323.451 | 324.465 | 321.932 | 218.608 | 218.560 | 218.736 |
| 4 | 308.547 | 308.965 | 308.049 | 190.992 | 192.032 | 191.936 |
| 5 | 313.965 | 313.755 | 313.026 | 204.368 | 204.432 | 203.664 |
| 6 | 311.348 | 306.863 | 316.653 | 191.600 | 191.616 | 191.648 |
| 7 | 314.240 | 312.657 | 312.416 | 204.400 | 204.368 | 204.432 |
| 8 | 311.620 | 308.807 | 312.317 | 200.320 | 200.272 | 200.752 |
| 9 | 317.039 | 318.442 | 316.830 | 212.512 | 212.416 | 212.928 |
| 10 | 312.884 | 315.118 | 308.871 | 200.304 | 200.368 | 199.264 |
| 11 | 316.295 | 316.844 | 316.091 | 213.456 | 212.704 | 213.632 |
| 12 | 313.859 | 312.217 | 313.469 | 206.448 | 207.296 | 207.408 |
| 13 | 319.939 | 319.172 | 323.619 | 218.144 | 216.656 | 219.552 |
| 14 | 314.664 | 310.626 | 316.744 | 206.480 | 206.400 | 206.336 |
| 15 | 322.149 | 321.192 | 322.507 | 216.480 | 217.408 | 217.648 |

A fresh five-shape sibling is justified:128/512/1/4096/64 preserves T128 as an adjacent reference, tests empty-rank and larger-load scopes, and directly examines the published T64 slowdown. It retains identical worker/timers and only extends the token tuple. This is queued after512 work, requires exact C1 restoration, and remains unexecuted. Keep all three passes and both scorers; do not choose a public policy or substitute diagnostic rows into the final CUPTI table.

Full values, source/library maps, per-rank ordering/margins and evidence hashes: [analysis.json](analysis.json), [raw-samples.csv](raw-samples.csv). Exact original analyzer: [analyze-frozen.py](analyze-frozen.py). Source-copy declaration and queued commands: [five-shape README](../../candidates/w4a16_tuner_metric_experiment_five_shapes/README.md).
