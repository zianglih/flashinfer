# Dispatch count handoff audit

Source baseline: `002ef1454cbacde09972ed5e2ec7dcfe37e55749`.
Candidate: `optimization/counts_overlap`, baseline plus the provisional
TMEM store-width change (`St32x32bOp` repetition 8 → 16), then the count handoff.
No GPU run or performance claim is included in this audit. This candidate must
be compared with its store16 parent. Store16 is not yet retained; if it is
rejected or replaced, rebuild and compare this change against the actual
retained stack before making any retention decision.

## What the trace range includes

`dispatch_exchange_counts_sync` wraps the inherited `dispatch_barrier` in
`kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py`. Its baseline work is:

1. Rendezvous the dispatch warps from every CTA of the source rank. Local
   payload/route staging, local send-count accumulation, and scattered route
   metadata have already run.
2. CTA 0 publishes each source-rank/expert count and atomically adds its token
   count into the destination rank's aggregate expert count.
3. Complete the cross-rank publication barrier, followed by a local dispatch
   grid barrier.
4. Dispatch arrives at named barrier 9 inside the trace range, then closes
   the range and begins pulling input tokens. Scheduler warp 7 originally
   waited at barrier 9.

The range therefore measures local preparation skew, count writes, peer
publication, and the final local rendezvous. It is not just an arithmetic
count exchange. Existing weight TMA, transform, and MMA roles have no work
record until the scheduler receives this full release.

## Candidate and ownership

The owned `W4A16TokenComm.sched_warp_pre_init_wait` now contributes exactly one
nonwaiting arrival to named barrier 9, then acquires each final aggregate
expert count. The scheduler can generate real work while dispatch completes
the global publication barrier. Weight TMA and decode need the final expert
shape and immutable expert weights, not the token payload.

The minimal vendored adapter changes only the receive-sum publication payload
and its memory ordering: high32 contributes one completed source rank, low32
is the original token count, and the existing system-release atomic helper
replaces the relaxed helper. The local `expert_send_count` high32 remains its
original CTA-arrival field. Every source rank contributes once for every
expert, including zero-token experts, after its existing local grid barrier.
Thus readiness is `high32 == world_size`, including heterogeneous per-rank
CTA counts. `world_size * local_sm_count` would have been incorrect.

For the target EP4 case, 64 local experts take two constexpr iterations, with
one expert per lane per iteration. A full-warp ballot keeps all lanes in the
poll loop; completed lanes stop loading their expert. A bounds predicate
handles partial groups. A final `sync_warp` shares acquired visibility with
lanes that had no expert in a partial group. No new full-CTA barrier exists.
Only a failed acquire poll sleeps for the existing helper's 100-unit PTX
`nanosleep` request, matching `spin_wait`'s current default. An already-ready
load never sleeps. This limits traffic from one scheduler warp per CTA;
the delay is a request rather than an exact elapsed time guarantee.

The existing dispatch threads still arrive once at barrier 9. Standalone
return threads, if configured, still wait there. The candidate does not
reuse barrier 9 for another phase or change its participant count. W4A16's
current configuration has no standalone return group.

## Packed-count consumers

A repository-wide search for `expert_recv_count_sum`, `ercs_peer_addr`, and
`sum_packed_init` found no existing high-word consumer:

| Consumer | Existing read contract | Effect |
|---|---|---|
| `dispatch_pull` | Int64 load, mask `0xffffffff` | Token count unchanged |
| `token_back_warp_body` | Int64 load, mask `0xffffffff` | Token count unchanged |
| Scheduler/expert count helper | Int32 sizes view with stride 2 | Low word unchanged |
| Buffer allocation/serialization/bank reset | Whole packed storage | Size and lifetime unchanged |

The candidate's scheduler poll is the only new high-word reader. It loads
the complete Int64 atomically with `sem="acquire", scope="sys"`, before the
scheduler starts the ordinary low-word size reads. No count write can remain
pending after all source-rank contributions have been observed.

## Publication proof

