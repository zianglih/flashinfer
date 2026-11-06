# PC profile export and analysis

Use this only on completed, immutable reports. These are CPU report imports;
they do not launch a target, query device metrics, or replace the AUTO/CUPTI
timing comparison. No new capture/export has been performed for this recipe.

## Reuse and inputs

- `harness/audit_ncu_reports.py` owns the eight-rank, one-action, actual
  `profiler__replayer_passes == 1` check and launch-resource extraction.
- `harness/analyze_pc_profile.py` consumes that audit, reuses the established
  canonical `extract_action`, verifies embedded project source hashes, and
  writes per-rank hot-PC/source tables. It does not implement a second report
  integrity/pass parser.
- The existing `extract_pc_samples.py` and `export_ncu_action_sass.py` were copied
  unchanged into `harness/profile_readers/`; `provenance.json` records original
  paths and SHA256. They came from `flashinfer-w4a16-megamoe`, whose
  `profiles/n64-profile-audit-plan/audit_pc_capture.py` is the useful control-flow
  audit precedent. Do not run its old file/96-register/640-thread/UTCHMMA-count
  assumptions, or historical fixed-PC summarizers, against this kernel.
- Preserve the capture's flat repository-relative source/SHA256 manifest and
  exact captured repository prefix separately for each arm. Use the frozen
  source, never today's moving checkout. Preserve the successful exit receipt,
  all per-rank/per-replay policy and tactic receipts, and original NCU log.
  `remote/profile_pair.py` writes these to `queues/LABEL/source-before.json`,
  `capture.json`, and `worker-receipts.json`; reports live in `profiles/LABEL`.

## Export commands

After reports have been copied to an analysis host with the matching NCU2026.1.1
Python report reader, set these paths to the existing capture. No command below
profiles a target. `CAPTURED_SOURCE_ROOT` is the absolute repository prefix
recorded inside that capture, even if analysis runs elsewhere.

```bash
set -euo pipefail
export PROFILE_PROJECT=/workspace/w4a16-mixed-clusters
export PROFILE_LABEL=retained-arm-pc-t4096
export CAPTURE="$PROFILE_PROJECT/profiles/$PROFILE_LABEL"
export PROFILE_QUEUE="$PROFILE_PROJECT/queues/$PROFILE_LABEL"
export NCU_PYTHON=/opt/nvidia/nsight-compute/2026.1.1/extras/python
CAPTURED_SOURCE_ROOT="$(python3 -c \
  'import json,sys; x=json.load(open(sys.argv[1])); assert x["source_unchanged"]; print(x["source"])' \
  "$PROFILE_QUEUE/capture.json")"

# The queue already creates report-integrity.json; reuse it when present.
if [[ ! -f "$PROFILE_QUEUE/report-integrity.json" ]]; then
  python3 "$PROFILE_PROJECT/harness/audit_ncu_reports.py" "$CAPTURE" \
    --ncu-python "$NCU_PYTHON" --output "$PROFILE_QUEUE/report-integrity.json"
fi
python3 "$PROFILE_PROJECT/harness/analyze_pc_profile.py" "$CAPTURE" \
  --audit "$PROFILE_QUEUE/report-integrity.json" \
  --source-root "$CAPTURED_SOURCE_ROOT" \
  --source-manifest "$PROFILE_QUEUE/source-before.json" \
  --ncu-python "$NCU_PYTHON" --top 20 --output "$CAPTURE/pc-analysis"

# Canonical SASS exporter currently uses the same NCU2026.1.1 reader path.
# Export all eight ranks; never transfer rank0's absolute PCs to another rank.
for rank in 0 1 2 3 4 5 6 7; do
  python3 "$PROFILE_PROJECT/harness/profile_readers/export_ncu_action_sass.py" \
    "$CAPTURE/ep_w4a16_megamoe_t4096.rank${rank}.ncu-rep" \
    --extent 0x100000 --output "$CAPTURE/pc-analysis/sass-rank${rank}"
done
```

Use a fresh analysis output directory. Keep reports unchanged between the audit
and extraction. The explicit SASS extent is an export bound, not evidence of
kernel length: check every hot PC and reviewed branch target is inside the
export; increase it if needed. A nonempty export alone does not prove complete
disassembly. The exporter uses the selected function's base plus 16-byte SASS
offsets; compare normalized offsets and instructions only after proving the
per-rank binaries/tactics match.

## Read the outputs in this order

