# EP4 baseline profiles

The parent approved profiling on the exclusively assigned hu9 devbox
`hashinfer-ep4-perf-0920` (c2/infra). Nsys T256 and T4096 are complete and
collected. Full NCU T256 completed40 application replays per rank, but its
profiler parents hung after writing the reports and required forced teardown.
The reports, outputs and source artifacts are independently validated below;
the launcher result remains exit1. Hu9 has been returned to the benchmark
owner. No additional GPU capture is planned.

This is a narrow adaptation of the preserved always-fused
`main-baseline-refresh-replacement/profiling/profile-forward-fused.py`, rather
than the older helper that expects a separate input-stage kernel. Helpers are
frozen by `helpers.json`. No HashInfer source is modified.

## Pinned workload

- Source: `7e6e977f4788f91eaf5988fd4ffea93fc4f1eed5`; every tracked source file is
  checked against `../baseline-source.json` before import and after execution.
- EP4, H7168/I2048/E256/K8, deterministic combine, `apply_topk_in_fc1=False`, O3.
  Compiled options must explicitly contain `--opt-level 3` and register cap96.
- The current native benchmark supplies weights, FP32 alphas, routing and BF16
  input. Every rank must reproduce the complete hu6 baseline's exact input,
  weight and output fingerprints in `selection.json`.
- Selected tactics, agreed by all four baseline ranks:

| Total tokens | MMA tile | Return | Cluster | Group / scheduler / flags |
|---:|---|---|---|---|
|256|(256,64,256)|epi_warps|(2,1,1)|512 / 2 / 4|
|4096|(256,128,256)|reuse_dispatch_warps|(2,1,1)|512 / 2 / 4|

Both also use `epi_flag_batch=(2,4)`, atomic-counter load balancing,
`use_2cta_instrs=True`, and `in_kernel_fc2_reduce=False`.

Runtime must match the measured CUDA13.2 baseline: NVIDIA B300 SXM6 AC,
Torch `2.12.0a0+5aff3928d8.nv26.05`, CUPTI13.2.0, CuTe DSL4.7.1. The devbox image
is `nvcr.io/nvidia/pytorch:26.05-py3`. The harness imports the native benchmark's
fixture functions, but never calls its CUPTI timing lifecycle or finalize.

## Capture protocol

`run_profiles.py` defaults to a CPU-only dry plan. Execution requires an idle
node matching its receipt's host, boot and GPU UUIDs, free rendezvous ports, a
fresh output directory and unchanged helper/source pins. Each run uses the
first four recorded GPU UUIDs, a dedicated torchrun rendezvous and per-rank
compile caches. No ordinary kernel replay or isolated-rank profiling is used.

- **nsys:** five cold-L2 CUDA-graph public forwards, one profiler per rank.
  Capture includes the surrounding L2 flush and NCCL rendezvous kernels so
  they can be distinguished in the trace. Export verifies exactly five fused
  MegaMoE kernels per rank and no standalone input-stage/TopkReduce kernels.
  Version3 uses `--trace=cuda-sw,nvtx`: the default Blackwell hardware trace
  lost incomplete events in version2. Both version3 captures contain every
  expected kernel, although the generic stop-boundary CUDA/NVTX warnings are
  preserved in their SQLite diagnostics.
- **ncu:** full metric set, four concurrent profilers using a TCP communicator,
  lockstep `stage::MegaMoE` NVTX range and an exact MegaMoE kernel-name filter.
  Application replay recreates all ranks; PrefixStore epochs prevent stale
  torchrun-store state. `MEGA_USE_NCU=0` keeps the production barrier code path.
  Exactly one eager public forward is selected per application incarnation.
- Both enable line information for source/SASS correlation, assert finite,
  repeated-bit-identical output and agreement with the measured baseline, and
  save actual PTX/cubins plus cuobjdump resource/SASS output for the four public
  input ABIs. The profiled ABI is fused int32/vector. These are diagnostic
  captures; their durations are **not** benchmark or retention latencies.
- Clean closure requires exit0, all rank results, complete reports, unchanged
  source and no surviving owned processes or GPU processes. Sanitizer is not
  part of this work.

## Executed node and local helpers

The executed environment is hu9, boot
`3d5c5f08-7541-4107-ac88-cd9ebe5f411c`, with source
`/workspace/hashinfer-ep4-perf-20260920/sources/baseline`, Python
`/workspace/hashinfer-ep4-perf-20260920/venv/bin/python`, and version3 helpers in
`/workspace/hashinfer-ep4-perf-20260920/profiling-v3`. Reports are under
`profiles-v3`. Nsys is `/usr/local/cuda/bin/nsys` version2026.2.1.210; NCU is
`/usr/local/bin/ncu` version2026.1.1.0.

`launch_hu9.py` records the detached owner PID/process group, checks the idle
node and frozen inputs, runs the dry plan and then executes. `profile_status.py`
only reads state. `collect_hu9.py` requires clean closure before export, archives
reports and evidence, verifies every downloaded file hash and excludes only
recompilation caches. These wrappers use the managed macOS `/usr/local/bin/h`.

```bash
python3 profiling/launch_hu9.py --mode ncu --tokens 256
python3 profiling/profile_status.py ncu-t256
python3 profiling/collect_hu9.py ncu-t256
```

## Generic preparation commands

Copy this entire directory and `baseline-source.json` beside it under
`/workspace/hashinfer-ep4-perf-20260920`, retaining helper hashes. Reuse the
unchanged source archive extracted as `sources/baseline`, and the matching
node receipt. On a new node, first reproduce the existing environment and save
its receipt; do not substitute an unverified Python environment.

