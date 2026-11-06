# Minimal full-grid retention plan for a unified PDL/cache candidate

Prepared read-only on2026-10-25. No candidate has been selected by this plan; no GPU, benchmark, source edit, commit, or PR operation was performed. Parent supplies the passing frozen source and reserves the GPU before execution.

## Scope and minimum new measurements

Preserve the established `scripts/BENCHMARK_PROTOCOL.md` / regular-TMA full-grid methodology and its recorded MegaMoE #6277 precedent. This is single-GPU simulated EP8/TP1, H7168/I2048/E256,32 local experts at offset0, top-k8, seed42, routing bias0.01, groups8/topgroup4, route scale2.5. It includes native logits routing, sort, routed preparation, FC1 activation/requantization, FC2, and deterministic combine. Initial activation/weight quantization and preparation, host allocation, compile/tune time, and communication remain outside timing. Routed payload/SF preparation is inside the replayed graph, while its host allocation occurs during graph construction.

Three CuTe modes: NVFP4 weights/activations with E4M3 SF16; homogeneous E4M3 MXFP8 with UE8M0 SF32; MXFP4 weights × E4M3 MXFP8 activations with UE8M0 SF32. Per-tensor scaling and unfused finalization only. Do not add per-token, W4A16, fused, distributed, or CAKE arms. Native TRT comparison is **NVFP4 only**, native logits routing and native finalize; `--no-fused-finalize` does not disable TRT's native finalize.

Exact ascending grid: **1,2,4,8,16,32,64,128,256,512,4096,8192,16384**. Report all13. Exclude only1/2 from retention: decode4–512 has8 points; prefill4096/8192/16384 has3; overall has11. Use10 warmups/100 cold-L2 CUDA-graph CUPTI iterations and the native median. Existing observers preserve medians, logs, histograms and AUTO-cache snapshots; they do **not** preserve the100 individual samples. Never claim otherwise.

The old `a65` B1/B2 and98fd regular-TMA/TRT campaigns remain immutable historical evidence. **Do not rerun original baseline arms.** Current B200-92 replaces B200-83 and has different GPU UUIDs; old medians cannot become adjacent new-node controls or prove a new controlled TRT ratio. The new control is corrected retained `aab93f854054de834447bdd8985b8bbd653fb3c8` (or a later explicitly approved retained source), not a65.

A compact schedule that reuses the same candidate data for both comparisons is:

1. Current-control R1, all3 formats (39rows).
2. Native TRT R1, NVFP4 only (13rows), on the same physical GPU as CuTe NVFP4.
3. Candidate R1, all3 formats (39rows); review before continuing. Stop broader retention if the complete screen fails the intended target.
4. If promising: candidate R2 (39rows), native TRT R2 (13rows), current-control R2 (39rows).

This gives current-control/candidate ABBA and TRT/candidate ABBA for NVFP4 without another candidate sweep:156 CuTe rows plus26 TRT rows,14 fresh processes total. A failed first full screen stops after91rows rather than running second repeats. If root already has an exact matching successful new-node arm, reuse its immutable record after checking provenance instead of rerunning it. None was assumed by this plan. Default to sequential work on one reserved physical GPU; parallel formats require separate stable per-mode GPU assignments, and NVFP4/TRT must still share one GPU. Never overlap measured runs on a GPU.

## Existing helpers to reuse unchanged

| Mode | Observer | Selection |
|---|---|---|
| NVFP4 CuTe | `scripts/run_split_benchmark.py` | Native `_benchmark_single(backends=("cutedsl",), profile_backend="cute-dsl", profile_cuda=False)` |
| MXFP8 / mixed | `scripts/unfused-blockscaled/run_split_benchmark.py` | `--weight-format mxfp8` / `mxfp4`, `--gated-group-size 16` |
| TRT NVFP4 | `scripts/trtllm_nvfp4_reference/run_trtllm_benchmark.py` | Native `_benchmark_single(backends=("trtllm-nvfp4",), profile_backend="trtllm-nvfp4", profile_cuda=False)` |

