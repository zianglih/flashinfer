# Independent final policy comparison

Verified clean `0b7fe901` versus tuner-only patch `cd7f0174`: all 156 cells, 62,400 C/A/A/C samples, 468 route/cache snapshots, 4,680 winner hits, 1,872 effective-scheduler records and 264 admission profiles. Both source manifests contain 87 verified entries; candidate admitted counts are exactly half. The raw-sample CSV and all 156 median CSV rows agree with the original JSON measurements. AUTO samples are excluded from performance aggregates; tokens 1/2 remain recorded and are excluded from retention.

| Scope | Overall speed change | Decode 4–512 | Prefill 4096–16384 |
| --- | ---: | ---: | ---: |
| V3 | −0.49% | −0.54% | −0.34% |
| V4.1-Flash | −0.41% | −0.97% | +1.07% |
| Kimi K3 | −1.90% | −0.86% | −4.61% |
| All | **−0.94%** | **−0.79%** | **−1.32%** |

Percentages are `100*(control/candidate−1)`, using the geometric mean of each arm's two phase medians. Positive means faster.

Of 132 retention cells, 79 retain the same geometry/depth: 60 only disable FC2 CLC (−0.65% geometric mean), while 19 only enable FC1 CLC (−1.00%). The latter include stable K3 losses of −6.26% at MXFP4x8/4096, −3.27% at MXFP8/4096 and −3.28% at W4A4/8192. FC2 was already static in these cells; their changed scheduling behavior is in FC1. These are observations within the selected geometry subset, not an unbiased average of every tactic.

K3/16384 loses −11.30% W4A4, −7.18% per-token and −9.45% MXFP4x8. Both candidate repeats are slower than both control repeats. These cases also change FC1 geometry and/or K depth, so they are whole-policy AUTO results rather than isolated FC1 scheduler measurements. The W4A4 and per-token repeat spreads are below 0.83%; MXFP4x8's candidate spread is 2.68%, still appreciably smaller than its loss. V4.1 W4A4/16384 gains +6.75%, also with a changed geometry, N128 to N256.

The separate 800-sample V3 MX/16384 confirmation is preserved without replacing the original table. MXFP4x8 changes from +3.52% to −0.49%, with 5.08% candidate-repeat spread in the confirmation. MXFP8 changes from −0.71% to +7.03%. These cells do not support a stable performance claim across campaigns.

Observed warm/persistent-cache AUTO worker wall-time sum falls 2852.47 s → 1665.75 s (41.60%); profile calls halve 84,480 → 42,240. These are concurrent worker/API wall-time observations, not campaign elapsed time or cold compilation speedups.

Recommendation: keep the current shared-CLC AUTO policy as the performance default. The smaller search space speeds up tuning, but the unconditional fixed policy loses performance on every model overall and substantially harms K3 prefill. No further GPU run is required to establish that tradeoff.
