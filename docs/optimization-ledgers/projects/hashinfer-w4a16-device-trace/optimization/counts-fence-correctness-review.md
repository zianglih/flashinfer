# Count-fence correctness and ownership review

The frozen `counts_fence` implementation has no new synchronization defect identified in this review, within its existing workspace, capacity and collective-launch contracts. Its early gate publishes finalized expert sizes and already-staged scores; it does **not** replace full input publication. This is a CPU/source review of an unretained prototype, not a retention decision or validation of a future cumulative/owned source.

Reviewed package SHA256: `771d8c303c79f299980ce97b9ffff53a24d86afea4ab1383bd2bfdd942d75951`. Source paths below are relative to `optimization/counts_fence/`. The fresh in-memory ownership plan passed all six method comparisons and three protected-file restorations: `ownership-port-evidence/counts-fence-correctness-port-review.plan.json`. It created no output worktree and changed no source.

## Publication edges

CUDA 13.2 ships PTX ISA 9.2. Its memory model allows a release/acquire-release fence followed by a strong relaxed write to form a release pattern. A system acquire load can synchronize with each earlier contribution through intervening atomic RMWs in observation order; the RED itself need not acquire. This covers only operations preceding the prefix fence, including causally preceding operations from other threads. Matching scope, proxy and complete overlap are required. The rule does not license replacing the source's aligned 64-bit acquire with a 32-bit source load. [PTX release patterns](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#release-and-acquire-patterns), [observation order and synchronization](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#observation-order).

The actual source implements these distinct edges:

| Edge | Source | Required behavior |
| --- | --- | --- |
| Local staging → every CTA0 count publisher | Owned `token_comm.py:58`; vendor `grid_sync.py:73–134`; vendor `token_comm.py:738` | Opening NB10 gathers the 128 dispatch threads; each CTA's elected relative thread0 performs the existing release atomic/completion observation/acquire fence; closing NB10 transfers visibility to all dispatch publishers. |
| Staged scores and finalized count contributions → scheduler | Vendor `token_comm.py:746–787`; owned `token_comm.py:26–53` | Every CTA0 publishing thread executes its system prefix fence before any expert RED. Each rank contributes high32=1, including for zero-token experts, and its low32 token count. Each scheduler warp acquires every local expert's full Int64 word until high32=`world_size`, then executes a full-warp synchronization. |
| Scheduler acquisition → work consumers, including immediate DONE | Owned kernel `megamoe_kernel.py:1214–1235`; owned `custom_ext.py:112–131`; vendor scheduler `moe_persistent_scheduler.py:170–190,711` | Both valid work and DONE use the same producer-commit/consumer-wait work pipeline. Early reduction preparation at kernel `:1584` reads local staged scores, not unfinished remote combine outputs. |
| In-loop per-source count stores → dispatch pulls | Vendor `token_comm.py:776–804,915,963,1573–1617` | These stores occur after the prefix. Preserve the trailing system fence, dispatch NB10, NVLink release/acquire publication and epilogue grid synchronization before pulls read per-source counts, token metadata or payloads. |
| Pulled activation → MMA; returned FC2 data → combine | Vendor `token_comm.py:579`; owned kernel `megamoe_kernel.py:1594–1627` | Keep FC1-ready checks, activation/raw/TMEM pipeline waits, all-role retirement, cross-rank return drain and the combine rendezvous unchanged. Count-ready scheduling permits early weight work only. |

The scheduler's NB9 arrival precedes its count polls. It is exactly one nonwaiting arrival, preserving the dispatch rendezvous's 160 participants in this W4A16 configuration. It does not convey the later acquire back to dispatch. Dispatch still arrives after full publication. W4A16 explicitly passes `token_back_standalone=False` at kernel `:269`; this review does not extend the early-gate override to an independently enabled standalone-return configuration.

Atomic-counter scheduler pre-initialization before the gate only claims/broadcasts a tile ID (`fc1_fc2_fuse_sched.py:492`). It does not decode count-dependent shapes. Static scheduler initialization remains after the gate (`megamoe_kernel.py:1218`). Ordinary low-word expert-size loads then execute after all contributions have completed; no current-generation writer remains to race with those narrower reads.

## Empty inputs, partial experts and counter generations

- **Empty/local-idle ranks:** publication is per expert, not per live route. Every source still contributes completion=1 for zero counts, so no expert waits for absent work. An immediately published DONE retains the local-score visibility needed by idle compute workers. Actual reduction still waits for peer returns.
- **Partial expert groups:** the scheduler iterates in warp-sized groups, predicates only the loads with `expert_idx < num_experts_per_rank`, and continues the loop while the warp ballot has any pending lane. The final full-warp synchronization includes lanes that never owned an expert. No out-of-bounds completion load is needed. Publication similarly bounds expert IDs before each peer address/store/RED.
- **Heterogeneous grids:** only the unique linear CTA0 publishes one contribution per expert after its own rank's complete local grid barrier. Completion counts ranks, not CTAs; local `expert_send_count` retains its separate CTA-arrival high word. Do not restore the old publisher while keeping the new threshold.
- **Prestaged or strided inputs:** the count gate does not change either ABI. In-kernel vector/scalar payload writers retain their async-global proxy fence; prestaged callers retain their existing stream-ordered staging contract. This review is not a new cross-stream or shared-workspace concurrency guarantee.
- **Normal replay:** kernel `:1069–1093` snapshots one bank consistently for aggregate counts, per-source counts and scheduler low-word views. Both banks initially come from zeroed workspaces (`frontend.py:297–298`). The previous bank is cleared after the current full dispatch publication (`megamoe_kernel.py:1465`); the later collective drain publishes those clears before the next invocation can use it. The selector toggles only at kernel `:1672`, after local roles retire. This preserves the existing in-order collective-launch lifecycle; count-ready does not move cleanup or reset.
- **NCU replay:** the compile-time NCU path keeps its active-bank cleanup plus cleanup-publication barrier (`token_comm.py:196–219`) and padding barrier. Normal CUDA graph replay coverage does not test this separate protocol.
- **Bounds:** readiness assumes exactly one contribution per rank/expert and no carry from summed low32 token counts into high32. Existing signed-Int32 count/index and workspace-capacity limits are stronger practical constraints for the tested workloads. The frontend does not establish an arbitrary-size overflow theorem; do not claim this scheme supports overflowing counters or duplicate concurrent invocations on one workspace.

