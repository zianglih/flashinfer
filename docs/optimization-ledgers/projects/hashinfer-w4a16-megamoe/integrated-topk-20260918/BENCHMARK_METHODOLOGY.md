# Current performance methodology

User update: September18,2026. This supersedes the older1–8192 retention
aggregate for future trials; old sealed evidence remains unchanged.

| Class | Global token counts | Retention role |
| --- | --- | --- |
| Decode | 1,2,4,8,16,32,64,128,256,512 | Primary objective; exclude only1/2 from decisions |
| Prefill | 4096,8192,16384 | Check every row for visible regressions |

1024 and2048 are excluded from performance sweeps because neither production
decode nor prefill uses that range.4 tokens now counts toward retention.
Keep1/2 in reported tables. A clear decode improvement may justify a very
slight prefill regression; do not hide prefill behavior in a combined average.
Use the4–512 geometric speedup as a concise decode summary, together with
individual rows and observed dispersion. No new numerical regression cutoff
has been specified.

Keep the established H7168/I2048/E256/top-k8/EP8, CUDA13.2 B300, full public
forward with precomputed routing, four-tactic AUTO/O3,3 warmups and100 cold-L2
CUDA-graph CUPTI samples per row. Report median per-iteration rankMAX latency
and before/after speedup. The deterministic path remains ordered FP32 combine
over BF16 FC2 outputs; the benchmark's historical `--no-fused-finalize` flag
selects that numerical contract even though staging and reduction are now
physically inside the MegaMoE kernel.

Benchmark candidates first. Run numerical/sanitizer qualification when a gain
warrants keeping a candidate; do not gate every performance trial on full
test suites. Source/lifetime review and useful generated-resource checks remain
appropriate. Already-completed validation is preserved. The accuracy test
Cartesian product is unchanged by this performance-only workload update.

Reuse source-bound same-node baselines for iteration. Existing baselines lack
16384, so measure that row before comparing a new13-shape candidate. Historical
overlapping rows plus a fresh16k control form an explicitly mixed-time trial
control, not a contemporaneous final pair. A final retained change requires
fresh confirmation and applicable correctness qualification.

PR bodies contain only the final before/after table for these13 shapes.
Incremental trial tables and execution history remain in this local ledger.

For the current final comparison only, the first main68/selected3de pair has
an unresolved16k slowdown despite all rows improving versus retained7dc.
Before observing additional results, request one complete reverse-order pair:
selected B2 then main A2. Report the median of all200 per-iteration rank-MAX
samples per row/source from A1+A2 and B1+B2, retaining every sample, per-run
summary and pair result. This is not a median of run medians. Disclose the
retained/banking control runs between A1 and B1; do not claim that reversal
cancels drift. Routine optimization trials remain one full13 sweep using
existing same-node controls.

The user subsequently accepted retaining the selected counter-lifetime
optimization for its useful decode gains, with any measured 16k slowdown
reported explicitly and addressed in later work. Finish the already-running
reverse confirmation using the predefined pooled200 statistic; do not request
additional timing repeats solely to eliminate that slowdown. Numerical and
sanitizer acceptance still applies before publication.
