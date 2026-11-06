# Held whole-chain performance reuse plan

Status: native/source/26-reference-test gates passed and root released the screen. All42 cache choices/routes passed native lookup. The two K3 CuTe-only jobs completed on GPUs4/5 in a separate immutable six-cell leaf while one shared TRT binding warms; the six remaining combined jobs are held only for that native-cache preflight. Original42 plan and complete four-phase CAAC per job are preserved. See `performance/subset-proof.json` and the launch receipts.

## Smallest meaningful screen

Reuse the existing per-token selection in `audits/quantizer-scalar-hoist/reuse-plan.json`: tokens **32, 4096, 16384**, four models, EP and TP. V3/K3/N3U use EP8 or TP8; V41F uses EP4 or TP4. This supplies 24 CuTe cells. Add the same three token counts for the six supported TRTLLM per-token model/topology arms: another 18 cells, **42 total / 16,800 CAAC samples**. K3 SiTU TRTLLM PER-TOKEN stays unsupported, not a missing measurement.

Use the existing four-phase controller/report machinery from `experiments/alpha-prefetch/performance/` and `harness/{run_perf,observe_benchmark,analyze_perf,report_evidence}.py`: 100 samples, 10 warmups, graph replay, cold L2, strict CUPTI/no fallback, unchanged route and winner checks, all negatives and clocks preserved. Source is retained c1ac versus the qualification owner's single paired-error overlay. Do not create another source copy or add an optimization/tuning axis.

The benchmark already supports both arms directly:

```sh
python benchmarks/bench_moe_deepseek.py \
  --functional-api --model nemo3-ultra --ep 1 --tp 8 \
  --quant-family nvfp4 --backends cute-dsl-per-token,trtllm-per-token \
  --num-tokens 32,4096,16384 --cache <frozen-cache> \
  --swap-ab --no-fused-finalize --include-activation-quant \
  --warmup 10 --iters 100 --no-autotune --output-format both
```

This is an entrypoint illustration, not a launch instruction. The existing observer supplies strict CUPTI and source/tactic/route receipts. For K3 select `cute-dsl-per-token` alone.

## Existing frozen inputs

- CuTe: `harness/frozen-inputs/{ep,tp}-{v3,v41-flash,kimi-k3,nemo3-ultra}-per-token/expected.json`; current remote managed caches are `harness/rebound-cache/<same-job>`. `harness/jobs-full.json` and `experiments/alpha-prefetch/performance/plan.json` retain the exact model/topology/job definitions. The former canceled scalar-hoist plan already enumerates all 24 selected identities.
- TRT source index: `publication-w4-tail-cutoff/completed-tables/baseline-index.json`. Under sibling project `flashinfer-w4a4-split-dynamic-n`, EP raw choices/results are in `optimization-20261027/retained-rerun/evidence/runs/<model>/nvfp4/{swap-ab-native-auto.json,a2/results.json}`. TP choices/results are in `optimization-20261028/tp-ep-post-sanitizer/evidence/runs/tp/<model>/nvfp4/{trtllm-managed-cache,c2-trtllm/results.json}`. These files exist locally; current remote namespace/cache admission is not yet qualified.
- All 78 saved supported TRT routing identities (six arms × 13 tokens) were compared with the corresponding CuTe frozen inputs and are identical. Reuse the selected records, not rendered tables or regenerated routes.

| TRT arm | T32 recorded choice | T4096 | T16384 |
|---|---|---|---|
| V3 EP8 | `[8,18]` | `[128,29]` | `[128,1]` |
| V41F EP4 | `[8,26]` | `[128,10]` | `[128,26]` |
| N3U EP8 | `[8,26]` | `[256,0]` | `[128,1]` |
| V3 TP8 | `-1` | `[128,11]` | `[128,11]` |
| V41F TP4 | `[8,26]` | `[128,2]` | `[128,27]` |
| N3U TP8 | `[8,56]` | `[128,15]` | `[128,15]` |

The single recorded TRT default is not permission to autotune. Current `core.py:3779` maps `-1` to native `[-1,-1]`; preserve that cache hit and establish the same default/native choice for both sources before timing it. Other selected TRT points have explicit two-element choices.

## Bounded runner adaptation, only after release

The observer and arm contracts already support TRT, both quantization stages, cache-hit recording and strict CUPTI. Reuse them. The old replay driver is CuTe-only in its expected-input and register-guard assumptions; do not pretend it runs TRT unchanged.

Use the eight existing model/topology jobs, adding the TRT selector for six of them. Supply expected winner records per backend from the two existing sources; preserve their origins rather than fabricating a historical joint measurement. Import the existing selected TRT entries alongside the CuTe entries into each job's managed cache with honest current metadata, preserving keys/choices/policies. No retuning. The small driver adaptation must compare each backend against its original record and permit only the explicitly recorded TRT default above. CuTe GEMM resource checks remain required; quantizer native qualification and source-bound per-arm caches cover the changed helper. Reuse the qualification owner's per-arm quantizer cache isolation while retaining the common immutable release C++ assets; do not share one writable quantizer object family across source arms.

## Exact comparison boundary

- The shared Python helper changes **CuTe PER-TOKEN initial and intermediate quantization**. Its whole-chain numerator must be freshly measured.
- `bench_moe_deepseek.py:1220–1232` calls the public **CuTe** quantizer for **TRTLLM PER-TOKEN initial activation**. `run` invokes it inside timing when `--include-activation-quant` is present. TRT's C++ intermediate quantizer is distinct and unchanged, but its whole-chain denominator still changes. The bounded screen therefore needs 18 fresh TRT cells. A later full-table refresh would need all **78 supported TRT PER-TOKEN rows**; K3's 26 rows remain N/A.
- Standard TRT NVFP4/W4A4, TRT BF16/MX, and W4A16 do not use this error-helper specialization in the current benchmark. Their historical denominators are not silently relabeled or rerun by this plan.
- A **current-source non-swap CuTe per-token** comparison also changes initial activation quantization, so it cannot be called an unaffected current-code denominator. The original frozen legacy/PR-head snapshots remain historical and untouched. Root decides any additional current-legacy measurement/publication only if the candidate is retained.
- Report candidate-versus-control gains separately for each backend, then any fresh cross-backend ratio. Do not divide the candidate CuTe result by an old TRT per-token latency and call it the current backend gap. All original published/raw historical data stays unchanged.
