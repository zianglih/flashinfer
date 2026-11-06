# V2: fold the existing cross-CTA SF publication into TMA completion

Base: `9334cb34fe9c81653dc4748632f44449e9aecd8d`. Independent patch
`29826937ae480a61b8e46160aa691c52d27e33a1a9309aa0707717a4b3b28d9e`.
Candidate core SHA256: `0179d9634d79bd963597b912182d4e8bafb5b5aa8a8db8b52a2f93b5310a7275`.

This snapshot does **not** include V1's unused wide-SFB storage cleanup. It
changes one kernel file, +20/−39, and leaves custom pipeline implementations,
public APIs, tactic enumeration, weight/SFA/B transports and epilogues unchanged.

## Dependency and count proof

| Transport | Current prerequisite | Candidate prerequisite |
|---|---|---|
| One-CTA cp.async SFB | Local 128-thread SF-full wait, proxy fence, TMA-full wait | Unchanged |
| Two-CTA cp.async SFB | Each CTA local 128-thread SF-full wait + proxy fence; two SF-ready arrivals; CTA0 SF-ready cluster wait; CTA0 TMA-full wait | Same local waits/fences; same two release.cluster arrivals to TMA-full; one CTA0 acquire.cluster wait on TMA-full |
| One-/two-CTA TMA SFB | Existing TMA-full transaction count/wait | Unchanged |
| Operand reuse | Sole leader UMMA empty commit after all channel MMAs; producer empty acquires | Unchanged |
| Accumulator reuse | Existing accumulator acquire/commit, epilogue release and tail | Unchanged |

The installed SDK capture in `scripts/shared_empty_20261026/sdk-pipeline-source.json`
establishes that `CooperativeGroup(Thread, count)` initializes the full arrival
count. `PipelineTmaUmma.producer_acquire` issues one elected
`arrive_and_expect_tx` only on CTA0; it does not issue `count` arrivals.
The TMA transaction-byte total is unchanged. For the existing two-CTA
cp.async-SFB case, the full barrier therefore expects exactly three arrivals:
one TMA expectation plus the same elected SF publication from each CTA.

Exact installed 4.7.1 call trace (complete class snapshot:
`scripts/clc_elected_owner_20261026/sdk-MbarrierArray.py`; version receipt:
`sdk-sync-source.json`):

1. `PipelineTmaUmma.create` builds `MbarrierArray` as `TmaLoad` with the passed
   producer group. Its constructor sets `arrive_count` from that group's size.
   `mbarrier_init` elects one lane of warp0 in **each CTA** and initializes every
   full slot with that count. The deferred common fence and cluster join are
   unchanged. The expected count is three in both local full arrays.
2. `producer_acquire` waits the local empty slot in each CTA, then guards the
   full arrival with `is_leader_cta`. `MbarrierArray.arrive(TmaLoad)` ignores
   `dst`/`producer_mask`; `arrive_and_expect_tx` elects one lane and issues one
   local operation. Thus only CTA0 contributes the TMA arrival, exactly once.
   Increasing `producer_group.size` does not multiply the issuing lanes.
3. Group-two TMA completions target CTA0's full barrier, as in retained code;
   the existing compiled control PTX clears the CTA-rank address bit before
   the group-two TMA operations. Both SF relays explicitly target peer rank0.
   Only the `cta_rank == 0` branch waits this combined full barrier. The peer's
   initialized full array is neither awaited nor a publication target, just
   as before when its count was one. Its pending count has no progress or
   reuse consequence: that array is not repurposed during the kernel lifetime.
4. `producer_mask` remains the existing multicast mask used by the **empty**
   TCGEN completion (`0b11` for the admitted two-CTA layout). The full TMA
   arrival ignores that mask. Hence the leader's sole empty release still
   grants both CTAs permission to reuse the same slot; no new peer full-ring
   wait/advance was introduced.
5. If both SF arrivals happen first, pending arrivals become one and the phase
   cannot complete while transaction count is initially zero. The remaining
   TMA `arrive.expect_tx` adds the complete expected-byte total before lowering
   that last arrival. Conversely, if TMA completes first, the missing SF
   arrivals prevent completion. The same successful leader wait/UMMA empty
   release orders the next same-slot generation in both cases.

PTX requires both the arrival and transaction counts to reach zero, and allows
signed transaction counts. The combined `arrive.expect_tx` adds the expected
bytes before its one arrival. At least one successful wait must precede an
arrival in the next phase. PTX's cluster example pairs remote release.cluster
arrivals with CTA0's acquire.cluster wait on its local barrier. These are the
same scope operations retained here. [PTX ISA 9.4, mbarrier semantics](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-mbarrier).

