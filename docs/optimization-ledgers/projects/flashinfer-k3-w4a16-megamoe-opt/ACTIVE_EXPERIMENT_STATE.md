# Active C2 experiments

Update 2026-10-09 06:05 UTC: combined exact passed8 logical EP2 cases on both
ranks (16 rank-local passes,0failures/skips); local archiveverified. Full
`combined-auto-v2` runs under supervisor58939, with the simple12-tactic catalog.
User asks about missing M128/N32. Source review finds no intrinsic blocker for
M128/N32/C2 with one-CTA instructions; preparing allowlist-only artifact and a
follow-up fixed candidate sweep. Keep currentAUTO running unmodified. M128
will not enter AUTO until measured; C1 guard and decoder design stay fixed.

Update 2026-10-09 05:58 UTC: user requested direct extension of the existing
tile loop. Root removed the separate two-tactic append and added
`(256, 32, 256)` alongside N128/N64. This preserves the existing combinations:
12 default tactics (8 old + 4 N32 across both return modes and group sizes).
Focused pre-commit passes. The unlaunched combined AUTO v1 bundle is superseded
by v2, which will install this simpler catalog after the same combined exact
gate. No extra baseline is planned; all13 points remain required.

Update 2026-10-09 05:55 UTC: `combined-exact-v1` dispatched. It installs final
local source bytes for scheduler, epilogue and tuner after verifying equivalence
to measured candidates, then runs eight logical EP2 prefix/N32 cases against the
existing bit-exact oracle. The tests include feature tails, remote routed-count
boundaries, empty/refill rounds and graph replay. Catalog remains unchanged on
C2 until this exact gate succeeds. Local candidate adds only two N32 epi tactics;
all eleven changed PR files pass pre-commit. `PERFORMANCE_PROGRESS.md` now keeps
a cumulative speedup column per increment, with combined AUTO still pending.

Update 2026-10-09 05:52 UTC: N32-v3 completed all13 points successfully.
Decode T4–512 improves2.11–6.10% vs saved BEFORE; prefill speedup is0.545–0.555x
(~1.8x slower), so N32 qualifies only as an additional small-token tactic, not
a replacement default. Strict report: `evidence/progressive-residual-n32-v3.*`.
Root applied reviewed N32 support/validator/test artifacts locally. The next
GPU action is combined exact validation (N32+residual, eight EP2 logical cases),
then a candidate-only full AUTO sweep with exactly two new N32 epi tactics.
`next-residual-exact-v2` remains synced but unlaunched and is superseded by the
combined qualification plan. Remote source is still measured N32-v3.

Update 2026-10-09 05:45 UTC: N32-v2 stopped before compilation because the
shared BF16/NVFP4 knob validator still rejected N32. Preserved at
`evidence/n32-token-v2-failed.tar.gz`. V3 is now dispatched with the same five
reviewed support files plus only the BF16-specific tuner whitelist addition.
No AUTO catalog or default changes. Its seal is
`21740daf133651250dd794553e0fb0555d0bf384cdfafe77938b43276a3091a3`.
The local scheduler and stronger prefix test pass focused pre-commit; the
stronger GPU check will follow this serialized screen.

Update 2026-10-09 05:42 UTC: residual-prefix-v1 passed all 13 performance
points (1.01540x versus saved BEFORE over the 11 retention points) and four
focused EP2 exact cases on each rank (8 rank-local passes, no skips). The patch
is now applied locally; a stronger non-power-of-two/multi-block fixture is being
prepared after independent review. N32 token-tile support is running as
`n32-token-v2`, supervisor51501, with the original scheduler restored for this
independent screen. Only token N changes relative to the saved native tactics;
the established decoder WG design and register partition remain fixed. V1
failed before source mutation because its seal included an unsynced Python cache
file. V2 excludes transient bytecode; no GPU result exists yet.

