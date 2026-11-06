# Isolated N3U TP16K intermediate quantizer

CAAC: control 429.698 / 430.514 µs; candidate 488.867 / 488.963 µs. Geometric phase-median ratio: -12.029%. Repeat spreads: control 0.190%, candidate 0.020%.

All 400 native CUPTI spans replayed. Exactly one quantizer per timed graph; active PDL retained. All 16 clock quartiles were checked: 0 exceptions, 0 missing. Actual loaded native images/configurations match the prior K640 evidence: 61→48 registers, LOCAL0, 64 threads. All defined output bytes match.

The captured retained FC1 input and arguments are byte-identical across all four phases: allocation 491,008×640 BF16, 426,752 processed rows, 360,448 live rows, original row limits, precise base math and fast MSE 4over6/E4M3-256. Frozen tactic/routes, full source inventories, release native hashes/Ninja and private per-arm quantizer caches were preserved. No FC2 was launched in the replay processes.

This separate diagnostic does not replace the rejected 42-cell whole-chain screen and does not reproduce predecessor/successor PDL overlap. No isolated speed difference alone proves the cause of the whole-chain loss.

| Phase | Median (µs) |
|---|---:|
| 0-control | 429.698 |
| 1-candidate | 488.867 |
| 2-candidate | 488.963 |
| 3-control | 430.514 |

Full raw spans/activities, launch intervals, clock samples, native images and source/cache receipts are in `evidence/`. The captured input remains remote and is bound by file and individual tensor hashes. The initial failed plumbing attempt is preserved at `../isolated-intermediate`; it produced no quantizer timing.

Interpretation: the candidate adds about 58.81 µs in isolation (13.67% longer duration), despite fewer registers/static instructions. Original whole-chain TP16K quantizer durations remain control465.298/466.578 µs and candidate529.731/530.245 µs. Successor FC2 overlap is not required for the adverse timing. This does not identify the hardware cause or quantify overlap in the full chain; predecessor state and concurrent memory traffic differ. No further timing, profiling or policy change was performed.
