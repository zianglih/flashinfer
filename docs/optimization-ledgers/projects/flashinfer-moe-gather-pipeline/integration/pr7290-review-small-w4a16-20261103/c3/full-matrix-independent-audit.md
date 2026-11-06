# Full B300 matrix: independent audit

Passed all source/choice/result/render checks for 8 jobs / 24 workloads / 48 comparisons / 48 phases / 14,400 CUPTI samples. Raw spans were independently reconstructed from host launch correlations and GPU activities. All phase hashes, routes, frozen key/tactic choices, current resolved configurations, CSV/table values and all 48 SVG labels agree. The PNG was visually inspected and is correctly ordered/readable.

| Scope | OFF speedup | ON speedup |
|---|---:|---:|
| ALL | +2.707135% | +3.561797% |
| EP | -0.600896% | +0.830513% |
| TP | +6.125258% | +6.367065% |

OFF has 6 negative comparisons, all EP; ON has 3, all EP. The worst OFF and ON cells are both V3 EP8 / 8 tokens: −7.1208% and −3.8991%. Positive overall aggregates therefore do not imply uniformly preserved performance.

All 144 measured phase/token windows and all 576 quartiles have NVML coverage. Every observed SM clock is2032MHz, memory clock3996MHz and event reason0. Maximum repeat spread is0.4664%. No negative cell was excluded or replaced.

## Separate V3 EP8 / 4-token pilot

| Dataset | GPU | Before (µs) | OFF (µs) | OFF speedup | ON (µs) | ON speedup |
|---|---:|---:|---:|---:|---:|---:|
| pilot | 0 | 50.5365 | 53.1840 | -4.9780% | 51.4807 | -1.8340% |
| results | 2 | 50.4165 | 52.7525 | -4.4283% | 50.2319 | +0.3674% |

Pilot and main use the same source references, benchmark/config/observer hashes, route identities, frozen choices and current resolved configurations; process-local library handles differ as expected. They execute on different physical GPUs (pilot GPU0; main GPU2). Both runs show the OFF regression. The ON sign flip accompanies a reduction in its FC1 timeline-extension medians from33.152/33.440µs in the pilot to32.128/32.000µs in the main run; sampled clocks remain2032/3996MHz in both. Temperature is37°C in the pilot and31–32°C in the main run, without sampled throttling events. This localizes the observed timing difference but does not prove its mechanism. Treat the small main ON gain as a near-neutral observation with cross-run variation; keep pilot and main evidence separate.

This fixed-choice audit performs no new GPU work, retuning, production edits, or native ELF verification. Full source postflight now also passed: 31,069 before and34,762 current content files match the independently audited manifests, and all five native-data links point into each source. Fresh native-autotune and native ELF checks remain separate. B300-origin frozen choices match the declared experiment; each before/OFF comparison preserves the baseline tactic/layout, while ON has its own retained winner.

Evidence: `full-matrix-independent-audit.json`, `audit_full_matrix.py`, `v3-pilot-main-comparison.json`, and the two `v3-*-components.json` files.
