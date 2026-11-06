# Retained N3U EP8 T16384 W4A4 FC1 metrics

Completed on recovery C2 B300 GPU3 at retained `2b8eb9d8`, swap source `482b636a`.
The original frozen M512/N128/two-CTA FC1 choice was preserved. Included input
quantization, functional API, unfused finalize, exact cached routes/tactics,
unchanged compiler options and persistent release cache. Five NCU application
replays returned the same FC1 and FC2 images; all10 native captures have zero
local memory. Full13,245-file source and four native ELF/Ninja hashes passed
before/after checks. GPU3 was verified idle and released.

| Metric | Current EP8 M512/N128/C2 | Earlier TP8 M128/N256/C1 |
|---|---:|---:|
| Diagnostic FC1 duration, µs |290.176|approximately472|
| Tensor activity, % |26.52|16.24|
| DRAM throughput, % |25.56|14.90|
| DRAM read / write, bytes |408,227,072 /160,811,264|389,265,000 /154,627,000|
| L2 hit / throughput, % |72.34 /41.23|76.46 /39.96|
| Issue activity, % |32.57|29.71|
| Long scoreboard, % |53.98|54.44|
| MIO throttle, % |2.00|9.81|
| Barrier, % |13.59|8.90|
| Short scoreboard / wait / math throttle, % |6.47 /5.35 /0.56|not used for this comparison|
| Initial registers / local bytes |168 /0|168 /0|
| Dynamic shared memory, bytes |189,440|222,208|

The old TP profile differs in partition, geometry and retained instruction
cleanups, so these are diagnostic context, not a before/after comparison.
The current189,440 dynamic bytes are distinct from190,464 allocated bytes
including the driver's1,024 bytes. The actual grid has148 CTAs,74 two-CTA
clusters, and the kernel uses four operand stages, one accumulator stage,
two overlapping accumulator windows and512 TMEM columns.

**No SF lane-coalescing prototype is justified by these aggregate results.**
MIO pressure is materially lower in this wide geometry. Low tensor activity
and the remaining long-scoreboard/barrier observations justify one native-PC
pass to distinguish gather/operand readiness, accumulator ownership and the
terminal CTA join. Warp-stall samples are not time fractions, and NCU perturbs
overlap;290.176µs is not a replacement for native CUPTI timing.

The actual N3U image also closes the gather task-bound question: all eight
static Gather4 sites are unpredicated in SASS; their PTX blocks contain only
the elected-lane guards and no task-bound comparison. This strengthens the
earlier representative-image check in `audits/n3u-ep-wide-fc1-source/`.

Reproduce the off-GPU checks with `python3 analyze_metrics.py`. The receipt is
`metrics-summary.json`, binding all raw/profile/native hashes. Original NCU
output and report are in `fc1-metrics/`; the verified transport archive is
`fc1-metrics-evidence.tar.gz`. The local pre-deployment oversized-argv failure
performed no remote action and is recorded in `transport-notes.json`.

PC profiling is authorized only after the independent GPU0 graph-policy search
and GPU1 ACCA timing owners have both released their runs. It has not started
as part of this metrics result.
