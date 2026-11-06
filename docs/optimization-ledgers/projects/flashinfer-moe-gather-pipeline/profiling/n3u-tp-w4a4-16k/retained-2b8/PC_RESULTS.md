# Current TP FC1 PC follow-up

**The SF-specific MIO signal persists on retained2b8.** The current TP capture has1,341 MIO observations at the eight4-byte SF copies plus177 at their completion instruction, versus232 at Gather4 issue. Together with aggregate MIO8.37%, this gives a concrete reason to qualify the general adjacent-K lane-coalescing candidate. It does not establish that added offset registers/shared-bank contention will pay off, nor justify a model-specific policy.

This completes the separately authorized PC follow-up to `RESULTS.md`; that earlier metrics report and `diagnostic-summary.json` retain their then-current “no PC launched” status unchanged. No production source change or candidate GPU work occurred in this diagnostic.

## Source and native binding

- Same retained2b8 source, actual swap482b kernel, frozen N3U TP8T16384 W4A4 tactic/routes and original compiler options as the metrics pass. The source-wide13,245-file and native release cache pre/post checks pass again.
- One NCU SourceCounters application-replay pass, four native replay images. Every image matches the metric FC1 cubin `db9cf0157a08bef023af8c67b2830bd52b9eeb13d73a3e97e6b7538234d47551`;168 registers,384 maximum threads,LOCAL0,SM103. All3,880 NCU instruction PCs/operands match this returned executable with bounded printer-only normalization.
- The exact SF copy sites are `0xd920/d960/d9a0/d9d0/da70/dab0/daf0/db30`; completion is `0xdbb0`. The earlier `sf-native-identity.json` verifies unchanged4B copy pattern versus old822, while preserving register-allocation/scheduling differences around it. Fresh PC counters avoid relying on old stall attribution.
- GPU3 is released: no PIDs,0MiB,0% utilization. No additional profiler run is needed for this question.

## Native instruction and wait observations

There are27,549 total sampled warp observations,2,220 MIO,15,294 long-scoreboard,1,242 short-scoreboard and2,442 barrier observations. These counts identify issue/dependency sites, not elapsed-time shares or independently summable critical-path components. Different warp counts and profiler replay also preclude inferring a causal speedup from count ratios.

|Site/group|MIO|Long scoreboard|Short scoreboard|Barrier|
|---|---:|---:|---:|---:|
|SF cp.async4B issue|1,341|0|0|0|
|SF cp.async completion|177|0|0|0|
|Gather4 issue|232|0|0|0|
|Scale S2T issue|62|0|0|0|
|Regular weight TMA issue|5|0|0|0|
|MMA issue|2|0|0|0|
|Gather operand reuse|0|458|0|0|
|Weight operand reuse|0|1,871|0|0|
|Gather completion relay|0|789|0|0|
|MMA gather readiness|0|1,280|0|0|
|MMA weight readiness|0|76|0|0|
|MMA accumulator reuse|0|422|0|0|
|Epilogue accumulator readiness|0|1,952|0|0|
|Epilogue TMEM loads|0|2,482|294|0|
|Epilogue TMEM stores|0|0|193|0|
|Final CTA join/deferred consumers|0|0|0|2,433|

- SF issue plus completion accounts1,518 of the2,220 sampled MIO observations. The older TP source-bound PC capture had1,986 of2,934; these are separate runs, not a matched before/after claim. Both attribute the major MIO issue sites to the same canonical4B SF copy path, whereas the new wide EP capture had only129 SF-related MIO observations.
- MMA gather readiness (`0x2620` plus its dependent branch/slow path) has1,280 long-scoreboard observations, versus76 for weight readiness (`0x2540`). Gather producer stage reuse (`0xd740`) has458; weight producer reuse has1,871. This pattern is consistent with the activation gather/SF path sometimes holding consumers back, but the waits remain real data dependencies and may also reflect overlap/backpressure. Do not delete them or assign all gather readiness latency to SF alone.
- Epilogue accumulator readiness (`0x2d20`) has1,952 long-scoreboard observations; the epilogue still contributes TMEM load/store work. This is a mixed pipeline, not proof of an exclusively SF-bound or epilogue-bound kernel.
- Final deferred CTA join is `0xe440`;2,433 barrier samples occur at the following predicated EXIT (`0xe460`). Static scheduler warp3 reaches this join without scheduled work. These observations must not be mistaken for a removable steady-state barrier; individual warp attribution is unavailable here. The other9 barrier observations are outside this terminal group.

## Candidate and history boundary

The source-only mapping proof in `audits/sf-coalesced-lanes/` preserves canonical SF memory/layout,4B instructions, exact live/zero/unused classifications and total copy count; it trades more coalesced global requests for possible shared-bank contention and additional offsets. A native exact/resource gate must reject spilling or excessive instruction growth before timing. Any final ownership policy must derive from compile-time K/SF geometry and apply generally, without extra tuning axes or topology/dtype rescue switches.

The old `scripts/sf_cache_experiment/README.md` tested **SF4B cp.async L2 prefetch64/128/256**, not Gather4 hints, and was neutral/slower on C1B200. That prefetch-only lead remains closed; `audits/sf-coalesced-lanes/HISTORY_AND_CURRENT_TP.md` records the correction. The lane-ownership candidate is distinct and cannot claim historical validation.

`pc-analysis.json` retains every role dispatch range, exact wait/barrier offset, slow-path target, native hash and top sampled instruction. `fc1-pc/source-sass.csv` and the complete raw profiler archive are preserved. `analyze_current_pc.py` and this renderer reproduce the report without source changes or new GPU activity.
