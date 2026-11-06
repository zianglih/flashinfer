# Rejected finer-phase v1 native traces

Source6afd622 / package+fixture84cc799. Both captures pass output checks but FAIL strict trace validity; no minimum-sync rank or human trace is selected. These are diagnostic artifacts, not accepted measurements.

| Global tokens | Rank/PID | Expected jobs | Resolve/issue/input wait each | Pool/ready each | Tail flush outside parent |
|---:|---|---:|---:|---:|---:|
| 128 | 1/46056 | 8 | 8 | 14 | 6/8 |
| 128 | 2/46057 | 8 | 8 | 14 | 6/8 |
| 128 | 3/46058 | 8 | 8 | 13 | 5/8 |
| 128 | 4/46059 | 8 | 8 | 14 | 6/8 |
| 4096 | 1/47421 | 112 | 112 | 211 | 8/8 |
| 4096 | 2/47422 | 112 | 112 | 213 | 8/8 |
| 4096 | 3/47423 | 112 | 112 | 212 | 8/8 |
| 4096 | 4/47424 | 112 | 112 | 213 | 8/8 |

128 per-track membership: store+ready duplicate on6/6/5/6 of8 tracks respectively; local source token residues are single, while most remote tokens duplicate. Rank2 CTA1/warp8 is a remote exception, so the effect is latency-dependent rather than a fixed source-rank branch.

Example rank0 CTA0/warp9, payload1, times relative to this warp’s own pull start (ns): whole pull0–5440; inputwait3776–3936; store4000–4512 and4544–4992; ready5024–5184 and5216–5344; flush10272–11744 outside the prematurely closed parent. The source processes this route once.

|4096 rank/PID|FC2 expert waits|Stage/issue|Output-store waits|Pacing|
|---|---:|---:|---:|---:|
|0/47421|104|107|214|142|
|1/47422|105|109|218|158|
|2/47423|107|107|214|136|
|3/47424|117|117|234|160|

Every one of32 recorded4096 WG2 tracks has two output-store-wait ranges per stage token and two pacing ranges per eligible token. Expert-wait and stage payloads themselves are unique. Later children escape the whole return wrapper after duplicate pops consume its stack entry.

Both original static bindings PASS:128 has145 bijective PMTRIG sites;4096 has153. All four ranks agree on configuration/decode context/kernel/original CUBIN in each capture. CUBIN hashes are701bf7289984af3bf84bdad37d252681748a3e9f86f0a8d4cffed6e80d3f1f35 and4029c34033940847cf1a54ccf6ed99fa7535f9d6dec4cbdc2792b6df99570751. This rules out the previous merged-scanner-window defect, but cannot establish valid dynamic nesting.

128 original SASS around the failing region: input wait push0x105c0; elected wait uses BSSY/BSYNC0x10600/0x10670 and pop0x106d0; store push0x10780; elected bulk completion uses BSSY.RECONVERGENT/BSYNC.RECONVERGENT0x10910/0x10970 and pop0x109d0; ready push0x10a80, existing warp-sync BRA.DIV0x10c90, pop0x10d00; outer token-loop BSYNC0x10d30. Merely putting source markers after an existing sync was insufficient in this native capture. Dynamic cohort behavior is consistent with the evidence; no SDK root cause is proven.

Next candidate: only move marker statements into existing elected TMA wait/issue/commit blocks, split the broad pool-store interval into issue and wait, and omit outside-elected ready/output-wait/pacing pairs. Keep unique expert-wait and whole-call wrappers. Add no computational barriers or guards; require a fresh source-bound static and dynamic audit. No repair/deduplication/tolerance is permitted.
