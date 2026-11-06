# Two input buffers per BF16 dispatch warp: held design

Source-only review of source03459447 / transport41bf279e. No primary changes,
runtime imports, compilation, GPU work, timing, or implementation are included.
The separate received-total loop bound is a smaller candidate; this design does
not require or combine it. No earlier two-input-buffer dispatch trial was found
in the substantive `w4a16_optimization_experiments.md` or older
`PERFORMANCE_LEDGER.md`. Entries044 (B4/S3),059 (ACC1),081 (raw6) and the raw4/B3/S2
trial show that changing the compute rings has real costs; none tests this input
lookahead protocol.

## Decision and scope

The memory-ownership protocol is feasible, but this is a broader scheduling and
layout experiment, not a barrier deletion. Keep four dispatch warps, five total
warpgroups, two decoders, existing public tactics and output semantics. Design
only for now: a clean implementation still needs an explicit CuTe scalar carry
across the rotated mapping loop, a complete transport/fitter specialization, and
native inspection for register cost. Do not duplicate the expert/rank mapper.

Current owned `token_comm.py:200–315` has one scratch row per warp. It completes
that row's input before issuing its pool store, then completes the store's SMEM
reads before the next input overwrites it. Two distinct rows allow the next
input transfer to start before waiting for and storing the current row. They do
not remove input completion, SMEM read completion, ordinary-store publication,
or return/tail synchronization.

## Storage and exact source-derived fitting

Use plane-major flat arrays with indices `stage*4 + warp` for barriers and
`(stage*4 + warp)*hidden_bytes` for scratch. Keep the inherited field names and
plane0's relative indexing: `token_back_by_push` uses barrier `warp` and scratch
`warp*hidden_bytes` (`src/src/token_comm.py:1355–1415`), and its caller passes
those field base pointers unchanged (`:1652–1676`). Increasing field lengths
changes later field offsets; all access must continue through the same selected
storage class. The standalone-return layout is outside this Mega specialization.

At H7168/E256, current communication storage is58400B:
`4*8 + 256*4 + 4*(7168*2)`. Two planes make it115776B:
`8*8 + 256*4 + 8*(7168*2)`, an increase of57376B (57344 scratch +32 barriers).
The existing control/communication structs align to16B; raw, scale and activation
arrays align to128B, in exactly `_smem_size` allocation order
(`megamoe_kernel.py:418–430`). Raw FP4/SF cost16384/2048B per stage; activation
cost16384B per N64 stage or32768B per N128 stage. Each raw or activation barrier
stage changes the control struct by16B. Applying those sizes and alignments:

| C2/N | Input planes | Raw/B/D | Control B | Comm B | Total user SMEM B | Result |
|---|---:|---|---:|---:|---:|---|
| 64 | 1 | 5/3/3 | 352 | 58400 | 200064 | saved native control |
| 64 | 2 | 4/3/3 | 336 | 115776 | 239104 | exceeds232448 |
| 64 | 2 | 3/3/3 | 320 | 115776 | 220544 | source-derived fit |
| 128 | 1 | 4/3/2 | 320 | 58400 | 230784 | saved native control |
| 128 | 2 | 2/3/2 | 288 | 115776 | 251264 | exceeds232448 |
| 128 | 2 | 3/2/2 | 288 | 115776 | 236928 | exceeds232448 |
| 128 | 2 | 2/2/2 | 272 | 115776 | 218496 | source-derived fit |

These new totals are arithmetic from current source and saved4bf
`compiled.raw_fit` descriptors, not new compiled allocations. Controls are the
completed `dispatch-post-flag-sync-default-auto13-direct-001-auto.log` records;
no timing fields or active0345 outputs were read. TMEM stays512 columns, ACC2,
with D3 for N64 and D2 for N128. Production N128 gives up an activation stage and
two raw stages; extra input overlap must pay for this loss.

Use the existing full layout fitter for other H, E, C1/C2 and alignment cases.
A private compile-time profile selects two planes only if its existing
B=(3,2), raw=(5..2) search fits; otherwise retry the unchanged one-plane profile.
If neither fits, retain the existing error. Select transport behavior, its
storage class and kernel allocation together before tracing the device body;
never fit one class and allocate another. A runtime stage selector or a mutation
of a previously cached/traced transport object would be an avoidable hazard.
No public capacity knob or shape table is needed.

## One-token lookahead state and sequence

Retain one monotonically advancing expert/rank mapping cursor and the immutable
per-lane count list. Move the existing mapper into one small private JIT helper
only if needed to share prologue and body. A pending token needs approximately
six scalar values: pool index, readiness tile, source rank, source token,
source top-k and routing weight. Source pointer arithmetic may be rebuilt from
these; do not carry whole transport/tensor/scheduler records or duplicate the
mapping cursor. Carry the current descriptor explicitly while mapping the next;
map/issue next input and load its weight before waiting for current input.
Actual CuTe loop SSA and first native use remain inspection requirements.

