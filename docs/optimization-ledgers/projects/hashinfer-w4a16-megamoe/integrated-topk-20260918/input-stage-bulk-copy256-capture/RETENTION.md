# Full256 staging: preserve evidence, do not retain

0103/E1 emits the intended native256-bit bulk load and store, with no observed
local-memory spills in the inspected selected variant. Its full13 comparator
passes104 exact output pairs and retains every A1 tactic. Decode4–512 geometric
speedup is0.987328645x; prefill4k/8k/16k ratios are1.017893978x,1.001095391x,
1.010866466x. These results do not justify the additional32-byte specialization
and decode regressions. The user prefers preserving existing layout contracts.
No code from this experiment is promoted; keep the frozen source and evidence.

One mapping limitation deserves preservation for a future revisit. Keeping the
original first128-bit stripe preserves first-wave concurrency, but it does not
preserve concurrency in a short residual bulk stripe. At H7168/EP8/T256, each
rank has28672 16-byte chunks and W=148*128=18944 dispatch workers. After the
first stripe,9728 chunks remain. The existing128-bit loop distributes them to
9728 threads/76 CTAs; this candidate's contiguous256-bit pairing distributes
them to4864 threads/38 CTAs. That is a plausible contributor to the observed
T256 regression, not a demonstrated sole cause. Other decode rows also change,
including shapes that only execute the unchanged-width first stripe.

If stronger alignment is reconsidered later, a full-grid-wide256-bit bulk with
128-bit residual stripes could preserve tail concurrency. That adds control
and index work, so it needs its own generated-code and full13 comparison;
no improvement or correctness validation is claimed for this unimplemented
idea. Avoid inferring a hardware vectorization limit from this one mapping.
Current priority is packed compute and instruction scheduling under the
existing16-byte contract.

Evidence: `decode13-benchmark/terminal-summary-table.csv`,
`codegen-selected/INDEPENDENT_EARLY_CODEGEN_REVIEW.md`. Full local archive
audits remain deferred while subsequent GPU timing runs; the early review
states that boundary explicitly.
