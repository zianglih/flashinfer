# GPU execution status

Retained control is 658a0c8942c7454050f990c0be3083aa61b6a89f. The existing C2
fi-mega-scale-1029 node remains allocated, eight B300s, image
nvcr.io/nvidia/pytorch:26.05-py3. No sanitizer.

## Prepared

- `setup/control-tracked-manifest.json`: all 13,245 retained tracked files.
- `frozen-inputs/`: 31 jobs, 1,455 unchanged tactic-cache files, complete original
  expected route/tactic records. Screen is 180 cells; full is 468.
- `setup/lane-plan.json`: V3 EP/TP on 0/1, V41F on 2/3, K3 on 4/5, N3U on 6/7.
- `harness/`: existing strict CUPTI CAAC engine and native observer, rebound to
  archived sources with full manifests rather than Git metadata. Per-variant
  config is passed through `FI_OWNERSHIP_CONFIG` to the observer adapter so
  concurrent variants never share mutable config. No changes to native timing,
  backend invocation, frozen choices, or route capture.
- `native-proof/setup/`: canonical native assets (21,553 hashes), full generated
  Ninja descriptions and dry runs. Control and W4-v1 generated descriptions
  are byte-identical. FP4, MXFP8 and moe_utils descriptions also match warmed
  Ninja files; dry run reports no work. The optional dsv3 routing module still
  has an older source-root command and may rebuild once if used.

Remote root is `/data/ziangli/flashinfer-w4a4-split-dynamic-n/element-scale-ownership-20261029`.
The shared C++ workspace is the prior completed GLM5 task's `cache/cpp`.
Canonical `csrc/include` links point to that task's tested source paths, and
CUTLASS/CCCL/spdlog links keep their existing persistent absolute paths.
Do not sync a small local directory to the remote task root: `h sync` deletes
remote files absent locally. Sync dedicated leaves only.

## Historical W4 v1 smoke

`smoke/frozen-w4-v1`: six exact cases passed, including K128 FC2, partial K384,
one/two CTA, static/CLC, PDL off/on, old/new layout. Correctness-only two-active-
cluster cap forces multiple tile metadata turns. All 12 loaded FC1/FC2 kernels
have zero local memory; initial registers are 96 for FC1 and 128 for FC2.
Native FP4/moe_utils checks took 0.013–0.383s. Sources/helpers/logs are retained.
This is **not qualification of the current candidates**: W4 was subsequently
updated to use voted, warp-uniform nonblocking readiness. Fresh A/B smoke is
required. Nothing has been retained or timed yet.

## Next

Wait for root approval of each immutable two-file candidate. Source owners:
A = `flashinfer-element-scale-review`; B = `flashinfer-crossed-producers-review`.
Use `freeze_candidate.py --name <variant> --review <path> --swap-sha <hash>
--w4-sha <hash>` to seal the exact two files and generate independent screen/full
configs. `prepare_candidate.py` creates/validates the remote frozen source once.
Run current smoke and confirm native command equality before performance.
Each GPU lane runs one complete C-A-A-C job at a time. A/B jobs on a shared lane
are sequential; disjoint lanes may run concurrently. Do not benchmark live
review checkouts. Do not infer retention from old smoke or compilation alone.

## Current execution (supersedes the earlier next-step note)

Root approved and sealed both corrected variants. A is swap02031c5f/W4
0ba17644; B is swap15d9533f/W4b29cce29. Complete immutable manifests and
patches are in `frozen-elements-scales-a/` and `frozen-crossed-b/`.

Both passed32 fresh bit-exact smoke cases (64total), using the repository
oracle with its actual MMA-K/K96 plan observer. Coverage includes tiny-K and
long-K rings, static/CLC, one/two CTA, PDL off/on, multiple metadata wraps,
allfive supported modes, and old/new W4 layouts. All128 loaded grouped GEMM
kernels passed register/resource guards with zero local memory. Complete
records are in `smoke/<variant>-<mode>-<group>/` and each variant's
`smoke/campaign.json`; `setup/smoke-final-audit.json` summarizes the receipts.
Each variant's full generated native Ninja descriptions match control.

The authorized first performance stage is now a smaller **72cells/variant**
triage: tokens4 and4096, all36supported model/topology/dtype combinations,
frozen choices and native strict-CUPTI CAAC. The first eight control processes
stopped at the cache-miss guard before emitting results. No AUTO or candidate
measurement occurred. Their failure artifacts are retained separately as
`triage-cache-miss/` and `<variant>/triage-cache-miss/` remotely.

