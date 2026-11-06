# Operand and scheduling audit at cb35

Read-only source audit at `cb35c42f6143aa08546ee1c6c8d6e6913c6cf03f`, with
existing exact/codegen evidence. Canonical source remains untouched. The isolated
candidate is unstaged in `flashinfer-operand-announcer-review`. The all11 exact
and codegen qualification passed on GPU1; matched performance runs follow below.
`source.json` pins the source and inspected codegen.

## Candidate: one owner announces the complete operand transaction count

The current shared full barrier expects two arrivals per stage. Weight warp0
announces A/SFA bytes and activation warp1 separately announces B/SFB bytes.
Both then issue their own independent TMA copies. One full wait on the MMA
warp already joins all bytes, followed by one empty-stage release.

Proposed small source-only diff:

1. Set the operand full-barrier producer count to1.
2. Have weight `producer_acquire` announce the sum of existing weight and
   activation transaction-byte terms for the whole CTA group.
3. Replace activation `producer_acquire` with the same local empty-stage wait
   through `operand_pipe.sync_object_empty.wait(index, phase)`.
4. Update the two existing ownership comments. Change no other waits,
   transfers, states, barriers, branch predicates or scheduler quorums.

The activation warp retains full independence: it can issue B/SFB as soon as
its existing empty barrier and PDL dependency are ready. It does not wait for
the weight warp to announce. The expected count is known at compile time and
includes every channel tile and both CTAs exactly as before.

The proof uses the actual two-counter barrier semantics. Before the weight
announcement, pending arrivals stays1, so no full phase can finish even if
activation or follower-CTA weight completions make tx-count negative. The atomic weight
arrive-and-expect adds the complete stage byte count and clears the one pending
arrival. Thereafter tx-count equals all stage bytes not yet completed, including
activation data that has not been issued. It reaches zero only when every
operand transfer is complete. Dynamic MMA N does not change these transfer
extents. The existing local empty waits prevent either producer from writing
the next generation before the previous MMA's empty release.

CUDA13.2.2 PTX explicitly permits signed transaction counts and requires both
pending arrivals and tx-count to reach zero for completion. This is a semantic
proof, not a runtime qualification. See [mbarrier contents and phase
completion](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-mbarrier-contents).
The combined per-stage byte count is below twice the per-CTA SMEM limit and
therefore well below the signed transaction counter's magnitude limit.

The SDK's existing leader guard still elects the only weight arrival. There is
no follower arrival: A/SFA/B native TMA group2 operations and the SFB helper's
existing leader-barrier redirection complete against that same leader barrier.
Each producer retains its own local empty wait. MMA waits for the leader full
barrier before releasing both local empty barriers, so the next ring generation
cannot overlap the previous generation's operand use. FP4 transaction counts
use the packed transfer size, not the larger unpacked shared-memory footprint.

`verify_static.py` checks the three-edit AST scope and enumerates 1,693,696
completion/announcement states over 478 feasible transfer geometries. The
maximum combined count in that bounded enumeration is425984 bytes versus the
signed limit1048575. This complements, rather than replaces, the lifetime proof.

Existing SASS for MXFP8 N256 FC1 contains an elected activation
`SYNCS.ARRIVE.TRANS64` with69632 expected bytes before the B/SFB TMA sequence;
see `activation-arrival-existing.sass`. Removing that arrival is a real
instruction target. A future compiled candidate must verify the expected
reduction, unchanged resources and complete byte counts before timing.

## Findings not proposed as patches

- CLC request-before-metadata-acquire was already rejected: it claims work
  while the local metadata ring is full and can worsen workload balance.
  Preserve the bounded claim policy, response reuse fence and response tail.
- Ordinary scheduling already has no local metadata ring. Centralizing those
  reads would add synchronization and repeats an unsuccessful prior trial.
- SFB's per-row-block source elections look redundant in PTX, but inspected
  SASS already merges the transfer sequence without separate elections.
  Hoisting the source election is not yet an instruction improvement.
- Full and empty rings protect different lifetimes. Operand tail, final CTA
  join, accumulator completion and peer TMEM deallocation remain required.
- In one-CTA kernels, the all-thread TMEM retrieval barrier is also the first
  rendezvous publishing warp0's deferred pipeline barrier initialization.
  Producers/scheduler cannot begin pipeline activity before it without another
  initialization rendezvous. A two-CTA-only bypass would complicate policy.
- Pure pointer/layout setup can move before that barrier, but most CuTe tensor
  partition construction is compile-time. No substantial independent startup
  work was demonstrated in generated code to justify rearranging role scopes.

## Qualification and performance status

- Candidate kernel SHA256: `5d3b3b003b37052671aa362bb2d41166e64dca7e12ae14ab11f6da838a3c9bd4`.
- Control SHA256: `b45b218b7bece21cf8c967bf88dc0dbfec32a5ebbb7472ac871e8e84ae8a2328`;
  remote source receipt has HEAD99f4 plus the exact source later committed as
  cb35. Deployment compared all342 captured source hashes to the cb35 checkout.
- All11 configurations passed176 storage-bit replays per source and88 matched
  compiled kernels. This covers all four formats, static/CLC, PDL off/on,
  one/two CTA, narrow/wide N, M512, SiTU/Swiglu/Relu2, live/empty/reactivated
  routes and repeated ring use. No spills, local memory or stack were generated.
- Every emitted expected-byte immediate and operand full-barrier initial count
  matched the protocol: control count2 with W/A announcements; candidate count1
  with W+A. PDL-off code remains free of GDC instructions.
- Codegen removes352 static SASS transaction-arrival sites across88 variants;
  the protocol benefit is one fewer executed full-barrier arrival per K-stage.
  This is not a blanket static-instruction reduction: config7 FC2 has16 extra
  emitted PTX wait sites in each scheduler/PDL variant after compiler expansion
  of the simplified loop. The other84 pairs have identical static wait counts.
  Independent inspection traced a control K-loop unrolled by2 with a backedge
  up to18 versus18 explicitly emitted candidate iterations: both execute18
  activation empty waits per tile. Source control flow and logical wait
  iterations are unchanged. Registers are
  unchanged in81 pairs, decrease in5, and increase by2 in2 static config7 FC2
  pairs. No shape-specific unroll policy is added; measured timing decides.
- Independent protocol review: `../../scheduler/sole-announcer-review/REVIEW.md`.
- Matched CAAC screen completed for V3/GPU1, V41F/GPU5, K3/GPU6 and N3U/GPU7.
  Tokens4/64/4096/16384, all four formats, unchanged public100-sample CUPTI
  cold-L2 methodology and10 warmups, frozen native winners and exact routes.
  C is the fresh cb35-equivalent control, A the isolated candidate. No external
  TRTLLM/legacy rerun, autotuning or sanitizer. Native C++ caches are retained.
  All32 family processes passed and all four GPUs were released. Independent
  aggregation and full raw evidence are owned under the scheduler review notes.

The protocol was sent to the parent before source editing. No descriptor
prefetch, row-owned prepare or extra tactic axis is proposed.

## Additional generated-code audit

Root checked `_absmax` against the captured retained FC1 SASS. The scalar-looking
Python loop already becomes eight native `FMNMX3` operations with absolute-source
modifiers (`combined/gate-evidence/outputs/candidate/config0-clc0-fc1-pdl0.sass`,
lines1433–1463). Replacing it with explicit three-input max PTX would duplicate
compiler lowering; no such source rewrite was made. This does not establish
that every possible reduction schedule is optimal.
