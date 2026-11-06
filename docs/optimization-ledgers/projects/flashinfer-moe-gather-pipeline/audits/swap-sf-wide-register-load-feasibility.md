# Wider SF register loads with canonical shared stores

Read-only, 2026-10-30; retained c1ac / swap SHA482b636a. No source edit, GPU operation, or new measurement.

**Recommendation: hold a prototype.** The transport is technically feasible without changing the public alignment contract, using existing CuTe alignment metadata and automatic vectorization, but it needs an alignment-sensitive launcher cache key. More importantly, an exact prior LDG128→canonical STS transport trial was measured and rejected. Current Gather4 scheduling and the new SF MIO evidence distinguish the environment, not the underlying transport. This should be treated as an explicit reopening of that experiment, not a newly untested mechanism.

## Exact history, including the changed premise

Both closed-lead indices were checked. The old [sfload experiment](../../flashinfer-w4a4-split-dynamic-n/scripts/sfload_experiment/README.md) is a direct match: same SF row ownership, one 128-bit global load for 16 SF bytes, four bank-free canonical 32-bit stores. Eight focused paired FC1/per-token cases passed. At T16384/stage5:

| Historical FC1 µs | N128 | N256 |
|---|---:|---:|
| Control |281.472|286.400|
| Synchronous vector SF |496.641|338.305|
| Load before empty-stage wait |354.113|325.471|

The exact `vector_core.py:815–893` issues payload cp.async before loading/storing SF. `prefetch_core.py:815–904` loads SF before acquire, issues A/B copies, then scatters SF. Both use a producer-side proxy fence. These are not merely wider-cp.async or cache-hint trials. The old implementation restricted the path to SF16 and K divisible by256; that restriction must not be copied here. Its baseline used cp.async B rather than today's dedicated Gather4 group, and only baseline native resource counters were recorded, so the old result does not establish the current candidate's register allocation.

The later [SFB copy audit](../../flashinfer-w4a4-split-dynamic-n/scripts/sfload_experiment/SFB_COPY_AUDIT.md) profiled composed Gather4, found fragmented SF traffic, and deferred further staging work; it did not rerun synchronous register transport there. The newer [15d6 diagnostic](../experiments/sf-coordinate-cache/ncu-diagnostic/RESULTS.md) now directly demonstrates fourfold SF theoretical-sector reduction and TP SF issue/completion MIO samples1601→3, but replaces that pressure with coordinate LDS→R2UR dependencies. That supplies a motivation to separate transport from coordinate ownership; it does not show that synchronous loads preserve useful stage run-ahead.

## Alignment, tails, and actual CuTe API

