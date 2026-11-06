# Fused input staging startup audit

Original source audit, 2026-09-19, pinned to then-PR #8 head
`534a623c7fc167837b5946b10e6b9ed1e22c9d3a`, archived under `source/` here.
Historical experiments are under `../integrated-topk-20260918/`.
The initial audit made no kernel edit or GPU measurement. The follow-up below
records subsequent experiments; the source walkthrough retains its original pin.

## Follow-up ledger review: implemented, none retained

The audit led to six completed staging candidates. **None earned retention.**
The batch used same-node `d01f074` controls, EP8 B300, H7168/I2048/E256/K8,
O3/AUTO4 and 100 cold-L2 CUDA-graph CUPTI rank-MAX samples per shape.
Ratios below are control/candidate; above 1 is faster. Decode is the geometric
mean over T4–512, while each prefill row is checked separately.

| Direction and candidate | Decode | Prefill 4K / 8K / 16K | Outcome and evidence |
|---|---:|---|---|
| Metadata-first weight/dequant runahead, `3cd1f70` | 0.949920× | 0.978707 / 0.983742 / 0.994360× | Every shape slower; [P1 result](../integrated-topk-20260918/metadata-first-staging/decode13-benchmark-hu59/RESULT.md) |
| Cheaper all-rank payload publication, `44b5` | 0.974916× | 0.975216 / 0.980820 / 0.989371× | 1.026314× versus P1, still slower than retained control; [Q1 result](../integrated-topk-20260918/metadata-payload-publication/RETENTION.md) |
| Per-row source readiness, `4cd6162` | 0.941059× | 0.954419 / 0.942848 / 0.991321× | Slower; also changes copy ownership to one CTA per row; [R1 result](../integrated-topk-20260918/row-ready-staging/decode13-benchmark-hu59-v2/RESULT.md) |
| Striped copies with source-CTA readiness, `ca05e165` | 0.944671× | 0.970046 / 0.984111 / 1.008488× | All decode rows slower; 16K aggregate affected by drift; [S2 result](../integrated-topk-20260918/cta-ready-staging/decode13-benchmark-hu15-recovery/RETENTION.md) |
| Initial scheduler-ID broadcast before input publication, `2bb3a02` | 0.987321× | 0.999837 / 0.959524 / 0.987197× | Mixed with material T32/T64 regressions; [startup comparison](../integrated-topk-20260918/parallel-startup-node-20260919/performance/RETENTION.md) |
| Dispatch staging before pipeline creation, `ec7428d` | 1.000089× | 1.004228 / 0.963794 / 0.989230× | Essentially flat decode, prefill regressions; [startup comparison](../integrated-topk-20260918/parallel-startup-node-20260919/performance/RETENTION.md) |

All six completed candidates preserved their controls' 13 selected tactics and
104 finite bit-exact benchmark outputs. The interrupted hu59 striped run is
excluded; S2 is the complete hu15 restart. Broader qualification was not run
for these unretained candidates. Serial controls do not remove temporal drift.

The rejection is a full-forward performance decision, not proof that overlap
is impossible. P1 added a third normal cross-rank publication. Q1 reduced its
cost but still lost to baseline. Row readiness changed copy ownership, and
striped readiness added publication/polling work. Preinit staging trades
potential copy/init overlap against later common-init/TMEM startup. These are
plausible costs, not a measured decomposition of the regressions.

**The requested causal diagnostic is still missing:** the inspected evidence
does not establish first weight/dequant activity before staging completion,
or its effect on first MMA. The final startup comparison also explicitly says
generated placement was not captured for `2bb`/`ec742`. The next useful step
is to locate an exposed dependency window, not repeat these same candidates.
No isolated pull-mbarrier-init or histogram-zero-only hoist trial was found
in the inspected ledger.

The [batch ledger](../integrated-topk-20260918/EXPERIMENTS.md) and
[batch summary](../integrated-topk-20260918/ROUND_SUMMARY_20260919.md) close with
no promotion. `d01f074` is the batch's retained control, not a current-HEAD
claim: this review found the canonical checkout clean at `7e6e977`, with later
PR #9 routing-weight placement, cleanup and documentation commits. Those are
separate from this overlap batch. No new GPU run was made for this review.

## Current ordering

The main pipeline/barrier setup is not blocked on staged inputs. It runs before
staging. The remaining distinction is whether staging can start earlier and
overlap that setup, rather than following its completion.

In `hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py`:

- 1079-1123: raw-weight, transform, activation and accumulator pipelines created
  with deferred synchronization.
- 1124-1145: TMEM allocator/deallocation-barrier setup, scheduler pipeline setup,
  and atomic-mode first work-ID preclaim. This is not expert/tile decode.
