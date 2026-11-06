# Retained, original ready-first, and mapper-loop results

All three are complete 14-row runs on hu-pdx-59 with the same four public F4 tactics and fresh tuning caches. Cold latency is the median of 100 per-iteration rank maxima measured with cold-L2 CUPTI. Tokens 1/2/4 are reported; retention uses 8–8192.

| Tokens | Retained 2e3b ms | Original 07d7 ms | Mapper 3071 ms | Mapper / retained change |
|---:|---:|---:|---:|---:|
| 1 | 0.089169 | 0.078273 | 0.085297 | -4.342% |
| 2 | 0.098321 | 0.105488 | 0.104545 | +6.330% |
| 4 | 0.115105 | 0.131329 | 0.119905 | +4.170% |
| 8 | 0.134592 | 0.154178 | 0.141777 | +5.338% |
| 16 | 0.152177 | 0.157313 | 0.154721 | +1.672% |
| 32 | 0.180081 | 0.175777 | 0.185553 | +3.039% |
| 64 | 0.203393 | 0.202657 | 0.203250 | -0.070% |
| 128 | 0.206145 | 0.209699 | 0.205265 | -0.427% |
| 256 | 0.212002 | 0.210610 | 0.212946 | +0.445% |
| 512 | 0.211650 | 0.218498 | 0.220593 | +4.225% |
| 1024 | 0.235042 | 0.233906 | 0.236178 | +0.483% |
| 2048 | 0.311283 | 0.315171 | 0.311890 | +0.195% |
| 4096 | 0.468500 | 0.472643 | 0.470676 | +0.464% |
| 8192 | 0.796709 | 0.818840 | 0.804536 | +0.982% |

Selected tactics are identical across all three runs: N64/F4/epi through 1024 tokens, N128/F4/reuse at 2048–8192.

| Retention comparison, 8–8192 | Geometric latency ratio | Change | Mapper lower rows |
|---|---:|---:|---:|
| Mapper / retained | 1.014702223 | +1.470222% | 2/11 |
| Mapper / original | 0.993944762 | -0.605524% | 6/11 |

Matched hot scores hold geometry and return mode fixed. They are the maximum of per-rank medians from the hot full-forward graph, printed to 0.1 µs; they are separate from the cold latencies above.

| Hot comparison | Tokens | Lower | Equal | Higher | Total |
|---|---|---:|---:|---:|---:|
| Mapper vs retained | 8–8192 | 1 | 0 | 43 | 44 |
| Mapper vs retained | 1–8192 | 1 | 0 | 55 | 56 |
| Mapper vs original | 8–8192 | 34 | 3 | 7 | 44 |
| Mapper vs original | 1–8192 | 38 | 7 | 11 | 56 |

The mapper reduces the measured overhead of the original ready-first implementation, but this sweep does not show a gain over the retained control. These are single sweeps, without a statistical-confidence claim. Both historical diagnostics passed their numerical oracles with zero observed reorders; no mapper diagnostic was repeated. Timing characterization only; promotion remains unadmitted.

Artifacts were reconstructed once and each pairwise comparison ran once; this table only joins those saved comparison results. The mapper proof checked 14 rows, 112 compiled records, 112 winner records, 56 candidate rankings and 1400 timing samples. Mapper benchmark wall time was 466.232496 seconds.

- [All 56 hot pairs versus retained](../../../logs/cu132-recovery0911c-ready-fc1-mapper-loop-vs-retained5869-f4-auto14-comparison-001/README.md)
- [All 56 hot pairs versus original](../../../logs/cu132-recovery0911c-ready-fc1-mapper-loop-vs-original07d7-f4-auto14-comparison-001/README.md)

| Saved artifact | SHA-256 |
|---|---|
| Mapper reconstruction | `73d8d5983a14258d8e8f88bf58be2be9c30fd0c62705c742cbb8f7e32fcf7424` |
| Mapper result | `e175b554903dc111edfcc75a79b2614600dd2d0cbb7e41d4c9fdc63a5071456e` |
| Comparison vs retained | `33a7c957044a8d64a8a938a4174777d19dd0b81b4af8b8df7256a53a3971626d` |
| Comparison vs original | `f5f06cc3bfce42105db8b42a50cf089744ccd21eea956196d125e50792561f19` |
