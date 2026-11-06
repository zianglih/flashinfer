# K3 W4A16 T4096 same-effective-tactic diagnostic

Completed on GPU1, B300, pushed `d1767be1f42fdc371f90db4fb06598299ea32845`.
The public functional benchmark ran CAAC with cloned managed caches:
C=`-1`, A=the previous explicit FC1/FC2 pair. Both resolve to
`(((256,128,256),(2,1),True), ((256,128,256),(2,1),True))`.
Source proof: `tuner.py:1393` converts -1 to None; `moe_w4a16.py:43–46,407–408`
resolves None to that pair. Same source, layout, policy and effective kernel.

| Pass | Cache encoding | Median100 ms | First25 ms | Last25 ms | Last50 ms |
|---:|---|---:|---:|---:|---:|
| 1 | current | 0.5336510 | 0.5308190 | 0.5898600 | 0.5889795 |
| 2 | explicit | 0.5326595 | 0.5311070 | 0.5843250 | 0.5843565 |
| 3 | explicit | 0.5328520 | 0.5312680 | 0.5849640 | 0.5837165 |
| 4 | current | 0.5331880 | 0.5310120 | 0.5906280 | 0.5800205 |

Mean of the two standard100-sample medians: current 0.5334195ms versus explicit
0.5327558ms; explicit/current−1 = -0.124%. This does not reproduce the
original approximately3% flag. The identical effective kernel shows the same
within-run low/high latency bands in both encodings; first25≈0.531ms and
last25≈0.584–0.591ms. Clock telemetry only brackets each process, so it cannot
identify the cause of that intra-run transition. No kernel/tactic regression
is established. Diagnostic strata do not replace standard100-sample medians.

Every run used graph replay, cold L2, 10 configured warmups and100 CUPTI samples;
no event fallback, cache misses or profiling. Exact route identity, target
cache-key/tactic, unchanged source hashes and frozen clone hashes passed. The
main campaign cache/results were untouched, native compilation caches retained,
and GPU1 released after confirming idle. No source change or sanitizer.

All15 fetched evidence files are SHA-verified in `evidence/fetch-hashes.json`;
raw samples are in each `evidence/[1-4]-*/results.json`, full commands and cache
entry/hash provenance in `evidence/receipt.json`. This is diagnostic evidence,
not replacement public table data or new external baseline measurements.
