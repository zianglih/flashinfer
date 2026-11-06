# Retention compile and AUTO coverage notes

CPU-only audit of `flashinfer/` HEAD `aab93f854054de834447bdd8985b8bbd653fb3c8`, 2026-10-25. No CUDA/Torch/CuTe imports, compilation, GPU work, or production edits. Paths below are relative to that repository unless stated otherwise.

## Tactic and specialization counts

`flashinfer/fused_moe/cute_dsl/tuner.py:80–128` produces this Blackwell menu; all raster flags are false:

|Route N|FC1 logical M choices|FC2 M choices|Joint tactics|Unique FC1|Unique FC2|
|---|---|---|---:|---:|---:|
|16|128|128|1|1|1|
|32|128|128|1|1|1|
|64|128|128|1|1|1|
|128|128,256,512|128,256|6|3|2|
|256|128,256|128,256|4|2|2|
|Total|||13|8|7|

The full joint menu is not13 independent FC1 kernels plus13 FC2 kernels: pairs reuse phase specializations. Logical M512 FC1 uses two physical M256 channel tiles inside the same two-CTA group, not four CTAs (`blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:248–273`). N16 and N32 remain separate specializations despite both allocating at least32 physical N rows.

Pure AST execution extracted only the four tactic builders, route-capacity helpers, and `is_valid_dtypes`/`can_implement` methods. Numeric dtype identities were represented by inert Python types; no GPU package was imported. Capability adapters were the actual FC1/FC2 source methods. For D7168, I2048,32 local experts, top-k8, gated FC1 and unfused BF16 FC2, every tactic passes for all three native formats:

|Format|Activation / weight|SF|Joint / FC1 / FC2|
|---|---|---|---|
|NVFP4|E2M1 / E2M1|E4M3,16|13 /8 /7|
|MXFP8|E4M3 / E4M3|UE8M0,32|13 /8 /7|
|MXFP4×MXFP8|E4M3 / E2M1|UE8M0,32|13 /8 /7|

Checked T=1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384. Core filtering requires positive dimensions, channels divisible by128, K divisible by4×SF-vector length, and routed capacity divisible by route N (`blackwell/...finalize_fusion.py:405–469`). Route allocation supplies the latter by construction (`moe_utils.py:145–174`). This establishes source eligibility, not successful compilation/performance of every tactic.

Native NVFP4 uses `CuteDslFusedMoERunner.get_valid_tactics` (`tuner.py:704–857`). Homogeneous MXFP8 and mixed MXFP4×MXFP8 use the benchmark's separate, dtype-correct `SplitMxfp8Runner` filter (`benchmarks/bench_cute_dsl_mxfp8.py:59–66,123–205`), not the standard packed-FP4 filter.

For one fixed model/device/flags, the three formats therefore require **24 FC1 +21 FC2 =45 distinct GEMM cache keys per source arm**, regardless of the number of token rows timed. Per-token mode, fused finalize, different model dimensions, PDL flags, output/scale dtype, or SM cap can add specializations. Auxiliary kernels are excluded from45.

## Static dimensions and launch

The active Blackwell host cache is `_blockscaled_kernel_cache`, not the later Rubin `_finalize_kernel_cache`. Its key (`blockscaled_contiguous_grouped_gemm_finalize_fusion.py:202–228`) includes device, tile/cluster, operand/output/SF dtypes and SF vector length, optional output-SF/global-normalization flags, routing-scale dtype, channels/K/experts, SM count, top-k, activation/SiLU parameters, per-token flag, fused-finalize flag, and PDL.

Channels, reduction K, and expert count are `cutlass.Constexpr`; routed capacity and token count are runtime `Int64` (`blackwell/...finalize_fusion.py:488–493`). Compile receives all dimensions, but subsequent calls pass only pointers, routes, and T (`host:235–263`). T is absent from the key. Public tile K is256 for FP4×FP4 and128 otherwise (`host:229–234`); physical K derives from dtype/tactic/phase via k_steps4 or8 (`core:255–268`). Changing reduction K recompiles; changing T alone does not recompile a GEMM.

The host passes `num_sms` as the constructor's misleadingly named `max_active_clusters` (`host:201,257`). Launch is `grid=(floor(num_sms/group)*group,1,1)`, `cluster=(group,1,1)`, with `min_blocks_per_mp=1` (`core:838–849`). Thus a148-SM B200 default gives148 CTAs:148 one-CTA clusters or74 two-CTA clusters. It is not148 two-CTA clusters. The later host `get_max_active_clusters` query is Rubin-only after the Blackwell return (`host:815–857`).

