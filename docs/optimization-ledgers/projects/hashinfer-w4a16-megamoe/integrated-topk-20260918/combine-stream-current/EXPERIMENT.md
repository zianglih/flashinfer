# FC2 partial read cache policy on retained PR8

Candidate `e193a2d521cadb8adf35f0437f04c5b2fa97a2e0` is the exact preserved,
previously unrun `8b8b1ec551635f85f43b965a46757e2b48a67933` patch ported to
PR8 head534a623. The reducer baseline is byte-identical at7dc,3de,and534.
This does not include the width16 candidate or PR9's FC1 weighting.

Only the ordered combine's FC2-partial copy atom changes from CopyUniversalOp
to CopyG2ROp with L1 NO_ALLOCATE priority. Copies remain128-bit. Score prefetch,
stores, ordered FP32 multiply/FMA, BF16 rounding, worker mapping and all existing
publication/readiness handoffs are unchanged. This is a cache-allocation hint,
not a noncoherent load or a new memory-ordering assumption. The earlier
activation-source hint was a different, measured and rejected trial; this
FC2-partial hint has not been measured.

Potential benefit: avoid L1 allocation for a one-pass partial stream. Potential
cost: forego useful L1 locality. No speedup follows from source inspection.
Run the same full13 AUTO4/O3/3warmup/100sample cold-L2 CUPTI sweep against A2
onhu15, retaining all samples and requiring104 bit-exact output comparisons.
Inspect emitted cache policy if the timing supports retention. No added layout
alignment, public knob, tactic, or new sanitizer run during iteration.
