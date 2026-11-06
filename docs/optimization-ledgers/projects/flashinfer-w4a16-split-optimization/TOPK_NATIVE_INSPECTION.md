# Minimal top-k native inspection

Candidate is the three-line top-k constexpr change approved by root (source8ad313cb). Use the same installed CUDA/DSL/ptxas and target architecture for BEFORE and AFTER. This reviewer has performed no compilation, GPU action or remote operation.

Executor-reported attempt `83096` failed during native artifact export: the requested DSL output/cache subdirectories did not exist, and automatic SASS export tried to open a missing cubin. Installed DSL 4.7.1 accepted the KEEP tokens; this was an export failure, not a numerical result. The corrected recipe below creates both directories, requests only PTX/cubin, and uses standalone `cuobjdump` for SASS. Corrected baseline and candidate captures are complete; [the actual native comparison](NATIVE_COMPARISON.md) records the results. Preserve the original failed attempt separately.

## Reuse the existing export mechanism

The prior split capture already ran an existing test with `CUTE_DSL_KEEP=ptx` and `CUTE_DSL_DUMP_DIR`:
`/Users/ziangli/playground/projects/flashinfer-w4a16/logs/w4a16_merged_tma_ir_ptx_20260722_170744/run.log:1–6`.

The historical Mega helper set export options **before importing CuTe**, with line info, a separate dump directory and a separate cache directory:
`/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/candidates/w4a16_fc2_per_k_readiness/validation/native_v2/capture.py:88–99`.
Use the corrected export settings below for this installed stack. Do not inherit Mega's fake tensor/frontend/envelope/96-register options or its profiler wrapper. Split `_get_compiled_kernel` currently supplies no extra `cute.compile` options; retain that.

```sh
mkdir -p "${capture_dir}/dsl" "${capture_dir}/cache"
CUTE_DSL_KEEP=ptx,cubin \
CUTE_DSL_LINEINFO=1 \
CUTE_DSL_DUMP_DIR="${capture_dir}/dsl" \
CUTE_DSL_CACHE_DIR="${capture_dir}/cache" \
"$project/.venv/bin/python" "$project/capture_split_topk.py" \
  --repo "$project/flashinfer" --case fused2 \
  --output "${capture_dir}/result.json"
```

Use a fresh process/directory for each source and specialization; run `fused3` and `ordinary0` separately with the same helper. Select the actual target architecture from the executor's environment; do not transplant a target from historical hardware. The checked-in older CUTLASS `base_dsl/env_manager.py:357–365` additionally documents `CUTE_DSL_KEEP_PTX=1` / `CUTE_DSL_KEEP_CUBIN=1`; the installed package is authoritative if its export spelling differs. No need for a new cache framework or a profiler run.

## Smallest compile-only adaptation

Call the real `flashinfer.fused_moe.cute_dsl.blackwell.moe_w4a16._get_compiled_kernel` and retain its returned object **without calling it**. That function already invokes the actual wrapper and `cute.compile` (lines94–195), so no monkeypatch or replacement kernel is necessary. Copy its typed `make_ptr` descriptors directly from `_run_grouped_gemm:238–304`; compile-only null-address gmem pointers suffice as descriptors and must never be launched.

Hold one GEMM2 tactic and shapes fixed, for example existing C1 `(128,64,256)/(1,1)/M-major`, M256/K512/N256, group_count8, actual_tokens65; activation_typeNone, enable_pdlFalse, use_clc_schedulerFalse. Obtain the normal max_active_clusters using the existing helper. Keep the same values for both sources. If the executor already has a real prepared test fixture, passing its pointers is equally direct.

Compile only these three cases per source:

| Case | use_fused_finalize | top_k passed to _get_compiled_kernel | Extra pointer descriptors |
| --- | --- | --- | --- |
| fused2 | True | 2 | Int32 permuted→expanded, FP32 scale table |
| fused3 | True | 3 | same types |
| ordinary0 | False | 0 | both None; num_tokens0 as the real launcher supplies |

BEFORE and AFTER take identical Python arguments at `_get_compiled_kernel`; its return ABI differs intentionally because the wrapper's top_k becomes compile-time. The direct compile call never invokes either ABI. This is the shortest no-launch path; alternatively simply enable dumps on already planned boundary-oracle tests, without adding another execution.

## Artifacts and admission checks

Save emitted `Sm100W4A16GroupedGemmKernel` PTX/cubin plus:

```sh
cuobjdump --dump-resource-usage "$cubin" > resources.txt
cuobjdump --dump-sass "$cubin" > sass.txt
nvdisasm --print-line-info "$cubin" > sass-lineinfo.txt
```

1. **Fused GPU body:** follow source-correlated quotient/remainder at `moe_w4a16_kernel.py:2161–2162` and quotient at2210. Actual baseline PTX has two `div.s32` instructions (lines2675/2958), despite the wrapper's Int64 annotation: the scale descriptor's runtime top-k extent is converted to32 bits at2541. The scale remainder is recovered by multiply/subtract at2676/2682, not a separate top-k `rem.s32`. SASS uses a loaded divisor and two reciprocal/refinement sequences. AFTER is expected to use constant division sequences (shift/mask for2; compiler constant multiply/shift/correction for3), but only its fetched dumps can establish that. Do not require every kernel division to disappear: dynamic work-shape/scheduler arithmetic is unrelated. Inspect both scale lookup and output scatter; check FP32/BF16 arithmetic and stores remain intact.
2. **GPU parameters:** fused scale-table inner extent/stride is static after specialization; record which former runtime descriptor values disappear. Host wrapper argument removal alone is not proof that GPU divisions disappeared.
3. **ordinary0 control:** compare actual GPU instructions, PCs, opcodes, both encoded words/scheduling and kernel parameter/resource metadata. Ignore symbol mangling and source line-number shifts; do not demand whole cubin byte identity (debug/name sections can differ). Top-k0 has no scale tensor and no fused finalize branch, so its GPU body should remain identical. Preserve its intentional host ABI difference separately.
4. **Resources:** compare register/local/stack/shared bytes, block and cluster sizes, raw/decoded/ACC/C stages, and output store widths. This change should not alter them, but only the actual artifacts establish it. Source alignment/top-k arithmetic reasoning is not a numerical pass.

The already extended six-geometry test product (top_k2/3 × fused-finalizeFalse/True) remains the runtime/cache/numerical check. Native dumping should be attached to that existing work when convenient; no second test matrix or result-reader layer is needed.
