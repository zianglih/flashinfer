# Queued five-shape scorer experiment

This fresh sibling extends the completed T128 diagnostic to global tokens **128, 512, 1, 4096, 64**. It is CPU-prepared and unexecuted. Root schedules it after the independent 512-thread gates/performance work and must restore the exact saved C1 source first.

The five Python files are copied once from the completed `paired-tuner-metric-baseline128-002` experiment. `worker.py`, `timers.py`, `static_gate.py` and `run_experiment.py` are byte-identical; `protocol.py` only appends 64 to its token tuple. Original worker/experiment files remain untouched. `source-copy-manifest.json` and the outer wrapper prove those byte relationships, freeze the saved source/native identities, and preserve the old helper hashes.

The measurements remain hot prestaged full-forward scopes including the reducer, with ten raw samples, MAX of local medians across eight ranks, and three forward/reverse/forward passes through all sixteen tactics. Scorer order alternates and reverses as before. Graph inputs do not rotate; graphs are synchronized/reset before the next workspace invalidation. Input/weight/routing bytes and addresses, bitwise output gates, runtime libraries, actual geometry and all 48 visits per rank/shape are recorded. These are diagnostic host/event scores, separate from public CUPTI tables. No public policy or cache entry is written.

T64 is included because it is a published post-32-token slowdown. T128 is retained as an adjacent reference; the first run's top graph margins were only 0.288–0.608 us. Five shapes can test whether scorer disagreement generalizes without treating one near tie as a production conclusion.

Run from `/workspace/flashinfer-w4a16-megamoe` using the validated CUDA13.2 interpreter. The wrapper reuses only the completed same-stack native Torch/FlashInfer caches and allocates fresh DSL/driver caches. Its CPU plan records whether current source matches C1; execution rejects any other overlay. The original launcher supplies the two-hour timeout and explicit localhost rendezvous.

```bash
/usr/bin/python3 candidates/w4a16_tuner_metric_analysis/run_baseline_five_shapes_003.py

# Parent scheduling only, after exact C1 restoration and all cache writers exit:
/usr/bin/python3 candidates/w4a16_tuner_metric_analysis/run_baseline_five_shapes_003.py --execute
```

The fixed run name is `paired-tuner-metric-baseline-five-shapes-003`. Fetch its complete `logs/<run>/` directory, `<run>-native-cache-plan.json`, `<run>-wrapper-status.json` and the separately saved driver log. Then run:

```bash
python3 candidates/w4a16_tuner_metric_analysis/analyze.py \
  paired-tuner-metric-baseline-five-shapes-003 \
  --output logs/paired-tuner-metric-baseline-five-shapes-003-analysis
```

Expected evidence: 1,920 rank/visit records and 38,400 raw samples, retaining each shape/pass/rank/scorer. The prior four-shape wrapper draft is superseded and was never run. The completed T128 analyzer is frozen with its original result at `logs/paired-tuner-metric-baseline128-002-analysis/analyze-frozen.py`.
