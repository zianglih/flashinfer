# First scheduler claim after pipeline initialization

One fresh source-only candidate: initialize the atomic scheduler's cluster broadcast pipeline in `create()`, then move its existing **first counter claim** to warp7 after the common pipeline initialization wait and uniform WG1 register decrease, immediately before the dispatch-to-scheduler NB9 wait. Keep static first-work initialization after NB9 and leave every steady-state claim unchanged. No implementation or performance result is claimed here.

Base: published `ceb619b21b02fb9d6235edd3eed10ea06627ba51`, source `3b42507e7fd9c405c9e4112a0692942dc303c6d2a2cfd5268aeb57e67f72f186`. Scope would be only the maintained `megamoe_kernel.py` and `fc1_fc2_fuse_sched.py`. Five WGs, two decode WGs, all stages, transport, work-record ABI, launch shapes and the fixed eight tactics remain unchanged.

## Concrete serialization in the current source and native control

Owned scheduler `fc1_fc2_fuse_sched.py:758–819` currently combines two operations in `internal_init()`: creating the cluster pipeline with deferred synchronization, and performing the first leader-CTA/lane0 atomic plus full-warp shuffle. Owned `megamoe_kernel.py:1130–1133` calls this before `pipeline_init_arrive`; the common wait is at1156. Thus the first claim result is already consumed before scheduler warp7 can contribute its initialization-barrier arrival.

The completed raw-release N64 control confirms this is a native dependency, not just Python ordering:

| Operation | Saved SASS PC |
|---|---:|
| First returning `ATOMG.E.ADD.STRONG.GPU` | `08f0` |
| Compiler-generated result-consuming shuffle / add | `0930` / `0940` |
| Source full-warp broadcast | `0970` |
| Cluster initialization arrival | `09c0` |
| Cluster initialization wait | `0a00` |

The control is `profiles/cu132-recovery0910a-raw-release-before-tmem-wait-default-n64-001/codegen/`, result SHA `7e13bb98e205a5e9726272722cd8c40a7752f9d1e48d1ee752a1020d1c16331c`. Other roles cannot pass the common cluster initialization while its scheduler participant is still awaiting that counter result. The setup between source arrive/wait largely constructs static tensors; the actual saved sequence above has no substantial independent kernel work between them. This establishes ordering, not the elapsed cost of that dependency.

BF16 `src/moe_bf16_glu/kernel_bf16_glu_fc12.py:1217–1233,1255,1278–1286` and NVFP4 `src/moe_nvfp4_swapab/kernel_fc12.py:1542–1562,1612,1637–1649` use the same early-claim pattern and explain why static Mega initialization must follow metadata exchange. Their comments say the first atomic overlaps pipeline setup, but the returning atomic/shuffle before the arrival limits that overlap. This proposal uses their established metadata boundary; it does not change either vendor implementation.

## Smallest owned change and dependencies

1. Move the existing single-stage `PipelineAsync.create` from atomic `internal_init()` into the atomic branch of scheduler `create()`, storing the resulting object through the existing `cluster_pipeline` constructor field. All barrier initialization still occurs before the existing `pipeline_init_arrive` fence. There is no additional object, mbarrier, arrival or stage; moving the entire old `internal_init` after the wait without this separation would be incorrect.
2. On warp7, after the current common init wait and uniform WG1 decrease, perform the unchanged atomic `internal_init` before `sched_warp_pre_init_wait`. Static mode retains its existing `internal_init` after that wait. Leave the first cached-result finalization, all subsequent `gen_next_work` calls, publication and terminal tail unchanged. Retain the current ADD/shuffle implementation: immediate result consumption is acceptable once it no longer holds the common initialization barrier.
3. Keep every other warp's path as it is. Dispatch warps8–11 can now begin their finite metadata preparation/exchange while warp7 completes its first claim. No new communication specialization, public option, serialized state or extra live claim is needed.

The claim reads only the existing load-balance counter; it does not need per-expert sizes. Transport `token_comm.py:1563–1622` performs `dispatch_prep`, metadata exchange/barriers, NB9 arrival, then payload pulling. None consumes the scheduler's claimed index. Warp7 still waits at NB9 before mapping its first work, so no expert-size or offset read moves before metadata publication. Dispatch's own CTA, grid and rank barriers are unchanged.

The common initialization barrier remains in place for raw/decoded/activation/accumulator/work/cluster pipelines. The TMEM allocation retrieval barrier includes epilogue0–3, MMA4 and decode12–19, but excludes warp7 and dispatch8–11; the current source makes only the former roles call `wait_for_alloc()`. Moving the atomic after WG1's existing uniform register decrease also avoids delaying that donation. Neither dispatch metadata nor TMEM allocation needs the first claim result, so this adds no producer/consumer wait cycle or unstarted-CTA ownership dependency. Existing fixed-grid transport residency and final-only workspace reset remain requirements.

Only claim timing between CTAs can change, which is already dynamic atomic scheduling. Exactly one first claim per leader cluster, its cached value, cluster broadcast phases/participants, final invalid sentinel and zero-work behavior must remain intact. Do not replace the initial dynamic claim with a static block index or issue another speculative claim.

## History, admission and limits

The bounded ledger/candidate-index search found no completed first-claim-after-init trial. Entries074–075's ADD/INC/ELECT work moved **steady-state** claims before current-record publication and explicitly preserved the first cached claim; ELECT was rejected after the full sweep. This proposal neither repeats that placement nor uses its election/inline-PTX machinery. Descriptor startup prefetch was already rejected (ledger532–547), as were FC1 no-peek, larger work-metadata depth, group256, FC2 nonterminal BAR1 and the tail fence reorder. None is revived here. No CLC or shared-operand-release work is included.

Before any numerical/performance admission, native must show: all mbarrier initialization still precedes the init fence/arrival; the returning first atomic and its dependent shuffle are after the common cluster wait, isolated to warp7 and before NB9; dispatch can reach its body independently; steady-state claim/publication order and legal resources are unchanged. The remaining uncertainty is how the DSL carries the existing pipeline/state object when construction moves to `create()`; the established constructor field and late static initialization provide narrow source precedents, not a guarantee of identical register allocation.

The expected benefit is limited to startup. Current profiling points to first-work waits but does not isolate the first counter round trip; dispatch metadata or rank skew may dominate instead. Removing this initialization dependency can be neutral or worse if the later claim is not hidden by metadata work. Use the existing whole retained3b425 result as BEFORE only if root chooses a trial; no new baseline or shape dispatch is proposed. This audit performed source/history and saved-SASS reads only, with no primary edits, runtime imports, tests, compilation, validators, remote or GPU work.


Root checked the current [PTX9.4 setmaxnreg contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#miscellaneous-instructions-setmaxnreg)
for the intervening WG1 donation. Its synchronization is within each warp;
all warps in a warpgroup must execute the same instruction, and explicit group
synchronization is required before another redistribution. The proposal retains
the single uniform decrease and introduces no second redistribution. It does
not add a new warpgroup rendezvous between warp4's TMEM wait and warp7's claim;
actual generated control flow still needs native inspection.
