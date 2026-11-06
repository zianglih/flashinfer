# PDL experiment ledger

## Initial PDL handoff (ee06621a)

Baseline: `68eb1fefb84701131213e423f2c20cf953bb5918`.
Candidate: `ee06621a8c734ad58f598df13abc1f57b307a05e`.

Every producer CTA signals eligibility near entry, with incoming stream ordering unchanged.
The external BF16 reducer opts into PDL and waits after independent score prefetch and before combine loads.
No arithmetic, reduction ordering, producer barriers, launch geometry, tactics, or register caps changed.

The first serial A1/B1 sweep completed successfully on the same B300 x8 node.
Both arms have matching fixtures; all 112 rank outputs match bit for bit.
Tactics match for every retention row (8 through 8192); only the 1-token row differs.
The complete untrimmed sample sets and tensor outputs are retained in collected-perf-ab1.
One serial pair is not enough to separate small effects from temporal drift.

| Tokens | BEFORE µs | AFTER µs | BEFORE/AFTER | Same tactic |
| ---: | ---: | ---: | ---: | :---: |
| 1 | 81.729 | 81.568 | 1.001962× | no |
| 2 | 95.552 | 98.513 | 0.969948× | yes |
| 4 | 115.058 | 106.529 | 1.080058× | yes |
| 8 | 128.449 | 129.537 | 0.991597× | yes |
| 16 | 147.569 | 150.257 | 0.982111× | yes |
| 32 | 170.193 | 176.482 | 0.964365× | yes |
| 64 | 196.513 | 194.161 | 1.012111× | yes |
| 128 | 202.833 | 200.866 | 1.009795× | yes |
| 256 | 194.481 | 204.242 | 0.952211× | yes |
| 512 | 205.746 | 209.041 | 0.984238× | yes |
| 1024 | 228.579 | 229.123 | 0.997626× | yes |
| 2048 | 302.067 | 305.603 | 0.988429× | yes |
| 4096 | 458.133 | 460.132 | 0.995658× | yes |
| 8192 | 779.302 | 771.527 | 1.010077× | yes |

8–8192 geometric speedup: 0.989673×. All14 rows retained;1/2/4 excluded only from this aggregate.

One serial A/B pair does not cancel temporal drift. Use a full A2/B2 pair if regressions or small changes are ambiguous; never replace selected rows. MAD describes within-arm sample spread, not a causal confidence interval.

The initial result does not establish a benefit. Keep the PR draft while profiling and testing a resource-aware improvement.

## Resource hypothesis

The producer reserves 96 registers x 640 threads = 61,440 registers per SM,
with balanced warp-group budgets 144/80/64/96/96. This leaves 1,024 registers
per SM subpartition. CUDA 13.2 cuda_occupancy.h uses 256-register allocation
units per warp and four subpartitions. A 36-register consumer warp therefore
requires 1,280 registers and cannot fit that remaining per-subpartition space.
The historical reducer used 36 registers; fresh candidate resource and timeline
evidence is still required before treating this as the observed constraint.

A 32- or 64-thread block alone does not solve that per-warp limitation. No such
geometry variant was implemented or benchmarked. If fresh evidence supports
the hypothesis, investigate a reducer-only 32-register compile cap with the
existing 128-thread geometry. Confirm actual allocation, spills, output bits,
and full before/after timings; source configuration alone does not prove overlap.

## Independent A1/B1 audit

`independent-ab1-audit.json` passed: the archive and all 78 members were rehashed;
all 16 tensor files and 112 cross-arm finite BF16-bit comparisons agree.
All 100 observations per row were retained. First observations range from
10.366 to 43.561 ms in both arms; the reported statistic remains the original
median. Ordered 25-sample medians show late drift at baseline/256
(194.049 to 283.074 us), baseline/8192 (755.239 to 827.591 us), and
candidate/8192 (761.961 to 820.650 us). These observations strengthen the need
for a complete confirmation rather than selecting individual timing samples.

## Profiling helper correction

