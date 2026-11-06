# ACC1/decoded3: saved numerical audit

PASS: 13 rank-test calls, 40 public configs, 40 compiled Mega objects and
40 matching prelaunch resources. N128 EP2 runs both-return reference_schedule
and pipeline_wrap (8/20); N64 EP2 runs both original references (4/16); manual
M128/N128/C2 EP1 runs the original epi-return reference (1/4), with one-CTA MMA.
Four N128 long-K rank cases retain H7200/I2112/T257 and K29/K9. The unchanged
references preserve ordinary/partial, scale/routing, empty/refill and graph
oracles. No new oracle or tolerance is introduced.

Source e8996291e4ad0aaa4acde731b1d128f6844e371282799c5f50a9ee70e3106c6d; completion c653b7e495f098ccdd4f3c2f9f339fbe08ab1c94cffb41f8997cacd22978467d. Original closure sessions:
{'original_session': 98210, 'manual_retry_session': 83226, 'canonical_idle_session': 32918, 'original_fetch_session': 27040, 'manual_fetch_session': 7116, 'idle_fetch_session': 55519}. The original outer failed after both
EP2 jobs passed: manual EP1 omitted MASTER_ADDR before any config or compiled
object (subprocess exit1), preserved separately. Only that manual job was
retried in its distinct folder and passed. All three selected successful job
exits and actual source/idle closure pass. Raw stages {'4': 4, '5': 36}; activation
{'2': 4, '3': 36}; scheduler {'2': 40}; local
bytes {'0': 40}. N128 has one physical, pipeline and epilogue
accumulator stage; N64 keeps two. Accumulator histogram
{'1': 24, '2': 16}; decoded histogram {'3': 40}.
The separate saved native review is inherited, with no native validator rerun.

Current job subprocess seconds:
- m256n128-ep2: 94.704587964
- m256n64-ep2: 70.255589574
- m128n128-ep1: 40.692981622

Audit SHA c83655d4336224a4c0db6c2c230afab37f5383d7273cca1977bab329376f608b. The earlier 129 host/4 GPU shared-layout
contract audit remains inherited evidence; it was not rerun or included in
13/40. Only completed original reports, observed scalars, resource Counters
and non-native closure hashes were reconciled. Original, native and baseline
validator runs: zero. No GPU work or AUTO retention claim. The eventual full13
comparison uses accepted shared-layout 1a763 current columns directly, with
8–4096 as the retention range.