- 1146/1169: common pipeline-init arrival and wait.
- 1170-1172: allocation and TMEM retrieval. Only warps 0-4 and 12-19 join the
  416-thread retrieval barrier; dispatch warps 8-11 bypass it.
- 1353-1370: dispatch decreases to 64 registers, stages inputs, then performs
  preparation/publication/pulls. Lexically earlier compute-role blocks do not
  serialize these distinct warps. TMEM/role setup can overlap dispatch staging.
- 1178-1186: scheduler waits for dispatch publication before generating useful
  work. The weight and transform roles consequently cannot decode useful FC1
  weights during initial source staging. They can run ahead of subsequent
  remote activation pulls, because only the activation loader waits for each
  FC1 input block (1234-1254).

The owned `token_comm.py:45-102` performs activation copying and its writer
proxy fence first, then stages IDs/scores and inactive-capacity IDs. Inherited
`kernel_src/cutedsl_megamoe/src/src/token_comm.py:1579-1622` performs dispatch
preparation, grid/NVLink publication, scheduler release and remote pulls.
Routing preparation depends on routing IDs, not activation values. These phases
are currently serialized within the dispatch warp group.

CuTe layout/tensor-view construction is not necessarily runtime work. In
particular the source between init arrival/wait mostly compiles away; historical
PTX/SASS, not the number of Python lines, establishes the available work.

## What was tested

All three trials used historical baseline
`7dc9626909834bc70209e09784e9dfdebadceff2`, not current PR device commit `3de81245`.
The 7dc-to-current diff preserves pipeline initialization, TMEM retrieval and
the input-staging position; current code additionally selects receive-counter
banks and changes counter lifetime. Timing conclusions are not fresh-current
measurements.

| Candidate | Actual change | Historical baseline/candidate ratio | Evidence status |
| --- | --- | --- | --- |
| e37cf879 | Move dispatch staging between common init arrive and wait | 0.992427x, decode 4-512, 3/8 wins | Rejected; generated placement verified; terminal 104 exact outputs; independent full archive audit pending |
| b215a7d2 | Three activation-copy WGs concurrent with TMEM allocation; 544-thread retrieval handoff | 0.995737687x, 8-8192, 5/11 wins | Rejected; independent raw audit, bounded numerics/queued validation pass; no sanitizer qualification |
| 772de58a | Two decode WGs copy while dispatch stages routing and performs preparation | 0.999078x, 8-8192, 4/11 wins | Rejected; independent raw audit and bounded validation pass; composite compared with 7dc, not prep-only isolation |

Evidence:

- `EXPERIMENTS.md:923-942,1030-1040,1084-1094,1288-1295,1321-1325`.
- `input-stage-prologue-overlap/decode13-benchmark/SEALED_RESULTS_PENDING_AUDIT.md:3-27`.
- `input-stage-prologue-overlap/qualification/codegen-audit/owner-placement-review.md:3-11`.
- `input-stage-multiwg-retrieve/independent-timing-audit.md`.
- `input-stage-prep-overlap/performance/independent-timing-audit.md` and `PERFORMANCE_LEDGER.md:14-22`.

The e37 generated review covers all 4 tactics x 4 fused ABIs x 8 ranks (128
artifacts), with REG96/STACK0/LOCAL0; actual captured output execution covers
int32/vector only, 32 rank/tactic outputs. The other ABIs were compiled, not
numerically exercised by that capture. A read-only archive check found the
local timing archive truncated at 390,070,272 bytes versus its sealed
530,800,048-byte expected length, with full tar reading ending in EOFError.
Do not upgrade its provisional terminal evidence to an independently verified
complete archive. Twelve timing control rows are historical; 16K is a fresh
supplement. All serial trials retain temporal-drift limitations.

The complete candidate E1 and A16 control benchmark-log members occur before
the truncated archive boundary. A separate audit streamed those members and
used the complete retained A1 log for the other 12 control rows. Log hashes
match the sealed comparison, and medians were recomputed from all 100 raw
rank-MAX CUPTI samples per row. The decode ratio recomputes to
0.9924274113096655 (3/8 faster); 4K/8K/16K ratios are 1.023230252,
0.999695164 and 1.012316579. This verifies the timing arithmetic and raw logs,
not the missing full archive or all serialized output buffers.

## Original distinction, subsequently tested without retention

The `ec7428d` and `2bb3a02` results above supersede the original untested status
of pipeline-creation overlap and first-ID broadcast. The following explains
what the earlier e37/b215/772 trials had and had not covered.

e37 still constructs all pipelines/barriers before staging. It overlaps copying
with completion of the common init rendezvous/other-warp startup; it does not
test overlap between copying and actual barrier initialization. The preserved
69c36e20 prototype copies before init arrival but also after pipeline creation;
it was source-only and delays allocation until copying finishes.