Update 2026-10-09 05:22 UTC: residual-prefix-v1 candidate-only full13 sweep is
running under supervisor45162. Only scheduler _advance_group differs from the
native intermediate; launch/frontend/decoder files are checked immutable. Full
saved BEFORE and native results are reused, unchanged recorded native winners,
100 samples per point. Source proof and finite integer audit passed; GPU exact
checks remain conditional on performance. N32 token-tile support is being
reviewed separately as a K3 epilogue tactic; no AUTO change or GPU launch yet.

Update 2026-10-09 05:16 UTC: user explicitly ruled out decoder-WG experiments.
Stopped only four-decode-wg-v1 torchrun PID43476; supervisor and all eight workers
exited. Restored kernel/frontend bytes exactly to full-native-v2 under the perf
lock. The partial capture is cancelled, excluded from retention, and archived at
`evidence/four-decode-wg-user-cancelled.tar.gz`; source receipt is
`queues/four-decode-wg-v1/restoration.json`. Remote source now exactly matches the
native intermediate (no count cache, no packed transpose, two decoder WGs).
Decoder WG count, partition, and role register design are fixed constraints.
The devbox remains allocated. Next source-only review: residual-scan elimination.

Update 2026-10-09 05:12 UTC: draft PR6277 exists at commit 03e1840c.
The native-tanh exact gate passed, but the completed 13-point AUTO result is
flat overall; native tanh is provisional. The user's current policy is to reuse
BEFORE `full-base-v2` and native `full-native-v2`, with candidate-only sweeps.
Packed-transpose and count-cache both completed all 13 points. Packing is flat;
count caching has a small 1.00672x overall gain versus BEFORE and is not promoted.
No additional correctness or IKET is running. The C2 GPU queue is idle while the
independent four-decoder-warpgroup artifact is prepared. Remote source is the
native epilogue plus count-cache scheduler; the next follower must restore the
original scheduler before applying its own delta. Devbox remains allocated.

Update 2026-10-09 04:23 UTC: AUTO-v3 finished, native tanh retained after the
4-point A/B/A screen (T32 1.047x, others smaller gains). Raw archive and summary
retrieved locally. Trace-v5 completed tracker and actual instrumented launches
on all8 ranks; 13GB raw data remains in persistent storage. Optional full-grid
CPU visualization was taking minutes while GPUs were idle; owner verified the
exact PID/command and stopped only run-iket19856 with SIGTERM. Trace exit1/-15 is
preserved, not reclassified as success. All8 receipts exist for both invocations.
Exact-v1 stops before tests on that failed trace gate. Fresh exact-v2 PID22668
uses the same sealed helper with an explicit recorded owner decision to proceed
after completed GPU capture and stopped visualization. It applies selected
native/oracle/nine-case patches and runs13 logical exact cases. Full-sweep bundle
is synchronized but not yet dispatched; its gate will be changed to exact-v2
before launch. No benchmark or kernel source formatting changes until the sealed
work finishes; Ruff-format reports only two line-wrap adjustments in epilogue.

Update 2026-10-09 04:02 UTC: trace-v4 failed in IKET CLI argument parsing,
before workers/GPU use. Its failed receipt remains unchanged. After verifying
the AUTO-v3 bundle seal, launched its unchanged plan directly through the
proven runner/queue.py, queue PID13633. This deliberately removes diagnostic
setup as a dependency of independent performance work. Fresh original/native
tanh/original AUTO at T32/512/4096/16384 is active. Trace-v5 will follow it with
installed CLI syntax verified before launch. Original AUTO-v3 follow-on13446
stopped on the trace-v4 failure and is not a second launcher.

Update 2026-10-09 04:00 UTC: scan-v3 completed and was not retained (mixed,
baseline drift explains apparent wins). All four codegen-v3 captures completed
with successful diagnostic receipts and archived binaries. Its final CPU
comparison failed because it expected one specialization per rank, but frontend
staging warmup creates int32/int64 IDs x vector/scalar-copy variants. V3 trace
and AUTO-v2 predecessor gates stopped before launching. Preparing trace-v4 with
successful-capture receipts as its prerequisite and a corrected CPU comparison;
do not rerun already completed captures or alter their saved exit status.