The first baseline Nsight attempt produced eight reports and passed finite
bitwise replay checks, but failed its resource-evidence gate. CuTe artifact
properties are file paths in this version; the helper incorrectly treated PTX
as source text and did not create the native dump directory. The corrected
helper creates that directory, reads the actual PTX/CUBIN, verifies PTX entries
and ELF magic, and extracts resources from the captured binaries. Original
failed evidence is preserved; a fresh paired diagnostic capture is running.
This did not change production source or the benchmark harness.

## Fresh resources and cap32 candidate

Corrected profiles completed successfully for both source arms, with all eight
rank outputs passing the finite bitwise repeat checks. Baseline reducer REG36
and PDL reducer REG34 both use zero stack, static shared memory and local memory.
Both round to 40 registers/thread for allocation; the producer remains REG96.

Candidate `ece6b57fc66d3f224416875d4c564f7f09f490f0` adds only
`--ptxas-options='-maxrregcount=32'` to the frontend reducer compile call, with a
short residency comment and source-ledger update. Existing 128-thread geometry,
per-thread work, arithmetic, producer source, and default optimization level
are unchanged. All pre-commit hooks and the scoped AST audit pass.
The source is frozen in `frozen-cap32`; fresh resources, native GPU validation,
profiling and a complete reverse-order before/after pair are next.

The initial isolated NCU runs requested `--set full` and completed 40 replay
passes per arm. Six ctc__tx/rx fabric metrics were inaccessible in both arms;
report them as unavailable rather than calling this complete metric coverage.

## Effective register cap

The plain cap in `ece6b57` produced byte-identical PTX and SASS to the initial
PDL reducer, still REG34. Its native tests passed, but no full timing or strict60
run was started after the resource gate failed.

An untested CuTe min_blocks_per_mp=16 alternative was preserved as a patch.
Its automatic shared-memory carveout behavior would add another experimental
variable; the final trial uses the documented compiler directive override instead.

`230907919e2ee91ad82d1c209d85abf7e843c133` compiles the reducer with
`-maxrregcount=32 --override-directive-values`, preserving launch/cache attributes.
A bounded isolated probe achieves REG32, with one 8-byte stack spill. Root
review traces it to a 64-bit hidden-element offset, stored once and reloaded
for the output address. There are still four packed FMUL2 and 28 packed FFMA2
instructions, and all baseline output bits match on the immutable fixture.
The original strict zero-stack gate remains recorded as false; the bounded
address spill is accepted for further performance evaluation, not called spill-free.
See `override-spill-review.json`. Full-forward profiles, native tests, strict60
and the complete reverse-order timing pair will decide retention.

## Definitive profile comparison and override native audit

The initial corrected archive and override archive have independently passed
full member/hash audits: respectively 572 files / 64,581,468 raw bytes and
279 files / 31,358,150 raw bytes. Their archive SHA256 values are
`c939374d0bea4b3523cf0facc70c518fccf4b135ddb62c9e1f8a6226b8389f71` and
`4b67b6d61699461a8634f3c89a62bb981e6fb8b3bc1e484412d2d8e921a84a4a`.
All three source arms have 40 captured forward graphs at EP8/global128 with
the same fixed N64 epilogue-warps tactic. All eight override rank outputs are
finite and BF16-bit identical to both earlier arms on identical fixtures.

| Median profiled interval (µs) | Baseline REG36 | Initial PDL REG34 | Override PDL REG32 |
| --- | ---: | ---: | ---: |
| Core duration | 214.161 | 195.553 | 198.305 |
| Reducer duration, including waiting | 2.976 | 4.752 | 199.585 |
| Core/reducer lifetime overlap | 0.000 | 0.704 | 196.706 |
| Tail from core end to reducer end | 3.584 | 4.128 | 2.976 |

The effective cap changes the reducer from a tail-only launch to an early launch:
it starts median 1.632 µs after core start, with overlap in all 40 graphs.
This demonstrates overlapping lifetimes; it does not establish useful concurrent
computation or identify same-SM activity. All five replays remain retained,
including large first-replay profiler overhead. These intervals are diagnostics,
not benchmark speedups. No graph DOT was produced, so no explicit graph-edge
or launch-attribute proof is claimed.

