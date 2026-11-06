# Packed half-output FC2 TMEM transpose

Current independent unstaged source: `flashinfer-fc2-packed-transpose-r2-20261026`, based on committed final guard `7f4e1703`. The frozen remote R4 namespace is `fc2-packed-transpose-r4`. Only the additional Blackwell `utils.py` delta is under experiment. Frozen control `quant-tail-guard` is byte-identical to the committed final-guard tree.

Current candidate patch SHA256: `a298309c6a0043e120a42d6a0d003d90498b4ceef917082bed73da42924d31b6`. `candidate.patch` adds 64 lines, with no public flag, input-format/model/tile dispatch, stage/PDL/scheduler change, or FC1 arithmetic change. Earlier representations and helper retries are preserved separately in versioned receipts; they are not the timed candidate.

## Mechanism

The fallback FC2 epilogue currently loads top and bottom sixteen-channel fragments, transposes each FP32 fragment separately into lane=token ownership, multiplies its rounded scale, converts to BF16/FP16, and stores. The candidate preserves the same FP32 multiply and final conversion, packs each native top/bottom half-output pair into one 32-bit word, reuses the existing TMEM transpose once, then deinterleaves the two sixteen-channel vectors in registers. Existing converted-output stores are shared. The bulk epilogue stays unchanged.

The source precedent is SM100 MegaMoE `moe_nvfp4_swapab/epilogue_refactor.py:2685`, `fc2_stg_post_f2fp_reorder`: each transposed 32-bit slot carries BF16x2. Our native token coordinate is `2*i + (lane//2)%2`, and channel is `8*(lane%2)+lane//4`. Both top/bottom values share the same token; per-token/fused-route scales are shuffled from the already rounded metadata. Uniform scales compile without these shuffles. Invalid output lanes remain guarded and all lanes participate in transpose/shuffle instructions.

This is different from rejected native-Ld16x256/MOVM and native narrow-bulk variants. It does not change weight layout, move FC1 quantization reductions, add SMEM staging, or revisit rejected gated per-token single-transpose activation.

## Validation status

`prove_layout.py` passes 67,584 symbolic operation-tree comparisons across BF16/FP16, uniform/per-token scales, and all 33 live-token counts. Static Ruff, Python compilation, and diff checks pass. GPU6 completed synthetic source-paired output-byte checks followed by the existing public changing-route chain adapted only in task-local helpers. No upstream tests/reference changes.

The synthetic helper initially omitted an explicit 32-byte output alignment annotation; unchanged control compilation caught it. The corrected helper's ad hoc PyTorch formula differs from control by an output ULP for some metadata conversions. This formula is recorded only as a diagnostic, not a new numerical reference: exact candidate/control output bytes are authoritative for the ownership reorder. Failed helper attempts and exact staged helper versions remain in launch receipts/logs. Candidate source has not changed during these retries.

The R4 codegen gate establishes a real TMEM-instruction reduction without resource regression. Bounded fixed-native CAAC timing follows below. Native C++ artifacts are shared through the verified persistent cache helper; CuTe DSL namespaces remain source-private. Current SDK `cute.compile` forces no-cache, so an absent disk cache is not evidence of missing native cache reuse.

## R4 gate and code generation

The current candidate is `flashinfer-fc2-packed-transpose-r2-20261026` at committed final guard `7f4e1703`, with only the packed-output change unstaged. Remote namespace is `fc2-packed-transpose-r4`. R1/R2 codegen exposed explicit dead local stores from a mixed-element RMEM recast, despite exact outputs; neither was timed. R3 converter-helper representation was staged but never GPU-launched. The final form uses the SDK's documented `TensorSSA.bitcast()` on values, preserving one element type per register allocation and the original vector conversion.

R4 passes29 synthetic cases/source and32 full public-chain graph replays/source across NVFP4 standard/per-token, MXFP8 and MXFP4x8, both PDL states,1/2CTA, inline/overlap, and static/CLC. The chain uses1025tokens so both phase schedulers are actually admitted where requested. All output/input/route/weight hashes match sources exactly; empty and reactivated replays pass. The additional scalar PyTorch estimate remains a recorded non-reference diagnostic.

`r4-codegen-summary.json` proves zero stack or local allocation/operations in16 core variants/source, unchanged SMEM/TMEM/stage/commit accounting, and byte-identical FC1 SASS in all8 variants. FC2 examples (PDL on):

| Format/geometry | Registers old/new | LDTM old/new | STTM old/new |
|---|---:|---:|---:|
| NVFP4 N16 M128 |106/72|12/7|6/3|
| Per-token NVFP4 N32 M256 CLC |112/80|12/7|6/3|
| MXFP8 N64 M128 CLC |107/71|24/14|12/6|
| MXFP4x8 N16 M256 |106/76|12/7|6/3|

