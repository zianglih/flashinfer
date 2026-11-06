# N3U EP8 / 16K W4A4: unchanged-space retune holdout

The native existing-space search selected FC2 M512 in place of the frozen M256 choice. A separate same-source CAAC holdout finds **+0.002966%**, effectively neutral. Keep the original frozen choice; this diagnostic does not warrant changing PR results or kernel policy.

| Phase | FC2 logical M | Strict CUPTI median (µs) |
|---|---:|---:|
| Control0 | 256 | 557.2840 |
| Candidate1 | 512 | 557.1235 |
| Candidate2 | 512 | 557.5080 |
| Control3 | 256 | 557.3805 |

Phase-geometric means: control557.332248µs, candidate557.315717µs. Within-arm repeat spreads are0.0173%/0.0690%. All400 CUPTI activity spans were independently reconstructed; all16 telemetry quartiles report median2032MHz and no clock-event reasons. Source13,245-file pre/post inventories, unchanged current release ELF/Ninja files, original managed-cache inputs, copied caches, routing identity, native compiler/resource guards and zero profiling during replay all pass.

FC1 remains M512/N128/twoCTA/K256 with four operand stages,189,440B shared memory and168 registers. FC2 changes from one to two channel tiles: six→four operand stages,205,824→222,208B shared memory and98→108 registers. Both retain one resident CTA/SM and zero local memory. The two source records are byte-identical retained2b8; source helper hashes were unchanged.

FC2 median duration changes225.601→225.130µs, and its critical-path extension188.025→187.793µs. Those small differences do not change overall latency meaningfully; FC1 contributes about287.4µs of the critical path and combine about54µs.

The search and holdout are different timing domains. Native selection uses the existing eager event profiler and seeded balanced synthetic routing. Holdout uses CUDA Graphs, coldL2, strict CUPTI, the actual saved sigmoid routes and input quantization. The search took118.65s, including95.11s inside115 `cute.compile` calls;321 native profile calls consumed7.90s exclusive of nested compilation. These are host wall spans in a warmed persistent compilation cache, not isolated compiler CPU or cold-build costs. The observer did not retain individual native selection scores, so old/new event-score margins cannot be reconstructed.

Preserved failures: the initial search R0 missed the historical outer bucket restriction and was stopped without a usable final public measurement. Holdout R0 stopped before its first phase because an extra reference-only check expected a newer field in the historical result schema. R1 handles the two known schemas explicitly; every measured phase still requires zero profiling. Both failed leaves remain intact.

Evidence: `evidence/evidence/`, `report/summary.json`, `report/analysis.json`, `report/component-replay/component-samples.json`, `audit.py`, and `gpu-release.log`. GPU0 was released idle. No production edit, frozen-cache overwrite, new tactic, or public-table update.
