# W4A16 pipeline audit, 2026-10-27

Source baseline: `1496b557`; review checkout: `flashinfer-w4a16-sync-review`.

## Resource lifetimes

| Resource | Producer | Consumer | Readiness | Last use / recycle | Decision |
|---|---|---|---|---|---|
| Packed weights and E4M3 scales, SMEM | Weight TMA warp 6 | Transform warps 8–15 | One TMA transaction barrier includes both byte counts | All transform warps finish input reads; retained release follows BF16 destination store | Already share phase and barrier; retain. Earlier release was repeatedly slower in the historical ledger. |
| BF16 transformed weights, TMEM (or SMEM alternative) | Transform warps 8–15 | MMA warp 4 | TMEM-store view fence, or SMEM async proxy fence; then async/UMMA full commit | UMMA completion empty barrier after last dependent MMA | Essential publication fence and completion; independent from activation readiness. |
| BF16 activations, SMEM | Activation TMA warp 7 | MMA warp 4 | TMA full barrier, after PDL dependency wait | UMMA completion empty barrier | Keep separate from raw weight stage. Its ring depth differs from transformed weights, so sharing an empty barrier would require changing storage/ring design. |
| Accumulators, TMEM | MMA warp 4 | Epilogue warps 0–3 | UMMA completion full barrier | Last active subtile loaded; TMEM-load fence then one release per epilogue warp | Already releases before activation/output conversion. Cannot remove fence or wait. |
| Output staging, SMEM | Epilogue warps 0–3 | TMA store warp 0 | Async proxy fence plus epilogue named barrier | TMA store group read completion, then CTA epilogue rendezvous | Both barriers protect actual inter-warp publication/reuse. Defer-to-reuse experiment previously neutral, so no blind repeat. |
| Fused-finalize scales, SMEM | Epilogue threads by route | Epilogue threads by fragment | Epilogue named barrier | Scale consumed before output scratch publication | First async proxy fence has no async consumer, but fused-finalize performance is explicitly outside current focus; keep scoped changes. |
| Fused-finalize payload, SMEM | Epilogue fragment owners | Per-route bulk reduction | Async proxy fence plus epilogue named barrier | Bulk read completion plus epilogue named barrier | Necessary. |
| Routing tile info, SMEM | Scheduler warp 5 | Every other warp | Generic shared stores plus release/acquire metadata pipeline | Consumers copy four values into registers and release | No async data proxy; generic→async fences redundant. CLC agent owns their removal and single-lane publication. |
| CLC response, SMEM | Cluster cancellation query | Scheduler warp 5 | CLC transaction completion | All consuming scheduler lanes release | CLC agent owns modernization. Do not conflate response completion with generic tile-info publication. |
| TMEM allocation pointer | Allocator warp 0 | MMA/transform/epilogue roles | Allocation/retrieval named barrier | Epilogue TMEM free follows last accumulator load and release | Restricted role-only barrier already benchmarked and rejected historically. Retain established allocator sequencing. |

MMA release of activation and transformed weights occurs after the same instruction sequence but the rings do not have the same depths, phases or physical slots. A shared empty ring is not a mechanical safe change. Weight and scale inputs already have the exact shared lifecycle that justifies merging them.

## PDL

Only the activation-load role waits for dependent payloads. Static weights/scales and decode can run ahead until capacity backpressure. FC1 publishes dependents from its weight role; standalone-combine startup is signaled from FC2 activation role after its dependency wait. The preparation owner is auditing routing publication while consolidating preparation. Do not move activation loads before the wait or remove it based on independent weight readiness.

## Historical exclusions

Consulted `/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md`:

- Raw-weight/scale merged barrier was retained; extra scale-TMA warp, scale EVICT_FIRST, and early input release were rejected.
- Restricted TMEM allocator participant set was rejected (lines 1309–1347).
- Extra nonblocking activation acquire was rejected (1927–1949).
- Dual MMA-ready peeks, late transform acquire, fragment lookahead and fragment-local TMEM store were rejected (5310–5570).
- Deferred deterministic output-store wait was neutral and removed (5610–5658).

## Candidate: static weight extents