Static SASS instruction-site counts also decrease for every FC2 variant, despite register deinterleave PRMTs and per-token scale SHFLs. The direct numeric conversions remain round-to-nearest; no new PTX helper or format-specific conversion branch was needed. Native output stores remain256bit where previously supported.

Fixed-current-tactic CAAC is authorized for all3models at tokens32/64/128/4096, with standard/per-token NVFP4 and both MX modes, initial NV activation quantization enabled. The unchanged W4A16 arm is executed by the public script's `cutedsl` selector but excluded from D retention. Four source-private processes per family run control/candidate/candidate/control, preserving10warmup/100cold-L2 CUDA-graph CUPTI samples and exact routing identities. Current final-guard NV and B+C MX AUTO caches are copied into immutable per-case snapshots; cache misses are errors. No full AUTO or benchmark-policy changes are part of this candidate screen.

## R4 fixed-current-native timing result

All six family runs completed with source hashes, immutable cached tactics, route identities, and 100 raw timing samples per arm verified. Each cell is median(control arm medians) / median(candidate arm medians), using CAAC order. This is fixed-current-native evidence, not a new full AUTO search.

| Model | W4A4 | Per-token NVFP4 | MXFP4x8 | MXFP8 |
|---|---:|---:|---:|---:|
| v3 | 0.998711x | 0.999900x | 0.998918x | 0.998717x |
| v41-flash | 0.999250x | 0.999097x | 0.999676x | 0.999834x |
| kimi-k3 | 0.999156x | 1.001241x | 0.999477x | 0.999292x |

These are geometric means over tokens 32, 64, 128, and 4096. Across the 48 affected cells the geometric mean is 0.999439x; this is neutral end-to-end, not a demonstrated performance win. Largest affected loss is V3 W4A4 token32 at0.996144x (101.409→101.801µs); largest gain is K3 per-token token4096 at1.006106x. Small paired losses recur at standard-NV token32 and mixed token4096, so they should not be hidden in a perf-win claim. The unchanged W4A16 selector is excluded from retention and has an unrelated K3 token4096 timing outlier.

Under the user’s updated criterion, the verified instruction and register reductions can justify retention if these tiny shifts are acceptable. No new policy branch or public knob is introduced. Final retention belongs to the parent task. All source copies remain unstaged; GPU0/1/3 were verified idle and released after this campaign.

Receipts and raw samples: `screens/`, `timing-summary.json`, `r4-codegen-summary.json`, and `r4-validation/`. The direct collection helper validates every raw median against the benchmark result, and never changes source, tactics, or timing policy.

## T16384 boundary and reverse-order follow-up

The additional all-model/all-format CAAC T16384 sweep completed. Source, saved native tactics, route identity and raw100-sample arm results passed the same checks. No source change or new native retune occurred.

| Model | W4A4 | Per-token NVFP4 | MXFP4x8 | MXFP8 |
|---|---:|---:|---:|---:|
| v3 | 0.999285x | 1.004014x | 0.993251x | 0.997587x |
| v41-flash | 1.004422x | 1.000581x | 1.000695x | 1.006698x |
| kimi-k3 | 0.993151x | 1.007897x | 0.977328x | 0.991417x |

Initial K3 mixed reported0.977328x, but controls drifted1069.302→1113.702µs and candidates1097.334→1136.311µs. A separate reverse ACCA repeat on the same GPU, source, data and immutable cache returned **0.998590x** for mixed (1099.054→1100.606µs) and **1.009123x** for MXFP8 (1316.688→1304.784µs). The >1% loss was not reproduced, so no NCU follow-up was launched. Both complete results are retained; the initial number is not silently replaced.

Pooled four-arm medians are diagnostic only; they do not create a new public benchmark row:
- CuteDSL MXFP8: 0.989669x.
- CuteDSL MXFP4x8: 0.997206x.

Evidence is `large-screens/`, `large-timing-summary.json`, `large-repeat-screens/`, `large-repeat-timing-summary.json`, and `large-repeat-pooled.json`. The unchanged W4A16 arm is excluded; V41 W4A16 also had a timing outlier unrelated to this source delta. GPU0 was released after the repeat. Native full-campaign retuning and final composition validation remain parent-owned; these fixed-tactic results alone are not a final retention claim.

Separate CLC diagnostics live in `nsys-k3-clc-20261027/` and `k3-clc-scores-20261027/`. They use the published and all-CLC sources, not R4; they must not be mixed with the packed-output causal screen.

## Retention decision

Parent retained R4 as an instruction/register simplification after source review, exact gates, spill-free codegen and the reverse-order large-prefill check. Do not claim an end-to-end speedup. `retention-receipt.json` records source identity, gates, resource changes, both large campaigns and limits. Parent owns composed-source tests, final native AUTO and separate commits. No source was changed during measurement.
