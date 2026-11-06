# Remove exhaustion checks already covered by the received-total bound

Held source-only follow-up on source64a81ed8; not applied, compiled or executed.
Base transport `199a9c28f20327b4db40626b13094d3578a811472d4973f52d871f0a81b8e97a`; proposed `b848151a2ad89b12e14b57937033de40742991c1c70fb7df1eec8c7fc81f6836`;
patch `a556315697d6b67925f6c86bad4cce064cdc9c1e583f6827bdd9f44434e5aa2f`. Current64a8 numerical/AUTO remains independent.

The patch removes exactly three guards: the expert-valid conjunct from the
inner prefix loop, the expert-valid wrapper around its next-count fetch, and
the expert-valid wrapper around the selected token body. The large textual diff
is dedentation of the unchanged mapping/payload body, not a duplicate mapper.
A local AST comparison confirmed exact equality to the base after only dropping
that conjunct and unwrapping those two if bodies (plus one explanatory comment); no runtime imports, tests,
validators, GPU work or additional validation helpers were run or created.

## Prefix proof

Let E be the number of local experts, nonnegative counts c[e], and
S[j]=sum(c[0:j]). The outer loop admits only 0<=k<R=S[E]. At entry the cursor is
−1 with end0, or a previously selected expert with its true end prefix. The
cursor moves forward only while k>=end. There must be a first prefix S[j+1]>k,
since S[E]>k. Thus every entered step fetches a valid expert j<E, including the
last positive expert; it cannot attempt the invalid E-th fetch. The search
terminates with a valid expert before the token body executes.

Zero-count prefixes and gaps advance normally. If every count is zero, or E=0,
R=0 and the unchanged outer guard skips the entire search/body. A stride that
jumps over several experts repeats the same prefix updates until its containing
expert is found. No new termination or bounds fallback is required. This is the
same existing signed Int32 prefix/index domain as the total-bound proposal:
counts are nonnegative, prefixes/indices do not overflow. The change neither
broadens that domain nor introduces a new public assertion.

All remaining calculations and effects execute in their previous order:
previous-expert pool/task padding, count-lane selection and shuffle, rank-count
reload on expert transition, source rank/token/top-k mapping, input/weight loads,
elected payload/provenance/weight publication, read/full waits, flag batching,
phase toggle and token stride. Tail/fire/final synchronization and the returned
input phase/count list are byte-unchanged. The tracker keeps its current token's
readiness address; no skipped suffix state is newly exposed to return/push.

## Current native evidence and limits

The actual64a8 total-bound capture still contains the guards; compiler range
analysis has not eliminated them. In N64/F4/direct SASS:

- d3b0/d3c0 compare expert against32/31; d3d0 skips the prefix loop.
- d400 compares the old expert against30; d4e0 skips the count-fetch/shuffle
  body when advancing would exhaust the expert range.
- d440 supplies the expert-bound backedge predicate; d5b0 combines it with the
  token/prefix comparison.
- d5f0 skips the selected-token body via the carried expert-valid predicate.

N128/F8 has the corresponding tests at f020/f030/f040, f080/f170,
f230/f260 and the body-valid branch after f270. N64/F1 retains the same pattern
at d370/d380/d390, d3c0/d4a0 and d5b0. The N64/F4 PTX explicitly contains all
three branches at lines7051–7055,7081–7085 and7111–7112 of the saved capture.
Control artifacts are
`profiles/cu132-recovery0910b-dispatch-total-bound-default-candidate-{case}/codegen`;
exact capture pins are in the parent's total-bound `execution/NATIVE_REVIEW.md`.

This is a source simplification with remaining native control-flow work to
remove, not a quantified instruction or timing saving. A candidate native check
must confirm guard removal, preserved count shuffle/source mapping and all
publication/tail/phase ordering, and inspect register/reconvergence changes.
Keep the earlier ordinary-mainline versus election-recovery routing-weight
scoreboard qualification. No extra workspace, public knob, mapper copy or
runtime fallback is added. Bounded ledger review found no prior trial of this
three-guard removal; it is enabled by the newly added total-bound invariant.


The held source was formatted with the repository-pinned Ruff0.12.8 before
execution. `formatting.json` records exact AST equality and current hashes;
`before_format/` retains the original reviewed patches and snapshots. Earlier
independent reviews describe the same executable AST. Primary remains unchanged.
