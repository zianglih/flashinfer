# Decode-only activation copy with concurrent dispatch preparation

Source-only follow-up to frozen `69c36e20fd01a570b22cedde203cbfcffe66c69a`
(base `7dc9626909834bc70209e09784e9dfdebadceff2`). No additional variant,
GPU work or change to the frozen three-WG trial.

## Verdict

The dependencies permit two decode WGs to copy activations while the dispatch
WG stages routing and executes `dispatch_prep`, before the same common release
init arrival/wait. Preparation requires neither TMEM nor initialized transfer
mbarriers. Its existing subsequent grid/NVLink publication must remain **after**
the common init wait. This is a plausible broader orchestration experiment, not
an implementation-ready one-line move: the inherited dispatch wrapper currently
invokes preparation itself and must be cleanly separated to avoid executing it
twice.

## Exact dependencies

All paths below are relative to the frozen repository.

- `hashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/src/token_comm.py:602–716`:
  `dispatch_prep` initializes its own `smem_expert_count`, synchronizes only its
  128 dispatch threads using barrier 10, counts local staged expert IDs, allocates
  slots through local `expert_send_count` atomics, then writes token/slot words
  into peers' `src_token_topk_idx`. It reads no activation data, score data,
  pipeline mbarrier, TMEM or scheduler work. The shared counter storage already
  exists in `comm_storage` before the proposed point; its own initialization and
  three subgroup barriers provide its shared-memory dependencies.
- The prep peer writes are data writes, not readiness publication. `dispatch_barrier`
  at lines 719–799 subsequently does grid synchronization, publishes counts to
  peers and performs the existing system-fence/NVLink barrier. Consumers and the
  scheduler must remain behind that chain. In particular, the scheduler arrival
  at lines 1612–1616 must not move before the common init wait.
- Pull/TMA mbarriers are initialized later in `dispatch_pull` at lines 823–827;
  no early preparation operation uses them. Scheduler communication is barrier 9,
  dispatch-private preparation is barrier 10, and the tail is barrier 8
  (lines 364–366). The common initialization uses the existing cluster rendezvous
  or CTA synchronization, not a competing dispatch barrier-10 phase.
- Owned kernel `megamoe_kernel.py:1051–1115` allocates the separate common and
  communication storage and initializes pipeline/scheduler objects before the
  staging location. Moving work here does not require moving initialization.
  Keep register redistribution at its original post-init sites: all early copy
  and prep work then uses the original initial 96-register allocation, avoiding
  a new blocking `setmaxnreg.inc` dependency before common arrival.
- Routing is staged with exact subsequent prep ownership in owned
  `token_comm.py:77–114`; IDs are private to the same dispatch lane until prep's
  existing subgroup synchronization. Full capacity remains the prep loop bound;
  inactive rows receive ID -1. The source live-row equality is already checked by
  public validation, so empty and partial ranks require no additional flag.

## Proposed phase order, with no extra synchronization

```text
existing pipeline/scheduler/shared-storage initialization
  decode WGs: copy live activation chunks; each writer async.global proxy fence
  dispatch WG: stage IDs/scores; existing dispatch_prep (barrier 10 phases)
  other roles: no new work
ALL threads: one release init arrival; one init wait
  dispatch: existing dispatch_barrier -> scheduler arrival -> pull/return body
  other roles: existing TMEM/register setup and compute roles
```

The existing CuTe helpers are pinned in `runtime-evidence.json`: regular cluster
arrival has release semantics and the matching wait is acquire; the size-one
case uses the existing CTA synchronization. Every actual activation writer must
fence before arrival. Then dispatch acquires the writers before participating
in the unchanged grid/system publication chain. No store between arrival and
wait can be justified by that handoff, and relaxed arrival is insufficient.
Keep both common sites convergent for all threads and retain all dispatch-only
barrier phases in the same four warps. The source design has no new wait cycle:
activation copying and routing/preparation are finite independent loops.

For queued invocations, the existing prior tail drains all prior communication,
then publishes shared counter resets before its final local resets. The next
local invocation sees its local counters through ordinary stream ordering.
Earlier new token-index writes do not overlap previous readers: the previous
cross-rank drain already completed before that rank can enter its next kernel.
The new path must retain both tail barriers and all reset phases unchanged;
first use still relies on the already initialized workspace. These are source
arguments, not a substitute for queued multirank validation.

## Implementation and measurement constraints

Use 128-lane WG-striped activation ownership over the two decode WGs, retaining
broad CTA coverage for small rows. At H7168/EP8/8192 global tokens and 148 CTAs,
256 copy threads per CTA have at most 25 loop trips versus 17 in the three-WG
prototype or 49 in dispatch-only staging. The alternative trades copy concurrency
for overlap with routing/count/peer-index work; no timing gain follows from those
counts. Both early variants postpone TMEM allocation until this init rendezvous.

The inherited `dispatch_warp_body` (lines 1563–1674) combines prep, publication,
pull and token return. Do not call it unchanged after early prep, replace prep
with a hidden no-op override, or introduce a runtime already-prepared flag. A
future implementation needs a small explicit owned orchestration of the existing
transport primitives, preserving instrumentation and token-back mode semantics;
raw pre-staged calls can retain the inherited complete wrapper. This adds source
ownership, so only pursue it if profiles show the serialization is significant.
No protected shared source, new kernel tactic or public option is required.

Before any retention decision, inspect generated release/wait/fence order,
subgroup participation, actual register/local-memory pressure and vector/generic
copy lowering; qualify empty/skewed queued multirank cases, then compare the full
1–8192 sweep. Nothing in this note establishes generated code or performance.
