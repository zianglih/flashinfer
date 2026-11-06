# Independent SF-readiness FC1 profile

Two actual-source FC1 launches at native T128/N16 were profiled on B200-92 GPU3,
using retained98fd and the frozen readiness core0f570a27 plus physical-N16 utils
e14d3300. Both sources use identical initialized output/SF allocations, routing,
weights and inputs. All six native input fingerprints also equal the previously
completed bounded T128 screen; no new primary measurement was run.

The NCU2026.1.1 full-set replay collects only the two marked GEMM launches.
Before/after output and SF bytes match, input fingerprints are unchanged, and
both source/dirty-file/data-path guards pass. Timings below are NCU replay
measurements, **not** cold-L2 graph/CUPTI medians.

| Metric | 98fd control | Independent readiness |
|---|---:|---:|
| Replay time (us) |77.472|79.296|
| DRAM reads (decimal MB) |497.378048|497.325312|
| DRAM read throughput (% peak) |83.74|81.77|
| Executed warp instructions |6,575,874|7,639,172|
| Executed branch instructions |304,195|643,155|
| Executed LDGSTS |430,080|215,040|
| Executed TMA loads |67,200|67,200|
| Executed TMEM CP |215,040|161,280|
| Executed MMA |107,520|107,520|
| Executed TMEM loads |26,880|7,680|
| Barrier stalled warps / issued instruction |0.16|0.28|
| Wait stalled warps / issued instruction |1.07|1.34|
| Long-scoreboard stalled warps / issued instruction |21.92|20.59|
| Registers / thread |64|50|
| Threads / CTA |288|320|
| NCU SMEM / block, including1024B driver overhead |198,528|174,080|

Compact SFB and physical N16 reduce scale-copy and epilogue work. Nevertheless,
executed instructions rise16.17% and branch instructions more than double,
while DRAM and useful MMA/TMA work remain effectively constant. This supports
investigating reduced coordination and publication-loop overhead. The profile
does not assign those added branches to a particular role without PC-level
evidence. Individual stall ratios do not prove a unique causal explanation,
and this profile does not establish that concurrency itself is unhelpful.

The next warp3 loader/publisher refinement was independently reviewed read-only
against0669a693; see `warp3-review.json`. Its GPU result is a separate experiment.

[Derived metrics](summary.json), [input-reuse receipt](../../evidence/sf-readiness-profile/input-reuse-check.json).
Raw archive: `evidence/sf-readiness-profile/raw.tar.gz`, SHA256
`8cd117f370e94ed35670be7eb2b53f0bf4023dd504fa22ddaafc34f1ef5a250a`.
`probe.py`, `run_remote.py`, actual source files, exactness receipt, command,
NCU report/CSV/log and environment are archived. Local `summarize.py` only
reads the raw CSV; no measurement or executed helper was modified afterward.
