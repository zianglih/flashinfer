# Post-gain qualification plan — not executed

Run only after root retains a performance gain and releases the GPU locks. This plan was source-checked at static experiment `f14e4bae9379703fd5693d8ee993faae23e130d5` (parent candidate3r). Freeze the actually retained source and helpers before qualification; do not transfer a pass between revisions. No tests, GPU commands, source changes or new test implementations were performed for this note. All performance remains native AUTO; the explicit configurations below are untimed correctness checks.

## Numerical contract and preparation

Reuse the existing [W4A16 oracle](../flashinfer/tests/moe_ep/w4a16_reference.py), the contract used by #6277: independently unpack NVFP4/SF and round weights to BF16 (lines44–54); FP32 FC1 accumulation and existing activation math with BF16 handoff; FP32 FC2 accumulation then BF16 route outputs (lines289–332); transport route bits through integer reduction and combine in the established ordered FP32 sequence (lines337–358). `assert_w4a16_bits` compares finite BF16 outputs as `int16` with zero tolerance, including signed zero (lines361–367). Do not substitute a direct-kernel parity reference or widen tolerances. The [reference dispatcher](../flashinfer/tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py), lines960–979, selects this comparator for deterministic W4A16.

Use the existing [project correctness harness](../harness/correctness.py). Its first-compilation wrapper synchronizes each rank's CUDA work and enters an EP barrier **after workspace initialization and before first launch** (lines209–237); its persistent runtime owner prevents repeated NVSHMEM initialization/finalization across cases (lines263–274). This qualifies collectively prepared execution. It does not establish unsynchronized production first-use safety. The upstream routing helper's barrier before `layer.forward` occurs before lazy compilation/allocation, so that barrier alone does not provide this safeguard ([routing helper](../flashinfer/tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py), lines1644–1654). Preserve this distinction in the final report.

Use the measured pinned image/runtime, retaining its Torch: `nvcr.io/nvidia/pytorch:26.05-py3`, DSL4.7.1, NVSHMEM3.6.5/nvshmem4py0.3.1. The oracle requires Torch2.12's BF16 split-K control. A skipped prerequisite or missing rank completion is a failed qualification gate, not a pass. Capture source-before/after manifests, helper hashes, exact commands/environment, image, driver, all rank logs, exit codes and timeouts. Serialize groups under the existing GPU owner/locks; enforce a process-group timeout and reap every rank before the next command.

## Ready commands: focused gate, then broader shape coverage

The commands assume Bash on the coordinated Linux devbox; set these paths to the project and retained checkout there. Create a fresh output root. `qrun` is a command recipe, not a new harness implementation. Keep native performance caches separate from sanitizer-specific compilation.

```bash
set -euo pipefail
export QUAL_PROJECT=/absolute/path/to/flashinfer-w4a16-mixed-clusters
export QUAL_SOURCE="$QUAL_PROJECT/flashinfer"
export QUAL_OUT="$QUAL_PROJECT/runs/retained-qualification-a1"
export QUAL_IMAGE=nvcr.io/nvidia/pytorch:26.05-py3
mkdir "$QUAL_OUT"
cd "$QUAL_SOURCE"
export PYTHONPATH="$QUAL_SOURCE" PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
export PYTHONUNBUFFERED=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTEST_ADDOPTS=''
export OMP_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export BUILD_NVEP=0 BUILD_NIXL_EP=0 BUILD_NCCL_EP=0 FLASHINFER_BUILD_NO_PIP=1
export CUDA_HOME=/usr/local/cuda CUDA_MODULE_LOADING=LAZY
export FLASHINFER_MOE_EP_KNOB_CACHE=0 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_NVFP4_4OVER6=1 FLASHINFER_NVFP4_4OVER6_E4M3_USE_256=1
export FLASHINFER_NVFP4_4OVER6_ERR_MODE=MSE FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH=1
export FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1
export FLASHINFER_WORKSPACE_BASE="$QUAL_OUT/cache/flashinfer"
export CUTE_DSL_CACHE_DIR="$QUAL_OUT/cache/cute-dsl"
export CUDA_CACHE_PATH="$QUAL_OUT/cache/cuda-driver" TRITON_CACHE_DIR="$QUAL_OUT/cache/triton"
export CUDA_CACHE_DISABLE=0 CUTE_DSL_NO_CACHE=0 FLASHINFER_CUTE_DSL_DISABLE_CACHE=0
unset RANK WORLD_SIZE LOCAL_RANK LOCAL_WORLD_SIZE GROUP_RANK ROLE_RANK MASTER_ADDR MASTER_PORT
unset MEGA_NO_DIST MEGA_SINGLE_GPU_GLOO MEGA_USE_NCU CUTE_DSL_DUMP_DIR CUTE_DSL_KEEP_PTX CUTE_DSL_KEEP_CUBIN
qrun() {
  local label="$1" ep="$2"; shift 2
  python3 -m torch.distributed.run --nnodes=1 --nproc-per-node="$ep" \
    --master-addr=127.0.0.1 --master-port=29741 --max-restarts=0 \
    "$QUAL_PROJECT/harness/correctness.py" --source "$QUAL_SOURCE" \
    --output "$QUAL_OUT/$label" --image "$QUAL_IMAGE" "$@"
}
```

