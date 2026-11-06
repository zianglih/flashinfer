- **Result:** 155 existing upstream pytest cases passed, with zero failures/errors/skips: 129 core MoE cases, 15 prepared MXFP4 controls, and 11 prepared two-stage cases. Original assertions/tolerances were retained. Both layouts also passed 107 task-local standalone cases each; a task-local W4A8 unfused check passed 12 pipeline configurations / 48 phases / 96 exact native-reduction comparisons.
- **Tested source:** `bde427290b33c55489e39c75d7e2a25365358ca0`, based on `07e519fcc149f39e6dd00264149c092c2e37767e`. Full current Python/JIT/native source was used, not the historical overlay. All six changed-file SHA256 values match the clean pushed checkout. Source archive SHA256: `022699934e7d31eb56a70ceab156555edc839fddc60138921c14b326916f2095`; built current `moe_utils.so`: `556cbd35d8680662b6505df465d23d84d2ba919247bcfd0e7630db2312a83819`.
- **Environment:** c2, `nvcr.io/nvidia/pytorch:26.05-py3`, B300 SXM6 AC / SM103, driver 590.48.01, CUDA toolkit 13.2.78, Python 3.12.3, Torch `2.12.0a0+5aff3928d8.nv26.05`. Eight GPUs allocated; native tests use GPU0, supplemental correctness uses GPU1 independently. EP8 is simulated within each single GPU, without inter-GPU communication. Official FlashInfer Python/cubin `0.7.0.dev20260923`, JIT-cache/SM103a `0.7.0.dev20260923+cu130` (all build `b395280a`); CuTe DSL 4.7.1, TVM FFI 0.1.11, pytest 9.1.1, cuda-bindings 13.2.0. JIT enabled; no package-version-check override. The full-source install reports `0.0.0+unknown` by design, without stale nightly build metadata.
- **Coverage:** deterministic W4A4 per-tensor/per-token and W4A16 accuracy; fused controls; cluster padding, route boundaries, wrapper graphs, simulated EP8, K tails, poisoned maps, and odd tile counts. New upstream prepared dual-tile routing and graph replay are tested in both ordinary and `MXFP4_DENSE_TWO_STAGE=1` modes; the latter preserves `skip_unpermute` and its separate finalizer.
- **Exact-reduction checks:** expanded/permuted rows; N=0/8/9/1024/1025, H264, top-k3; FP32/BF16/FP16 routing scales; random/cancellation/subnormal-input/subnormal-output/tiny-FP32-weight patterns; random EP8/all-masked routes, poisoned unused rows, PDL off/on, changed-input eager/graph execution. FP16 scales use exact FP32 promotion for the native oracle; zero-token checks exercise only the candidate no-op. W4A8 uses fixed tactics, H256/I128, top-k8, 256 global/32 local experts, N1/17/1025, offsets0/128, mixed/all-nonlocal/restored routing and three graph replays per phase. Native reduction consumes the same FC2 rows, so this is an exact reduction/synchronization check, not an independent W4A8 GEMM accuracy oracle.
- **Host checks:** changed-file pre-commit, including mypy/Ruff, and `git diff --check` pass. Eight mocked CUTLASS CLI-to-backend wiring cases and CLI help pass; these are not CUTLASS GPU tests.
- **Limits:** no full-suite, multi-GPU transport, other-architecture, exhaustive concurrency, or >2 GiB offset campaign. No performance rerun for this rebase; all performance tables above retain their pre-rebase revisions. The audit found no introduced numeric, indexing, synchronization, or integration blocker; it does not establish new performance gains from upstream kernel changes.

<details>
<summary>Reproduce the 155 current-source upstream tests</summary>

Run in Bash inside the image above. Install matching wheel packages for available prebuilt components, then use the entire pinned source. Only unchanged CUTLASS/CCCL/spdlog headers come from the nightly; the changed native routing ABI requires current `csrc`/`include` and a first-use build.