The following uses hu6's existing environment as an example. Change the node
receipt and Python path together for an assigned replacement. Run dry first;
append `--execute` only after review/assignment. Each command blocks until the
capture and clean closure are complete; an outer owner may launch it detached
with a recorded PID/process group as in the existing benchmark workflow.

```bash
cd /workspace/hashinfer-ep4-perf-20260920
/workspace/flashinfer-pr8-sync-20260919/venv/bin/python -B profiling/run_profiles.py \
  --source sources/baseline --manifest baseline-source.json \
  --node-receipt node-fi-mega-sync-0919.json \
  --python /workspace/flashinfer-pr8-sync-20260919/venv/bin/python \
  --tool /usr/local/bin/nsys --mode nsys --tokens 256 \
  --output profiles/nsys-t256

/workspace/flashinfer-pr8-sync-20260919/venv/bin/python -B profiling/run_profiles.py \
  --source sources/baseline --manifest baseline-source.json \
  --node-receipt node-fi-mega-sync-0919.json \
  --python /workspace/flashinfer-pr8-sync-20260919/venv/bin/python \
  --tool /usr/local/bin/ncu --mode ncu --tokens 256 \
  --output profiles/ncu-t256
```

Repeat with `--tokens 4096` and fresh `profiles/nsys-t4096`/`profiles/ncu-t4096`.
Run the two profilers sequentially on one node; the default ports32554/49324
are private to this harness and checked before launch.

After clean closure, export without running any CUDA application:

```bash
/workspace/flashinfer-pr8-sync-20260919/venv/bin/python -B profiling/export_reports.py \
  --output profiles/ncu-t256 --tool /usr/local/bin/ncu
/workspace/flashinfer-pr8-sync-20260919/venv/bin/python -B profiling/export_reports.py \
  --output profiles/nsys-t256 --tool /usr/local/bin/nsys
```

NCU exports raw, session and details pages, binds reports to actual device
metadata (filenames can differ from ranks), and retains unavailable counters
explicitly. Nsys exports SQLite and records kernel counts. Archive the reports,
exports, rank results/codegen, summaries, helper/source manifests, selection,
node and environment receipts. Compare actual register/SMEM/stack/local
traffic, eligible warps, instruction and memory throughput, and sampled stall
PCs at scheduler/raw-decode/activation/accumulator waits. Do not treat a high
whole-kernel stall percentage as proof of a particular phase bottleneck.

## Local preparation checks

`ruff format`, `ruff check` and Python byte compilation passed. All four
`dryplan-{nsys,ncu}-t{256,4096}.json` files were generated locally while checking
all104 baseline source hashes. Their local source/helper paths are preparation
evidence, not remote execution commands. Tool flags, imports, GPU execution,
report completeness and post-capture interpretation are recorded per run below.

## Capture ledger

- **Version1, no capture:** the optional host-side `_smem_size` diagnostic
  required an active CuTe MLIR location. Four ABIs compiled and eager/graph
  warmup completed on all ranks, but execution stopped before profiler capture.
  Clean failure closure is preserved. Version2 removed only that invalid host
  recomputation; actual cubin/launch resources provide the measurement.
- **Version2, partial T256 trace:** execution and output checks passed on all
  ranks, but rank2's default Blackwell hardware trace dropped17 incomplete
  CUPTI events. This is not accepted as a complete trace. Preserve the original
  reports and `nsys-t256-diagnostics.json`; do not infer a kernel correctness
  failure from profiler event loss.
- **Version3, complete nsys T256 and T4096:** each of four reports has exactly
  five MegaMoE launches, with no standalone staging/combine kernel. Every
  rank's output matches the selected baseline bits; all process groups closed
  and GPUs were idle. Local `collected-nsys-t256` and `collected-nsys-t4096`
  contain130 hash-verified files each. Archive SHA256 values are
  `0c1989a505328b01382f0b6ad93bc73d9e816ea35bafa80340feed3e5de74abf`
  and `d5f284b81cf863bdc343ebbfc3a350ccc394b0c9c81a7c9886dbfa5563278fd4`.
  Both take about111seconds including process start, compilation and teardown.
- **Actual resources:** both selected kernels launch640threads and96registers
  per thread, with zero local bytes/thread. Dynamic shared memory is200064bytes
  for T256/N64/epi return and230784bytes for T4096/N128/dispatch return. Saved
  PTX/cubins and cuobjdump reports cover all four fused input ABIs; no stack or
  local spills are reported. `cuobjdump` static shared size and the nsys static
  shared field differ; raw reports remain available, and neither is used as
  a substitute for the measured dynamic allocation.
- **Full NCU T256:** all40 application replays completed on every rank. Four
  completed reports imported successfully before and after forced teardown,
  with unchanged hashes. The four profiler parents stayed GPU-empty, at zero
  CPU and futex-blocked after report generation; their recorded groups received
  TERM, with one requiring KILL after30seconds. The capture launcher exited1.
  `forced-teardown.json` preserves this limitation; no success flag was repaired.
  `collected-ncu-t256` contains4079 hash-verified paths, stored as394 unique files
  with internal archive hardlinks. Archive SHA256:
  `5a3329782a675f9059edcc7c32e446a53e2ea223ffef4213931d38df41c97218`.
  The independent auditor verifies160 rank/epoch records, their exact source,
  tactic and input/weight fingerprints, and458752 finite BF16 output elements
  per record against the baseline bytes. All selected cubins have one hash.
  Read `INTERPRETATION.md` for counter availability, implausible aggregate
  ratios and source/SASS findings; these are diagnostic evidence, not retention
  latency or a clean profiler-launch result.
