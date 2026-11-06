# Fresh cleanup-head performance and publication plan

Read-only audit, 2026-10-30. No benchmark, remote write, repository edit, commit, or PR update was performed by this audit. `inventory.json` pins the existing evidence/harness files, all 31 job definitions and baseline fields; `frozen-choices.json` records all 468 routing/tactic choices. The final cleanup and output-format changes are now committed as `326c4a793085e79b64b9c7fd79e77320c220ccba`; runtime qualification remains owned by the GPU agent. Publication builders are under `cleanup-20261030/performance`.

## Existing publication boundary

- Upstream PR7290 publication receipt: source head `658a0c8942c7454050f990c0be3083aa61b6a89f`, body SHA `26733b1161219c48ca1a1aa3603f940032ea9d7d801209c5119b4850a78c9f26`, 48,790 bytes.
- Its split performance is older: 364 swap cases at `b52e4e09649dc180fc7583a25ec35ff55f04654d` plus 104 W4A16 cases at `1e4b127a0901282bda5faec70ef6d5a19c835943`. Do not relabel these as current cleanup measurements.
- The authoritative published comparison rows are `upstream-integration-20261029/performance/external/{ep,tp}/summary-cells.csv`. Reuse their `model,tokens,column,baseline,status,baseline_ms,reason,baseline_evidence` fields unchanged; update only candidate latency/evidence and derived speedup.
- Baselines: TRTLLM same dtype; old non-swap `e2728a290`; pre-PR W4A16 `002529e1` with its legacy layout. Non-swap MX uses required fused finalize (†); candidate remains unfused. No TRTLLM BF16 column. Historical controls were measured on other B300 instances, so this refresh is not a new same-GPU baseline comparison.
- Keep the already published GLM5 MegaMoE section and its artifacts unchanged. This requested full refresh is the split-MoE EP/TP matrix.

## Frozen matrix and choices

See `matrix.md`: 31 jobs, 36 supported model/topology/backend arms, 13 token counts and 468 candidate cells. Tokens are `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. Run all; show only 4+ in tables/plots/aggregates (396 candidate cells). Two fresh A passes of 100 samples give 93,600 candidate CUPTI samples and 62 complete process phases.

Presets are V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, N3U EP8/TP8. K3 MXFP8 and V41F TP MX are skipped because neither historical comparison supports those contracts. All other current matrix cells, including both N3U MX modes, remain required. The rejected A/B ownership candidates' 8-byte local-allocation failures do not turn retained-source N3U into unsupported cases.

`element-scale-ownership-20261029/frozen-inputs/<job>/expected.json` supplies the original full-token route and winner identities. These match the published 31-job matrix. There are **458 explicit choices and 10 recorded W4 defaults**, not merely the seven defaults in the recent 24-cell extension:

- EP: V3 8192; V41F/K3/N3U 16384.
- TP: V3/K3 16384; V41F/N3U 8192 and 16384.

For those exact cached `-1` choices preserve `-1 → None → DEFAULT_W4A16_MOE_TACTIC`. The unchanged default is FC1/FC2 `((256,128,256),(2,1),True)`; the boolean is raster order. Preserve actual resolved tiler/cluster/raster/CLC/PDL and compiled-library joins using `broader-harness/w4_resolution_observer.py`. Do not substitute explicit tactics or accept an unexpected miss/default.

## Reusable execution harness

Reuse the candidate-only A-A structure from `fc1-gather-20261028/optimization-next-20261029/retained-control128-full/run_perf.py` and its W4 full refresh counterpart. Bring forward the current source manifest checks, runtime adapters and W4 default observer from `element-scale-ownership-20261029/broader-harness`; do not launch the old historical config or the rejected C-A-A-C experiment source.

The existing GPU owner confirmed the current eight-B300 node uses `nvcr.io/nvidia/pytorch:26.05-py3`. Record its actual CUDA/driver/PyTorch/CuTe/CUPTI identities and GPU UUIDs in the new run. No new devbox is required for this plan. Keep clocks unchanged, sample NVML quartiles, and retain missing/low-clock windows and repeat spreads in the report.

Cache handling is important: use the current `element-scale-ownership-20261029/rebound-cache/<job>` with its hash-bound import proof. The original 1,424 entry files were copied byte-identically into the honestly observed runtime namespace; seven MX jobs additionally preserve `measure_execution_mode=cuda_graph`. Keep `cache-rebind/receipt.json` and `cache-rebind/policy-receipt.json` with the new campaign. Extend native read-only lookup/preload verification from the selected screen tokens to all 468 choices, including the ten defaults. Do not fake runtime versions, rewrite entries, retune, or fall back after misses.

Retain source-specific persistent FlashInfer C++/CuTe/driver caches and stable data include paths. Avoid instrumentation compiler flags in the timed campaign. Existing source-bound driver guards run before launches, with current 128/128/248 swap and 80/64/144 W4 policy. Guard numerical/resource failures before timing; any incomplete job remains visibly incomplete rather than substituting historical candidate values. A local allocation is not automatically proven spilling.

Per-job operation after the final source, harness and config are frozen:

```bash
python run_perf.py --config perf-config.json --job ep-v3-w4a4 --gpu 0
```

The driver invokes the public benchmark through the strict-CUPTI observer, with these benchmark arguments (the observer supplies the existing W4A4-only or W4A16-only selector when appropriate):

```bash
python benchmarks/bench_moe_deepseek.py \
  --functional-api --model v3 --ep 8 --tp 1 --quant-family nvfp4 \
  --backends cutedsl --swap-ab --no-fused-finalize \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 \
  --include-activation-quant --cache /path/to/frozen-winners \
  --warmup 10 --iters 100 --no-autotune --output-format both
