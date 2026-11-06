# Candidate007 retention assessment — first complete sweep

Recommendation: **one complete confirmation sweep**, preserving this first result and the whole005 refresh control. Root has authorized that confirmation on unchanged007. Retention is pending; this document interprets the completed full sweep and does not replace or subset its published metric.

Inputs: [complete comparison](BENCHMARK_COMPARISON.md), before `logs/candidate005-tma-prefix-refresh-ep8-nonfused.json` (`85329501`), after `logs/candidate007-useful-subtiles-ep8-nonfused.json` (`0673dacd`). Each selected tactic below comes from the exact token key in that row's saved `.t<T>.autotune.json`, whose hash matches the row record. Later cumulative caches were not substituted for earlier row snapshots.

## Which rows execute the changed code

The workload uses SwiGLU, so GEMM1 is gated and excluded. GEMM2 is nongated and ordinary. The source guard at `active-kernel.py:2120–2132` additionally requires route N > epi N; epi N is min(N,32) for these tactics. Only selected N64 and N128 run the new bound. Host `moe_w4a16.py:399–401` unpacks the tactic pair and requires identical route N for both GEMMs; GEMM2 receives the second tactic at499.

All listed tactics use K256, cluster(2,1), and the same final Boolean True. `M/N` below denotes the actual MMA tile pair, not runtime feature M. No selected N, K, cluster, or Boolean changes between arms; listed selection changes affect only MMA M.

| Tokens | FC1 M/N before → after | FC2 M/N before → after | New bound runs | Latency change |
|---:|---|---|:---:|---:|
| 1 | 256/16 → 128/16 | 128/16 → 128/16 | No | −0.084034% |
| 2 | 128/8 → 128/8 | 128/8 → 128/8 | No | +0.001135% |
| 4 | 128/32 → 128/32 | 128/32 → 128/32 | No | +0.108791% |
| 8 | 128/16 → 128/16 | 128/16 → 128/16 | No | −0.383735% |
| 16 | 128/8 → 128/8 | 128/8 → 128/8 | No | −0.097904% |
| 32 | 128/8 → 128/8 | 128/8 → 128/8 | No | +0.041984% |
| 64 | 128/16 → 128/16 | 128/16 → 128/16 | No | +0.052773% |
| 128 | 256/16 → 256/16 | 128/16 → 256/16 | No | +0.041829% |
| 256 | 128/16 → 128/16 | 128/16 → 256/16 | No | +0.301195% |
| 512 | 256/32 → 256/32 | 256/32 → 128/32 | No | +0.078124% |
| 1024 | 256/64 → 256/64 | 128/64 → 128/64 | Yes | −0.114954% |
| 2048 | 256/64 → 256/64 | 128/64 → 256/64 | Yes | −0.180127% |
| 4096 | 256/128 → 256/128 | 256/128 → 256/128 | Yes | −0.304228% |
| 8192 | 256/128 → 256/128 | 256/128 → 256/128 | Yes | −0.580661% |

The **full retention scope, tokens8–8192, remains −0.104435% latency GM (1.001045×),6/11 lower**. Tokens1/2/4 remain reported and excluded from retention. For interpretation only, the four affected rows have −0.295152% latency GM,4/4 lower; the seven excluded retention rows have +0.004710% latency GM. The three affected rows with an exactly matching whole tactic pair (1024/4096/8192) have -0.333464% latency GM,3/3 lower. These are descriptive source-based partitions, not replacements for the full sweep or significance estimates. T2048's speed difference cannot be attributed solely to007 because FC2 changes MMA M128→M256.

## Benefit versus cost

The added13 source lines and eight native instructions in each inspected multi-subtile specialization compute a bounded dynamic trip count. They remove wholly invalid suffix TMEM loads and associated epilogue bookkeeping; they do not reduce full-tile MMA work, valid stores, or external fixed-order FP32 combining. The existing full tile requires2 subtiles at N64 and4 at N128;007 executes ceil(D/32), bounded to at least1 for private zero/negative-route progress. Fused and one-subtile ordinary controls emit byte-identical code, per [native control comparison](../../native/CANDIDATE007_UNCHANGED_CONTROLS.md).

The saved T1024 routing summary proves an actual opportunity: all32 local experts have17–42 routes, so each has one N64 tile; median28.5 implies at least16 experts need only one32-row subtile. Thus at least16 of the original64 FC2 epilogue subtiles per feature position are unnecessary (at least25%). At larger token counts, full tiles retain their full loops and only the last tile of each expert can shrink. The saved min/max counts guarantee qualifying tails exist, but summaries do not contain all32 counts, so no exact total saved-trip count is claimed.