Therefore those earlier results did not prove that all startup overlap was exhausted.
Starting dispatch copying before the common creation block while other warps
initialize would be a distinct design. Its initializer ownership, common
participation, register-donation order, and loss of existing copy/TMEM overlap
must be established before calling it safe or beneficial. Do not move two-CTA
TMEM allocation before the peer-start rendezvous without a separate proof.

Archived installed CuTe 4.7.1 runtime source makes that distinction concrete:
`../gpu-validation/owner6-source-audit/cutlass-runtime/pipeline/helpers.py:329-352`
initializes pipeline mbarriers using an elected thread in hardware warp 0.
The deferred pipeline creation paths omit their own rendezvous; common
`helpers.py:989-1030` supplies the init fence and CTA/cluster rendezvous. This
supports source-level feasibility of separate dispatch copying and warp-0
initialization, but is not a validated new participant/scheduling design.

Smaller independent pieces remain late in the current source:

1. The scheduler preclaims its first atomic ID at
   `fc1_fc2_fuse_sched.py:495-523`, but the first DSMEM ID broadcast remains
   coupled to tile decoding after dispatch readiness
   (`594-658,1030-1038`). The broadcast needs initialized cluster barriers but
   does not need expert counts. Splitting it from count-dependent decode is a
   narrow runahead opportunity subsequently tested as `2bb3a02`, without retention.
2. Pull mbarrier initialization and warp synchronization happen only at
   `dispatch_pull` entry, after dispatch publication (shared
   `token_comm.py:822-827`). Their inputs are fixed local shared storage and
   warp identity, not activation/routing values. A hoist must remove the late
   initialization and preserve phase/reuse correctness. This is a small
   opportunity, not evidence of a material bottleneck.
3. Dispatch's histogram zeroing and local barrier (`617-626`) need neither
   activations nor IDs, whereas later histogram work needs IDs. The broader
   772 candidate overlapped routing preparation but changed copy ownership and
   added a handoff dependency, so it does not isolate a tiny setup-only hoist.

Next evidence should measure actual per-CTA startup boundaries on the selected
source: init completion, staging completion, routing preparation completion,
dispatch publication/scheduler release, first weight load and first MMA.
Use such diagnostics only to locate a gap, then uninstrumented full-forward
timing to decide whether a narrow change helps. Earlier setup alone is not a
speedup if staging/publication remains the critical path.

## Weight loading and dequantization during source staging

### Finding and prior-experiment coverage

Useful weight TMA/dequantization does not currently overlap initial source
activation staging. It does overlap subsequent remote activation pulls. These
are separate windows. The mathematical weight transform needs packed weights
and scales, not activation values; the current scheduling dependency delays it
until the combined routing/input publication.

At the initial audit, no implemented or measured metadata-first
weight/dequantization trial was found in the records inspected. This status is
superseded by `3cd1f70` and its publication/readiness follow-ups above.
The original search covered project Markdown excluding
repository copies and frozen/captured sources, with focused inspection of the
integrated-topk ledger and staging reviews, `pdl-finalize-20260918`,
`latest-kernel-sync-20260917`, and `scheduler-publication-20260915`. Queries
included early scheduler release, routing-first, split metadata/payload
publication, weight prefetch/preload/runahead, and speculative expert loading.
This is a bounded records search, not proof about every historical branch.

- e37 retained the old dispatch publication/scheduler gate.
- b215 and 772 finish activation copying before the handoff that precedes
  publication and scheduler release. Even 772's routing preparation is not an
  early metadata-ready publication. Its generated-order review explicitly
  retains this ordering (`input-stage-prep-overlap/qualification/codegen-audit/generated-order-review.md:9-15`).
- The PDL experiment overlaps finalizer preparation with the core tail; its
  ordinary core launch cannot overlap the preceding staging kernel
  (`../pdl-finalize-20260918/source-reasoning.md:6-12`).
- The older scheduler-publication experiment elects one record writer while
  retaining all pipeline arrivals; it does not release work earlier
  (`../scheduler-publication-20260915/README.md:3-5`).

Consequently the rejected staging/preparation results are not evidence against
this distinct weight/dequantization overlap proposal.

### A concrete design that reuses the compute pipelines

The cleanest non-speculative prototype is to separate routing readiness from
activation-payload readiness, keeping dispatch responsible for copying and the
existing weight/dequantization workers available for their original work:

```text
Dispatch: IDs/scores + routing prep -> publish metadata -> release scheduler
                                                         |
Dispatch:                                      copy hidden activations
                                                         |
Dispatch:                                      publish payload -> remote pulls

Compute:                           exact work -> weight TMA -> dequantization
                                                               |
Compute:                         existing activation-ready wait -> MMA
```

This diagram shows overlapping warp roles, not one sequential instruction
stream. The proposed dispatch sequence is:

1. Stage IDs/scores and preserve capacity-tail ID masking.
2. Run existing `dispatch_prep` and `dispatch_barrier` to publish stable counts
   and route metadata, then arrive at the existing dispatch-to-scheduler barrier.
3. Copy hidden activations using the original dispatch workers and writer proxy
   fences while the scheduler, weight loader and two decode WGs run normally.
4. Complete a separate payload-publication boundary before any remote payload
   pull; then continue the existing pull, return and cleanup paths.

This needs owned transport orchestration and a readiness-protocol change, but
does not inherently require another weight pipeline, speculative task matching,
more decoded storage, changed GEMM math, or a new numerical reduction contract.
This was the source-supported proposal subsequently implemented by `3cd1f70`;
its timing did not merit retention or broader qualification.

Exact current dependencies:

- Owned `token_comm.py:34-74` copies hidden data; `76-102` stages IDs/scores.
  These are separable operations currently executed in the opposite order.
- Shared `token_comm.py:639-715` prepares routing from IDs without reading
  activation values; `738-798` publishes counts and synchronizes ranks.
- `fc1_fc2_fuse_sched.py:784-790` needs valid global expert counts to identify
  real work. Claiming a linear work ID alone does not identify the expert.
- `megamoe_kernel.py:861-913` loads only the scheduled expert's weights/scales.
  `hashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:385-456` performs
  decode from those weights/scales into the existing TMEM pipeline.

### The new publication cannot be omitted

The existing FC1 activation-ready wait protects the **local received pool**
(shared `token_comm.py:578-599`). It does not prevent dispatch itself from
reading another rank's unfinished source staging buffer. Those remote TMA reads
occur at `995-1005`, before local readiness is published. Merely moving scheduler
release earlier and assuming the existing FC1 wait covers remote input safety
would leave that gap.

For an initial correctness prototype, reuse `nvlink_barrier` after hidden
copying with both prologue and epilogue grid synchronization. Together with
the retained writer `async.global` fences, this provides the separate payload
publication using existing primitives (`token_comm.py:1498-1559`). It adds one
cross-rank collective and two local grid-sync phases, but no new ready counters
or epoch flags. Metadata/count updates must execute only once; do not call the
entire count-publishing `dispatch_barrier` twice.

The protocol review must cover all ranks, including empty ranks, and queued
invocations. Keep the persisted NVLink phase counter separate from the receive
counter bank. Preserve the entry-bank snapshot, previous-bank clear and tail
bank flip. For the NCU mode, the existing four-call self-cancellation sequence
must be revised: the new payload publication can replace the padding call;
blindly retaining that padding would produce five calls. Actual profiler
replay still requires its own validation.

Dispatch must never wait for weight/decode completion before finishing its
copy/publication/pull path. Then full raw/decode rings backpressure compute
without blocking the independent producer that will make activations ready.
Preserve register-donation order and CTA/cluster rendezvous participation.

A later lower-cost alternative could publish per-source payload-ready epochs
and acquire the appropriate epoch before remote pulls. It needs a local writer
join, system visibility, initialization/reuse and graph-replay proof. Likewise,
polling the high completion bits in packed expert counts is not a readiness
protocol already used by this scheduler: current decoding reads the low count
through an ordinary view after the combined publication. Neither alternative
is justified as a free synchronization removal by this audit.

### Bounded overlap and performance decision

Existing decoded TMEM holds only **three K256 stages for N64 or two for N128**
(`megamoe_kernel.py:79-98`); the raw ring fits 2-5 stages (`383-397`). MMA waits
for both operands before releasing the decoded slot (`1312-1323`). Therefore
early scheduling can warm the initial weight/decode stages, then naturally
stalls until activations arrive. It cannot pre-decode an arbitrary expert or
the whole FC1 into the existing storage.

There may be no gain even if this overlap is achieved: today weight startup
already overlaps remote pulling. If pulls hide that startup completely,
moving weights earlier only moves already-hidden work, while the additional
payload publication adds cost. Copying and weight loading may also contend
for memory bandwidth. A correct implementation is not evidence of a speedup.

First establish actual weight-load/decode activity before hidden-copy completion
and measure first-MMA timing. Compare the unchanged full-forward workload with
the same fixed tactic for attribution, then the normal AUTO policy for retention;
retain the current decode 4-512 and individual prefill guard methodology. Check
both weight-startup stalls and added payload-publication time. No new GPU run
or speedup is claimed here.

Speculative L2 weight prefetch is a separate, smaller possibility that could
leave publication unchanged, but it is not scheduled dequantization. Before
global counts are known, empty/skewed experts make predicted first work
uncertain. Speculatively filling the real TMA/decode rings would require expert
identity matching, discard/reuse handling and pipeline-state reconciliation;
that is less clean than metadata-first scheduling for a first prototype.
