# Final 442 validation plan (CPU audit only)

Audited commit `442d2aa53f68b4640c3ab5118a76f1599ff60d34`. This file originally staged commands for **after the final ABBA benchmark**. After parent authorization, the95 focused existing tests completed:95 passed,0 failed/errors/skips, with24 fused boundary cases deselected. No optional57 wrapper/graph/EP cases were launched. No repository test file was added or changed. Numerical evidence is in `../../evidence/final442-validation/numerical/`; sanitizer results are tracked separately. The already completed56 capability tests,72 composed paired phase checks, and15 native exact configurations are existing evidence, not work to repeat here.

## Recommended existing numerical tests

All selections below explicitly avoid fused finalize. The test file is `tests/moe/test_cute_dsl_fused_moe.py`.

| Selection | Count from decorators | What it adds |
| --- | ---: | --- |
| `test_gather_gemm_k_tail` |60 =6 K×2 token counts×5 N capacities|Exact expected SwiGLU for NVFP4 K64/128/192/256/384/512, N16/32/64/128/256, reverse routing and poisoned adjacent SF row; physical M128/oneCTA only.|
| `TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy` |4|Independent unfused end-to-end reference: NV per-tensor SwiGLU, NV per-token ReLU2, W4A16 SwiGLU and ReLU2.|
| `TestCuteDslMoeW4A16::test_weight_scale_mapping` |6 =2 scale axes×3 geometries|Exact zero-tolerance row/K SF mapping for oneCTA, twoCTA and cluster2 W4A16 geometries. This alone is an ungated raw GEMM check.|
| `TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy -k False` |24 =6 route tiles×2 tail patterns×2 top-k values|Gated W4A16 layout integration for route8/16/32/64/128/192, one/twoCTA and mixed FC1/FC2 geometries; explicitly unfused. This is the useful regression check for removal of the old gated row remapping.|
| `TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a16-ordinary]` |1 test /3 hidden-size invocations|Unfused W4A16 full-cluster→padding-peer→full-cluster reuse, hidden256/384/256.|
| `TestCuteDslMoEWrapper::test_wrapper_accuracy -k False` |36 =3 T×3 quantization modes×2 top-k×2 expert counts|Unfused wrapper NV per-tensor/per-token and W4A16 numerical reference.|
| `TestCuteDslMoEWrapper::test_wrapper_cuda_graph -k False` |18 =3 T×3 quantization modes×2 expert counts|Unfused graph capture/replay with custom SwiGLU constants; includes per-token and W4A16.|
| `TestExpertParallelism::test_functional_with_ep -k False` |3 =3 quantization modes|Unfused EP8 with a nonzero local expert offset; one GPU simulates the local shard.|

Fast triage is the four deterministic-finalize cases. The focused numerical/layout set is95 cases (first five rows); adding the unfused wrapper/graph/EP selections gives152 cases. These are source-derived counts, not a pytest collection receipt. Counts include no skipped cases on supported B200/CuTe DSL, but runtime collection must confirm this. Runtime estimates are not reliable because reference loops synchronize per token/route and first-use compilation depends on cache state.

The generic numerical checks use the existing `check_accuracy` policy: at least97% of values within `abs_error < max(0.05,1.5*reference_std)` **or** relative error<0.5. They are independent-reference regressions, not bit-exact proof. The tail and W4A16 SF-mapping tests explicitly use rtol=atol=0. Already completed paired phase checks supply a separate exact-to-control boundary.

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n/candidate
source ../scripts/recovery442/env_candidate.sh
export PYTHONPATH=.
# Set CUDA_VISIBLE_DEVICES only to the GPU released by the coordinator.
PY=../.venv/bin/python
TEST=tests/moe/test_cute_dsl_fused_moe.py

# 4-case first triage; omit this separate call if immediately running the71-case batch.
$PY -m pytest -q "$TEST::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy"

# 71 cases, including those same4; do not repeat triage unnecessarily.
$PY -m pytest -q \
  "$TEST::test_gather_gemm_k_tail" \
  "$TEST::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy" \
  "$TEST::TestCuteDslMoeW4A16::test_weight_scale_mapping" \
  "$TEST::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a16-ordinary]"

# 24 unfused W4A16 boundary cases; only use_fused_finalize contributes a bool ID here.
$PY -m pytest -q \
  "$TEST::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy" -k False

# 57 additional unfused wrapper/graph/EP cases. All quant-mode IDs are explicit;
# False selects only use_fused_finalize=False, including BOTH per-token modes.
$PY -m pytest -q \
  "$TEST::TestCuteDslMoEWrapper::test_wrapper_accuracy" \
  "$TEST::TestCuteDslMoEWrapper::test_wrapper_cuda_graph" \
  "$TEST::TestExpertParallelism::test_functional_with_ep" -k False
