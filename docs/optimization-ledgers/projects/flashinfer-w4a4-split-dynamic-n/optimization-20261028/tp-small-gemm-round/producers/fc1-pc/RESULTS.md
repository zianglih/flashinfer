# N3U EP8 MXFP4x8 FC1 PC audit

Source `1054743780dda2919c1424124c1e3258248b8c19`, tokens 16,384, frozen 83df winner/routes. Nsight Compute 2026.1.1.0 SourceCounters used seven application-replay passes, clock/cache control none. Raw report/source CSV and full source binding are in `ncu-evidence/`; transferred files verified by `ncu-evidence-verification.json`.

- 3,516 of 3,543 barrier samples occur at the final 256-thread teardown join. Keep it: completed producer/scheduler roles wait for epilogue/MMA completion before shared resource destruction.
- Long-scoreboard samples concentrate at epilogue accumulator-full and producer operand-ring empty waits, with smaller MMA full/empty waits. This does not establish removable synchronization or support adding independent operand pipelines.
- The hot epilogue contains repeated TMEM transposes and quantization instructions. Closed transpose/absmax proposals were checked against prior rejected ledgers before selecting two smaller leads.
- At PC 0x36a0 and 0x3a10, the same SF32 absmax register feeds two separate scale conversions/inverse calculations, one for each 16-channel store. Share these pure parameters while retaining existing SF/payload store ownership; no new shared-memory joins.
- First filter the algebraically equivalent SF row padding formula with exact/codegen comparison. No timing claim from profiler duration.

See `analysis.json` for exact per-PC counters and hashes. Sampling/compiled static counts are diagnostics; replay changes concurrency and cannot be subtracted directly from a different NCU pass.
