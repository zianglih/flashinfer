# W4A16 MegaMoE: 32-byte alignment and native 256-bit global accesses

Read-only source audit, 2026-09-26. Baseline is HashInfer `cd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7` in `../../hashinfer` (paths below are repository-relative). Other agents' current candidate edits are not treated as baseline. No source edits, GPU runs, or GitHub operations were performed by this audit.

The user's current instruction supersedes the historical preserve-16-byte/fallback preference: establish a real 32-byte contract, reject violations, and evaluate native 256-bit copies. This does not justify pretending that every scalar/metadata access is 32 bytes or that a 32-byte allocation makes arbitrary slices 32-byte aligned.

## Recommended order

| Priority | Site | Present behavior | Candidate benefit | Ownership / decision |
|---|---|---|---|---|
| 1, current trial | Final BF16 top-k payload | 8 BF16/lane, one LDG128 per route and one STG128 | For the same 16 output elements, top8 payload instructions can drop from 16 loads + 2 stores to 8 loads + 1 store | Entirely W4A16-owned; 32-byte combine/output bases, contiguous hidden rows, 16-element worker |
| 2, smallest additional change | Final-combine FP32 routing-score prefetch | Top8 row is 32 bytes but frontend promises 16; current SASS uses two LDG128 at each prefetch site | Top8 score row can become one LDG256; top16 can use two | Internally allocated score buffer; requires aligned base and a row stride divisible by 32 bytes. Keep this a separately measured stacked change if the payload trial does not already include it |
| 3, broader contract | BF16 input staging | 8 BF16/lane, explicit LDG128/STG128; generic strided source path also exists | 16 BF16/lane can halve bulk memory instructions and amortize loop/address work | W4A16-owned implementation, but source is caller-owned. Existing support includes strided and offset inputs; stricter source contract affects those callers. A true256 prototype was previously measured and rejected; see below |
| Existing, not new | FC1 and direct FC2 global stores | Already explicit native 256-bit stores with 32-byte pointer annotations | No new width opportunity | Strengthened allocation/validation closes proof gaps; do not claim these stores were newly enabled |
| Low priority | Counter-prefix bulk clearing | Scalar Int32 zero stores after the required drain/publication points | Theoretical 8-to-1 stores for full 32-byte groups | Tiny prefixes, fewer active lanes and stricter bank alignment; synchronization-sensitive shared vendor path. Not an LDG256 opportunity and not recommended for this round |

The cleanest new **payload** opportunity after final combine is input staging. The cleanest **small instruction-count** opportunity is routing-score prefetch. Both need separate codegen and timing evidence; neither is a demonstrated current-head speedup.

## Exact alignment proof for combine and output

`cute_dsl/megamoe/bf16_nvfp4/topk_reduce.py:18-19,64-116` sets 8 hidden elements per thread and 128-bit copies. `frontend.py:111-114` requires H divisible by 32 and I divisible by 64. For compact BF16 combine `[T,K,H]`:

```
address = base + 2 * ((token * K + route) * H + hidden_start)
```

With `base % 32 == 0`, `H % 16 == 0`, and `hidden_start % 16 == 0`, every 16-BF16 payload address is naturally 32-byte aligned. Existing H%32 is stronger than needed. The same proof applies to compact output `[T,H]` with route omitted. Bounds must cover all 16 elements; the existing H%32 removes a hidden-dimension tail. Empty live output ranks perform no payload access, but must still participate in the collective kernel.

Baseline `frontend.py:629-652` checks combine shape/dtype/device and output contiguity, but does not establish combine contiguity or either pointer's 32-byte alignment. Raising `_to_cute`'s default would conceal rather than close that gap. Check actual source layouts/pointers before constructing the stronger CuTe descriptor; reject bad lower-level inputs. The native output is internally allocated by `modes/mega_layer.py:420-430` using `torch.empty`. Its post-allocation contract can be enforced in FlashInfer/HashInfer without changing the SGLang integration.

`get_symm_buffer_for_bf16_nvfp4_mega_moe` owns symmetric activation, routing IDs, scores, and combine buffers (`frontend.py:850-858`). `kernel_combine_output` only reshapes/slices at offset zero. Shape/row-stride proofs hold for these compact allocations once actual base alignment is established. Direct FC2 peer writes also need the mapped peer address aligned; a local assertion alone does not establish an arbitrary peer mapping.

## Routing-score prefetch

`topk_reduce.py:31-40` copies one complete score row into registers when top-k <=16, independently for each hidden worker. For K=8, the FP32 row is exactly32 bytes; for K=16 it is64. Payload vector widening halves the number of workers and therefore already halves the number of score prefetches for a given output tensor. Native256 score prefetch can additionally halve the number of memory instructions within each remaining top8/16 prefetch.

