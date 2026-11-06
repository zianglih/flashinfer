# Completed preferred5, two-transform-group PC capture at global 4096

The inspected two-group binary adds no transform local-memory instructions and
uses the same 216576 dynamic shared bytes as one group. Its PC capture does
show more sampled math-pipe throttling at FP4 conversion and MIO throttling at
shared loads. A claim of "no added contention" would be stronger than this
evidence supports. Exact raw-query and free-TMEM waits remain prominent. The
matched production timing determines the overall benefit; these samples do
not provide latency ratios or normalized stall rates.

- **Integrity:** all eight rank reports completed with one application replay
  pass. The PC metadata separately records two aggregated PC passes, a
  4096-cycle interval and a 32 MiB buffer. Overflow and dropped bytes are zero
  in every report. Every correlated metric conserves exactly after duplicate
  PCs are summed, and then again when the final per-PC rows are summed.
  All raw report SHA256 values were verified locally. Every sampled instruction
  that the report can resolve matches the independently exported rank-0 SASS.
  Unresolved PCs are retained explicitly rather than silently discarded.
- **Source:** all reports embed kernel SHA256
  `58e4af6b935612ed1a68c27fbf355819a02d5a3e622e3fcf5e1dcff0f91c83f7`,
  matching the frozen `candidates/w4a16_fitted5_transform2/source` snapshot and
  local commit `fe4f8132439df1b812f77279e7d033a5128f1ed4`. The remote checkout
  remains an upstream `91bda04` base plus the recorded overlay; do not describe
  its Git HEAD as the local source commit. The launcher descriptor was unset.
  [Frozen manifest](frozen-source-manifest.json),
  [embedded source manifest](embedded-source-manifest.json) and
  [provenance log](../../logs/tmem-fitted5-transform2-ncu-pc-001.provenance.log)
  identify the actual code and command.
- **Workload:** B300 x8, CUDA 13.2, NCU 2026.1.1, EP8, global tokens 4096,
  H7168/I2048/E256/top-k8, M256/N128/K256, preferred raw depth 5, two activation,
  decoded-TMEM and accumulator stages, group512, flag4, epilogue flags (2,4),
  atomic balancing and epilogue-warp token return. The profile uses three
  warmups, one selected profile iteration and the benchmark's cold-L2 path.
  This audit performs only CPU reads of already completed reports.
- **Artifacts:** [complete raw archive](complete-artifacts.tar.gz), all eight
  local `.ncu-rep` files, [NCU log](ep_w4a16_megamoe_t4096.ncu.log),
  [full extracted PCs](t4096-pc-samples.json), [analysis JSON](analysis.json),
  [rank CSV](rank-summary.csv), [selected PC CSV](selected-pcs-all-ranks.csv),
  [wait comparison CSV](one-group-comparison-counts.csv) and
  [opcode comparison CSV](one-group-opcode-comparison-counts.csv) are retained.
  CPU reproduction: `python3 summarize_ncu_transform2_pc.py` from the effort
  root. Ruff, formatting and the complete analysis validation pass; see
  [validation output](../../logs/tmem-fitted5-transform2-pc-analysis-001.log).

Every launch reports 640 threads, 96 registers/thread and 216576 dynamic
shared bytes. The one-group comparison reports 512 threads, 128 registers and
the same shared bytes. The source's corrected register distribution is
128 threads per role at 176/80/64/80/80 registers, totaling 61440, equal to
640 x96 at launch. Control and decode groups release registers before the
epilogue requests 176. This source accounting and observed launch metadata
do not establish the register behavior of an older CUDA compiler.

The complete two-group function has 5672 decoded SASS instructions versus
6048 for one group. Both have 16 STL instructions and five LDL instructions.
In the new binary all 21 occur in the FC2 router region, offsets 0xa8c0 through
0xb8e0. Neighboring instructions correlate to vendor router source lines
2360/2363/2389/2444/2445, including the local staging/reload sequence; optimized
line tables attribute a few stores to nearby generic kernel/helper lines.
There are no LDL/STL instructions in the transform body. This is an inspected
binary statement, not a blanket "no spills" guarantee. Static whole-function
instruction counts also do not measure executed work or speedup.

The offsets below were mapped from this binary's contiguous
[SASS and source](t4096-rank0-sass/sass.json), not reused from one group.
For each slow path, `analysis.json` retains the fast-path caller branch,
barrier query, sleep, back-edge and return branch.

| Site | Fast-path caller offsets | Sleep offsets | Barrier offset |
|---|---|---|---|
| Weight TMA free raw stage | 0x47c0 / 0x4a50 | 0x14700 / 0x14760 | +0x28 |
| Activation TMA free B stage | 0x53e0 / 0x5890 | 0x14a60 / 0x14ac0 | +0x80 |
| Transform raw weights/SF ready | 0x64e0 / 0x7400 | 0x14ca0 / 0x14d60 | +0x00 |
| Transform free decoded TMEM stage | 0x6540 / 0x7460 | 0x14d00 / 0x14dc0 | +0x60 |
| MMA free accumulator | 0x8770 | 0x14fa0 | +0xa0 |
| MMA decoded weights ready | 0x8840 | 0x15000 | +0x50 |
| MMA BF16 activation ready | 0x8880 | 0x15060 | +0x70 |
| FC1 epilogue accumulator ready | 0x9300 | 0x151d0 | +0x90 |
| FC2 epilogue accumulator ready | 0xa640 / 0xb6f0 | 0x15230 / 0x15290 | +0x90 |