```

The direct command is a reproduction of benchmark configuration, not a substitute for the source-bound observer's no-event-fallback guarantee. Per-token jobs select `cute-dsl-per-token`; MX selects `cute-dsl-w4a8,cute-dsl-mxfp8` (K3 only the first), `--quant-family mxfp`, and omits initial quantization. NVFP4 includes the input quantizer; W4 consumes BF16 directly. Preserve per-token MSE4over6,256scale,error-fast-math recipe and base FP4 fast-math disabling exactly.

The output-format owner has now frozen benchmark SHA `0d1d6c8bc4aa4d6305c2576c9af6cfc41986479779bb5f9310c0fffbc82c2409`, with 63 CPU formatting checks and unchanged measurement-call AST. The peer diff review found no blocker. Use `--output-format both` after it joins the final qualified commit: preserve the exact CSV plus native table stdout as an artifact, and publish a compact Markdown table view of the actual printed candidate values. Do not include CSV fences in the PR body.

## Qualification and completion gates

Update: the M512 artifact boundary is resolved. Root reports36 candidate exact smokes and92 existing tests passed,16 control/codegen cases executed, and150 sanitizer cases collected only; no sanitizer was run. The GPU owner is finalizing codegen comparison/source receipts before full performance starts. Bind final qualification to unchanged kernel hashes in326c4a79, and do not present collection as execution.

For every fresh phase verify the full source manifest against the committed tree, benchmark/observer hashes, public functional API, `swap_ab`, unfused finalize, routes, backend set, unchanged key/runner/tactic, zero tuning/admitted candidates, cache bytes, compiler policy, same physical GPU within the A-A job, and 100 positive strict-CUPTI durations. Recompute activity-span durations and phase medians from raw data. Include initial quantizer flags and source-bound resource receipts. Never sum overlapping component kernels to obtain E2E.

Require all 31 complete jobs/468 unique cells before claiming a full refresh. A1/A2 are independent new processes; candidate latency is `sqrt(median(A1) * median(A2))`. Speedup is `100*(historical baseline/candidate-1)`. Bands remain decode4–64, middle128–512, prefill4096–16384. Keep all negative results; spreads are repeat variability, not confidence intervals.

## Publication changes required after data arrives

1. Create a new project-local report and immutable artifact prefix for the new committed head. Do not overwrite historical raw reports or baseline assets. Adapt the retained full assembler to refresh all468 rows, with one current `candidate_measurement_head` and zero reused candidate cells. It currently contains 104-only update/reuse assertions and an obsolete checkout path; those cannot be reused literally.
2. Recompute both nine-column external tables from unchanged baseline fields. Preserve all936 comparison entries including 1/2 in downloadable evidence; display792 entries (44rows×9columns×2topologies), of which660 have supported comparisons. Rehash baseline-field projections before/after.
3. Adapt `upstream-integration-20261029/performance/assemble_stats.py`: remove its hardcoded historical two-head set, historical byte-equality source and stale prose. Reuse its validation, supported-comparison mapping and geometric aggregation, with new report bindings.
4. Replace `export_public_data.py`'s hardcoded historical CSV-log parser/output with source-bound final-pass **table view**. Show the16 model/topology/family groups directly without folds, compact names and all13 token rows; V41F TP MX remains an explicit unsupported panel. Preserve complete stdout/JSON including1/2 in downloadable artifacts. Tables show individual final-pass values, labeled distinctly from two-pass geometric comparison medians. Do not rerun baselines to fill raw table columns or label old values as fresh stdout. If grouping separate job outputs, say they are grouped from the final pass rather than one literal contiguous log.
5. Reuse `plot_speedup_table.py` with fresh external CSVs; preserve red/white/green, common0.5–2.0ratio scale,44rows×9columns, compact V3/V41F/K3/N3U labels, and fused† markers. Render EP/TP PNG/SVG and visually inspect both.
6. Update `build_body.py` to the measured cleanup head, new sample/spread/clock counts, qualification receipts and table raw output; remove the stale not-remeasured/revert caveat. Preserve the GLM5 section, templates and historical-baseline limitation. Existing body is48,790B, with20,313B of rawCSV; verify new tables keep it below65,536B. The exact 31 native family tables exceed the PR limit: their 4+ data rows alone occupy at least 71,885 bytes before headers. The local sizing-only preview `raw-table-size-preview.md` instead groups every printed candidate latency/TFLOPS value into 16 compact Markdown tables, drops only unselected baseline columns and repeated setup, and preserves all 396 displayed values. At 12,361 bytes it projects a 40,838-byte body, with the GLM5 section retained. Latest user steering removes both numerical speedup tables from the body: keep them as downloadable artifacts and keep heatmaps prominent. This preview uses historical data strictly for sizing, not final publication. Link byte-for-byte fresh stdout, including native wide tables and1/2, as a separate artifact.
7. Adapt the asset publisher to a new prefix and new receipt path; do not rerun the existing script that asserts assets.json is absent and has a historical fixed prefix. Root owns GitHub writes, `zianglih` identity, uploads, PR edit, exact body/asset readback and final head verification.

No current performance result is claimed by this plan. The stale candidate rows remain published until fresh measurements and independent audit complete.
