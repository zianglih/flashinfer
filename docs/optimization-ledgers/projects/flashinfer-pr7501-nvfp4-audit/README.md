# FlashInfer NVFP4 regression #7962

Upstream PR (ready for review): https://github.com/flashinfer-ai/flashinfer/pull/7976

Current PR head: `2bd125681b8d34c1835c1bd1916f8b9e3a630f6a`. Performance measurements and the full numerical suite were run at `9ac7ef83e8013cc0d37d5fd8ee62f325f211f6c4`; the benchmark-only review follow-up leaves the kernel and tests byte-for-byte unchanged. The independent checkout is `flashinfer/`, branch `fix/nvfp4-zero-scale-predicate`. The PR is open, ready for review, mergeable, and its published body/head/files were verified against the local result.

## Implementation and numerical contract

The final change hoists the independent approximate reciprocal of the global scale outside the encoded-E4M3-byte predicate. It retains `fp8SFVal != 0`, the multiply/reciprocal arithmetic, and zero-scale behavior. Twelve boundary tests cover FP16/BF16, ordinary/TMA shapes, and FP32 neighbors below/at/above the E4M3 zero midpoint through single and batched APIs.

The dedicated `bench_nvfp4_quantize_backend_comparison.py` now supports targeted M/K lists, iteration controls, optional CUDA graphs, reproducible identical backend inputs, per-sample CSV export, and heatmap suppression. The user-rejected `--fail-on-error` change is absent from the final commit and PR.

## Source arms