The existing all-resident persistent-grid requirement is unchanged. Count polling can cost performance, but it adds no dependency on compute completion: dispatch can finish publication while schedulers poll. Control and dispatch retain their register donations before their respective gates.

## Ownership-port hazards and required preservation

The fresh plan uses the frozen helper unchanged. It copies the selected publisher and four reachable marker-bearing transport methods into `W4A16TokenComm`, the exact selected transform into `_MegaMixedInput`, and restores all three protected files to PR base406bc0d. Marker-stripped publisher AST equality, exact normalized ASTs for the other five copies, explicit import origins and preservation of other owned members pass. These checks establish a mechanical source transformation, not CuTe frontend dispatch/codegen equivalence.

Before freezing an actual owned source:

1. Keep `self.dispatch_barrier(...)` dynamically bound from owned `dispatch_warp_body`; do not accidentally call the restored vendor class method. The old high-word contract can hang the new rank-count gate on a multi-CGA launch even if a one-CGA fixture appears valid.
2. Keep the prefix after the complete local grid barrier and before every publisher thread's first RED. The fence must not move under `iket_active`, lane0 or representative-warp predicates. The three new uniform marker ranges guard only marker calls; the algorithmic statements stay outside those guards.
3. Preserve one NB9 arrival, full-width system acquire polling, final warp synchronization, unchanged trailing publication and the FC1-ready/return-drain gates. Use the existing relaxed system-u64 RED helper with its exact import origin. Do not infer ordering from the native opcode suffix alone.
4. Preserve the selected parent's TMEM width and transform method/probe mode exactly. Restoring the shared grouped helper must not silently restore probes in the owned transform or discard selected direct waits.
5. If payload splitting is subsequently selected, keep the 256-participant NB11 handoff **before** this local grid barrier. All 128 epilogue threads arrive even for empty/prestaged/no-assigned-copy cases; writers execute the proxy fence first. Dispatch's 128 threads donate registers before waiting; epilogue arrives before requesting 144 registers. Thus the existing local grid gathers the payload writes before the new prefix. The individual candidate results do not validate this new combination.

The restored vendor shim retains its original compatibility fallback; owned copies use `hashinfer._compat.iket`. Delegating the full restored `dispatch_pull` body would reactivate its removed lane-divergent nested markers. The explicit copies and their source-origin checks are intentional maintenance cost; no global IKET rebinding is involved.

## Prepared raw-only plus counts candidate

A second plan-only audit passes for `store16_raw_counts`, source SHA256 `3ec75add37d200d2c06d986436f3a87c61774706c0c79d0bfab0878b7baf99c1`. Its owned token class, vendor publisher and kernel file are byte-identical to counts_fence; its shared transform file is byte-identical to the frozen raw-only parent. The transform contains zero raw `consumer_try_wait` calls and retains both TMEM `producer_try_acquire` calls. All six ported methods and protected restorations pass without creating an output worktree. Evidence: `ownership-port-evidence/store16-raw-counts-correctness-port-review.plan.json` and `counts-fence-correctness-review.json`.

This checks the prepared combination and the helper's preservation of one-probe removal; it does not select the combination, establish CuTe compilation, extend any individual candidate's device evidence to it, or change R1 retention.

## What evidence already exists and what remains

The source-bound native audit in `native-codegen-overlap.md` checks all four fused Int32/Int64 × contiguous/strided ABIs. It confirms the prefix after local-grid completion, two relaxed u64 REDs without per-RED release bundles, retained trailing publication, unchanged acquire polls and no spills/resource growth. Source/PTX uses 64-bit acquire; the compiler narrows the unused low word in native SASS. This review relies on the PTX contract and records that lowering without inventing a native memory-model proof. The native audit covers the frozen unowned prototype, not a future port, prestaged ABI or actual empty execution.

The completed stateful audit (`dispatch-second-pass-audit.md`) supplies 1,080 rank outputs for counts_fence: 540 partial33/heterogeneous-grid and 540 full-GLM5/full-grid. Each uses tactics2/6/1, changing routes, all-empty, one-global-token, refill, score-only changes, queued graph replays and an eager call. All nonempty outputs match the independent BF16-bit reference; empty outputs match empty tensors. This is EP4/O3/FC2-placement coverage, not EP8, NCU, FC1 placement, every tactic or sanitizer coverage.

An actual selected cumulative/owned source still needs its own source closure, all applicable final numerical/lifecycle suites, final native PTX/SASS binding, EP4/EP8 performance against its immediately retained parent and a fresh-autotuned native trace. Include the partial33/full-grid changing-state cases again after porting; compile all fused dtype/stride ABIs and the prestaged path. If payload NB11 is selected, run both planned synccheck cases on the combined source. Qualify NCU separately only if claiming it. The final trace audit must bind all three new subsection sites to the actual instrumented cubin and compare event times within each rank.

No GPU workloads, remote transfers, primary edits, frozen-candidate edits or retention changes were made for this review.