The MX assembly in the current repository is byte-identical to frozen v2 `scripts/unfused-blockscaled/bench_cute_dsl_mxfp8.py` (SHA632e8587…). Its adapter calls the same native input creator and unchanged full-chain assembly. No benchmark overlay or group64 compatibility shim is needed between aab and its descendant. `source-receipt.json` records literal equality and helper/source hashes.

The current native CLI supports `--backends cute-dsl-mxfp8` and `--backends cute-dsl-w4a8`, both with `--no-fused-finalize`, and `--backends trtllm-nvfp4`. However `--backends cutedsl` also runs W4A16. `--profile-backend cute-dsl` is CLI-coupled to `--profile-cuda`, so it must **not** be used as a replacement ordinary-timing NVFP4-only command. The original NV observer's programmatic filter is correct and preserves full precision/provenance/cache records.

Do not run the old `regular_tma_final_campaign/run_candidate_arm.sh`, old `verify_final.py`, or TRT `run_reference.py` unchanged: they pin442/review hashes, old output directories and/or B200-83 UUIDs. Reuse their chronology, source, cache and aggregation checks in a fresh outer manifest for this campaign. Never weaken those frozen validators or edit files in `fc1_regular_tma_auto/`; its manifest intentionally covers every top-level Python file.

## Freeze and cache policy

Prefer a parent-reviewed **committed candidate** in its own project-owned checkout. The clean-source observers reject tracked or untracked production/benchmark modifications; `--expected-head` is the tested commit, not a substitute for a dirty patch digest. A dirty candidate would require a new strict outer adapter with base commit, exact allowed changed-file list, full file/patch hashes, actual-module import guards and postflight checks; preserve the measured loop and demonstrate literal/AST equivalence as the regular-TMA adapter did. Do not reuse the442-specific dirty adapter for aab or label a dirty hash as a tested commit.

Pin identical benchmark/timer bytes across current control, candidate and TRT; explicit image `nvcr.io/nvidia/pytorch:26.05-py3`, current CUDA13.2.78/Torch26.05/CuTe4.7.1/CUPTI environment, physical GPU UUID, native source/cubin hashes, and source-import paths. Check every shared vendor target HEAD against the checkout's `3rdparty/<name>` gitlink. Ignored project-owned data/header symlinks are expected, but their resolved identity must be recorded. Keep `FLASHINFER_WORKSPACE_BASE` on the existing candidate native epoch when native `csrc/include` and resolved data hashes match; do not switch into or rebuild the a65 epoch.

Reuse a stable CuTe compiler cache for the same exact source/format between R1 and R2. A changed source gets a distinct cache identity; reuse an already compiled exact-source cache if available, without assuming experimental module aliases match canonical import cache keys. Keep native JIT artifacts that are unchanged. **AUTO caches are different:** set `FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0`, omit input `--cache`, and leave normal AUTO enabled in every fresh sweep. The saved per-token AUTO files are evidence only. Preserve in-process bucket reuse and ascending token order; do not spawn one process per token or manually sweep every tactic first.

Current aab exposes13 joint tactics/format, comprising8 unique FC1 and7 unique FC2 geometries. Source capability checks admit all13 for this workload. The three formats therefore have45 distinct GEMM geometry/dtype specializations per source arm before ancillary kernels/compiler implementation details, not13×13×2 kernels. See `../epilogue_codesign_audit/RETENTION_COMPILE_NOTES.md` for the source-count receipt and qualification. This is a specialization bound, not a promised compiler invocation count or wall-time estimate.

The Blackwell host path passes the SM count as the persistent CTA-grid limit; the kernel rounds it down to a multiple of the CTA-group size and uses `min_blocks_per_mp=1`. This is an SM-count-bounded launch, not a resource occupancy query. **One CTA per SM does not exclude a two-CTA cluster** spanning two SMs. Retain M256/two-CTA and logical-M512/N128 FC1 tactics; do not prune them, force cluster1, change launch grids, or add stage/register variants for this campaign. CuTe uses uncapped hybrid token buckets and reaches16K; native TRT retains its default8192 tuning cap. Do not normalize either by changing its policy. The CuTe helper profiles cold L2 with its established balanced approximate-max routing; actual measurements retain native seed42 routing.