1. **Fast prepared numerical gate:** one EP2 mixed static/N32/epilogue-return case, H288/I448, boundary33, including the helper's balanced, uneven, skewed, single-token, empty-source, all-empty and refill rounds, plus refill graph replay. If only an atomic tactic is retained, select `atomic_counter` here instead. Stop at any failure.

```bash
qrun focused-static 2 --variants mixed4+2 --schedulers static --shapes tail \
  --tile-n 32 --return-modes epi_warps --boundary-token-counts 33 --graph
```

2. **After that passes:** cover both scheduler modes and return paths for the mixed kernel at all three N sizes, channel/K tails and inactive CTA pairs. Each loop iteration is16 configuration cases, not16 independent rank samples. The same helper executes changing batches and exact routed-count boundaries. Repeat tail/pair-tail coverage at EP4 only after EP2 passes. These are prepared-execution checks and do not enumerate the product group hints.

```bash
for qual_n in 32 64 128; do
  qrun "mixed-ep2-n$qual_n" 2 --variants mixed4+2 \
    --schedulers static,atomic_counter --shapes tiny,tail,pairtail,aligned \
    --tile-n "$qual_n" --return-modes epi_warps,reuse_dispatch_warps \
    --boundary-token-counts 15,16,17,31,32,33,63,64,65,127,128,129 --graph
done
qrun uniform-controls-ep2 2 --variants uniform2,uniform4 \
  --schedulers static,atomic_counter --shapes tiny,aligned --tile-n 32 \
  --return-modes epi_warps,reuse_dispatch_warps --boundary-token-counts 33 --graph
for qual_n in 32 64 128; do
  qrun "mixed-ep4-n$qual_n" 4 --variants mixed4+2 \
    --schedulers static,atomic_counter --shapes tail,pairtail --tile-n "$qual_n" \
    --return-modes epi_warps,reuse_dispatch_warps \
    --boundary-token-counts 33,65,129 --graph
done
```

3. **Placement evidence:** run the maintained scheduler test directly (single GPU, no torchrun) to observe actual preferred/fallback execution and exact work coverage. It has12 parameter combinations and multiple empty/ragged/partial-channel patterns; for `launch_shape="mixed"`, require the printed counts to contain both2 and4 with nonzero counts. Its assertion currently permits a degenerate physical mix, so passing pytest alone is insufficient for that placement claim.

```bash
CUDA_VISIBLE_DEVICES=0 python3 -m pytest -q -s -ra \
  tests/moe_ep/test_w4a16_mixed_cluster_scheduler.py
```

Then use the existing process-local [forced fallback override](../harness/forced_fallback.py) for full-kernel fallback branches in both modes and return paths. It keeps mixed code and logical `(4,1,Z)` grid but requires physical cluster2, refuses normalization to uniform4, and disables disk JIT caches before import. This is a fallback-only diagnostic, not naturally mixed placement and not performance evidence.

```bash
qrun forced-fallback-ep2 2 --variants mixed4+2 --force-fallback-clusters \
  --schedulers static,atomic_counter --shapes tail,pairtail --tile-n 32 \
  --return-modes epi_warps,reuse_dispatch_warps --boundary-token-counts 33 --graph
```

The natural full-kernel harness records host capacity, **not physical placement of its numerical launch**. Scheduler counts and the separate candidate3r PC profile cannot prove that invocation used both sizes. Exact same-launch mixed numerical coverage remains a receipt/instrumentation gap; qualify that explicitly before claiming it. Uniform4 control and forced2 tests independently exercise both branches but do not close this same-launch gap.

## Upstream entrypoints and remaining matrix boundaries

Current upstream entrypoints are in [the multirank suite](../flashinfer/tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py):

| Entry point | Existing scope |
| --- | --- |
| `test_w4a16_cluster_geometry_empty_refill` | EP2, four cases: uniform4 static-small/atomic-tail; mixed static-tail/atomic-pair-tail; N32, group6, refill and boundary33 graphs. |
| `test_nvfp4_mega_uneven_sources_and_empty_refill -k n32` | EP2, eight original M128/M256 N32 static/atomic cases; SwiGLU/epilogue and SiTU/dispatch, tails, empty/refill, boundary/graph checks. |
| `test_nvfp4_w4a16_epilogue_contract` | EP4 or EP8, nine activation/norm/routing-weight contract cases with graph replay; existing uniform geometry. |
| `test_nvfp4_mega_geometry_and_pipeline_tails -k w4a16` | EP2, uniform2 large-K/stage-wrap and skinny-channel controls, both returns. |

