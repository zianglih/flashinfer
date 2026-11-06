# Retention decision

The parent retained follower-MMA cleanup, compile-time PDL guards and consistent
activation/SF cache priority in `cb35c42f6143aa08546ee1c6c8d6e6913c6cf03f`.
The rationale is less redundant follower work and PDL-off code, a simpler
operand-pair cache policy, and a slight consistent decode benefit. This is not
a claim of a large end-to-end performance gain. Descriptor prefetch was rejected
as neutral; its isolated NV/MX geometric means were+0.035/−0.145%.

The fresh four-model MX matched diagnostic keeps the normal100-sample medians:
all eight decode cells improve0.19–0.48%; the16-cell geometric mean is−0.57%.
Some prefill medians are negative, including V3 MXFP4x8−3.51%. Sequence inspection
shows a transition between low/high latency groups near the median, with
overlapping control/candidate strata. The initial characterization of that V3
cell as a clear patch regression was withdrawn.

V3 ABCCBA isolates preserve the same standard metric:

| Change | Decode MXFP8 / MXFP4x8 | Prefill MXFP8 / MXFP4x8 |
|---|---:|---:|
| SF cache priority | +0.24% / +0.21% | −1.55% / −0.93% |
| Follower-MMA cleanup | −0.01% / +0.01% | +2.63% / −2.50% |

For MXFP4x8, first25/last50 strata instead give−0.08/+0.67% for SF cache and
−0.18/+0.14% for follower cleanup. MXFP8 strata leave a modest late-SF-cache
negative signal but broad overlapping distributions. Source-specific prefill
regression is therefore unproven/ambiguous. Temperature/clock telemetry cannot
be aligned with individual timing samples and does not establish a cause.
Published tables retain the original median methodology; strata are diagnostic
context, not substituted metrics. No hardware clocks or benchmark policy changed.

Evidence: [matched table](matched-mx/evidence/diagnostic/summary.md),
[isolate table](v3-mx-isolate/evidence/diagnostic/summary.md),
[strata](v3-mx-isolate/strata.md), [exact/codegen gate](combined/README.md).
All assigned GPUs are released; the next audit is read-only.
