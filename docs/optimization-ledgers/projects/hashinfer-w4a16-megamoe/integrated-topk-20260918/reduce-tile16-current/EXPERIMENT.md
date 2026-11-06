# Wider ordered combine on the retained PR8 kernel

Candidate `d9d510f7a9e1764c96778c36b3f1bae3c6d2278e` is the exact preserved,
previously unrun `34c9a3a57d42e47f91a582e9f669bf35508d9a22` reducer change,
cherry-picked onto PR8 head `534a623c7fc167837b5946b10e6b9ed1e22c9d3a`.
Its base reducer blob is identical at 7dc, retained3de, and 534a623. This branch
does not contain PR9's FC1 routing-weight placement or other unpromoted trials.

Each worker reduces 16 hidden elements, sharing each FP32 route weight and
index across two 128-bit vectors. It retains the original ordered FP32
multiply/FMA and final BF16 rounding. Loads/stores remain 128-bit and output
alignment remains 16 bytes. The redundant inner token guard is removed because
the sole caller bounds every worker by rows * hidden_tiles; supported H%32
also guarantees complete 16-element tiles.

The larger accumulator becomes live after FC2 completion. No barrier, grid,
warp role, register budget, public option or tactic changes. This differs from
the rejected I1 paired-slab experiment: I1 preserved the first stripe and paired
later nonadjacent slices; this trial uses width16 for every worker. It also
differs from the PR9 narrower unweighted-worker trial.

Potential benefit: fewer score/index operations and more independent packed
arithmetic per worker. Risks: fewer active workers for decode, more register
state, and two memory instructions where a larger alignment contract could
have allowed one. Do not add that contract. Source review does not establish
native vectorization, lack of spills or speedup.

Run the full13 AUTO4/O3 cold-L2 CUPTI sweep against same-hu15 A2, retaining
all100 samples and requiring104 same-contract outputs to match exactly. Decode
4–512 drives retention;1/2 are report-only and allthree prefill rows are checked.
Per the user's updated policy, no sanitizer runs during optimization iteration;
defer sanitizer until the final selected implementation. Inspect numerical or
generated-code evidence as required by actual benchmark results.


## Selected T4 codegen follow-up

The matched retained3de/L1 capture onhu59 passed eager/graph repeats and all8
paired raw outputs (4nonempty,4empty). All64 ABI resource reports retain
REG96/STACK0/LOCAL0/shared1024, with no local spill traffic. The selected
N64/epi reducer remains128-bit: width16 issues two halves, exposing the
complementary half-sector pattern. It also changes dequant-role register
allocation/scheduling outside reduction. See
[the complete generated-code review](codegen-selected-t4/MATCHED_T4_REVIEW.md)
and immutable422-member evidence archive. This is diagnostic evidence, not
a new timing run or promotion. hu59 closed idle.