Use `python3 -m torch.distributed.run --nnodes=1 --nproc-per-node=2 --master-addr=127.0.0.1 --master-port=29743 --max-restarts=0 -m pytest -q -ra tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_w4a16_cluster_geometry_empty_refill` as the upstream geometry command; substitute the other node and the required EP count for the listed suites. Capture separate rank JUnit/logs and require expected case sets with zero failures/errors/skips. These direct pytest entrypoints lack the project harness's post-allocation first-use guard/persistent runtime owner; do not silently count them as the prepared path. Resolve that launch-preparation boundary before scheduling them as the required upstream qualification, without weakening the oracle.

The ready project harness supports EP2/EP4 only, top-k2, M256, fixed small shapes, deterministic reduction, and no explicit group-hint/activation/routing-weight-placement option. Omitted group hint resolves to frontend launch capacity, **not** product256/512/1024 ([frontend](../flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/frontend.py), line352). Its graph check captures/replays refill; the upstream geometry case also graphs boundary33. Therefore a retained release still needs a focused adaptation of the existing #6277 model-sized oracle harness for EP8 GLM5/top-k8, retained and exposed N/group/mode/return combinations, repeated replay/reset and both routing-weight placements if exposed. No such adaptation is implemented by this plan. Scope claims to what ran, or restrict unqualified exposure. The separate [IKR qualification plan](MIXED_IKR_QUALIFICATION_PLAN.md) remains mandatory if mixed IKR is exposed: its established BF16 atomic-term band is not deterministic bit equality, and current mixed harness graph checks do not support IKR.

## Sanitizer plan after numerical gates

Use per-rank Compute Sanitizer targets concurrently within each EP group, preserving peer progress; serialize different groups. Check the installed sanitizer version/help before launch. The CLI topology below follows the prior maintained [sanitizer worker pattern](../../flashinfer-k3-w4a16-megamoe-opt/hashinfer/tests/moe_ep/test_w4a16_megamoe_sanitizer.py), lines67–110/414–430: torchrun launches one sanitizer per rank, each directly launches the Python harness, so `application-only` instruments all EP Python ranks without compiler descendants. The [NVIDIA CLI reference](https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html) defines process targeting, kernel-substring filters and `%q{ENVVAR}` log expansion.

Start with EP2 mixed/N32/tail, both scheduler modes and both returns; reuse the prepared initialization guard. The filter intentionally checks owned MegaMoE kernels, not the oracle or every FlashInfer kernel. Require a matching instrumented kernel on every rank, complete harness receipts, zero sanitizer errors and successful process exits. A zero-error report with zero matched kernels is not coverage.

```bash
export QUAL_SANITIZER=/absolute/path/to/compute-sanitizer
for qual_tool in memcheck synccheck racecheck; do
  mkdir "$QUAL_OUT/$qual_tool-logs"
  python3 -m torch.distributed.run --nnodes=1 --nproc-per-node=2 \
    --master-addr=127.0.0.1 --master-port=29745 --max-restarts=0 --no-python \
    "$QUAL_SANITIZER" --tool "$qual_tool" --target-processes application-only \
    --error-exitcode 86 --check-exit-code yes --print-level info --print-limit 0 \
    --show-backtrace yes --kernel-name kns=Sm100W4A16MegaMoEKernel \
    --log-file "$QUAL_OUT/$qual_tool-logs/rank-%q{RANK}.log" \
    python3 "$QUAL_PROJECT/harness/correctness.py" --source "$QUAL_SOURCE" \
    --output "$QUAL_OUT/$qual_tool-cases" --image "$QUAL_IMAGE" \
    --variants mixed4+2 --schedulers static,atomic_counter --shapes tail \
    --tile-n 32 --return-modes epi_warps,reuse_dispatch_warps \
    --boundary-token-counts 33 --graph
done
```

After the focused sanitizer gates pass, repeat memcheck/synccheck on EP4 mixed tail/pair-tail at N32/N64/N128 and routed boundaries1/128/1024, plus the forced-fallback path; retain graph/reset coverage. Keep racecheck bounded to the small case unless evidence requires expansion. These ready commands still lack the EP8/model-size/group enumeration and per-launch mixed-placement receipts noted above. The old #6277 EP4/EP8,36-clean-rank-log result is historical evidence only and cannot be counted toward this revision.

Do not silently carry forward `--check-tensor-ops no`. Prior Compute Sanitizer2026.3 reported a legal two-CTA peer-barrier TMA false positive and used that documented exclusion **with** compiler `-g-tmem-access-check` guards. The current project harness has no corresponding compile-option wrapper; its frontend emits only `-maxrregcount=96` (lines440–447). If the current tool reproduces that limitation, retain the report and separately approve/document the narrowly scoped guard/exclusion adaptation before claiming comparable sanitizer coverage. A sanitizer timeout, internal tracking failure or unsupported check is not a clean result.

Completion requires exact source linkage, all rank completion markers, exact BF16 verdicts, explicit actual/forced placement scope, sanitizer logs, and honest remaining gaps. Do not aggregate stalled, partial, historical or forced-diagnostic results into the ordinary numerical total.
