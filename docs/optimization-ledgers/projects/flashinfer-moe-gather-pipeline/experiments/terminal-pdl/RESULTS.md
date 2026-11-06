# Terminal PDL wait removal: fixed-winner screen

**Rejected after the separate same-GPU ACCA follow-up.** The complete 56-cell screen is near neutral: **−0.0373% overall**, **+0.0895% decode (4 tokens)**, and **−0.1640% prefill (16,384 tokens)**. All 25 negative cells remain in the report. This does not establish a throughput improvement. The three targeted prefill losses also occur in the separate reverse-order follow-up, and two actual FC2 native winners grow registers. The original screen remains intact; no full refresh or shape-specific rescue will run.

Control is the immutable production-equivalent `02de7785` snapshot (`candidate-composed`); candidate is the same 13,245-file inventory except the three-line terminal MMA/scheduler PDL-wait deletion, kernel SHA `ec0f3685f42df89160ad1840ad561e728ec757623327bdb2ced29e51d74adb02`. Materialized snapshots have no Git metadata; the complete frozen manifests identify the tested bytes.

- 23 jobs, 28 supported swap arms × 2 token counts; all four model families, EP and TP, every supported swap mode. W4A16 is unchanged and excluded.
- Same physical GPU for each full C–A–A–C job; strict cold-L2 CUDA-graph CUPTI, 10 warmups and 100 samples per cell per phase; NVFP4 input quantizer included. Frozen routes/native choices, no retuning, timing fallback, clocks changes, trimming, or sample replacement.
- Cell speedup = `100 * (sqrt(C1*C2 / (A1*A2)) - 1)`, where each phase value is its 100-sample median. Group means are geometric means of cell ratios. Repeat spread and every raw phase are preserved.
- All 22,400 samples replayed, 448 loaded MoE resource records pass with zero local bytes, all source/route/tactic/cache bindings pass. All 896 NVML quartiles are available; 53 have median SM clock other than 2032 MHz or a nonzero observed throttle reason.
- Source inventories match before/after. The four existing C++ release libraries and generated Ninja descriptions are byte-identical across both arms and remain unchanged/no-op after execution. GPUs 3/4/5/7 are idle and released.
- Qualification: six numerical pairs plus four graph cases per arm (active/empty/partial routes), static/CLC, PDL on/off, one/two CTA. All 27 paired kernels have zero stack/local bytes; unaffected FC1/combine/PDL-off cubins are byte-identical. Nine affected FC2 captures remove one ACQBULK and 2–5 non-NOP instructions; five reduce registers by two, none increase. These are the qualified shapes, not a claim that every timed native winner has a captured ELF.

| Group | Cells | Geometric speedup | Negative cells |
|---|---:|---:|---:|
| band/decode | 28 | +0.0895% | 9 |
| band/prefill | 28 | -0.1640% | 16 |
| band/all | 56 | -0.0373% | 25 |
| mode/CuteDSL MXFP4x8 | 14 | -0.0601% | 7 |
| mode/CuteDSL MXFP8 | 10 | -0.0296% | 3 |
| mode/CuteDSL PER-TOKEN | 16 | -0.0858% | 8 |
| mode/CuteDSL W4A4 | 16 | +0.0263% | 7 |
| model_topology/kimi-k3/ep | 6 | -0.7828% | 5 |
| model_topology/kimi-k3/tp | 6 | -0.0441% | 4 |
| model_topology/nemo3-ultra/ep | 8 | +0.6999% | 1 |
| model_topology/nemo3-ultra/tp | 8 | -0.3002% | 3 |
| model_topology/v3/ep | 8 | +0.1795% | 3 |
| model_topology/v3/tp | 8 | +0.0442% | 1 |
| model_topology/v41-flash/ep | 8 | -0.2314% | 6 |
| model_topology/v41-flash/tp | 4 | -0.0550% | 2 |

The leading regressions are listed below only to make the unresolved cases visible; the full table contains all 56 rows. Low between-repeat spread alone is not a statistical confidence claim, particularly when clocks and within-phase trajectories vary.