Baseline `_runtime_kwargs` uses `_to_cute(inputs.topk_weights, static_layout=True)` with the16-byte default. In the cd7cc07 native SM103a SASS, pairs at `0x14ec0/0x14ed0`, `0x15ba0/0x15bb0`, and `0x16900/0x16910` load contiguous16-byte halves. The first address is computed from `token * 8 * 4`; this agrees with the top8 score-row prefetch. These are static code sites repeated for different retired roles, not a claim that one worker executes all three sites. Check the candidate's source-bound disassembly rather than infer success from a copy-width argument.

K is accepted in `[1,32]`, not only8. A contiguous FP32 row has byte stride`4*K`; base alignment alone is insufficient when K is not divisible by8. There is no benefit in overreading padded rows or restricting all supported K values merely to widen this small input. Exact-fit compile-time widths for actual row lengths are a separate issue from a runtime fallback for a violated 32-byte buffer contract. If the current task requires every score row to satisfy32-byte alignment, padded score-row allocation/strides and all consumers must be changed consistently; this is a broader ABI/layout change than the combine payload contract.

Scores are also consumed in dispatch and FC1, but those accesses differ: vendor `dispatch_pull` reads exactly one selected FP32 score in lane0 per token (`src/src/token_comm.py:1032-1045`), and the FC1 epilogue reads one pool-row score per lane when applying top-k in FC1 (`epilogue.py:602-610`). Fetching eight unrelated scores per lane would not reduce useful instructions. Scalar per-expert alpha/norm loads likewise remain scalar and naturally4-byte aligned.

## Input staging: worthwhile but previously tested

`cute_dsl/megamoe/bf16_nvfp4/token_comm.py:24-75` divides hidden input into16-byte chunks, with128 dispatch threads/CTA. The compact source branch builds a flat `(8,live_chunks)` BF16 tensor and explicitly issues128-bit copies. The generic branch uses the caller's row/column strides and natural2-byte alignment. The target is the internally allocated symmetric BF16 input buffer. Publication uses the existing `fence_proxy("async.global")`; wider copies must retain its ordering and the later grid/NVLink publication.

An all256-bit compact implementation can use32-byte chunks and16-BF16 registers. Source and destination bases must be32-byte aligned; compact BF16 rows with H%32 satisfy row alignment. More general rows with hidden stride1 are also possible if `2*row_stride % 32 == 0`; arbitrary column strides are not a native256 vector. That is a real source contract, not one guaranteed by output allocation.

Source ownership is explicit in `backends/mega/kernel/sm100/bf16_nvfp4_bf16_cutedsl/backend.py:224-286`: the backend stores the original `(hidden_states,topk_ids,topk_weights)` references for fused staging. `frontend.py:_staging_key/_staging_args` currently distinguishes compact16-byte versus generic input variants. SGLang's `run_flashinfer_megamoe` passes `x.to(torch.bfloat16)`. If `x` is already BF16, `.to` can preserve the original storage/layout; this source line does not prove32-byte alignment. Consequently the earlier “no SGLang changes needed” conclusion is exact for internally owned combine/output buffers, not an unconditional guarantee for a future strict256-bit input source contract.

Historical evidence is preserved under:

- `/Users/ziangli/playground/projects/hashinfer-w4a16-megamoe/integrated-topk-20260918/input-stage-bulk-copy256-capture/RETENTION.md`
- Its `codegen-selected/INDEPENDENT_EARLY_CODEGEN_REVIEW.md`.

That true256 staging prototype `0103fe15` emitted `ld.global.v8.b32` and `st.global.v8.b32`, with native `LDG.E.ENL2.256` at`0xb4e0` and `STG.E.ENL2.256` at`0xb520` in the inspected H7168/EP8/T16384 selected variant. The review saw no local spills in that selected variant. It preserved a128-bit first stripe, then used256-bit bulk pairing. The historical comparator reported104 exact output pairs, decode4–512 geometric speedup**0.987328645×**, and4K/8K/16K prefill**1.017893978× /1.001095391× /1.010866466×**. It was not retained. Full archive qualification was explicitly incomplete in the early codegen review; do not relabel it as fresh current-head qualification.

The observed mapping concern remains relevant: H7168/EP8/T256 leaves9,728 old16-byte chunks after the first18,944-thread stripe. Pairing those into256-bit copies drops residual coverage from76CTAs to38. The ledger calls this a plausible contributor, not a proven sole cause. An all256 implementation changes the first stripe too and must be tested afresh. The old alignment-preservation objection is superseded by today's request; the decode/parallelism concern is not.

## FC1/FC2 already use256-bit stores

