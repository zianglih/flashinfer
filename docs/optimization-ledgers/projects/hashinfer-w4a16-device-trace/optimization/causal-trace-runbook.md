# Controlled dispatch overlap traces

These helpers are local experiment artifacts, outside the HashInfer PR.
No new trace or GPU result was produced while preparing them.

The default comparison holds a previously autotuned winner fixed across
`store16`, `counts_overlap`, and `parallel_payload`. Each source first runs
the existing uniform256 harness's independent bit-exact baseline validation,
then native IKET captures exactly one full-grid integrated launch. It uses
the native cluster-0 recording filter; GPU work distribution is unchanged.
The wrapper records winner-file, wrapper, and source fingerprints and checks
that source content is unchanged across each run. Reusing a winner is labeled
explicitly and is not described as fresh tuning on the changed source.

The fixture is EP4, H6144/I2048/E256/top-k8, 256 tokens/rank, uniform routing,
32 tokens/expert globally. Both candidate sources already include store16.
If another optimization is retained before this experiment, first rebuild
the candidate stack and use its immediate predecessor as the control.

## Commands

Copy these three helpers plus `evidence/validate_iket_trace.py` with the same
project-relative layout to the existing devbox. Copy the selected original
`autotune.json` winner record unchanged; its bytes identify the selection.
Use a fresh output directory and the parent's exclusive GPU queue.

This command only prints its execution plan. Append `--execute` when the
queued GPU slot is ready:

```sh
python /workspace/hashinfer-trace/optimization/capture_causal_traces.py \
  --arm store16=/workspace/hashinfer-trace/optimization/store16 \
  --arm counts_overlap=/workspace/hashinfer-trace/optimization/counts_overlap \
  --arm parallel_payload=/workspace/hashinfer-trace/optimization/parallel_payload \
  --winner-record /workspace/hashinfer-trace/uniform2-checks/autotune.json \
  --output-dir /workspace/hashinfer-trace/optimization/results/causal-traces
```

It runs serial baseline/capture pairs and creates per-arm logs, original
baseline/capture reports, PID-to-rank manifests, JSON traces and Perfetto
files. Native IKET performs its normal sizing/capture reruns. Every capture
process still executes the target once. The final comparison refuses
differing tactics or input/weight fixtures and verifies each capture against
its own source-matched reference-validated baseline.

For the final promoted source, make a separate fresh-autotuned capture:

```sh
python /workspace/hashinfer-trace/optimization/capture_causal_traces.py \
  --arm final=/workspace/hashinfer-trace/hashinfer \
  --retune \
  --output-dir /workspace/hashinfer-trace/optimization/results/final-winner-trace \
  --execute
```

The final command uses the existing native candidate catalog and tuner,
including all raw per-rank timing samples. Those hot CUDA-event tuner scores
select a trace tactic; the established cold-L2 CUPTI benchmark remains the
performance qualification and retention criterion.

## What the comparison establishes

`summarize_causal_traces.py` anchors each rank separately at its own
CTA0/warp8 `dispatch_exchange_counts_sync` end. It reports both CTAs' first
scheduler publication, weight-load marker, transform parent, actual decode
subsection, decoded-weight commit, activation-load marker, and MMA marker.
Negative offsets establish that the marker occurred before the same GPU's
dispatch publication range ended. There is no cross-GPU clock alignment.
Offsets comparable to the trace's 32 ns granularity are not useful leads.

For count overlap, look for actual `transform_load_decode_nvfp4` activity
before dispatch publication completes, not just a scheduler range that begins
early. Count readiness still requires every rank's final count. Activation
and MMA may remain blocked on the unchanged payload path. The analyzer reports
the union of decode intervals intersecting the dispatch range; it does not
sum warp occupancy or interpret nested ranges as GPU utilization.

For parallel payload, inspect epilogue payload-copy windows, dispatch route
staging, the prep span before `dispatch_wait_input_payload`, and the NB11 wait.
The prep marker includes its inherited local barriers. The extra subrange
prevents attributing payload rendezvous time to route processing. The analyzer
requires one payload range and one join range per participating warp and
checks that the join cannot complete before any local payload marker ends.

The established strict native validator runs on a temporary canonical-label
view. Only `sched_wait_dispatch_counts` and `dispatch_stage_routes` are mapped
to their old validation roles; the two new payload markers are allowed and
checked separately. Original trace labels and data stay unchanged. Per-K
coverage, paired push/pop, nesting, work agreement, grid geometry, and warp
identity checks remain enabled.

## Delayed-rank diagnostic

Run regular captures first. No launch delay is automatically inserted.
Delaying an entire rank before launch postpones its counts as well, so that
does not isolate count readiness from the later global publication barrier.
If regular captures are inconclusive, a separately fingerprinted, one-shot
diagnostic could pause a rank *after all its count publications complete but
before its global-barrier arrival*. Apply the same diagnostic to control and
candidate and keep it out of performance measurements. Such a kernel edit is
not part of these prepared sources or scripts.

## Local verification

The analyzer passed the existing four-rank uniform256 archive. Its baseline
rank2 CTA0 offsets are +3.072 us for first scheduler publication, +3.328 us for
the weight marker, +6.016 us for the decode subsection, and +35.232 us for the
first MMA marker; the pre-publication decode overlap is zero. This only
qualifies parsing against existing evidence, not the new candidates.

No candidate device compilation, new trace, numerical run, or performance
result is claimed here.
