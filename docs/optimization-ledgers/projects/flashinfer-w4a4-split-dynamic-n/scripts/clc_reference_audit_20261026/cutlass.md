# CLC audit against CUTLASS

Read-only source audit, 2026-10-26. No production edits, GPU kernels, or timing runs.

## Pinned sources

- FlashInfer PR7290: `flashinfer/`, commit `9b4721b08057d0a488c1f0236467acb75c48cd00`.
- Official CUTLASS: `references/cutlass/`, commit `91843b71d90737e0a9b86f7d9df213cff5a3526f` (v4.8.1, 2026-10-20), cloned from `https://github.com/NVIDIA/cutlass.git`.
- Actual benchmark dependency: CuTe DSL **4.7.1**, imported read-only from the existing c3 virtualenv. Exact class/function text and hashes are in `sdk-source.json`, `sdk-*.py`, and `cutlass-receipt.json`. Import did not create a CUDA context or run kernels. Its `PipelineClcFetchAsync` hash matches the earlier SDK capture.
- `PipelineClcFetchAsync` and `issue_clc_query` are AST-identical between captured4.7.1 and reference4.8.1. `clc_response` differs only in4.8.1 removal of explicit `res=` result-type arguments to the NVVM query bindings; both perform the same plain128-bit shared load and contain no warp synchronization/election. Use captured4.7.1 APIs for any experiment.
- FlashInfer's CUTLASS submodule is uninitialized locally; its pinned C++ commit is `b46b16d003484063bca4ed365e44095c4c6ed633`. This is distinct from the installed Python DSL and the newly cloned reference.
- A pre-existing read-only TransformerEngine submodule is CUTLASS4.2 (`57e3cfb47a2d9e0d46eb6335c3dc411498efa198`, 2025-09-15). It was used only for initial orientation; conclusions below use current official source and exact SDK4.7.1.

`K` below means `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py` in FlashInfer. CUTLASS paths are relative to the pinned reference clone.

## Lifecycle and ownership

| Contract | Current FlashInfer | CUTLASS reference and conclusion |
|---|---|---|
| Initial job | Physical launch coordinates through `initial_work_tile_info`; same mapping is used for startup weight prefetch (K1477–1519). | SDK `sdk-ClcDynamicPersistentTileScheduler.py:256–270` does the same. Preserve this agreement when changing ownership. |
| Claim ownership | Only CTA0 scheduler warp acquires the response slot and issues cancellation (K2111–2116). | CUTLASS DSL `dense_gemm_persistent_dynamic.py:1009–1030` uses CTA0 scheduler too. No missing leader restriction. |
| Response storage | One aligned16-byte response per CTA; one full and one empty barrier (K1121–1127,1405–1414). | CUTLASS dense DSL explicitly uses one response stage (`dense_gemm_persistent_dynamic.py:440–442`). Single-stage response is not an implementation gap. |
| Cluster notification | SDK producer acquire uses lanes0…cluster_size−1 in CTA0 to arm each CTA's full barrier; hardware multicasts response. | Exact SDK `sdk-PipelineClcFetchAsync.py:24–37,108–119,138–167`. A whole-loop election cannot preserve this unmodified for2CTA. |
| Response consumers | All32 scheduler lanes in each CTA consume response; `32*cta_group_size` arrivals return to CTA0 (K1409–1411,2140–2143). | SDK consumer release is a single underlying arrive per executing thread, with destinationCTA0 (`sdk-PipelineClcFetchAsync.py:117–119,194–201`). Counts match current participation. |
| Publication to workers | Scheduler computes expert/valid metadata once per CTA; one elected publisher writes three fields and commits the local queue (K2117–2138). All160 or288 worker threads read and release it (K1233–1246,1396–1403). | CUTLASS dense DSL has workers consume/decode rawCLC response directly (`dense_gemm_persistent_dynamic.py:997–1000,1109–1112,1391–1394`). Our extra queue avoids repeating MoE routing loads in every worker and decouples response ownership from worker progress. It is not automatically redundant. |
| Proxy ordering | Scheduler response decode inserts async.shared fence before response slot release. | Exact SDK `sdk-ClcDynamicPersistentTileScheduler.py:216–238`; its doc explains generic-read→next-async-write protection. Keep it unless replacement load/order semantics are proved. |
| End of work | Invalid response produces terminal local metadata. Local worker release is drained by final CTA join; CTA0 separately drains CLC response before exit (K2144–2156). | SDK `PipelineAsync.producer_tail` waits all response-empty stages to prevent arrivals to an exited CTA. Current CUTLASS C++ retains the CLC tail too. Removing local metadata tail does not justify removing response tail. |