FC1 `epilogue.py:588-715` constructs a256-bit BF16 store atom and writes16 output elements. The destination is the internal FC1 output pool. Each hidden start is`tile_m*64 + warp*16`; BF16 byte offset is a multiple32. The row stride is I BF16 with I%64. Kernel workspace `_RegionSpec("fc1_output",...,align=128)` guarantees a128-byte region offset relative to the local allocation. The allocation base still needs a true guarantee/check. The current cast to `assumed_align=32` is not itself proof.

Direct FC2 `tmem_epilogue.py:584-626` computes`stg_width_elems=min(32,256/dtype.width)=16` for BF16 and uses256-bit copies. `Fc2OutputRouter` constructs32-byte destinations; each hidden start is a multiple16BF16, and compact H%32 rows preserve alignment. Peer metadata selects token/route/rank but does not change hidden alignment. Both peer combine output and local return workspace paths are covered by this reasoning. The mapper call explicitly requests`byte_align=32`.

The cd7cc07 original CUBIN SASS (`../marker-coverage-20260925/audit-2/original-pmtrig.sass`) already has six native256 store sites at`0x6e90,0x7170,0x8310,0x8320,0x8460,0x8470`. There are no native256 LDG sites in that inspected specialization. These six store sites agree with the FC1/directFC2 source, so the candidate should not claim a six-store256 breakthrough. Record deltas in the precise reducer/staging regions.

## Paths that are not LDG256 candidates

- **Packed weights, block scales, FC1/FC2 activations:** `megamoe_kernel.py:_load_weights/_load_activations` issues TMA copies to shared memory. TMA already transfers whole tiles. Replacing these with per-thread LDG256 is a pipeline redesign, not an alignment win.
- **NVSHMEM token pulling and reused dispatch returns:** vendor `dispatch_pull` uses a TMA bulk load into each warp's shared pull buffer, then a TMA bulk store to the FC1 pool. `token_back_by_push` uses the corresponding bulk load/store or bulk reduction for returned FC2 data. These are already bulk paths; raising a CuTe global pointer assumption cannot make them LDG256.
- **NVFP4 transform:** the inherited `fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:_transform_tile` reads packed weights/scales from **shared** memory after TMA, decodes in registers, and writes TMEM. `num_bits_per_copy=32` in the Mega caller describes the shared packed-element path, not a32-bit global weight load. The previous TMEM store widening was explicitly withdrawn; this audit does not propose reintroducing it.
- **Scheduler work records:** `custom_ext.py:write_to_smem` copies8Int32 fields to **shared** memory using128-bit operations. A global256 contract is irrelevant. Shared-memory width/record publication would be a different optimization.
- **Counters and metadata:** routing counts, release/acquire flags, atomics, readiness probes and one8-byte provenance record per selected token have semantic dependencies and sparse/dynamic ownership. Do not coalesce independent synchronization objects into a wider global transaction simply because their allocation is aligned.
- **Weight preprocessing:** gate/up interleave, scale swizzle and quantization live outside the timed public forward and already use Torch operations or their own CuTe kernels. A forward speedup cannot be claimed from strengthening prepared-weight pointer annotations; packed weights are subsequently read through TMA.

## Allocator and shared-helper boundary

The shared `kernel_src/sm100/cutedsl_megamoe/shim/comm.py:sym_zeros` currently calls`nvshmem.core.tensor(shape,dtype)` then zeros it; the plain-CUDA branch calls`torch.zeros`. It supplies no explicit alignment argument and checks no actual pointer. `_compute_peer_offsets` obtains real peer addresses for the workspace and preserves the NVSHMEM pointer-difference model. A W4A16-local contract check can be added without copying this whole allocator. A natural shared helper extension is possible if accepted for all call sites, but must preserve collective allocation/free ownership and the existing allocation-kind tag.

`workspace.py:_layout_regions` aligns individual region offsets to their declarations and rounds the final size to16bytes. Data regions are128-aligned; counters/metadata usually16. Making the total allocation size a multiple32 does **not** align the returned base. Likewise, padding the total says nothing about inner row strides.

