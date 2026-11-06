# Retained group512 versus group256 — completed whole runs

**Rejected.** Retention 8–4096: **+4.222221% latency GM**, 0/10 wins. Full 13 secondary: +1.998146% GM, 3/13 wins. Tokens 1/2/4 do not enter retention.

| Tokens | Retained group512 ms | Group256 ms | Change | Retained tactic | Group256 tactic |
|---:|---:|---:|---:|:---|:---|
| 1 | 0.088848 | 0.081473 | -8.301% | M256/N64, C2, F8, epi, S2, G512 | M256/N128, C2, F8, epi, S2, G256 |
| 2 | 0.106513 | 0.099488 | -6.595% | M256/N64, C2, F4, epi, S2, G512 | M256/N64, C2, F8, epi, S2, G256 |
| 4 | 0.119937 | 0.119761 | -0.147% | M256/N64, C2, F8, epi, S2, G512 | M256/N64, C2, F8, epi, S2, G256 |
| 8 | 0.136065 | 0.141297 | +3.845% | M256/N64, C2, F8, epi, S2, G512 | M256/N64, C2, F8, epi, S2, G256 |
| 16 | 0.156082 | 0.172434 | +10.477% | M256/N64, C2, F8, epi, S2, G512 | M256/N64, C2, F4, epi, S2, G256 |
| 32 | 0.176594 | 0.196753 | +11.415% | M256/N64, C2, F8, epi, S2, G512 | M256/N64, C2, F8, epi, S2, G256 |
| 64 | 0.208803 | 0.211458 | +1.272% | M256/N64, C2, F8, epi, S2, G512 | M256/N64, C2, F8, epi, S2, G256 |
| 128 | 0.212625 | 0.223554 | +5.140% | M256/N64, C2, F4, epi, S2, G512 | M256/N64, C2, F4, epi, S2, G256 |
| 256 | 0.212626 | 0.218466 | +2.747% | M256/N64, C2, F8, epi, S2, G512 | M256/N64, C2, F4, epi, S2, G256 |
| 512 | 0.221554 | 0.224818 | +1.473% | M256/N64, C2, F8, epi, S2, G512 | M256/N64, C2, F8, epi, S2, G256 |
| 1024 | 0.239026 | 0.245107 | +2.544% | M256/N64, C2, F4, epi, S2, G512 | M256/N64, C2, F4, epi, S2, G256 |
| 2048 | 0.312035 | 0.313538 | +0.482% | M256/N128, C2, F4, reuse, S2, G512 | M256/N128, C2, F4, epi, S2, G256 |
| 4096 | 0.474036 | 0.490276 | +3.426% | M256/N128, C2, F4, reuse, S2, G512 | M256/N128, C2, F4, epi, S2, G256 |

Every full dictionary changes group_hint 512→256. N/flag/return selector changes occur at [1, 2, 16, 256, 2048, 4096]; 7 rows retain those selectors. Their latency changes: T4 -0.147%; T8 +3.845%; T32 +11.415%; T64 +1.272%; T128 +5.140%; T512 +1.473%; T1024 +2.544%. These sequential AUTO runs do not isolate a fixed-tactic or group-only effect.

Benchmark subprocess 601.491638550s versus retained 599.645277633s; outer 603.554998041s, timer utility 5.894709638s. Tuning/setup wall remains separate from each primary latency.

All 13×100 cold-L2 CUPTI samples reproduce the printed medians. The 13×8 secondary hot-score rankings, 104 winner dictionaries and 104 Mega resources agree. Activation stages {'3': 104}; raw stages {'4': 24, '5': 80}; scheduler stages {'2': 104}; local bytes {'0': 104}.

Separate staging observations remain 104 warmups: 87 fused nonempty and 17 empty Torch fallbacks, with all 80 retention observations fused. The eight rank-local staging callables remain separate from the Mega objects. Original saved checks report 23 native entries unchanged.

Source90a1 changes the factory group hint on published stagingd891. The saved numerical audit4516 reconciles eight E8 EP2 case passes and eight B3/raw5/S2/local0 objects across N128/N64 × group512/256. Source-derived boundaries from actual balanced routed IDs are not scheduler execution telemetry. Original49706 rendezvous failure produced no GPU case/resource records; unchanged-oracle localhost retry42662 passed. No additional graph/lifecycle or full-catalog numerical cohort is claimed.

The entire current run comes from original51022 and the completed original reconstruction/closure pinned in comparison.json. The baseline is the intact accepted staging9ce run. No original, baseline or native validator was rerun; no rows were replaced, spliced or adjusted.

[Full comparison and pins](comparison.json) · [Original reconstruction](../cu132-recovery0909d-group256-direct-auto-reconstruction-001/README.md) · [Saved numerical audit](../cu132-recovery0909d-group256-numerics-independent-001/audit.json)
