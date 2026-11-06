# PDL ancestor-publication owner audit

Read-only audit of clean retained `dea2c065dc8e75ae26fe1ef8123e964db7b4eadb`.
Exact source hashes are in `source.json`. No source changes or GPU runs.

## Conclusion

One physical CTA can republish completed immutable ancestors in preparation and
static GEMM launches. Every CTA must retain its signal, and every dependent must
retain its payload wait. A fixed physical CTA0 publisher is **not established as
safe for CLC**: cancellation may prevent that cluster from executing at all.
For CLC, one publisher per executing cluster is the smallest simple owner with
an existing lifetime guarantee. This is a scheduling-lifetime distinction,
independent of dtype, model, token count, tile extent, and MMA shape.

The [PTX grid dependency contract](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-griddepcontrol)
connects a GPU release before the first CTA trigger to dependent-grid start in
the same memory synchronization domain. The issuing thread's preceding wait
has already acquired completed ancestor writes. This publishes ancestor routing
only; downstream waits still cover the current grid's payload and scales.

## Callsite audit

| Site in retained source | Ancestor publication / dependent reads | Proposed owner |
|---|---|---|
| `blackwell/moe_prepare.py:94–99` | Wait completes routing; FC1 reads expert IDs/count before its wait; prepare payload/SF remain protected by FC1's wait. | Physical CTA `(0,0,0)`, retaining warp0 signal in every CTA. Prepare has a static one-dimensional grid. |
| Common GEMM `:1256–1271`, FC1 startup | Common all-thread wait completes prepare/quantizer and its ancestors. FC2 prefetch reads immutable routing, weights and SFA; B/SFB remain after its wait. | Static: physical `(0,0,0)`. CLC: rank0 of each executing cluster. |
| Common GEMM `:1500–1509`, FC2 producer exit | Republish routing/scales for combine's pre-wait metadata loads. Queued MMA/epilogue output remains covered by combine's wait. | Static: physical `(0,0,0)`. The public FC2 configuration is static. A private CLC specialization would use its executing-cluster leader. |
| `blackwell/moe_finalize.py:131–141` | Only routing rows/weights precede wait; expert output loads follow it. | No change to consumer order. |
| Per-token quantizer `:1033–1041` | Retained CTA0 publication is the existing example; it does not cancel CTAs. | No change. |

All valid launched static CTAs execute their publication/trigger site even when
the live route count is zero. Preparation publishes before its row loop; the
GEMM startup site precedes work; producer-exit is after the possibly empty loop.
No new early return, live-work test, ring change or teardown change is needed.
Zero allocation/invalid zero-grid behavior is not expanded by this proposal.

## Why CLC needs different ownership

[PTX cancellation](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-clusterlaunchcontrol-try-cancel)
may cancel a not-yet-running cluster. Neither that contract nor the
[CUDA CLC guide](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cluster-launch-control.html)
reserves cluster0 or guarantees it launches before cancellation is possible.
Current startup signaling precedes the scheduler's cancellation loop. Thus a
nonzero cluster can signal, cancel the proposed sole publisher, and continue
while a dependent starts without the intended release. Testing cannot replace
the missing scheduling guarantee.

Every executing cluster has its rank0 CTA, and cluster launch/cancellation is
atomic at cluster granularity. That leader waits and publishes before its own
first signal. A peer may signal sooner, but dependent launch still waits for
the leader's signal/completion. No extra shared/global election, allocation,
atomic counter or synchronization is needed. In group1 this leaves the current
per-executing-CTA publication unchanged; group2 can halve it.

Physical CTA0 must test all three original `block_idx()` coordinates, before the
existing division by CTA-group size. Testing normalized X selects both group2
CTAs; testing physical X alone selects every CLC route row with X=0. Neither is
a single physical owner. `cta_rank==0` is intentionally a *cluster* owner only.

## Small isolated candidate, pending parent approval

Use two source snapshots over clean dea2, without touching the shared review:

1. Prepare: add the physical-CTA0 predicate around only `release_gpu()`.
2. GEMM: derive `publishes_ancestors` from static physical CTA0 or CLC cluster
   rank0, then guard its three existing release sites. Keep each trigger in its
   existing control-flow position. In the less common startup branch without
   `publish_routing_before_signal`, all threads of the publishing CTA must still
   fence before their own possible first trigger; do not accidentally let an
   unfenced warp in that CTA trigger first.

No public/private API parameter or format policy is needed. Keep warp0 as the
existing issuer instead of conflating this with single-lane fence changes.
The retained CLC FC1 path is group1, so that path remains unchanged; static FC1
and FC2 reduce publication from one warp per CTA to one warp per grid.

Focused validation should bind the snapshot, verify generated release predicates
and first-trigger ordering, then reuse changing-input/route exact cases with
PDL on/off, zero local routes, static one/two CTA and real CLC cancellation.
The CLC group2 leader path needs an explicitly forced diagnostic if it is not
admitted by the retained public host policy. No broad tests or timing launches
have been performed for this proposal.

## History check

Searched the PDL, generality, decode and optimization ledgers plus task-local
Markdown experiment notes. The retained quantizer CTA0 trial is recorded in
`GENERALITY_AUDIT_2026-10-25.md:139–167`; no prepare/GEMM CTA0 publication trial
was found. The old `pipeline-fence-r1` trial merged pipeline initialization
fences, a different operation; it passed45 exact replays but remained unretained
for noisy/negative performance. This proposal does not repeat that experiment.
