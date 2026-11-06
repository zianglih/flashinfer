# W4 output-stage late acquire: prior evidence and remaining boundary

An isolated **non-descriptor FC2-only** trial already exists and was rejected as neutral. This closes the exact GEMM2 mechanism; it must not be described as new merely because the current W4 producer has five warpgroups.

The original ledger is `/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md:5607–5653`, with raw logs bound in `history-evidence.json`. It moved `PipelineTmaStore.producer_acquire()` from immediately after commit to immediately before output shared-buffer reuse, allowing the next accumulator load, release, scaling and BF16 conversion to proceed first. GEMM1 remained unchanged. All six numerical cases passed. B200, CUDA13.2, PDL, deterministic unfused finalize, CUDA graphs and CUPTI were the recorded environment. Both arms retuned in the raw logs, so this is historical adjacent-source evidence, not today's frozen-winner CAAC.

| Historical non-descriptor FC2 experiment | Control | Candidate | Change |
|---|---:|---:|---:|
| Isolated EP8 T4096 |432.575µs|432.416µs|+0.0368%|
| Full EP8 T1…4096,13 cells |—|—|+0.1908% geometric mean|
| Full TP8 T1…4096,13 cells |—|—|−0.0008% geometric mean|

The apparent +1.43% full-sweep EP4K result came from a slow baseline and did not reproduce in the adjacent isolated gate. The source was restored. Full raw rows, log hashes and calculations are preserved in `history-evidence.json`; no timing was rerun.

The later October28 descriptor source03→04 experiment changes both the gated and nongated output paths. It passed96 paired W4 graph replays,10 existing tests and4 fused compatibility cases. Its32 fixed-winner CAAC cells measured +0.3651% overall, +0.2976% decode and +0.4325% prefill, spanning −0.8037% to+4.9673%. The bounded TP V3T64 result was191.369→182.313µs (+4.9673%); TP V3T16384 was2231.229→2219.052µs (+0.5487%). This is descriptor-context evidence, and the larger descriptor family was not retained. Neither it nor the earlier FC2 trial isolates a non-descriptor gated-FC1 improvement.

The retained W4 file (`de042712…`, unchanged in b52) still issues commit/acquire/reuse join at lines2525–2527 gated and2704–2706 nongated. CUTLASS `TmaStoreFence.wait` is `cp_async_bulk_wait_group(num_stages-1, read=True)`. Thus the next slab's TMEM/register work waits early; moving that wait is lifetime-sound only if the same issuing warp waits and all shared writers join before their next overwrite. Publication fences/joins and terminal drain remain independently required. Current gated FC1 uses TMA even for padded tails; nongated FC1/FC2 keep SIMT partial tails. Partial SIMT stores do not advance or touch the TMA shared ring.

Searches of this project's Markdown, descriptor patches, W4 hybrid notes and the original W4 optimization ledger found no isolated non-descriptor FC1-only late-acquire trial. This is a bounded history search, not a proof no other artifact exists. A new FC1 test needs source-bound evidence that its output acquire contributes a real bubble; no production edit, source copy or GPU run is authorized by this audit alone.
