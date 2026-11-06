# Experiment state

Current source is **candidate3r**, kernel SHA256
`664a74fde4f0d60957a2ddb07839c95f393d477f7ee84d5ce4415bb56bf4d939`.
The product catalog contains 34 default tactics; the benchmark wrapper exposes
only its 18 mixed4+2 tactics. Baseline performance uses original AUTO16.

| Patch | Current state | Purpose |
|---|---|---|
| `hoist-b-tma.patch` | Applied in candidate2 | Select persistent activation descriptors and geometry once |
| `mixed-b-tma-try-acquire.patch` | Applied in candidate3r | Reuse established activation producer lookahead |
| `mixed-registration-overlap.patch` | Applied in candidate3r | Register fallback groups before the metadata wait |
| `auto34-mixed-group256.patch` | Applied in candidate3r | Add six mixed group256 choices using existing group scaling |
| `mixed-raw-weight-try-acquire.patch` | Prepared, unapplied | Reuse local W4A16 raw weight/scales producer probes; baseline PC evidence does not justify application |
| `auto52-mixed-static.patch` | Prepared, unapplied | Append existing static scheduling choices; baseline PC evidence does not justify application |

Individual notes and validation receipts preserve their preparation-time state.
Do not reapply the first four patches to the current checkout. The final three
candidate3r changes were measured together to shorten iteration time, so that
comparison does not isolate their individual effects.

The completed short screens do not establish a speedup over the pristine
baseline. Exact results and run-state updates belong in
[`../OPTIMIZATION_LEDGER.md`](../OPTIMIZATION_LEDGER.md). All performance captures
use native AUTO; profiler durations are diagnostic only.

The a2 PC pair completed with eight audited reports per arm and unchanged
source, after support-module preparation outside NCU. Startup coordination
dominates many baseline ranks, so sampled percentages are not production-time
fractions or evidence for the prepared raw/static experiments. Candidate PC
analysis and a matched T128/T512 AUTO pair are in progress. Source remains
frozen while timing captures run.
