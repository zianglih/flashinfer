# PR7290 final validation commands and raw results

Tested head: `83dfef8a656384f5cd10db847602593bb6f9b2c6`. B300, `nvcr.io/nvidia/pytorch:26.05-py3` (CUDA 13.2); full runtime versions and raw results are below.

## Portable repository test commands

Run these from a FlashInfer checkout at the tested head with the recorded dependencies installed and an exclusively assigned GPU. The two pytest command blocks are unchanged from the existing test-command artifact: all 27 exact selectors and 25 API selectors were checked against the actual final-head subprocess receipts, expanding to 33 and 62 tests. The JUnit filenames are output labels, not GPU assignments. No local probe helper is required for these repository tests.

```bash
export FLASHINFER_CUDA_ARCH_LIST=10.3a
export FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1
export FLASHINFER_DIST_AWARE_AUTOTUNE=0
export TRTLLM_ENABLE_PDL=1
export MAX_JOBS=8
export OMP_NUM_THREADS=1
```

```bash
python -m pytest -q --disable-warnings --maxfail=1 \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[True-swiglu-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[True-w4a4-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_geglu_tanh_accuracy[True-w4a4-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[True-gate-clamp-w4a4-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_situ_accuracy[True-gate-and-up-clamp-w4a4-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestExpertParallelism::test_functional_with_ep[8-swap-ab-w4a16]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_cute_dsl_pinned_recipe_matches_env[e4m3_max448-swap-ab-fast]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_cute_dsl_pinned_recipe_matches_env[e4m3_max256-swap-ab-strict]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n16-swiglu-w4a8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n16-swiglu-mxfp8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n16-situ-gate-w4a8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n16-situ-gate-mxfp8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n16-situ-gate-and-up-w4a8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n16-situ-gate-and-up-mxfp8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n128-two-cta-swiglu-w4a8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n128-two-cta-swiglu-mxfp8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n128-two-cta-situ-gate-w4a8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n128-two-cta-situ-gate-mxfp8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n128-two-cta-situ-gate-and-up-w4a8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_mxfp_unfused_public_apis[n128-two-cta-situ-gate-and-up-mxfp8]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_swap_ab_gemm_k_tail[16-1-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_swap_ab_gemm_k_tail[16-17-128]' \
  tests/moe/test_cute_dsl_mxfp8_moe.py::test_mxfp8_relu2_moe \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[True-relu2-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_cute_dsl_pinned_recipe_matches_env[e4m3_max448-swap-ab-strict]' \
  'tests/moe/test_cute_dsl_fused_moe.py::test_cute_dsl_pinned_recipe_matches_env[e4m3_max256-swap-ab-fast]' \
  tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_weight_scale_update \
  --junitxml \
  gpu6-exact.xml
```

```bash
python -m pytest -q --disable-warnings --maxfail=1 \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-tensor-unfused-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-tensor-fused-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-token-unfused-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a4-per-token-fused-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-w4a16-unfused-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-swap-ab-w4a4-per-tensor-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-swap-ab-w4a4-per-token-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-2-swap-ab-w4a16-128]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-tensor-unfused]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-tensor-fused]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-token-unfused]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-token-fused]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a16-unfused]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-swap-ab-w4a4-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-swap-ab-w4a4-per-token]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-swap-ab-w4a16]' \
  tests/moe/test_unified_moe.py::test_cute_dsl_typed_activation_matches_flat_reference \
  tests/moe/test_cute_dsl_fused_moe.py::test_w4a8_fused_moe_tactics_and_apis \
  tests/autotuner/test_autotune_cache_scope.py \
  tests/autotuner/test_autotune_cache_v2.py::test_measure_policy_overrides_profiling_config \
  tests/autotuner/test_autotune_cache_v2.py::test_measure_policy_isolates_store_identity \
  tests/autotuner/test_autotune_cache_v2.py::test_measure_policy_attach_carries_to_serving \
  tests/autotuner/test_autotune_cache_v2.py::test_measure_policy_execution_mode_resolution \
  tests/autotuner/test_autotune_cache_v2.py::test_measure_policy_all_none_is_default_identity \
  tests/autotuner/test_autotune_cache_v2.py::test_policy_switch_reprofiles_in_process \
  --junitxml \
  gpu7-api.xml
```

Linux compilation-cache tests (same command as the retained-head receipt):

```bash
python3 -m unittest discover -s ci/tests -p test_compile_cache.py -v
```

## Local focused-probe harness and raw results

The following record contains the actual deployment-specific `validation-tools/run.py` commands. These commands require the archived local harness and source/runtime receipts; they are **not portable commands provided by the FlashInfer repository**. The focused sanitizer probe uses the tracked repository sanitizer filters/options, but adds project-local compile/route observation. Its within-source storage-bit checks are distinct from the maintained numerical-reference tests above. Relative evidence links below refer to the archived validation bundle.

### Retained compact FC2 validation

Passed on `83dfef8a656384f5cd10db847602593bb6f9b2c6`: **95 selected pytest cases**, **11 Linux compilation-cache tests**, and **384 focused sanitizer graph replays** (128 each for memcheck, synccheck and racecheck). Zero failed/error/skipped pytest cases and zero sanitizer errors/warnings. All five groups passed on their first attempt; pytest warnings remain visible in the raw output below.

