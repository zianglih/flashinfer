# PR #4824 refresh — 2026-10-24

- Restored an independent checkout in the original project folder.
- Original branch: `b6e4cdaddcfb716bf757f343c5cad5823c6dd362`, retained at `backup/pr4824-pre-rebase-20261024`.
- Upstream: `03f82fddadaebed69879b4e7d28f3df38c4e28d2` (1,316 commits after the original base).
- Rebased feature: `e07d67af9339c8ace3791bcea1b6c6614206e5d4`, one consolidated commit.
- Preserved current register-resident quantizer, CTA selection, output-scale folding, explicit 4over6 recipes, generic MoE dispatcher, Rubin localization, and tuner fields.
- Aux inputs are keyword-only after current public positional arguments. Compile/runtime ABIs share tuple construction, with persistent cache specialization for aux and its valid-row bound.
- Fixed the original Rubin guard; aux producer is restricted to SM100/SM103. Current upstream already rejects partial N tiles; no new fallback is needed.
- Unbounded aux quantization now initializes swizzled scale-padding rows like upstream; bounded calls continue to leave inactive rows untouched.
- Tests use explicit recipes and cover FP16/BF16 immediate PDL handoff, GeGLUTanh, output-scale folding, streaming widths, architecture guards, and device-bound CUDA graph replay.
- Selected-file pre-commit passes, including mypy. GPU results and benchmark results are recorded alongside this file.

## Validation environment

Managed `/usr/local/bin/h` with a bare `fi-4824-rebase` devbox in c2/infra after ziangli quota proved unavailable. The queued ziangli request was deleted. No size override.

Live NGC catalog checked before allocation. Releases 26.06/26.07 use CUDA 13.3, and 26.08/26.09 use CUDA 13.4. The newest CUDA 13.2 image is `nvcr.io/nvidia/pytorch:26.05-py3`.

References: https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch and https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-05.html . Exact observed versions and image digest are in `environment.txt` and `image-digest.txt`.

Current correctness command:

```bash
CUDA_VISIBLE_DEVICES=0,1 FLASHINFER_CUDA_ARCH_LIST=10.3a MAX_JOBS=8 \
python3 -m pytest -q tests/utils/test_nvfp4_per_token_input_amax.py tests/moe/test_cute_dsl_per_token_aux_amax.py
```

## Historical evidence

The original README, PR body snapshot, scripts, NCU reports and raw benchmark artifacts are preserved. August timing is not evidence for the rebased branch, particularly because upstream has since introduced register-resident standalone quantization.

## Completed correctness checks

Candidate `e07d67af9339c8ace3791bcea1b6c6614206e5d4` passed:

```text
77 passed, 829 warnings in 483.79s (0:08:03)
26 passed, 21 warnings in 0.41s
```

The first result covers both changed test files. The second covers the existing MoE can-implement suite and tuner-cache, GEMM2 dtype, localization-cache and PDL-forwarding selectors. Warnings are retained in the raw logs. All selected-file pre-commit checks passed, including mypy and ruff. No full-suite, SM100 runtime, or model-level validation is claimed.

## Fresh performance protocol requested by the user

The user requested PR #7196 methodology, deterministic-RL only. The earlier proposed fixed-tactic/warm-cache helper was not run and is not primary evidence.

- Sources: main `03f82fddadaebed69879b4e7d28f3df38c4e28d2` versus candidate `e07d67af9339c8ace3791bcea1b6c6614206e5d4`.
- Order: before R1, after R1, after R2, before R2; four independent processes, one B300, sequential execution.
- Native DeepSeek workload and normal AUTO selection; separate output caches, none loaded across arms. Same physical checkout path preserves native compilation caches across source switches without reusing AUTO selections.
- Token grid: 1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Only 1/2 excluded from retention aggregates; decode 4..512 and prefill 4096/8192/16384 also reported.
- 10 warmups, 100 cold-L2 CUDA-graph CUPTI samples; CUDA-event fallback rejected, distributed-aware timer disabled.
- Row ratio: sqrt((before R1 * before R2)/(after R1 * after R2)); aggregate geometric means, no row minima or replacement by fixed-tactic results.
- W4A4 per-token deterministic-RL: explicit NVFP44Over6Config(e4m3_max=256, err_mode='MSE', err_use_fast_math=True), FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1, unfused deterministic finalize, async memset disabled.
- Identical benchmark-only adaptation supplies the explicit recipe and its matching FC2 scale 1/(6*256). The native benchmark still uses a legacy scale1.0; retaining it would bypass the current explicit-recipe validation. The adaptation is preserved separately from repository changes.
- Initial activation quantization, weight preparation, allocation, compilation and tuning excluded. Routing and intermediate activation quantization included. EP8 is a single-GPU local-shard simulation with no communication.
- CUPTI Python13.4.0 and library13.4.58 installed in the same CUDA13.2 container. Runtime CuTe DSL4.8.1 is shared across both sources; this follows #7196's methodology without claiming its older DSL4.7.1 runtime.

Original performance evidence remains archived locally and will be superseded in the refreshed PR body. No inference configuration will be run or retained as current evidence.

## Measured policy correction

The initial refreshed min4 campaign at e07d67af completed all52medians and5200samples. Independent audit reproduced every median, source hash, cache hash and routing histogram. Overall GM was1.045652007x; decode0.987660268x; prefill1.217491924x. All T4..256 regressed in both repeats, including T8 with identical full tactics across allfour runs. T512 and allprefill rows improved.

The original four-token policy was therefore stale. Final candidate e40fad018174232e26d97a69c66dd60e1ddfb59b raises the minimum to512 and bumps the pipeline cache schema. The originalT2/T4 dispatchcases remain; T511/T512 were added. Small-shape algorithm coverage explicitly forcesaux in its helper, independentof the productionperformancegate. No cases were removed.

The e07d67af source and entire initialcampaign remain archived at backup/pr4824-min4-20261024 and pr7196-deterministic-rl/. They are not mixed into the new campaign at pr7196-deterministic-rl-final/. Both baselines and both candidate runs are freshly measured for the finalpolicy. The frozen benchmark runner SHA256 is f39f104974167b8f92096a95bbabf55eb53a71b09b88720a258c183504f0dec8.