1. Initialize both per-warp input barriers and their next phases to0. Map token0;
   if valid, issue its input into plane0 and establish its expected transaction.
   An invalid first token takes the existing empty tail without an input issue.
2. With token i pending, map i+1. If valid, complete all prior pool-store SMEM
   reads with `cp_async_bulk_wait_group(0, read=True)` **before** issuing input
   i+1 into the other plane. On the first iteration this is an empty wait; it
   can be kept simple or omitted in the explicit prologue. Issue/expect i+1,
   retaining its compact descriptor and early scalar weight load.
3. Wait for token i's own input barrier and phase. For F>1, full
   `wait_group(1)` before its pool store leaves at most one prior incomplete
   write group. In the elected issuer, store current payload and provenance,
   commit that group, and store its weight. There are now at most two pending
   groups for that issuer. F1 can omit the pre-store wait because its preceding
   publication completed every earlier group.
4. Before a full batch publishes, retain full `wait_group(0)` in all lanes and
   the existing warp synchronization. Then accumulate the **current** readiness
   address with constant tracker phase0. F1 keeps its unconditional full wait
   and synchronization before every publication. Rotate to the next pending
   descriptor; if absent, leave the loop only after current processing finishes.
5. Retain the full write drain and synchronization before a partial tail's
   `fire()`, then the final warp synchronization and inherited return handoff.
   No issued lookahead may be discarded at exhaustion.

The scratch-reuse wait must be READ0, not READ1. When body i is about to issue
input i+1, that plane can still be the source of output i−1, the **newest**
previously committed group. READ1 may exempt precisely that group. READ0 permits
its destination write to remain pending while guaranteeing safe scratch
reuse. The full wait1 in step3 limits outstanding destination writes; it is a
different obligation. Input TMA transactions use the per-plane mbarriers and
are not entries in the issuing thread's cp.async.bulk store-group queue.

Use the full-warp deterministic election contract already relied on by the
one-plane implementation: all32 lanes reach the same elected scopes. All lanes
execute group waits, so the owner is included; the next full-mask input election
cannot run ahead of that owner's source-read wait. Election is convergence,
not memory publication. Full write wait + warp sync before flags still transfers
completion and ordinary provenance/weight-store visibility to rotating release
lanes. Native must confirm the election mask and issuer/control-flow lowering;
preserve the known mainline-versus-election-recovery weight-dependency limit.

## Phase, tail and zero-work invariants

Keep one next-phase bit for each plane; toggle a plane only after consuming its
input completion. A warp processing n tokens uses plane0 ceil(n/2) times and
plane1 floor(n/2) times. Return `ceil(n/2) & 1` as plane0's next phase, **not**
`n & 1`. Returning the count list unchanged lets inherited push keep its existing
expert traversal. Zero tokens return0; one token drains plane0 and returns1;
two tokens drain both and still return1; three tokens return0. No outstanding
input or source-read dependency survives the final handoff. Plane1 remains
reserved and unused during inherited return; no storage alias or new barrier
invalidation is needed solely because it is idle.

Lookahead exhaustion must not use the advanced mapping cursor as the current
loop's validity guard: crossing the last expert while mapping i+1 must still
consume/store/publish pending i. This is the main loop-rotation correctness trap.
Batch phase remains the constant0 used today, independent of both input phases;
using either input phase in the tracker would introduce unintended releases.

## Limits and later admission, if selected

At the captured production launch there are148*4=592 dispatch warps per GPU.
Roughly balanced rows per rank are about globalT; many <=512 shapes therefore
have at most one token per warp and no steady lookahead benefit, while still
paying for shallower GEMM rings. Skew may differ. An optional compile-time bound
`world_size*capacity*topk <= actual_dispatch_CTA_count*4` could prove lookahead
unreachable and retain one plane, but the actual grid is formed after today's
fitter. This is only a possible general reachability check, not a selected
heuristic, correctness bound on balanced routing, or promised sweep gain.

The current64-register dispatch allocation makes the extra live descriptor and
weight a material risk. Native admission must show both inputs outstanding in
the intended order, per-plane phase wrap, READ0 before overwrite, full1/commit
bounds, full0 before every publication, stage0 return phase, and no spill or
unintended early scalar dependency. Verify actual selected resources rather than
accepting this arithmetic as native evidence.

Existing large-skew EP2 cases have12/13 pulls per warp and F1/F4/F8, useful for
odd/even phases, partial tails and empty peers. Their small H does not exercise
production N128 raw2/B2 fitting. If selected, root identified a targeted unchanged
oracle case at large H and a capacity-forced one-buffer fallback case as needed
additional coverage. No test or runtime package is created now. Those limits,
plus the compute-ring tradeoff, argue for keeping this broader direction held
while trying the smaller received-total bound independently.
