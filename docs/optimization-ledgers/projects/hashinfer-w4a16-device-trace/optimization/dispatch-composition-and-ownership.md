# Communication composition and final ownership plan

CPU review of the frozen local candidates, 2026-09-25. **No retention or speedup is inferred.** The combination is not yet a compiled/tested candidate. Source hashes, actual three-way merge checks, method dependency inventories and marker-stripped AST checks are recorded in `dispatch-composition-audit/audit.json`, produced by `audit_dispatch_composition.py`. No source worktree or GPU job was changed.

The source review found no additional race or barrier requirement when `counts_fence` and `parallel_payload` are combined **with their existing order preserved**. Their synchronization paths compose: payload handoff precedes local-grid completion, which precedes count publication. The new early scheduler cannot bypass the payload handoff. This conclusion is a source proof to qualify with the combined stack; individual numerical passes do not establish combined correctness.

## Required ordering in the combination

```text
epilogue WG: payload stores → writer async-global proxy fence → NB11.arrive
                                                                   │
dispatch WG: route/score staging → inherited dispatch_prep → NB11.sync
             → existing local software_grid_sync/NB10
             → CTA0 prefix fence.acq_rel.sys
             → every expert receives rank-completion RED64, including count0
             → existing trailing system fence and NVLink/global publication
             → dispatch_pull → FC1 pool store completion/release counters

scheduler: one NB9.arrive → acquire all final expert counts → warp sync
             → publish work or DONE
weights/transform: work record → weight TMA → decode → bounded TMEM slots
activation: work record → FC1-ready acquire → activation TMA
MMA: decoded weight AND activation ready
```

NB11 connects the new payload writers to dispatch's existing publication chain. Scores remain on the original dispatch owners. It must stay **before** `software_grid_sync`, not merely before `dispatch_pull`: moving the count prefix or REDs ahead of NB11 would invalidate the combined publication proof and change the readiness boundary.

