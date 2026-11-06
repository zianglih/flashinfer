# Repository-only reproduction of the selected 26 cases

These commands execute the same exact pytest nodes, each in a fresh process, using repository tests directly. They do not require the project-owned validation wrappers. Run them from the HashInfer repository in the documented 8×B300 environment with its pinned Python/CUDA dependencies installed. The package/test bytes must match tested commit `55cd345d57ccc56327966201bd0725767a11593a`; the documentation-only head `a1486e2fc63d5a54fe727b3123ee04b1e611c035` is also compatible. Reserve the GPUs for the whole serial run.

The completed measured gate additionally recorded per-rank JUnit, imported-package provenance and source closure through the project wrapper. Direct pytest below preserves the test assertions and numerical JSON/CSV output but does not recreate those wrapper attestations. A skipped test is not a pass. No Compute Sanitizer run is included in this selection.

```bash
set -euo pipefail
git diff --exit-code 55cd345d57ccc56327966201bd0725767a11593a -- hashinfer tests/moe_ep
python - <<'PY'
import hashlib
from pathlib import Path
digest = hashlib.sha256()
for path in sorted(Path("hashinfer").rglob("*.py")):
    digest.update(str(path).encode())
    digest.update(path.read_bytes())
assert digest.hexdigest() == "a7001bd59e04b03b372ba4315b3cad8cdcfd7e2db40a96006a5a987c08939e29"
PY
export PYTHONPATH="$PWD" PYTHONFAULTHANDLER=1 PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1 TORCH_NCCL_ASYNC_ERROR_HANDLING=1 MEGA_USE_NCU=0
unset CUTE_DSL_COMPILER_OPT MEGA_NO_DIST
validation_out="$PWD/w4a16-validation-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir "$validation_out"
case_index=0

run_case() {
  local ranks="$1" node="$2" case_dir
  case_dir="$validation_out/case$(printf '%02d' "$case_index")"
  case_index=$((case_index + 1))
  mkdir "$case_dir"
  export HASHINFER_NUMERICS_REPORT_DIR="$case_dir/numerics"
  export HASHINFER_MOE_EP_KNOB_CACHE="$case_dir/knobs.json"
  case "$ranks" in
    8) export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 ;;
    4) export CUDA_VISIBLE_DEVICES=0,1,2,3 ;;
    2) export CUDA_VISIBLE_DEVICES=0,1 ;;
    1) export CUDA_VISIBLE_DEVICES=0 ;;
    *) return 2 ;;
  esac
  if [ "$ranks" -gt 1 ]; then
    timeout --signal=TERM --kill-after=30s 3h \
      python -m torch.distributed.run --nnodes=1 \
      --master-addr=127.0.0.1 --master-port=29791 \
      --nproc-per-node="$ranks" --max-restarts=0 \
      -m pytest -q -s -p no:cacheprovider --maxfail=1 "$node" \
      2>&1 | tee "$case_dir/run.log"
  else
    timeout --signal=TERM --kill-after=30s 3h \
      python -m pytest -q -s -p no:cacheprovider --maxfail=1 "$node" \
      2>&1 | tee "$case_dir/run.log"
  fi
}

numeric=tests/moe_ep/test_w4a16_megamoe_numerics.py::test_w4a16_megamoe_numerics
tail=tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_geometry_and_pipeline_tails
refill=tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_mega_uneven_sources_and_empty_refill
graph=tests/moe_ep/test_mega_cuda_graph_multirank.py::test_nvfp4_mega_two_rank_graph_replay_lockstep
prestaged=tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py::test_nvfp4_kernel_matches_torch_reference

# Three strict EP4 nodes, then one strict EP8 node.
run_case 4 "${numeric}[topk_fc2-random-ep4-glm5-t1024]"
run_case 4 "${numeric}[topk_fc2-skewed-ep4-glm5-t1]"
run_case 4 "${numeric}[topk_fc1-random-ep4-glm5-t1024]"
run_case 8 "${numeric}[topk_fc1-random-ep8-glm5-t128]"

# Ten geometry/pipeline tail nodes.
run_case 2 "${tail}[w4a16-small-epi_warps]"
run_case 2 "${tail}[w4a16-small-reuse_dispatch_warps]"
run_case 2 "${tail}[w4a16-tail-epi_warps]"
run_case 2 "${tail}[w4a16-tail-reuse_dispatch_warps]"
run_case 2 "${tail}[w4a16-n64-wrap-epi_warps]"
run_case 2 "${tail}[w4a16-n64-wrap-reuse_dispatch_warps]"
run_case 2 "${tail}[w4a16-n128-wrap-epi_warps]"
run_case 2 "${tail}[w4a16-n128-wrap-reuse_dispatch_warps]"
run_case 2 "${tail}[w4a16-activation-tail-epi_warps]"
run_case 2 "${tail}[w4a16-activation-tail-reuse_dispatch_warps]"

# Four uneven-source/empty-refill nodes and two graph lifecycle nodes.
run_case 2 "${refill}[static-epi_warps-w4a16]"
run_case 2 "${refill}[static-reuse_dispatch_warps-w4a16]"
run_case 2 "${refill}[atomic_counter-epi_warps-w4a16]"
run_case 2 "${refill}[atomic_counter-reuse_dispatch_warps-w4a16]"
run_case 2 "${graph}[w4a16-epi_warps-manual]"
run_case 2 "${graph}[w4a16-reuse_dispatch_warps-manual]"

# Six prestaged single-rank oracle nodes; direct pytest matches the gate.
run_case 1 "${prestaged}[regular-e4-epi_warps-w4a16]"
run_case 1 "${prestaged}[regular-e4-reuse_dispatch_warps-w4a16]"
run_case 1 "${prestaged}[tail-e4-epi_warps-w4a16]"
run_case 1 "${prestaged}[tail-e4-reuse_dispatch_warps-w4a16]"
run_case 1 "${prestaged}[singleton-e1-epi_warps-w4a16]"
run_case 1 "${prestaged}[singleton-e1-reuse_dispatch_warps-w4a16]"
```

The four strict cases each exercise O2/O3 × eight tactics × eager/graph: 32 combinations, 96 collective reference comparisons and 496 pairwise comparisons per case. Across the selected strict cases that is 128 / 384 / 1,984, without multiplying collective comparisons by rank. The remaining tests retain their own geometry, lifecycle and reference assertions and are not relabeled as that strict matrix. Completion evidence must show all 26 outer cases and 58 rank pytest passes with no failures, errors or skips. The parent-owned wrapped gate has now passed those actual checks; raw evidence is in `results/owned-r2-final-correctness-1.md` and its JSON audit.