PTX observation order follows a write through subsequent atomic RMWs to the
final acquire load. A system-release contribution therefore synchronizes
with that load even if another rank performs the last addition. The existing
local grid barrier gathers dispatch writes before CTA 0 contributes; its
release/acquire chain is cumulative. The final warp synchronization transfers
acquired visibility across scheduler lanes. See NVIDIA's [observation order,
memory synchronization, and causality definitions](https://docs.nvidia.com/cuda/parallel-thread-execution/#observation-order).

Using a relaxed contribution would not publish staged scores to early idle
CTAs. The system release is necessary: `_prepare_reduce_worker` can read
local routing scores after an immediate DONE record. Each final count
includes this rank's contribution, so its local staged scores precede the
scheduler's work/DONE publication and the consumers' acquisition.

The proof relies on the existing aggregate-count capacity contract: low-word
token accumulation must not overflow into the high word. This does not add
a larger supported count range. All count publishers and polling loads use
the same 64-bit width; the later 32-bit size reads occur after completion.

## Payload and epilogue gates

- `dispatch_barrier` still completes the original cross-rank publication
  before `dispatch_pull` can issue input payload TMA.
- FC1 activation waits for `fc1_ready_counter`, unless the scheduler has
  already acquired a satisfied ready counter. Those releases follow pulled
  payload and source-metadata preparation.
- FC2 activation waits for FC1 completion. FC2 epilogue metadata prefetch
  waits for the accumulator unless its acquired peek-ready flag proves FC1
  completion. That path therefore remains downstream of dispatched inputs.
- Early weight TMA and decoded-weight TMEM stores can fill their normal
  bounded pipeline slots, but cannot start MMA without ready activation.
- Compute-idle CTAs may retire earlier, but remain at the existing tail
  rendezvous until dispatch completes. Tail reduction data remains gated by
  the original cross-rank return drain.

The owned kernel marker becomes `sched_wait_dispatch_counts`; its old name
incorrectly implied the full dispatch metadata barrier. The reduction
preparation comment now names the incoming count publication that provides
score visibility.

## Counter lifecycle and replay

The scheduler uses the already snapshotted `expert_recv_count_sum` bank.
Normal launches still clear the previous bank after global input
publication, and drain publishes those clears before the bank is next used.
The kernel toggles its bank selector only after all producers retire. NCU
mode retains its existing active-bank reset and cleanup publication; the
candidate neither changes barrier rounds nor resets a live polling bank.
No host allocation, stride, ABI, or counter-ring change is involved.

## Earlier attempts and distinction

Read the older ledger as historical evidence, not current-head timing:

- `hashinfer-w4a16-megamoe/integrated-topk-20260918/input-stage-multiwg`:
  three-WG staging was correct but measured GM 0.995738; dispatch-prep overlap
  measured 0.999078. Reassigning staging to decode groups did not justify its
  extra shared synchronization.
- The metadata-first staging variant and its Q1 variant measured 0.949920
  and 0.974916. This candidate does not move payload staging later or add a
  new payload-ready grid barrier.
- `early-scheduler-broadcast` measured 0.987321. It only broadcast the first
  task ID before the metadata wait, so no real weight/decode work was freed.
  This candidate waits for actual final counts and then publishes usable
  work records.
- Per-row and striped-CTA ready variants measured 0.941059 and 0.944671.
  This candidate leaves token-ready ownership and payload pulls unchanged.

## Qualification still required

Static source checks and CPU-only inspection of the installed DSL signatures
are complete. Device compilation, independent numerical references,
repeated/graph replay checks, small-expert partial-warp coverage, nonuniform
routes, sparse/empty compute CTAs, and native SASS inspection remain for the
parent's exclusive GPU queue. There is no asserted performance benefit.

Native SASS should show the expected system-release operation per published
expert, acquire 64-bit count polling, one scheduler barrier-9 arrival, and
the four x16 weight-TMEM stores rather than eight x8 stores. Stronger count
publication adds instruction/ordering cost, so a trace that starts weights
earlier is insufficient by itself: compare full-forward cold-L2 CUPTI timing
against the immediately preceding retained stack.
