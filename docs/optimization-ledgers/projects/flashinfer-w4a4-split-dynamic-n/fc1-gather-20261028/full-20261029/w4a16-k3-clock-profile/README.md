# K3 EP prefill: read-only clock diagnostic

The retained W4 FC1 Gather4 kernel remains unchanged. This repeats the old-prepare and retained-gather K3 EP8 4096/8192-token traces with the same frozen tactics and exact input/routing identity, and adds a separate host process reading NVML. All source/tactic/input/cache/timing guards passed. GPU6 is exclusive to this experiment; B300, CUDA13.2, strict CUPTI, 10 warmups/100 samples, cold L2, graph replay, unfused.

The capture observer records existing correlated CUPTI activity records after all GPU timing has completed; removing that observer restores the original timing function's exact AST. The sampler performs read-only NVML and CUPTI timestamp queries, never creates a CUDA context, and never changes clocks, power, work or synchronization. Polling can affect host scheduling, so this is diagnostic evidence and does not replace the full104 retention results.

| Source | Tokens | Median µs | Quartile means µs | Observed SM MHz during timing | Clock-event mask |
|---|---:|---:|---|---|---|
| old prepare | 4096 | 535.154 | 535.40 / 533.18 / 535.51 / 595.75 | 2032 | 0 |
| retained gather | 4096 | 543.7775 | 541.84 / 538.81 / 566.60 / 599.89 | 2032 | 0 |
| old prepare | 8192 | 997.843 | 913.57 / 958.97 / 998.98 / 1045.80 | 2032 → 1980 | 0 |
| retained gather | 8192 | 1006.755 | 913.73 / 964.11 / 1022.48 / 1054.14 | 2032 → 1567 | 0 |

Memory clocks remained 3996MHz, sampled temperatures31–40°C. NVML updated some values only every~100ms despite2ms polling, so the samples show clock variation but cannot resolve/prove the cause of every late-sample slowdown. In particular, the4K slowdown occurs while the reported clock remains2032MHz. No thermal, power-cap or other clock-event flag was observed. Do not infer that the clock transition alone caused the measured source difference.

The earlier normal C-A-A-C run (`../w4a16-k3-ep-profile`) had7.72%/9.56% control-phase spread; these within-run quartiles explain why an isolated~1% comparison is insufficient for retention. A controlled fixed-clock diagnostic can distinguish DVFS from kernel behavior, but no clock change has been made in this experiment.

Artifacts: `analysis.json` aggregates, `samples.csv` all400 kernel samples matched to nearest read-only clock sample (maximum1.004ms distance), `evidence/` immutable source/config/observer/timeline/NVML receipts and raw samples. `analyze.py` reproduces the table. Helper: `../clock-telemetry/nvml_clock_wrapper.py`.