`min_blocks_per_mp=1` is a compiler launch-bound input, not a request to increase residency or proof that resources permit only one CTA/SM. Existing control PTX records `.minnctapersm 1` (`../scripts/epilogue_codesign_audit/pdl-codegen-r1/resources-r1/control-fc1-n16.ptx:35`). No resource/launch change is proposed here.

Auxiliary compile cost is not zero: preparation's key includes a capacity-derived grid (`blackwell/moe_prepare.py:250–265`), while combine selects32/128 threads around T8 and vector count above T1024 (`blackwell/moe_finalize.py:240–260`). Hence45 must not be called the total whole-chain compilation count.

## AUTO timing coverage and reuse

**CuTe is not capped at8192 in the current native benchmark.** The wrapper receives `max_num_tokens=n` (`bench_moe_deepseek.py:491`); runner bucket generation is a bare callable (`tuner.py:535–546`) evaluated using actual input T (`autotuner/autotuner.py:4047–4050`). The pure AST bucket generator returns:

```text
T8192:  1,2,4,8,16,32,64,128,256,512,768,1024,1280,1536,1792,
        2048,2560,3072,3584,4096,8192                     (21 buckets)
T16384: the same list plus16384                         (22 buckets)
```

Definitions are in `fused_moe/utils.py:228–275`. With unchanged cache identity, previously tuned buckets are skipped before synthetic-input creation/profiling (`autotuner.py:2776–2811`). The complete22-bucket menu has286 candidate/bucket combinations per format before cache hits/failures, while sharing15 GEMM binaries. This is not a count of actual CUDA launches or timing samples.

The8192 default belongs to TRT-LLM APIs (`fused_moe/core.py:4922,6571`); the native benchmark passes no override (`bench_moe_deepseek.py:767–776,974–979`). Its capped mapper maps T≥8192 to that bucket (`shared/tuning.py:307–308`, `fused_moe/utils.py:284–287`). Preserve this distinction when reporting16K results; do not silently alter the established benchmark method.

The native benchmark prewarms under `_autotune_context` then measures outside it (`bench_moe_deepseek.py:580–584`; MX helper:367–378). Profiling captures the selected path, warms it three times, then profiles (`bench_moe_deepseek.py:313–334`). Non-tuning `choose_one` looks up a winner; graph replay does not rerun Python selection. Between rows, allocator cleanup does not clear tuner or compiled-kernel caches (`bench_moe_deepseek.py:1098–1126`).

AUTO winner keys contain operation/runner identity, bucketed tensor shapes, and extras (`autotuner.py:4134–4161`); persisted keys omit runner hash (`:1352–1389`). Native runner hash/extras do not include the entire tactic catalog or source hash (`tuner.py:654–694`), whereas the MX helper extras include `tuple(all_tactics)` (`bench_cute_dsl_mxfp8.py:149–164`). Source/catalog edits alone therefore do not reliably invalidate existing winner entries. A supplied JSON is loaded even with tuning disabled (`bench_moe_deepseek.py:112–120`); a non-tuning cache miss can return fallback-1 (`autotuner.py:2416`), so `--no-autotune` is not itself proof of winner replay.

Minimal retention plan: one fresh process and separate AUTO bundle per source arm; keep all token rows/formats for that arm in-process to reuse compilation and previously tuned buckets. Preserve model/flags/environment and verify cache-hit/winner coverage before a profiler-only replay. The compile cache, AUTO winner cache, and existing disk JIT artifacts are distinct; none establishes another's validity.

## Source receipt

|File|SHA256|
|---|---|
|`cute_dsl/tuner.py`|`8f165cea7243c2a98ffbc2c7b3d9c9a5d5e2e689e6e8afe99237b9c23120bc2b`|
|shared Blackwell host|`2a8a4a3ad8e927cc8bccc8adf3fc3668e9b7b581eb4eb9d35d1416e21abc2ce0`|
|Blackwell core|`7c0fe69faab5acecafdd3d67a157f016836e149fafdc29942542d44ef4852c66`|
|`bench_moe_deepseek.py`|`b065e2e52b1dd8704b152e9c7e3e477f2a5c4d1e0e4e88b863bf92af7ea8442f`|
|`bench_cute_dsl_mxfp8.py`|`632e8587180b88c2fd867d42a03899c5072b04cdcea0fabc58badfcb883b9b23`|
|`autotuner/autotuner.py`|`0db42ad90d1a3fec6f81509a2c520c1892cea0a433f5dbd7f43468a2a10243ca`|
