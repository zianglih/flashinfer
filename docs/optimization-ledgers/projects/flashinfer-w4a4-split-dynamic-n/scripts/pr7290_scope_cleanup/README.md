# Raw benchmark tables for PR #7290 scope cleanup

The original V3 table run is archived at `evidence/pr7290-tables-r1`: MX completed; NV was interrupted at the user’s request to skip CUTLASS. Its deployed helpers and raw partial evidence remain unchanged. New runs use the model helpers described below.

`run_tables.py` runs the public `benchmarks/bench_moe_deepseek.py` CLI in two fresh processes. Its default launches NVFP4 on physical GPU0 and MXFP on GPU1 in parallel. Both use the final isolated source clone, simulated EP8/TP1, the 13-token grid, native AUTO, 10 warmups / 100 cold-L2 CUDA-graph CUPTI iterations, and no initial activation quantization or per-token activation scaling. CuTe DSL and CUTLASS fused finalize are disabled; TRTLLM retains its native finalize.

The NVFP4 invocation retains the script's complete default table. The MXFP invocation retains all five requested backend columns: CuTe DSL MXFP4xMXFP8, CuTe DSL MXFP8, TRTLLM MXFP4xMXFP8, TRTLLM MXFP8, and TRTLLM BF16. Both tables include three speedup groups, one for each comparison backend. No `--backends` filter or profiler instrumentation is used.

## Launch after deployment

Copy this directory to the same path under `/workspace/flashinfer-w4a4-split-dynamic-n` and use the final clean source clone and its full commit SHA. The root task owns deployment and launch authorization. This helper never edits the source clone or the measured/frozen source copies.

```bash
source /workspace/flashinfer-w4a4-split-dynamic-n/scripts/recovery442/env_candidate.sh
/workspace/flashinfer-w4a4-split-dynamic-n/.venv/bin/python \
  /workspace/flashinfer-w4a4-split-dynamic-n/scripts/pr7290_scope_cleanup/run_tables.py \
  --repo /workspace/flashinfer-w4a4-split-dynamic-n/pr7290-scope-cleanup \
  --expected-head FINAL_COMMIT_SHA \
  --output /workspace/flashinfer-w4a4-split-dynamic-n/results/pr7290-scope-cleanup \
  --image nvcr.io/nvidia/pytorch:26.05-py3
```

Use `--dry-run` to print commands without importing CUDA, accessing a GPU, or creating result files. `--family nvfp4` or `--family mxfp` permits a separately recorded invocation if only one table needs rerunning. Each real invocation requires a new output directory and refuses an occupied selected GPU.

The sourced environment retains the established native compilation workspace and network/proxy environment. Each family gets a private CuTe cache under its output directory. The runner clears inherited autotune timer overrides, tactic blocklists, DA settings, 4over6 recipes, and dump instrumentation; it disables cache-file loading and uses the target checkout as `PYTHONPATH`.

## Output

- `receipt.json`: final source HEAD/tree and source hashes, image, package and CUDA versions, GPU UUID/model/PCI identity, exact arguments and nonsecret relevant environment, timings, exit status, and before/after source identity.
- `{nvfp4,mxfp}/stdout.log`: untouched public benchmark output, including the raw table for the PR body.
- `{nvfp4,mxfp}/stderr.log`: untouched diagnostic output.
- `{nvfp4,mxfp}/command.json` and `command.sh`: exact invocation and relevant environment.
- `{nvfp4,mxfp}/result.json`: exit status, log hashes, and a minimal check that all 13 table rows contain five finite positive backend latencies. Parsed values retain only the public table's display precision; the raw output is authoritative.

Tokens1/2 remain in the raw tables and remain excluded from optimization retention aggregates. These tables are current backend comparisons; they do not replace the archived original-before versus final-after evidence.

## Model and stage-policy runs

The already-deployed `pr7290-tables-r1/run_tables.py` and its commands remain unchanged. New runs use `run_model_tables.py`, `deploy_model_tables.py`, and `observe_table.py`. Their full-table parser expects four NVFP4 latency columns (CuTe W4A4, CuTe W4A16, TRTLLM NVFP4, TRTLLM BF16) and five MXFP columns; CUTLASS is excluded from the default table. Explicit `--backends` output is parsed as the existing CSV format.

Model selector defaults are `--model v3 --ep 8`. Use `--model v41-flash --ep 4` explicitly for the second workload. The benchmark owns model dimensions, activation, routing and quantization settings; the helpers only pass the public selector.

Example local deployment (launch only after coordinating GPU ownership):

```bash
python3 scripts/pr7290_scope_cleanup/deploy_model_tables.py \
  --repo /Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n/flashinfer-pr-scope-review \
  --tag pr7290-v41-stage-baseline-r1 --source-tag stage-baseline \
  --model v41-flash --ep 4 --nvfp4-gpu 2 --mxfp-gpu 3
```

For an existing separate experiment clone, change `--repo`, use a distinct tag/source label, and add `--allow-dirty`. The deployer saves `source.patch`, applies exactly that patch to a new remote clone without staging or committing it, and checks HEAD, tree, patch SHA256, and source-file hashes against the local snapshot. Tracked source changes are allowed only with that explicit patch; untracked source and staged experiment changes are rejected. The runner records both source snapshots and requires identical before/after hashes. A deployment `--dry-run` prints the proposed source snapshot/configuration without any remote call or launch.

