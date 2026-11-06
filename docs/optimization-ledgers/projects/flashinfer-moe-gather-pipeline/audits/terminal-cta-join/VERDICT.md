# Terminal CTA join: attribution and lifetime audit

No new deletion or scheduling prototype is justified. The 3,557 samples are blocked warp observations at the terminal rendezvous, not measured kernel time that can be recovered by removing it. The saved profile proves intentionally early-arriving roles; it does not expose the identity or arrival timestamp of the last active role. The remaining join is the lifetime boundary used by earlier retained simplifications.

This is CPU/source analysis only. `replay.py` independently replays the saved PC table and binds the native images, source, and result in `replay.json`. Current source is `49c91adf47d30fc2049c76cbaf34d0ccf3291434`. The measured native profile remains **82254e20**, not the later source: the three terminal statements are AST-identical, but whole-kernel current binary identity is not claimed.

## What the native samples establish

The saved V3 TP MXFP8 T16384 FC1 is static scheduling, two CTAs, 384 threads per CTA, three operand stages and one accumulator stage. Its returned CUBIN `92a69210…` is identical across all four profiler application replays; the existing native PC proof maps every instruction to that image. There is no Python line-debug information or per-warp arrival timeline.

| Native site | Observed evidence | Interpretation boundary |
|---|---|---|
| `0xfef0 BAR.SYNC.DEFER_BLOCKING 1,384` | 1,776 warp executions = 148 CTAs × 12 warps; 7 samples, zero barrier samples | One terminal rendezvous per warp, not a per-tile join |
| `0xff20 @P0 EXIT` after that deferred barrier | 3,558 samples, **3,557 barrier samples** | The deferred wait is observed at the following exit; nonallocator warps take this exit |
| Allocator path `0xff30–0x10250` | 148 executions on its straight-line path; zero samples | No observed exposed allocation-permit/deallocation instruction cost |
| Two-CTA peer-deallocation slow path `0x11000–0x11050` | Zero executions and samples | This capture does not implicate peer teardown as the stall source |
| Weight operand-tail main path `0x19a0–0x1ba0` | 7 samples, including 6 long-scoreboard samples | Some waiting occurs, but it is not the 3,557 barrier observations |
| Its first two slow paths | 2,061 / 2,310 repeated checks, zero samples | Executed polling is real; zero sampling does not prove zero cost |

The denominator is 27,253 total samples and 3,672 barrier samples. These are warp samples, not fractions of end-to-end critical-path time.

Two native branches explain early arrival without guessing from a source label:

- At `0xc20–0xc30`, warp 3 branches directly to `0xfef0`. With CLC disabled, the scheduler warp has no work loop in either CTA.
- At `0x41a0–0x41c0`, the condition includes nonzero cluster CTA rank and warp ID other than 2. The follower CTA's MMA warp branches to the same join; only the leader issues the collective MMA stream.

Therefore three of the cluster's 24 warps can wait at the terminal join while useful roles still execute. Later-finishing weight, relay, gather, MMA and epilogue roles also arrive at different times. The aggregated PC table cannot partition the 3,557 observations among those roles. **CLC termination is excluded for this particular capture**, since CLC is compiled out. A previously verified histogram model estimates maximum rounded-MMA work 13.1% above the mean across clusters; that is a possible scheduling imbalance, not measured role timing or proof of the terminal wait's cause.

## What each role must finish

Source anchors below are the current `flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py`.

| Role | Completion before the common join |
|---|---|
| Weight, warp 0 | Last A/SFA issue and next-work termination, any required producer-exit publication, then the single operand producer tail (`2924–2938`). That tail protects the shared ring used by both operand producers and pending asynchronous MMA releases. |
| Activation/relay, warp 1 | Regular FC2 TMA issuance, or every FC1 gather-local completion/acquire and its release to the leader. It has no duplicate producer tail. |
| MMA, leader warp 2 | All operand/gather readiness waits, S2T and MMA work, operand releases, and accumulator full publications. Its redundant accumulator producer tail is already absent. |
| Scheduler, warp 3 | Static: no work loop. CLC: final invalid metadata publication plus the leader's raw CLC-response tail (`2803–2859`). The local metadata tail is already omitted because all consumers join here. |
| Epilogue, warps 4–7 | All output work, final TMEM-load completion fence and accumulator release, then next-work termination (`3399–3408`). An early overlap release does not finish all remaining TMEM reads, so release alone cannot replace the join. |
| Gather, warps 8–11 | All Gather4/SF requests and final next-work consumption; relay/MMA waits and the operand drain cover their asynchronous completion. |

The all-thread join at `3586–3588` orders these roles before allocator warp 0 calls relinquish/free. Two-CTA `TmemAllocator.free` additionally joins the peer CTA's allocator after its local join. The [PTX 9.2 allocation contract](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#tcgen05-instructions-tcgen05-alloc-dealloc-relinquish-alloc-permit) requires synchronized peer TMEM accesses before collective deallocation. Relinquishing the allocation permit only gives up future allocation rights; it does not free storage.

## History and reference comparison

- The old project's `scripts/sync_audit_20261027/scheduler/terminal-barrier-proof.md` already removed the genuinely duplicate 128-thread barrier between relinquish and free. It explicitly retained this full-CTA join and peer handshake.
- `fc1-gather-20261028/optimization-next-20261029/accumulator-tail-audit-b139/README.md` removed the accumulator producer drain because ordinary consumer arrivals plus this join and the peer handshake already close that lifetime. Removing this join would invalidate that proof rather than complete another equivalent cleanup. The local metadata producer drain was likewise already removed.
- Current `experiments/terminal-pdl/RESULTS.md` preserves the rejected terminal dependency-wait deletion: repeated prefill losses and actual native FC2 register growth. It is not reopened. The profiled gathered FC1 does not instantiate that delayed terminal wait at all; its payload dependency is acquired at startup.
- Current Rubin `blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py` has separate producer tails, an accumulator producer tail, and an epilogue-local join before free (`3330–3336`). That ownership pattern is not proof that swap's common join can disappear; swap deliberately traded redundant drains for this common lifetime boundary.
- Blackwell MegaMoE `block_scaled_swap_ab_mega_moe_kernel_gen_specialized.py` frees TMEM inside the epilogue role, then still drains the predecessor router and joins every local role before its grid rendezvous/workspace-counter reset (`1189–1190`, `1226–1245`). Empty routes make the latter lifetime distinct. Its reset join cannot be substituted for or deleted by analogy with this split kernel.

The relevant old `CLOSED_LEADS.md`, scheduler audit, retained drain-removal proof, current rejected terminal-PDL results and `audits/post-tail-sync-staging-audit.md` were checked. No untested duplicate terminal join was found.

## Scheduling opportunity boundary

The weight tail already starts immediately after its last work item and required publication. Moving it before the final issues would violate its drain purpose; moving it to another role needs new state/ownership. CLC response cleanup is similarly placed after final response consumption and is not present in the sampled kernel. An early allocation-permit relinquish is semantically different from freeing TMEM, but no sampled allocator cost supports it; this specialization holds all 512 columns until free, so the move would not release capacity. None supplies a credible independent cleanup operation to overlap earlier without new policy or state.

Keep the existing join. Identifying the exact last-arriving role would require a new source-bound role timeline; no such collection is requested or launched here, and the current evidence does not justify a barrier-removal experiment.
