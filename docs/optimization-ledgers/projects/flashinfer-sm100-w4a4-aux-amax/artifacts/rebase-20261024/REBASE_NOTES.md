# PR #4824 refresh — October 24, 2026

Current source: `3363d5d65d390f9a10e856981a241bb6c071568e`. Measured feature commit `e40fad018174232e26d97a69c66dd60e1ddfb59b` is directly on upstream `03f82fddadaebed69879b4e7d28f3df38c4e28d2`; the current head rebases both the feature and 11-line cleanup onto upstream e734816171909b755ed1a9a510b7178d23bdf692. The original six-commit branch is preserved at `backup/pr4824-pre-rebase-20261024` (`b6e4cdad`), and the preliminary four-token policy at `backup/pr4824-min4-20261024` (`e07d67af`).

## Current implementation

- Reuse GEMM1 maxima from rounded FP16/BF16 output in native blocked-8 layout; preserve maxNum NaN/zero behavior and packed-output exactness.
- Preserve the current standalone register-resident/streaming quantizer, CTA selection, output-scale folding, explicit 4over6 recipe, PDL ordering, persistent JIT cache and positional API. New auxiliary inputs are keyword-only.
- Restrict the producer to SM100/SM103. Preserve the generic dispatcher, Rubin localization, existing partial-N rejection and tuner fields.
- Bound the consumer with the device routing extent; inactive rows remain untouched. Unbounded calls initialize swizzled scale padding like upstream.
- Use auxiliary maxima from 512 input tokens. Smaller batches retain standalone quantization. Tests cover 511/512 and retain small-shape algorithm coverage independently of the performance gate.

## Validation

All selected-file pre-commit checks passed, including mypy and Ruff. The combined focused and existing interface selection passed at the measured commit `e40fad01`:

```text
105 passed, 830 warnings in 60.07s (0:01:00)
```

Full output: `gpu-tests-final.log`. Static output: `pre-commit-final.log`. Exact nine-file manifest: `source-manifest-final.json`; patch and bundle: `rebased-final.patch`, `candidate-final.bundle`. No B200/SM100 runtime, sanitizer, full-suite, multirank, or model-level claim is made.

## Cleanup validation at 3363d5d6

Removed the new tuner cache-schema constant/extras and the new auxiliary-output parameter/forwarding on the deprecated `_nvfp4` dispatcher alias. `tuner.py` is byte-identical to current upstream; the deprecated alias AST also matches upstream. All seven other feature files are byte-identical to e40fad01, and the dispatcher AST excluding that alias is unchanged. No new stale-contract support remains in production. The current upstream recipe-default semantics in shared test preparation remain intact.

The two-file pre-commit selection passed, including mypy/Ruff; `git diff --check` passed. See `cleanup-source-audit.json`, `cleanup.patch`, `pre-commit-cleanup.log`. No GPU rerun was performed for this cleanup or the final rebase. The new upstream commit e7348161 changes only QSA decode files, with no overlap in MoE/benchmark paths; `cleanup-rebase-range-diff.txt` confirms identical feature and cleanup patches. All feature files are byte-identical before/after that rebase. The measured source is retained locally at backup/pr4824-measured-20261024 and in candidate-final.bundle, and the reproducer explicitly fetches its SHA. Fresh AUTO used no prior tactic-cache loads, so removing a cache-key suffix does not alter the measured CUDA work; raw measurements continue to name e40fad01. Saved cache snapshots remain evidence only and are not loaded by the reproducer.

At e40fad01, GitHub pre-commit passed. PR Test run40153148645 stopped at the run-ci authorization gate with GPU jobs skipped; its red summary is not a GPU test failure. See `ci-pr-test.log`. The devbox was deleted after all evidence was copied locally; `devbox-cleanup.log` records resource deletion.

## Final deterministic-RL performance