Thus neither an early SF publication nor early peer TMA completion can release
the combined phase before the TMA expectation, both SF publications and all
TMA bytes have arrived. The candidate changes the barrier address of the SF
arrivals; it does not move local cp.async completion or the generic-to-async
proxy fence. The latter remains necessary before group-wide S2T reads. The
leader uses the existing explicit cluster-acquire helper, **not** the default
CTA-scope `a_pipe.consumer_wait`, on this combined path.

The operand consumer index/phase still advances once per K stage and persists
across work tiles. All producers still acquire the common empty phase before
overwriting a slot. CTA0 first observes combined full completion, then issues
scale copies/all channel MMAs, then performs the same UMMA empty commit.
Consequently the next generation cannot arrive before that successful wait.
The peer may advance after its publication, but its next same-slot local SF
completion requires a producer overwrite, which is blocked by the same empty
ring. No additional reset, phase or ring exists.

PDL startup still prefetches only weights/SFA, acquires at most
`min(num_stages, k_tiles)` initial slots and does not wrap. Those TMA expectations
simply remain pending until the unchanged post-dependency activation/SF work
finishes. The metadata scheduler, PDL waits/triggers and startup producer-state
clone are unchanged. Empty/padded work does not enter the per-K pipeline;
static/CLC, inline/overlap and two-channel M512 use identical producer and
consumer state transitions. Existing producer/accumulator tails and the final
CTA/TMEM teardown remain intact.

## Scope and history

The only added expression derives the arrival count from the **existing**
cross-CTA SF transport predicate; there is no dtype/model dispatch, new tactic,
public knob or policy threshold. Removing the separate readiness array also
removes its matching storage count and private planner argument. V1's unused
wide full array is intentionally still present in this independent snapshot.

This does not repeat `scripts/merged_operand_ring_experiment`: that trial
changed one-CTA producer roles and directly combined 128 cp.async commits with
three TMA arrivals. V2 retains both local cp.async rings and all producer roles;
it combines only the already-existing two-CTA publication relay with the
existing TMA completion. The old role/publisher/merged-ring screens are not
evidence for V2 performance. The proxy-fence requirement in
`scripts/sf_readiness_profile/INHERITED_PROXY_ORDERING.md` is preserved.

## Validation boundary

Scoped pre-commit, syntax and diff checks pass. Actual pure planning methods
pass 1,152 metadata cases and 2,880 capacity cases; no enumerated capacity plan
changes. The abstract protocol check passes all 120 permutations of the five
publication/completion events and 1,600 ring/PDL schedules with depth 1/2/3/7,
repeated work and empty tiles. That model checks count/lifetime dependencies;
it does not substitute for the scope/proxy proof or compile device code.

Approved for the focused paired exact/codegen gate, pending independent root
review. Required evidence: narrow one-/two-CTA, both PDL modes, static/CLC,
inline/overlap, changed data/routes including empty→active and repeated stage
wrap; wide controls; M512 two-channel coverage. Inspect actual full count three,
unchanged TMA byte count, preserved local cp.async/proxy ordering, cluster-scope
wait, removal of the separate readiness init/wait, spills and actual storage.
No GPU or performance result is claimed by this source review.

## Subsequent isolated gate review

The collected isolated V2 gate now passes 96 exact replays per source and 48
compiled pairs: the original 44 pairs plus four narrow M512 pairs. Independent
review verified all 384 kernel artifact hashes, unchanged stages/TMA expected
bytes/local cp.async commits/proxy-fence sites/UMMA commits, and no local spills.
For all 12 affected core pairs, the first operand full slots initialize with
count three; the separate per-stage init ring disappears. Cluster-release
arrivals and cluster-acquire wait sites remain, while the additional TMA wait
is removed for each emitted loop body. Shared allocation decreases by 0 or
128 bytes. `codegen-review.json` contains per-core facts.

Manually traced `clc-gpu0/candidate/config3-fc1-pdl0.ptx` around lines1194–1217:
the MMA warp waits its local SF-full address, executes the async-proxy fence,
maps the operand-full address to rank0, performs release.cluster arrival, then
only CTA0 executes acquire.cluster wait on that same unmapped local address.
The M512 extra confirms two channel tiles remain in the same ownership cycle.
The existing static gate covers unchanged paths; the final composition adds
the narrow two-CTA M512 static counterpart. No isolated V2 timing claim is made.