Model compiler caches are isolated under `cache/model-stage/{source_tag}/{HEAD}-{patch_sha256}/{model}/{family}`. Repeated C/A runs reuse those compiled artifacts but create fresh native AUTO state with file loading disabled. `repeat_model_tables.py --launch evidence/RUN_TAG/launch.json --tag NEW_TAG` reuses the exact frozen source and staged helper hashes without recloning; optional model/EP/GPU overrides reuse that source for a second workload.

The model runner uses a task-local observer driver. It imports the unchanged public benchmark, wraps `_benchmark_single` only to observe its return value, and calls `main()` with the exact public CLI arguments. After each token's timed work returns, it saves all full-precision `BenchmarkResult` dataclasses, the benchmark's returned routing histogram summary, and an `AutoTuner.save_configs` snapshot. This does not collect individual iteration samples or introduce any work inside the timed region. Public stdout remains the original benchmark table.

New per-family artifacts:

- `observed/results.json`: full-precision native medians/TFLOPS, returned histogram summaries, routing IDs/weights SHA256 and full expert histograms, exact public CLI argv, benchmark/observer hashes and AUTO-cache hashes. The observer retains routing tensors created by the benchmark’s existing untimed histogram call, then hashes them after timing; it never invokes an additional router.
- `observed/token_<N>.autotune.json`: native AUTO cache snapshots saved after each token.
- Top-level `source.patch` and receipt `source` / `source_after`: exact unstaged experiment attribution, separate from Git HEAD.

Fetch any completed run with `python3 scripts/pr7290_scope_cleanup/fetch_tables.py --tag RUN_TAG`; it preserves these observer artifacts as well as untouched stdout/stderr. Use `--allow-incomplete` only to archive a stopped run as incomplete. Both C1 baselines and A1 stage-capacity-r2 screens were launched after explicit root authorization; run receipts remain the source of completion status. A2/C2 repeats require root coordination. Future snapshots use full-index Git diffs, preventing repository object-count differences from changing patch-byte receipts; existing C1/A1 staged helpers are preserved.

## Runtime import provenance

The earlier C/A runners’ `receipt.software.packages` recorded installed distribution metadata and collapsed duplicate names. In this environment, the inherited global CuTe DSL 4.4.2 entry overwrote the actual venv CuTe DSL 4.7.1 entry in that field. Preserve the original receipts; use `evidence/stage-runtime-imports-20261025.json` for the separate post-run import check of the exact timed `.venv/bin/python`: it records module versions and file paths, both distribution locations, CUPTI 13.4.58, and actual `nvidia-smi` driver 580.178.04. The import probe did not initialize CUDA and did not alter a benchmark process. Final clean-source table runners instead query the selected distributions and also record actual imported CuTe/Torch versions, module file paths, interpreter prefix and hostname directly in each run receipt.

### Shallow experiment snapshots

When a frozen experiment checkout lacks the historical bundle base, pass
`--bundle-repo flashinfer-pr-scope-review` to `deploy_model_tables.py`. The donor
must have exactly the experiment's HEAD and contain the bundle-base ancestry.
Only committed Git objects come from the donor; the tracked patch and all source
hashes are captured from the experiment, and the remote copy is verified against
those hashes. This leaves the frozen experiment checkout untouched. The failed
first depth2 packaging attempt is preserved under
`evidence/pr7290-v3-clc-depth2-a1-packaging-attempt` and launched no remote work.

`summarize_auto_choices.py` joins all four saved native AUTO selections to the
already audited paired medians. It keeps every point in JSON, expands changed
choices and prefill points in Markdown, and records the exact cache file hashes.
A changed choice is an association with a timing change, not causal evidence.

### Replacement-host iteration after `0c1e00fc`

The completed `pr7290-{v3,v41}-clc-final-tables-r1` runs remain the final public
table evidence for B200-92. On the next iteration, the devbox was no longer
present. Do not use those old-host medians as paired-retention denominators for
a replacement GPU. Preserve them and create fresh clean-`0c1e00fc` controls on
the replacement host, using the same native AUTO observer and token grid.

The deployment helper accepts explicit `--devbox`, `--cluster`, and
`--namespace` and records them in its launch receipt. Repeat and fetch inherit
that connection, with optional explicit overrides. Historical receipts without
a connection retain the old `fi-w4a4-narrow-1025/c1/ziangli` defaults. The
benchmark runner and observer are unchanged by this transport adjustment.

The new controls use V3 EP8 on GPUs4/6 and V4.1-Flash EP4 on GPUs2/3. Select
`--nvfp4-backends cutedsl` and
`--mxfp-backends cute-dsl-w4a8,cute-dsl-mxfp8`; W4A16 remains an unaffected
noise observation. Use all13 tokens, 10warmup/100iterations, native AUTO,
cold-L2/CUDAgraphs/CUPTI, PDL on, unfused finalize and no initial quantization.
Tokens1/2 are reported but excluded from retention. Await root coordination
before a candidate launch or closing repeats. No original `a65` rerun.