`blackwell/custom_pipeline.py` defines operand/accumulator pipelines, **not** a CLC implementation. The kernel imports `PipelineClcFetchAsync` directly from the installed CUTLASS pipeline package. Do not attribute its lane-distributed arming behavior to a custom FlashInfer CLC class.

## Claim timing and queue depth

The retained scheduler acquires the local metadata slot before requesting another job, then publishes current metadata while cancellation runs. This has a useful workload balance constraint: the fast scheduler cannot claim arbitrary work ahead of slow payload consumers. Invalid padded routes are skipped without entering the worker queue (K2107–2116).

Current CUTLASS C++ SM103 explicitly has a separate throttle pipeline. The loader publishes progress and scheduler waits for it before requesting another job, with a source comment explaining workload imbalance from persistent-worker skew:

- `include/cutlass/gemm/kernel/sm103_blockscaled_gemm_tma_warpspecialized.hpp:590–605` configures throttle ownership.
- `:758–766` gates claim on throttle; `:820–824` publishes loader progress.

This supports retaining a bounded progress dependency, not copying another barrier into FlashInfer. Our metadata queue already supplies backpressure. CUTLASS's exact queue depth/default is not performance evidence for our MoE pipeline. Prior rejected request-before-slot-acquire and deeper metadata queues remain rejected; this audit does not reopen them or add a tuning axis.

Current public FC1/FC2 wrappers both pass `num_tile_info_stages=1` (`blockscaled_contiguous_gather_grouped_gemm_act_fusion.py:992`, `blockscaled_contiguous_grouped_gemm_finalize_fusion.py:993`). CLC adds one warp to160/288worker threads, yielding192/320total threads (K395–399). Raw scheduler storage is64bytes perCTA at one metadata stage:16metadata +16metadata barriers +16response +16response barriers. The budget formula reserves80bytes including alignment headroom (K488), then rounds the whole metadata slab. These are compile-time resource choices; no additional search dimension is needed.

## Most useful new experiments

1. **One elected scheduler owner perCTA, preserving the existing queue and claim order.** FlashMLA provides the stronger motivation; CUTLASS source defines the API changes needed to implement it safely. Change response-empty participants from `32*cta_group_size` to `cta_group_size`; each CTA owner arms its own full barrier for16bytes, CTA0 owner waits for empty and issues one multicast query, all CTA owners wait/read/fence/release. Keep terminal CLC drain on CTA0. Use raw `cute.arch.issue_clc_query` inside the elected loop: SDK `Scheduler.advance_to_next_work` already performs an election, which should not be nested under a full-loop election. Raw issue and response decode have no hidden warp collective (`sdk-issue_clc_query.py:22–38`, `sdk-clc_response.py:20–72`); `sdk-elect_one.py` lowers to `elect_sync`. Existing info publication already has one producer, so move its election outside the loop as part of ownership refactoring rather than adding another election. This is a protocol change requiring1CTA/2CTA and terminal/padded-route validation, not a textual wrapping of the existing loop.
2. **Remove scheduler dependence on TMEM pointer readiness.** Current kernel's TMEM retrieve barrier includes every CTA thread, including scheduler (K1416–1425), and all execute allocate/wait/retrieve before scheduler work (K1439–1441). The scheduler never consumes TMEM. CUTLASS dense DSL's retrieve barrier contains only MMA and epilogue participants (`dense_gemm_persistent_dynamic.py:748–750`); the scheduler runs without retrieving TMEM. Excluding our scheduler from the rendezvous could let routing publication/CLC startup progress earlier with PDL. Update barrier count and participating call sites together; preserve the cluster barrier-init fence/join and final CTA join. This can be a uniform role-based implementation, independent of model/dtype/tile dimensions.
3. **Inspect redundant barrier-init fences after the two above.** Custom operand and accumulator constructors each issue an init fence (`custom_pipeline.py:71,226,374`), then the kernel issues another after CLC/SF barrier initialization (K1434–1438). A final collective initialization boundary could make earlier fences unnecessary in this caller, but changes must preserve other users and static/singleCTA paths. This is lower priority and needs generated PTX/SASS confirmation; do not broaden shared utilities on inference alone.

Single-lane ownership is **not** a32× reduction in issued instructions. Warp instruction issue counts can remain identical with fewer active lanes. Potential savings are fewer barrier arrival transactions, fewer repeated elections/branches, and a simpler ownership protocol; register/resource and end-to-end effects must be measured. Keep exact mathematical behavior and the shared360-vs-independent720autotune comparison isolated from these kernel experiments.

## TMEM exclusion proof and minimal proposal

The exact deployed4.7.1 allocator is captured in `sdk-TmemAllocator.py`:

- Constructor initializes the2CTA deallocation barrier only from the configured allocator warp, with32arrivals; scheduler is not one of its participants (`:25–47,129–139`). Preserve the constructor and its initialization before the existing cluster join.
- `allocate` only issues `alloc_tmem` from allocator warp0 (`:219–230`). It also updates object bookkeeping (`:231`), so the smallest change can leave `tmem.allocate(...)` in common code. There is no need to move or duplicate physical allocation.
- `wait_for_alloc` only calls the configured named barrier (`:234–244`). Its present count is192/320 underCLC, covering160/288workers plus32scheduler threads. The reduced count should be160/288, preserving all existing worker roles.
- `retrieve_ptr` reads the shared holding address and creates the pointer; it supplies no synchronization (`:247–265`). It must remain after `wait_for_alloc` for every actual TMEM user. Scheduler must bypass both waiting and pointer retrieval, not read a not-yet-published pointer and hope dead-code elimination removes it.
- Current pointer users are confined to the producer/inline-epilogue role (K1753), dedicated epilogue role (K1837,1864), MMA role (K1904,1914,1931,1960), and final freeing role (K2159). Scheduler's path atK2091–2152 has no pointer use. Moving wait/retrieve into the existing worker role blocks is one structurally safe option; if retrieval is needed again in the final `warp<4` freeing block, retrieve there after the final join rather than creating a pointer with an uninitialized incoming SSA value. A scoped common worker branch is another option if CuTeDSL can preserve the typed pointer cleanly.
- `free` synchronizes and deallocates only allocator warp0 (`:339–376`). For2CTA, warp0's32threads arrive at the peer barrier and wait for the local peer completion; it does not use the TMEM retrieve named barrier. Scheduler exclusion therefore does not remove any remote-deallocation participant. Current `warp<4` permit/free code and128thread namedbarrier2 can remain unchanged (K2156–2159).

**Important initialization caveat:** under1CTA CLC, the existing TMEM retrieve barrier is also the first CTA-wide rendezvous after deferred CLC/info-barrier initialization. The explicit init fence atK1435 does not make other warps wait for warp0 to finish initializing those barriers. Excluding scheduler from retrieval without a replacement initialization rendezvous would let it use uninitialized barriers. Under2CTA the existing cluster arrive/wait atK1436–1438 already provides this rendezvous and must remain.

Minimal safe ordering is:

1. Construct operand, accumulator, info, response, and TMEM allocators exactly as today; initialize optional SF-ready barriers.
2. Complete the common barrier-initialization boundary before role divergence. Preserve2CTA cluster arrive/wait. For1CTA CLC, add a CTA initialization rendezvous before allocation. This is a required synchronization distinction, not a workload-dependent optimization policy. The CUTLASS `pipeline_init_arrive`/`pipeline_init_wait` helpers encode this distinction (`python/CuTeDSL/cutlass/pipeline/helpers.py:1147–1188`), but exact4.7.1 helper behavior should be captured before substituting them.
3. Leave common `tmem.allocate` bookkeeping, while only the160/288workers participate in namedbarrier3 and retrieve the pointer; scheduler immediately proceeds with its own metadata work.
4. Leave payload/PDL waits, the response-tail drain, final all-thread namedbarrier1, and the2CTA deallocation handshake unchanged.

Startup weight prefetch currently begins atK1490 and issues only in warp0, after its TMEM readiness wait. This proposal need not move it. Scheduler bypass is independently useful because scheduler can decode/publish initial work and request bounded future work while warp0's allocation/pointer readiness blocks the workers. With `prefetch_weights_before_wait`, the existing routing-publication contract already lets scheduler skip the payload wait atK1523–1531; without it scheduler still waits as today. No claim is made that the added1CTA init rendezvous has net positive latency; compare SASS, startup traces, and end-to-end timing before retaining.

## Not recommended from this audit

- No extra CLC depth, throttle, or ownership autotune axis.
- No switch to direct raw-response consumption just to resemble CUTLASS; preserve MoE metadata reuse until an independently measured replacement beats it.
- No deletion of the response proxy fence, CLC producer tail, or2CTA initialization join based solely on a shorter reference implementation.
- No use of upstream mixed-cluster or special-shape policies as a new model/dtype branch in this backend.
- No claim that CUTLASS defaults are fastest. It supplies lifecycle examples and API invariants; performance decisions require this backend's V3/V4.1-Flash/K3 measurements.

## Reproduction

Read-only SDK capture:

```sh
python3 nvfp4-epilogue-port-20261026/remote_exec.py \
  scripts/clc_reference_audit_20261026/read_sdk.py \
  > scripts/clc_reference_audit_20261026/sdk-capture.b64
```

The receipt records hashes of all source files cited above. The official commit can be browsed at https://github.com/NVIDIA/cutlass/tree/91843b71d90737e0a9b86f7d9df213cff5a3526f . No benchmark or correctness result is inferred from this source-only audit.