Follow-up allocator audit inspected the exact published NVSHMEM4Py0.3.1 cu13/cp312 x86_64 wheel in memory. Wheel filename is`nvshmem4py_cu13-0.3.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_34_x86_64.whl`, size3,118,281bytes, SHA256`51d38cae4ee0544815150f40005c0e71ea44aef2ad926f3b6492341063c64e73`, [PyPI metadata](https://pypi.org/pypi/nvshmem4py-cu13/0.3.1/json). It is the matching version/ABI package, not a byte-for-byte comparison with the installed devbox files.

- `nvshmem/core/interop/torch.py:67` has signature`tensor(shape,dtype=float32,release=False,morder="C",except_on_del=True)`; there is no alignment argument. At96 it calls`buffer(get_size(...))`, then DLPack and zero-offset dtype/shape views.
- `nvshmem/core/memory.py:57,91` has no alignment parameter either and calls`resource.allocate(size,...)`.
- `nvshmem/core/nvshmem_types.py:298,316` allocates via`bindings.malloc(size)` and registers the exact returned pointer as the allocation owner.
- `interop/torch.py:61,204-221` frees by looking up the exact tensor data pointer. An aligned interior slice from an overallocated tensor would not be found by`free_tensor` unless the original allocation owner is separately retained and freed. Such a workaround adds lifetime complexity and is unnecessary here.

The native allocator has a stronger implementation guarantee in the recorded runtime version. At NVIDIA NVSHMEM tag`v3.6.5-0`, commit`6e53a40d9db16df170b3b0057e94c340d72f77eb`, [custom_malloc.h:18](https://github.com/NVIDIA/nvshmem/blob/6e53a40d9db16df170b3b0057e94c340d72f77eb/src/include/internal/host/custom_malloc.h#L18) defines`NVSHMEMI_MALLOC_ALIGNMENT=512`. [custom_malloc.cpp:74-84](https://github.com/NVIDIA/nvshmem/blob/6e53a40d9db16df170b3b0057e94c340d72f77eb/src/host/mem/custom_malloc.cpp#L74) aligns the initial heap cursor; at131-149 it rounds each allocation to that granularity before splitting free chunks. [mem_heap.cpp:385-394,1805-1806](https://github.com/NVIDIA/nvshmem/blob/6e53a40d9db16df170b3b0057e94c340d72f77eb/src/host/mem/mem_heap.cpp#L385) uses this allocator for static and dynamic heaps and routes the ordinary malloc request through it. Consequently normal allocations in this inspected native implementation already exceed32-byte alignment.

The [public memory-management API](https://docs.nvidia.com/nvshmem/api/latest/gen/api/memory.html) describes malloc as suitably aligned for object types and offers`nvshmem_align(alignment,size)` for an explicit request. The low-level Python binding exposes`align` (for example [v3.8.0-0 binding:481](https://github.com/NVIDIA/nvshmem/blob/270759e5481b16ef5a71930e1d9b8df184cd7072/nvshmem4py/nvshmem/bindings/nvshmem.pyx#L481)), but it is not integrated into the tensor/MemoryResource allocation interface. Do not call that raw pointer API and pass the result to`free_tensor` without owning the missing resource/tracker lifecycle.

**Recommended implementation:** preserve the normal allocator/free path and enforce actual32-byte alignment at the W4A16 allocation boundary, before emitting a stronger CuTe assumption. This makes the desired contract explicit and fails closed on an unsupported allocator/runtime; it neither falls back to128-bit instructions nor requires a new allocator implementation. Live qualification should still record actual local and mapped peer addresses because the source audit is bounded to the referenced library implementation.

The frontend should annotate each tensor according to its validated operation. Avoid a blanket32-byte default for FP32 alpha/norm scalars, dynamically sliced rows, or top-k rows whose stride is not divisible by32. All actual256-bit data accesses must satisfy the stronger contract and reject invalid inputs; natural scalar accesses remain valid scalar operations.

## Measurement and retention gates

1. Baseline exact current PR head; candidate payload256 with truthful contract. Preserve raw before/after outputs, fresh AUTO tactic choices, source/runtime hashes, cold-L2 graph-CUPTI rank-MAX samples and all per-shape negatives using the established methodology.
2. Inspect actual selected SM103a PTX/SASS for native256 **loads and stores** in combine, not just already256 epilogue stores. Compare instruction counts over equal output payload; a16-element worker performs twice the arithmetic of an8-element worker. Check register/local spill changes and all relevant compiled variants.
3. Validate bit-exact finite outputs, K8 and supported non-K8 values, partial/zero live rows, direct/reused dispatch return tactics, normalized/no-normalization mode, graph replay, offset-output rejection, and malformed-layout rejection.
4. If retained, stack score-prefetch256 as the next small candidate, then consider strict input256 separately. Each new decision compares with the previous retained performance, not the original control.
5. Treat4K/8K/16K as **global** token counts for the current primary EP4/H6144 contract, with EP8 and decode guards. Historical EP8/H7168 measurements are leads rather than current retention evidence.

Native256 global operations and their natural32-byte alignment requirement are documented by NVIDIA's [PTX `ld` instruction](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-ld) and [address operands](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#addresses-as-operands). A256-bit operation reduces instruction count, not bytes moved; it can reduce small-shape parallelism and increase per-worker registers. The final retention decision must follow the measured current candidate.
