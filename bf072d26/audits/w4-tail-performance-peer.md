# W4 partial-K tail: independent performance assessment

The complete 12-cell screen is valid and supports the authorized broader affected-shape coverage. It does not yet establish a broad prefill benefit or a final retention decision. The six small-token gains are consistent and attributable mainly to FC2; the five prefill losses remain part of the result.

## Evidence checked

- Immutable source: retained `02de7785` versus W4 kernel `25aa126d` and shared Mega caller `66ec9ae8`. The full 13,245-file inventories differ only in those two files and match qualification `77b097eb`.
- Three TP jobs, four token counts, complete C/A/A/C: all 4,800 raw CUPTI spans and 48 phase medians independently replayed; no event fallback, retuning, sample removal or row replacement. The estimator is the geometric mean of each arm's two phase medians.
- Frozen routes, cache bytes, benchmark flags and native choices match. All three recorded 16K defaults resolve to the fixed existing tactic; their 24 stage/library/resource joins pass.
- All 80 loaded functions have zero local memory. All 24 cell/stage resource and compile-configuration records are equal across all four phases: FC1 96 registers/640 maximum threads; FC2 128/512. This proves actual loaded resource equality, not timed native cubin identity.
- The 192 clock quartiles contain 37 exceptions and one unavailable window (K3 TP128, second candidate phase, quartile 1). Every available small-token quartile reports median SM 2032 MHz and reason 0. No clock setting changed.
- Independently reconstructed 288 FC1/FC2/combine duration and exposed-extension medians and 72 component deltas from the raw correlated activity intervals. Overlapping kernel durations are not summed; medians of separate components need not sum to the E2E median.

Receipts and replayable scripts: `w4-tail-data-peer.json`, `audit_w4_tail_data.py`, `w4-tail-components-peer.json`, and `audit_w4_tail_components.py` in this directory. The original evidence and author report remain unchanged under `evidence/w4-tail-dequant-screen/1793368574438182000/`.

## All measured cells

Positive speedup means lower latency. Repeat spreads describe only the two observed phase medians, not statistical confidence.

| Model/topology | Tokens | Speedup | Control spread | Candidate spread |
|---|---:|---:|---:|---:|
| K3 TP8 | 4 | +2.136% | 0.000% | 0.461% |
| K3 TP8 | 128 | +3.036% | 0.037% | 0.024% |
| K3 TP8 | 4096 | −0.241% | 0.000% | 2.640% |
| K3 TP8 | 16384 | −0.746% | 3.189% | 1.104% |
| N3U TP8 | 4 | +2.197% | 0.035% | 0.034% |
| N3U TP8 | 128 | +1.973% | 0.145% | 0.105% |
| N3U TP8 | 4096 | −0.563% | 0.271% | 1.033% |
| N3U TP8 | 16384 | −0.578% | 0.194% | 0.543% |
| V41F TP4 | 4 | +1.352% | 0.271% | 0.080% |
| V41F TP4 | 128 | +1.165% | 0.031% | 0.086% |
| V41F TP4 | 4096 | −0.284% | 3.489% | 4.978% |
| V41F TP4 | 16384 | +0.423% | 0.418% | 0.283% |

Geomeans: all 12 **+0.815%**; token 4 **+1.894%**; token 128 **+2.055%**; six prefill cells **−0.332%**.

## Interpretation and complexity

For all six token-4/128 cells, both candidate phase medians are below both control medians. FC2 exposed duration falls by 0.44–1.01 µs at token 4 and 2.86–10.32 µs at token 128, while FC1 changes by at most 0.18 µs. This is a useful, source-consistent signal for skipping an unused dequantization group, rather than a neutral aggregate supported only by fewer instructions.

Prefill is unresolved. N3U TP16K loses 0.578%, and FC2's exposed extension increases by 8.216 µs; its candidate repeat spread of 0.543% is only just above the report's descriptive 0.5% cutoff. It must not be dismissed because it misses that cutoff. K3's prefill losses contain larger FC1 extension changes alongside FC2 improvements. N3U/V41F 4K show losses despite all sampled clocks reporting 2032 MHz/reason 0. The 16K clock trajectories vary across all arms. These facts limit attribution; none cancels a loss.

The source adds a private consumed-K contract, one group-index argument, and two guarded regions around existing decode/store work. It preserves the synchronization path and adds no public option or model rule. Much of the 64+/45− diff is indentation, but the affected native code still adds 8–32 static instructions. The measured small-token gains can justify evaluating that complexity; instruction count alone cannot justify retention. Aligned/all-live split cases and padded-Mega callers have qualified identical binaries, while affected prefill behavior requires the remaining frozen coverage. Do not broaden this assessment into an EP, distributed Mega, sanitizer, or full-matrix speedup claim.
