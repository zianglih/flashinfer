# Existing return signals cannot certify individual combine slices

Read-only audit of retained3de81245,2026-09-19. **No safe per-token/per-route early combine is available from the existing counters.** Their meanings and ordering edges do not certify completed FC2 returns. A worthwhile implementation would require a new completion publication protocol; it is not a small relocation of the existing wait. No source/GPU change or gain claim is made.

Paths below are relative to `selected-counter-lifetime/hashinfer/hashinfer/moe_ep/`. O=`cute_dsl/megamoe/bf16_nvfp4`; S=`kernel_src/cutedsl_megamoe/src/src`.

| Existing state | What it certifies | Why it cannot release an individual combine slice |
|---|---|---|
| `expert_recv_count[rank,expert]` and sum | Source input-routing counts published in dispatch setup; sum also feeds scheduler expert sizes | Written before FC1/FC2. No output store precedes these publications. S/token_comm.py:719–797, especially773/780; O/megamoe_kernel.py:1033–1056. |
| `fc2_done_counter[local_expert]` | Batched completion of expert-owner local FC2 tiles for dispatch's TMA reads | GPU-scope release and GPU acquire; published **before** return copies. No source-token/route/hidden-slice identity. Absent in epilogue-return mode. O/epilogue.py:197–212; S/token_comm.py:1319–1337; O/megamoe_kernel.py:1612–1619. |
| `token_back_schedule_counter` | Work reservation by dispatch warps | Relaxed GPU atomic increments reserve batches before transfer, not a completed-return frontier. S/token_comm.py:1240–1281. |
| NVLink barrier signal slots | All ranks have reached the current global phase after the local grid rendezvous | Whole-rank/global completion only, after mandatory producer retirement; not fine-grained output readiness. S/token_comm.py:1501–1559. |

`spin_wait(..., peek_only=True)` exists, but it remains a GPU-acquire peek at whichever counter is supplied (`src/moe_nvfp4_swapab/moe_utils.py:93–115`). A nonblocking peek cannot change the counter's meaning, scope, or publication placement.

## Exact store/visibility boundary

Dispatch return waits for the expert-local FC2 threshold, loads source metadata `(src_rank,src_token,src_topk)`, and targets `combine_output[src_token,src_topk,:]` (S/token_comm.py:1332–1378). The elected issuer performs the TMA load/store, then full bulk commit/wait at1415–1416. The BF16 caller passes `chunk_bytes=self.hidden_bytes` at1669, so this is full-row completion for one route. **No receiver-visible flag/counter is written after that wait.** The terminal system fence is at1480, after the entire return loop. There is no callback between per-row completion and the next scheduled return; subclassing `token_back_by_push` means owning its substantial scheduling/transport loop, or changing the protected shared API.

Epilogue return directly writes peer slices through `Fc2OutputRouter` and the STG helper (O/epilogue.py:238–264,301–305), suppresses `fc2_done_counter` publication (197–212), then performs the system fence only after the entire epilogue loop (O/megamoe_kernel.py:1331–1350). It has no completed-route/slice receiver certificate either. A producer's register/TMA wait state is private; a receiver cannot infer completion by observing payload values or local expert counters.

Current visibility is provided by the complete chain: outgoing-copy completion/system fences → common640-thread retirement barrier → dispatch prologue grid synchronization → system-release signals from CTA0 → system-acquire of all-rank target → epilogue grid broadcast → second common640-thread barrier → combine reads. See O/megamoe_kernel.py:1485–1523, O/token_comm.py:105–150, S/token_comm.py:1501–1559 and S/grid_sync.py:73–134. The grid leader uses release-GPU atomic/fence plus its dispatch-group barriers. This is the inherited global publication path, not evidence that earlier per-slice reads are ordered.

## Dependency and reuse limits

A dequant WG that waits for the existing global tail target before the first640-thread barrier creates a direct cycle: its dispatch WG cannot leave that barrier, so the prologue grid cannot complete and CTA0 cannot publish the target being awaited. A finite one-shot probe could avoid waiting, but the target for that invocation cannot become valid through this path before the caller joins retirement. Local FC2 counter success is earlier but does not make returned data safe.

The two receive-counter banks are input-count epochs, not route-arrival masks. The kernel snapshots the bank once (1033–1056), clears the opposite bank after input publication (1371–1381), and toggles at1550–1555. Current counts still serve scheduler/input consumers; changing their meaning or stealing bits would require a new ownership/alias protocol. Next invocation's input publication also protects the previous combine buffer from early overwrite. None of these lifetime guarantees supplies the missing completion notification.

NVLink signal slots separately cycle slot/direction over four calls (S/token_comm.py:1512–1525). Retained normal mode has two calls per invocation, while NCU1 adds padding/cleanup calls (O/token_comm.py:119–150,167–190); the counter advances before lane0 completes its acquire (S:1537–1550). Raw slot values are not token epochs and must not be treated as stable per-token flags. A post-all-rank/pre-local-broadcast consumer would need a separate phase/lifetime proof on3de; this would still consume only globally ready data and would not achieve the requested pre-drain per-slice overlap. The older raw-slot reuse rejection occurred before banking removed a call, so it must not be copied as a complete current-normal-mode impossibility proof.

## History and recommendation

`EXPERIMENTS.md:1051–1066,1107–1120,1177–1195` records c2b's new stable local relay **after** global acquire (1.001292× old8–8192 aggregate, unpromoted) and0190's nonblocking CTA retirement (0.992183×, rejected). These are not per-route notification schemes;0190 was a measured valid protocol, not the hypothetical blocking cycle above.

`NONBLOCKING_RETURN_PREFIX_FEASIBILITY.md` already reviewed the exact distinct design of new per-local-token arrival masks plus a finite dequant ready-prefix loop after producer-tail. It was not implemented or timed. It would add system-release publications after each true row completion, system-acquire mask checks, bank/epoch storage and a sizeable owned return specialization; direct epilogue return needs its own producer protocol. The existing flag batch rotates +1 GPU-release expert-counter addresses and is not a per-route/system-release substitute (S/flag_batch.py:46–89,111–119).

**Recommendation: do not queue an existing-counter early-combine patch.** There is no existing fine-grained certificate to reuse, and no clean small owned hook for dispatch completion publication. Keep the earlier mask/prefix proposal as a transport/API ownership direction only. New counters, barriers or duplicated shared methods were explicitly outside this audit; current evidence does not establish that their overhead would buy useful overlap.
