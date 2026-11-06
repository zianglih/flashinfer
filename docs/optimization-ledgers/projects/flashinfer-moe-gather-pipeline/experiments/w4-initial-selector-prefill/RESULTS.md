# Fresh W4 prefill: 82254e20 → 02de7785

The complete same-session matrix is **+0.434% geometric-mean speedup**, with **7/24 negative cells**. It does not reproduce a broad prefill regression from the initial W4 scale-selector change. The adverse rows remain in full; the K3 EP16K loss is an unresolved adverse observation, not discarded as noise.

Control is actual immutable `82254e206a44b95d9925e4594fac936731f80d21`; candidate is the immutable base822 snapshot plus the exact patch committed as `02de7785c10847b3528340840bed40bd405d85b4`. Both 13,245-file inventories passed before/after. The two changed files are the W4 scale-selector utility and the swap kernel, which this W4-only run does not invoke. Historical measured326/production-equivalent822 comparison rows are not substituted into this paired result.

All eight original jobs use the frozen routes/choices, including 14 explicit choices and ten recorded defaults, with C–A–A–C order, 10 warmups and 100 strict CUPTI samples per phase in cold-L2 CUDA Graphs. No retuning, event fallback, NCU, sanitizer, source edit, or historical native-library restoration. All four current release C++ ELF/Ninja fingerprints stayed unchanged and no-op. GPUs1–4 passed idle postflight and were released.

Validation: 9,600 raw spans, 96 phase medians, 120 loaded LOCAL0 function records, 48 unchanged measured FC-stage resource configurations, and 80 actual default-stage/resource joins. Clock coverage is 384 quartiles: 100 have non2032 median SM clock or a nonzero reason, zero are missing. None of the seven losses has both repeat spreads ≤0.5%; this is only a descriptive repeat threshold, not statistical confidence. Positive rows with variation are also preserved.

E2E speedup is `sqrt(C1*C2/(A1*A2))-1`; all group aggregates are geometric means. Component deltas below use the arithmetic mean of each arm's two phase medians, in microseconds. Overlapping kernel durations and medians must not be summed to reconstruct E2E. The separate critical-extension columns show each stage's extension beyond the preceding completion; they are descriptive attribution, not a new timing estimator.

## Complete matrix

| Model | EP/TP | Mode | 4096 | 8192 | 16384 |
|---|---|---|---:|---:|---:|
| kimi-k3 | EP8 | CuteDSL W4A16 | -1.445% | +2.037% | -1.464% |
| kimi-k3 | TP8 | CuteDSL W4A16 | -1.248% | +0.826% | +0.731% |
| nemo3-ultra | EP8 | CuteDSL W4A16 | -0.058% | +0.598% | -0.149% |
| nemo3-ultra | TP8 | CuteDSL W4A16 | +0.097% | +1.612% | +0.595% |
| v3 | EP8 | CuteDSL W4A16 | -0.003% | +0.910% | +1.506% |
| v3 | TP8 | CuteDSL W4A16 | +0.063% | +1.938% | +0.465% |
| v41-flash | EP4 | CuteDSL W4A16 | +0.971% | -0.642% | +0.595% |
| v41-flash | TP4 | CuteDSL W4A16 | +1.161% | +1.311% | +0.113% |

EP aggregate: +0.2324%; TP aggregate: +0.6354%.

## Every negative row

Positive Δ means slower candidate. The complete phase and clock trajectories follow in [negative-details.md](negative-details.md).

| Cell | E2E speedup | C/A repeat spreads | ΔE2E µs | ΔFC1 µs | ΔFC2 µs | Δcombine µs | Clock exceptions /16 |
|---|---:|---:|---:|---:|---:|---:|---:|
| K3 EP8 / 4096 | -1.4454% | 5.081/4.056% | +8.192 | +2.927 | +3.832 | +0.656 | 0 |
| K3 EP8 / 16384 | -1.4640% | 1.433/0.916% | +29.704 | +14.024 | +13.752 | +5.208 | 11 |
| N3U EP8 / 4096 | -0.0582% | 0.463/0.596% | +0.232 | -0.016 | +0.288 | +0.176 | 0 |
| N3U EP8 / 16384 | -0.1494% | 8.085/5.490% | +1.664 | +11.664 | +2.392 | -1.569 | 7 |
| V3 EP8 / 4096 | -0.0033% | 0.680/0.061% | +0.008 | -0.480 | +0.456 | +0.104 | 0 |
| V41F EP4 / 8192 | -0.6420% | 6.065/4.345% | +4.424 | +3.384 | -0.592 | -0.968 | 0 |
| K3 TP8 / 4096 | -1.2478% | 1.654/5.016% | +9.048 | -0.528 | +6.736 | -0.336 | 4 |

