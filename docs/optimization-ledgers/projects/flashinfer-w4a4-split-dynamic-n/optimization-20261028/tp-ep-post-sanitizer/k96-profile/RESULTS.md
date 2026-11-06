# Retained K96 V3 prefill pipeline diagnostic

Runtime source files are byte-identical to `2cfb06afd` (K64) and `21fbe72c` (K96): all 344 pinned runtime files verified independently against both Git commits. V3 EP8 / TP1, 16,384 tokens, W4A4, unfused swap-AB, input quantization included, identical saved winning tactic. Primary B300 GPU7; 20 cold-L2 graph replays per NSYS capture and one FC1/FC2 capture per NCU arm with five application-replay passes. Managed cache selections are checked, no tuning is allowed, source/cache hashes remain unchanged. Every capture uses a private working directory. GPU7 is released.

All 28 raw reports/CSV/SQLite/source and winner receipts are fetched and hash-verified; archive SHA `e233e02820de4175122aaa9a2011edd24b8b86a4d90cfefd5173b1c85c02b473`. These diagnostic captures do not replace the matched CUPTI retention medians. NCU replay perturbs overlap and clocks/caches are not forced.

| Stage | K64 NSYS duration / critical extension µs | K96 NSYS duration / critical extension µs |
|---|---:|---:|
| Input quantizer | 51.06 / 51.06 | 50.67 / 50.67 |
| Prepare | 25.38 / 25.18 | 25.38 / 25.18 |
| FC1 | 184.50 / 179.60 | 175.01 / 170.06 |
| FC2 | 140.98 / 123.31 | 136.69 / 123.68 |
| Combine | 88.30 / 84.27 | 86.42 / 82.51 |
| Whole graph | 501.99 | 490.90 |

Critical extension measures the amount by which each kernel extends the latest completion time; it avoids adding overlapping PDL durations. The table omits the three unchanged routing stages (their raw data remain in `evidence/summary.json`). Stage medians need not sum to the graph median. About 40% of the K64 graph's critical path is outside FC1/FC2. FC1's extension falls by 9.54µs, while FC2's extension is effectively unchanged. FC2's shorter visible duration alone therefore does not demonstrate a corresponding pipeline improvement. The trace's +2.26% whole-graph result is consistent in direction with the retained +1.61% CUPTI row, not a replacement measurement.

| NCU metric | K64 FC1 | K96 FC1 | K64 FC2 | K96 FC2 |
|---|---:|---:|---:|---:|
| Duration µs |184.00|176.19|127.46|128.42|
| Tensor active / elapsed % |67.39 /62.69|51.36 /48.21|45.19 /42.98|33.34 /31.62|
| DRAM read / write MB |610.79 /67.77|612.80 /67.73|285.61 /205.35|285.95 /203.80|
| Long scoreboard % |55.56|55.82|42.51|42.76|
| Barrier % |19.20|19.21|23.15|23.57|
| Wait % |8.27|8.63|17.72|17.61|
| Eligible warps/cycle |0.15|0.16|0.16|0.16|
| Executed warp instructions, millions |25.744|26.131|20.348|20.515|
| Registers/thread |78|80|118|122|
| Dynamic SMEM bytes |195328|195584|229632|230400|

The lower tensor-active percentage is not evidence of less useful arithmetic: the logical GEMM is unchanged. Combining average active cycles with tensor-active percentage gives approximately 200,123→150,096 FC1 tensor-active cycles and100,072→75,047 FC2 cycles, a ratio near 0.75 in both cases, matching four→three MMA instructions per K256 stage. Yet memory traffic and long-scoreboard/barrier/wait proportions are almost unchanged, and overall issued warp instructions rise 1.50%/0.82%. This supports a narrower conclusion: K96 reduces tensor issue/activity, but much of this chain is limited by work it does not remove. Aggregate counters do not locate the long-scoreboard or barrier stalls to a particular warp/PC, so they do not justify deleting a synchronization.

Frozen-winner SASS backs that interpretation: K64→K96 has four→three MMA sites per stage, unchanged 12 SF-copy sites and unchanged synchronization sites. FC1/FC2 total static instructions increase 5496→5536 and2408→2424; FC2 uniform-register spill/fill pairs 19→21. Both retain zero local-memory/stack use. Operand stages and epilogue scratch counts are unchanged; the slightly larger physical SMEM follows alignment. K96 descriptor reuse reduced reconstruction versus the earlier K96 prototype, but did not remove SF publication or output traffic.

The current compact FC2/TMA-output experiment targets the unchanged output movement/issue work identified here. No extra stage-width experiment or synchronization removal follows from this one-shape profile.