The transform's raw-readiness **peek-result** branches are separately at
0x64a0/0x73c0. Predicate P3 is produced by
`SYNCS.PHASECHK.TRANS64.TRYWAIT` at 0x6430/0x7380. They correlate to inherited
local `_transform_tile` source line 474; their predicate-producing queries
correlate to line 463. The transform free-TMEM branches query barrier +0x60
at 0x6530/0x7450 and correlate to line 488. Samples of these dependent branches
can reflect waiting for the query result. They do not establish that raw data
was absent for the sampled duration. Similarly, long-scoreboard samples at
`NANOSLEEP.SYNCS` do not by themselves identify a global-memory load producer.

All counts below are `smsp__pcsamp_sample_count`, not cycles or wait entries.
Producer-tail sites remain separate in JSON/CSV.

| Rank | Total samples | Unresolved | Raw-ready sleep | Free-TMEM sleep | Weight raw-free sleep | MMA decoded sleep | MMA activation sleep | FC1 acc sleep | FC2 acc sleep | Raw peek branches |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 180346 | 212 | 0 | 1853 | 252 | 0 | 123 | 2718 | 21 | 4085 |
| 1 | 32220 | 430 | 0 | 1725 | 163 | 1 | 80 | 2446 | 6 | 3418 |
| 2 | 3262144 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | 359905 | 356 | 0 | 2004 | 189 | 0 | 95 | 2493 | 18 | 3532 |
| 4 | 137812 | 452 | 0 | 2027 | 275 | 0 | 139 | 2329 | 62 | 3624 |
| 5 | 2654072 | 427 | 0 | 1734 | 246 | 1 | 116 | 2529 | 46 | 3422 |
| 6 | 1920309 | 518 | 0 | 1753 | 249 | 0 | 114 | 2413 | 66 | 3471 |
| 7 | 251694 | 500 | 0 | 1977 | 295 | 1 | 133 | 2555 | 96 | 3802 |

Rank 2 has 95 correlated PC instances with no useful compute-path coverage;
the earlier one-group capture has the same limitation on this rank. Its large
sample total is not evidence of compute coverage or omitted kernel work.
All eight reports remain in the integrity audit, but only ranks
0/1/3/4/5/6/7 support the compute observations. The unresolved samples above
have empty SASS and no source in the report, including PCs outside its named
function. They are counted in conservation and retained in JSON with absolute
addresses; their instructions are not guessed.

The one-group comparison is also preferred5, PC-only, one application replay
and the same 4096-cycle sampling interval. Decode warp count doubles from
four to eight, while each group handles part of the same K tile. The compiler
unrolls fewer operations per thread: the static decode-body E2M1 conversion
count is 256 versus 128, packed `LDS.128` count 16 versus 8 and TMEM `STTM.x8`
count 32 versus 16. Those are static instruction sites across FC1 and FC2,
not dynamic totals. Counts cannot be normalized merely by dividing by two.

| Rank | E2M1 math-pipe stall samples, one group | E2M1 math-pipe, two groups | LDS.128 MIO stall samples, one group | LDS.128 MIO, two groups |
|---:|---:|---:|---:|---:|
| 0 | 14 | 284 | 9 | 225 |
| 1 | 16 | 303 | 3 | 188 |
| 2 | 0 | 0 | 0 | 0 |
| 3 | 18 | 285 | 2 | 223 |
| 4 | 10 | 263 | 10 | 223 |
| 5 | 14 | 259 | 16 | 249 |
| 6 | 18 | 245 | 6 | 199 |
| 7 | 11 | 225 | 8 | 231 |

These samples are summed over the inherited helper's transform-body opcode
sites with its own source/SASS mapping. The two-group opcode CSV contains
all associated sample, long/short scoreboard, math-pipe and MIO counts.
E2M1 conversion sites have 1239–1524 total samples across useful ranks, with
zero long-scoreboard and 67–121 short-scoreboard samples. MIO throttling at
`LDS.128` and math-pipe throttling at conversion are therefore visible issue
pressure, not transform local-memory spilling. They support a contention
hypothesis but cannot quantify its effect on end-to-end latency.

Raw peek-result counts are 3418–4085 in two groups versus 1735–2058 in one;
free-TMEM sleep counts are 1725–2027 versus 953–1368. Both groups execute the
same pipeline waits, so more waiting warp samples are expected even if the
stage lifetime does not grow. FC1 accumulator sleep counts are 2329–2718
versus 2966–3451, and weight-producer raw-free counts are 163–295 versus
287–406. This pattern is consistent with changed overlap and backpressure;
it does not prove an isolated mechanism. Both captures have zero sampled
raw-ready slow sleeps and very few MMA decoded-ready sleeps, which does not
exclude short waits or query latency.

For the pending N64 three-decoded-stage experiment, the sampled free-TMEM
backpressure provides a concrete site to inspect after a matched numerical
and timing gate. A third stage might allow decode to run farther ahead, while
also exposing more math/shared-pipe pressure. Preserve the N64 two-stage
control and use its own binary/source mapping for that comparison. This audit
makes no recommendation to change the current M256/N128 defaults, launch a
new profile, or attribute measured production speedups to the PC counts.
