# Single-owner CLC tile-metadata publication

Independent unstaged source: `../../flashinfer-clc-single-owner-20261026`, based
on retained `7f4e1703d984831efc13eea63a868b3e558d243b`. Frozen patch SHA256:
`e7de223d7458c7275b14162632f36e9da47e2c1aeb1115c06a2a3eb9c264f262`.
Only the shared blockscaled kernel changes (+4/−6); W4A16 and MegaMoE are
read-only references. No tactic, shape, dtype, resource-count or API rule changes.

The CTA-local tile-info pipeline changes its full arrival count from32 to1.
The elected owner performs all three generic shared stores and the full arrival
inside the same `elect_one`. The previous async-proxy fence and warp32 named
barrier disappear. Every scheduler lane still acquires the empty stage, advances
its pipeline state, participates in CLC response handling and waits in tail.
Every consumer still waits, reads and releases, preserving the complete empty
count and stage-wrap protocol. Final `-1` publication uses exactly the same path;
padded but still-valid CLC tickets are still skipped without publication.

## Ordering proof

The installed CuTe DSL4.7.1 source is captured in `sdk-source.json` with extracted
classes/functions alongside. `PipelineAsync.create` uses `AsyncThread` for both
ends. `producer_commit` calls `MbarrierArray.arrive`, whose AsyncThread branch
calls ordinary `cute.arch.mbarrier_arrive`; `consumer_wait` calls the barrier
wait. Metadata stores and consumers' `sInfo` reads are ordinary shared-memory
accesses, not async-copy or TMEM accesses.

The [PTX mbarrier arrive contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-mbarrier-arrive)
defaults to release at CTA scope. A successful
[mbarrier wait](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-mbarrier-test-wait-mbarrier-try-wait)
uses acquire and makes earlier ordinary accesses from the arriving thread visible
to consumers. Keeping stores and arrival on the same elected lane provides that
ordering directly. The removed proxy fence orders generic versus async access;
the tile-info payload has no such crossing. Actual generated PTX/SASS still must
confirm this lowering before any performance inference.

The separate CLC response pipeline remains a cluster-aware async transaction
with its existing peer releases. The two-CTA SF readiness join, operand and
accumulator pipelines, PDL publication, initialization fence and cluster startup
barrier are unchanged. CTA-local metadata needs no cross-CTA release: each CTA
publishes its own local metadata after the unchanged CLC-response synchronization.

W4A16's scheduling loop has the old elected-stores/fence/warp-barrier/32-arrival
sequence, so it does not establish necessity. MegaMoE's common scheduler transport
uses32-thread publication with a wider tensor copy and a separate cluster claim
pipeline. Neither implementation is modified or used to waive the release/acquire
proof for this simpler three-scalar transport.

## Validation plan and boundary

The reused source-paired public-wrapper gate forces both FC1 and FC2 to CLC for
both sources. Four configurations cover standard/per-token NVFP4, MXFP4x8 and
MXFP8; narrow/wide N, one/two CTAs, inline/overlapped epilogues and PDL off/on.
Each captured graph replays balanced, skewed, empty and reactivated local routes
with changing input and routing weights. The live-work count exceeds the resident
grid, exercising stage reuse and terminal tickets. PTX/SASS and resources are
captured from those same compilations. The gate changes only diagnostic tactic/
overlap controls, never timing contracts. GPU2 is reserved for this bounded gate;
no performance timing or retention claim yet.

Persistent native C++ artifacts are shared only after source identity verification;
control and candidate CuTe caches are private. `source.json`, `control-source.json`,
`deploy.py`, `probe_scheduler_pair.py` and `run_pair_gate.py` record the exact inputs.

## Completed exact/codegen gate

All64 source-paired graph replays pass (32 per source), across all four configurations and both PDL settings. The gate verifies unchanged input/weight/routing identity, zero output for empty local work, reactivation, and exact output byte hashes. `validation.json` binds every collected artifact and both frozen sources.

All16 kernel pairs retain identical register counts, static shared memory and zero local/spill sites. Each candidate PTX changes the metadata full-barrier count32→1, keeps stores and arrival inside the same elected branch, and preserves consumer acquire waits. The metadata `bar.sync 5,32` and one async-proxy fence disappear in every pair. Actual SASS removes that named barrier and predicates the full arrival with the same elected predicate as both shared stores. The unqualified PTX mbarrier instructions use the documented default release/acquire semantics. `ptx-proof.md` contains per-specialization excerpts.

Representative two-CTA MXFP4x8 FC1/PDL-on: control metadata SASS has `FENCE.VIEW.ASYNC.S` at 0x51c0, `BAR.SYNC.DEFER_BLOCKING 0x5,0x20` at 0x51d0 and all-lane arrival at 0x51e0; candidate uses @P4 stores at 0x5150/0x5160 and @P4 arrival at 0x5170 with no metadata fence/barrier. Registers remain 80 and local/stack remain 0. This establishes simpler publication, not an end-to-end speedup.

## Fixed all-CLC timing

`run_fixed.py` compares clean 7f4 with the frozen single-owner patch in CAAC order
on GPU2. Both sources use the same independently selected native all-CLC cache;
the runner asserts that every measured blockscaled tactic has both scheduler
flags enabled, all cache lookups hit, and complete tactics and route identities
match across the four runs. W4A16 is an unchanged control in the NV family.

Timing uses the public benchmark with 10 warmups, 100 cold-L2 CUPTI samples and
initial activation quantization included for the NV family. The source-private
compiler caches remain separate. `observe_table.py` and `arm_contracts.py` are
byte-identical copies of the parent's all-CLC campaign observers; they preserve
raw samples and full-precision medians without changing tactics or timing.
`collect_timing.py` and `summarize_timing.py` retain and validate the evidence.

The first sequence covers V41/MX and K3/NV at 32, 128, 4096 and 16384 tokens,
using each completed `all-clc-native-20261026/.../1-B` cache. Other model/family
sequences wait for their native cache to complete. This comparison isolates the
publication change; it does not compare static scheduling with CLC or refresh
TRTLLM results. Padded cancellation tickets that skip metadata publication are
unchanged, so this optimization cannot remove their scheduler tail.

## Completed timing and recommendation

All six model/family CAAC sequences completed on GPU2: V3, V41-Flash and Kimi K3;
NVFP4 W4A4, per-token NVFP4, MXFP4x8 and MXFP8; 32, 128, 4096 and 16384 tokens.
The NV family also measures unchanged W4A16 as a control. All 60 points validate
source, cache, complete selected tactics, routes and raw medians. The 240 public
measurements retain all 24,000 samples. `retention-receipt.json` binds the frozen
source, exact/codegen checks, scoped static checks and timing artifacts.

The geometric mean across 48 affected points is 1.000574×. The largest aggregate
gain is V41 MXFP4x8 at 16384 tokens, 1.01672×; the largest aggregate regression is
V3 MXFP8 at 16384, 0.99526× (801.82→805.64 µs), with forward/reverse ratios
0.99099/0.99952. The unchanged W4A16 control also shows prefill variation. These
results support retaining this as a small, neutral synchronization cleanup;
they do not establish a material general speedup or recover the all-CLC prefill
gap. No new model/dtype/shape policy is introduced.

GPU2 was checked free and released after all six sequences. A separate read-only
consumer-owner proposal was rejected without implementation: the converged
consumer arrivals already aggregate and shared reads broadcast, so adding three
shuffles would introduce work. See `consumer-publication-audit.md`.
