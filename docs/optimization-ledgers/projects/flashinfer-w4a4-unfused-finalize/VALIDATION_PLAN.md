# CuTe DSL W4A4 unfused-finalize validation plan

Implementation source audited: `flashinfer/` at upstream main `eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095`.
The runtime will use `0.7.0.dev20260917`, commit `d233e27ddddbcfdc24eec38ab4dffda1f43ff49c`, with matching nightly Python/AOT/cubin packages. The parent task verified that the W4A4 FC2 source and `fused_moe.py` match main. To avoid unrelated newer W4A16 tests, use the **unmodified nightly test snapshots** in `validation/native_tests/`, whose source revision and SHA-256 hashes are in `SOURCE.json`. `validate_pdl.py` imports the installed runtime and loads these helpers directly; it does not add the main clone to `PYTHONPATH`.

This document records proposed validation, not executed GPU results. The audit did not modify repository source or run GPU work.

## Native correctness tests

All selectors below are in the unmodified nightly `validation/native_tests/test_cute_dsl_fused_moe.py`. They retain the native accuracy thresholds. Parameter IDs were derived from the checked-in decorators and explicit IDs; confirm collection on the GPU environment before running. No custom pytest plugin or monkeypatch is required for these native checks.

| Native selector | Focused cases | What it establishes |
| --- | ---: | --- |
| `TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy` | 4 | Unfused functional reference checks: W4A4 per-tensor SwiGLU, W4A4 per-token ReLU2, and W4A16 SwiGLU/ReLU2 controls; includes 515-token partial rows and top-8. |
| `TestExpertParallelism::test_functional_with_ep` | 6 | EP8, 32 local experts out of 256, local offset 128, top-8, 256 tokens; W4A4 per-tensor/per-token and W4A16, each with fused and unfused finalize. |
| `TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-MODE-FINALIZE]` | 6 | 64 tokens, 256 experts, H256/I512, top-2; all three precision/scaling cases and both finalize modes. The unfused arm requires bitwise-identical outputs across three graph replays, then checks the numerical reference. |
| `TestCuteDslMoEWrapper::test_wrapper_accuracy[256-8-MODE-FINALIZE-128]` | 6 | Eager wrapper, 128 tokens, 256 experts, H256/I512, top-8; all three precision/scaling cases and both finalize modes. |

This bounded selection is **22 parameterized cases**, subject to ordinary device/DSL availability skips. Report passed/skipped/failed counts from the actual run. Do not report skips as coverage.

From the project root (outside the source checkout), use Bash so imports resolve to the prepared nightly runtime:

```bash
set -euo pipefail
test_file=validation/native_tests/test_cute_dsl_fused_moe.py
selectors=(
  "$test_file::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy"
  "$test_file::TestExpertParallelism::test_functional_with_ep"
)
for quant_case in w4a4-per-tensor w4a4-per-token w4a16; do
  for fused in False True; do
    selectors+=(
      "$test_file::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-$quant_case-$fused]"
      "$test_file::TestCuteDslMoEWrapper::test_wrapper_accuracy[256-8-$quant_case-$fused-128]"
    )
  done
done
CUDA_VISIBLE_DEVICES=0 python -m pytest --collect-only -q "${selectors[@]}"
CUDA_VISIBLE_DEVICES=0 python -m pytest -v -ra "${selectors[@]}"
```

Native coverage references in the nightly test snapshot:

- Scaling case IDs: lines 168–172.
- Deterministic reference cases: lines 1530–1600; numerical helper: 1654–1729.
- Wrapper eager cases: lines 2027–2102.
- Wrapper graph cases: lines 2174–2304. Unfused equality assertion: line 2284. The graph test uses parameterized SwiGLU constants, not only default SwiGLU.
- EP8 functional cases: lines 2748–2824.
- `CuteDslMoEWrapper` and functional APIs default `enable_pdl=True`: `flashinfer/fused_moe/cute_dsl/fused_moe.py:593` and `:1149`. Thus the selected checks execute the production PDL-enabled path unless runtime setup overrides it.
- `tests/moe/utils.py:1210–1230` uses the existing FP4 reference criterion: at least 97% of outputs pass either absolute error `< max(0.05, 1.5 × reference_std)` or relative error `< 0.5`. Preserve this criterion, but do not describe it as strict before/after equivalence.