```

## Dtype and fused-finalize boundary

The six low-level supported pairs are FP4/E4M3-SF16, FP4/E8M0-SF16, FP4/E8M0-SF32, E4M3/E8M0-SF32, E5M2/E8M0-SF32, and activation-E4M3×weight-FP4/E8M0-SF32. Existing repo numerical selections above cover NVFP4 SF16 plus W4A16 and per-token behavior, **not all six independent-reference split formats**. Preserve the existing72 composed paired phases and15 native exact configurations as the evidence for the other supported pairs; do not relabel unrelated dense GEMM or TRTLLM tests as coverage of this core.

`tests/gemm/test_cute_dsl_blockscaled_gemm.py` targets `Sm100BlockScaledPersistentDenseGemmKernel`, a different implementation. `test_split_nvfp4_kernel_matches_torch_reference` in the MoE-EP suite uses TRTLLM. `test_w4a8_fused_moe_tactics_and_apis` uses fused finalize, and the public unified W4A8 runner explicitly rejects unfused finalize. Those are not substitutes for retained split-core coverage.

Do not run the entire `test_cute_dsl_fused_moe.py` file, `TestAllValidTactics`, `TestOddTileCountBoundsContract`, default functional numerical/SiTU/GeGLU tests, or the W4A4 cluster-padding cases as a split-only validation claim: they use the default or explicit fused finalize. No broad fused, CAKE, unrelated dense GEMM, or distributed test expansion is staged here.

## Sanitizer stages

The installed tool is Compute Sanitizer2026.1.1.0, build37663202. After the numerical suite passed, the authorized sanitizer campaign completed:3 reference+12 FC1+24 FC2 memcheck cases with zero errors, then12 FC1+24 FC2 racecheck cases with zero hazards/errors/warnings. Full receipts are under `../../evidence/final442-validation/sanitizer/20261025T095319Z/`. These flags are supported: `--error-exitcode`, `--check-bulk-copy` (default yes), `--racecheck-memcpy-async` (default yes), and `--tool memcheck|racecheck|synccheck|initcheck`. Do not force blocking launches: that would change the pipeline/PDL scheduling under investigation. These passes cover only the bounded cases listed below; no exhaustive sanitizer claim is made.

First instrument a small existing reference subset (3 test cases) to catch launch/tool issues before expanding. These exact node IDs are explicit in the source:

```bash
mkdir -p ../logs/final442-validation
compute-sanitizer --tool memcheck --error-exitcode 99 --check-bulk-copy yes \
  --log-file ../logs/final442-validation/memcheck-reference.log \
  $PY -m pytest -q \
  "$TEST::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]" \
  "$TEST::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[relu2-per-token]" \
  "$TEST::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[w4a16-ordinary]"
```

For the actual changed twoCTA/NB2/TMA-SFB geometries, reuse existing task-local probes **directly**, without `run_paired.py` or `install.py`. Direct execution imports production `_run_blockscaled_gemm` from the442 checkout; it never selects the rejected SF loaders. This adds instrumented memory/synchronization coverage, not another ordinary paired numerical rerun. The FC1 probe only prints completion when run directly; it has no independent numerical oracle. FC2 also checks untouched output/canary storage.

```bash
# 12 production FC1 launches: six formats × quantized/per-token, M512/N128,
# K384, M768 channel tail,257 routed tokens, reverse gathers, SF poison guard.
SFREG_K=384 SFREG_N=128 SFREG_M=512 SFREG_CTA=2 \
compute-sanitizer --tool memcheck --error-exitcode 99 --check-bulk-copy yes \
  --log-file ../logs/final442-validation/memcheck-fc1.log \
  $PY ../scripts/fc1_sf_register_experiment/probe_fc1_formats.py

# 24 production FC2 launches: six formats × N128/N256 × per-token off/on,
# twoCTA, N+1 route tails, M384 channel tails, output canaries, unfused only.
SFB_GROUP=2 SFB_TILES=128,256 \
compute-sanitizer --tool memcheck --error-exitcode 99 --check-bulk-copy yes \
  --log-file ../logs/final442-validation/memcheck-fc2.log \
  $PY ../scripts/fc1_sf_register_experiment/probe_fc2.py
```

If memcheck passes, use the same two commands with `--tool racecheck --racecheck-memcpy-async yes --racecheck-report all` and separate log names to exercise stage ownership. Synccheck was not run because the bounded memcheck/racecheck stages were clean; it remains a follow-up only if a synchronization concern appears. No blanket suppressions are proposed. Report unsupported instrumentation, warnings, or resource failures as such; a zero exit status with skipped/no kernels is not a pass. Sanitizer instrumentation is not a performance measurement. PDL-on graph behavior is covered by the existing graph selections; optional sanitizer reruns with `SFREG_PDL=1` must be separately labeled if performed.

Source anchors: test decorators and bodies at307,1854,1972,2141,2173,2659,2805,3372; tolerance at `tests/moe/utils.py:1284`; architecture-specific16-row weight preparation at `flashinfer/fused_moe/prepare.py:2495`, W4A16 decode remapping removal at `blackwell/moe_w4a16_kernel.py:1063`.
