# Routing preparation alongside fused input copying

Read-only design review, 2026-09-18. Canonical source:
`83750772b22a1f6158e488496a9adc100d3de08b` (device code from `7dc9626`).
Three-copy-WG candidate inspected: `b215a7d22784fd7675452cb9df70d6e29dcf0722`.
No implementation, GPU run, or measured improvement is claimed here. This is
a follow-up to b215, not another implementation of that candidate.

## What overlap exists now

The current kernel can decode FC1 weights before the **remote pulls** finish,
but it cannot decode useful weights before **source staging and dispatch
publication** finish:

1. Canonical [kernel:1323](hashinfer/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1323)
   runs `stage_inputs` before `dispatch_warp_body`.
2. Shared [transport:1579](hashinfer/hashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/src/token_comm.py#L1579)
   runs preparation, then the grid/NVLink dispatch barrier, then arrives at
   dispatch-to-scheduler barrier 9 at line 1616. Only then does it start pulls.
3. Canonical [kernel:1148](hashinfer/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1148)
   waits on barrier 9 before generating/publishing scheduler work. Weight and
   decode roles first consume that work at lines 1165 and 1407. Early scheduler
   initialization at line 1115 does not publish a work record.
4. The activation role separately waits for FC1 input readiness at line 1212;
   the weight role has no corresponding activation wait. That is the existing
   decode-versus-pull overlap.

Consequently b215's TMEM handoff after copying does not sacrifice useful weight
decode during source staging. Its important new dependency is the reverse one:
dispatch cannot start routing preparation until TMEM allocation and the
544-thread retrieval rendezvous finish. Canonical dispatch did not wait for
TMEM. Small inputs could expose that extra dependency even when copying is fast.

## First, distinguish the small change

b215 currently copies activations with dispatch plus both decode WGs, joins the
TMEM retrieval barrier, then stages routing. A small isolated follow-up can move
only dispatch's `stage_routing` call **before** that same retrieval barrier,
after dispatch finishes its own activation-copy strip:

```text
warp 0:       TMEM allocation ------------------ join retrieval barrier
dispatch WG:  activation copy -> stage routing - join retrieval barrier
decode WGs:   activation copy -> writer fence -- join retrieval barrier
dispatch WG:  unchanged inherited dispatch_warp_body
```

This retains three activation-copy WGs and the full inherited transport body.
It hides only ID/score staging under any remaining decode-copy/TMEM time; it
does **not** overlap the three preparation barriers, expert-count atomics, or
peer-index writes. When dispatch already has the longest copy strip, this move
may hide little. At K8, live routing destination writes are 96 bytes/token,
versus 14,336 activation bytes/token for H7168; capacity-tail ID masking is
additional. Treat it as a small orchestration experiment, not a likely large gain.

All IDs/scores remain ready before the existing dispatch publication. Neither
decode copying nor TMEM allocation reads those buffers. The change introduces
no barrier, participant, routing ownership, public option, or wrapper.
The b215 [stage_routing:76](input-stage-multiwg-retrieve/hashinfer/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/token_comm.py#L76)
and [handoff:1144](input-stage-multiwg-retrieve/hashinfer/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1144)
are the exact sites.

## Concrete larger opportunity: prepare routing during two-WG copying

Keep b215's post-initialization TMEM allocation and existing retrieval barrier,
but assign activation copying to the two decode WGs. Dispatch concurrently
stages IDs/scores and calls the existing `dispatch_prep` primitive. Both paths
then join the same 544-thread retrieval barrier. Dispatch continues with the
unchanged publication, scheduler arrival, pull and optional token-return phases.

```text
existing pipeline-init wait
warp 0:       TMEM allocation -------------------- join retrieval barrier
dispatch WG:  stage routing -> dispatch_prep ------ join retrieval barrier
decode WGs:   activation copy -> writer fence ----- join retrieval barrier
dispatch WG:  grid/NVLink publication -> scheduler arrival -> pull/return
compute:      original scheduler/TMEM-dependent roles
```

This differs from the older
[pre-init proposal](input-stage-multiwg/DECODE_COPY_DISPATCH_PREP_DESIGN.md):
it keeps allocation after the original cluster-init wait and overlaps allocation
with copying/preparation. It adds no common init rendezvous or barrier phase.
Retain b215's 544 fused participants (warps 0–4 and 8–19); raw pre-staged calls
retain the original 416 participants and inherited dispatch body.

### Dependency proof

- [Shared preparation:602–716](hashinfer/hashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/src/token_comm.py#L602)
  reads only routing IDs and initialized local counters. It initializes its
  own shared expert counts and uses only dispatch-private barrier 10. It neither
  reads activation data nor needs TMEM, pull mbarriers, or a scheduler record.
  Keep capacity as its `num_tokens` argument because line 703 uses it for peer
  metadata stride; do not substitute live rows.
- Copying touches the activation destination only. Every copy writer retains
  its `async.global` proxy fence before the retrieval handoff. Dispatch joins
  that existing handoff before entering the original grid/system publication.
  The barrier gathers writers; the proxy fence supplies the cross-proxy edge.
  Neither operation replaces the other. b215's
  [runtime/source proof](input-stage-multiwg-retrieve/README.md) still applies.
- Preparation's peer-index writes are data writes, not readiness publication.
  Keep [dispatch_barrier:719](hashinfer/hashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/src/token_comm.py#L719)
  and scheduler arrival strictly after the handoff. No next phase can read
  unfinished activations through an early count or scheduler publication.
- Do not move register redistribution: early work uses the initial 96 registers.
  In particular, no early epilogue register increase may wait for a dispatch
  decrease that now occurs after this handoff. Keep the original control80,
  dispatch64, epilogue144 and two decode96 budgets.
- Empty/skewed ranks still execute the same barrier participants. The finite
  copy and preparation loops do not await each other, so the source structure
  introduces no new cyclic wait. Queue safety depends on retaining both existing
  tail publication/reset phases; source indices are not part of counter resets.

### Ownership and expected benefit

The existing standalone FlashInfer
[dispatch kernel:92–147](/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/flashinfer/flashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/src/dispatch_kernel.py#L92)
at `fc676ce6821c1dcf51ef2966f1c4ae4da3aae0d7` already orchestrates preparation,
publication and pulls as separate primitives. Reuse those primitives. Do not
modify the shared drop, make preparation a no-op override, execute it twice,
or add a runtime `already_prepared` state.

The owned fused path would need approximately 80–100 lines of explicit
post-preparation orchestration/argument forwarding from shared lines 1593–1673,
plus the early prep call and existing instrumentation. This is real maintenance
cost, even though the underlying transport algorithms remain shared. There is
no existing post-prep wrapper to call. Keep raw pre-staged calls on the inherited
complete body through compile-time dispatch.

Let A be allocation time, C2/C3 the two-/three-WG copy critical paths, R routing
staging, and P preparation. Before common publication, b215 is roughly
`max(A,C3)+R+P`; this candidate is roughly `max(A,C2,R+P)`. These are dependency
models, not timing predictions. At H7168, EP8 and 8192 evenly divided global
tokens, 148 CTAs imply at most 25 versus 17 vector-copy loop trips. The candidate
must hide enough R+P to repay lower copy parallelism and possible memory contention.

Prefer the inexpensive routing-staging move first if b215 is retained. Pursue
the larger split only if profiling or a controlled prototype shows material
preparation serialization; a tiny/noise-level gain does not justify the copied
orchestration. Validate generated barrier ordering, vector/generic lowering,
register/spill changes, queued graph exactness and scoped sanitizer coverage,
then compare the complete 1–8192 full-forward sweep against the retained source.

## Why not simply move deterministic reduction earlier

Canonical [kernel:1428–1497](hashinfer/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py#L1428)
already prepares decode workers before the final transform producer wait and
other workers while dispatch drains returns. Actual combine loads follow the
second common tail barrier. The dispatch return counter describes expert-side
FC2 production ([shared:1328](hashinfer/hashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/src/token_comm.py#L1328));
it is not a destination token/hidden-block completion certificate for all K
remote route contributions. Reading combine terms before the drain would need
a new completion/publication protocol for both return modes and repeated
invocations. Do not infer readiness from local scheduler retirement or turn
ordered FP32 reduction into atomic/TMA accumulation. The input-preparation
co-design above is a smaller opportunity with existing readiness boundaries.