```bash
set -euo pipefail
export TASK_ROOT=${TASK_ROOT:-$PWD/fi5319-rebase-validation}
mkdir -p "$TASK_ROOT"
cd "$TASK_ROOT"
export TASK_ROOT=$PWD
unset PIP_CONSTRAINT PYTHONPATH FLASHINFER_DISABLE_JIT FLASHINFER_DISABLE_VERSION_CHECK
python -m pip install --no-deps \
  flashinfer-python==0.7.0.dev20260923 flashinfer-cubin==0.7.0.dev20260923 \
  flashinfer-jit-cache==0.7.0.dev20260923+cu130 \
  flashinfer-jit-cache-sm103a==0.7.0.dev20260923+cu130 \
  --index-url https://flashinfer.ai/whl/nightly \
  --extra-index-url https://flashinfer.ai/whl/nightly/cu130
python -m pip install 'nvidia-cutlass-dsl[cu13]==4.7.1' \
  apache-tvm-ffi==0.1.11 cupti-python==13.4.0 pytest==9.1.1
git clone --filter=blob:none https://github.com/flashinfer-ai/flashinfer.git repo
git -C repo fetch origin bde427290b33c55489e39c75d7e2a25365358ca0
git -C repo checkout --detach bde427290b33c55489e39c75d7e2a25365358ca0
python - <<'PY'
import importlib.metadata as m
from pathlib import Path
repo = Path('repo').resolve()
wheel_data = Path(m.distribution('flashinfer-python').locate_file('flashinfer/data'))
data = repo / 'flashinfer/data'
data.mkdir(exist_ok=True)
for name in ('csrc', 'include', 'cutlass', 'cccl', 'spdlog'):
    target = repo / name if name in ('csrc', 'include') else wheel_data / name
    (data / name).symlink_to(target, target_is_directory=True)
assert not (repo / 'flashinfer/_build_meta.py').exists()
PY
export PYTHONPATH=$TASK_ROOT/repo FLASHINFER_WORKSPACE_BASE=$TASK_ROOT/cache
export CUDA_VISIBLE_DEVICES=0 MAX_JOBS=16 PYTHONUNBUFFERED=1
unset FLASHINFER_DIST_AWARE_AUTOTUNE
cd "$TASK_ROOT/repo"
MAIN=tests/moe/test_cute_dsl_fused_moe.py
SITU=tests/moe/test_cute_dsl_mxfp4_situ.py
export MXFP4_DENSE_TWO_STAGE=0
python -m pytest -v --tb=short --durations=20 \
  "$MAIN::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy" \
  "$MAIN::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles" \
  "$MAIN::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy" \
  "$MAIN::TestCuteDslMoEWrapper::test_wrapper_cuda_graph" \
  "$MAIN::TestExpertParallelism::test_functional_with_ep" \
  "$MAIN::test_gather_gemm_k_tail" \
  "$MAIN::test_w4a8_fused_moe_tactics_and_apis" \
  "$MAIN::TestMoeSortBufferInitPoisoned" \
  "$MAIN::TestOddTileCountBoundsContract"
python -m pytest -v --tb=short --durations=20 \
  "$SITU::test_dense_dual_tile_routing_follows_rows_per_expert" \
  "$SITU::test_dense_dual_tile_keeps_128_where_256_pads" \
  "$SITU::test_dense_route_preprocess_pdl_matches_torch" \
  "$SITU::test_dense_gemm1_cluster_split_k_matches_plain"
export MXFP4_DENSE_TWO_STAGE=1
python -m pytest -v --tb=short --durations=20 \
  "$SITU::test_dense_dual_tile_routing_follows_rows_per_expert" \
  "$SITU::test_dense_dual_tile_keeps_128_where_256_pads" \
  "$SITU::test_dense_gemm1_cluster_split_k_matches_plain"
```

The fused memset-policy test is intentionally excluded from the two-stage phase: its assertions require the fused output-clearing contract. No assertions were changed to make tests pass.

</details>

Supplemental scripts are task-local validation artifacts, not new upstream tests. Complete logs, JUnit XML, environment/source hashes, and scripts are preserved in `c2-evidence.tar.gz`, SHA256 `ed21f540e4768e398be4727fc70e773049fba90cf36f14b02576973476e0a39f`. Complete per-case outcomes follow; deprecation-warning text and JIT-download chatter are omitted from the presentation.
