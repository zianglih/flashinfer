# CuTe DSL W4A4 unfused finalize optimization

Deliverable: draft upstream FlashInfer PR #5319, CuTe DSL code only, now covering W4A4 and W4A16 unfused finalize. Original per-tensor/per-token W4A4 measurements using the same EP8 DeepSeek benchmark methodology as SGLang PR #40105. Source branch: `codex/w4a4-unfused-finalize-pdl`; upstream base `eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095`.

## Runtime and method

- Devbox `fi-w4a4-finalize-0918`, C2, namespace ziangli; 8 B300 allocated, benchmark GPU0 only. Correctness/isolated tuning use GPU1/GPU2. Image `nvcr.io/nvidia/pytorch:26.05-py3` is the newest NVIDIA PyTorch image providing CUDA13.2, confirmed from live NGC/release notes before provisioning.
- Latest official nightly `0.7.0.dev20260917`, source `d233e27ddddbcfdc24eec38ab4dffda1f43ff49c`; matching Python/cubin/JIT-cache and SM103a cache provider. The changed W4A4 files match upstream base byte-for-byte before this patch; W4A16 reference stays on nightly.
- Full environment: `artifacts/environment.txt`; setup command: `scripts/setup_nightly.sh`.
- The SM103 cache wheel omits shared `moe_utils`, `dsv3_fused_routing`, and `trtllm_utils`; these were built on first use. All source overlays must share the unchanged `overlays/pdl-only/flashinfer/jit` package so C++ source/include paths stay constant. Do not run future controls from the installed package with an unset PYTHONPATH: it changes cache build paths. JIT remains enabled.
- Native nightly benchmark snapshot `scripts/bench_moe_deepseek.py` has an external-only W4A4 selector addition. No timing or workload code changes. `scripts/run_benchmark.sh` uses powers of2 from1 through16384, H7168/I2048/top8/256global/32local, TP1, simulatedEP8, input activation quantization included, PDL and CUDAgraphs enabled, coldL2, CUPTI,10warmups/100timed iterations, median. Each arm/mode has a separate autotuner cache. One sweep per candidate/configuration; no reverse sweep.

## Experiments and final validation

- Baseline unfused: full15 points, both W4A4 activation modes and a W4A16 control, complete. Raw logs/tactics under `artifacts/baseline/`.
- PDL-only: early FC2 launch hint after prerequisite wait, elected MMA lane, unfused+PDL only. Five points show no meaningful end-to-end improvement. Both CSV tables completed; the shell's completion print failed because its file was inadvertently updated during execution. Do not treat it as a fully successful script run. Numerical/performance claims must distinguish this diagnostic from final evidence.
- Combined v1: new expanded-row CuTe finalizer prefetches metadata before its PDL wait, then vector-loads BF16 rows and performs ordered FP32 FTZ-FMA with one BF16 conversion. Full15point sweep complete. Improves2–1024tokens; regresses at1 and largebatches. First-token autotuner chose a different FC1 tile. Raw logs/tactics under `artifacts/combined/`; derived `artifacts/combined-v1-summary/`.
- V1 correctness:40 phase cases byte-exact against baseline (PDLoff/on,eager/graph,inputchanges,EP8offsets0/128,tokens1/3/16/128/4096,H256/I512);963standalone cases pass;22native tests pass. Native oracle in phase checks runs only through128tokens;4096checks equality, notreference. Standalone FP16 scales use exactFP32promotion as oracle because native BF16input/FP16scale binding is absent. Zero-token cases validate candidate only.
- Final V2 commit: `fff0070cbeefda46e8f3c987a2bdc8e20584f062`; source parity verified against the measured `combined-v2` overlay in `artifacts/final-source-hashes.json`. Geometry uses 32 threads through 8 tokens, otherwise 128; four vectors per thread above 1024 tokens, otherwise one. V1 source remains in `artifacts/expanded_finalize-v1.py`.
- Final benchmark: all 30 W4A4 token/mode points improve against nightly unfused. At 16384 tokens, speedups are 1.0460x per-tensor and 1.0339x per-token; candidate remains 8.79%/7.36% slower than nightly fused respectively. `artifacts/final-summary/BENCHMARKS.json` contains 120 validated native rows including unchanged W4A16 references. One sweep; independently autotuned arms; no error bars or aggregate speedup claim.
- Final native tests: 22 passed, 629 deprecation warnings, 35.11s (`artifacts/native-tests-v2-session.log`). No new upstream tests.
- Final matched pipeline: 40 small/medium phase cases plus 4 production-shape cases pass byte-exact against nightly baseline, PDL on/off, eager/CUDA graphs, changed inputs and replay (`pdl-combined-v2-session.log`, `production-candidate-session.log`). Native numerical oracle is used only through 128 tokens in the small-shape harness; production-shape and 4096-token cases establish baseline equality only.
- Final standalone boundary checks: 96 byte-exact cases against native finalize, N1024/1025/4096, H264/7168, top-k3/8, FP32/BF16 scales, random/cancellation data, random EP8/all-masked routes, PDL/eager/graphs (`artifacts/finalize-v2-boundaries-session.log`). The earlier 963-case matrix is diagnostic V1 evidence only.
- Final fixed-tactic Nsight profile: 20 iterations per mode/arm at 4096 tokens, verified identical selected tactics. Per-tensor FC2/finalize pair span 89.393 to 78.6245 us; per-token 90.769 to 80.577 us. Finalizer lifetime includes its PDL wait. Raw 80 pairs and reports are under `artifacts/profiles-final/`.
- Changed-file pre-commit checks (including mypy/Ruff/format) and commit hooks passed. The full repository `--all-files` suite and other GPU architectures were not tested.

