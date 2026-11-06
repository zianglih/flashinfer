# Gather-pipeline benchmark harness

Control: `82254e206a44b95d9925e4594fac936731f80d21`. Source is read-only here.
The old project remains the authoritative historical evidence store; copied
tables and winner entries retain their original source paths and SHA hashes.
Nothing in `historical/` is a new822 control measurement.

## Matrix and retention

- Models: V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, N3U EP8/TP8.
- Modes: W4A4, per-token NVFP4, W4A16, MXFP4x8, MXFP8. The existing supported
  matrix has36 arms: V41F TP MX modes and K3 MXFP8 have no matching supported
  comparison arm and remain excluded. `jobs-full.json` has31 native jobs.
- Compact: tokens1,2,4,512,16384 →180 measured cells,108 retention cells.
  Every supported arm contributes decode/middle/prefill;1/2 are diagnostics only.
- Final: tokens1,2,4,8,16,32,64,128,256,512,4096,8192,16384 →468 cells,
  396 displayed/retention cells. Do not rerun TRTLLM/non-swap baselines.
- Iterations: control/candidate/candidate/control on the same physical GPU,
  fresh process per phase. Final retained publication: two candidate processes.
- Public `benchmarks/bench_moe_deepseek.py`, functional API, swap-AB,
  unfused finalization,10 warmups,100 CUPTI CUDA-Graph samples, coldL2.
  NVFP4 includes initial quantization; W4A16 directly consumes BF16.
- Frozen recorded choices, including ten existing W4A16 defaults. No retuning,
  event fallback, compiler flags, clocks or tactic axes are introduced.
- Primary phase estimator is geometric mean, matching the latest published
  full table. CAAC output also keeps arithmetic diagnostics and all raw medians;
  older W4-only arithmetic experiments retain their original estimator labels.
- Keep every positive/negative row, both repeat spreads, NVML quartiles and
  missing clock windows. Component extension/gap times account for overlap;
  summing raw FC1/FC2 durations is not end-to-end time.
- Neutral performance plus added kernel complexity is insufficient to retain.

`GAPS.md` and `historical/gaps.csv` rank current external-gap signals. Old MX
fused-finalize comparisons have a structural boundary and are not a causal
measure of the new pipeline. New822 CAAC runs determine retention.

## Files and provenance

`port-provenance.json` records the previous harness source; `local-validation.json`
checks the small orchestration diff and unchanged timing/guard observers.
`frozen-inputs/` contains only routes, choices and original cache entry bytes,
not historical timings. `import_cache.py` rebinds entries to the installed
runtime namespace, preserving profiling-policy fields and every entry byte.
It records all468 successful native lookups and ten explicit default expansions.
Do not bypass that check when the runtime changes.

`configure.py` requires a root-verified `{head, files}` all-file822 SHA inventory, including
native submodules. It supports materialized source trees whose Git directory
may be older than their actual contents. A source record distinguishes the
verified base commit from an unstaged experiment label and records every delta.
Full tracked bytes are verified once at freeze and pre/post campaign; per-process/compile guards check the bounded70-file launch dependency set and every changed file. Existing-file experiments are supported; adding a new imported source file
requires explicitly extending the inventory before freezing.

## Remote preparation

Node: `fi-gather-pipeline-1030`, C2, namespace `ziangli`;8 B300 GPUs.
Requested image: `nvcr.io/nvidia/pytorch:26.05-py3` (CUDA13.2).
Root owns environment/source deployment and resource allocation. Do not run
the following until its source freeze, runtime and numerical/codegen gates pass.

Persistent native workspace already exists:
`/data/ziangli/flashinfer-w4a4-split-dynamic-n/upstream-integration-20261029/megamoe-glm5/cache/cpp`.
Preserve the existing stable `flashinfer/data` symlink target: changing native
include paths rebuilds otherwise identical C++ modules and causes cache lock
contention. Before timing, run `native_preflight.py` once per source with that
same workspace; compare the complete generated Ninja descriptions. Do not
clear caches or change links while a build is active. CuTe cache uses the new
persistent project path with strict source keys; driver cache is persistent too.