| Cell | ΔFC1 critical extension µs | ΔFC2 critical extension µs | Δcombine critical extension µs |
|---|---:|---:|---:|
| K3 EP8 / 4096 | +2.903 | +3.856 | +0.184 |
| K3 EP8 / 16384 | +14.048 | +13.768 | +0.440 |
| N3U EP8 / 4096 | -0.008 | +0.288 | +0.024 |
| N3U EP8 / 16384 | +11.648 | +2.448 | +0.536 |
| V3 EP8 / 4096 | -0.472 | +0.264 | -0.008 |
| V41F EP4 / 8192 | +3.375 | -0.033 | +0.112 |
| K3 TP8 / 4096 | -0.391 | +6.441 | +0.680 |

## Interpretation

- **K3 EP8 / 4096:** Both FCs move slower; 5.08/4.06% repeat spreads overlap. Clocks remain 2032/reason0, so clock telemetry alone does not explain the variation. Not a stable FC1-only loss.
- **K3 EP8 / 16384:** Both candidate E2E phases are slower than both controls. FC1 and FC2 contribute similarly; 11 clock-exception quartiles and different throttling trajectories prevent clean instruction-local attribution. Preserve as an unresolved adverse observation.
- **N3U EP8 / 4096:** Near-neutral loss; FC1 is slightly faster and FC2 slightly slower. Not an FC1 regression signal.
- **N3U EP8 / 16384:** Large 8.08/5.49% phase spreads, mixed clocks, and phase-overlapping medians. No stable source-local regression established.
- **V3 EP8 / 4096:** Near-zero E2E change; faster FC1 offsets slower FC2. Not an FC1 regression signal.
- **V41F EP4 / 8192:** FC1 is slower, but 6.07/4.34% phase spreads exceed the 0.64% point estimate. Both candidate phases lie within the two control E2E medians; normal clocks do not remove this repeat variation.
- **K3 TP8 / 4096:** FC1 is slightly faster; most measured critical-extension growth is in FC2. Candidate spread is 5.02% and four clock-exception quartiles retain reason4 despite median2032MHz. Not an isolated FC1 selector loss.

The 02de native qualification previously showed six fewer FC1 SHF instructions and unchanged FC2/finalizer raw cubins in four tested tactics. This fresh campaign verifies actual loaded resources and resolutions, but does not capture every timed native image; it therefore does not assert raw-cubin identity for every cell. A slower downstream FC2 span can reflect scheduling or other variation and does not, on its own, prove either a direct FC2 code change or harmless noise.

K3 EP16K is the strongest adverse row: both candidate medians exceed both controls, and both FCs slow. A single same-GPU reverse-order ACCA on that cell would be a reasonable next diagnostic if authorized; the original CAAC must remain separate. No such follow-up is included in this report.

Together with the earlier commit trace, this does not identify a commit causing the broad 1–5% red cells in the historical public table. `bf072` has small observed prefill losses with documented repeats/clocks; `49c` changes only swap and reuses all W4 rows; `2b8` K3 primary and diagnostic prefill comparisons are nominally positive. These boundaries do not prove every retained change is regression-free.

## Evidence

- [Complete 24-cell raw/report leaf](../../evidence/w4-initial-selector-prefill/1793388462716534000): both candidate and control, all phases, native printed stdout, routes, frozen choices, clocks and source/cache receipts.
- [All four phase medians](../../evidence/w4-initial-selector-prefill/1793388462716534000/report/table.md) and [component CSV](../../evidence/w4-initial-selector-prefill/1793388462716534000/report/component-deltas.csv).
- [Source/current-cache preflight](screen/source-cache-preflight.json), [launch](screen/launch.json), [release postflight](screen/gpu-release.json).
- [Historical commit trace](../../audits/w4-prefill-regression-trace.md), [bf072 full paired table](../w4-tail-dequant/combined39/table.md), and [49c/2b8 attribution](../../audits/w4-prefill-attribution-situ/RESULTS.md).

No production or published evidence was changed. No repeat or further GPU work was run.

Independent full raw replay passed: [root receipt](../../audits/w4-initial-selector-data-root.json).