Current public gather validation in [moe_swap_ab.py](../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab.py):346–385 guarantees byte-valued contiguous SF, row stride `R=K/sf_vec_size` divisible by4, and base address divisible by4. The pointer is explicitly created with alignment4 at147. A contiguous base+4 view is accepted even if R and stage SF bytes are16/32. Thus a fixed vector width based only on R and stage width is invalid; PTX vector accesses require natural alignment. [PTX9.2 addressing](https://docs.nvidia.com/cuda/archive/13.2.1/parallel-thread-execution/index.html#addresses-as-operands).

There is an existing metadata-only route:

1. Host-side effective base alignment `A=gcd(actual_data_ptr,R,32)` is safe and takes values4/8/16/32. Pass it through the existing `make_ptr(..., assumed_align=A)`, not through a new public or kernel parameter.
2. **Add A to `_blockscaled_kernel_cache`'s key.** Its current key at177–214 omits alignment and directly reuses the compiled callable at265–269. Without this change, an aligned first call could select code unsafe for a later base+4 view; the inner CuTe type system cannot repair this outer cache hit.
3. In the gather body let per-row stage bytes `S=tile_k/sf_vec_size`, `D=gcd(R,S,32)`. Use contiguous D-byte source/register views and the existing `cute.autovec_copy`; effective width is bounded by `gcd(A,D)` and register-view alignment. No runtime alignment branch or dtype/model whitelist is required. Dynamic row/K offsets must preserve their mathematically known D divisibility; leaving only the old `assume(divby=4)` may prevent widening.

This uses actual APIs: FlashInfer's `_Pointer.mlir_type` includes `_assumed_align` ([utils.py:282](../flashinfer/flashinfer/cute_dsl/utils.py)); vendored CuTe `algorithm.py:219–290` computes automatic copy width from layouts and `iterator.max_alignment`, capped at256 bits. [CuTe4.8 autovec_copy documentation](https://docs.nvidia.com/cutlass/4.8.0/media/docs/pythonDSL/cute_dsl_api/cute.html#cutlass.cute.autovec_copy) describes this policy. This is source/API feasibility, not proof of installed compiler lowering. The resulting alignment classes are compile-cache specialization requirements, not selectable tactics, but they are still extra cache complexity.

Tail proof: D divides R and S, so every final live D-byte chunk is complete. With `q=k_tile*S+j*D`, predicate `q<R` implies `q+D<=R`; all other chunks are zero. Keep existing row predicates: load only live rows, store zeros through `mma_n`, and do not write unused rows. SFB remains full N in each CTA, including group2. No vector may read across a row or past K. The base+4 specialization automatically retains scalar-width loads in the same body.

Existing explicit helpers are available but do not solve alignment automatically: `quantization_cute_dsl_utils.py:742` has `ld_global_v8_u32` requiring32B alignment; `cute_dsl/fp4_common.py:134` has regular `ld_global_v4_u32`; an experimental v2 helper also exists. Prefer the generic copy over new width-dispatch helpers. Do not substitute `.nc` loads: retaining ordinary global loads avoids changing the PDL/publication memory contract.

## Shared-store publication

The necessary change is **normal release arrival after all SF STS**, replacing each thread's `cp.async.mbarrier.arrive.noinc`. Keeping cp.async completion after generic stores would be incorrect: it orders prior cp.async operations only. Successful acquire wait observes prior producer STS under release arrival. The relay then retains its proxy fence and existing one-/two-CTA publication to MMA. PTX release/acquire transitivity and proxy-fence composition support that chain; this is a source-level derivation, not native qualification. [PTX9.2 mbarrier wait](https://docs.nvidia.com/cuda/archive/13.2.1/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-mbarrier-test-wait), [fence semantics](https://docs.nvidia.com/cuda/archive/13.2.1/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-membar).

Concretely: producer `STS → arrive.release(local)`; relay `wait.acquire(local) → fence.proxy.async.shared::cta → existing gather arrival`; MMA existing gather acquire then S2T. Group2 keeps the existing release/acquire cluster handoff in `_gather_mbarrier_arrive/_wait`, so both CTA-local SFB images remain published. The current `1+min(N,128)` local arrival count and payload expected-byte accounting remain unchanged because ownership and participant set do not change. Operand-empty acquire, stage advances, PDL wait, CLC metadata arrivals and terminal joins remain unchanged. No extra barrier follows from this substitution.

This is also the existing retained relay's proxy-placement pattern: the old acquire wait observes completed non-bulk cp.async generic-proxy writes; the new acquire would observe completed generic STS instead. Independent integration review found no missing edge under these explicit qualifiers; [earlier relay audit](gather-relay-proxy-fence.md) gives the source boundary. CUTLASS `PipelineAsyncUmma` supports ordinary async-thread producers; its tutorial's producer-fence-before-arrival is another valid placement, not evidence that this proposal may omit the cross-proxy fence entirely.

## Work and liveness tradeoff

For W=S/4 words per row, with a full-width load the transport changes **W cp.async → 1 LDG + W STS**, plus normal arrival instead of async completion. For W=1/2/4/8 this is1→2,2→3,4→5,8→9 memory instructions per row block before address/predicate/control lowering. If alignment limits width to V, the count is `S/V + W`; base+4 produces2W rather than W. Original canonical destination ownership remains bank-free. Wider same-row requests can reduce theoretical global-sector requests, but extra stores/issue and synchronous completion can offset that gain.

Loading SF, issuing independent Gather4, then consuming SF in scattered stores offers some latency-hiding distance. It does not guarantee that PTXAS schedules the LDG early or hides its dependency, and the producer cannot advance to the next stage until those STS and release arrival are issued. This is the old experiment's principal risk, now against a different payload engine.

Keeping an entire stage live across Gather4 adds `B*W` Uint32 values, B=max(1,N/128), up to16 under existing W≤8/N≤256 geometry. Unlike coalesced lanes, it does not multiply routed offsets or payload coordinates. Nevertheless the retained TP native image already has uniform/general-register pressure, so no zero-spill or residency claim follows from this count. The minimal adaptation still touches the host alignment/cache key and the load/store/publication block; it is not a pure instruction deletion.

Given the exact prior rejection, hold rather than silently repeat it. If explicitly reopened because of current Gather4/MIO evidence, the bounded first question would be whether the generic path emits wide loads while preserving base+4/tail correctness and current resources. No width-specific fallback, quota change, forced assembly, or performance screen is justified before that evidence. No implementation or launch was performed for this audit.