This is a real work-reduction mechanism with preserved ordering, not a source-size cleanup. All three matched affected rows move in the favorable direction, making one confirmation worthwhile. The gains remain small (0.11–0.58%) and the complete sweep is nearly flat. One sweep does not establish causality or statistical significance; unchanged-code controls also move, and no raw sample spread is available. If the confirmation does not support the affected-row direction without a material full-sweep regression, prefer rejecting the added runtime/source complexity rather than repeatedly measuring until a favorable run appears.

## Confirmation pending

Expected complete result: `logs/candidate007-useful-subtiles-repeat-ep8-nonfused.json`, compared with the same whole005 refresh control. No new source, numerical, native or GPU action was requested by this assessment. Preserve both complete runs independently; do not select minima or replace first-run rows.

## Completed confirmation and final recommendation

**Recommend rejecting007; do not perform another confirmation.** The first-run assessment above is preserved as the decision before the authorized repeat. The repeat is now complete: [whole repeat comparison](BENCHMARK_REPEAT_COMPARISON.md), `logs/candidate007-useful-subtiles-repeat-ep8-nonfused.json`, SHA256 `60f8bd7539d7f311004b1be5d636816d45e8e2223ebdaa0cf61f6dc65f0a9b2d`. It uses the same whole005 control; no rows from either candidate sweep were replaced or selected as minima.

The repeat row caches were checked against their recorded hashes. In the repeat, **all four affected rows exactly match the control's complete FC1/FC2 tactic pair**, including T2048 reverting FC2 M256 to M128. The affected N values remain N64 at1024/2048 and N128 at4096/8192. T8192's entire tactic pair is identical in the control, first007 and repeat007, so its repeat increase is not explained by a tactic switch.

| Tokens | Repeat FC1 M/N | Repeat FC2 M/N | Changed from control | Changed from first007 |
|---:|---|---|---|---|
| 1 | 128/32 | 128/32 | FC1, FC2 | FC1, FC2 |
| 2 | 128/8 | 128/8 | None | None |
| 4 | 128/32 | 128/32 | None | None |
| 8 | 128/16 | 128/16 | None | None |
| 16 | 128/8 | 128/8 | None | None |
| 32 | 128/8 | 128/8 | None | None |
| 64 | 128/16 | 128/16 | None | None |
| 128 | 128/16 | 256/16 | FC1, FC2 | FC1 |
| 256 | 128/16 | 128/16 | None | FC2 |
| 512 | 256/32 | 256/32 | None | FC2 |
| 1024 | 256/64 | 128/64 | None | None |
| 2048 | 256/64 | 128/64 | None | FC2 |
| 4096 | 256/128 | 256/128 | None | None |
| 8192 | 256/128 | 256/128 | None | None |

All other tactic fields remain K256, cluster(2,1), Boolean True. The repeat T1 changes N16→N32 but remains compile-time excluded from007; its row is outside retention. T128 still changes only M, also on an excluded N16 path.

| Scope / row | First007 latency change | Repeat007 latency change |
|---|---:|---:|
| Full tokens8–8192 | −0.104435% GM;6/11 lower | +0.208398% GM;7/11 lower,1 tie |
| Affected1024–8192, interpretation only | −0.295152% GM;4/4 lower | +0.666601% GM;2/4 lower |
| T1024 / N64 | −0.114954% | −0.070571% |
| T2048 / N64 | −0.180127% (FC2 M differs) | +0.028595% (whole pair matches) |
| T4096 / N128 | −0.304228% | −0.132553% |
| T8192 / N128 | −0.580661% | +2.872689% |

Absolute T8192 latencies are625.494µs control,621.862µs first007 and643.4625µs repeat007. This variation does not prove a causal source regression, just as the first improvement did not prove a gain. No raw sample dispersion or significance estimate is available. Two retained positive signals at1024/4096 are small;2048 is essentially flat once tactics match, and the affected/full-sweep outcomes do not support a stable material improvement. The existing work-reduction proof remains valid, but saving masked epilogue iterations has not demonstrated enough end-to-end benefit to justify13 extra source lines and eight native instructions in the changed specializations. Preserve the experiment as measured evidence and prefer the simpler retained005 implementation.

This conclusion is independent of the exact numerical/private-zero/native PASS records: those establish behavior and progress for the tested scope, not performance retention. No source, PR, GPU, benchmark or compiler action was performed by this assessment. Parsed tactic facts are saved in [retention-tactic-rows.json](retention-tactic-rows.json); complete absolute timing tables remain in the two whole comparison documents linked above.