The complete final campaign follows PR #7196: native routing plus W4A4 MoE, independent normal AUTO in four serial processes ordered before R1 → after R1 → after R2 → before R2, 10 configured dry runs and 100 cold-L2 CUDA-graph CUPTI samples per row. The native timer's initialization/estimation warmups remain intact; its 2×L2 flush is outside the measured graph GPU span. No timer fallback or cross-process tactic-cache loading occurred.

All 52 medians reproduce from 5,200 samples. All source hashes were checked against exact Git objects; cache hashes, routing histograms, shared runtime/recipe, and process order passed independent audit.

| Scope | Geometric speedup | Geometric latency reduction |
| --- | ---: | ---: |
| All 11 included points | 1.056478× | 5.346% |
| Decode T4–512 | 1.001315× | 0.131% |
| Prefill T4096/T8192/T16384 | 1.218895× | 17.958% |

T1/T2 are reported and excluded from the aggregates. T512 and all three prefill points improve in both repeats with identical complete tactics across all four runs. Small batches are effectively at parity; tiny T8/T16/T128 geometric regressions have mixed repeat signs. Two repeats do not establish statistical significance.

Current results, raw samples, medians, full selected tactics and source/runtime evidence: [final campaign](pr7196-deterministic-rl-final/summary.md). Only this new complete min512 campaign enters the current PR tables; results remain attributed to measured commit e40fad01.

The preliminary min4 campaign at e07d67af showed regressions at every T4–256 point in both repeats, including T8 with identical tactics. It motivated the 512-token threshold and remains separately archived in `pr7196-deterministic-rl/`; it is not combined with final rows. Both baseline repetitions were also rerun for the final campaign. August evidence and the unused warm-cache helper remain historical only.

## Workload and environment

H7168/I2048, 256 experts, top-k8, groups8/top-groups4, routing scale2.5, seed42, bias scale0.01; single-GPU EP8/TP1 simulation with 32 local experts at offset0. Initial activation quantization, weight preparation, allocation, compilation, tuning and communication are outside the timer; routing, intermediate quantization and deterministic finalize are inside.

Explicit `NVFP44Over6Config(e4m3_max=256, err_mode="MSE", err_use_fast_math=True)`, `FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1`, matching FC2 scale1/1536, unfused finalize and async memset disabled. The identical benchmark-only adapter preserves native input generation/routing/AUTO/timer and supplies the current explicit recipe contract.

One B300 SXM6 AC, driver595.91.07, image `nvcr.io/nvidia/pytorch:26.05-py3`, digest `sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`; CUDA13.2, nvcc13.2.78, imported CuTe DSL4.8.1, TVM-FFI0.1.15.post0, CUDA Python13.2.0, CUPTI Python13.4.0/library13.4.58. Runtime Torch reports `2.12.0a0+5aff3928d8.nv26.05`, while distribution metadata is `2.12.0a0+5aff3928d8.nv26.5.50603568`. The inherited `CUTLASS_DSL_VERSION=4.4.2` is stale environment metadata.

The live NGC catalog was checked before allocation: 26.05 was the newest CUDA13.2 image; 26.06/26.07 use13.3 and 26.08/26.09 use13.4. References: https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch and https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-05.html .

The bare devbox was created with managed `/usr/local/bin/h`, c2/infra after ziangli quota was unavailable, with no size override. The unused queued ziangli request was deleted. Runtime setup logs and both benchmark campaign logs are retained.

## Reproduction

The exact frozen runner is at the project root: `bench_pr7196_deterministic_rl.py` (SHA256 `f39f104974167b8f92096a95bbabf55eb53a71b09b88720a258c183504f0dec8`). The final launch sequence is `scripts/run_pr7196_deterministic_rl_final.sh`. `PR_BODY.md` contains the complete runner and portable setup/launch commands. Its embedded runner hash, shell syntax and preserved experimental template were checked.

```bash
python3 scripts/summarize_pr7196_deterministic_rl.py \
  artifacts/rebase-20261024/pr7196-deterministic-rl-final \
  --require-evidence --after-head e40fad018174232e26d97a69c66dd60e1ddfb59b
```