| Model/topology/mode | Tokens | Speedup | Control spread | Candidate spread | Observed SM MHz |
|---|---:|---:|---:|---:|---|
| ep-kimi-k3-mxfp / CuteDSL MXFP4x8 | 16384 | -2.6192% | 0.4232% | 0.4923% | 1267/1335.0/1387.0/2032 |
| tp-nemo3-ultra-mxfp / CuteDSL MXFP8 | 16384 | -1.9930% | 0.7392% | 0.2872% | 1582/1612.0/2032.0 |
| ep-kimi-k3-per-token / CuteDSL PER-TOKEN | 16384 | -1.9547% | 0.1983% | 4.1432% | 2032.0 |
| ep-v41-flash-mxfp / CuteDSL MXFP8 | 16384 | -1.7396% | 4.5619% | 2.9905% | 1440.0/1875.0/1972.0/2032 |
| ep-v3-mxfp / CuteDSL MXFP4x8 | 16384 | -1.0045% | 0.9869% | 4.6435% | 2032 |
| tp-nemo3-ultra-mxfp / CuteDSL MXFP4x8 | 16384 | -0.8103% | 1.9469% | 0.2729% | 1777/1830/1837/2032 |
| tp-v41-flash-per-token / CuteDSL PER-TOKEN | 16384 | -0.4445% | 0.0325% | 0.0548% | 2032.0 |
| ep-v41-flash-per-token / CuteDSL PER-TOKEN | 16384 | -0.2781% | 0.0336% | 0.2094% | 2032.0 |

K3 EP MXFP4x8 16K is −2.6192%, with 0.4232%/0.4923% C/A repeat spreads. Its component medians show +28.841 µs E2E, +19.896 µs FC1 exposed extension, and +6.9765 µs FC2 exposed extension. FC1 is source-unaffected, but that is attribution context, not grounds to discard the loss or infer native binary identity. All four phases drift from roughly 974–986 µs in Q0 to 1164–1191 µs in Q3; clock drops differ across phases. `screen/k3-prefill-initial-trajectory.json` preserves the complete original trajectory. No overlapping kernel durations are summed into an invented critical-path total.

Evidence:

- [Full 56-cell table](../../evidence/terminal-pdl-screen/1793367348696239000/report/table.md) and [machine-readable cells](../../evidence/terminal-pdl-screen/1793367348696239000/report/cells.csv).
- [All phase components](../../evidence/terminal-pdl-screen/1793367348696239000/report/phase-components.csv) and [component deltas](../../evidence/terminal-pdl-screen/1793367348696239000/report/component-deltas.csv).
- [Raw replay summary](../../evidence/terminal-pdl-screen/1793367348696239000/report/summary.json), [fetch receipt](../../evidence/terminal-pdl-screen/1793367348696239000/fetch-receipt.json), and [execution/cache/idle postflight](screen/execution-complete.json).
- [Numerical/codegen qualification](../../validation/terminal-pdl/summary.json), [source safety review](../../audits/terminal-pdl-peer.md), and [screen peer review](screen/peer-review.json).
- [Held full-refresh plan](full-refresh-plan.json): 308 additional AA swap cells, 56 source-identical candidate screen cells, and 104 source-equivalent unchanged W4 cells. No new launch authorized by this document.

The separate ACCA follow-up preserved the original physical GPU UUID for each case and all 1,200 samples. Results were K3 EP MXFP4x8 **−3.9672%** (C/A spreads 4.3512%/1.7784%), N3U TP MXFP8 **−1.1043%** (0.3593%/0.4687%), and V41F TP per-token **−0.3642%** (0.0137%/0.0012%). No original value is replaced or pooled into a new preferred result. See [both order blocks and phases](reverse-order/COMPARISON.md).

The 24 actual native captures show byte-identical FC1 images across arms. FC2 registers are K3 **108→108**, N3U **106→118**, and V41F **150→152**, with no local bytes/LDL/STL and unchanged maximum-thread attributes. The small-case qualification missed the latter resource increases in actual native benchmark winners. FC2 removes one ACQBULK in each case, but fewer instructions do not justify the repeated losses. N3U candidate and V41F control have two same-PTX ELF variants differing at 9/7 uniform-register operand sites; addresses, nonuniform operands, control words and resources match. Every image remains saved; no universal binary-identity or no-timing-effect claim is made.

The parent rejected this experiment. Main source and published PR remain `02de7785`; no performance publication changes were made. Only the rejected local review worktree/branch were removed after exact source/patch/status checks and preserving its ignored Ruff cache. Immutable remote sources, both timing campaigns, all helper scripts, native images and failed CPU preparation/audit attempts remain. See [retirement receipt](retirement/receipt.json).
