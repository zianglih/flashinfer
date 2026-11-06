# Same-phase CONTROL Mega-only comparison

Previous Mega rows are reused from the completed same-phase paired alpha run. Current run executes Mega only, removing preceding split setup/tuning/measurement and changing process history. Canonical preparation and primary cold-L2 CUPTI metric are unchanged; no drift adjustment, row minima, split speedup or controlled process-wall saving is inferred.

All thirteen token counts, three warmups and 100 samples are retained.

| Tokens | Previous Mega ms | Current Mega ms | Change | Previous/current |
|---:|---:|---:|---:|---:|
| 1 | 0.092977 | 0.088320 | -5.009% | 1.052729× |
| 2 | 0.118817 | 0.117680 | -0.957% | 1.009662× |
| 4 | 0.134641 | 0.134562 | -0.059% | 1.000587× |
| 8 | 0.170658 | 0.169457 | -0.704% | 1.007087× |
| 16 | 0.180017 | 0.187649 | +4.240% | 0.959328× |
| 32 | 0.198849 | 0.212482 | +6.856% | 0.935839× |
| 64 | 0.234866 | 0.231298 | -1.519% | 1.015426× |
| 128 | 0.252371 | 0.231347 | -8.331% | 1.090876× |
| 256 | 0.255698 | 0.244001 | -4.575% | 1.047938× |
| 512 | 0.251970 | 0.260082 | +3.219% | 0.968810× |
| 1024 | 0.279635 | 0.268562 | -3.960% | 1.041231× |
| 2048 | 0.353090 | 0.350676 | -0.684% | 1.006884× |
| 4096 | 0.519910 | 0.512402 | -1.444% | 1.014653× |

Current/previous geometric-mean latency: 0.989284425; 10/13 lower. Actual configs match at 104/104 rank/shape pairs. All actual configs and returned choices remain in JSON.

The original GPU benchmark subprocess exited0. Its frozen controller failed afterward on the unsupported eight-empty-rank-file assumption and wrote no original control.json/results.json. This independent saved reconstruction uses v2 only for split-recorder absence; all original compiled/sample/provenance/source validators run unchanged. The box disappeared after the saved successful idle stdout capture and before canonical JSON fetch; no current live owner or AUTO result is claimed.

All 104 CONTROL configurations agree with alpha: M256/N128/F4/epilogue. This fixed sweep cannot assess N64; full AUTO remains required before retaining register. Alpha stays published.

Current subprocess wall: 251.388635435 s. Mega timer utility: 6.244132766 s. These process histories differ; the wall delta is not a controlled kernel saving.