Current update, 2026-10-09 03:46 UTC:
- Replacement devbox `k3-w4a16-opt-c2`, C2/ziangli, same node `hu-pdx-120`.
  Original devbox disappeared; no delete was requested or performed.
- Recovery `recovery/setup-20261009T034347Z` succeeded, preserving Torch,
  source diff, submodules and persistent caches. Core runtime versions match
  `native-a1`; pip also resolved editable-install optional dependencies, recorded
  in `editable-install.log`. New comparisons use fresh baselines in this container.
- Active serialized chain: cooperative-group-scan-v3 (supervisor3393, queue3397),
  codegen-native-v3 (supervisor3739), trace-baseline-v3 (supervisor3747).
  Scan runs original/cooperative/original at T4/32/128/512/4096 with fixed N64.
  Codegen and traces are diagnostics, not performance/correctness evidence.
- V1 failed before workers on hostname rendezvous; v2 failed before compilation
  because a helper-directory `queue.py` shadowed the standard library. Both are
  preserved. V3 uses loopback rendezvous and isolated helper imports.
- No GPU correctness has run. The existing zero-tolerance oracle/tests remain
  the only intended correctness gate after a confirmed performance gain.

The entries below are chronological history, not current launch instructions.

Remote root: `/data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt`.
All source changes/benchmarks are serialized on the retained C2 B300 devbox.

- Completed `queues/exploration-native-v1` (9 fixed-tactic arms).
- Completed `queues/prefill-n128-v2` (baseline/packed/native/baseline).
- Completed `queues/secondary-decode-v1`: secondary-a1,small-group-h,scheduler3-i,
  single-cta-j,epiflag44-k,group4096-repeat,secondary-a2.
- Launched by follow-on PID108089 in `next-combine/follow_on.py`: launches
  `queues/k16-combine-v1` only after secondary queue exits successfully.
  Arms combine-a1,combine-scalar-b,combine-a2; T4/32/512/4096 fixedN64/G1024.

No GPU correctness checks have run. User now requests only existing
zero-tolerance W4A16 reference/tests, concise cases, and matching reference
changes for algebraically equivalent arithmetic. No non-exact behavioral
test is retained. DraftPR not created yet. Both devboxes must remain allocated.

- Next waiting follow-on PID112376 in `next-auto-baseline/follow_on.py`: a full
  11-point nativeAUTO originalkernel baseline (`auto-base-1`) starts after
  `queues/k16-combine-v1` succeeds. It resets epilogue.py,topk_reduce.py,autotune.py
  to the new upstream base; benchmark v2 remains applied.

Scheduling candidates have no repeatable gain and are not retained. Initial
G4096 T4 improvement failedrepeat (107.360 versus lastcontrol106.631us).
Currentlocaltestfile has9 exact epilogue cases, no standalone nonexact test.
Native-tanh-oracle-v2.patch is preparedbutunapplied. Localepilogue remains
packed-v2; finalarithmetic hasnotbeenselected.

Update 2026-10-09 03:15 UTC: combine queue completed successfully; fetched all
secondary and combine raw artifacts locally. K16 scalar scores remain unretained
(only T512 modestly improved). auto-base-1 started 03:12:55 UTC and is running.
Prepared full and bounded native-tanh follow-on bundles are not yet launched.
The next diagnostic step is original/native-tanh compiled artifacts plus native
K3 IKET traces with the actual deterministic combine.

Update 2026-10-09 03:27 UTC: full original-kernel auto-base-1 completed all11
points successfully and raw archive retrieved as evidence/auto-base-1.tar.gz.
Dispatched serial chain:
- next-codegen-v1, PID121540, queues/codegen-native-v1: 4 short binary captures.
- next-trace-v1, PID121046, queues/trace-baseline-v1: waits codegen success,
  then baseline IKET at T512/N64 and T4096/N128, real fused combine.
- next-scan-v1, PID121570: waits trace success, then
  queues/cooperative-group-scan-v1, scan-a1/scan-coop-b/scan-a2.
All bundles sealed; do not edit or overwrite dispatched bundles. Stop gates
retain failed source for inspection. AUTO native-tanh bundles are not launched.
No GPU correctness runs have been performed.