## PDL-specific correctness gaps

The native selection covers the changed path but is insufficient by itself to establish that an FC2 synchronization change preserves all outputs:

1. **No W4A4 PDL-on versus PDL-off equality test.** The selected tests use the default PDL setting. The explicit `enable_pdl=False` cases in this file are W4A16 or W4A8, not a matching W4A4 on/off pair.
2. **No combined unfused EP8 graph check.** EP8 is tested eagerly, while the graph reference/equality case uses all local experts. Validate the combined EP8 + graph + unfused setting if the implementation changes dependency ordering across FC2 and reduction.
3. **W4A4 cluster-padding native cases are fused-only.** Nightly `test_finalize_handles_cluster_padding_and_partial_tiles` at lines 1602–1652 has `use_fused_finalize=True`. It is a useful fused-path control, not an unfused-tail test.
4. **Tiny sparse routes and production dimensions.** The chosen native unfused cases start at 64 tokens; they do not establish correctness at 1–32 tokens or H7168/I2048. The performance harness does not check output accuracy.
5. **No exhaustive tactic coverage.** Native accuracy checks usually dispatch the default tactic; native performance autotunes. A PDL-only change should also be checked using the exact tactics selected in performance runs, especially both one-CTA and two-CTA FC2 variants affected by the patch.

The external synchronization harness `validation/validate_pdl.py` covers W4A4 per-tensor and per-token; fused=False; EP8 offsets 0 and 128; eager and graph; tokens 1, 3, 16, 128, and 4096; H256/I512. It pins the same explicit native default tactic (or a supplied `--tactic-json`) for PDL off/on, checks finite outputs and exact eager/graph/PDL equality, changes activation and routing buffers in place, then restores the initial values and checks replay again. Every phase has at least one local route even at one token. Four-local-route and one-local-route phases change routing density to exercise sparse local work. It saves canonical CPU outputs and input hashes for an exact matched baseline/candidate comparison.

**Native reference coverage is limited to <=128 tokens** by default for speed, without changing its tolerances. The 4096-token case checks PDL and graph equality plus baseline/candidate equality when `--compare-to` is supplied; it does not run the slow native reference oracle. This boundary appears explicitly in `report.json`. The harness has no performance timer and does not claim exhaustive tactic or production-dimension coverage. A trace should separately establish whether FC2 and the reduction actually overlap.

```bash
# From the project root; prepared baseline nightly runtime active.
CUDA_VISIBLE_DEVICES=0 python validation/validate_pdl.py \
  --output artifacts/pdl-baseline \
  --tokens 1,3,16,128,4096 --offsets 0,128

# Same packages with the candidate CuTe source change active.
CUDA_VISIBLE_DEVICES=0 python validation/validate_pdl.py \
  --output artifacts/pdl-candidate \
  --tokens 1,3,16,128,4096 --offsets 0,128 \
  --compare-to artifacts/pdl-baseline/outputs.pt
```

For smoke validation use the same `--tokens 1,3` on both arms. `--replays` controls semantic graph replays, not repeated performance sweeps. Outputs must use new directories to preserve evidence. `report.json` records package identity, the actual imported FC2 source hash, the fixture revision/hash, every check, and any error. No upstream test file was changed.

## Native performance commands

Use `benchmarks/bench_moe_deepseek.py` from each recorded baseline/candidate revision, with that revision's FlashInfer package actually imported. Record `flashinfer.__file__`, `flashinfer.__version__`, source commit, image tag/digest, GPU, CUDA/PyTorch/DSL versions, and the full command before timing. Do not assume running a copied benchmark implies that the modified package is loaded.

The main A/B comparison is **baseline unfused versus candidate unfused**, separately for W4A4 per-tensor and per-token activation scaling. Fused finalize and W4A16 are controls. The old release benchmark under `../sglang-flashinfer-unfused-finalize-default/benchmarks/artifacts/` used FlashInfer `v0.6.18.post1` and EP1; it provides motivation only and is not the matched baseline for main plus EP8.

Run the following once per baseline/candidate source revision, on the same otherwise idle GPU. Keep one sweep per configuration; do not add repeated or reverse-order runs. `benchmark_output` must refer to the owning project's result directory for the current source revision.