- All 348 recorded source hashes match the pinned Git commit. The tracked snapshot stayed clean before/after every group and at postflight; the retained reference and actual-plan fixture were used directly.
- Five assigned NVIDIA B300 SXM6 GPUs (SM103), C3 `fi-moe-nvfp4-port-1026`, image `nvcr.io/nvidia/pytorch:26.05-py3`. Python 3.12.3, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CUDA `13.2`, CuTe DSL 4.8.0, pytest 9.1.1, TVM-FFI 0.1.15.post1.
- Compute Sanitizer 2026.3.0.0; persistent native compilation caches retained and dump/output directories isolated. GPUs 1–5 were idle/0 MiB at postflight and released to the parent benchmark campaign.

| Group | Result |
|---|---:|
| Existing accuracy/kernel tests | 33 passed |
| Wrapper, graph, unified API and autotuner tests | 62 passed |
| Linux compilation-cache tests | 11 passed |
| Memcheck | 128 replays / 64 compiled GEMMs |
| Synccheck | 128 replays / 64 compiled GEMMs |
| Racecheck | 128 replays / 64 compiled GEMMs |

Raw summaries:

```text
33 passed, 1311 warnings in 140.70s (0:02:20)
62 passed, 2424 warnings in 95.41s (0:01:35)
Ran 11 tests in 5.687s

OK
```

memcheck:
```text
========= COMPUTE-SANITIZER
========= ERROR SUMMARY: 0 errors
PASS 128 source-bound exact replays
```

synccheck:
```text
========= COMPUTE-SANITIZER
========= ERROR SUMMARY: 0 errors
PASS 128 source-bound exact replays
```

racecheck:
```text
========= COMPUTE-SANITIZER
========= RACECHECK SUMMARY: 0 hazards displayed (0 errors, 0 warnings)
PASS 128 source-bound exact replays
```

Commands used (each on an exclusively assigned idle GPU):

```bash
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563 --kind memcheck --gpu 1
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563 --kind synccheck --gpu 2
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563 --kind racecheck --gpu 3
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563 --kind exact --gpu 4
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563 --kind api --gpu 5
```

The existing pytest selectors are unchanged in [selection.json](evidence/validation-tools/selection.json). All expanded subprocess commands, environment settings, source hashes and JUnit results are retained in the per-group receipts. The graph probe is a local artifact and adds no repository test or production source changes.

Coverage and boundaries:

- H512/I384, 257 tokens, top-2, 96 local of 192 experts. Eight explicit configs 0/3/4/5/6/7/8/9 cover NVFP4 per-tensor/per-token, MXFP4x8/MXFP8, narrow/wide N, one/two CTA, M512, static/CLC, PDL off/on and balanced/skewed/empty/reactivated routes. Each tool compiled 24 partial-K and 40 aligned GEMMs.
- Each tool executes 64 compact-output replays across all four formats. Actual compiled metadata reports `output_is_routed=True`, 64-row/two-stage slabs. Every skewed replay has **six full and three partial slabs**, for both schedules and PDL settings. N128 valid rows are `[128,43,128,44,128,43]`; N256 rows are `[171,172,171]`. Each maps exactly 514 live rows. Post-replay inspection verifies exclusive compact prefixes, unique expanded indices, and exact dense-index mapping within allocation bounds. All-nonlocal and reactivated replays exercise index lifetime changes.
- Automatic 64-row slab coverage here is separate from the prior forced 32-row-slab source-paired gate. The focused probe checks storage bits across schedule/PDL variants within the same source; the separate 33-test group supplies the maintained independent numerical oracle. This is not an exhaustive tactic sweep.
- Tracked sanitizer filters/options are unchanged, including memcheck `--check-tensor-ops no`. All 64 memcheck cubins contain `-g-tmem-access-check`, nine named TMEM guard routines with matching assembled trap sites, and at least three direct guard calls. This establishes compiled instrumentation, not execution of each error branch. Only GEMM codegen is captured; native filter presence does not prove every matching native routing/prepare function executed. Instrumented memcheck local-memory accesses are not production spills.
- Earlier broad 150-case sanitizer results remain separately labeled d1767 evidence. This refresh does not repeat that matrix, qualify Hopper/Rubin, or add reference self-tests. No performance timing is included.
- Upstream precommit and Build Docs passed for this head. The upstream GPU jobs were skipped pending authorization; the failed [Test Results Summary](https://github.com/flashinfer-ai/flashinfer/actions/runs/40717866793/job/122920420727) is that gate, not a GPU test result.

Evidence:

- [Independent audit](audit.json), SHA256 `10b7f1ced543b1a193106841e48c4eefc483d142f3282605ac60158cfe8c690c`.
- [Verified archive](evidence-transfer.tar.gz): 813 files, SHA256 `b0c9272c65b63f5ba2717205bfc3e33319520e7531fb681212c8a50a86b55c5c`.
- [Manifest](evidence/validation/validation-manifest.json), SHA256 `d4e2282a527a4693ac77e2cab7b432b6a87137237d1b451ea5fd19a15733e815`.
- [Postflight](evidence/validation/postflight.json), SHA256 `435460999c71e7527c2c17cbbc0c2f5bfae692394373f94b431e8f25ff13556a`.
- Source receipt SHA256 `2744243f82e04fc0e45b93051ba3d5418768c47565ea839aef12902927a1f200`; runtime receipt SHA256 `eee35fe2acf3186a4ffb1c3269725cbfb2737fc5df3d4ae734351f4c1474d1a5`.
- Retained reference SHA256 `d8473bf5bc07ed35873415ac6be48548f86063a0ea60b943ea255ed5f27e6316`; actual-plan test file SHA256 `b96d1d7c1cf6d72429e1c24c3bf4c496dff608a648e924391e6af10608f5f502`.
