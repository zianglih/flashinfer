# Split W4A16 dynamic-N comparison

## References and latest user steering

The requested earlier split implementation optimization is [FlashInfer #5186](https://github.com/flashinfer-ai/flashinfer/pull/5186), `perf: reduce split W4A16 routing and output overhead` (live GitHub check: merged). #5319 is the separate shared unfused-finalize optimization and is not the closest methodology reference.

Canonical retained campaign: `/Users/ziangli/playground/projects/flashinfer-w4a16-split-optimization/`.
The `scripts/run_split_benchmark.py` here is copied byte-for-byte from its `run_split_benchmark.py`. Its `_benchmark_single` signature and W4A16-only selector match the new checkout's upstream benchmark as inspected on October 24, 2026.

The user subsequently specified the **exact token grid and retention policy from the latest merged MegaMoE optimization**, [FlashInfer #6277](https://github.com/flashinfer-ai/flashinfer/pull/6277), `Add small-shape W4A16 MegaMoE tactics and model benchmarks`. Live GitHub verification as authenticated `zianglih`: merged **2026-10-14T21:52:15Z**, head `866c80d0c70a90624b4c2056d12d1543d709609e`, merge `ceb589ce3e28bebcbb3b6628b5d4fcb5c2c2eceb`. A live search for all user-authored merged FlashInfer PRs since that date returned only #6277. The full source body and verification metadata are saved in `pr6277-reference.json`.

This changes token inclusion and retention assessment. Keep the existing split workload, routing-inclusive scope and ten-warmup native timer from #5186. #6277 itself used distributed GLM5, precomputed routing, three warmups and rank-MAX samples; those are not silently substituted into this split experiment.

**Latest explicit user override:** “we don’t care about the fused path performance.” Retention and further optimization use **unfused performance only**. All already collected fused timings remain reported for transparency; fused gains/regressions do not enter retention and do not require more tuning or diagnostic runs. Preserve all 106 measured medians across the eight primary arm sweeps and the baseline T16384 appendix.

## Matched workload and timing

- Native `benchmarks/bench_moe_deepseek.py` W4A16 arm, wrapper enabled, unchanged native input generation and timer.
- H7168 / I2048; 256 global experts; top-k8; groups 8/top-groups 4; routed scaling 2.5; seed 42; routing-bias scale 0.01; SwiGLU; BF16 activations/output, NVFP4 weights.
- Single-GPU simulated EP8/TP1: 32 local experts, local offset 0. Routing is timed. Weight preparation, allocation, compilation/autotuning and inter-GPU communication are excluded.
- Exact requested tokens for new sweeps: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384` (13 points).
- Baseline unfused R1 had already started on the original 14-point grid through 8192. Reuse it without rerunning any measured row; preserve T1024/T2048 as supplemental, potentially unpaired observations. Measure its missing T16384 separately in `baseline-unfused-r1-extra16384.json`. Candidate R1 and subsequent new sweeps use the exact 13-point grid.
- Fused and unfused finalize were measured separately. Unfused is the sole performance retention target; preserve the completed fused measurements as reported-only evidence.
- Ten warmups, 100 cold-L2 CUDA-graph native CUPTI samples per row, median latency. `TRTLLM_ENABLE_PDL=1`, `FLASHINFER_DIST_AWARE_AUTOTUNE=0`, GPU0 exclusively used.
- Normal autotuning independently in every fresh sweep process, `autotune_cache=None`; do not load tactics from another arm for the primary comparison. Saved per-row tactic caches are evidence and optional diagnostic profiling inputs.
- Use identical benchmark harness/source, GPU and compiler/runtime for before and after; record full commits, source hashes, image, toolchain and hardware. Keep before and after on the same pinned upstream base except the candidate patch.

## Commands

From the project root inside the chosen CUDA 13.2 devbox, with the project's Python environment active:

```bash
export CUDA_VISIBLE_DEVICES=0
export TRTLLM_ENABLE_PDL=1
export FLASHINFER_DIST_AWARE_AUTOTUNE=0
export PYTHONUNBUFFERED=1
export TORCH_EXTENSIONS_DIR="$PWD/caches/torch-extensions"
export FLASHINFER_WORKSPACE_BASE=/root

tokens=1,2,4,8,16,32,64,128,256,512,4096,8192,16384
python scripts/run_split_benchmark.py --repo baseline --tokens "$tokens" --no-fused-finalize --output results/baseline-unfused-r1.json
python scripts/run_split_benchmark.py --repo candidate --tokens "$tokens" --no-fused-finalize --output results/candidate-unfused-r1.json
python scripts/run_split_benchmark.py --repo baseline --tokens "$tokens" --output results/baseline-fused-r1.json
python scripts/run_split_benchmark.py --repo candidate --tokens "$tokens" --output results/candidate-fused-r1.json
```

These are reproduction commands for new measurements, not instructions to replace existing output. Run arms sequentially and preserve stdout for every invocation. Existing baseline R1 is reused; only its absent row needs an additional command:

```bash
python scripts/run_split_benchmark.py --repo baseline --tokens 16384 --no-fused-finalize \
  --output results/baseline-unfused-r1-extra16384.json
```

The copied harness records source hashes, actual runtime versions, routing histograms, native medians and saved tactic caches; it converts CUPTI fallback warnings to errors and imports CUPTI 13+ explicitly. Independent autotuning can choose different tactics, so overall gains are not necessarily fixed-tactic instruction gains. Repeat evidence uses the existing planned R2 arms; this policy correction does not schedule a rerun of any completed point.

## Reporting and retention

- Publish all raw sweep medians with per-row before/after ratios.
- For one repeat, speedup is Before/After. For two repeats, speedup is `sqrt((before_r1 * before_r2) / (after_r1 * after_r2))`; do not select minima across runs, pool samples across arms or replace rows with fixed-tactic diagnostic results.
- **Unfused retention only; exclude only T1/T2. T4 is included.** The exact 11 retention points are `4,8,16,32,64,128,256,512,4096,8192,16384`. Fused rows and descriptive aggregates are reported separately and excluded from the retention decision.
- Report overall geometric mean, decode geometric mean over `4,8,16,32,64,128,256,512` (eight points), and prefill geometric mean over `4096,8192,16384` (three points).
- T1024/T2048 remain in raw/report tables if already measured. They are supplemental, outside #6277's exact grid, and require no extra matching measurement. Missing cells stay missing.
- Unfused retention requires useful, repeat-consistent performance and an explicit assessment of fixed-tactic tradeoffs. Review all unfused pointwise gains/losses and selected tactics, including every prefill point. AUTO selecting a tactic, or a small aggregate gain driven by tactic changes, is insufficient by itself. Fixed-tactic probes remain separately labeled diagnostics. A repeatable unfused gain at T8192 can justify retaining the change alongside a smaller unfused T16384 tradeoff; quantify that tradeoff rather than requiring every fixed tactic to improve or claiming all regressions are resolved. Fused performance is not a gate under the explicit override.
- **No universal percentage threshold is stated in #6277.** Its retained GLM5 result was a mixed 1.00495× overall / 1.00777× decode / 0.99747× prefill. Later local N32 candidate experiments were rejected despite roughly 0.2–0.9% aggregate gains because of same-tactic regressions, flat unaffected points and mixed behavior; do not invent a 1%/2% cutoff or require every independently tuned row to improve.
- Small differences and tactic changes remain subject to run variation. Two sweeps do not establish statistical significance.
- #6277 explicitly reused a saved baseline and published one final sweep; its final evidence did not pool samples across arms. Preserve all existing evidence under this correction. The split predecessor used one final sweep for unfused and two for fused; the current planned two repeats for both modes add a consistency check.

The local `scripts/summarize_results.py` validates source/head/environment/histogram/cache hashes and accepts separate `<arm>-<mode>-rN-extra*.json` additions only for missing rows (duplicate rows are rejected). Default final reporting validates all eight already collected source/mode/repeat arms and the complete 13-point grid; this is an evidence-integrity check, not a fused performance gate. `--allow-partial` reports screening evidence and explicitly marks missing retention coverage. Missing T16384 never becomes a silently reduced final aggregate. The summarizer neither alters raw inputs nor runs GPU work.

Primary retention source: live #6277 body. Local interpretation/decision evidence: `/Users/ziangli/playground/projects/flashinfer-k3-w4a16-megamoe-opt/N32_GLM5_OPTIMIZATION.md` (measured candidate decisions and measurement contract), plus `evidence/scheduler-retention-assessment-v1.md` (no additional threshold, no pooling, limitations of within-run evidence).

## Historical runtime and environment (not current evidence)

The old B300 campaign needed 524.26 s for its initial fused sweep including first-time JIT; its warmed nonfused sweeps took 41.81 s and 41.88 s. These are planning estimates only, not promises for the new source/toolchain.

The old environment was `nvcr.io/nvidia/pytorch:26.05-py3`, B300/SM103, driver 590.48.01, Python 3.12.3, Torch 2.12.0a0+5aff3928d8.nv26.05, CUDA 13.2.78, DSL 4.7.1, cupti-python 13.4.0 / library 13.4.58. The DSL bundled compiler was 13.3.27 despite system CUDA 13.2; preserve this distinction when recording the new environment. Choose the newest live NGC image supplying CUDA 13.2 for this task.

Historical comparison sources were before `488ffbd9fe4455c3b4c3030cf668b5603c6698e4` and final head `88ff7db6a558e8acbc0cd964275410cf94e5c22c`; do not benchmark against these old revisions for the new patch.

## Focused correctness reference

#5186's existing focused selection was 66 cases and covered route boundaries, padding/cache reuse, EP8 and CUDA graphs. A dynamic-N change additionally needs irregular valid-token tails and every applicable MMA/cluster geometry, including empty/padded peer CTAs; use unchanged reference arithmetic and tolerances.

```bash
CUDA_VISIBLE_DEVICES=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0 \
python -m pytest \
  tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy \
  tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles \
  tests/moe/test_cute_dsl_fused_moe.py::TestExpertParallelism::test_functional_with_ep \
  tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph \
  -k 'w4a16 or test_finalize_handles_cluster_padding_and_partial_tiles' -v --tb=short
```

This selection may have evolved since #5186; inspect current collection before assuming the old count.

## Performance-first iteration order

After the initial focused GPU smoke passed, the user requested deferring rigorous correctness and sanitizer checks until a solid optimization is retained. All eight primary arm sweeps and the baseline T16384 appendix are now collected. The remaining bounded performance work is ten **unfused** fixed-cache diagnostic measurements at T8/T4096/T16384. Broader correctness checks follow unfused retention. No further fused performance tuning is requested. The primary harness stays byte-identical, and existing primary rows are never rerun merely to adopt this policy.
