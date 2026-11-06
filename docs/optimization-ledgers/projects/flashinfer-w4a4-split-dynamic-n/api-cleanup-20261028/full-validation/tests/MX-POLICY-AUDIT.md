# MX graph tuning semantics: 17bff619c -> d1767be1

No unintended profiling-semantic change found. Autotuner and autotune_cache.py
are byte-identical between these commits. The old wrapper/functional option
constructed the runner with `use_cuda_graph=True`; the new public graph policy
sets the effective TuningConfig to the same value before synthesis/search/profile.
The runner field itself is now False, but its remaining uses are only its hash,
cache extras, and initial TuningConfig: it does not affect kernel launch or tactic
admission (`tuner.py:552,679,716,739`).

| Profiling setting | Old | New |
|---|---|---|
| Graph | True in runner config | True from policy |
| Cold L2 | True | True inherited |
| Warmup | AutoTuner default 3 | Same 3 |
| Repeats | AutoTuner default 10 | Same 10 |
| Replays per sample | 1 | 1 |
| Cold chain | False | False |
| Timer | CUDA events | CUDA events (`MeasurementPolicy.timer`) |
| Estimator | Median isolated cold graph invocation | Same |
| Flush | 2x L2 before each sample, outside event interval | Same |
| Delay | `_CUDA_GRAPH_DELAY_MICRO_SECS` | Same |
| Input synthesis/hook/bucketing | Native MoE config | Same |

Anchors: `autotune_cache.py:127–239,696–713,869–908`;
`autotuner.py:551–576,1715–1718,1902–1945,2653–2674,3542–3647,3767–3833`.
Public end-to-end measurement remains CUPTI/100 samples; native candidate
profiling is CUDA-event based in both versions. Do not conflate those timers.

Intentional differences:
- v2 prepends `-1` to candidates for the first runner (`autotuner.py:2780–2786,
  2912–2917`). This can change the selected winner and the compilation/warm-state
  history before later candidates. The existing enumerated 360 tactics, their
  relative order, and their effective parameters are unchanged.
- Cache ownership is an explicit per-context managed store with policy namespace,
  rather than global v1 loaded-file/in-memory lookup. The graph marker moves from
  runner cache extras into the managed measurement identity. Fresh tuning does
  not consume old JSON winners. Replay uses the same policy and cannot retune.
- Removed unpublished version tags/old tactic normalization do not alter the
  current five-field enumerated tactics or their parameters.

No source/GPU changes were used for this audit. A new selected tactic being
slower on real routes may reflect probe-vs-serving distribution or tuning noise;
the source audit cannot attribute the observed K3 T8 difference to either.
