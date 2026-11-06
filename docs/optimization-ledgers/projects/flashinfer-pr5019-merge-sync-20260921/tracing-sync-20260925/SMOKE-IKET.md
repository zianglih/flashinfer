# FlashInfer native IKET W4A16 smoke

These external helpers target FlashInfer `74ba96d551640938edde68d628b36ba404a7f331` and do not change either source repository. The default is a CPU-only source-bound plan. `--run` uses EP4 with H=1024, I=1024, E=256, top8 and 32 tokens/rank (128 global tokens, 1,024 routes). All experts receive four tokens globally and one from each source rank; each token selects two distinct experts per owner. Each rank receives 256 routes; global totals are 256 local and 768 remote routes.

The fixed N64/G512 `epi_warps` tactic has `enable_iket=True`, deterministic external top-k reduction, native compiler defaults, two CTAs/cluster, and the normal full persistent grid. There is no tuning, target warmup, graph replay, or copied MoE computation. Packed weights and independent BF16/FP32 reference computation come from the selected FlashInfer checkout's existing `tests/moe_ep/w4a16_reference.py`. Input/weight preparation and the oracle execute other, unmarked kernels. The driver compiles all required staging variants before the rank barrier, launches the target once per rank, and requires finite BF16 bit equality for 32,768 output elements/rank. IKET may rerun the application during its own sizing/capture phases.

The earlier E16/T4-per-rank attempt completed its four-rank numerical checks and profiler execution, but cluster zero had no transform work on ranks 0 and 3, so the structural smoke correctly failed. The larger fixture increases scheduled work while retaining the same native atomic scheduler, full launch grid, and recorder filter. The earlier outputs remain separate historical evidence; this new fixture requires a fresh capture.

## CPU checks

```bash
cd /Users/ziangli/playground/projects/flashinfer-pr5019-merge-sync-20260921/tracing-sync-20260925
python3 smoke_iket_w4a16.py --source ../flashinfer --output smoke-check > smoke-plan.json
python3 test_smoke_iket_cpu.py
ruff check smoke_iket_w4a16.py audit_smoke_iket.py test_smoke_iket_cpu.py
ruff format --check smoke_iket_w4a16.py audit_smoke_iket.py test_smoke_iket_cpu.py
```

The plan verifies the exact clean Git commit and hashes all package Python files, the imported oracle, and the driver. Runtime checks these identities again after the numerical comparison and verifies the imported FlashInfer module resolves to the requested checkout. Native no-op IKET fallback is rejected. This is developer evidence preparation; GPU success is pending until actual output is collected.

## Native execution (coordinating task only)

Upload the three helper Python files beside the external validation scripts. After existing FlashInfer GPU tests finish, run in the already prepared environment, with fresh output directories:

```bash
set -euo pipefail
TASK_ROOT=/workspace/w4a16-trace-sync-0925
source "$TASK_ROOT/venv/bin/activate"
cd "$TASK_ROOT/flashinfer"
unset CUTE_DSL_COMPILER_OPT MEGA_NO_DIST
export PYTHONPATH="$PWD" OMP_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=0,1,2,3
export FLASHINFER_TRACE_IMAGE=nvcr.io/nvidia/pytorch:26.05-py3
export FLASHINFER_WORKSPACE_BASE="$TASK_ROOT/cache/flashinfer"
export CUTE_DSL_CACHE_DIR="$TASK_ROOT/cache/iket-smoke"
mkdir -p "$TASK_ROOT/validation/iket-smoke"
run-iket --output-dir "$TASK_ROOT/validation/iket-smoke/native" profile \
  --enabled-cluster 0,0,0 --postprocess all --keep -- \
  python -m torch.distributed.run --standalone --nproc-per-node=4 -- \
  "$TASK_ROOT/smoke_iket_w4a16.py" --source "$PWD" \
  --output "$TASK_ROOT/validation/iket-smoke/check" --run \
  > "$TASK_ROOT/validation/iket-smoke/run.log" 2>&1

python "$TASK_ROOT/audit_smoke_iket.py" --source "$PWD" \
  --smoke "$TASK_ROOT/validation/iket-smoke/check/smoke.json" \
  --iket-root "$TASK_ROOT/validation/iket-smoke/native" \
  --output "$TASK_ROOT/validation/iket-smoke/audit.json"
```

Require successful `run-iket`/`torchrun` exit as well as the audit result: the numerical JSON is written before final workspace/process-group teardown. The `--` before the driver path prevents torchrun from abbreviating the driver's `--run` as its own `--run-path` option.

The recorder filter does not cap the launch. The auditor requires four distinct capture PIDs and exact resolved rank/world/shape fields, locates each native JSON and Perfetto file using its rank's hexadecimal PID, requires one FlashInfer W4A16 launch per rank, and validates full-grid/two-CTA warp identity and paired range endpoints. All 16 transform warps must have matching ordered work-payload/K sequences, with exactly these four ordered subranges for every K iteration under every recorded transform work range:

- `transform_wait_raw_tma_ready`
- `transform_wait_tmem_slot_free`
- `transform_load_decode_nvfp4`
- `transform_store_commit_bf16`

Missing work on the selected cluster, missing/duplicate subranges, wrong source, malformed records, or numerical failures are errors. The audit records native JSON and decompressed Perfetto SHA256 values. This smoke checks actual compile/execute behavior and postprocessed hook structure; it does not claim complete SASS instrumentation coverage, instrumented performance, or an independently verified trace time unit. Keep all outputs outside the FlashInfer checkout.