## Tools and artifacts

- `scripts/remote.py`: gzip/base64 smallfile upload and argv-safe managedh remote execution. It uses the already approved existing HAI checkout only through the CLI's inherited context; never a task-local HAI environment.
- `validation/validate_pdl.py`: matched deterministic native-fixture input/output snapshots and graph replay checks.
- `validation/validate_finalize.py`: standalone contract/FP edge checks; optional isolated timing.
- `scripts/tune_finalize.py`: fixed geometry microbenchmark, each variant one10/100coldL2graphCUPTI measurement, complete rawsamples.
- `scripts/profile_finalize.py`: identical-cache baseline/candidate FC2–finalize timelines. Always use source overlays for BOTH arms. `--output-root artifacts/profiles-v2` preserves aborted initial profiles.
- `scripts/summarize_benchmarks.py`: validates all15token rows, emits detailed ratios and full native CSV fields; no aggregate speedups.
- `VALIDATION_PLAN.md` and `PROFILE_FINALIZE.md`: planned coverage and exact helper usage; actual evidence belongs in logs/reports.

Upstream draft PR: https://github.com/flashinfer-ai/flashinfer/pull/5319 . Initial W4A4 head `fff0070cbeefda46e8f3c987a2bdc8e20584f062` was published and verified with three CuTe files. The W4A16 extension is now pushed as `ca2692a62679336301758d1b83b193b3c5b1170c`, with five CuTe files total. See `w4a16-extension/README.md` for its separate baseline, all fifteen token points, 8K exception, 30 native tests, 52 pipeline checks, and 200 standalone cases. The PR remains draft and attached to the Codex task.

## Evidence preservation and cleanup

- All 110 remote artifact files were downloaded and checked against remote SHA256s. Final archive: `artifacts/final-remote-evidence.tar.gz`, 227670205 bytes, SHA256 `fc9fc9837e4bd3143f6d5a12286b711473fbcc4faca97a711dca215d677ab665`; manifest: `artifacts/final-remote-evidence-manifest.json`. The first truncated archive and failed transfer log are retained separately; the retry log records complete verification.
- Local helper/harness reproduction archive: `artifacts/reproduction-harnesses.tar.gz`; source remains in the independent clone and public PR. Benchmark/test command logs remain under `artifacts/`.
- After verified evidence recovery and PR publication, managed `/usr/local/bin/h delete fi-w4a4-finalize-0918 -c c2 -n ziangli --force` confirmed deletion of this task's StatefulSet, Service, ConfigMap, and Workload. No GPU devbox remains for this effort. Public GitHub CLI account remains `zianglih`.

Publication verification: upstream PR #5319 is OPEN and draft at `ca2692a62679336301758d1b83b193b3c5b1170c`; its title, exact body, and five-file CuTe-only diff were read back from GitHub and verified. See `w4a16-extension/artifacts/published-pr.json` from the project root.


Full audit and cleanup published at `11b786f6fdda99d22eea62afbb82aab5cd5c412f`; PR remains OPEN/draft, exact body and five CuTe files verified from GitHub. Runtime logic is unchanged from measured `ca2692a`. Detailed audit: `audit/README.md` from the project root.


Ready for review: PR #5319 at `f9dd3c10541e087b716772245a9d033499745048`. Added the earlier CUTLASS benchmark finalize-flag wiring fix, accurate help/status, eight passing host-side mocked-GPU CLI-to-backend cases, and passing hooks. Six files total: five CuTe sources plus `benchmarks/bench_moe_deepseek.py`. No GPU rerun. Added to upstream W4A16 tracker #4561; both PR ready status and exact tracker body verified.