Launch geometry and shared-memory fields stay unchanged: core 640 threads,
REG96, dynamic shared 200,064 bytes and cluster (2,1,1); reducer 128 threads
and no user shared allocation. Driver `sharedMemoryExecuted` remains 233,472
bytes for the core and 32,768 for the reducer, with PreferShared/OptIn and
requested-percentage NULL. These driver configuration values are distinct from
per-block allocation; they do not establish a carveout serialization cause.

The isolated NCU captures use local128 rows, H7168/top-k8, one nominal launch
with 40 kernel replay passes per arm. Registers allocated per thread are
40/40/32 and theoretical occupancy is 75%/75%/100%; actual occupancy is
32.724%/33.886%/32.075%. The override's STACK8 is real spill traffic, not merely
an unused resource declaration: the same captured reducer cubin has one
`STL.64` and one `LDL.LU.64`, and NCU records 3,584 local-load plus 3,584
local-store instructions and 28,672 local sectors in each direction. Earlier
arms have no such local instructions or traffic. Six CTC metrics remain
unavailable for all three captures. Isolated durations 7.136/6.816/7.072 µs
are profiler observations, not evidence of end-to-end improvement.

Full details are retained in `profile-analysis/nsys-cap32-override.json/.md`,
`profile-analysis/nsys-launch-resources.json/.md`, and
`profile-analysis/ncu-cap32-override-summary.json/.md`.

The independent native audit for source `2309079` also passes on hu-pdx-115:
25 EP1 cases plus 17 EP2 cases on each of two ranks, including the two existing
opt-in IKR tests. This is 42 logical cases / 59 rank executions; four optional
FlashInfer parity cases were deselected. Both phases exit zero and recorded GPU
process sets are empty after each phase, at completion and archive creation.
The native archive does not contain a separate post-transfer PID/group absence
snapshot. It is distinct from the pending strict60 and sanitizer qualification.
See `independent-native-override-audit.json` (13 members, archive SHA256
`9d20514e112e95fd82cef9e05085b7314dfa7a0b43e45eb4f2f17fdaf1754fee`).

The approved final timing comparison executes B2 (`2309079`) then A2 (`68eb1fe`)
with the unchanged full14/3-warmup/100-sample protocol and separate fresh caches.
Source identity follows explicit labels. Its result is pending; the earlier
initial-PDL A1/B1 candidate differs, so these are not interchangeable repetitions
of one candidate. All 1/2/4-token rows remain reported and are excluded only from
the retention aggregate.

## Current publication and host closure

Current source `230907919e2ee91ad82d1c209d85abf7e843c133` was pushed to
HashInfer draft PR #7. The PR body distinguishes the completed initial
`ee06621a` timing from the still-running current-candidate comparison.
No merge, repository-rule edit or HAI integration bump was performed.
The GitHub CLI identity was restored to `zianglih` after the private PR update.

The final all-files pre-commit run passed (`final-precommit.log`); the repository
worktree and `git diff --check` are clean. The current PR changes only three
implementation files and the copied-source README ledger (26 insertions,
4 deletions). `final-source-review.md` contains the independent ordering and
generated-code approval; full strict numerical, sanitizer and timing results
remain separately required.

## Final PDL sanitizer qualification

Candidate `230907919e2ee91ad82d1c209d85abf7e843c133` passed all six scoped batches in 3947.67 s. Independent archive/source/log audit: `independent-sanitizer-override.json` (SHA256 `5bfee535dc94c812d371c1459612883279283f3b5b538f7946fa04526baa7eda`). All 36 rank reports are clean; 216 workload-rank and 864 tactic-workload-rank executions. Archive SHA256 `9c9a6a7de09afd54ff308451538c772372a6f6d4c6d250f46783a1711d970594`; all 126 members and 104 frozen source files verified. Scope and checker limitations are unchanged. Native, strict accuracy, and sanitizer qualification are complete; performance remains a mixed 0.996978× result and PR #7 stays draft.
