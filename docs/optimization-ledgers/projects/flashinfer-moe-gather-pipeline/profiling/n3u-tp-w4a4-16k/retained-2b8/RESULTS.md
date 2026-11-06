# Retained N3U TP8 T16384 W4A4 FC1 metrics refresh

**The high-MIO signal persists on the current implementation:** 8.37% MIO throttle versus 9.81% in the old TP capture, and 2.00% in the freshly measured wide EP capture. The unchanged SF copy pattern makes lane coalescing worth further attribution; these aggregate metrics do not by themselves justify a source prototype.

- **Source/runtime:** retained `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`, swap kernel `482b636a…`, recovery C2 B300 GPU3, `nvcr.io/nvidia/pytorch:26.05-py3`, driver595.91.07. Full13,245-file source pre/post checks and release ELF/Ninja checks pass. Existing cache remains unchanged. GPU3 is released, no PIDs/0MiB/0% utilization.
- **Native contract:** same original TP routes and frozen tactic as the old PC capture: route256, FC1 M128/N256/C1/K256/four operand stages, FC2 M256/N256/C2; static persistent scheduling, swap-AB, unfused, functional API, initial quantization included. No retune, source edit, compiler-option change or benchmark replacement.
- **Capture:** one NCU aggregate-metrics command, five application replays. All five current FC1 images are identical: cubin `db9cf0157a08bef023af8c67b2830bd52b9eeb13d73a3e97e6b7538234d47551`;168 initial registers,384 maximum threads, LOCAL0,222,208B dynamic shared memory. FC2 is captured/guarded too but not profiled. Native benchmark arguments, routes and cache hits are verified in every replay.

| Metric | Old TP822 | Retained TP2b8 | Retained wide EP2b8 |
|---|---:|---:|---:|
| Diagnostic FC1 duration (us) |475.680|427.744|290.176|
| Tensor activity (%) |16.24|18.06|26.52|
| DRAM throughput (%) |14.90|16.51|25.56|
| L2 throughput (%) |39.96|36.71|41.23|
| L2 hit (%) |76.46|77.44|72.34|
| Issue activity (%) |29.71|31.63|32.57|
| Long scoreboard (%) |54.44|55.24|53.98|
| Short scoreboard (%) |4.18|4.51|6.47|
| MIO throttle (%) |9.81|8.37|2.00|
| Barrier (%) |8.90|8.91|13.59|
| LSU global read sectors |58,518,633|58,518,633|28,657,718|
| Dynamic shared memory (B) |222,208|222,208|189,440|

The old TP uses a different node/source cohort, and EP uses different model partition/geometry. These profiler durations are not a causal performance comparison. The unchanged TP read-sector count and similar MIO/scoreboard pattern are mechanism evidence only.

## What is and is not identical

The entire gather-warpgroup source subtree and `_copy_gather_sf` inline-PTX helper are AST-identical from old822 to retained2b8 (`gather-source-identity.json`). This covers route ownership, zero-fill predicates, shared destination layout, all stage/arrival logic and payload task construction.

`sf-native-identity.json` verifies the actual current eight4-byte SF `LDGSTS.E.LTC128B` copy sites plus one `ARRIVES.LDGSTSBAR`. The copy sites retain their predicates, source `+0/+4/+8/+12` offsets,512B shared strides, instruction order and cache modifiers. Their PCs moved by−0xe00. Current source/destination registers map to the old names as R17→R0, R20→R56 and R18→R66. PTX independently specifies4-byte copies: `LTC128B` is not a128-byte transaction claim.

The surrounding instructions were rescheduled and registers renamed. **The full native gather block is not byte-identical**, and the full FC1 differs due to retained MMA-descriptor/epilogue work. Exact old/current excerpts are saved, without hiding those differences. Both functions still have168 registers and zero local allocation; `MOV.SPILL` in this region is uniform-register transfer, not evidence of local-memory spilling.

Old source-bound TP PC evidence attributed1,731 MIO observations to SF copy issue plus255 at completion, versus227 at Gather4 issue. Those counts remain historical observations, not fresh current-code counters. A single current SourceCounters pass is appropriate if the parent proceeds toward the lane-coalescing experiment: it will distinguish persistent SF issuing pressure from nearby scheduling or other MIO effects. **No current PC pass or source prototype has been launched.**

## Evidence

- `fc1-metrics/raw.csv` / `ncu.log` / `profile.ncu-rep`: complete native profiler output.
- `fc1-metrics-fetch.json`, `controller-receipt.json`, `gpu3-release.json`: archive/source/cache/runtime/idle checks.
- `metrics-summary.json`, `gather-source-identity.json`, `sf-native-identity.json`: replayable derived receipts; scripts beside them reconstruct every check.
- `setup.json` and `expected-held.json`: exact TP choice and routing identity match the original saved PC run.

The previous EP conclusion remains scoped to wide EP; this TP refresh prevents incorrectly generalizing its low MIO pressure to all shapes. Any future implementation must remain a general compile-time ownership policy, without TP/model-specific switches.
