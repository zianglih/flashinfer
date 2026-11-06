# Split W4A16 Gather4 experiment

## Source and evidence boundaries

- Before: current PR head `36740c36a32a6c6d1c7d8162823fe823912de741`.
- After: the same head plus the unstaged Gather4 patch. Record the actual diff and source hashes; do not invent a candidate commit or relabel previous measurements.
- Live local check on October 25, 2026: `git diff 6e070a25f6cdd3c07c715590dd2b0554aaecda0c HEAD -- flashinfer benchmarks/bench_moe_deepseek.py` is empty. Historical production-equivalent evidence is not a matched baseline for a new GPU allocation.
- The previous `w4a16-dyn-n-1024` C2/ziangli devbox is recorded as unavailable. Requesting or allocating a replacement is outside this read-only benchmark audit. The new allocation must use the newest live NGC CUDA 13.2 image, explicitly pinned. The historical image is `nvcr.io/nvidia/pytorch:26.05-py3`, eight B300 GPUs.
- Keep all existing 184 medians unchanged. Historical H7168 after measurements at `9ec90d0` predate later combine/arithmetic changes; they are not a whole-kernel current-head baseline. Historical K3 after measurements at `6e070a25` are source-equivalent but should not be mixed with a different host's candidate run.

## Retention and timing

- User steering: single-GPU, non-distributed benchmark only, to speed up iteration. Skip K3 entirely. Unfused finalize only; no fused-finalize, MegaMoE or dense performance campaign.
- Exact grid: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`.
- Run T1/T2 but exclude only those rows from retention. T4 is included.
- Overall geometric mean: 11 rows T4–512 and T4096/T8192/T16384. Decode: eight rows T4–512. Prefill: three rows T4096/T8192/T16384.
- Ten warmups and 100 native cold-L2 CUDA-graph CUPTI samples per row. PDL enabled. Reject CUDA-event fallback. Native input generation and timer remain unchanged.
- Fresh process per sweep and independent normal AUTO; no loading a saved cache into primary runs. Per-row AUTO selections are saved as evidence.
- ABBA: before R1, after R1, after R2, before R2. Row speedup is `sqrt((before_r1 * before_r2) / (after_r1 * after_r2))`. Preserve per-repeat ratios and all absolute medians. Do not select minima, pool samples, or substitute fixed-tactic diagnostics.
- No universal percentage cutoff. Require useful repeat-consistent performance, examine pointwise losses and prefill, and use separately labeled fixed-tactic crossover diagnostics where changed AUTO tactics would otherwise obscure the conclusion.
- Performance-first iteration remains authorized: focused correctness smoke before measurement; rigorous exact coverage and sanitizer work after a solid candidate is retained.

## Workload

H7168/I2048 single-GPU simulated EP8: `scripts/run_split_benchmark.py` preserves `bench_moe_deepseek._benchmark_single`; 256 experts, 32 local, top-k8, groups 8/top-groups4, scaling2.5, seed42, SwiGLU, BF16 activation/output and NVFP4 weights. Routing is timed; communication is absent. Native wrapper plus FC1/activation/FC2/unfused combine are timed.

## Existing environment setup

Use a project virtual environment with system site packages, retaining the container's Torch. Historical pins are `nvidia-cutlass-dsl[cu13]==4.7.1`, `cupti-python==13.4.0`, `nvidia-cuda-cupti==13.4.58` and `pytest==9.1.1`. Baseline and candidate need the same CUTLASS/CCCL/spdlog submodules and editable package data links. No distributed transport setup is needed. Record actual imported package versions and CUDA compiler/runtime separately.

Do not run old drivers blindly:

- `scripts/setup_remote.sh` pins old baseline `316faec`.
- `scripts/run_campaign.sh`/`complete_benchmark.sh` also run fused arms.
- `scripts/sync_candidate.sh` requires a clean committed candidate and updates remote refs.
- `scripts/summarize_results.py` and `summarize_k3_distributed.py` hardcode historical commits/hashes. Keep their historical reports intact; use an experiment-specific report for new evidence.

## New runner

`run_campaign.sh` accepts the remote project, independent before/after checkouts and a new output directory. It changes no Git refs or staging state. It requires both checkouts at current PR head, verifies production/benchmark before files are clean, archives the after diff, records source manifests including new untracked source files, and refuses output overwrite. The candidate patch must be stable across R1/R2. It saves the exact native harness, actual host/GPU/package versions, compiler output, GPU process/clock snapshots and selected environment fields. Set `W4A16_CONTAINER_IMAGE` to the actual pinned image before running.

```bash
project=/workspace/flashinfer-w4a16-gather4
export W4A16_CONTAINER_IMAGE=nvcr.io/nvidia/pytorch:26.05-py3 # Use the actual verified image.
bash "$project/experiments/gather4/run_campaign.sh" "$project" \
  "$project/baseline" "$project/candidate" \
  "$project/experiments/gather4/results/split-v1"
```

These are proposed commands, not execution evidence. Obtain a focused passing smoke and ensure exclusive GPU use before invoking them. Do not rerun completed historical rows; the fresh before arm is specifically a current-head control on the new allocation.

After copying all four complete sweeps, summarize without importing GPU libraries:

```bash
python3 experiments/gather4/summarize_results.py /absolute/path/to/split-v1
```

The summarizer creates `RESULTS.md` and `RESULTS.json` inside that new run folder and refuses to overwrite a report. It verifies runtime/source/cache provenance and the complete token grid, preserves every raw median and complete cache document, and compares complete token-specific tactic entries separately from cumulative cache contents. The geometric paired ratio is primary; median-of-two-sweep latencies and their ratio are explicitly descriptive only. Source differences are restricted to `moe_w4a16.py` and `moe_w4a16_kernel.py`.