The PTX rules used here are narrow: a release fence followed by a strong write forms a release pattern; matching barrier arrivals synchronize with the barrier wait; atomic observation order can link earlier contributions to the final acquiring reader. Only writes preceding the prefix are covered by that pattern. These are the documented [release-pattern](https://docs.nvidia.com/cuda/parallel-thread-execution/#release-and-acquire-patterns) and [synchronization](https://docs.nvidia.com/cuda/parallel-thread-execution/#memory-synchronization) rules. This source reasoning assumes the same existing cumulative local-grid implementation and system-scope peer-atomic contract as the separately reviewed count candidate.

Important boundaries:

- Per-source `expert_recv_count` stores are after the prefix fence. Early consumers must continue using aggregate counts only. `dispatch_pull` and standalone return remain after the trailing/global publication; do not move them to the count-ready gate.
- A compute-idle CTA may receive DONE and run `_prepare_reduce_worker` before dispatch finishes its global barrier. Its local scores are safe because every incoming count includes this rank's contribution after local route/score staging and grid completion. The final scheduler warp sync transfers acquire visibility to tail lanes; scheduler record publication transfers it to consumers. Remote combine reads still wait for the existing return drain.
- Atomic scheduler pre-init only preclaims a task ID. Static scheduler initialization reads expert sizes only after the gate. Do not move static initialization earlier.
- Count-ready, Store32, and direct transform waits do not remove activation readiness. Both transform waits remain blocking; raw release, TMEM commit/fence and ring phase advancement must remain unchanged. Earlier weight production may encounter the same bounded backpressure; that is not a correctness failure or automatic performance benefit.
- Native PTX uses64-bit system-acquire loads, but ptxas currently narrows the unused-lowword native poll to a high32 load plus invalidate. This observed lowering is the same in counts_overlap and counts_fence. Preserve the source/PTX acquire contract and recheck final code; do not rewrite the source poll to an ordinary32-bit load based only on SASS.

## Participation, lifecycle and progress cases

| Case | Requirement and source assessment | Qualification needed on the combined final source |
|---|---|---|
| Empty live source rank / all-empty batch | Payload loop may do no stores, but all128 epilogue threads still arrive at NB11; all128 dispatch threads still wait. Every rank publishes high32+=1 for **every expert**, including low32=0. Scheduler polls must not be conditioned on local live tokens or expert activity. | All-empty→refill, one global token, hot routes on another rank; changing-route runner already defines these phases. |
| Expert receives no tokens / compute-idle CTA | Final count0 is ready after all rank contributions. Scheduler can publish DONE. Early score preload is covered by the rank's own published staging; full-CTA retirement and return-drain gates remain. | Skewed/hot0→hot3 transitions and score-only updates with idle CTAs, both weight placements. |
| Partial local expert warp | Bounds check prevents out-of-range loads. All lanes participate in ballots and final warp sync; an unused lane must not return from the method early. Each valid expert still receives all rank completions. | `partial33` has33 local experts; supplement with existing singleton/small-expert tests. |
| Heterogeneous per-rank CTA counts | Readiness is world_size, independent of local sm_count. Each rank's own grid barrier uses its actual CTA count before rank publication. Payload copy stride remains each rank's sm_count. | `partial33:heterogeneous`, then full GLM5 grid. |
| Fused contiguous / strided input | Copy partition and vector-alignment guard are unchanged except owning WG. Each actual writer keeps its proxy fence. Route ownership remains same-lane through inherited prep; no extra route grid barrier is needed. | Four fused ABIs: Int32/Int64 IDs × contiguous/strided BF16; odd live rows and capacity tails. |
| Prestaged input | `staging_inputs is None` skips both staging bodies, not NB11 participation. Existing caller stream order owns readiness. The extra handoff still runs once even without a copy. | Direct frontend prestaged cases; native artifacts so far contain only fused inputs. |
| Both counter banks / graph replay | Scheduler and dispatch use views snapshotted before roles begin. Normal previous-bank clearing is still after global input publication; drain publishes clears before reuse. Bank toggle remains after retirement/cleanup. No early clear is introduced. | First graph after route/score update, queued replays, empty/refill and alternating-bank transitions. |
| NCU kernel replay | Existing active-bank reset and four-call signal cycle must remain exact. Combining these source changes adds no cross-rank barrier phase. | Not covered by current regular-mode evidence. Run a dedicated supported replay check only if claiming NCU support on final source. |
| Standalone token-back | W4A16 construction explicitly sets `token_back_standalone=False`. Inherited standalone code would still wait at NB9, but the new payload WG assignment is specific to this640-thread W4A16 kernel. | Do not claim generic standalone transport coverage or apply the subclass outside W4A16. |

No additional register-pool cycle is introduced: control donates to80 before its scheduler gate; dispatch donates to64 before NB11; epilogue arrives nonblocking at NB11 before requesting144. TMEM allocation/retrieval precedes epilogue staging, but it does not depend on count readiness. The early scheduler now necessarily follows completion of NB11 on every source CTA. The original61440-register redistribution remains unchanged. Combined compiler register placement must still be inspected; individual zero-spill outputs do not guarantee a combined zero-spill output.

## Concrete source references

Line numbers refer to the frozen candidates, not a future port:

- [Count acquire and warp completion](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/counts_fence/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/token_comm.py:25).
- [Prefix/count publication and retained trailing/global gate](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/counts_fence/hashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py:718).
- [Local grid NB10/release/acquire implementation](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/counts_fence/hashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/grid_sync.py:73).
- [Payload copy and writer proxy fence](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/parallel_payload/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/token_comm.py:25), [inherited prep followed by NB11](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/parallel_payload/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/token_comm.py:120).
- [Unconditional epilogue arrival before register increase](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/parallel_payload/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1419), [dispatch donation and staging](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/parallel_payload/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1455).
- [Score preparation](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/counts_fence/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1006), [bank snapshot](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/counts_fence/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1069), [tail rendezvous and combine gate](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/counts_fence/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1594), [bank toggle](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/counts_fence/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:1667).
- [Atomic versus static scheduler pre-init](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/counts_fence/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/fc1_fc2_fuse_sched.py:492), [FC1-ready peek](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/counts_fence/hashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/custom_ext.py:260), [activation blocking wait](/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/counts_fence/hashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py:578).

## Minimal cumulative implementation after decisions

1. Start a new experiment snapshot from the **actually retained** store-width/no-peek parent. Use component deltas against frozen store16, not complete patches against002: every dispatch prototype embeds Store16 and blindly applying its full patch risks reverting Store32.
2. Apply count-ready's owned scheduler method, explanatory score comment and `sched_wait_dispatch_counts` label; apply its count publisher as an owned override in the ownership step below. Keep high32 rank normalization, failed-poll sleep100 and all existing generation/return gates.
3. If payload is also selected, take its `stage_payload`, `stage_routes`, `dispatch_prep`, constant11 and kernel call sites. Retain the count-ready method beside them. There must be one payload copy owner, one routes owner and one NB11 site per participating role; do not retain an accidental call to old `stage_inputs` as well.
4. Union imports (`Int64`, `_nanosleep`, owned `iket`, publisher helpers) and methods deliberately. CPU three-way merge checks on all four prospective parents (store16, store32, store16_no_peek, store32_no_peek) show the kernel and vendor deltas merge cleanly. The **owned token_comm file has two textual conflicts**: `Int32` versus `Int32, Int64` import, and insertion of the scheduler method adjacent to the stage_inputs→stage_payload split. These are method-union conflicts, not conflicting synchronization algorithms. Exact conflict excerpts are in the JSON.
5. Preserve the parent's TMEM repetition literal and selected `_transform_tile` exactly. Count/payload changes are independent of Store32's copy atom and direct-wait ring semantics. Record new full source digest; never relabel the existing individual evidence as testing this combination.

Do not port an unretained performance candidate merely to simplify the final diff. Tracing itself is retained, so its ownership cleanup below is needed independently of count/payload decisions.

## Full protected-file restoration: copy scope and alternatives

Restoring only `dispatch_barrier` is insufficient. Comparing PR base406bc0d to002 finds five vendor methods changed for tracing. There is **no `__call__` change** in this file; the dispatch orchestration method is `dispatch_warp_body`.

| Vendor method at002 | Lines including decorator | Why it changed | Owned override needed for current reachable W4A16 trace |
|---|---:|---|---|
| `fc1_tma_b_predispatch_spin` | 23 | Explanatory token-ready wait name | Yes |
| `dispatch_pull` | 320 | Removes lane0-only nested per-token markers | Yes; delegating the restored method would reactivate those markers |
| `token_back_by_push` | 301 | Explanatory per-token return name | Yes, if preserving the current label; called through current return paths |
| `dispatch_warp_body` | 112 | Explanatory prep, counts, pull and return ranges | Yes |
| `token_back_warp_body` | 68 | Standalone return rename | No; W4A16 explicitly disables standalone token-back |
| `dispatch_barrier` in counts_fence | 87 | New early-count publication contract | Only if count-ready retained |

The four reachable trace method copies total **756 lines**; count publication adds87, for843 transport-method lines before imports/provenance. The markerized transform adds120 lines if probes stay, or98 if no-peek is retained. Thus tracing plus no-peek plus count publication entails941 copied method lines, before the already-existing owned staging/tail methods. This is a real source-maintenance cost, not a small label-only port.

The safe minimal delegation is **inside** these owned methods: keep inherited `dispatch_prep` routing mechanics (except the owned NB11 wrapper), `_cta_linear_id`, storage/ABI construction, NVLink barrier, return encoders and reset helpers; keep inherited transform layout and `_finish_transform_stage`. Their existing signatures/calls remain exact. Owning the orchestration and only the marker-bearing bodies avoids copying the entire transport class.

A wrapper around an unchanged inherited method cannot remove its nested marker calls. Whole-method delegation therefore cannot preserve the marker-removal fix in `dispatch_pull`. Per-instance global IKET replacement/monkeypatching is unsafe and unnecessary; import-time AST/source rewriting would hide the copy and complicate CuTe source inspection. A new vendor hook could reduce copied bodies, but it would leave a new protected-file contract to merge upstream. That is a separate design choice, not a zero-diff restoration. Trace-label rewriting after decode would reduce the301-line rename-only copy but would split names between native instrument metadata and the displayed artifact, and would still not solve the unsafe pull markers. The recommended ownership plan is explicit method copies with mechanical equivalence checks.

Port layout:

- Keep these methods in existing owned `W4A16TokenComm`, avoiding another inheritance layer during a performance-sensitive port. Use the same method signatures/decorators. Reuse unchanged helpers through explicit imports; `audit.json` lists every method's referenced globals. The largest dependency set includes `GpuReleaseFlagBatchTracker`, `TokenSrcMetadata`, scalar types and existing PTX helpers. Do not access them by global rebinding.
- Import IKET through `hashinfer._compat` for owned code. Either normalize `_iket`→`iket` in copied methods under an explicit AST rename check, or use an import alias consistently.
- Add `_MegaMixedInput._transform_tile` from the selected parent's exact method, regardless of no-peek retention, and import `decode_nvfp4_fragment_to_bf16` from the existing owned codec utility. Leave setup/layout/finish methods inherited.
- Restore **all three protected files** byte-for-byte to406bc0d: shared grouped helper, vendor token_comm, vendor iket_compat. The owned `_compat.py` remains the clean import path; restoring the original vendor fallback is compatible with it and does not require changing the vendor again.
- Add a short provenance note beside copied methods and record original commit/method AST hashes in the synchronization audit. Future syncing can compare base method semantics against the owned copy without treating them as unrelated implementations.

Exact PR-base SHA256 checks:

```text
hashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py
  f283fdc3b627e04923951588a42c543be95573899a0eb313c68da3bed0671f76
hashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py
  de06383771ab500aa62fc37a8c79d6aa38bece761fe04d59c83d6ef66a783296
hashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/iket_compat.py
  bb130a47b521a42f72669bea64337ad54e19ea069bb6a0b5590393ebdc1a914b
```

The CPU audit **already verifies** that stripping only IKET calls and now-unused marker predicates from all five002 vendor methods yields ASTs identical to PR base. It also verifies that stripping markers from002's transform yields the PR-base transform AST. This establishes the comparison baseline, not a completed port. After porting, check copied trace methods against the current frozen methods verbatim (or normalized IKET alias), marker-stripped semantics against these hashes, count publisher against counts_fence exactly, and no-peek transform against the selected exact parent. No-peek's intentional wait changes must not be erased by the marker-stripping equivalence test.

## Optional final-trace subdivision of owned dispatch publication

Once `dispatch_barrier` is owned, add three coarse push/pop ranges without changing indentation of its algorithmic body. Use a warp-uniform predicate identical to its caller's outer marker: `sm_idx == 0 and warp_idx == 0`, where warp_idx is dispatch-relative. Every lane of that warp executes each push/pop. Keep all markers outside the expert loop and its per-lane expert-valid predicate.

| Label | Length | Exact existing statements to bracket | Meaning and caveat |
|---|---:|---|---|
| `dispatch_wait_local_route_counts` | 32 | The initial `software_grid_sync` call, including its internal NB10 sandwich | Wait for all local CTAs' route preparation and count accumulation. If payload split is retained, NB11 already completed before this call. The barrier also gathers earlier staging/metadata writes. |
| `dispatch_publish_expert_counts` | 30 | Entire `if sm_idx == 0` publication body: optional selected prefix fence, expert loop with per-source count stores and count REDs, existing trailing fence | Captures the marked publishing warp's count publication work. Other CTA0 dispatch warps also publish; this range alone is not proof that all of their expert updates completed. |
| `dispatch_wait_input_publication` | 31 | Existing post-publication dispatch NB10 and the entire `nvlink_barrier(..., prologue_grid_sync=False, epilogue_grid_sync=True)` | Establishes cross-rank visibility of staged input payload, route IDs/metadata, scores and per-source/aggregate counts, including the local dispatch rendezvous and final local-grid release. It is not a token-fetch or payload-transfer duration. |

The final name deliberately covers the complete dispatch input publication, including metadata; describe that contract in the marker guide. `dispatch_wait_peer_input_publication` would be36 characters and exceeds the current32-character marker constraint. No token-level or expert-level divergent instrumentation is needed.

Leave `dispatch_exchange_counts_sync` as the enclosing existing range in `dispatch_warp_body`. It closes after the original dispatch NB9 arrival; the third subsection ends just before that arrival. The subsections nest on the same CTA0/dispatch-warp0 stream and partition existing work without creating a new synchronization edge.

For count-ready, keep `sched_wait_dispatch_counts` on every CTA's scheduler warp. A scheduler may finish that gate and issue weight work while `dispatch_wait_input_publication` remains open, which is precisely the intended window. There is no requirement that it finish after the marked publication warp's second scope: incoming experts can be published by other ranks/warps. Without count-ready, preserve the metadata-gate name and NB9 wait; it must still follow full publication.

The final trace should compare scheduler release, first weight load and decode against both publication completion and outer-range completion **within the same rank**. Since only CTA0's dispatch barrier is marked, retain the explicit CTA0/warp8 anchor and show both recorded CTAs' consumer events. Do not suggest CTA1 has its own marked dispatch range or align clocks across GPUs. The new three-way split can distinguish local-grid waiting from final peer publication in a long initial range, but it cannot identify host launch skew by itself.

For trace-only ownership without count-ready, adding this subdivision would require owning the unchanged87-ish-line publication method solely for tracing; count-ready retention already requires that copy. Before freezing the final source, add the expected labels to fixture/trace validators and docs, preserve marker-stripped AST equality to the selected publisher, then re-export native instrument points and confirm the PMTRIG source/cubin binding. Earlier instrument-point audits cannot validate the additional sites.

## Qualification before final attribution

Use the existing source-bound runners; no new GPU test was run for this audit.

1. CPU closure: protected files equal the three hashes, owned methods match selected prototypes, only selected optimizations remain, no unresolved/global method dependencies, all trace labels and marker branches validate. Extend the existing owned-transform guard to run even if probes remain, using the corresponding method expectation.
2. Compile/export the **combined owned source**, timed Int32-contiguous ABI and all fused dtype/stride variants; add a prestaged export if using native code evidence for that path. Inspect NB11 before register growth, count prefix/RED/trailing fence and acquire polls, one scheduler NB9 arrival, unchanged activation gate, Store32 stores if selected, blocking direct waits if selected, no new spills. Individual exported resource counts are not transitive.
3. Stateful EP4 combined-source checks: tactics2/6/1, `partial33:heterogeneous` and `glm5:full`, both routing-weight placements, with the existing all-empty/one-token/refill/score-change/queued-replay phases. Preserve the output's actual source digest.
4. Final suites from `final-validation.md`: strict EP4/EP8, tails, lifecycle and prestaged. If NB11 retained, both existing synccheck cases are required. If claiming NCU replay, add that separate qualification; normal CUDA graph replay is not NCU replay.
5. Matched full-forward cold-CUPTI measurements against the immediately retained parent, using the final ownership source, followed by fresh-autotuned final winner trace. Re-audit native instrumentation points. Early weight start alone does not establish total-runtime improvement.

Reproduce the local audit with `python3 optimization/audit_dispatch_composition.py`. It performs read-only source/Git reads, AST comparisons and temporary plain-file merges inside the effort; it neither constructs a promoted candidate nor touches a GPU.