The mismatch is the managed cache's environment namespace: historical source
was packaged as0.7.2 with an older compiler-stack distribution fingerprint;
this source archive correctly reports0.0.0+unknown/current stack. Root approved
an explicit fixed-choice import in `cache-rebind/rebind.py`: the1424 original
CuTe entry files remain byte-identical and are placed in a separate namespace
with the honestly observed current manifest. Original caches are untouched,
no opaque engine IDs are imported, native preload/lookup are verified, and
all missing-cache/AUTO guards remain active. No environment versions are
spoofed and no retuning occurs. A complete pilot CAAC job will be checked before
filling the eight lanes again. Neither180-cell screening nor468-cell full
measurement is authorized to start automatically.

Namespace import completed for all31 jobs:1424 byte-identical entry files, including58 unchanged unused W4 default sentinels. All selected4/4096 winners passed explicit-tuple native lookup and zero skipped preload records. The first V3 EP8 W4A4 control phase passed native CUPTI/sample/route/tactic/resource guards in21.1 seconds; candidate phases are next. No runtime or source version was spoofed.

The first import missed MX's additional original manifest field
`measure_execution_mode=cuda_graph`. The seven first MX control attempts
therefore stopped at the native cache-miss assertion before recording any
complete timing. `cache-rebind/policy-receipt.json` separately records an
additive correction: all original MX entry bytes are also present under the
honest current runtime plus that unchanged policy field (namespace
8fec41c4ced8bd23). The first receipt/configs remain immutable, and no entries,
tactics, policy values, kernel sources, or benchmark timing changed.

`recovery-helper/resume_lanes.py` resumes only lanes whose original controller
has stopped and whose GPU is idle. Failed MX jobs are preserved under each
variant's `triage-policy-cache-miss/`; each resumed job restarts a fresh CAAC
and copies the same corrected cache to both arms. Completed NVFP4 jobs are
reused. Original V41F TP has no MX arm and continues normally. Final status
must combine the original and recovery controller receipts, then verify all
62 complete jobs / 144 cells; the original controller's expected failure
receipt alone is not the final campaign outcome.

## Final execution status

Original A/B attempts are terminal: each has29 complete CAAC jobs/64cells and
2 resource-failed N3U mixed-MX jobs. All four failures report8 bytes of native
local memory in MXFP8 FC1; no guard was relaxed. This does not establish actual
register spilling without codegen. Their entire mixed jobs remain excluded
from aggregates; no narrowed MX timings were run. Raw failed/complete jobs,
`job-status.json`, and `qualified-{summary.json,cells.csv,table.md}` are local.
The independent final audit is owned by the parent's data-audit agent.

The separate thin W4 FC1-only candidate passed8 exact/resource smoke cases,
then16 CAAC cells across8 model/topology arms (7 fresh jobs and reused V41F TP
pilot). Full results and summary are under `w4-fc1-only/screen/`. Sources remain
unstaged. No retention/publication decision was made by the GPU worker.

All8 B300 GPUs were observed idle with0MiB/0% after completion. Leave the
existing node and persistent C++ cache allocated; `FINAL_HANDOFF.json` records
access/cache details. No additional GPU work is queued.

## Authorized broader thin-W4 screen completed

The additional 24 cells at64/512/16384 completed on all8 model/topology
lanes, each with four verified strict-CUPTI CAAC phases. All original16 cells
at4/4096 are reused unchanged, for40 total and16,000 native timing samples.
The source pair remains658a control and thin W4 kernel1debc908, with swap-AB
unchanged. No additional smoke, tuning, source changes, or profiling occurred.

Seven recorded native cache entries at16384 contain the deterministic-1
choice. A read-only cache preflight and source AST proof establish the unchanged
-1 → None → fixed default resolution. Passive host receipts bind actual FC1/FC2
compiled tiler, cluster, raster, CLC, and PDL settings to native resource guards;
all settings match across CAAC. The trailing tactic boolean is raster order,
not CLC. Original entry bytes and native miss/AUTO guards are unchanged.

New24-cell geomean is−0.161%; combined40 is+0.107% overall,+0.365% EP,
−0.149% TP. Decode+0.365%,512+0.011%,prefill−0.101%. Maximum repeated
control/candidate spread is5.343%/2.933%; this is not evidence of a robust
broad improvement. Complete raw evidence is under `w4-fc1-only/broader/`,
and the combined table/provenance is under `w4-fc1-only/combined40/`.
Independent actual-data/default-resolution audit is in progress.

All8 B300 GPUs are again idle with0MiB and0% utilization. No further GPU
work is queued; keep the node and compilation caches available. No retention
decision, source commit/push, or PR write was performed by this worker.
