# Gather relay scope audit

**Recommendation:** test one compile-time scope choice inside the existing arrive/wait helpers: ordinary CTA release/acquire for `cta_group_size == 1`, and the existing cluster publication sequence for two CTAs. Preserve the relay, barrier counts, proxy fence, stage reuse, and all warp ownership. This is a synchronization-scope correction, not a new tactic or runtime policy. No source change, compilation, or GPU work was performed for this audit.

## Ordering contract

The retained kernel launches clusters exactly `(cta_group_size, 1, 1)` and rejects mismatched cluster geometry (`moe_swap_ab_kernel.py:2056,2501`). Thus a one-CTA MMA group has no remote participant. Each local gather stage still combines 128 SF `cp.async` completions with one payload-TMA transaction arrival. Its relay waits for that local stage, crosses the async/shared proxy, then publishes to the MMA warp. The final gather barrier counts one arrival per CTA (`:2752–2760,3039–3068`); only CTA0's MMA consumes it (`:3069,3252`).

For group1, a local release arrive and local acquire wait connect that same-CTA handoff. For group2, both CTAs publish their completed local SMEM to CTA0 before a two-CTA MMA/SF copy, so retain the current mapped leader address and cluster release/acquire. Do not copy CUTLASS's historical CTA default onto that remote handoff. Do not remove the caller's async proxy fence: simplifying the generic publication scope does not remove the mixed TMA/cp.async proxy dependency.

PTX distinguishes synchronization scope from the barrier's storage space. Local arrive defaults to release/CTA, and a successful local wait defaults to acquire/CTA. The restricted shared-memory release/acquire fences require cluster scope. The existing group2 sequence matches NVIDIA's explicit shared publication example. [PTX mbarrier arrive/wait](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-mbarrier-arrive), [restricted fences](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-membar).

## Reference implementations

- Project-local CUTLASS `91843b71d90737e0a9b86f7d9df213cff5a3526f`: `python/CuTeDSL/cutlass/pipeline/sm100.py:538–559` uses no producer destination for one-CTA `PipelineAsyncUmma` and a leader destination for two CTAs. `pipeline/helpers.py:403–418` routes the former through local `cute.arch.mbarrier_arrive`; `cute/arch/mbar.py:286–315,414–462` gives the ordinary local arrive/wait primitives. Its explicit comment warns that the historical CTA-scope default for remote arrivals is insufficient for formal DSMEM data publication; it is not a reason to weaken group2 here. The local reference checkout is clean.
- Captured CuTe DSL4.8 runtime source independently has the same local arrive/wait policy: `w4a16-perf-20261027/sync/pipeline-implementation.txt:150–228`; runtime pipeline helper hash `7c68144b…` is saved in `optimization-20261027/warp-specialization/sdk-pipeline-read.txt`.
- Rubin's `blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1449–1487,2341–2400` explicitly bridges per-CTA cp.async completion to a two-CTA consumer with a relay. Its one-CTA cp.async path uses local completion. This validates the scope distinction, but its different pipeline topology is not a reason to add a bypass here. Its TMA path and MegaMoE's `create_{ab,weight,token}_pipeline` (`sm100/.../block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:684–748`) use direct `PipelineTmaUmma`; they do not contain our combined cp.async-SF/TMA-payload relay and cannot justify removing it.

## Retained executable evidence

`audit.py` verifies the saved control kernel bytes against pushed `f63e9485`, all captured SASS/PTX hashes, and the 23 FC1 compilations (9 one-CTA, 14 two-CTA). The older source HEAD label in the frozen receipt is not used as the equivalence claim: kernel SHA is exactly `0be06569fda8e0aa88301052f6623b175ccf3577314c6b07d16231a515194837`. All instances have zero stack/local storage. Full identities and counts are in `retained-codegen.json`.

| Retained instance | CTA group | N / stage K | Explicit cluster release/acquire sites | Elected extra MEMBAR / ASYNC fence sites | Leader-address remap |
|---|---:|---:|---:|---:|---|
| `000-fc1`, FP4/FP4 | 1 | 128 /512 | 1 /1 | 1 /1 | One PRMT in stage loop |
| `008-fc1`, FP8/FP8 | 1 | 16 /256 | 1 /1 | 1 /1 | One PRMT in stage loop |
| `028-fc1`, FP4/FP4 | 1 | 256 /256 | 2 /2 | 2 /2 | Two PRMT sites in unrolled stages |
| `032-fc1`, FP8/FP4 | 1 | 256 /128 | 4 /4 | 4 /4 | Four UPRMT sites hoisted before stage loop |
| `004-fc1`, FP8/FP4 | 2 | 128 /128 | 2 /2 | 2 /2 | Two PRMT sites; retain remote publication |

For `000-fc1.sass`, relay local completion is at `0xdd0`. The existing caller's proxy fence lowers to `MEMBAR.ALL.CTA` at `0xe40` and `FENCE.VIEW.ASYNC.S` at `0xe50`. The explicit cluster helper then emits another elected `MEMBAR.ALL.CTA` at `0xe90`, `FENCE.VIEW.ASYNC.S` at `0xea0`, `PRMT` at `0xeb0`, and the necessary arrival at `0xec0`. These three control instructions beyond the arrival are real, not just PTX notation. All 23 FC1 instances have one such elected fence pair per explicit release site. Mapping can be hoisted, so do not count every static mapping as per-stage dynamic overhead.

The consumer's restricted cluster acquire adds no separately visible MEMBAR/FENCE opcode in the inspected MMA regions. Keep its semantic role in group2; do not promise a consumer instruction saving. A nearby ordinary CUTLASS publication in the same executable uses a proxy fence plus default release arrive with only one MEMBAR/ASYNC-fence pair (`000-fc1.ptx:255–258`, SASS `0xb50–0xb70`). This is encouraging evidence for avoiding the duplicated pair, but is not a substitute for compiling the proposed helper.

## Bounded follow-up, if approved

Pass existing compile-time `cta_group_size` into both helpers. Select standard `cute.arch.mbarrier_arrive` / `mbarrier_wait` for1; keep current inline assembly for2. Use explicit1/2 cases rather than a silent fallback. No new exposed optimization flag, relay bypass, wait removal, role branch, or changed transaction accounting. First inspect paired generated code for N16/N128/N256, both CTA groups, all four formats, and CLC/static. Require unchanged group2/FC2 code and no new local storage. Only then use existing exact cases and a small fixed-tactic stock-clock CUPTI C-A-A-C screen. There is no measured speedup claim from this read-only audit.