| Arm | Revision |
|---|---|
| before | `03d7f4a399a47e72d93631e19becd804147fc47b` |
| regressed | `fb022756415cc9cad1e1a64ee918860e17638fe8` (merged #7501) |
| historical_v3 | `fb022756` plus reciprocal-hoist code |
| main_before | `3472ad3ab194141353be7199807cb29f0d20af09` |
| flashinfer | `9ac7ef83e8013cc0d37d5fd8ee62f325f211f6c4` |

Upstream later advanced to `c472a430bdc4f0196e042e58bbd92d4047b43fc8`; its two added commits do not change the measured quantizer, dispatch, timing utility, or dedicated benchmark files. Historical and main pairs are reported separately because dispatch/scheduling changed between them.

## Remote environment

C3 devbox `fi-nvfp4-7962`, namespace `ziangli`, requested with `--bare` and no size option. Image `nvcr.io/nvidia/pytorch:26.05-py3` was selected from the live NGC catalog as the latest release providing CUDA 13.2. Remote task root: `/hai-workspace/flashinfer-nvfp4-7962`.

8 NVIDIA B300 SXM6 AC GPUs; driver 595.91.07, nvcc 13.2.78, Python 3.12.3, g++ 13.3.0, PyTorch 2.12.0a0+5aff3928d8.nv26.05. Timing used GPU 0 and validation GPU 1. GPU 0's requested SM lock was 1980 MHz, with memory 3996 MHz. The lock was reset after all measurements; the devbox remains available.

```sh
/usr/local/bin/h ssh fi-nvfp4-7962 -c c3 -n ziangli -- bash -lc 'cd /hai-workspace/flashinfer-nvfp4-7962; pwd'
```

## Final evidence

- `results/dedicated-final/`: primary dedicated backend benchmark. Same PR script used with all five source arms; BF16; M1024/2048 × K4096/7168/8192; layout128x4; both CUDA/CuTe; six serial rotated/reversed rounds; 100 warmups and 1000 measured samples per case/backend. CUPTI, CUDA graphs, cold L2, seed 42, standard fast NVFP4, PDL off. Separate precompile runs excluded. 30 measured processes and 360000 individual timing samples; all backend verification passed.
- `results/batched-final/`: supplemental native unified-runner measurements for the exact issue cases: single M1024K7168, batched B4M1024K4096, batched B8M2048K8192, with global scale1. Same six-round timing policy. All three historical cases recover beyond the parent. The main pair retains about 32 ns increases on the two batched cases (+0.26%,+0.05%), explicitly reported.
- `final-tables.md`: complete raw per-round medians and derived summaries. Dedicated CUDA gains vs#7501 range 0.38–1.22%; five of six cases meet/beat the parent. M2048K4096 retains a 0.35% parent gap.
- `results/sass-final/`: actual measured binaries' selected kernel dumps, resource usage, binary hashes, and compiler commands. `sass-analysis.md` contains the brief three-way explanation included in the PR. Historical register counts remain 80; main pair 72; all have 0 local and1024 shared bytes.
- `logs/fp4-final.log`: 1507 passed,1 failed in233.19 s. All 12 new boundary cases pass. The same CuTe graph capture failure occurs on unchanged main (`logs/fp4-main-before-full.log`:1495 passed,1 failed in278.54 s), at output allocation before launch. Final isolated graph test passes in 1.56 s. The underlying suite-context allocator/capture issue is not diagnosed here.
- `logs/pre-commit-all.log`: all repository checks passed.
- `logs/dedicated-cli-selfcheck.log`, `results/dedicated-final-cli-selfcheck/`: CPU CLI/options/CSV integration checks. `logs/bandwidth-smoke.log`: real GPU bandwidth-mode smoke test, 3 samples exported.
- `pr-body.md`, `pr-7976-verified.json`: final publication and verification receipt.
- `source-manifest.json`: exact final source hashes, revisions and PR-body hash.
- `evidence-final.tar.gz`: downloaded logs/results, excluding JIT caches. Full per-sample data is also extracted locally. Exact dependency versions are in `logs/pip-freeze.txt`.

## Helpers and retained investigation

`scripts/run_backend_comparison.py` and `scripts/run_benchmarks.py` orchestrate existing repository benchmark implementations; they validate outputs and reject fallback/missing samples. `scripts/report_results.py` renders final tables. `scripts/inspect_sass.py` captures measured SASS without recompiling. `scripts/pr-repro.sh` is the PR's reproduction shell sequence (syntax checked).

Earlier unsuccessful candidates remain for audit: `results/pilot`, `results/final-v1`, `results/candidates-v2-v3`, `scripts/predicate*.patch`, and `scripts/check_predicate.cu`. The exhaustive 2^32-FP32 check validates only the abandoned early-predicate candidate, not the final reciprocal-only implementation; it is deliberately excluded from final PR validation claims. Useful helpers and logs were preserved.

## Publication follow-up

PR #7976 was marked ready for review. Tracker #7504 now includes it and reflects the merged #7196/#7501 statuses. A concise reply was posted to NVIDIA issue #7962: https://github.com/flashinfer-ai/flashinfer/issues/7962#issuecomment-6516056118

All three remote changes were read back and verified; see `publication-followup-receipt.json`.

## Benchmark review follow-up

Commit `2bd125681b8d34c1835c1bd1916f8b9e3a630f6a` addresses both findings in review thread `discussion_r4420866152`: materialize the CUDA per-token scale before capture; reject the CUPTI graph fallback before writing CSV rows. Eager event fallback retains L2 flushing. CSV headers derive from metadata, and early heatmap skips reduce the benchmark delta versus main from 214 to 152 changed lines.

- `results/review-bot-repro/` and `logs/review-*.log`: pre-fix GPU reproductions retained.
- `scripts/check_benchmark_review_fix.py`: seven process-isolated real-GPU checks, using existing C3 B300 image/caches and `FLASHINFER_NVCC_THREADS=1` to match the diagnostic native cache. All seven pass: per-token/standard/bandwidth graphs; eager missing-CUPTI fallback; graph rejections for missing/old CUPTI and a multiline import error. Each successful backend exports three samples; rejected modes export zero.
- `results/review-fix/20261030T061311.485267Z/`: logs, CSVs, and exact source hash; `review-fix-evidence.tar.gz` is the downloaded archive. These are functional checks, not additional performance evidence.
- `results/review-fix-cli-selfcheck/`: CPU CLI checks, including defaults and invalid inputs.
- `logs/pre-commit-review-fix-all.log`: all pre-commit checks pass.
- `pr-body-review-fix.md`: current PR body; original `pr-body.md` remains the historical publication snapshot.
- `pr-7976-review-fix-reply.json`, `pr-7976-review-fix-resolved.json`: review reply and resolution receipts.

## Strict-mode applicability check

The analogous strict `__fdiv_rn` source hoist generates byte-identical SASS for the entire quantization module (605 function sections) on C3/CUDA13.2/SM103a. It adds no scheduling benefit, so the PR remains fast-only at2bd12568. The strict branch was not directly changed by#7501. See `strict-hoist-analysis.md`, `results/strict-hoist/`, and the retained experiment patches. Current PR body is `pr-body-strict-analysis.md`; older publication snapshots remain preserved.
