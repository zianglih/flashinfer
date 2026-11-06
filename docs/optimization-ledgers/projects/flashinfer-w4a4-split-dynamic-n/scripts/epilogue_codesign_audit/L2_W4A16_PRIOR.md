# W4A16 cache-policy reference and closed experiments

CPU-only source/ledger audit, 2026-10-25; no GPU work or source changes. Scope is split W4A16, MegaMoE references, and prior experiments. The separate current blockscaled whole-chain inventory belongs to the parent reviewer.

## Policy meanings

Eviction priority, allocation/cache level, and prefetch are different controls. Semantics are pinned to the installed-toolchain-compatible [CUDA13.2.2 / PTX ISA9.2 cache operators](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#cache-operators) and [eviction-priority hints](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#cache-eviction-priority-hints), checked directly on2026-10-25 (sections9.7.9.1–2), rather than newer PTX9.4 syntax:

- `evict_first`/`evict_last`: prioritize eviction of cached data. Neither means bypass/no allocation, nor guarantees persistence.
- Ordinary-load `.ca` allocates at all cache levels; `.cg` bypasses L1 but still caches in L2. Streaming `.cs` allocates with evict-first priority. Ordinary stores have separate `.wb`/`.cg`/`.cs` controls. These are performance hints, not synchronization.
- `no_allocate` is distinct from `evict_first`; instruction/cache-level support must be checked rather than transferring a modifier from ordinary loads to TMA by name.
- Descriptor prefetch warms TMA descriptor access. Data prefetch requests future payload cache lines/tiles. Neither replaces the actual operand load or its completion barrier.

Source-level absence of a hint below means **no explicit policy in that source**, not a verified emitted instruction or measured residency. No new PTX/SASS was generated in this audit.

## Actual split W4A16

Main reference: `flashinfer/` HEAD `aab93f854054de834447bdd8985b8bbd653fb3c8`. Paths in this section are relative to that repository.

|Path / line|Operation|Explicit policy|
|---|---|---|
|`flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:1449–1457`|B: routed BF16 activations, TMA G2S|`EVICT_LAST`, literal `0x14F0000000000000`|
|same`:1536–1544`|A: packed NVFP4 weights, TMA G2S|`EVICT_FIRST`, literal `0x12F0000000000000`|
|same`:1546–1554`|S: E4M3 weight scales, TMA G2S|No `cache_policy` argument|
|same`:905–910`|A/B/S/C descriptor prefetch|`cpasync.prefetch_descriptor`, issued by first epilogue warp|
|same`:2124–2134,2302–2306`|Gated FC1 / full-subtile output TMA stores|No `cache_policy` argument|
|same`:2335–2340`|Predicated SIMT output tail store|No explicit cache modifier at call site|
|same`:2239–2241` and`:2200–2204`|Finalize mapping/scale loads|Ordinary indexing, no explicit cache modifier|
|`flashinfer/fused_moe/cute_dsl/blackwell/utils.py:135–144`|Optional fused BF16 combine|`cp.reduce.async.bulk.global.shared::cta.bulk_group.add.noftz.bf16`, no cache-policy operand|

The BF16 activation path has no activation SF tensor. Weight-S TMA is a separate operation despite sharing the weight load pipeline. Do not describe the packed-weight EVICT_FIRST hint as also covering scales.

The wrapper explicitly materializes routed BF16 rows through native `moe_permute` (`blackwell/moe_w4a16.py:441–455`). Native `csrc/nv_internal/tensorrt_llm/kernels/cuteDslKernels/moeUtils.cu:32,91–95` uses `uint4` source/destination assignments without explicit cache intrinsics; metadata loads at82–89 are also ordinary accesses. Source vector width does not establish a special allocation policy.

Standalone combine is the shared CuTe implementation (`blackwell/moe_w4a16.py:34,501–509`): `blackwell/moe_finalize.py:127–128,156,173` uses the same128-bit `CopyUniversalOp` atom for expert-output reads and final-output writes, with no explicit cache hint. Mapping/scales are ordinary loads at133–138. The older Triton `.cg` experiment below is not this current implementation.

The separate W4A16 checkout at `../flashinfer-w4a16/flashinfer`, HEAD `adcf4b123caaeda1fe589a722462c8beb75d7176`, has the same four descriptor-prefetch calls and two explicit cache-policy assignments at `moe_w4a16_kernel.py:872–875,1425,1512`; line numbers differ due to later unrelated integration.

## MegaMoE comparison

At the same aab checkout, actual BF16-activation/NVFP4-weight MegaMoE uses the same operand tiers in `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py`: packed-weight A TMA FIRST at955–961, weight-SFA TMA with no explicit policy at963–969, and BF16 activation B TMA LAST at1029–1036. There is no activation scale operand. These are the only two `cache_policy` occurrences in that BF16_NVFP4 directory, which has no `prefetch_descriptor` call. Do not infer descriptor prefetch from methods named metadata `prefetch`.

Mega transport has an additional, explicit policy distinction. Abbreviate `M = flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4`, `V = flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src`:

- `M/token_comm.py:12–15` inherits `TokenInPullTokenBackPush`. Peer activation pull uses `tma_load_1d_raw` at `V/src/token_comm.py:1182–1192`; its inline PTX explicitly supplies L2 EVICT_FIRST (`V/src/ptx_helpers.py:46–63`). Local FC1 pool stores use `tma_store_1d` at `V/src/token_comm.py:1296–1307`, explicitly L2 EVICT_NORMAL (`V/src/ptx_helpers.py:73–83`).
- Optional dispatch-based FC2 return loads use the same FIRST helper at `V/src/token_comm.py:1605–1610`; the non-reducing peer store uses NORMAL at1622–1626. The reduce-top-k branch instead invokes the reduction helper at1615–1620. This is source policy, not proof of a particular peer-memory caching effect.
- Initial BF16 staging uses128-bit `CopyUniversalOp` without explicit hints (`M/token_comm.py:57–70`); FC1 output uses256-bit ordinary copies (`M/epilogue.py:612–614,723–738`); FC2 direct output (`M/tmem_epilogue.py:653–692`) and top-k payload loads/stores (`M/topk_reduce.py:70–82,110–118`) also have no explicit hint.
- Metadata methods called `prefetch` load routing weights/pointers into registers (`M/epilogue.py:617–630`, `M/tmem_epilogue.py:409–465`); they are neither TMA descriptor prefetch nor a global payload-prefetch instruction.

The separate SM100 NVFP4 reference `V/moe_nvfp4_swapab/mega_reference.py:980–985` prefetches A/B/SFA/SFB/C descriptors. Its TMA operand copies at1310–1336 have no explicit `cache_policy`. The NVFP4 `kernel_fc12.py` mainloop instead issues weight/SFA copies at1732–1747 and activation/SFB copies at1962–1977 without an explicit cache policy, and has no descriptor-prefetch call. Do not attribute the reference's descriptor prefetch to this mainloop or to the BF16_NVFP4 implementation.

## Closed or retained prior axes

Historical W4A16 ledger: `../flashinfer-w4a16/w4a16_optimization_experiments.md`. Numbers below are that ledger's reported measurements, not fresh comparisons against aab.

|Ledger lines|Experiment / disposition|
|---|---|
|312–337|Activation B EVICT_LAST retained; EP8/TP8 geomeans1.0107x/1.0114x.|
|1048–1085|Packed-weight A EVICT_FIRST retained; two EP8 sweeps1.0215x/1.0230x. Scale policy unchanged.|
|607–624;1087–1096|Scale LAST and FIRST separately rejected; FIRST on top of weight-FIRST lost about1.8–2.2% at EP8 T128/256.|
|654–667|Weight LAST rejected: small geomean gain with larger-token regressions.|
|731–746|FC1 output TMA-store LAST rejected: EP8 neutral, TP8 regression. This already tests a producer-side retention idea.|
|3820–3834|Old Triton combine BF16 row-load `.cg` rejected: EP8 T4096 0.427920→0.475072ms. This tests L1 bypass, not L2 no-allocation, and is not the current CuTe combine.|
|4284–4324|FC2 weights+scales initial and rolling bulk-TMA prefetch rejected; EP8/TP8 geomeans0.9945x/0.9925x.|
|4326–4357|FC2 weight-only rolling `cute.prefetch`, one pipeline depth ahead, rejected; EP8 T4096 about3% slower.|
|4395–4444|FC2 direct `prefetch.global.L2` weight-line lookahead rejected; EP8 geomean0.9911x. This added line-address/issue work, not descriptor prefetch or a completion-tracked operand stage.|

Current-project historical controls also matter:

- `scripts/pipeline_cache_experiment/README.md:3,18–22,26–41,95`: frozen7829fc00 Gather4 epoch, T16384 M256/N256. A-FIRST, B-LAST, their combination, and descriptor prefetch did not improve the large-token target; T128 full-chain differences were at most0.6%. This is not evidence that every policy on current regular-TMA decode is closed.
- `scripts/sf_cache_experiment/README.md:3–17`: SFB4-byte `cp.async.ca` plus L2 prefetch64/128/256B, and no-prefetch inline-PTX control, were neutral/slower on the same old large-token geometry. These are extra fetch-size hints, not eviction/allocation changes.
- `scripts/cache13_experiment/README.md:7–17`: later13ca retest separated geometry and retained only weight A-FIRST for one-CTA/eight-K-step kernels; B-LAST lacked sufficient whole-chain evidence, and NB2 A-FIRST regressed. The retention is recorded at `OPTIMIZATION_LEDGER_2026-10-24.md:185–187`. Thus even the prior record already disproves a blanket interpretation of the earlier negative cache screen.

The audited evidence does not establish a matched current-aab whole-chain experiment coordinating ordinary metadata/preparation/finalizer allocation and eviction with TMA operand priorities. Any such proposal must name which operation/level changes; merely reapplying the same weight hint or broad payload prefetch repeats a closed mechanism.

## Source identities

|File|SHA256|
|---|---|
|aab `blackwell/moe_w4a16_kernel.py`|`2fdadcdaee4a1819b050815fddab44017b31e4649f5146a99278cddcefa536cf`|
|aab `blackwell/moe_w4a16.py`|`09771708151bfda13c7654a79d7143bb16851555d1b5e8d6dfb3595ad6f6658e`|
|aab MegaMoE `bf16_nvfp4/megamoe_kernel.py`|`376110139f7197455d768a7af0681621a5a0afeaa06dfa959359e3768baab277`|
|aab MegaMoE `bf16_nvfp4/token_comm.py`|`b63cdd57842f3b13557ca3375c6bf1c5c8039b3449ad3a0f184a521419515fd5`|
|aab MegaMoE transport `src/token_comm.py`|`1665b19dffbe412b53212ef13d9578f302c0bee73d2ea09f7ddef69c6a6e175b`|
|aab MegaMoE transport `src/ptx_helpers.py`|`958aab5294398299a3c0e11fc093a199685d63f64784ddeef29c607928cbd31b`|
|aab MegaMoE NVFP4 `kernel_fc12.py`|`80d34cd0f662d64e62d26c4be1f779d48655896c3b5a22030b08788440dd9e40`|
|adcf W4A16 kernel|`4a870648549397c4ef8d4db52b4bfe3dde3ff09feed94abd942ea945f3185866`|
|W4A16 optimization ledger|`c8a7b0790d1dd51a9a9a3a1c483370d6ec832fef52ce78acb1c0e9854e832c08`|