The launcher knows weight M and K but passes both as runtime Int64, and the compile cache deliberately omits them. This leaves weight strides, scale-layout arithmetic and K-loop bounds dynamic across all three models. The new blockscaled implementation specializes weight shapes. A small candidate can make M/K constexpr while preserving dynamic token extent N, and include M/K in the kernel cache. Measure compilation cost and generated instructions as well as end-to-end latency; this has no model-specific policy and changes no numerical or synchronization contract.

The candidate is now unstaged in the review copy. It also removes M/K from the compiled runtime invocation, because CuTe removes constexpr parameters from that ABI. N remains a runtime argument. The initial compile gate caught that required invocation change before any candidate timing; the corrected candidate will use a new source-bound deployment.

The first fixed-tactic helper attempt accidentally used the blockscaled route-prefix tactic encoding; W4A16's encoding is only the FC1/FC2 GEMM pair. Corrected the task-local helper; that failed control attempt produced no timing. Failed evidence remains separate from the corrected deployment.

## Deferred startup synchronization idea

Installed CuTe's `pipeline_init_arrive` performs the barrier-init fence and optional cluster arrival; `pipeline_init_wait` performs a CTA barrier for singleton clusters or a cluster wait otherwise. W4A16 subsequently calls the full-CTA TMEM allocation wait. The singleton CTA barrier may be subsumed, but removing it would require a new singleton/cluster policy or replacing the established helper flow. Preserve it in this round: the user explicitly asked to retain this helper and avoid unnecessary diff. No timing or generated-code evidence currently justifies a production change here.

Installed helper source is recorded in `pipeline-implementation.txt`. Independent review of the CLC candidate confirms its elected lane owns all four generic shared stores and the release arrival; the full/empty pipeline orders generic shared metadata reads and reuse. Its removed async proxy fences did not connect to an async consumer.

## Independent composed-candidate review

Reviewed `flashinfer-w4a16-composed-review` after preparation, CLC and static-weight-extents composition. No synchronization blocker found:

- Metadata producer count is one and commit occurs inside the same elected lane as all four generic SMEM stores at all three publication sites. Consumers wait, materialize all four scalars, and release before their role's payload work. Every non-scheduler thread participates, including both CTAs where required; no generic metadata reader relies on the removed async proxy fence.
- CLC response consumers remain `32 * cluster_size`; its transaction barrier and terminal producer tails are retained. These are distinct from the local generic tile-info ring.
- All payload pipeline barriers, SMEM/TMEM publication fences, accumulator early release, output-store read-completion waits, and `pipeline_init_wait` remain unchanged by composition.
- Shared preparation preserves BF16 byte copies and untouched invalid rows, 256-thread geometry, and original 128/256-bit alignment contract. The PDL wait precedes routing reads; launch-dependent signaling permits independent FC1 setup/weight prefetch while the activation TMA role still waits for copied activations.
- M/K and `max_active_clusters` are explicit kernel cache keys in composition. Runtime N is omitted, as required for token-count cache reuse. The shared CLC bit is included and the autotuner cache schema is versioned for the changed tactic tuple.

The isolated static-extents patch changes no synchronization operations. Retention is based on simplifying generated addressing/loop bounds plus the focused exact gate and neutral timing screen, subject to root's composed AUTO comparison.

## Codegen evidence correction

The initial timing workers compiled concurrently from a shared source CWD. Some retained PTX/cubin files were inconsistent across model/phase (for example K3's expected SiTU signature was replaced by a V4.1 SwiGLU signature). Those captured artifacts and all aggregates derived from them are excluded. The timing runs themselves completed and source-paired output hashes match; no performance rerun is inferred from the codegen correction.

`codegen_probe.py` and `codegen_worker.py` instead compile each source/model/token/FC in its own CWD, serially, using documented `CUTE_DSL_NO_CACHE=1` and a distinct `CUTE_DSL_CACHE_DIR`. They immediately save PTX/cubin, disassemble the saved cubin, record hashes and kernel names, and check expected activation signatures. `codegen_analyze.py` verifies source hashes against the timing arms, PTX/cubin names, file hashes, all FP32 exp2 signatures, resources, spills and non-NOP instruction counts. Installed SDK environment documentation is in `sdk-cache-documentation.txt`.