```bash
set -euo pipefail
tokens=1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384
benchmark_output=/path/to/project/artifacts/BASELINE_OR_CANDIDATE
mkdir -p "$benchmark_output"
common=(
  --backends cutedsl
  --num-tokens "$tokens"
  --ep 8 --tp 1
  --warmup 10 --iters 100
  --include-activation-quant
)

CUDA_VISIBLE_DEVICES=0 python benchmarks/bench_moe_deepseek.py \
  "${common[@]}" --no-fused-finalize \
  2>&1 | tee "$benchmark_output/unfused-per-tensor.log"
CUDA_VISIBLE_DEVICES=0 python benchmarks/bench_moe_deepseek.py \
  "${common[@]}" --no-fused-finalize --use-per-token-activation \
  2>&1 | tee "$benchmark_output/unfused-per-token.log"

# Fused controls; these invocations use the native True default.
CUDA_VISIBLE_DEVICES=0 python benchmarks/bench_moe_deepseek.py \
  "${common[@]}" \
  2>&1 | tee "$benchmark_output/fused-per-tensor.log"
CUDA_VISIBLE_DEVICES=0 python benchmarks/bench_moe_deepseek.py \
  "${common[@]}" --use-per-token-activation \
  2>&1 | tee "$benchmark_output/fused-per-token.log"
```

Interpretation and controls:

- `--backends cutedsl` executes only CuTe DSL **W4A4 and W4A16** MoE backends. The native harness cannot select just one of these through `--backends`; `--profile-backend` is restricted to profiler mode.
- `--use-per-token-activation` changes W4A4 scaling. W4A16 consumes BF16 activations and ignores this flag, so label it as the same W4A16 control rather than a separate per-token precision mode.
- Workload: H7168, I2048, 256 global experts, top-8, group count 8, top-4 groups, scaling factor 2.5, seeded random inputs and routing bias scale 0.01. EP8 means 32 local experts on **one GPU**, not an eight-GPU communication benchmark. Local expert offset is zero in the native benchmark.
- `--include-activation-quant` includes initial BF16→NVFP4 quantization for W4A4. Both modes include top-k routing. W4A16 has no initial activation quantization.
- The default wrapper API and production PDL are enabled. CUDA graphs are enabled, CUPTI is requested, L2 is flushed between timed iterations, and the result is the median of 100 samples after 10 warmup iterations. Autotuning happens before timing. Verify actual CUPTI availability and record any fallback.
- Do not pass `--no-autotune` for the primary production-dispatch comparison. Use fresh processes and avoid sharing baseline/candidate tuner caches. If performance shifts because tactics differ, report that fact and use a separate fixed-tactic diagnostic to isolate the FC2 change.
- Latency is GPU elapsed span from the first measured kernel start to the final kernel end. Benchmark output is native CSV embedded after setup/tuning logs. Preserve both absolute timings and raw output.
- Speedup = baseline latency / candidate latency for the **same precision, scaling, EP, finalize setting, and token count**. Report decode 1–128 and prefill 256–16,384 separately, plus the maximum latency regression. Do not aggregate per-tensor and per-token rows or treat W4A16 repeated control rows as additional independent evidence.
- The native CLI has no `enable_pdl` switch. PDL-off diagnosis requires a project-local API harness, not a misleading environment-variable claim.

## Focused profiler follow-up

Only after observing a reproducible target bottleneck, use the native profile mode for a representative slow shape, preserving the same scaling/EP/finalize settings:

```bash
CUDA_VISIBLE_DEVICES=0 python benchmarks/bench_moe_deepseek.py \
  --backends cutedsl --num-tokens 4096 --ep 8 --tp 1 \
  --include-activation-quant --no-fused-finalize \
  --profile-cuda --profile-backend cute-dsl --profile-iters 10
```

Add `--use-per-token-activation` for the per-token case. Run under the available GPU profiler to capture the CUDA-profiler range. Profiling is not a substitute for ordinary benchmark timings, and profiler replay can change scheduling/cache behavior. If comparing traces, preserve and identify the production-selected tactics.

## Completion evidence

Publish only evidence actually obtained: exact tested source revisions; environment/import identity; raw native test outcomes; source-to-CSV row-count and finite-value checks; complete speedup table and commands; and any remaining PDL/graph/EP/tactic gaps. Keep the PR draft as requested and keep non-CuTe implementation changes outside its scope.
