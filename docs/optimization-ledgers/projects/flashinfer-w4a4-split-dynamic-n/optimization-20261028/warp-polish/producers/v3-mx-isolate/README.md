# V3 MX isolated retention diagnostic

Completed2400 CUPTI samples on GPU0 in ABCCBA order. A is clean99f4; B is the
frozen activation-SF cache policy; C is the frozen follower-MMA cleanup. Both
MX formats and tokens64/16384 use the same public observer, frozen native
winners/routing, ten warmups and100 cold-L2 samples per phase. No autotuning,
external baseline, hardware-clock change or benchmark-policy change occurred.
All source/cache/routing/timer checks passed. GPU0 is released.

Standard100-sample medians remain in `evidence/diagnostic/summary.md`. B improves
decode0.21–0.24%; C is decode-neutral. Prefill moves in both directions, but
sequence strata do not isolate a stable MXFP4x8 slowdown. Relative to control,
first25/last50 median speeds are B−0.08/+0.67% and C−0.18/+0.14%. The100-sample
medians of−0.93% and−2.50% cross low/high latency transitions instead. Treat
those prefill effects as ambiguous.

MXFP8 first25/last50 speeds are B−0.04/−1.82% and C−0.01/+0.98%, with overlapping
p10–p90 distributions. This leaves a modest late-MXFP8 negative signal for B,
not a separated end-to-end regression. `strata.py` reproduces `strata.md/json`;
it is descriptive retention evidence, not an alternative published metric or
a significance test on temporally correlated samples.

Subsecond telemetry observed changing SM clocks and37–46C, but the observer
does not timestamp individual timing samples. It cannot attribute the latency
transition to hardware clocks. The source patches and measured clones remain
unchanged; retention is the parent's decision.

Archive SHA:
`6520dac75ebbf8519f2ac88f3c946c151d89f48c1d6a9209b9adb7215ab83956`.
All55 archived file hashes were verified locally.
