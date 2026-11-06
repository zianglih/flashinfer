# W4A16 finalize extension validation

The external harnesses in `validation/` reuse the original effort's unmodified
nightly native helper snapshot (`../validation/native_tests/utils.py`, provenance
and SHA-256 checked against `SOURCE.json`). They never install packages, change
FlashInfer sources, autotune, or run performance measurements by default.

The runtime must be the prepared nightly environment with matching Python,
cubin, and JIT-cache distributions. Both overlays must use the same PR-base
W4A16 host and GEMM files, because these differ from the nightly's source. Only
the candidate routes unfused W4A16 through the new CuTe finalizer. Use separate
processes for baseline and candidate to avoid package and CuTe kernel-cache
contamination. The existing fixed W4A16 fallback tactic is recorded in each
report, checked against the runner's valid tactics, and shared between arms.

## Full pipeline: PDL, graph replay, and exact baseline comparisons

`validate_pdl.py` constructs the same activation, weights, routing, and scales in
each process. It hashes all API inputs before saving canonical CPU outputs.
Both PDL modes must match byte for byte in eager mode and on three graph replays,
then match baseline outputs byte for byte. Inputs change after capture and are
restored afterward to expose stale activation/routing state. Weights remain
fixed. The native W4A16 reference uses BF16 input and alpha-adjusted BF16 expert
weights, exactly as the native `_prepare_moe_quant_mode_inputs` helper does;
no tolerance is changed.

The small-shape matrix has 40 phase cases: tokens 1/3/16/128/4096, EP8 offsets
0/128, mixed/all-nonlocal routing, and initial/changed data. All-nonlocal routing
exercises zero-work FC2 grids and must produce exact zero. Native accuracy runs only through 128 tokens;
4096-token cases establish exact A/B, PDL, and graph equality only.

Copy the effort's `validation/native_tests` folder and these harnesses to the
corresponding remote paths before running. Replace the following root and overlay
names only if provisioning selected different names:

```bash
set -euo pipefail
ROOT=/hai-workspace/fi-w4a16-finalize
BASELINE="$ROOT/overlays/baseline"
CANDIDATE="$ROOT/overlays/candidate"
VALIDATION="$ROOT/w4a16-extension/validation"
ARTIFACTS="$ROOT/w4a16-extension/artifacts"
mkdir -p "$ARTIFACTS"

CUDA_VISIBLE_DEVICES=1 PYTHONPATH="$BASELINE" \
python "$VALIDATION/validate_pdl.py" \
  --native-tests "$ROOT/validation/native_tests" \
  --output "$ARTIFACTS/pipeline-baseline" \
  --tokens 1,3,16,128,4096 --offsets 0,128 --ep 8 \
  --hidden-size 256 --intermediate-size 512 --replays 3 \
  --max-reference-tokens 128 \
  2>&1 | tee "$ARTIFACTS/pipeline-baseline.log"

CUDA_VISIBLE_DEVICES=1 PYTHONPATH="$CANDIDATE" \
python "$VALIDATION/validate_pdl.py" \
  --native-tests "$ROOT/validation/native_tests" \
  --output "$ARTIFACTS/pipeline-candidate" \
  --compare-to "$ARTIFACTS/pipeline-baseline/outputs.pt" \
  --tokens 1,3,16,128,4096 --offsets 0,128 --ep 8 \
  --hidden-size 256 --intermediate-size 512 --replays 3 \
  --max-reference-tokens 128 \
  2>&1 | tee "$ARTIFACTS/pipeline-candidate.log"
```

Production H7168/I2048 adds four phase cases at N2048/EP8/offset0. This is an exact
baseline comparison, not a separate numerical oracle:

```bash
CUDA_VISIBLE_DEVICES=1 PYTHONPATH="$BASELINE" \
python "$VALIDATION/validate_pdl.py" \
  --native-tests "$ROOT/validation/native_tests" \
  --output "$ARTIFACTS/production-baseline" \
  --tokens 2048 --offsets 0 --ep 8 \
  --hidden-size 7168 --intermediate-size 2048 --replays 3 \
  --max-reference-tokens 0 \
  2>&1 | tee "$ARTIFACTS/production-baseline.log"

CUDA_VISIBLE_DEVICES=1 PYTHONPATH="$CANDIDATE" \
python "$VALIDATION/validate_pdl.py" \
  --native-tests "$ROOT/validation/native_tests" \
  --output "$ARTIFACTS/production-candidate" \
  --compare-to "$ARTIFACTS/production-baseline/outputs.pt" \
  --tokens 2048 --offsets 0 --ep 8 \
  --hidden-size 7168 --intermediate-size 2048 --replays 3 \
  --max-reference-tokens 0 \
  2>&1 | tee "$ARTIFACTS/production-candidate.log"
```

