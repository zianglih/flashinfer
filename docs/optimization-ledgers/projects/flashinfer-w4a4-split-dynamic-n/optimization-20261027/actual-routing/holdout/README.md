# Bounded serving-warmup holdout

This checks whether the experimental matching-profile input hook is safe to
retain when an EP rank's autotuning warmup is unrepresentative of later traffic.
It is separate from the three-cell benchmark and changes no production source.

- Source: candidate `1e69d0a39` plus the unchanged two-file actual-routing patch.
- Fixture: the public N3U EP8 PER-TOKEN4096 benchmark, with its original weights,
  hidden values, 4over6 recipe, deterministic combine, and included input
  quantization. Valid unique top-K expert IDs are supplied through the
  benchmark's existing precomputed routing input.
- First warmup: every route targets a remote expert, so this rank has zero local
  work. Normalized routing weights remain byte-identical to the original case.
- Selection: the existing candidate cache is copied with only the matching
  4096-token entry removed. All 19 nonmatching native entries are preserved;
  exactly one profile must be admitted, with the original 320-valid-tactic hash
  from the unchanged 360-tactic catalog. No winner is forced.
- Replay: existing real-trained winner versus new warmup-trained winner on the
  original real routes, C-A-A-C, cold L2, 10 warmups and 100 CUPTI samples/pass.
  CUDA-event fallback is forbidden. Both arms execute the same candidate source.
- If no stable regression greater than 5% occurs, repeat on independent seed77
  routing. A clear material regression is sufficient to stop this bounded test.
- The outer wrapper consumes only SystemExit(None/0); nonzero exits propagate.
  `cpu-gate.json` records the small no-GPU wrapper/fixture checks.

`warmup_observer.py` injects fixtures outside timing and delegates to the
unchanged native observer. `run_holdout.py` verifies source, cache geometry,
admitted tactics, prepared route identity, cold-L2 pointer preservation,
100 samples and frozen cache hits. It saves original raw results and routing
proofs; the old inner instrumentation's known SystemExit bookkeeping flag is
preserved, while native exit/result and the corrected outer wrapper establish
completion.

Runtime uses the existing task-owned C3 B300 CUDA13.2/CuTe4.8 environment and
source-private persistent compilation cache. GPU0 was verified idle before
launch; no compile cache is removed. Native NV profiling remains eager.