1. `report-integrity.json`: eight unique ranks, one matching kernel per rank,
   one actual profiler replay, exact kernel identities/report hashes, and the
   launch metadata. This is separate from the sampler's aggregated-pass field.
2. `pc-analysis/rank-resources.csv`: rank/device, actual replay count,
   registers/thread, block/grid size, dynamic/static SMEM, sampler passes,
   dropped bytes/overflow, sample count and unmapped-source count. Missing
   fields remain blank and are listed in `analysis.json`; they are not zero.
   Inspect resources for every rank instead of assuming an old 96/640 layout.
3. `hottest-pcs.csv`: top20 sampled SASS sites **per rank**, exact PC, source
   file/line/text, raw sample count, share of that rank's sample count, and
   per-reason counts. `hottest-source-lines.csv` groups only the exact embedded
   file/line; it is a navigation aid, not a dependency attribution. Full rows
   and every correlated metric stay in `pc-samples.json`.
4. `rankN.embedded-sources.json` plus `sass-rankN/sass.json`: inspect the hot
   instruction, its predicate, barrier address/phase, incoming caller branches,
   retry loop and return target before naming an async wait. The analyzer
   deliberately disables historical automatic wait labels. It requires the
   current `bf16_nvfp4/megamoe_kernel.py` embedded hash to match the captured
   manifest and checks every embedded file under the supplied source prefix.
5. Reject a causal interpretation if correlated counts fail conservation,
   sampler overflow/dropped bytes are nonzero, source hashes differ, or the
   relevant PCs cannot be mapped. The canonical reader handles populated NCU
   instances even when `has_value(index)` is false, then requires instance-sum
   equality. `analysis.json` preserves missing metadata/loss findings for review;
   a successful export is not a clean-profile verdict.

## Pipeline attribution and interpretation

Current symbols to find in the **embedded** W4A16 source:

| Call site | Dependency to investigate |
|---|---|
| `_weight_task`: raw `producer_acquire` | Free packed-weight/SF stage released by transform |
| `_activation_task`: `producer_acquire` / lookahead | Free activation stage released by MMA consumers |
| Transform `consumer_wait` / `producer_acquire` | Raw TMA completion / reusable decoded-weight stage |
| MMA `transform_pipe.consumer_wait` | Decoded weights ready |
| MMA `activation_pipe.consumer_wait` | Activation TMA ready |
| MMA `acc_pipe.producer_acquire` | Accumulator stage released by epilogue |
| Scheduler/registration/communication barriers | Work handoff or cross-CTA/rank coordination; trace the exact caller |

A hot `NANOSLEEP.SYNCS`, `SYNCS.PHASECHK`, or adjacent branch needs control-flow
review. Optimized line information can name a nearby operation or shared helper;
the source line alone cannot identify which pipeline/barrier owns the wait.
An empty-stage producer wait is downstream backpressure, so it does not by
itself show slow incoming memory. A full-stage consumer wait identifies missing
readiness; follow its actual producer before proposing a TMA/MMA change.

`share_of_rank_samples` is `PC sample_count / rank sample_count`. It is neither
elapsed stall time nor an instruction issue rate. Counts depend on the sampled
warp population, sampling interval, replay, and work distribution. Preserve
ranks separately; a higher share can result from fewer samples elsewhere.
The ordinary reasons can be sampled even while another warp issues; the
`_not_issued` variants apply when that scheduler issues nothing. Stalls are
attributed to the waiting consumer, so inspect source/SASS dependencies.
[NVIDIA profiling guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html)

Do not divide `_not_issued` counts by ordinary sample counts or subtract the
two families: NVIDIA notes they can come from different profiling passes and
need not correlate exactly. Report raw counts or use each metric's own total
with an explicit denominator. A `long_scoreboard` label at an async barrier or
control-flow site is not proof of HBM-bound weight loads.
[NVIDIA source-view sampling definitions](https://docs.nvidia.com/nsight-compute/NsightCompute/index.html)

`--warp-sampling-max-passes=1` limits sampling passes, not all application replay.
Keep the logged replay sequence, `profiler__replayer_passes`, and
`smsp__pcsamp_aggregated_passes` separate. Any unstable AUTO winner/grid or
missing rank invalidates the matched capture. Instrumented eager durations do
not enter the CUPTI speedup table; a proposed bottleneck still needs a controlled
AUTO performance experiment.

Validation status: canonical helpers copied byte-for-byte; local Ruff, syntax,
and CLI help checks pass. Actual new report imports and SASS mapping remain
pending completed captures. No remote source/helper was changed by this work.
