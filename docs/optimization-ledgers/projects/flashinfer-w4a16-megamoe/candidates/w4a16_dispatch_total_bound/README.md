# Stop dispatch at the actual received-token total

Held source-only proposal on source03459447, transport `41bf279e646f7a7fcd07ce91b0bdc737da7e8f79ebe13fb666a324b43e4a0bee`.
Patch `42dbb68c38ad737da971b74c113ba9cea178a1cd957af870784606ddff685c43`; proposed transport `199a9c28f20327b4db40626b13094d3578a811472d4973f52d871f0a81b8e97a`.
No primary changes, runtime imports, compilation, GPU work, timing, or new knob.

The patch adds one lane-local constexpr sum of the existing cached expert-count
list and one full-warp `warp_redux_sync(..., "add")`, then replaces only the outer
loop guard with `token_idx < total_received_tokens`. It does not reload counts,
allocate workspace, add a per-token condition, change the inner prefix/rank
mapping, or alter the payload/publication sequence. `"add"` is the existing CuTe
API spelling; see `flashinfer/topk_varlen/kernels/gvr2_topk_decode.py:245`.

## Source proof

- Each valid expert belongs to exactly one `(list index, lane)` pair. Padding
  entries remain zero. The counts are the same immutable low32-bit nonnegative
  values used by the old expert-prefix loop. A full-warp sum is uniform and
  equals that loop's final `expert_end_idx`. All32 lanes reach the reduction
  after the existing initialization synchronization.
- For every token index below that total, some expert prefix contains it. The
  unchanged inner scan reaches the same expert, pool offset, readiness tile,
  source rank, token and top-k slot as before. Global-warp striding is unchanged,
  so every existing work item is visited exactly once by the same warp.
- An index at or beyond the total previously scanned the remaining expert
  suffix and performed no pull. Those final cursor/pool/task-offset updates are
  not returned or read by `flag_tracker.fire()`: the tracker already owns its
  pending addresses. Omitting them leaves the input phase, cached count list,
  full write drain, ordinary-store publication sync, partial flag release and
  inherited token-back handoff unchanged.
- Zero received tokens skip the body and retain phase0. A zero-length expert
  list has lane sum0 and uniform total0; the dispatch slice still runs its old
  initialization and tail. This does not add zero-expert support to other kernel
  components. Empty expert prefixes between live experts are still scanned.
- Signed Int32 arithmetic inherits the existing valid prefix/index domain.
  Within that domain every partial sum of nonnegative counts is bounded by the
  total, so reassociation introduces no new overflow. This is not a new promise
  for counts or strided indices exceeding the old Int32 domain, and no API
  restriction or defensive fallback is added.

## Scope and admission limits

The substantive ledger is `w4a16_optimization_experiments.md`; its Entries085–089
cover write/read overlap, two pull barriers, scalar-load placement, post-flag
convergence and the elected writer. Bounded searches there and in the older
`PERFORMANCE_LEDGER.md` found no prior received-total outer-bound trial. Earlier
CLC metadata scans belong to a removed scheduler and do not implement this pull
loop bound.

This trades a startup reduction and one live total for fewer idle/exhaustion
prefix scans; no speedup is established. Native review must check that the
reduction remains outside the loop, count initialization and full-mask
participation are correct, and payload/election/read/full-wait/publication/tail
ordering remains intact without resource spills. Preserve the earlier
mainline-versus-election-recovery routing-load dependency qualification. Existing
empty-rank, skew, partial-tail, F1/F4/F8 and reused-return cases cover the changed
termination boundary; no additional validation machinery is prepared here.