## Commands once root freezes a clean winner

These are templates, not a launcher or authorization to run. The named variables must be assigned by the parent; select a fresh campaign directory and stable physical GPU. Each invocation below is one fresh sweep. Repeat only the approved schedule above, with distinct arm/output names.

```bash
set -euo pipefail
project=/workspace/flashinfer-w4a4-split-dynamic-n
cd "$project"
source scripts/recovery442/env_candidate.sh
export CUDA_VISIBLE_DEVICES="$reserved_gpu"
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
for task_recipe_name in ${!FLASHINFER_NVFP4_4OVER6@}; do unset "$task_recipe_name"; done
tokens=1,2,4,8,16,32,64,128,256,512,4096,8192,16384
image=nvcr.io/nvidia/pytorch:26.05-py3
# Set repo/head to the frozen control or winner; out to a fresh arm prefix.
test "$(git -C "$repo" rev-parse HEAD)" = "$head"
git -C "$repo" diff --exit-code HEAD -- flashinfer include csrc benchmarks
set -o noclobber

# CuTe NVFP4: source-specific cache reused only for this source's repeats.
export CUTE_DSL_CACHE_DIR="$project/cache/retention-$head/nvfp4"
"$project/.venv/bin/python" scripts/run_split_benchmark.py \
  --repo "$repo" --expected-head "$head" --image "$image" \
  --tokens "$tokens" --output "$out-nvfp4.json" > "$out-nvfp4.log" 2>&1

# CuTe MXFP8 and mixed: sequential, same frozen source.
for format in mxfp8 mxfp4; do
  export CUTE_DSL_CACHE_DIR="$project/cache/retention-$head/$format"
  "$project/.venv/bin/python" scripts/unfused-blockscaled/run_split_benchmark.py \
    --repo "$repo" --expected-head "$head" --image "$image" \
    --weight-format "$format" --gated-group-size 16 \
    --tokens "$tokens" --output "$out-$format.json" > "$out-$format.log" 2>&1
done

# Separate native TRT sweep on the frozen clean control checkout.
# out must be a new T1 or T2 prefix; native backend/library hashes stay fixed.
export CUTE_DSL_CACHE_DIR="$project/cache/retention-trt-$control_head"
"$project/.venv/bin/python" scripts/trtllm_nvfp4_reference/run_trtllm_benchmark.py \
  --repo "$control_repo" --expected-head "$control_head" --image "$image" \
  --tokens "$tokens" --output "$out-trt.json" > "$out-trt.log" 2>&1
```

No `--no-autotune`, `--profile-cuda`, `--functional-api`, `--include-activation-quant`, DA routing, or saved-tactic replay is added. The ordinary native CLI reproduction for MX/TRT is available in `scripts/unfused-blockscaled/NATIVE_REPRODUCTION.md`; the observers above add the evidence needed for retention.

## Verification and decision

Before source changes, archive all raw JSON/logs, every13-point cache snapshot and hash, AUTO winners, commands, source trees/patch or commit, helper hashes, native-build evidence, GPU/process snapshots and environment. Require complete13-row output, positive finite medians, correct backend/finalize scope, matching native input-routing histograms, no CUPTI fallback, unchanged source/dispatch and nonoverlapping chronology. Histograms alone do not prove cross-backend numerical equivalence. Existing focused exact checks are a prerequisite; broader affected tests/sanitizers follow retention, not another pre-screen sweep.

For each token compute `sqrt(C1*C2/(A1*A2))`; NVFP4 versus TRT uses `sqrt(T1*T2/(A1*A2))`. Then geometric-mean over the exact8/3/11-point groups; report both repeat directions, all13 rows, candidate/control drift, tactic changes, and each prefill tradeoff. Do not select minima, replace AUTO with a fixed-tactic result, pool timings, multiply ratios across hosts, or claim significance from two repeats. The recorded #6277-style protocol does not prescribe a universal percentage threshold. A small changed-AUTO winner alone is insufficient evidence of the intended stable improvement.