## Standalone permuted-row finalizer

`validate_finalize.py` compares
`flashinfer.fused_moe.cute_dsl.blackwell.moe_finalize.moe_unpermute` to the native
CuTe utility's C++ `moe_unpermute`, both with `input_is_expanded=False`. Active
rows are placed at unique random physical row indices among NaN padding. Index
zero is explicitly exercised as a valid row; negative entries mask unavailable
experts. Graph replays reverse positive row mappings, then change data/scales.
Every output must be byte-identical to the native oracle for PDL off/on and
for eager/graph execution. FP32 and BF16 scales include signed random and
cancellation-heavy values. All-masked outputs must be exact zero.

This matrix exercises both thread-count boundaries (8/9 tokens) and the
vectors-per-thread boundary (1024/1025), H264's partial tiles and H7168, and top-k
3/8. It contains 192 nonempty cases plus eight zero-token no-op cases. The native
zero-grid launcher is deliberately not called for zero tokens.

```bash
CUDA_VISIBLE_DEVICES=2 PYTHONPATH="$CANDIDATE" \
python "$VALIDATION/validate_finalize.py" \
  --output "$ARTIFACTS/permuted-finalizer" \
  --tokens 0,1,8,9,1024,1025,4096 \
  --hidden-sizes 264,7168 --top-k 3,8 \
  --scale-dtypes float32,bfloat16 \
  --patterns random,cancellation --routing random_ep8,all_masked \
  --replays 2 \
  2>&1 | tee "$ARTIFACTS/permuted-finalizer.log"
```

Standalone PDL calls do not establish overlap or the correctness of a live FC2
producer; the full-pipeline comparisons provide that producer/consumer check.
The harness retains optional subnormal/FP16 cases and standalone timing flags
from the earlier effort, but the command above does not use them.

## Existing native tests

The original 22-test subset plus eight native W4A16 boundary cases can run under the candidate overlay to cover
both W4A4 modes, W4A16, fused/unfused, graph/eager and EP8 controls. Do not modify
the native tests or their tolerance. The six route-tile cases use unfused
finalize with PDL off. The two cluster-padding/partial-tile native cases are
fused controls, so they do not directly validate the new unfused helper. An explicit path-based invocation is:

```bash
TEST_FILE="$ROOT/validation/native_tests/test_cute_dsl_fused_moe.py"
SELECTORS=(
  "$TEST_FILE::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy"
  "$TEST_FILE::TestExpertParallelism::test_functional_with_ep"
  "$TEST_FILE::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy"
  "$TEST_FILE::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[256-w4a16]"
  "$TEST_FILE::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[384-w4a16]"
)
for MODE in w4a4-per-tensor w4a4-per-token w4a16; do
  for FUSED in False True; do
    SELECTORS+=(
      "$TEST_FILE::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-$MODE-$FUSED]"
      "$TEST_FILE::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-8-$MODE-$FUSED-128]"
    )
  done
done
CUDA_VISIBLE_DEVICES=1 PYTHONPATH="$CANDIDATE" \
python -m pytest -v -ra "${SELECTORS[@]}" \
  2>&1 | tee "$ARTIFACTS/native-tests-candidate.log"
```

For direct unfused partial-tile coverage, rerun the pipeline pair with distinct
output directories, `--hidden-size 384 --intermediate-size 512 --tokens 17
--offsets 0,128 --routing-modes mixed,all_nonlocal`. This adds eight phase cases
using the existing two-CTA fallback tactic, with native reference enabled.

## Local preparation validation

Both scripts passed `python3 -m py_compile` and their `--help` paths without
importing a CUDA runtime. No GPU validation result is claimed by this document;
the commands must complete and their reports must have `complete: true` before
including results in the PR body. Every `--output` directory must be new, so a
rerun cannot silently overwrite earlier evidence.