Use the managed HAI CLI from the read-only HAI working directory:

```sh
cd /Users/ziangli/playground/repos/hai
PATH=/usr/local/bin:$PATH command -v h
/usr/local/bin/h sync fi-gather-pipeline-1030 -c c2 -n ziangli \
  --source-dir /Users/ziangli/playground/projects/flashinfer-moe-gather-pipeline/harness \
  --remote-path /data/ziangli/flashinfer-moe-gather-pipeline/harness --show-files 0
/usr/local/bin/h ssh fi-gather-pipeline-1030 -c c2 -n ziangli -- bash -lc \
  'cd /data/ziangli/flashinfer-moe-gather-pipeline && python3 harness/import_cache.py --repo control'
```

`import_cache.py` is one-time: it refuses to overwrite an existing rebound cache.
If setup fails, preserve the failed directory/receipt and use a deliberate new
attempt rather than deleting an active cache.

After a source candidate is frozen, configure and run remotely (replace the
manifest and candidate paths with their verified paths; the example is not an
authorization to start GPUs):

```sh
cd /data/ziangli/flashinfer-moe-gather-pipeline
python3 harness/configure.py \
  --control control --candidate candidates/EXPERIMENT \
  --base-manifest runtime/local/control-manifest.json \
  --control-record runtime/source-control.json --candidate-record runtime/source-candidate-r1.json \
  --output runs/EXPERIMENT-compact --label EXPERIMENT-on-82254e20 \
  --matrix compact --mode caac \
  --cpp-workspace /data/ziangli/flashinfer-w4a4-split-dynamic-n/upstream-integration-20261029/megamoe-glm5/cache/cpp \
  --cute-cache /data/ziangli/flashinfer-moe-gather-pipeline/cache/cute-sm103-cuda13.2-dsl4.8 \
  --driver-cache /data/ziangli/flashinfer-moe-gather-pipeline/cache/driver
python3 harness/campaign.py --config runs/EXPERIMENT-compact/perf-config.json --gpus 0 1 2 3 4 5
python3 harness/aggregate.py --config runs/EXPERIMENT-compact/perf-config.json
```

Reserve6/7 for independent source-specific correctness/codegen gates; each of
the six benchmark lanes serializes its jobs. The final refresh uses
`--matrix full --mode aa`, once retention is approved. No existing result
directory is overwritten.

For a bounded control-only CUPTI plumbing check, configure `--candidate control
--mode aa --jobs ep-v3-w4a4 --tokens 1,2,4`; qualify source/cache first and run
only the explicitly allocated GPU. This is a new822 measurement, never a
replacement for the historical external baseline.

## Final table/publication

Keep fresh candidate results for all31 jobs and both passes. Join the final
two-pass aggregates to the unchanged historical baseline fields in
`historical/external/{ep,tp}/summary-cells.csv`; retain unsupported/fused markers.
Heatmaps exclude1/2. The original script table stdout is saved per native
process; do not reconstruct it from CSV or call a mixed historical table fresh
stdout. If table comments reuse old TRT data, replay the actual native formatter
and explicitly label historical final-pass reuse versus aggregate heatmaps.

Codegen/smoke reference (root-owned port): old project's
`cleanup-20261030/validation/harness/{capture_case.py,smoke_case.py,register_guard.py,register_guard_w4.py}`.
For a new paired native qualification, use this project's
`validation/templates/paired-native/run.py` as the controller copy source;
`validation/templates/README.md` documents its unchanged checks and two-worker
source verification. Do not retrofit sealed or active experiment controllers.
The accompanying `config.json` lists36 existing smokes and16 paired signatures;
`compare_codegen.py` and `validation-summary.json` preserve the old48 native
binary comparisons. These are references, not qualification of a new candidate.
