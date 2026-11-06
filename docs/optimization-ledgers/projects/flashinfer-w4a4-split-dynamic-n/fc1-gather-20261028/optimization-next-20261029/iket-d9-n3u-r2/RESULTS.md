# Current N3U EP8 16K W4A4 pipeline trace

Retained source `d9dee2dae50fef5d14c609e277fbc29d48df08b4`, native winner and
routing, public benchmark profiler path. The trace supports examining FC1
accumulator/epilogue work next; it does not establish a new performance win or
compare causally with the historical d35/fb66 trace, whose winner differs.

- **Binding:** all514 source hashes match the committed d9 tree. Route IDs SHA
  `e5aa19cec523609ef943e5d240b918b1f529f01a8f38975f271b53f0e02cc6e4`,
  route weights SHA `4cc7a2e390aab43a772647ae26952101ffceeae1fb18f35894e95064ed34dc43`.
  Frozen tactic: N128, FC1M512/cluster(2,1), FC2M256/cluster(2,1), K4/4, CLCoff.
  FC1 actually compiles with384threads, four operand stages, K256, two CTAs,
  PDLon. Input quantization is included and finalize is unfused.
- **Instrumentation:** only the first two physical two-CTA groups emit FC1
  NativeDump ranges. Removing marker operations gives an identical source AST.
  All148 CTAs still launch. FC2 is not instrumented. The selected graph replay
  is index3: three public-profiler warmups precede the single cold-L2 replay
  between cudaProfilerStart/Stop. The regular warmup and all four graph replays
  are preserved and separately summarized.
- **Resources:** tracker and profiling processes compile the same marker-enabled
  CUBIN `7b56573456051ce0f97b581b7280f315d3232cba01f32f595234eb80463c02f0`.
  Both prelaunch guards show REG168, STACK0, LOCAL0, noLDL/STL. The installed
  NativeDump path is pass-through and does not run PMTrig SASS resource selection
  (`runtime-source.json`). Source, winner-cache, tactic and route guards pass.
- **Tool qualification:** R0/R1 stopped before FC1 launch because the helper did
  not create compiler-dumps; no_cache alone did not fix it. R2 creates that
  directory explicitly, retaining the resource guard in both tool phases.
  Failed receipts/logs/source hashes remain in their own immutable archives.
  iKET reported optional CUDA compatibility support unavailable, but the tracker,
  profiler, trace export and guards completed successfully. No sanitizer ran.

## Observations from the final graph replay

Both sampled leaders process51 scheduled tiles and408 K stages. Their sampled
warp spans are329.44/333.28µs; these are instrumented spans, not full-kernel or
end-to-end latency measurements.

- Weight and gathered-B ready waits on the MMA warp have medians64ns/32ns,
  P90both96ns. These ranges do not show persistent input starvation at the
  sampled MMA consumers. The startup dependency markers are0–32ns and are too
  short for a useful fine-grained conclusion at this trace resolution.
- The producer empty-stage waits are longer: weight384ns median, gather224ns;
  the gather relay’s128ns median has a1536ns P90. Empty-stage waits reflect
  backpressure/reuse, while the relay range waits for local TMA+SF completion.
  It would be incorrect to attribute all of these waits to HBM load latency.
- The representative epilogue warp has4032ns median body and1856ns median
  accumulator-ready wait; the MMA accumulator-empty wait is960ns median.
  These larger scopes identify accumulator/epilogue scheduling as a useful
  target, but `epi_body` includes conversion, transpose, quantization and stores
  and cannot distinguish them by itself.
- Early release already overlaps work. For all50 successive tile pairs on each
  leader, the next tile’s first MMA issue starts before the previous epilogue
  body ends. Median overlap is2528ns/2816ns for CTA0/2. The next accumulator
  acquire completes1024ns/896ns after epilogue-body start. A design that removes
  this overlap would discard an existing pipeline benefit.

The table combines CTA0/2; epilogue uses representative warp4, while gather
uses all four issuing warps8–11. Counts therefore differ by ownership. Issue
ranges measure GPU warp instruction issue work, not asynchronous operation
completion. Concurrent warp ranges overlap and must not be summed into a
kernel-latency model.

| Marker | Warps | Count | Mean ns | Median ns | P90 ns |
|---|---|---:|---:|---:|---:|
| producer_tma_empty | 0 | 816 | 496.9 | 384 | 1216 |
| producer_weight_tma | 0 | 816 | 81.5 | 64 | 192 |
| producer_gather_relay_wait | 1 | 816 | 563.6 | 128 | 1536 |
| producer_gather_empty | 8,9,10,11 | 3264 | 381.9 | 224 | 1088 |
| producer_gather_issue | 8,9,10,11 | 3264 | 189.6 | 160 | 384 |
| mma_acc_empty | 2 | 102 | 915.1 | 960 | 1184 |
| mma_tma_ready | 2 | 816 | 69.1 | 64 | 96 |
| mma_sf_copy_issue | 2 | 816 | 56.1 | 32 | 96 |
| mma_gather_ready | 2 | 816 | 61.8 | 32 | 96 |
| mma_sfb_copy_issue | 2 | 816 | 57.9 | 32 | 128 |
| mma_umma0_issue | 2 | 816 | 59.7 | 32 | 128 |
| mma_umma1_issue | 2 | 816 | 40.2 | 32 | 64 |
| mma_release_issue | 2 | 816 | 30.0 | 32 | 64 |
| epi_acc_wait | 4 | 102 | 2024.2 | 1856 | 2368 |
| epi_body | 4 | 102 | 3836.9 | 4032 | 4288 |

## Artifacts

- `timeline.png`/`.svg`: first60µs on the two sampled leaders; visually checked.
- `all-warp-ranges.csv`: every marker/CTA/warp for all five captured launches.
- `summary.json`: binding/resource proof, launch inventory, all marker statistics
  and adjacent-tile overlap accounting.
- `captured-evidence/`: original trace, sampled source, both CUBIN/SASS/resource
  captures, receipts and helpers. All21 semantic files were hash-verified;
  archive SHA `abc7af715bf494a25c894e609a337ea2cb846898d048b61277f66364ade6807e`.
- `../iket-d9-n3u/failed-attempt-audit.json`: committed514-file source proof and
  R0/R1 incident boundary. GPU0 was verified idle after completion; no clock or
  power setting changed.
