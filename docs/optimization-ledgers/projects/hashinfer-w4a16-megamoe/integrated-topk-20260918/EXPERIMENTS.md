# Integrated finalize experiment ledger

## Initial dispatch-WG implementation

- Baseline: main68eb1fe, deterministic external TopkReduce.
- Dispatch warps8–11 perform the existing ordered FP32 combine after their
  complete transport tail. No barrier or transport-protocol change.
- The original BF16 worker body is factored into one shared CuTe JIT method;
  the standalone kernel remains available for diagnostics.
- Output pointer and active row shape are part of the runtime descriptor
  cache key. Leading output rows are dynamic, including zero. The raw launch
  thunk holds a zero-row scratch output to preserve its raw-compute scope
  without reading inactive partials.
- User-visible forward/API, five compute roles/two decode WGs, symmetric
  per-route scratch and optional BF16 atomic FC2 path remain unchanged.
- Initial source/host gates are recorded; GPU qualification is pending.

## Compile integration and parallel decode variant

- `95e55b5`: first native run passed four preprocessing cases, then failed
  output-layout conversion. Pytest's CuTe tensor formatting segfaulted while
  reporting the exception; native traceback isolated the host error.
- `fdb4e21`: use the output tensor's actual dimension order, as the standalone
  reducer does. Compilation then exposed a dynamic top-k score extent.
- `6b2243f`: a static tiled score view fixed that error; compilation exposed
  missing combine-vector alignment information from dynamic strides.
- `5362e53`: preserve the actual static layouts of the config-fixed symmetric
  score/combine allocations. This fixes both lost metadata properties without
  adding alignment assertions or reconstructing assumed strides. Remove the
  intermediate score-view workaround; the shared reducer arithmetic/body is
  again unchanged from extraction. Only the output's live row count is dynamic.
- Preserve all failed-run logs and frozen sources. These errors occurred
  before kernel execution and are not GPU numerical failures.
- Decode variant `f4aea69` includes the same descriptor fixes and reuses both
  retired decode WGs (warps12–19, 96 registers). All640 threads join the next
  phase of the existing tail barrier after dispatch completes communication.
  WG-striped worker indexing preserves the dispatch baseline's SM spread for
  small outputs. No top-k recurrence is split across workers; ordered FP32
  arithmetic and BF16 rounding are shared with the baseline. Native GPU gates,
  timing and retained-candidate qualification remain pending.

- Native dispatch `5362e53` is fully green: 25 EP1 cases and 17 on each EP2
  rank (42 logical cases, 59 rank executions), four optional installed-
  FlashInfer parity cases deselected. Collected archive SHA256
  `1607cf1adf7515f4eb36c793274369a1c52c2a67584e04934c62f0a0609f91c8`;
  independently rehashed104source files and13archive members, checked zero
  return codes and complete test sets (`independent-native-static-layout-audit.json`).
- `f5f4de6`: third local control reuses all five retired WGs. Relative to decode,
  the same all640-thread handoff remains; only role selection and grid-stride
  worker assignment change. No register redistribution, transport change or
  new public knob. Native validation and timing are pending; this control is
  queued behind decode2WG and not promoted.
- `integrated-store-completion-review.md`: exact source plus pinned CuTe/PTX
  semantics review finds both return modes already complete and publish their
  BF16 stores before integrated reduction. No new system/proxy fence or bulk
  wait is justified. Current generated dispatch-return PTX remains a useful
  follow-up confirmation during planned profiling; no GPU ordering proof is
  inferred from source review alone.


## Dispatch-only full before/after sweep

Same secondary node (hu-pdx-115, unchanged boot), baseline68eb A1 followed by
5362e53 B1. Complete14-row/100sample CUPTI sweep and112 cross-arm BF16 outputs
pass. Speedup over8–8192 is0.992158x (4/11 rows faster);8192 is0.936536x
(781.334us baseline,834.281us integrated). All2–8192 rows select the same
native tactic. This does not establish an overall benefit and dispatch-only is
not promoted. Full table is paired-benchmark/dispatch-comparison.md; immutable
archive SHA3d35f1a4b3a1c661915431952c58dd8a1c072a4b4ab0d1c192eca705cbee63bf.

The original comparator remains byte-identical; its generic prose says external
finalize/serialpair. Here the candidate finalization is inside MegaMoE, and
future candidate-only runs reuse this A1 chronologically rather than claiming
contemporaneous pairs. Raw timing/output/provenance validation is unchanged.
Do not infer bandwidth causality from this table alone. Decode2WG timing and
retained-candidate profiling will test the parallelism hypothesis.

## Two-decode-WG sweep and overlap follow-on

Decode source `f4aea692749db40ba91a77a2e63c865c0dbf8572` passed the same 42 logical
native cases as dispatch (25 EP1 + 17 on each EP2 rank; 209.11 s). Independent
catalog/source/archive audit: `independent-native-decode2wg-audit.json`.
Full 1–8192 C1 sweep reuses the same secondary-node A1 baseline. The reported
8–8192 geomean is 0.998224× vs external finalize, 1.006114× vs dispatch B1
(7/11 rows faster; all retention-row tactics match). This remains near parity,
not a demonstrated net benefit. All14 rows/100 observations and112 BF16 cross-arm
outputs are present in the owner receipt; complete raw archive audit is pending.
Full tables: `candidate-benchmark/decode-comparison.md` and
`decode-vs-dispatch-timing-derived.md`. Temporal drift is not cancelled.

`513b11d46cb510455e64e6ada465f2a98503c05c` is a separate two-decode-WG experiment:
move the existing all640-thread handoff after the first cross-rank drain, before
counter cleanup. Dispatch cleans counters/publishes resets while decode performs
the exact same ordered worker loop. Transport operations and their order are
unchanged; no extra fence or barrier. Generic transport has two explicit phases
and keeps its original consecutive wrapper. Independent expanded-AST/source
review and scoped pre-commit pass; no GPU result yet. Design/proof:
`drain-cleanup-overlap-design.md`, `decode-overlap/independent-source-review.json`.
Frozen104-file source manifest SHA256
`2e29eea0ece17f7d615bea0e4f136ad55127faa4e6fe23851eab5b6085b57fe3`;
archive `3c4f55197af147a197f93be7582a10fe086004c59eba0b7f8c0f865298234add`.
Native and queued-graph validation precede timing/retention.

C1 independent full audit now passes (`independent-perf-c1-audit.json`):
51 files, 235455969 raw bytes, archive SHA256
`4ad4b44f8fe3e6ea695297e21561f93ba6569746f225db78769bfc4b3b7a2034`.
All1400 C1 observations and retainedA1/B1 observations match their summaries;
112 finite BF16 outputs match exactly for both comparisons. C1 8192 timing
quarters rise from772.580 to843.686us, so this serial comparison does not
establish causality. Combined table: `VARIANT_RESULTS.md`.

Decode queued supplemental also independently passes (`independent-supplemental-decode2wg-audit.json`):
EP2/H1024 + EP4/H1056, all4tactics, O2/O3, random/skew =96 case-rank records,
288 eager same-partial reducer checks and1536 queued snapshot checks. The16
queued replays have no per-replay host/rank barrier. Raw/public/raw descriptor
checks are separate synchronized phases; do not call that sequence barrier-free.
Archive SHA256 `77055b572ed22bbee921be3b5fe4cfdc2b053a25925b5cc406238c30823ba875`.
This uses the standalone reducer on the same partials, not an independent full
MoE reference; the large strict matrix remains a separate qualification gate.

## Four retired WGs during cleanup

`14a9e720d02472ae602ca3ed3ba121f273de4573` is a bounded tail-only follow-on to
`513b11d`: epilogue, control and both decode WGs reduce after the same early
all640-thread handoff, while dispatch continues counter cleanup. Skip dispatch's
128 thread indices with one warp-uniform branch; retain WG-striped512-worker
partition. No compute-role/register-budget, transport, arithmetic or barrier
change. Scoped pre-commit,240 CPU partitions and independent root AST/mapping
review pass. GPU qualification/timing are pending. Frozen104-file manifest
`cd9f745a3b9778084fec68590239ebad03951df9331d0664ab341b00e0198ebd`;
archive `375f762b645285ab0a1ef97cd46f1ce003fd6eabd30ded2ffe8dda6cbf261c2a`.

All5 `f5f4de65` full14 owner timing receipt reports1.005510× over8–8192 and
776.840us at8192; full independent raw audit is pending. Native25+17/rank passes.
PR branch prepared as `62de7e6`, with identical implementation/tests/benchmark;
only README corrects the copied-source ledger's old dispatch-only description.
No production retention decision or full strict/sanitizer qualification yet.

All5 profile diagnostics are running separately on primary. Initial nsyst128
reports REG96/STACK0/LOCAL0 for the core, matching the qualified baseline128
resource reference. Source/cubin/timeline and full metric interpretation remain
separate gates; no speedup is inferred from this observation.

## Reviewable PR head and nsys diagnostics

Pushed PR8 head `62de7e6367adaa8a2dcd54aec1dce0a2cb107ecf`, retaining draft status.
All implementation/test/benchmark files are byte-identical to tested all5
`f5f4de65`; README alone updates the source ledger to describe retired-WG reuse.
The PR body now contains its complete 1–8192 table and limits; no full strict60
or sanitizer pass is implied. Public layer signatures and the optional lower-
precision FC2 control remain unchanged. Final output is an internal launch
input with cached pointer/shape/stride and dynamic live rows; raw thunks keep
zero-row output ownership and the one compiled Tensor signature. No additional
public tactic, output layout requirement or float atomic path is introduced.

The separately captured all5 nsys128 and nsys8192 phases independently show
80 total graph replays with exactly BF16 staging + integrated core and zero
external TopkReduce launches. Both core captures use REG96/STACK0/LOCAL0 with
no static local-memory instructions; N64 staging cubin is byte-identical to
baseline. Current N128 dispatch-return PTX now confirms the outgoing copy,
commit and full wait0 (without .read) before next-token scheduling/tail. This
closes the prior current-codegen mapping gap; no new fence is justified by it.
Evidence: `profiling/review-all5/RESULT.md` and its hash-bound audit/excerpt.
Only rank0 codegen is in early bundles; no all-rank codegen identity claim yet.
NCU full-metric interpretation remains pending.

## Selected four-WG qualification and publication

Native25 EP1+17 per EP2 rank and queued supplemental96 case-rank checks pass
on secondary with independent audits. Full14 selected4 timing archive
5d5f3021ca224bdf595015a44ebf82d11048cabfb856734eb8b5cef7a4cffdac
passes independent audit:1.0098909607918802x vs retainedA1 over8–8192,
8/11 retained rows faster,112 exact finite BF16 outputs. Regressions remain at
8/128/256 and chronological drift limits small-gain interpretation. One final
reverse-order baseline68eb sweep is running to resolve these differences.

Published e2fc313819b98596d5ac83f6b0783b7184379267 to draft PR8. All source,
test and benchmark files match selected frozen14a9e72; only README differs.
The full selected table and pending full qualification are reflected in body.
Strict60 and main6 will run concurrently on separate existing nodes after each
node's current profiling/timing work closes. No new permission or merge action.

All5 fullNCU capture finished40 application replays and320 epoch-rank outputs,
but filename verifier assumed rank0..7 while NCU emitted other numeric report
suffixes. Original failed receipt/raw data preserved; collection-only metadata
mapping review pending. No kernel failure inferred; no completed metrics claim.

## Refreshed baseline A2 independently audited

A2 sealed archive72312b7be19720462dd1263f2c720f3881927b9bf90b70c09bbd330b9c6e0da9
has51verified files/235455062raw bytes/188706576archive bytes. Independent
raw audit ae3d2d96cb99f5c3d7261968ff8ef3ddff9659ff1f7ede495caee48325617d5f
passes all source/environment/helper/process/1400sample/output gates. Selected14
and both baseline runs agree for all112 finite BF16 outputs. Full separate tables
and original samples are retained in selected-four-wg-vs-baselines.md/json.

Run chronology UTC: A1 10:55:42–11:03:28; selected14 12:02:00–12:09:50;
A2 12:18:50–12:26:35. Ratios8–8192: A1/selected1.009890961 (8/11 faster),
A2/selected1.016513254 (9/11), A1/A2 .993485285. All14 A2/selected tactics
match; A1 differs at2048. Eight tokens is slower against both controls;
128 reverses to a gain;4096 is .998981x againstA2. No blended control or causal
small-gain claim. PR body will show the final A2 full table with explicit order.

The first independent refresh audit encountered a pathname assumption: reviewed
launch used byte-identical exported baseline manifests while the stage receipt
retained the original source-manifest path. Adapter now binds both exact paths,
all manifest bytes and reviewed command; no runtime or evidence gate was relaxed.

## Selected14 strict60 fully qualified

Independent selected14-accuracy-audit.json df497fb6f849ca83f765099f4e01564c5d81c145cabb19304f6ce56132627511
passes full_matrix_passed. Archive22b6d6801f3badfa25e1f0917eda32940310acacb3eea3ab499918d267093bb3,
922163B/132files/48315171rawB,104source files pinned14a9e72/cd9f. Counts:
60axes/960configs/2880refs/7200pairs/2400repeats/60480rank observations/
135287341056 compared elements; all finite BF16-bit exact. EP4 andEP8 launcher
return0 and every rank has30passed. Driver2176.868s (phase954.344+1221.993,
rank times not summed). Fresh owner closure separately binds launchPGID/source/
finish/nodeboot and empty owned group/GPU processes. Summary:
SELECTED14_ACCURACY_RESULT.md. Main6 racecheck remains pending.

Docs-only2c16abe028ec92ba343b3420253f6b8f1cc0a6d6 corrects the README transport
row to non-dispatch WGs. No non-README file differs from tested14a9e72.

## Selected14 main6 qualification complete

The unchanged, pre-reviewed selected14 auditor41634760 passes all terminal
checks. selected14-main6-audit.json SHA4538c8620149af88c2a455bc42d215ad068d3fa921b780b049778bc179a160dd;
archivecf4415c3401693c9abc9df4c2e570c0577f690094ff64da25d920290d5e8d555
contains126verified members/136841rawB/22931archiveB. All104frozen14 source
files rehashed. Six tool/EP batches,36rank reports,216workload-rank cases,
864tactic-workload-rank cases pass. All24mem/sync reports have zero errors;
all12race reports have zero hazards/errors/warnings with no extra diagnostic.
Driver5244.035s (setup/compilation/checker overhead included, not kernel timing).

The preserved original verification.json failed its old12-argument metadata
schema; the selected14 auditor already pins the reviewed13-argument launch
including --tb=native. No runtime, source, checks, or scope changed to pass.
Separate owner closure binds exact hu115/boot/PGID81918/source/finish and empty
owned-group/GPU lists; independent terminal review confirms that recorded
closure. See SELECTED14_SANITIZER_RESULT.md and selected14-main6-terminal-review.json.
Scoped checks cover MegaMoE+BF16 staging, default deterministic finalize. IKR,
external kernels and arbitrary global/NVSHMEM/TMEM ordering are not established
by this sanitizer run. The existing tensor-ops checker workaround remains.

Final PR8 body published at2c16abe028ec92ba343b3420253f6b8f1cc0a6d6,
SHA b3afa8412bdc96a3a0f20c77e3ec1b40e7f2c5bfaa222518a49e76c567b119eb.
Remote exact head/body/draft verified in pr8-final-verification.json; GH account
restoredzianglih. Includes final A2 full1–8192 table, independent strict60 and
main6 results, reproduction/tool setup. Performance remains a modest serial
observation with drift and an8-token regression; no robust gain or merge claim.
Secondary release authorized after independent terminal audit; owner performs
fresh identity/idle/evidence closure before deleting only that devbox.

Secondary release completed and exact inventory absence verified in
gpu-setup/release-receipt.json after fresh hu115/boot identity, empty owned
groups/GPU lists, and32local evidence archive rehashes. Both task-owned
devboxes are released; all local artifacts retained.


## Owned finalize helpers and early preparation

Ownership-only commit `04c51ad94738877e67045ece949ed16cd12c6f82` is pushed to
PR #8. It owns the specialized BF16 reducer and transport tail phases under
`cute_dsl/megamoe/bf16_nvfp4/`, retaining the unchanged universal transport base
through the package facade. All shared `kernel_src/cutedsl_megamoe/` files are
restored to main; the PR has zero net edits there. Executable source AST checks
and scoped hooks pass. The fresh 12-pair generated-code matrix and native/queued
numerical checks are running on C2 B300 node hu-pdx-99, boot
af9b307c-73d6-415d-898c-6cb2664707e5, image nvcr.io/nvidia/pytorch:26.05-py3.
Full strict60/main6 qualification remains attributed to14a9e720. See
ownership-refactor/pr8-scope-verification.json and frozen-source/receipt.json.

Early-preparation experiment is independently committed as
`859854169d7df51e6fc7ed03d5ad612619f94e2d` in the project-local
`early-reduce-prep/hashinfer` worktree; it is not pushed to PR #8. The retired
four WGs prepare worker coordinates and the first live worker's immutable local
routing scores during dispatch's FC2 drain. The existing second640-thread
handoff still gates all FC2 partial reads. One reduction loop handles every
worker, preserving the packed FP32 multiply/FMA sequence and BF16 cast. No new
barrier, fence, public knob or shared-source edit is introduced. Scoped hooks,
independent source review, arithmetic AST and72 work-partition cases pass.

Candidate106-file archive:8a16f1ffaa0698d0864b979388162c88466b423608a84674b44fbc1da5826139;
manifest:cedd46827da11acadef10aa914f6e1a29300020ecfdcfce8a8e3d017152a10cf.
The reviewed baseline driver will measure04 on the same node after its checks.
Candidate codegen placement, resource inspection, numerical validation and
matching1–8192 timing remain pending. Retention compares candidate with04,
using8–8192; no split/cross-node/old14 timing substitutes. Detailed dependency
proof and implementation limits are in early-reduce-prep/implementation-design.md.


A second independent prototype, `24b794f1f20b4a7e2b92a94ce2c23bdbd59f74f8`,
changes only the reducer strip width from128 to32 in three constants, plus its
comment. It is based on04 rather than859 so work distribution can be evaluated
independently of early preparation. Roles, arithmetic, stride, barriers and all
other module AST are exact. Scoped hooks and partition/coalescing checks pass;
no GPU launch or PR promotion. Worktree/evidence: `warp-striped-reduce/`.
Source106-file archive8cb7917824f75a5fde256abff4d25d8e98283e40e152f55c00a09a54a4510645;
manifest388d144131259eef072247b6431e2a7adc287615e847b1cb109f342d4b7a5b56.
Current GPU queue remains04 qualification/baseline, then859 placement/numerics/timing.


### Ownership04 qualification complete

Full local independent codegen audit passed:12 cases/96 rank pairs, all192
stage/core CUBIN pairs byte-identical,576 PTX/SASS/resource comparisons equal,
and finite BF16 output equality. Every captured core reports REG96/STACK0/
LOCAL0. Archiveb7cdf818ed14cb8f468272db8f986c0457a9b9b14ca8e47d6703b0427c7c8fa0;
receipt `ownership-refactor/collected-codegen-remaining/full-matrix-approval.json`.
Native25 EP1+17 perEP2 rank passed (42 logical/59 rank executions,218.699s);
independent-native-audit.json SHA6260352e08e1639abb9e641d6b1bfc819cb38bcb8ad2d1167271836e866fa5d4.
Queued96 case-rank records/6 summaries passed:288 eager and1536 queued checks,
124.180s; independent-supplemental-audit.json
SHA45cad69eccba8514eeec7692cbcb3ea34fef7fb927508e3c7619fc6d22e19ccd.
All106 source files and exact setup/node/boot/helper pins verified. These are
fresh bounded04 checks, not fresh strict60/main6 or current-head timing.

PR8 remains draft at04; body updated with this qualification, explicitly
preserving14 attribution for full qualification and old measured table.
Remote receipt: ownership-refactor/pr8-qualification-verification.json;
bodySHA58f2f6929d8a7d41d8296e5f5aacfbba66e7fdea24cc498cf3539b05ba7a4298.
GitHub identity restored tozianglih. Fresh04 baseline launched alone onhu99,
PID/PGID66247, after all gates; no profiling/transfer/other GPU validation
concurrently. No baseline or859 performance result yet.


###859 held before execution: aligned-barrier contract

A fresh PTX ISA review found859's two warp-conditional second-handoff sites
violate the intended CTA-convergent source contract for aligned named barriers
unless the compiler merges them; we will not rely on that optimization. No859
GPU execution has occurred. Preserve859's frozen artifacts, stop its queued
launch, and replace it with one common handoff source site around guarded
prepare/consume phases.04 has a common site already and is unaffected; its
baseline continues. Earlier source reviews missed this constraint; see
`early-reduce-prep/BARRIER_REVIEW.md` for the primary reference and resolution.


Corrected candidate53caea384acd53cadce44d276d8a8a155b3c119d is committed/frozen
under `early-reduce-prep-convergent/`; source remains in the original early-prep
worktree. One common second handoff dominates the unchanged consumer; source,
scoped hooks and independent review pass.106-file archiveee1414c357ed5c150108efc3d18ca5602d59c935e1f97a737fdd1790a2c97ea1;
manifest2eee96a867fa45a9a94afdb3e04c0971466d159fe512b0cfd2138025c2037450.
Old859 remains unexecuted/held. New helper/capture/validation namespace is the
sibling early-reduce-prep-convergent; completed04 baseline is reused explicitly.
All14 BEFORE rows finished cleanly. A managed SSH reset interrupted only the
sealed archive transfer; owner preserves/resumes verified chunks, no GPU rerun.


53 capture completed all4 H7168/global128/O3 tactics across8 ranks. All32
outputs are finite and bit-exact04; staging CUBIN unchanged. Capture archive
SHAa4a081656bec6ede1b29c037f98537ff1148a6367855d899c3fb09676214128d,
18,074,529B/597files. PTX/SASS review confirms scores before the common second
640-thread handoff and combine loads after. Core remains REG96/STACK0/LOCAL0,
with unchanged per-role register budgets. Three scalar-default instructions
remain in SASS (tactic0 HFMA2 R0=0, CS2R R44/R45=0, UMOV UR10=0); do not
claim cost-free dispatch setup. The timing sweep decides the benefit/cost.

53 native independent audit passed:42logical/59rank executions,220.136s;
receipt early-reduce-prep-convergent/independent-native-audit.json
SHA7139fd3aad133044998a1b1ae610920e2ea00df89cf7c6c963fa02d265aaf9fb.
Queued checks and timing remain pending. The verified04 BEFORE is preserved
at early-reduce-prep/BEFORE_TIMING_RESULT.md, with all100 samples perrow;
8192 retains late drift and cannot establish a small optimization gain alone.


53 generated-code review completed: manual-placement-review.json
SHA cfed1c4cdefa95a7764067646bf8e08ae75e496742d300830e5cd4b08f2fd877,
including actual per-tactic SASS CFG and one shared secondbarrier site. Three
retained scalar-init instructions are recorded rather than treated as free.
Queued53 independent audit also passed:96case-rank/6summaries,288 eager and
1536queued checks,112.260s; receipt independent-supplemental-audit.json
SHA4a2b501411c299e2cd9e121bbfc197fbd4430f6201238c05b395b4b19d7f1726.
After all three source/codegen/native/queued gates, root authorized reviewed
c90e4e0a AFTER against the fixed04 baseline, with no competing GPU work/transfer.
Performance remains pending; full strict60/main6 has not been run for53.


### Broader decode-first preparation prototype

Committed36461de4f81c03e899e9a07ef3bbbfb7a8b83866 in isolated
`early-decode-prep/hashinfer`, based on53. Its two constexpr preparation phases
assign initial work to retired decode WGs and prepare their metadata/scores
before the first common CTA rendezvous. Epilogue/control prepare in the second
compile-time phase during the collective drain. The owned transport's first
rendezvous moves to the sole owned caller; its dispatch drain body is unchanged.
One common second handoff still precedes every FC2 partial load.128-lane strips,
consumer math, five-WG layout and register budgets remain. No runtime phase loop,
new barrier/fence/public knob, duplicated reducer, or shared-source modification.
Net diff versus53 is52insertions/38deletions in two owned files.

Source/hooks/phase+partition proof and independent reviewb45e370c pass; GPU
lowering, numerical/sanitizer and timing qualification are pending. Original
split-barrier draft artifacts remain under held-split-barrier and never ran.
Freeze106-file archive095466782303d638d99a47525135509f444062ddb154ade9911811ec870ac233;
manifest466975eff943c7d1ca6a33b65f716700c46bdc3cdb8228687218efb0eda2bdbf.
GPU owner prepares helpers locally during53 timing, stages only after that arm
seals, then follows codegen/native/queued/timing gates. Reuse04 baseline and
retain53 for a direct incremental comparison.32-strip prototype remains unqueued.


### Verified early-metadata timing and decode-first queue

53caea3 completed its full CUDA13.2 EP8 H7168/I2048/E256/K8 AUTO4
1–8192 sweep against the sealed same-node04 integrated-combine baseline.
Independent full-archive audit7d417f70 passed:1400 samples/arm,112 finite
bit-exact rank outputs, identical fixtures, and all14 rows preserved. The
8–8192 geometric speedup is1.013773058x with7/11 rows faster. Tactics match
on13/14 rows; only1 token changes N128 toN64. Full latency/MAD/winner table:
early-reduce-prep-convergent/TIMING_RESULT.md. These are observed serial-arm
results, not a drift-cancelled causal estimate;8192's0.995197x is within its
substantial within-arm spread. No sample is excluded.

The AFTER raw archive65ecaeb30ef09a18e7f06729dc272ee49d63acb3c80e72eeaaa09620c3c2ff56
is fully recovered and verified at188712462 bytes/58 members. A truncated
transport was resumed with prefix/chunk/full hashes; no GPU timing was rerun.
36461de codegen capture follows the sealed timing arm on the same owner/node;
performance must await codegen, native and queued checks. PR8 remains at04.

The read-only prologue analysis in early-decode-prep/prologue-feasibility.md
finds that physical SM register headroom is not part of the current CTA pool.
REG96x640 reserves61440, exactly consumed by144/80/64/96/96 role budgets.
Raising both decode WGs to104/112 without safe redistribution is invalid and
can deadlock. A future scores-only longer-lived experiment must first fit the
unchanged96 budget and prove no spills. No budget change is queued.


36461de qualification gates passed before timing: all32 finite codegen outputs
match04/53; allfour PTX/SASS variants retain one common first and second
barrier, decode score loads beforefirst, other score loads between, allFC2
loads aftersecond, and one ordered packed reduction body. No runtime phase
loop or static spills;REG96/STACK0/LOCAL0 and role budgets unchanged. Manual
receipt e24ed13c records retained scalar setup overhead. Native42logical/59rank
passed226.424s (audit283882bf); queued96case-rank/1536checks passed124.407s
(audit1271988d). Root ran the prepared pin-only numerical auditors locally.

Reviewed364 AFTER driver6abf2799/runtime db549fb6 launched serially after all
gates, bound to original04 and retained53. This arm's timing remains pending.
No strict60/main6 qualification or source promotion is claimed for364.

A separate local pre-producer-tail prototype is being prepared while this
sweep runs: decode metadata immediately after its final transform loop and
before the unchanged producer-tail wait. A narrow private helper replaces
constexpr phase orchestration, preserving common CTA barriers and allconsumer
math. It is not queued or part of frozen364. Read-only design is saved at
early-decode-prep/pre-producer-tail-feasibility.md.

### Decode-first timing and pre-producer-tail resource repair

The 36461de full 1–8192 sweep completed and passed the independent three-arm
archive audit (d6f46a8515bb50479fd3d158b3eafb480c3252ea3da7b232ad8d8d8e876793de).
Its 8–8192 geometric speedup is 1.002818308x over 04 and 0.989194080x over
53; the mixed result is not promoted. Full medians, MAD, tactics and limitations
are in early-decode-prep/convergent-v2/independent-timing-audit.md.

The subsequent 1ba42a3 prototype prepares decode metadata before its unchanged
producer-tail wait. All 32 captured rank outputs are finite and bit-exact, and
native coverage passes 42 logical / 59 rank executions in 229.20 seconds
(independent audit 5c3be4f8e532178eac0f091b5cd86456e52afd36fec1ba750fc2090bc470b819).
However, actual SASS contains spills: 39 LDL/STL instructions and STACK48 in
tactics 0/2, 20 LDL/STL and STACK32 in tactics 1/3. REG96 and reported LOCAL0
alone do not establish absence of spills. Queued tests and timing are held.

A source-order repair, ee70815d70fc8c656372d124a6a4523a0e15d883, moves the exact
decode role block and its stable combine setup after the other mutually
exclusive compute roles. No math, pipeline, barrier or register budget changes.
Both local AST permutation checks and an independent per-warp control-flow
review pass. This is a live-range hypothesis, not a demonstrated spill fix;
GPU codegen capture is next. Workspace: pre-producer-tail-reordered/.

The isolated partial-load L1 no-allocation experiment (22a61eb) is also held
because its base is 1ba. It will be rebased onto a resource-clean measured
base. It changes only the owned reducer's single-use FC2 partial load, using
CopyG2ROp so CuTe 4.7.1 actually receives the hint. No ordering/fence semantics
are attributed to the hint, and emitted PTX/SASS must still be checked.

Input staging fusion is being implemented separately in input-stage-fusion/.
Dispatch copies aligned BF16 inputs and retains existing routing ownership,
capacity-tail masking and publication barriers. Only activation-writing
threads perform the generic-to-async proxy fence. This first prototype retains
routing metadata copies, so launch fusion can be evaluated independently of
later layout/metadata elimination. CPU ownership and host-state checks pass;
GPU compilation, accuracy, sanitizer and timing are pending.

### Fused staging becomes the sole public forward path

User steering removes HASHINFER_MEGA_FUSED_STAGE and the standalone-stage
fallback from the intended public path. The new staging prototype therefore
supports empty and legal strided/expanded/misaligned sources inside MegaMoE.
Four warmed compile signatures cover int32/int64 IDs and contiguous-vector /
generic-stride activations. Typed pointers and explicit runtime rows/strides
avoid unbounded layout specializations. The explicit low-level pre-staged API
remains separate and compiles only when used; it is not a public-forward
fallback. No extra symmetric workspace or source-copy allocation is added.
The existing graph test now compares four caller layouts with identical
contiguous inputs, including first generic-layout capture after normal warmup.
Owned standalone staging files and their sanitizer filter/environment override
are removed in the prototype. CPU host-state checks pass 12 cases; GPU evidence
is pending. No staging source is promoted yet.

### Source-order repair exposes scheduler state ownership

The ee70815 reorder fails CuTe verification before any GPU execution. Diagnostic
IR proves a scheduler ring index/phase value escapes the earlier epilogue role:
`pre-producer-tail-reordered/gpu-setup/failed-core-rank1.mlir` line 17817 uses
`%6946#0` for an eight-field scheduler-buffer coordinate, while its definition
at line 5313 belongs to an earlier role's pipeline-state advance. This is not
an observed device hazard or a performance result. Both failure attempts and
the raw-IR diagnostic are preserved; no verification was disabled.

Successor 1ad281df3b74a10c926edebc590c055d5e70c1ba creates each scheduler consumer
inside its own warp role, matching the shared MoESchedConsumer documentation.
It adds five role-local constructions and removes the single shared one;
barriers, register budgets and arithmetic remain unchanged. Source/hooks pass.
GPU capture is pending under pre-producer-tail-local-consumers/ before deciding
whether the reorder actually removes spills or improves performance.

### Role-local consumer qualification and always-fused staging freeze

1ad281df now passes the canonical H7168/T128/O3/EP8 captures: all 32 finite
outputs exactly match 04 and 364. Manual generated-code review confirms that
decode score loads precede the unchanged final producer-tail waits, while all
FC2 partial loads remain after the second common CTA barrier. Role budgets and
ordered packed reduction arithmetic are unchanged. Three tactics have no local
loads/stores; tactic 0 retains one 32-bit spill slot (STACK8, seven static
LDL/STL, including decode-loop loads). This is accepted for measurement, not
reported as spill-free or promoted. Manual review hash:
1abc145232b4f10b23d511d0c41892a05de96087b7b299c3caf5df1114432d5a.

Native coverage passes 42 logical / 59 rank executions in 209.894 seconds;
independent audit fc07006e7b541cb5f50c81b224c838ad6fa0cab8ca81560d75b3db7bebab56f5.
Queued coverage passes 96 case-rank records, 1536 queued snapshots, and 288 eager
same-partial checks in 120.786 seconds. The GPU owner executed the unchanged,
independently authored auditor with exact candidate pins; root inspected the
receipt. Audit 8505377ea60ed6e600c3247e75dfaf5cb6f1df847691b2b11f0140bf7ca8172d.
These bounded tests do not replace the full numerical/sanitizer suite. The full
1–8192 timing arm is running serially against the sealed 04 control.

Always-fused staging is frozen at f668598a03fe4509ce8521211adb734a4caebc76,
including the same role-order/local-consumer repair. The clean worktree contains
104 tracked files; archive a131f6e1ed86d22dce4b30a05cb582d8bf045822f1365deef69c5395d428c1eb,
manifest 9a86fb565fc50efede939f31ed3698e0bd5380277f6a844a172c646516a55f1f.
The source-only tail-port audit proves only the intended role permutation and
consumer initialization change relative to the always-fused cleanup. Four ABI
capture tooling and an independent CPU comparator are ready; GPU compilation,
copy-width/proxy-fence review, correctness, sanitizer and timing remain pending.
No environment switch or public-forward standalone staging fallback remains.
The new existing-test layout axis raises native coverage to 48 logical / 65 rank
executions (31 EP1 and 17 per EP2 rank).

The separate FC2 partial-load NO_ALLOCATE candidate is rebased without other
changes onto 1ad as 1e0ad3bf58def4c4b55693b6246b503714cfeb7e. It remains local
and unmeasured; staging is the next GPU capture after the current sweep.

### 1ad full sweep: no demonstrated aggregate gain

The complete 1–8192 timing archive passed the root's independent audit:
2e33b67fc6a34dd2eacc62b29f1d8b11af6d80b1dacbc919ffd0e1bda0bb5c99.
All14 rows retain100 rank-MAX samples; all112 finite BF16 rank outputs exactly
match04 and53. Archive62d65a331c208d21eefe5ae7ce1b111e24e792852b028677ac51ea3a6e256cb4
contains58 files/188712061 bytes. A managed-SSH reset interrupted download;
verified chunk/prefix resumption recovered the same sealed archive without any
benchmark rerun or source change.

8–8192 geometric speedup is0.997002141x against04 and0.983456931x against53.
Only4/11 rows improve against04;64 tokens improves5.889%, while8/16 are about
1.6–1.8% slower,4096 is2.54% slower and8192 is2.00% slower. Serial drift remains
a limitation, particularly the large row's spread; the result does not justify
promoting this tail-only change. Full table/MAD/tactics and raw-sample trends:
pre-producer-tail-local-consumers/independent-timing-audit.{md,json}.

Fused staging remains based on1ad for an isolated comparison of launch fusion,
and will also compare against public04. The canonical f668 capture has compiled
allfour ABIs for the firsttwo tactics and passed their16 rank outputs so far;
this is nonterminal, not a full qualification. Native tests may run while sealed
capture evidence downloads, but timing waits for codegen, native and queued
review. A second devbox is queued for full bit-exact/sanitizer qualification.

The separate caller-source cache trial08e78064a9a90c0be337be561b7efc6ac739ec3b
is frozen onf668. It changes only the proven contiguous128bit source load to
CopyG2ROp with L1 NO_ALLOCATE; generic source loads, destination stores and all
publication/math are unchanged. Source checks/hooks passed; no GPU evidence.

### Correct the fused fast-path specialization before timing

Independent capture verification passes for f668:789 members,32 finite output
triples against04/1ad,128 ABI artifacts, and identical raw code/resource hashes
across all8 ranks within each tactic/ABI. Root inspection found the nominal
vector ABI still uses row/remainder mapping and8 scalar BF16 source loads.
Its unannotated Python integer stride tuple became runtime Int32 parameters;
`cute.is_static(hidden.stride)` was therefore false. The destination store is
already128bits. This is a performance-specialization defect, not an observed
numerical error or artifact overwrite. Details: input-stage-fusion/
scalar-fastpath-diagnostic.{md,json}. No f668 performance sweep will run.

Successor f655751d6d736cb755be34f7eabb10a3e934a120 passes all12 host checks and
scoped hooks. It uses None for the private contiguous-stride descriptor and
constructs `(self.hidden,1)` inside JIT; generic runtime strides, pointer alignment,
copy helper and synchronization are unchanged. This is two files,10+/3−, with no
runtime selector or new public knob. Source frozen104files, archive
f1ee17c50722fbb9fcf6c46071ffdff515b473c24a40e257fedfd14108f4da22,
manifestef1e912ef06d30b855f6a5e75d75a1b0920b6ef963ffdae7f5ba32585a46dbd3.
The first fused native run is allowed to finish; queued coverage of superseded
f668 is deliberately skipped. Primary f655 capture/native/queued follow, and
timing remains gated on the actual generated128bit path and numerical checks.

Second node hashinfer-fused-qual-0918 (c2/infra, hu-pdx-7,
boot30b16995-7b03-4179-8699-1f7be11b670e) was requested with explicit
nvcr.io/nvidia/pytorch:26.05-py3 after a fresh catalog check. The personal queue
had no quota; infra quota was accepted and later physical capacity became ready.
Setup preserves the same Torch/CUDA13.2,CuTe4.7.1,NVSHMEM3.6.5,CUPTI13.2 and
sanitizer2026.3 versions. No primary-node operations are owned by this worker.

To avoid keeping the new node idle, root authorized independent full f655
bit-exact qualification after the narrow fix's source/host review, in parallel
with primary codegen/native work. Strict60 launched asPGID2411 at
1789767598.1581535 after104-source/helper/node/idle verification. Main6 may follow
only its successful same-source terminal closure. A source hold file can stop
that progression if a successor is needed. These suites are running, not yet
claimed passed; the first randomEP4/t1 checks are finite and bit exact.

### Fused vector copy confirmed; reduce host compilation separately

The complete f655 capture passes independent source/archive/output verification:
32 finite bit-exact outputs against 04/1ad and 128 tactic/ABI/rank artifacts.
All eight vector tactic/ID combinations now contain a 128-bit source load and
destination store; generic code is unchanged from f668. Resource usage matches
the tail-only base: REG96 everywhere, tactic 0 STACK8/seven static local-memory
instructions, and tactics 1–3 STACK0/no local-memory instructions. Manual review
also passes all 16 combinations: writers fence before routing publication,
early score loads precede final producer-tail waits, and FC2 partial reads
follow the second common 640-thread barrier. Receipt:
input-stage-fusion-static-stride/manual-codegen-review.json,
SHA256 c5b1da851e9ca1238cae4df8103e32a4af639e60d6ec25f1c3d89789571d939c.
Native/queued tests and strict60/main6 remain in progress, so no full
qualification is claimed.

The superseded f668 native suite completed 48 logical / 65 rank executions with
no failures in 927.84 seconds. Its queued and timing arms were deliberately not
run after discovering scalar source loads in the nominal vector specialization.

Host-only successor 7dc9626909834bc70209e09784e9dfdebadceff2 compiles only the
active ABI during private AUTO trials and warms all four ABIs for the final
public configuration and fused raw thunk. Its 16 CPU control-flow checks and
scoped hooks pass. The only edits are frontend/backend preparation; device code,
compile/launch builders, math, barriers and public capture readiness are unchanged.
Source-level compile-call counts drop from 16–20 to 7–8 for a cold four-tactic
search. This is not a measured startup improvement. The independent review is
input-stage-fusion-compile-warmup/independent-source-review.json.

Primary-node plan: finish the already-running f655 native/queued checks, then
verify 7dc generated-code equality and public AUTO/first-generic graph behavior.
The focused host gate uses the existing 11-case EP1 graph test file and the
unchanged 96-record queued harness; it does not repeat the entire reference/EP2
suite. If those gates pass, run one complete 7dc 1–8192 timing arm against the
sealed 04 and 1ad baselines; do not also run a redundant f655 timing arm.
Secondary-node strict60/main6 remains on f655. Any eventual reuse of that device
qualification must explicitly record the codegen bridge and separate 7dc host
validation.

Two independent cache-policy candidates were ported onto the corrected f655
base without other changes: 4d20f000b26fc90c259b17e8bb304b8b534874e7 changes only
the vector caller-activation load to CopyG2ROp/L1 NO_ALLOCATE;39fa0ef35a3d0f7486eb1cbb9a7058bd1df58893
changes only the ordered combine's FC2 partial load to that policy. Both are
local, source-checked and unmeasured. Destination stores, generic source loads,
routing-score caching and all publication fences remain unchanged. Evaluate
their effects separately after measuring the unchanged-policy fused path.

### Fused native/replay gates pass; isolated next trials prepared

The corrected f655 build passes the complete native suite: 31 EP1 cases and
17 cases on each EP2 rank, or 48 logical / 65 rank executions, in 904.34 seconds.
Independent audit: input-stage-fusion-static-stride/independent-native-audit.json,
SHA256 f0074d0426c8c5c8931daca7fc474015537abe45e7ca12faf638cd7813b94d40.
Its queued replay suite also passes all 96 case-rank records / six summaries,
including 1,536 queued output checks, in 275.45 seconds. Independent audit:
input-stage-fusion-static-stride/independent-supplemental-audit.json,
SHA256 eb3c43c447e140412df0df31a86e7f86e27a6eedd1038eb499cfe58729137fa1.
The full bit-exact matrix is still running separately; sanitizer has not started.

The host-only 7dc successor is now undergoing its generated-code identity gate
on the primary node. Its focused graph tests, queued checks and single full
timing arm follow only on success. No f655 timing arm is needed.

The two isolated cache trials now have corresponding 7dc-based successors:

| Trial | Commit | Workspace |
| --- | --- | --- |
| Caller activation L1 no-allocation | `4d527ac603cc61eaee31ef490b03ca43cbb85883` | `input-stage-source-cache-hint-compile-warmup/` |
| FC2 partial L1 no-allocation | `8b8b1ec551635f85f43b965a46757e2b48a67933` | `combine-cache-hint-compile-warmup/` |

Both retain exactly the earlier one-patch device changes and pass scoped hooks
and full-module AST reversal checks. The plan in
input-stage-fusion-compile-warmup/CACHE_HINT_RETENTION.md reuses the measured 7dc
baseline and runs each full 1–8192 sweep separately. Existing capture/codegen
and queued checks cover these cache-only changes; the host graph suite is not
repeated because host/ABI preparation is unchanged. No cache trial has run.

A third, lower-priority source trial is prepared at
input-stage-prologue-overlap/hashinfer, commit
e37cf879a7a4a687ae706be5608238fbe3d695b1. It moves the exact dispatch register
release and input staging between common pipeline initialization arrival and
wait. Every barrier, allocator call, later dispatch operation and register
budget is preserved. This may overlap cluster-arrival skew and early scheduler
initialization; dispatch already bypasses the TMEM allocation wait, so do not
claim newly hidden TMEM allocation. It adds a second warp-role guard site, with
no data-dependent selector or public knob. Source reversal and scoped hooks
pass; actual branch/spill changes and performance are unmeasured. No GPU run is
queued for it.

The fused profiling bundle is ready at
input-stage-fusion-compile-warmup/profiling/. It selects fixed tactics only from
the completed final timing arm, expects one fused MegaMoE graph kernel, and
prepares five Nsight Systems graph replays plus full-metric Nsight Compute
application replay across all eight ranks with MEGA_USE_NCU=0. It has passed
offline checks only; no new profiles are claimed.

### Host cleanup: one compiler CSE variant, not complete binary identity

The 7dc capture passes all 32 numerical comparisons but fails the strict
128-CUBIN identity gate. Exactly one binary differs: H7168/T128, tactic 1,
rank 0, int64 IDs with generic activation strides. The other 127 CUBINs are
byte-identical to f655, including the other seven ranks of the same variant;
all resource reports match. The failed identity receipt is preserved.

Root and the independent auditor traced the actual difference. The compiler
reuses the linear dispatch-warp index prepared for routing rather than
recomputing it before input pulls. Both expressions equal
`(warp - 8) + 4 * (ctaid.x + ctaid.y + 2 * ctaid.z)` modulo 2^32. The earlier
value has no intervening write. After removing only those nine redundant PTX
index instructions, the remaining 7,155 lines match exactly under a consistent
register mapping; every non-register byte is unchanged. There is exactly one
register merge, joining the two equal old values. SASS has eight fewer static
instructions: nine index/address operations disappear and one padding NOP is
added. Barrier/fence counts and reported resources are unchanged.

This is real compiler common-subexpression elimination, not binary metadata,
and no performance gain is attributed to this isolated compilation variation.
The root accepted a narrow, hash-bound equivalence exception after inspecting
the raw chains and SASS inventory. Timing remains gated on the existing
focused graph and queued checks. Describe the evidence as 127 exact binaries
plus one reviewed equivalent index-CSE variant, never as a complete binary
identity pass. The original strict checker/result remains unchanged.

### Publish the fused-only implementation as a draft

7dc passes the focused 11-case graph suite and unchanged queued suite (96
case-rank records / 1,536 snapshots). The complete 1–8192 performance arm is
running on hu-pdx-99 as PGID 200499 with the unchanged 100-sample methodology,
comparing against sealed same-node 04 and 1ad controls. No timing result or
performance-retention claim is made yet.

The implementation was fast-forwarded and pushed to draft HashInfer PR #8 at
7dc9626909834bc70209e09784e9dfdebadceff2. Its title and body now describe fused
input staging plus integrated deterministic finalization, with current native/
graph/replay evidence and explicit pending performance/full-suite status. The
previous performance table is labelled historical and does not measure fused
input staging. This is publication for inspection, not a claim of a new best.
No shared protected kernel-drop file changes or HASHINFER_MEGA_FUSED_STAGE
references remain in the tracked implementation/tests/README. The checkout is
clean. Read-back receipt: pr8-fused-publication.json; GitHub body SHA256
d350e2b23565c8b96a904bcfe72c8b0bc4b126523233a96ad8dd5aeaa48c95cf.
The prior PR body is preserved as PR_BODY.before-fused-input.md.

### Always-fused staging: complete 1–8192 timing

The frozen 7dc full sweep passed on the existing hu-pdx-99 boot. Its 605.97 s
arm uses all 100 cold-L2 CUPTI samples per row with the unchanged public-forward
method. The independent CPU audit verifies all 1,400 samples per arm, 112 finite
bit-exact rank/token outputs against both 04 and 1ad, source/helper identity,
node/boot, launch chronology and endpoint process closure. The complete table,
MAD and tactic selections are in
`input-stage-fusion-compile-warmup/independent-timing-audit.md`; detailed quarter
medians and bindings remain in the JSON. Audit SHA256:
`0477e8dec1e2a55b5121c18f8e4229f0f37a6ca8063ed8ceee2bd8eb9f4d470b`.

For 8–8192 tokens, 04/7dc geometric speedup is 1.0297369804x (8/11 faster);
immediate 1ad/7dc is 1.0328332693x (9/11 faster). Gains concentrate at 8–512;
1024 and 8192 are about 0.5% slower than 1ad in this serial run. All retained
rows select the same tactics across the three arms. No fresh f655 timing exists,
so none of this GPU gain is attributed to host-only compile preparation. Serial
controls retain temporal drift; quarter/MAD diagnostics do not remove it.

The fused-only public behavior remains the intended implementation. The PR's
performance table is being refreshed with this explicitly incremental comparison;
main68's old cross-boot numbers are not mixed into a new full-PR speedup. New
full strict60 and main6 qualification remain pending on the secondary node.

Root authorized isolated activation-source hint 4d527ac6 after this audit:
existing capture/codegen review, queued checks and one full 1–8192 sweep versus
sealed 7dc. No native11 repeat, combined cache hints or extra tuning dimension.
FC2-partial hint and prologue overlap remain prepared/unmeasured. Profiling
plans bind 128/8192 to the actual 7dc winners but have not executed.

Docstring-only follow-up 8375077 is pushed to PR8 and changes no runtime code.

### Prepared three-WG staging and metadata overlap design

`input-stage-multiwg/hashinfer` contains isolated 69c36e20, based exactly on7dc.
It borrows dispatch plus both decode WGs for activation copying, preserving the
first128-lane strip across all CTAs. The two owned files split activation/routing
staging and move only the activation work before the existing init arrival;
fused arrivals gain release ordering, while raw pre-staged calls remain relaxed.
No barrier, public knob, compute role or register budget is added. Local AST,
copy ownership and scoped-hook checks pass. Generated code, numerical behavior
and performance remain untested. Root reviewed the mapping, public batch-shape
invariant and PTX pre-arrival memory-order requirement. Actual collected CuTe
helpers, not their reversed nearby comments, bind the intended arrive/wait calls.
The main tradeoff is losing existing copy/TMEM-allocation overlap.

A later alternative could give activation copying to only the two decode WGs
while dispatch stages routing and runs dispatch_prep concurrently. Source review
found no activation/TMEM dependency in prep, but inherited orchestration must be
split in owned code while preserving all later publication/scheduler/pull steps.
This is design only; no no-op override, runtime flag or additional trial was
implemented. See input-stage-multiwg/DECODE_COPY_DISPATCH_PREP_DESIGN.md.

### Activation-source cache hint: generated-code gate

4d527ac6 capture passes all32 finite exact output pairs versus7dc and all128 ABI
artifact checks. Each of64 vector ABI comparisons changes exactly one encoded
cache-policy bit: caller-source LDG.E.128 becomes LDG.E.NA.128. Instruction
addresses, registers, stores, fences, barriers and resource reports otherwise
match. All64 generic binaries match f655;63 match7dc, with the remaining exact
reverse of the already reviewed one-off CTA-index CSE. Manual receipt:
input-stage-source-cache-hint-compile-warmup/codegen-cache-review.json,
SHA d77054e7ac203be15d3c6976fc9d3e9a808f4f38feee8bf4f903ae14ea932559.
Queued96 is running; full1–8192 timing follows a clean pass. No hint performance
claim or source promotion is made yet.

### Activation-source hint decision and next staging candidate

The 4d527ac6 queued suite passed (96 case-rank records / 1,536 snapshots), and
its complete 1–8192 sweep was independently audited. All 112 output pairs match
7dc and 04 exactly; all 14 selected tactics are unchanged. The primary 7dc/4d
geometric speedup over 8–8192 is 0.995104878x, with four of eleven rows faster.
128 improves by 8.752 us, but 16 slows by 5.5205 us. The 8192 row has appreciable
within-run upward drift in both arms, so it does not establish a strong isolated
cache-policy effect. Keep the hint as an unpromoted experiment; 7dc remains the
performance baseline. Complete table and variability are in
`input-stage-source-cache-hint-compile-warmup/RETENTION_RESULT.md`;
independent audit SHA256 is
`28a46f898aa729b4616614aacc8c0b8bf302030bdef7e18a623b5fbffae433a7`.

The preferred three-WG candidate is b215a7d22784fd7675452cb9df70d6e29dcf0722
in `input-stage-multiwg-retrieve/hashinfer`, based exactly on 7dc. It retains
the original init/cluster-wait/TMEM-allocation order, lets dispatch and both
decode WGs copy activations alongside warp-0 allocation, and reuses the single
existing TMEM retrieval barrier as the writer-to-dispatch handoff (544 fused
participants; unchanged 416 for raw pre-staged calls). No new barrier, knob,
role or register budget is introduced. The tradeoff is that TMEM consumers now
also wait for staging, potentially delaying initial decode runahead. Source
checks pass; device codegen, correctness and timing remain pending. The earlier
69c36 pre-init variant is preserved rather than combined with this candidate.

7dc Nsight Systems capture completed for the actual 128 and 8192 winners:
five MegaMoE graph nodes per rank, 80 total across both eight-rank cases, with
no separate staging or reduction node. Collection and detailed resource review
are still in progress. This timeline cannot distinguish internal combine and
dispatch phases. Full NCU collection has not run for this source.

### Complete fused-base accuracy and selected-profile audit

The f655 full numerical matrix passed all 60 cases in 7,193.58 s on hu-pdx-7:
GLM5, powers of two 1–16,384, random/skewed routing, EP4/EP8, four tactics,
O2/O3 and eager/graph execution. Counts: 960 tactic/compiler/execution outputs,
2,880 reference checks, 7,200 pair checks and 135,287,341,056 element comparisons;
zero mismatches and zero nonfinite values. Archive SHA256:
31bea98dcbc80d744e5ab988c157cfc0376c4e2913564cb4594172226b8ab12d.
Source and idle closure passed. The existing monitor started the authorized
six-batch scoped sanitizer suite at the same f655 source (PGID 31602). This is
not yet a sanitizer pass and does not qualify the later b215 staging trial.

Independent 7dc Nsight audit verifies all 80 graph executions, the measured
N64/epilogue and N128/dispatch winners, REG96 with STACK0/LOCAL0 and no SASS
local loads/stores for the selected kernels, and full outgoing bulk-copy waits.
See `input-stage-fusion-compile-warmup/profiling/SELECTED_NSYS_SUMMARY.md`.
This does not measure internal-phase timing. PR8 now reports the completed
accuracy matrix and Nsight findings while explicitly keeping sanitizers pending.
Readback body SHA256:
78e80889883d9747324df7eda71defe1ca24b8cdbf5e1bde7fc22f7d1b265022.

Canonical head 948e9a15858ed96bf8595e140de8e58c43449d86 updates only the README
source ledger after 8375077's docstring change; executable code remains 7dc.
No new performance result is attributed to these documentation commits.

The scheduler dependency review also tightens the b215 tradeoff: the original
scheduler cannot publish useful work until source staging and dispatch
publication finish, so the copy handoff does not displace useful dequantization
during staging. The actual new dependency is dispatch metadata waiting for TMEM
allocation. `FUSED_STAGE_METADATA_OVERLAP_REVIEW.md` traces this distinction and
records two future routing-preparation overlap variants without implementing them.

### Three-WG capture gate and large-copy coverage

b215 captured 128 fused ABI artifacts and 32 finite bit-exact output pairs.
Every fused artifact has the single intended barrier 2 with 544 participants,
128-bit vector copies (or eight 16-bit generic loads plus 128-bit stores), and
writer proxy fences before the rendezvous. Resource reports match 7dc: tactic 0
has STACK8 and seven local SASS operations; other tactics have STACK0 and none.
All use REG96 and the same role budgets. See
`input-stage-multiwg-retrieve/CODEGEN_PLACEMENT_REVIEW.md`.

The capture has only 16 local rows. The existing queued suite also uses only
capacity17 at H1024/1056; neither exercises actual copy work in both additional
WGs. Root therefore added the existing independent bit-exact numerical cases
GLM5/global1024/EP4/random+skewed to the pre-timing gate, retaining all four
tactics, O2/O3 and eager/graph checks. Their 256 local rows produce 196,608
16-byte chunks, exceeding all three first strips and exercising repeated loops.
No tolerance or production test change is made. Native and queued suites remain
separate. The native low-level reference cases exercise the true pre-staged
ABI; the queued helper's so-called raw thunk is explicitly a fused-zero-output
frontend call, so it must not be cited as a 416-participant runtime check.

A separate unqueued source prototype 772de58a64ffc504f90369d5bdc6e195cc0570cf
is preserved under `input-stage-prep-overlap/hashinfer`. It uses two decode WGs
for copying while dispatch stages routing and executes preparation, before the
same existing handoff. Only the owned post-preparation orchestration is mirrored;
the underlying transport primitives remain inherited. CPU structural/mapping
checks pass. Its extra argument forwarding requires a material measured benefit
before adoption; no GPU result or canonical change is claimed.

### Three-WG staging: correctness gates pass, performance rejected

`b215a7d22784fd7675452cb9df70d6e29dcf0722` passed native validation
(48 logical cases / 65 rank executions), the two large-copy GLM5 T1024 cases
(random/skewed, EP4, all four tactics, O2/O3, eager/graph), and queued validation
(96 case-rank records / 1,536 exact snapshots). The targeted cases compare more
than 2.11 billion elements with zero mismatch or nonfinite values and exercise
all three copy workgroups. No sanitizer pass is attributed to this candidate.

The full 1–8192 sweep and independent raw-evidence audit passed. The sealed
archive is `43bb3be7e0c223a0b8a947525d5a3a02dd6688c6d6a24661f15c44ead1d59c64`;
all 112 rank outputs match the controls exactly. Against retained `7dc9626`,
the 8–8192 geometric speedup is **0.995737687×**, with 5/11 rows faster and all
14 selected tactics unchanged. T16 rises from 135.0890 µs (MAD 1.4240) to
148.5615 µs (MAD 1.0715), a 9.973% latency regression. Its four 25-sample quarter
medians remain separated, so a single sample does not explain the regression.
Serial-arm temporal drift remains uncontrolled; no causal confidence interval
is claimed. Full medians, MADs, tactics and quarter trends are preserved in
`input-stage-multiwg-retrieve/independent-timing-audit.json` and the companion
table. Retain the simpler `7dc9626`; no b215 code is promoted to the canonical PR.

The reviewed full-metric Nsight Compute collection for retained 7dc starts with
T128 on hu-pdx-99 (supervisor/PGID 268770). T8192 is authorized only after the
T128 result and clean process/GPU closure pass. Profiling is separate from the
latency table; no new NCU result is claimed at launch. The second-node f655
sanitizer suite continues independently.

The first NCU owner stopped before launching a profiler/worker: its hard-coded
`/usr/local/cuda/bin/ncu` does not exist on this image. That zero-launch failure
is preserved as failed evidence. Fresh resolution verifies `/usr/local/bin/ncu`
at Nsight Compute 2026.1.1.0. The separately reviewed retry changes only this
path, the output namespace and dependent hashes; source, workload, metric flags
and lifecycle checks are unchanged. T128 retry supervisor/PGID is 269603, under
`c1-selected-ncu-pathfix/ncu-t128`. No new profile result is implied by launch.

After both selected-source NCU phases close cleanly, one fresh main68→7dc
paired benchmark is authorized for the PR's full-scope performance table.
`main-baseline-refresh/PLAN.md` and `prepared.json` bind the sources and exact
workload. Root reviewed the driver diff: only primary-node proof/host/boot,
names, docstring and port change; all six runtime helpers are reused unchanged.
The existing 1–8192, 100-sample method and bit-exact output comparison remain.
This is a baseline refresh on qualified source, not another retention trial.
Execution and independent evidence audit remain pending.

### Profiling devbox lost; sealed performance evidence retained

The task-owned `hashinfer-ownership-0918` devbox disappeared during the path-fixed
T128 NCU attempt. Managed HAI inventory shows no matching devbox in c2/ziangli or
the all-namespace listing, and diagnosis reports no pods. The infra qualification
devbox remains present. No delete/release was issued by this task. Last successful
NCU polling recorded one completed replay per rank and another active; the profile
is **incomplete and uncollected**, with no terminal pass or clean-closure claim.

All completed b215, 7dc and earlier performance evidence and Nsight Systems
reports were already collected locally. The b215 retention decision is unchanged.
A replacement using the live-checked explicit CUDA 13.2 image is authorized,
starting with c2/ziangli, `--bare`, no size override. See `NGC_CUDA132_REFRESH.md`.
The hu-pdx-99-bound profiling and main-baseline-refresh owners must not be replayed
against a replacement without a fresh environment proof and explicit node/boot
rebinding. The eventual main68→7dc comparison must run both arms on that node.

### Fused-base sanitizer qualification completed

All six f655 batches passed: memcheck, synccheck and racecheck, each at EP4 and
EP8, O3, 1/128/1024 tokens, random/skewed routing and all four deterministic
tactics with eager and graph execution. Collection verifies 36 clean rank
reports, 216 workload/rank cases and 864 tactic/workload/rank cases, with no
reported hazards. Runtime was 5,152.55 seconds. Archive SHA256:
`30c9b07d2ac7f8ba7aca348e9c2caafa95ed55ee9dfcc23eaefbec4ae10557f7`.
Root verified that local archive hash and read the verifier, monitor-complete
and clean-closure receipts. All 104 source files are intact; the owned process
group is gone and all GPUs were idle at closure.

Scope remains the owned MegaMoE kernel. Memcheck uses the existing
`--check-tensor-ops no` workaround for Compute Sanitizer 2026.3 two-CTA
peer-barrier false positives; compiler TMEM guards remain enabled. Racecheck
does not establish arbitrary global/NVSHMEM/TMEM ordering. Source qualification
is f655; the separately documented 7dc host preparation and device-equivalence
checks still apply. This does not qualify b215 or the unmeasured 772 prototype.

The completed qualification frees hu-pdx-7 for a bounded 772 prototype gate:
generated-code/resource inspection, the two existing strict large-copy cases,
and queued replay/lifetime tests. That work is isolated under
`input-stage-prep-overlap` and does not modify the canonical PR or delay its
fresh main68→7dc performance-table publication.

### Fresh full-scope performance table published

The replacement hu-pdx-9 completed a fresh serial main68→7dc pair on one node
and boot. Independent audit passed all 2,800 timing samples, 112 finite
bit-exact rank/token output pairs, source bindings and process/GPU closure.
The full 1–8192 table is in
`main-baseline-refresh-replacement/PR_BODY.fresh-pair.md`; raw results and the
audit remain alongside it. Geometric speedup over 8–8192 is 1.028476×, with
7/11 rows faster. T8 and T2048 regress, T4096 is effectively tied, and T8192
is slower with substantial spread. This serial pair does not cancel temporal
drift; the mixed result is disclosed without filtering any samples.

PR #8 now contains that complete main-before/PR-after table and the completed
six-batch sanitizer scope. Exact GitHub body readback passed, with head
948e9a15858ed96bf8595e140de8e58c43449d86 and draft status unchanged. Body SHA256:
`acf0ceceb5e9dbb3d3645a4e9783b9f9393df7633735e5ebccb1bd9e79702108`.
The publication receipt confirms restoration of the `zianglih` CLI identity.
No new code or unvalidated prototype was promoted by this publication.

### Next fusion overlap and lifetime trials

772 routing-preparation overlap passed its bounded generated-code, numerical
and queued-replay gates on hu-pdx-7. This includes 128 fused ABI artifacts,
32 exact control outputs, two strict GLM5 T1024 cases with 2,113,929,216 finite
BF16 comparisons, and 1,536 queued plus 288 eager comparisons. The final source,
process-group and GPU closure passed. No full accuracy matrix or sanitizer
qualification is attributed to this candidate.

A fresh serial retained7dc→772 full 1–8192 performance pair is now running on
that node. It compares the full composite candidate, including the earlier
multi-WG copy changes; it does not isolate routing preparation alone. The
existing six runtime helpers and timing method are reused unchanged. The
primary node independently runs the retained source's full-set NCU collection.

An isolated reduction-lifetime prototype is committed at `34c9a3a` under
`retired-reduce-tile16/hashinfer`. It doubles hidden elements per worker to 16,
using existing 128-bit copies, ordered arithmetic and register budgets. Larger
accumulators become live only after the FC2 readiness handoff. The output
alignment contract remains 16 bytes, and the redundant inner token guard is
removed because the sole caller already bounds every worker. Source checks and
scoped pre-commit pass; generated resources, GPU numerics and timing are pending.
This candidate is separate from 772 and has not been promoted or pushed.

The more direct tail-overlap prototype `c2b93f5` is in
`local-reduce-ready/hashinfer`. It relays CTA 0's existing all-rank completion
acquire to a stable rank-local flag before the dispatch grid broadcast. Live
retired workers acquire that flag instead of waiting for the second whole-CTA
handoff, allowing reduction to overlap the broadcast and unchanged cleanup.
The first CTA barrier, every transport barrier, arithmetic, register budgets
and protected files remain unchanged. One flag is appended outside tail-zero
regions and reset only in the next local dispatch prologue, before publication
and scheduler release. Direct polling of cycling NVLink signal slots was
rejected because a faster peer can advance those slots before a delayed local
consumer observes the old target. Source hooks and syntax checks pass; the
documented ordering/lifetime argument is awaiting independent review and all
GPU validation remains pending. This is not part of the canonical PR.

### Retained-source full NCU128 collected and interpreted

The fresh B1 N64/epilogue-return profile completed 40 application-replay epochs
per rank (320 records), eight device reports and 8,212 verified archive paths.
The compact collection and full details/SASS exports are under
`main-baseline-refresh-replacement/profiling/collected-b1-selected-ncu-t128`.
Integrity audit `2a730744` and interpretation receipt `0bcaeade` pass. All 28
nonempty section labels and unavailable metrics are recorded, not filtered.

Selected CUBIN resources remain REG96/STACK0/LOCAL0, with no static or reported
dynamic spills. Sampling identifies dispatch preparation/publication and
scheduler mbarrier instruction regions, supporting further source inspection
without establishing a causal bottleneck. Replay durations are 17.6–202.2 ms
versus approximately 196 us in normal CUPTI timing, and some reported occupancy
ratios exceed 100%. Those ratios and profiler durations cannot justify tuning
or replace the performance sweep. Internal tail arrival times are unavailable.
The full 8192-token profile continues independently on the primary node.

### Preparation overlap rejected after full audit; local-readiness trial advances

The fresh hu-pdx-7 7dc→772 pair is independently audited: all 2,800 timing
samples, 112 finite bit-exact output pairs and source/node/closure bindings
pass. Receipt `130e549b0758359e9cc858c9537b54f6f17837e0c8b9aac47bfecafe53d3f2e8`
and the complete table are in `input-stage-prep-overlap/performance`.
The 8–8192 geometric speedup is 0.999078× with 4/11 rows faster and all 14
tactics unchanged. T16/T32 regress approximately 1.7–1.8%; T1024–4096 improve
1.3–2.2%. Both T8192 arms drift substantially within their sample windows.
The aggregate result does not justify the additional orchestration: retain
7dc and preserve the 772 experiment without promotion or PR-body changes.

Local-ready c2b passed its independent generated-code gate (`e055c898`): all
32 finite exact control outputs and 128 artifacts across 16 tactic/ABI groups.
Each group has one 640-thread barrier 8, unchanged 16 transport barrier-10
sites, the same-lane system-acquire→GPU-release sequence before dispatch
broadcast, and live-worker GPU acquire before combine loads. All groups have
REG96/STACK0/LOCAL0; tactic 0 removes 7dc's STACK8/seven local-memory sites.
One group has two PTX text variants but identical binaries across its ranks.
Strict GLM5 T1024 random/skewed validation is running; queued replay and the
full AFTER sweep follow if their gates pass. This is bounded qualification,
not a full accuracy/sanitizer pass or permission to promote.

A source-only follow-up is committed at `d4b828851064a57a70bb21f11a6405564e1f6fc1`
under `async-retirement/hashinfer`, parent c2b. The first rendezvous retains all
640 arrivals but only dispatch waits: retired compute roles arrive
nonblocking and can prepare metadata immediately. Explicit unaligned barrier
forms avoid promising convergence across different role paths. The reset
proof now depends on the unchanged dispatch-publication/scheduler-record
handoffs, which needs independent review. Scoped pre-commit, syntax and diff
checks pass. No GPU execution is queued or claimed for this follow-up.

The asynchronous-retirement d4 source review now passes (`b8fa7884`). Every
reducer role has a prior dispatch-publication carrier: scheduler warp 7 waits
directly at the handoff, while the other roles consume its work/terminal
records. The reviewed unaligned 512-arrive/128-wait protocol preserves
dispatch's all-producer retirement dependency. GPU qualification is pending.

The previously unrun 24b794f warp-striping idea is now ported to retained 7dc
as `58dd078b763dabe3fffa7db64490f94d8a89d8fa` in
`warp-striped-current/hashinfer`; the old worktree remains untouched. It changes
only three mapping constants, 128→32, and their comment. Whole-module AST
equivalence outside those constants, full first-stride bijections for four
CTA counts, 120 shape/count cases, warp coalescing and alignment checks pass.
At one H7168 row per rank, active reducer CTAs increase from 7 to 28 without
changing the resident grid. Current decode-first roles, early preparation,
arithmetic, barriers and register budgets remain unchanged. This trial is
independent of c2b/d4. Independent source review and all GPU evidence are
pending; primary-node preparation may proceed locally while its NCU8192
collection finishes. No new source is promoted to PR #8.

### Readiness qualification and compiler-ordering follow-up

c2b bounded qualification is complete (`20bccd62`,
`local-reduce-ready/qualification/BOUNDED_VALIDATION.json`): 32 exact captured
outputs/128 ABI artifacts, 2,113,929,216 finite bit-exact element comparisons
over strict T1024 cases, and 1,536 queued plus 288 eager output checks. Source,
owned-process and GPU closure pass. Its full C1 1–8192 AUTO4/CUPTI sweep is
running against the fresh retained7dc A1 from the same hu-pdx-7 boot. The six
runtime helpers and all 100 samples per row are unchanged. CPU-only collector
review was allowed to overlap execution; it did not change timing code or
launch guards. Full qualification remains conditional on retention.

Before running d4, root identified that its inline synchronization assembly
must expose memory effects to the compiler. Successor
`0190cce2ebf085f75d985c01f347a07617ba518e` changes only the constraint string to
`~{memory}`; it adds no hardware fence or barrier. Scoped hooks pass and
independent successor review `a59fbff5` explicitly supersedes the d4 execution
approval. The old d4 source/archive/helpers remain preserved and unrun.
The successor's 104-file freeze is in `async-retirement/frozen-source-v2`.

58dd's source and helper reviews pass (`5d00d7b1`, `c141d2d2`). All four
captures completed on hu-pdx-9 after its NCU GPU phase ended; the capture
archive is local, while generated-code/output review and strict/queued gates
remain pending. NCU8192 completed all 40 replay epochs per rank, 320 records
and eight reports. CPU export/transfer is separate from qualification, with
explicit report hashes and GPU-phase closure; terminal collection audit is
still pending and no 8192 bottleneck conclusion is claimed.

Further read-only analysis is in `COUNTER_BANK_LIFETIME_PROPOSAL.md`,
`COUNTER_BANK_LIFETIME_INDEPENDENT_REVIEW.md`, and
`local-reduce-ready/NEXT_OVERLAP_INDEPENDENT.md`. Two receive-counter banks
could remove the cleanup publication barrier, provided all aliases (including
the scheduler's expert-token sizes) share the device-selected generation and
reuse proof. No implementation exists. The analysis also distinguishes early
reduction from shorter kernel completion: existing reduction already overlaps
cleanup, so profiling-only phase timestamps would help identify which side
actually limits completion before adding a broader transport protocol.

## Receive-counter banking prototype (unrun)

Prepared isolated commit `b6fd43a026c4fb791e53e37da2cc1d4bc43a26aa` on retained7dc: two receive-counter banks and one device generation bit remove cleanup zero-publication NVLink barrier. Both original full-CTA tail barriers and FC2 drain retained. All four aliases, including scheduler sizes and cleanup prefix, select the same bank. No protected drop edits. Scoped pre-commit, actual-layout checks (30) and abstract 2/3/4-rank five-launch interleavings pass; no GPU or performance claim. See `receive-counter-banks/README.md`. Independent source review and bounded GPU qualification pending. Canonical PR8 unchanged.

## Current overlap sweeps: retained 7dc remains selected

The sealed full sweeps do not establish a useful gain. All use powers of two
1–8192, unchanged four-tactic AUTO/O3 and 100 cold-L2 CUPTI samples per row.
The retention aggregate excludes only 1/2/4; those rows remain in each full table.
Controls are earlier runs on the same physical node and boot, not contemporaneous
or drift-cancelled measurements. Final archive audits are noted separately.

| Candidate | Matched control | 8–8192 geometric speedup | Decision |
| --- | --- | ---: | --- |
| 772 input/prep overlap | hu7 retained7dc A1 | 0.999078× | Reject; independent audit passed |
| c2b local-ready overlap | hu7 retained7dc A1 | 1.001292× | No standalone promotion; independent audit passed |
| 58dd warp32 striping | hu9 retained7dc B1 | 1.000708× | Reject mixed/marginal result; independent audit passed |
| 0190 asynchronous retirement | hu7 retained7dc A1 | 0.992183× | Reject; independent audit passed |
| 0190 asynchronous retirement | hu7 c2b C1 | 0.990903× | No benefit over local-ready alone |

Full tables and immutable evidence stay in each candidate's `after-benchmark`
(or `after-benchmark-v2`) folder. 58dd notably regresses64 tokens despite improving
some larger rows; 0190 loses most retained rows with the same selected tactics.
No prototype is cherry-picked into canonical PR8 and its published table is
unchanged. b6fd receive-counter banking is now undergoing bounded GPU validation
on hu9. A profiling-only per-role timestamp diagnostic against7dc is being
prepared for hu7 to measure tail critical-path opportunities directly.

### Counter-bank validation and diagnostic scope

b6fd capture and all 128 generated ABI variants pass independent review
(`9424024e`). Both original 640-thread handoffs and the full outgoing-transfer
wait remain. The cleanup publication removal reduces static dispatch barrier
sites from 16 to 12; captured variants have REG96/STACK0/LOCAL0, including the
previously spilling tactic. Strict T1024 random/skewed EP4 validation passes
(`b7a837e7`): 32 tactic/optimization/graph combinations and all 96 reference,
240 pairwise checks. Queued replay and native pre-staged/IKR tests are pending.
One full D1 sweep against the earlier same-hu9 retained B1 is authorized after
those gates. This is not full numerical/sanitizer qualification or promotion.

The isolated `tail-phase-diagnostic` source instruments warp-leader timestamps
at work-loop/role boundaries, producer tail, both full-CTA handoffs, drain,
reduction and cleanup. These are issue observations, not new completion fences.
Fresh hu7 control and instrumented timing will quantify perturbation at fixed
128/8192 tactics; hu9 B1 supplies only tactic provenance. Cross-GPU clocks will
not be subtracted. No diagnostic source is intended for the PR.

### Next startup-overlap candidate

Revisited the preserved, unrun input-stage-prologue-overlap worktree. Its actual
HEAD is `e37cf879a7a4a687ae706be5608238fbe3d695b1`, based on retained7dc.
The unchanged dispatch staging call and register decrease move between common
cluster-init arrival and wait. Root reran its complete-module AST relocation
proof and diff check; independent review/local qualification-helper preparation
are pending. This owns only the W4A16 file and adds no synchronization or
public knob. No GPU run or performance benefit is claimed.

### Counter-bank tail reuse follow-up

b6 bounded gates now pass: generated/output `9424024e`, strict `b7a837e7`,
queued `5f9185a7`, and native pre-staged/optional-reduction `64034962`. The
full D1 1–8192 sweep is active on hu9 against retained B1.

Prepared isolated stacked source `0d8f7d625df2ea8a7c6c258be8fa94b43f63e522`
in `banked-dispatch-reduce/hashinfer`. After b6 removes cleanup publication,
dispatch can finish its local clears and join reduction as the fifth WG.
The existing four WGs still start reduction immediately and overlap cleanup.
Decode-first assignment is preserved, with dispatch appended as the final
strip and grid stride changed512→640. Ordered math and both full-CTA handoffs
are unchanged. Scoped hooks, exact AST transformation and45 worker-coverage
cases pass. Independent review/GPU qualification pending; no performance
claim or promotion. This is different from historical f5f, which delayed all
five groups' reduction until complete cleanup.

### Receive-counter bank full sweep sealed

D1 completed on the same hu9 boot: 1.02905388× geometric speedup over the
earlier retained B1 across8–8192,9/11 rows faster. T64 is0.32% slower and
T8192 is0.84% slower; the serial control does not cancel temporal drift. The
full14-row table is in `receive-counter-banks/after-benchmark/SEALED_RESULTS_PENDING_AUDIT.md`.
Archive8776715d is sealed; independent final archive audit is pending. This
is promising enough to continue qualification and compare the fifth-WG follow-up,
not sufficient for promotion or a new PR final-performance table.

0d source/lifetime review3836feeb and helper review4f284cc4 pass. Its bounded
capture is active on hu9; strict/queued checks follow if output and generated
placement/resources pass. One full E1 sweep is authorized after all bounded
gates, with all archive transfers finished before timing. Compare E1 against
both retained B1 and fresh b6 D1; no new b6 timing is required for the trial.

The b6 terminal timing audit now passes (`6deb6e3b`): all2800 paired samples,
112 finite exact output buffers,208 source files, same host/boot/environment
and clean process/GPU closure. All14 rows selected identical tactics. Full
median/MAD/quarter table is `receive-counter-banks/after-benchmark/independent-timing-audit.md`.
8192 has MAD25.168→23.632µs and upward Q1→Q4 drift in both arms; this limits
causal attribution of its0.84% difference. A fresh confirmation is required
before promoting a final candidate. No PR table changed.

## User methodology update: decode priority and16k prefill

Future performance runs now use1,2,4,8,16,32,64,128,256,512,4096,8192,16384.
Primary retention is decode4–512;1/2 remain in tables only, while4 now counts.
Prefill4k/8k/16k should not visibly regress; very slight regression is acceptable
for clear decode gains.1024/2048 leave performance sweeps, not the accuracy
tests. Benchmark first and qualify beneficial candidates afterward. Detailed
current rules are in `BENCHMARK_METHODOLOGY.md`; no old evidence is relabelled.

Under the new decode subset, the audited historical b6 result is1.034581875×,
7/8 decode rows faster;4096 is1.003535×,8192 is0.991634×,16384 unmeasured.
Minimal same-node16k controls will fill the missing row before new13-shape
trials. Primary also needs a b6 parent16k row to compare0d against both b6
and retained7dc. Remaining unstarted strict/queued gates for0d and e37 are
skipped before timing; the already-running captures/resource checks finish.
PR bodies keep only final before/after tables, never incremental trial history.

### New13 timing launch and diagnostic interpretation

Both runtime adaptations are independently reviewed and active under exclusive
node owners. Primary runs retained7dc B16, banked b6 D16, then stacked0d E1;
secondary runs retained7dc A16 then early-staging e37 E1. The timing worker and
CUPTI helper remain byte-identical. Single16k controls supplement explicitly
labelled historical rows; they do not turn the trial into a contemporaneous pair.
No additional strict/queued/full suite is run before the performance decision.

The retained diagnostic interpretation is complete at
`tail-phase-diagnostic/retry-api-cleanup/DIAGNOSTIC_INTERPRETATION.md`
(independent review eff72a1d). At128, cleanup leader issue observations end
about6.2us after reduction; at8192, reduction ends about18.5us after cleanup.
This supports the two trial directions but is not a production speedup or an
all-lane completion measurement. Instrumented latency changes are mixed.

Root also inspected the retained reducer lowering: six of eight vector loads
are already hoisted ahead of the first packed multiply in the representative
8192 SASS. No manual-prefetch or double-buffering source change is proposed
from source appearance alone. No production source or PR body has changed.

The primary16k supplements passed: retained7dc B16 median1530.5395us
(MAD47.5685), banked b6 D16 median1510.1725us (MAD25.2165),
ratio1.01348654x. Both selected N128/dispatch. Both distributions drift
upwards within the100 samples; the first samples72.187884ms and45.672302ms
are retained. These are provisional owner-reported control results until
the complete E1 archive/comparator audit. No samples were trimmed.

Secondary retained7dc A16 median1541.376us/MAD70.3045 has similar
within-arm drift, and its first36.7ms sample is retained. This supplements
only the hu7 baseline; node controls are never mixed. Both full13 E1
sweeps continue. Source/PR promotion remains pending.

### Completed new13 trial decisions and capacity-guard successor

e37 terminal checks passed all104 finite exact outputs, but decode4–512
geometric speedup is0.992427x (3/8 wins). Do not retain it or spend additional
qualification on it. The complete table is in its decode13-benchmark folder.

0d terminal checks passed104 exact outputs against each retained/banked control
(208 comparisons). It gives1.036127x decode versus retained7dc, but only
1.001494x versus b6;256/512 regress about1.9% versus b6. Prefill versus b6
is1.021579x/1.013145x/1.000140x at4k/8k/16k. Full sealed archives remain
remote and local transfer/audit are pending; these are provisional trial
decisions, not published final evidence.

Prepared isolated f25d564 capacity-gated-dispatch-reduce: prove at compile
time whether the fifth strip can have any work from workspace capacity and
launched CTA count. False specialization restores complete b6 AST; true
restores complete0d AST.132 ownership cases and scoped hooks pass. No public
knob, runtime shape threshold, new synchronization or duplicated reduction.
Benchmark-first G1 is next, without separate strict/capture/full pretests.

Large raw-tensor archive transfers may pause only at fully verified chunk
boundaries, preserving all bytes and immutable remote seals. Timing starts
only after transfer processes close; downloads resume after timing or during
later numerical validation. Final promotion/publication still requires the
complete evidence audit. A fresh main68 thirteen-shape control is being
prepared on hu7 for the final PR-only before/after table.

### Guarded sweep result and previous-bank reclamation trial

f25 G1 terminal checks pass104 exact outputs against each composite control.
Decode versus b6 is0.98977250x,3/8 rows faster;T256 is207.346us versus
190.817us, with identical N64/epilogue tactics and low within-arm MAD.
Prefill4k/8k/16k is1.00130x/1.03679x/1.01558x versus b6, with drift limits.
Do not promote the guard on these results. Existing caches contain no usable
MegaMoE PTX/CUBIN, so source AST equivalence does not prove binary identity
or explain the measured decode difference. Full archive audit is pending.

Prepared1d56c67 early-inactive-counter-clear on b6, independently of the
fifth-group variants. Normal launches select the previous bank only for
zeroing and clear it immediately after dispatch_body returns, before the
existing retirement/drain. Input publication retires previous readers;
drain publishes clears before next writers. Local clears/reduction/all
barriers stay unchanged. Two owned files,31+/13-; hooks, exact reversal,
30 actual layouts and bounded rank-interleaving checks pass. Benchmark-first
H1 follows source/runtime review. No new full suites before measured gain.

NCU1 retains the parent active-tail path in this trial. Independent review
identified a separate inherited b6 kernel-replay limitation: restored local
bank state can allow reuse before another rank clears its active bank. If
banking is retained, repair the profiler-only publication in a separate
commit: reduce padding2→1 and publish after active clear, keeping four
signal calls and leaving the normal mode unchanged. Preservation is not a
claim of validated replay safety.

Fresh hu7 main68 A1 full13 passed104 finite repeat outputs/1300 samples and
is sealed e3c7961d (342029053bytes), with transfer deliberately unstarted.
Fresh retained7dc R1 full13 is now running on the same node for a current
retention control as well as the PR-start baseline. No raw downloads occur
during timing. Final candidate selection, full qualification and PR update
remain pending; canonical PR8 is unchanged.

### Profiler publication repair and fresh controls

Prepared separate profiler-only commit `ccb0c6a` on `1d56c67`: move one
NCU padding barrier to after active-bank clearing. The existing helper
publishes every clear before a replay can reuse a restored bank selector;
four NVLink calls/eight grid phases remain. Production-mode full AST is
unchanged. Scoped hooks and independent source review pass. The bounded
model finds the inherited reuse counterexample and checks the new abstract
order for two to four ranks over five invocations. Actual Nsight replay is
not yet validated. Artifacts: `profiler-counter-publication/`.

Fresh hu7 main68 A1 versus retained7dc R1 passes104 exact outputs and all13
tactics match. Decode4–512 is1.050204x; prefill4k/8k/16k is
1.008233x/0.998635x/0.965416x. Both16k arms rise materially across their
sample quarters. No clocks/power/temperature series were recorded, so the
cause is unknown and the measured16k slowdown remains visible. These are
controls, not a newly selected optimization or a final PR table.

H1 early-clear full13 timing launched on hu9. A fresh b6 banking control is
being prepared on hu7 against its new R1 control while H1 runs. Archive
downloads remain paused during timing. Canonical PR8 and its body remain
unchanged pending candidate selection and qualification.

H1 completed all13 rows and104 exact outputs against each control. Parentb6/H1
decode GM is1.023010667x (6/8 wins), with4k/8k/16k ratios
1.01137285x/1.02455019x/0.99738958x. Retained7dc/H1 decode is1.058388294x
(8/8). This meets the revised preliminary retention criteria; full qualification
and fresh same-node confirmation are warranted. No slowdown row is excluded.

Assembled `selected-counter-lifetime/hashinfer` candidate3de81245 on canonical948
with three separate commits. Freeze104 archivea7910c49/manifested248236 and
independent snapshot review9ccad325 pass. The canonical checkout/PR remain
unchanged. Strict60 is being staged on hu9; hu7 will benchmark this exact head
after its freshb6 control, then run the unchanged six sanitizer batches.

H1's complete independent timing audit passedf240e2e0. Fresh selected3de B1
also passed104 exact outputs against mainA1, retainedR1 and bankingB6. Decode
speedups are1.092655x/1.040422x/0.994245x respectively. Early clearing's
incremental decode gain did not reproduce on hu7; the combined candidate still
improves all eight retained decode rows. Against retainedR1,4k/8k/16k improve
1.013014x/1.004770x/1.006646x. Against mainA1,16k remains0.971832x with
substantial within-arm drift. Do not describe the incremental2.3% result as
uniform or confirmed across nodes.

Request one reverse-order full13 selectedB2→mainA2 confirmation to assess
that main16k guard. The final aggregate was specified before this repeat:
median all200 samples per source/row, with raw series and per-run summaries
retained. Transfers pause at verified chunks during these additional timings;
mode1 ordinary queued96 and sanitizer follow. Strict60 continues on hu9.
This does not change routine single-sweep retention or the accuracy matrix.

### Retention decision after decode confirmation

The user favors retaining selected3de for useful decode improvements and
explicitly accepts documenting the16k slowdown for future work. The existing
reverseB2→A2 comparison continues with the predetermined pooled200 estimator;
no further confirmation sweeps are planned solely to close16k. Full strict60,
mode1 ordinary queued96 and scoped san6 remain the final qualification. No
claim of actual Nsight kernel-replay validation is made. PR8 and its canonical
checkout remain unchanged until those results are collected and reviewed.

A separate source-only experiment is being prepared for moving dead local
counter clearing into the existing all-rank drain window. It must preserve
both640-thread rendezvous, return waits, generation lifetime and profiler-mode
behavior, and will be evaluated independently on the13-shape methodology.

Prepared separate benchmark-only commit534a623 on selected3de in
`benchmark-methodology/hashinfer`: default/example13 shapes, decode4–512
retention wording and neutral finalization wording. Scoped pre-commit passes;
full executable AST excluding TOKEN_COUNTS is unchanged. Current GPU jobs use
explicit13 shapes and frozen3de, so their source is not changed by this commit.
Canonical promotion can fast-forward to this descendant after qualification.

### Final confirmation and next concurrency direction

The predetermined A1+A2 versus B1+B2 pooled200 comparison passes all source,
method, fixture, finite output and cross-arm checks. Decode4–512 geometric
speedup is1.088895x,8/8 faster;4k/8k/16k ratios are
1.007325x/1.000918x/0.973730x.16k latency is2.70% higher and remains in the
single final table. Full raw archives are transferring during correctness;
independent archive audits are pending. No additional timing repeat is planned.

The user accepts retaining this optimization and directs subsequent work toward
instruction efficiency, generated-code/PTX inspection, wider vectorization,
ILP and concurrency across the owned staging-through-combine lifetime. Keep
one CTA occupying each SM, two weight-dequant WGs and five total WGs. Reduced
resident staging/combine parallelism is a plausible cause of prefill loss,
not an established causal finding. Preserve ordered FP32 numerical recurrence.

Source-only local-clear candidatecfaa51e is prepared and independently read;
no timing gain is claimed. A separate source-only staging vectorization/ILP
candidate is being developed on3de, avoiding combination withcfaa so each
performance decision remains attributable.

Following the user's explicit retention decision, fast-forwarded the clean
canonical local PR branch from948e9a1 to534a623 (selected3de plus benchmark-only
default/docs). GPU jobs remain pinned to immutable3de and its104-file manifest;
no source or worker was restaged. Remote PR8 is unchanged pending publication.
A1/B1 full local archive audits pass; B2/A2 transfer/audits remain pending.
Mode1 ordinary queued qualification passes96 records/1536 replay checks and
288 same-partial eager output checks; no actual Nsight kernel-replay claim.
Full strict60 and san6 are still running and must not be described as passed.

All four final performance archives now pass independent CPU audit. Local pooled
recomputation is byte-equivalent to the remote report (3fadd45f); final audit
receipt is reverse13-confirmation/final-pooled-audit.json. Decode GM remains
1.088895x and16k remains2.70% slower. Primary accuracy access was lost after
28/60 clean cases; recovery is being investigated and no full pass is claimed.
Sanitizer EP4 memcheck passed; the remaining five batches continue on hu7.

Published accepted534a623 to draftPR8 with the one final pooled table. The body
explicitly records incomplete accuracy60/san6 and passed queued96 scope.
No new ILP/local-clear/donation experiment is part of this published head.

### Replacement node and benchmark-first continuation

The primary hu9 devbox disappeared after28/60 clean accuracy cases. Its loss
record preserves the incomplete result; no terminal or source-closure claim
is made. The replacement hu15 is a new boot with8 B300s and the same explicit
26.05-py3 CUDA13.2 image, selected after a live catalog check. Fresh setup and
source proofs are required; old-node benchmark timings are not a control for
this new node.

Follow the user benchmark-first policy: exact selected3de A1 then a0fe59b
staging ILP B1, each full13, followed by source closure and generated-code
inspection. Full strict60 qualification resumes on the retained head after
the performance decision. No timing is added to the independent hu7 sanitizer
node. Old strict-gated wrapper drafts are preserved unexecuted; fresh setup
and idle proof replace the impossible old terminal prerequisite in a separate
successor package.

Instruction study: the existing staging loop has a single LDG128/STG128 pair
per iteration. The reducer already hoists seven route vector loads ahead of
its first packed multiply. The next staging trial exposes two independent
loads while retaining16B alignment and thread ownership. The independent
register-donation experiment retains dispatch96 during staging, then donates
to64 before transport; one CTA per SM and the61440-register pool remain fixed.
Neither source intention establishes faster emitted code or end-to-end gain.

Hu7 was also lost after two reported clean memcheck batches. Their full
per-rank artifacts/JUnit were not collected, so they are not final auditable
qualification. Replacementhu59 is set up independently; all6 sanitizer batches
will rerun on the selected head, with small completed-batch evidence checkpointed
locally during the suite. The public draft body now states this boundary.
Freshhu15 selected3de A1 launched with exactsource104 and reviewed immutable
13shape runtime; a0 B1 follows automatically after closure, then T16384 codegen.

### Staging ILP2 compiler diagnosis

Fresh selected3de control on hu15 completed all13 shapes,104 finite repeat-equal
rank outputs and1300 rank-MAX timing samples. Its sealed archive is
0ad7051dcf84d4ef31b4496faefce6957f3e82ae599f2545f8d73647725a097a.
The a0fe59b ILP2 arm exited before any timing rows. A separate unchanged-source
T1 diagnostic persisted the compiler exception before distributed teardown:
`cute.copy` expected16 copy bits but received128 for the added predicated copy.
All eight rank traces agree. This is an implementation/lowering failure, not a
performance result or evidence against staging ILP. Evidence is preserved in
input-stage-unroll2-ilp/diagnostic-compile/; the failed frozen source is retained.

A separate successor uses a full-pair loop with two unconditional128-bit loads
before stores, then one guarded128-bit tail. This avoids the rejected predicate
lowering without changing alignment, thread ownership, fences or CTA geometry.
The fresh same-node3de control remains valid for that successor while the boot,
environment and benchmark method remain unchanged. Full retained3de sanitizer
qualification runs independently on hu59, with each completed batch checkpointed
locally; it does not qualify this unmeasured staging change.

Fixed successor7dc3c63 (only vector staging loop versus3de) passed source/freeze
review and launched full13 C1 on the same hu15 boot, preserving faileda0 B1.
FirstT1 row completed after successful compilation; no partial retention claim.
A1 full local independent audit passes588f91a1, all104 outputs and1300 samples.
This is the valid current before-control, not older-node PR-start timings.

Retained3de sanitizer recovery first batch memcheckEP4 passes with four zero-error
rank logs now locally saved (archiveceaa8c33). Root verified archive/member hashes
and summaries. Full suite remains incomplete; checkpoint is in
sanitizer-recovery-20260919/batch-checkpoints/1-1789803000/.

### Predicate-free ILP2 full13 result (7dc3c63)

Remote terminal and comparison pass all104 finite exact cross-arm outputs and
all13 rows retain the same selected tactics. Decode4–512 GM is1.000796631x,
only3/8 rows faster; T8 is0.969837693x, T2561.048997767x. Prefill ratios are
1.007102496x/0.997039405x/1.020309192x at4k/8k/16k.16k median changes
1497.769→1467.956us, but within-arm MADs69.216/54.5885us limit attribution.
Do not promote this mixed standalone result. Full table is
input-stage-pair-tail/decode13-benchmark/terminal-summary-table.csv.
Candidate archive1a4cfa8992dc6d693b6b265f0eaec44a84e8a2dc9497f2bf92e87308b7e3f550
is sealed; local collection/audit and actual16k-winner codegen are underway.

Next independent trial is full256 staging on exact3de. Joint source/destination
alignment proof permits one256-bit load and store in the bulk loop; original
first-stripe workers are preserved, and generic/16B fallback remains. This
addresses instruction count and avoids the load-only prototype's split-store
sector penalty. Two owned source files only, no occupancy/register/barrier or
numerical changes. Source preparation is not a performance claim.

Full C1 selected16k capture now independently passes all32 compiled ABI resource
checks (REG96/STACK0/LOCAL0/no LDL or STL). Eight selected int32-vector rank
records pass eager repeat and two graph replays, with full raw outputs saved.
Other three ABI families are compile/resource coverage only. Two independent
LDG128 before two STG128 survived compilation. C1 still is not promoted.
Collector preparation retained a stale pin: the actual read-only collector
added a tar-member-set assertion; reversing exactly that assertion/line split
restores the prepared hash. Capture/helper/driver/source pins are unchanged;
the audit records this discrepancy explicitly.

The full256 D1 attempt b45 compiled and autotuned all four tactics, and T1
eager outputs were finite and repeat-equal. It then failed before timing because
backend.validate_capture_ready still expected four input variants, now six.
This is a host graph-readiness integration omission, not a256 lowering failure.
All failure records/source/group/GPU closure are preserved. Isolated successor
0103fe1573104ac9477f11618e3310864431f6ff changes only that count4→6 plus a
short family comment. Scoped hooks and16 actual-method readiness cases pass;
kernel/frontend bytes remain exactb45. Full13 E1 uses the same existing A1.

### Full256 staging result and existing-contract compute follow-up

0103/E1 completed full13 against the same hu15 A1 with all104 output pairs
exact and all13 tactics unchanged. Decode4–512 geometric speedup is0.987328645x
(1.28% latency regression), with only2/8 wins. T256 changes190.466→202.321us
(MAD0.8475→1.2005us). Prefill4k/8k/16k ratios are1.017893978x/1.001095391x/
1.010866466x; the16k difference is below each arm's MAD. Full rows and MADs are
in input-stage-bulk-copy256-capture/decode13-benchmark/terminal-summary-table.csv.
The sealed candidate archive isf7b2fedfdabd534ef26952f1b8d3ba0a941f1147769aff941a1b1d3d4c472020.
Local full archive audit and selected-winner codegen are pending. Do not promote:
this result does not justify decode regression and additional alignment families.
Preserve the implementation/evidence for later reference as requested.

The next memory-side trial is9f06ff6 paired128 plus delayed dispatch register
donation, under the existing16-byte contract. It compares with both3de/A1 and
7dc/C1 to distinguish net benefit from the donation's isolated effect.

An independent compute-side candidate ccfa0942 on exact3de changes only8+/1
lines in owned topk_reduce.py. Generated C1 code expands each packed BF16 pair
with three integer instructions; natural Uint32 recast plus shift/mask targets
two, preserving operand bits and unchanged FP32x2 multiply/FMA recurrence.
All65536 BF16 encodings, including signedzero/subnormals/NaN payloads, match the
CPU conversion oracle; this is not GPU qualification. Source/freeze104 and
scoped hooks pass. No new alignment, worker mapping, barriers, public knobs or
register budget. Native codegen/full13 performance remain pending. See
combine-packed-bf16-expand/SOURCE_REVIEW.md and frozen source ccfa0942.

### Paired128 with delayed register donation (9f/F1)

Full13 remote sealing/comparisons pass against both exact retained3de/A1 and
pair-only7dc/C1, with104 exact output pairs per comparison and unchanged13
tactics. A1/F1 decode4–512 GM is1.002157537x; C1/F1 is1.001359823x. This is
only0.22% net decode improvement and does not establish a useful general gain.
Against A1, prefill4k/8k/16k ratios are1.020747922x/0.966126766x/1.009804298x.
The8k median rises759.9215→786.565us with MAD4.928→30.976us; the increased
spread limits causal interpretation.16k changes1497.769→1483.227us with
MAD69.216→63.4725us. Keep this experiment unpromoted; do not infer that a
different simpler register-lifetime implementation cannot help.

Full net/incremental tables are input-stage-pair-tail-registers/decode13-benchmark/
terminal-summary-table.csv and comparison-c1-table.csv. Sealed archive
f4acf6deedc2552fa013c6a2b76ada27ada1446edf9e50d88717b8fab2756da0 remains
remote; heavy transfers are paused for the next timing arm, so full independent
local raw-evidence audit remains pending. No actual F1 codegen resource gain
is claimed. The next isolated ccfa/G1 packed compute trial uses unchanged A1
and the same13-row benchmark, without stronger alignment or changed workers.

### Packed BF16 expansion G1 and completed sanitizer qualification

ccfa/G1 full13 sealed against unchanged same-node3de/A1. All104 output pairs
are exact and all13 tactics match. Decode4–512 GM is0.989376437x,0/8wins
(about1.07% latency regression); prefill4k/8k/16k is1.003100386x/0.967527197x/
0.995017502x. The8k spread rises MAD4.928→25.216us. Leave G1 unpromoted;
full rows/MADs remain in combine-packed-bf16-expand/decode13-benchmark/
terminal-summary-table.csv. Archive9e583e13c99839d622ca41b9bcf6beca1d190dcc72506378fa40ba0b8c60e649
is sealed remotely; independent local full raw-timing audit awaits collection.
Matched exact3de/ccfa codegen at the actual G1 T16384 tactic1 completed with
8 bit-exact cross-source output pairs and64 ABI/resource compilations. Early
rank0 generated evidence is local; instruction analysis/full archive audit
remain separate and pending. No source-count reduction is yet claimed as a
measured GPU instruction reduction or speedup.

The retained3de sanitizer scan is now complete:6/6 batches,36 clean rank
reports (24 zero-error mem/sync reports and12 zero-hazard race reports),216
workload/rank and864 tactic/workload/rank cases,4961.57s. Root independently
verified all126 archived evidence files,104 source files, six JUnit results,
exact workload/tactic coverage and process/GPU closure. The archive is
ac2544b41e4655f41b54e5d476a50a3b86fe1aa592070a283c055fddf1b16ace;
audit is sanitizer-recovery-20260919/collected-sanitizer/root-integrity-audit.json.
Scope and memcheck tensor-op limitation remain in the audit. PR8 validation
status was updated without changing its source or final performance table.
Full60 bit-exact accuracy is active on retained3de/hu59; no full pass yet.

Next full13 performance arm is isolatedc038 unsigned worker divmod, preserving
existing nonnegative/nonoverflowing worker semantics and layout contracts.
Source/runtime preparation is reviewed; no custom magic-number implementation
or public tuning dimension is introduced. Tail register redistribution remains
an unimplemented conditional hypothesis because current reducer SASS has no
shown80-register pressure (see vectorization-research/TAIL_REGISTER_REDISTRIBUTION.md).

### Generated G1 instruction savings and control refresh

The matched3de/ccfa T16384/tactic1 early rank0 capture confirms the intended
BF16 expansion96→64 instructions. The selected reduction body falls147→115
instructions, whole kernel6408→6376, with unchanged8LDG128/1STG128,
4FMUL2/28FFMA2/4packed BF16 conversions. All eight early resource records remain
REG96/STACK0/LOCAL0, with no local loads/stores. Seven pre-multiply route loads
become six, but arithmetic starts six instruction slots earlier; this is a
scheduling difference, not a proven defect or explanation for decode timings.
Full details and scope: combine-packed-bf16-expand/codegen-selected/
MATCHED_REDUCER_REVIEW.md. Full403-member archive remains deferred.

After five serial candidate arms, request one new exact3de full13 control A2
on the samehu15 node, preserving A1. This creates a current reusable baseline
and helps assess whether the roughly1% all-row G1 difference includes drift;
it is not one baseline rerun per candidate and does not cancel temporal drift.
Both old/new comparisons must stay visible locally. G1 is still unpromoted.

A separate two-slab bulk reduction prototype is implemented on exact3de in
combine-coalesced-slabs/hashinfer. It preserves original width8 first-strip
workers and pairs later slices with warp-contiguous128-bit memory accesses,
sharing scores/address work without stronger alignment. Widths not divisible
by512 retain the original loop. Actual scheduling-AST ownership checks pass276
cases/8,729,128 tiles; per-element arithmetic and fallback-loop AST match base.
Scoped hooks pass. Source review and native benchmark are pending; this is
not a measured gain. Larger live state is a known tradeoff to inspect in codegen,
not a reason to preemptively change registers or add synchronization.

### Exact content reuse for evidence collection

All32 serialized rank-output files in E1/F1/G1/H1 have SHA256 hashes identical
to the eight already locally audited A1 files. Avoid re-downloading four342MB
gzip archives. Collect only noncached members from each original sealed archive,
then assemble complete local evidence using exact hash-matched A1 file bytes.
Every original member hash/filelist remains checked; label this file-level
verification separately from an original-gzip-byte audit. Preserve original
seals and partially downloaded chunks. No tensor equality assumption substitutes
for byte-hash equality, and benchmark/test execution is unchanged.

The eight A1 T16384 tensors also yield exact raw BF16 storage bytes matching
all eight G1 paired-capture outputs. They are cached with source-tensor hashes
under evidence-content-cache/; extraction performs no dtype conversion. This
allows codegen bundles to reuse the same raw output bytes for both arms. Any
future cache miss still requires collecting that original member. This changes
transport only, not the required timing/output/source/closure validation.

### FC1 routing-weight placement and score-free combine (2026-09-19)

PR9 (`[private repository link omitted]`) is an opt-in experiment
stacked on PR8. Initial implementation2a4986d1, current headf4c521f5; kernel,
frontend, reference, and benchmark bytes are identical across these two heads.
Apply FP32 route weights after FC1 expert scaling/clamping/SwiGLU and before
BF16 handoff. The final ordered FP32 combine no longer loads or multiplies
scores. False remains default. The two placements have different BF16 rounding
contracts, partitioned caches, and separate reference coverage. No new barrier,
transport buffer, alignment contract, role, or autotune tactic is introduced.

The EP8/GLM5/random/T128 numerical smoke passes all16 combinations,48 reference
and120 pair checks. All256 captured PTX files confirm RN multiplication and
ordered RN combine addition without score loads; retained SwiGLU still uses
approximate FTZ instructions. Full True numerical/sanitizer qualification is
pending. Eleven CPU cache/interface tests and pre-commit pass.

J1 complete13 comparison against fresh same-hu15 A2 is mixed: decode4–512 GM
1.007038x (6/8 wins); prefill4K1.002899x,8K0.975117x,16K0.985110x. T1 is the
only tactic change. Prefill dispersion is substantial and serial arms retain
drift. All104 outputs per arm repeat exactly; no cross-mode equality is claimed.
The full final table is in PR9 and fc1-routing-weight/PR_BODY.md. All64 original
J1 members are locally verified, including8 raw outputs reconstructed via
hash-checked XOR deltas against A1. The original gzip is not locally verified.
Auditc975c25b9b3e799ee970a9b4720c0ace5e7014e4fed695dfdd370c2f3ca17f19.

K1 (`e26fb67beca1896e3ee7bfbcae69ab9efca5c3fe`) is isolated under
fc1-combine-quad/. True mode uses four-element/64-bit combine workers to spread
smaller outputs across more of the existing CTAs. False stays8/128. Ordered
math and all tail barriers remain unchanged. Independent source review passes
144 scheduling cases/1,823,796 tiles; this is not GPU validation. The same-mode
full13 J1/K1 benchmark launched hu15 at10:05:27UTC, requiring104 exact outputs.
No promotion yet. Smaller vectors may increase prefill indexing/instruction
cost; source simplicity is not sufficient retention evidence.

The score/slot lifetime follow-up found no additional supported cleanup:
FC1 score addresses are already hoisted in generated code, staged scores
remain needed by peer pulls and later FC1 tiles, and top-k slot metadata remains
needed to preserve ordered combine. See SCORE_METADATA_FOLLOWUP.md under
fc1-routing-weight/. Avoid speculative load-hoisting or cross-warp broadcasts.

K1 finished with all104 same-mode outputs bit-exact and13/13 unchanged tactics.
J1/K1 decode GM0.995858x (2/8 wins): T4 improves3.4%, but T8/16/256 regress.
Prefill ratios0.998726/0.998221/1.011326x include substantial dispersion at16K.
Leave K1 unpromoted and preserve its branch/full table. PR9 remains f4c/width8;
its final before/after table remains J1 vs default A2. Next qualification checks
use current PR9 f4c, not K1: EP8/GLM5/T1 random andT16384 skewed, all4 tactics,
O2/O3 and eager/graph, against each case's independent bit-exact reference.

Both current-head edge cases pass. Audit0563927ba1edefe824975e237bac88f4162eae620d8614a5055df07e98873ab2
verifies the original294954-byte gzip,19members,source104,and clean closure.
The two cases cover32 combinations,96 reference checks,240 pair checks and
16912465920 BF16 elements with finite bit equality. T1 has seven empty source
ranks; T16384 sends all131072 routes to owner7. Together with the initialT128
case,48 combinations/144 reference checks/360 pairs pass. PR9 checks updated;
performance table unchanged. Primary hu15 proceeds to f4c True-only sanitizer6;
secondary hu59 finishes immutable3de default60, then f4c True-only accuracy60.
Keep these source/mode qualifications separate; no completed full new-mode
suite is claimed yet.

The additional False-mode audit confirms its deterministic path does not read
expert-pool routing scores; FC1 True and FC2 IKR are their only consumers.
Source-local scores are still required by False combine. The inherited
`dispatch_pull` unconditionally fetches/stores expert-pool scores and offers no
small overridable/nullable hook. Avoid copying its350-line protocol or editing
the shared upstream drop for this small candidate. A future shared constexpr
transfer option could address it cleanly; no gain is measured and no change is
implemented. See fc1-routing-weight/FALSE_SCORE_TRANSFER_BOUNDARY.md.

### Return to PR8 benchmark-first iteration; sanitizer deferred

The user stopped PR9 sanitizer and then clarified that sanitizer should run
only after all performance optimization is complete, not per trial. The run
stopped with0/6 batches completed and is not a pass. Exact owned processes and
GPU contexts closed cleanly; partial original archive76df22b6d1985e2eec17c509c755558bd27ec96733bc25818ed5ea768019565c
and26members are retained under fc1-routing-weight/sanitizer-qualification/.
The reviewed PR9 True60 accuracy successor remains prepared but unlaunched;
the already-running PR8 retained3de accuracy60 continues unchanged.

Next PR8 candidate d9d510f7 is the exact previously unrun34c9a3a width16 reducer
ported to534a623/retained3de. NoPR9 source is included. Its original source
review remains applicable to the unchanged reducer blob; current caller review
is separate. Wider workers reuse each score across two128-bit vectors with the
same16-byte caller alignment, ordered math, barriers and register allocation.
Full13 benchmark against same-nodeA2 comes first, with104 exact output checks.
No sanitizer or broad test suite is a pre-benchmark gate. See
reduce-tile16-current/EXPERIMENT.md and its frozen104-file receipt.

L1 width16 actually launched hu15 at10:47:28UTC, PID/PGID107721. Benchmark
source at534 differs from retained3de only in documentation/default token list;
the executed exported benchmark304a and allsix timing helpers remain unchanged,
with the explicit13-shape command. Source and execution hashes are bound
separately. No pre-benchmark sanitizer or numerical suite was launched.

M1 is queued as a separate PR8 trial: e193a2d5 ports the previously unrun
8b8b1ec FC2-partial L1-no-allocation hint onto534. The baseline reducer is
byte-identical; this four-line patch changes only its128-bit copy atom/cache
priority. It is not the earlier rejected activation-source hint, does not
include L1's width16, and has no new alignment/order/arithmetic assumption.
Its full13 sweep will reuse the same-nodeA2 control after L1 closes. All
sanitizer is now deferred to the final selected implementation per user policy.

I1 two-slab reduction is unpromoted: A2/I1 decode GM0.995592x, prefill
0.999554/0.965531/0.996969x. Its bulk path does not execute for the canonical
decode workloads on148SM, so decode differences do not demonstrate bulk-path
effects. All59 original members and104 outputs are locally verified. Full
results and scope are in combine-coalesced-slabs/RETENTION.md.

### Retained 3de: full 60-case numerical qualification completed

All 60 cases passed: 960 combinations, 2,880 reference checks, 7,200 pairs and
135,287,341,056 element comparisons; zero mismatches/nonfinite values. The
original archive SHA256 is
`41b0978137e965643e7dd8bf1bd6150edfa06a4bf2133caefafdf75c83c2ccf6`.
All 132 members, 104 frozen source files, exact coverage and clean process/GPU
closure passed the independent audit in
`sanitizer-recovery-20260919/collected-accuracy/root-integrity-audit.json`.
PR #8 validation text is updated; its final performance table is unchanged.
This qualifies retained `3de` and benchmark-only descendant `534`, not L1/M1
or PR #9 True mode. PR #9 True60 remains held. Sanitizer is deferred until
performance optimization finishes.

### L1: wider combine full13 result

Audit `a44929ec021a957cc23cc04b431dc1af1199b01607e1a9eb68ae305878786f36`
verifies all 59 original members, 1,300 samples per arm and 104 exact output
pairs against each of A2 and A1. The original gzip remains remote and was not
verified locally. A2/L1 decode geometric speedup is 1.008089x, with 3/8 rows
faster; prefill is 0.995368/0.989270/0.992764x. L1 is unpromoted.

The T4 improvement, 97.648 to 88.9125 us, uses the same N64/epilogue tactic on
all eight ranks, with separated quarter medians. Excluding T4 only as an
explanatory diagnostic gives 0.995829x for the other seven decode rows; the
official retention set still includes T4. The full table, MAD and quarters
are in `reduce-tile16-current/RETENTION.md`.

M1 launched on hu15 at 10:59:36 UTC, PID/PGID 114284, port 30070, after L1
closure. Hu59 separately ran a bounded baseline/L1 codegen capture at the
actual H7168/T4/O3/EP8 winner. That capture includes eager/graph repeats and
cross-version output equality, with no timing claim or sanitizer.

### M1: partial-cache hint full13 result; not promoted

A2/M1 decode geometric speedup is 0.998050236x (5/8 rows faster); prefill is
1.005850/1.009739/0.999377x. T8 regresses from 121.1045 to 129.8245 us with
the same tactic and separated quarters. T4 improves from 97.648 to 93.8885 us.
These results do not support retaining the general cache policy.

All 104 finite bit-exact outputs match each of A2 and A1. The full-file/raw
sample audit and complete table are in `combine-stream-current/`. No extra
codegen, numerical suite or sanitizer is requested for M1.

### Confirmation and compilation-cache finding

A3 remeasures retained 3de, followed by L2 repeating the exact L1 source.
Each uses its original physical source/cwd and CuTe/CUDA cache paths, with
fresh knob caches, AUTO4, 13 shapes and 100 cold-L2 samples. Root reviewed the
narrow driver diffs. This confirmation follows a selective T4 result; it is
not a new baseline for every trial.

The prior A2 CuTe cache directory was empty; its CUDA driver cache existed.
Root traced the pinned CuTe 4.7.1 wheel: `cute.compile` exposes
`CompileCallable`, which forces `compile_only=True` and `no_cache=True` in
`base_dsl/compiler.py`. The original general JIT cache analysis did not apply
to this explicit compile entry point. `CACHE_REUSE_REVIEW.md` is corrected,
with its previous version preserved. A3/L2 settings and source remain
unchanged. No CuTe cache hit or compilation-time saving is claimed; this
does not invalidate their timing.

A3 passed 104 exact outputs and all 13x100 samples. Independent audit
`06dffff54460a1641ea3071906a6031129c8ab66228238383c41a581d6c42469`
verifies the 59 original members, source and closure. A2/A3 decode speedup is
0.995121x. A3 T4 is 97.665 us versus A2's 97.648 us. L2's live T4 row is
96.8165 us (MAD 1.1365), using the same N64/epilogue tactic on all eight ranks.
The earlier L1 value of 88.9125 us has not repeated. Treat that selective gain
as unconfirmed; the full L2 sweep continues.

### Matched T4 codegen and whole-path coalesced successor

The T4 baseline/L1 capture passed eight exact rank-output pairs plus eager
and graph repeats. All 64 ABI resource reports show REG96/STACK0/LOCAL0,
with no local spills. Adjacent16 still issues two 128-bit halves. Widening
also reschedules dequant instructions, so no causal timing explanation is
established. See `reduce-tile16-current/codegen-selected-t4/MATCHED_T4_REVIEW.md`
for the full verified 422-member archive and generated-code counts.

N1 is queued after L2 closure: commit
`21f598d8db88df87302e96e233599eab2f6db048` uses one coalesced16 body for every
worker, including decode and the first stripe. It differs from rejected I1's
head8/bulk16 design and has no runtime shape selector. Two eight-element
slabs use a compile-time lane group dividing H/16, preserving every existing
H%32 shape and 16-byte alignment. The equivalent mask expression
`tile + (tile & -G)` avoids signed group division/remainder.

The original 519 snapshot is preserved; the final source is under
`combine-coalesced16-wholepath/frozen-v2`. Independent source review
`53054d80` and 1,200 CPU ownership cases pass. No GPU execution or performance
gain is claimed yet. Compare against A3 and L2 using the unchanged full13
method, without another baseline or a sanitizer/pretest gate.

### L2 complete; N1 launched

L2 passed all 104 exact output pairs against A3 and A1. A3/L2 decode geometric
speedup is 1.000462938x, with 4/8 rows faster and identical tactics on all 13
rows. Prefill is 0.996049/1.041689/1.007718x; A3's 8k/16k MAD is
30.0335/80.817 us versus L2's 5.9815/39.535 us. Keep the dispersion and serial
drift limitations. The full table is under `reduce-tile16-repeat/`.
The T4 gain from the first L1 run did not repeat; adjacent width16 remains
unpromoted. Archive: `d6b4c41e3e47204c27a1c7654708bf82f4e736a42820226ab8dbcf0e139e0084`.

N1 actually launched on hu15 at 11:36:26 UTC, PID/PGID 131130, port 30076,
after source, node, idle, predecessor closure and transfer gates. Source is
`21f598d`; stage SHA256 is
`0fa81e8974ee818c246cccaabb7146d3baf02096d76c790230f6994feb311928`.
The 13-shape/100-sample/AUTO4 public-forward method is unchanged. Compare
primarily with A3, with a separate L2 comparison to assess coalescing.
No pretest or sanitizer gate was added.

### N1 full13 audited; confirmation and bounded numerical checks

The coalesced16 candidate `21f598d` completed all 13 shapes. A3/N1 decode
geometric speedup is 1.007560295x (6/8 rows faster), and L2/N1 is 1.007094073x.
Prefill A3/N1 ratios are 1.002053/1.014905/1.015226x. All 13 selected tactics
match A3; all 104 finite rank outputs match A3, A1 and L2 bit-exactly. The
independent audit is `5fb9e4104b514ee4b25ec4059a8318c72412fbba60daca8d0183be00e962243a`.
All 59 original member files and every raw sample were locally verified;
only the compact transfer gzip was downloaded, so the original archive hash
`83bc2ba70c46e9d38168fe0749149ee0d3e5c54ed58280fc6e09ad68890cbc3d`
is a remote seal reference, not a locally verified gzip byte stream.

T8 and T16 improve by 2.34% and 1.90% against A3, while T4 is 0.65% slower.
N1's T8 value still lies within the range of the unchanged retained controls,
and A1/N1 decode is 0.998530620x. The large prefill MAD also limits causal
interpretation. Preserve selected3de; do not update the PR's final table from
one marginal sweep. An exact N2 repeat is authorized on hu15 with fresh AUTO
knob/output state and unchanged source/methodology. Hu59 independently runs
existing generic-lane-group/graph/stride cases and one GLM5 T128 random EP8
bit-exact case, including all four tactics, O2/O3 and eager/graph. No sanitizer,
full60 rerun, PR9 task, or additional primary GPU trial is authorized here.

A source audit found no existing per-route completion certificate for safely
starting combine before the full drain. Input counts, expert-local FC2 counts
and return-work reservations have different publication meanings; waiting on
the global completion signal before the first CTA rendezvous would cycle.
See `vectorization-research/EXISTING_RETURN_SIGNAL_FEASIBILITY.md`. A new
receiver publication/epoch protocol remains a separate transport design,
not a small counter or barrier removal justified by current evidence.

### N2 and bounded native checks complete; retain selected3de

N2 repeats exact21f598d with 1.006041049x decode geometric speedup versus A3
(4/8 wins), but 0.997024989x versus historical A1. N1/N2 is 0.998492154x.
All 104 outputs match A3, A1 and N1 exactly; all 59 original member files
and 1300 timing samples are audited. Decode/prefill tactics are unchanged;
only T1 differs. Audit: `72a0b7ac3f118af0021805bc5400d1a3becdfc6624e996426ab940fb719ab7ae`.
See `combine-coalesced16-repeat/RETENTION.md` for every row and quarter.
The original archive gzip is not downloaded; all sealed member bytes are
verified locally. Hu15 is idle after source/process/GPU closure.

The selective decode improvements move between N1/N2, and prefill retains
large temporal shifts. The coalesced16 candidate remains unpromoted. No PR8
performance table change is justified by these repetitions.

Native checks of21f598d also pass: eight graph/layout cases, two H2880 tail
references, and GLM5 T128/random/EP8 over all16 tactic/O-level/execution
combinations. The last case has48 reference checks,120 pair checks and
132120576 finite BF16 bit comparisons with zero mismatch/nonfinite values.
Total390.36s. Original archive `2f221e2426c5b621f909ead12730173f23377dd1c3baa6b11ac2e14aeb7a3aa3`
and135 member files are downloaded and verified. No sanitizer ran.

The separately requested EP-local FP32 combine investigation lives at
`../ep-local-combine-20260919/`. The user's later instruction paused initial
helper/reference implementation for a source/cost review against direct FC2
remote stores. Publish an issue instead of a PR if the current pipeline does
not support a convincing tradeoff. This does not change PR8's selected source.

### Caller-bound cleanup published; EP-local combine documented

Commit d01f074947d2cc754d6062c2b2ffe674e1577a34 removes only the redundant
reducer inner token bound, its field and alias; the unchanged arithmetic body
is dedented. The sole caller bounds every worker before preparation/reduction.
Whole-module normalized AST and the byte-identical caller pass source checks.
H6144/H7168 already constexpr-eliminated the guard, so no performance rerun
or new gain is claimed.

Six existing native tests pass: four H1600 graph/input-layout cases and both
H2880 tail-reference return paths, zero skips/failures/errors,126.390s. Original
gzip b160723274139e2ed0cde66953355a3cc8151afa69b03b0eb219ccc4c75b4062,
all132members and104sourcefiles are locally verified. Independent terminal
audit4531eb324612c0a1d146f40c79583bf3d2ef0e40e27c27ecf65f643fadb5c66c
confirms source/node/process closure. No sanitizer, fullsuite or benchmark ran.
Canonical PR8 fast-forwarded/pushed to d01f074; body readback matches
PR_BODY.md and still contains only the original final3de performance table.
PR8 remains draft; full60/sanitizer qualification is explicitly pinned to3de.

EP-local analysis is published as [private repository link omitted]
Direct FC2 peer stores already overlap remaining work; simple FP32 staging
adds substantial logical accesses and worst-case capacity. Random EP8/K8
reduces ideal return payload33.82% but materialize-all adds33.09% logical
bytes versus dispatch (excluding the common output store). These are model
estimates, not timing evidence or lower bounds on all possible designs.
Singleton bypass and bounded native-layout consumers remain research options.
No new-mode GPU test/implementation PR; uncommitted helper/reference drafts
are preserved. User renewed PR8 optimization, with sanitizer still deferred.

### Continued optimization: weighted width4 and staged-ID layout investigation

The width4 weighted reducer candidate54301c6 is isolated on d01f074.
It changes four source lines: worker width/doc and both copy atoms128→64bit.
Output alignment follows width and becomes8bytes; arithmetic remains ordered
FP32-pair multiply/FMA per output. This differs from the prior PR9 True-mode
width4 experiment, whose score-free arithmetic is not PR8's contract. Primary
control is same-node retained3de/A3 with historicalA1 shown separately.
The d01 parent cleanup was already constexpr-disabled at H7168; baseline
source versions remain explicit rather than claiming a new d01 measurement.
Source/helpers are under combine-width4; full13/100/O3/AUTO4 is planned onhu15.
No sanitizer or prebenchmark native suite.

An independent staging investigation found the owned ID destination retains
a dynamic row stride, although public symmetric buffers have fixed layout.
A naive static descriptor is unsafe for direct fused frontend callers that
change destination strides because the old compilekey lacks that layout.
Evaluate a complete private compilekey without ownership flags or additional
public tuning; preserve arbitrary caller source layouts and raw dynamic mode.
No implementation/performance benefit is established yet.

### Width4 rejected; user staging audit motivates metadata-first scheduling

54301c6/O1 passes independent terminal audit0d4c43e8: all59 original
member files,104 exact finite outputs against each A3/A1 control and1300
raw samples. Originalgzip062b3402 remains remote; local memberbytes verified.
DecodeA3/O1 is1.002623997x (5/8 wins), historicalA1/O1 is0.993638560x.
PrefillA3/O1 is0.990471/1.041513/1.002567x; the8K advantage does not
survive comparison with historicalA1 and bothlarge-prefill rows drift.
All13tactics match. Keepwidth8/d01; width4 remains unpromoted with fulltable
in combine-width4/RETENTION.md. No extra numerical/sanitizer suite ran.

The user pointed to fc1-fc2-handoff-audit-20260919/FUSED_STAGING_AUDIT.md.
It identifies a distinct window absent from earlier staging trials: release
real scheduled work after routing/count publication, allowing weight TMA and
dequantization during source activation copying. Earlier trials kept scheduler
release after copying. Localprototype3cd1f70 implements the reviewed unified
metadata→scheduler→copy→payload-publication→pull sequence using existing
primitives in owned token_comm.py. Two owned files only, all sharedcode unchanged.
Every rank, including prestaged/empty ranks, joins the new payload publication.
NormalNVLink phases increase2→3; NCU replaces oldpadding, retaining4.
Existing proxyfences, twoCTA TMEM initialization, fiveWGs/registerbudgets,
received-pool readiness and counterbank lifetime are unchanged.

Source/hooks/ASTscope proofs pass; frozen104 archive0dfcc9f7 /manifeste943f525.
P1 full13/100/AUTO4/O3 onhu15 is prepared with A3/A1 controls and O1closure.
No GPU correctness/performance claim at sourcefreeze. Additionalpublication
may exceed any boundedweight-startup savings; diagnostic should establish
actual overlap/firstMMA before attributing results. Sanitizer staysdeferred.

Independent912f109 staticstaged-ID-layout fullpair runs onhu59 againstfresh
d01baseline in its own namespace. No cross-nodeperformance comparison or
combination with metadatafirst is intended.

### Primary node reclaimed before metadata-first launch

The reviewed P1 package3cd1 source did not execute. Managed inventory reports
no ziangli/c2 devbox hashinfer-recovery-0919; lossreceipt15d407a5 is preserved
under metadata-first-staging/decode13-benchmark/. No source transfer/launch
receipt exists for that attempt. O1's complete locally verified59members and
source/timing audits remain valid; its original sealedgzip is now unavailable
from that node. Do not carry A3/A1 timingcontrols onto another node.

Use still-activehu59 after its static-ID B1 closes, reusing freshd01 A1 from
that same node/boot/software. Secondary remains soleGPUowner; primaryagent
helps CPU-only successor preparation. No replacement request orGPUwork was
launched by the lost-node owner. Original P1 runtime/source remain immutable.

## 2026-09-19 — final-combine audit and independent dispatch certificates

The user supplied `FINAL_COMBINE_AUDIT.md` alongside the staging audit and
explicitly authorized parallel devboxes. The first prototype is isolated in
`../final-combine-prefix-20260919/hashinfer`, based on published `d01f074`.
It owns a deterministic BF16 full-row return specialization and carries an
explicit optional readiness view through the owned kernel ABI; protected
shared source remains unchanged. Two symmetric route-mask banks are part of
the existing receive-bank layout. Existing bank snapshots, opposite-bank
clears, NCU active-bank cleanup and terminal publication cover their lifetime.

Notifications are system-release ORs issued by the same elected thread after
its full bulk-store wait. A compile-time experimental constant separates
notifications-only overhead from a finite early prefix on retired decoder
workers. Every early worker system-acquires its row mask, preserves ascending
ordered FP32 reduction, and exits on the first miss without spinning. Both
common tail barriers and the global drain remain. Direct epilogue and optional
in-kernel BF16 reduction retain inherited behavior.

CPU bank/ownership checks passed (540 actual layout cases,160 worker mappings)
and scoped pre-commit passed. These are source checks, not GPU correctness or
performance evidence. Independent ordering/codegen review and benchmark remain
pending. No sanitizer during performance iteration. The new devbox allocation
`hashinfer-combine-0919` uses explicit `nvcr.io/nvidia/pytorch:26.05-py3`;
although it reuses physical hu15, it is a fresh container with no old workspace.
Fresh same-node control is required. The source prototype and all artifacts
remain outside the published PR8 branch.

## 2026-09-19 — metadata-first P1 regression and publication-cost follow-up

The hu59 P1 `3cd1f70` full13 sweep completed with all104 finite outputs bit-exact
against its fresh same-node d01/A1 control and all13 selected tactics unchanged.
Decode4–512 geometric speedup is0.949920108666× (about5.27% higher latency),
with0/8 decode wins; every reported shape is slower. Prefill speedups are
0.978707×/0.983742×/0.994360× at4096/8192/16384. Preserve the full raw table,
samples and terminal evidence under `metadata-first-staging/decode13-benchmark-hu59`.
This trial stays unpromoted, with no broader qualification. The output checks
and timing do not establish how much actual dequantization overlaps staging.

A follow-up is isolated in `metadata-payload-publication/hashinfer`, based on
3cd. It keeps the full all-rank payload boundary while replacing its final
local grid broadcast with a system-acquire by each dispatch CTA and its normal
128-thread CTA barrier. A separate persistent payload prologue-grid counter
keeps the ordinary resettable grid counter's rounds even. The next drain's
prologue proves every old payload-slot reader has retired before reuse.
Source review/benchmark are pending; no performance claim. Compare against
both the same hu59d01/A1 andP1, with no historical hu15 ratio reuse. New final
combine experiments run independently on the replacement hu15 allocation.

## 2026-09-19 — Q1 rejected; row-scoped input publication prototype

Publication follow-up44b5 completed full13/100/O3/AUTO4 on hu59. It improves over metadata-first3cd by1.026314× over decode4–512, but retained d01/A1 remains faster:0.974916× (1/8 decode wins), prefill0.975216×/0.980820×/0.989371×. All104 outputs are finite and bit-exact against both controls; all13 selected tactics match. The independent audit verifies all170 reconstructed member files and raw arithmetic. Preserve full table/MAD/quarter samples in `metadata-payload-publication/RETENTION.md`; reject Q1, no broader qualification. Original compressed archive bytes remain remote, distinct from complete locally verified member bytes.

The next local prototype, `row-ready-staging/hashinfer`, replaces the extra rank-wide payload gate with individual source-row publication. One CTA owns each row; all128 writers fence/rendezvous before its system-release flag. The same elected issuer acquires the peer row flag before TMA. All local copies precede that CTA's pulls, preventing a wait-before-publication cycle. Ready flags use the existing two receive-bank lifetimes. The owned BF16 pull specialization retains scheduling, router-weight traffic, TMA waits, metadata and arrival batching; shared transport is untouched. This trades small-shape copy parallelism and per-row signaling against the removed global wait. Actual bank/mapping CPU checks and scoped pre-commit pass; source review and full13 timing pending. No performance claim or PR change.

The independent return-certificate experiment passed bounded native eager/graph checks on replacement hu15 for forced N64/N128 dispatch:32 cross-source raw BF16 comparisons exact,192 compiled ABIs. Executed int32/vector variants use96 registers withzero stack/local; notifications-only N64 int64/generic is compile-only and has8 stack bytes. Do not generalize the executed ABI resource result. Full fresh-control/notifications/early-prefix AUTO sweep is running. The held prefix-count diagnostic records existing worker continuation after the finite loop and resets sentinel before each observed execution; it has no timing retention role. Sanitizer remains deferred.

## 2026-09-19 — row-ready result and measured finite-prefix coverage

Row-ready4cd completed full13 on hu59: retained d01/A1 divided by candidate decode4–512 GM0.9410589765,0/8wins. Prefill ratios4096/8192/16384 are0.954419/0.942848/0.991321. All13 tactics unchanged and104 rank outputs finite/bit-exact; independent terminal audit verifies167 original files and raw samples. Reject, no broader tests/sanitizer. The implementation removes the whole-rank payload gate but changes copy ownership; this result does not isolate each cause. Full table under `row-ready-staging/decode13-benchmark-hu59-v2/RESULT.md`.

On replacement hu15, the final-combine A1/B1/C1 sweep completed with all104 exact output comparisons for each pair and438 reconstructed original member files independently verified. All decode winners use the unchanged epi return path, so those variations do not establish an early-prefix effect or justify rejecting its active path. At8K/16K, early-prefix203fc5 versus notifications-only782bbf is1.008447×/0.993519×, mixed amid substantial prefill sample drift. At4K both candidates select epi and show no net benefit versus retained dispatch. No promotion. Full13 table, selected modes and dispersion are in `../final-combine-prefix-20260919/RETENTION.md`.

The reviewed08e diagnostic measured actual finite-prefix continuation on forced N128 dispatch, with eager/repeat/two graph-replay observations. All24 rank results and96 snapshot counts pass independent audit; all compiled ABI resources have96 registers andzero stack/local. At128, eligible decoder work completed before the drain is0%,0%,0%,1.45%;4K roughly0.95–1.16%;16K4.91–5.35%. The latter is only2.48–2.70% of all reduction workers. This establishes limited nonzero instrumented work, not uninstrumented timing causality or proof that all possible overlap is exhausted. No sanitizer ran.

A striped-copy alternative is preserved under `cta-ready-staging`: restore the original flat activation mapping, publish one source-CTA bitmap bit, and acquire only the owners of a requested row. Review caught an unproven equal-CTA-count assumption before GPU execution. The corrected1455 source publishes each rank's count through the existing metadata barrier, loads descriptors only in active pull warps, and retains constant-modulo lowering for equal grids with a correct heterogeneous fallback. No new collective or public constraint. Frozen-v5 review/benchmark pending; earlier bitmap freezes are unexecuted and ineligible for promotion.

The corrected striped-copy1455 candidate has passed source/runtime review and launched S1 on hu59 after R1 closure. It supports distinct producer/consumer CTA counts via an existing-publication header, with no per-row remote descriptor load and no header traffic from idle pull warps. The final freeze is `cta-ready-staging/frozen-v5`; all earlier bitmap variants were held/unexecuted. Benchmark remains13/100/O3/AUTO4 against samehu59 d01/A1, with R1 as incremental context. No promotion, broad tests or sanitizer before its result.


## 2026-09-19 — interrupted striped sweep and narrow scheduler runahead

Corrected ca05 striped staging compiled and executed T1/T2/T4/T8 on hu59; the devbox then disappeared from managed inventory. No kernel failure was observed in the last valid poll. Preserve all four rows as interrupted partial evidence, not a full retention table, and do not splice them into another node. Runtime INTERRUPTION.json records the identity and missing-node response. Recovery moves the unchanged frozen source to the idle hu15 container using that node's completed d01/prefix-A1 control. All prior hu59 completed evidence remains local.

An independent narrower opportunity from FUSED_STAGING_AUDIT is isolated at early-scheduler-broadcast/hashinfer2bb3a02 (16 added/30 removed lines in two owned files). The atomic scheduler already claims an ID before common initialization; the experiment moves only its existing first cluster broadcast after common init and before dispatch readiness. The resulting one Int32 feeds first gen_next_work, whose expert-count decode remains after the unchanged wait. Subsequent/static paths, barriers, atomics, math, staging and registers stay unchanged. Private optional argument resolves at compile time. Scoped precommit passes; frozen104 archive914a612/manifest7acae18. Source review and fresh-node timings pending; no speedup claim or PR change.


A replacement second node is ready: hashinfer-startup-0919,c2/infra,hu115,b474cb00-f717-4583-a4b5-978d501455c6,8B300. Root withdrew the no-quota queued ziangli request and stopped only its old local wait process, then allocated infra with bare explicit26.05. Live release-page capture confirms26.05CUDA13.2.1.009 and newer26.06/07/08CUDA13.3/13.3/13.4; no moving tag. ikr owns setup/fresh d01 control, prep owns hu15 striped recovery. The2bb source/state/trace-time audit7681aafb passes, including unchanged102files and firsttilepipelineadvance ownership; native compilation/codegen still pending.

A separate one-file candidate ec7428d moves unchanged dispatch64 and stage_inputs before raw_pipe.create (13+/10−); common init arrival/wait, TMEM allocation/retrieval, all publishers and budgets stay intact. This enables overlap with warp0 barrier initialization but delays TMEM startup until staging completes. It is distinct from historical after-create/multi-WG trials and stays lower priority than early broadcast. Scoped hooks pass; archive2d52d424/manifest08fd782d. Exact source review and same-node full13 timings pending. No current-best claim, no PR or sanitizer changes.


Hu15 S2 recovery now runs under PID/PGID52355 at1789829658.261233, port30104. Runtime reviewac2171d7 binds prepared2ddfc587/runtime d032223b; stage6fea35f7 verifies source104, matching boot/software, the prefix study's A1 source and final seal, subsequent diagnostic closure, idle GPU and free port. Full13 restarts here; no partial hu59 splicing. Hu115 pinned setup ec5420b9 passes with identical prior environment, Torch preserved, CUPTI13.2, no GPU tests; fresh control and two independent candidates held for runtime review. ec742 exactsource review1eb62a62 passes.


Hu115 final runtime uses the reviewed compile-exception-only worker0ffdd07 in all arms, preserving its successful AST against c3bc. Root review5f502b17 verifies24 runtime files,312 source files,13/100/AUTO4/O3 command scope, both source reviews, setup closure and stage/launch gates. Prepared6244b25f/runtime15487833; no per-arm source stacking. Staging/launch authorized. Earlier unexecuted c3bc-worker preparation is preserved separately. No added pretests or sanitizer.

Hu115 three-arm full13 launched at1789829942.491576 under PID/PGID3816,port30106 after fresh312source/identity/software/group/GPU gates. A1d01 precedes B1earlybroadcast2bb and C1preinitstagingec742 automatically; all3 use same exception-only worker and timing helpers. Hu15 remains separately owned for ca05S2. No transfers during active timings, no performance result yet for startup changes.


## 2026-09-19 — striped staging rejected; current-tail concurrency retest

Hu15 S2 ca05 completed all13 rows with104 finite/repeat-exact cross-arm outputs and all13 tactics unchanged. Independent audit645db008 verifies169 original member files, source/runtime/control and process/GPU closure (1789830278.104872). DecodeGM0.944670589,0/8wins; every candidate decode quarter median exceeds every corresponding baseline quarter. 4K/8K/16K ratios0.970046/.984111/1.008488. The last aggregate is drift-heavy and does not establish a prefill gain. Reject without further qualification/sanitizer. Complete table/MAD/quarters in cta-ready-staging/decode13-benchmark-hu15-recovery/RETENTION.md. Originalgzip18087913 remains remote; complete member verification is local, not originalcompressed-byte verification.

Ported the exact historical b6→f25 compile-time capacity-gated fifth-WG patch onto retained d01 as2739b8d (45+/4−,one ownedfile). The original f25 prefill rows showed possible gains while inactive decode varied, but it preceded current early previous-bank clearing. The new retest changes only dispatch joining the unchanged ordered reducer after local cleanup; four existing WGs still overlap cleanup. Workerstride512→640 onlywhen staticcapacity canreach the fifth strip. No new register redistribution, barrier, storage or publicaxis. Decode4–512 benchmark capacities prove extra strip inactive (ceil(T/8)*896≤512*148); candidate's actual compiled false-path evidence is required if prefill timing merits retention. Do not ascribe inactive-code timing noise to the fifthgroup. Frozen104 archive0561e344/manifest0762d01e; scopedhooks pass, independent review and hu15full13 pending. CanonicalPR8 remainsd01.


2739 exact current-base source reviewc98ea383 passes:103 otherfiles unchanged; false fold restores d01 AST;132 ownership cases and staticcapacity/CTA, singlecleanup, bothNCUcollectives, IKR/raw/currentbank lifetime checked. Hu15 W1 preparation77e56009/runtime3509763f reviewed00ee7020 binds18 runtimefiles/104sourcefiles, same0ff measurementworker and sameprefixA1; S2 onlyclosurepredecessor. Stage/launch authorized withport30106. No generated-code identity or speedup yet.

Iteration audit corrects an earlier rough compilation estimate: existing records show8 compile API calls per row/rank (4actualtactics,1reappliedwinner,3unusedwinnerABIs), not16. A futurebenchmark-only guarded `_compile`/`_staging_key` wrapper could omit the3 syntheticunusedrequests and rejectany attempttoexecute them, preserving all5 real compilecalls, warmup/autotune/publicforward/timer. This is narrower ABI coverage, not a full public validation; requires measuredpreparationtime and actualcode/output comparisonbeforeadoption. No runtime/source changesmade; allcurrenttrialskeepthefullworker. See benchmark-iteration-audit/UNUSED_ABI_COMPILE_AUDIT.md.

W1 launchedhu15 at1789830841.613969 underPID/PGID60229,port30106; stagef335029a rechecks104source, sameboot/software, prefixA1 andS2closure, GPUidle. Full13/100 beginswithnoextratransfers; GPU qualification/sanitizerremainconditional/deferred.

## 2026-09-19 — remaining address-efficiency experiments

The first scheduler-broadcast2bb full13 finished on hu115 with preliminary
decodeGM0.987321 and prefill0.999837/0.959524/0.987198 versus freshA1. C1preinit
still runs; raw/terminal independent audit is pending before a final conclusion.
Current-base fifth-WG2739 W1 finished onhu15:104 exact outputs,13same tactics;
active prefill ratios1.010541/.960070/.979782. Mixed, no promotion. Inactive
decode timings are not attributed to the fifthWG. Compact evidence is being
independently checked. No qualification/sanitizer is scheduled for these trials.

Two independent small d01-based candidates target generated address work:

- `reducer-coordinate-recurrence/hashinfer`63f49bc (28+/2− in2ownedfiles)
  advances token/hidden-tile coordinates with a static quotient/remainder plus
  one carry, replacing continuation divmod. Initialworker and score prefetch,
  orderedmath, ownership and barriers are unchanged. Source review878cf6f0
  verifies104files/102unchanged, reverse completeAST,1074actualhelper cases,
  exactfour-WG stride, zero-remainder fold and validInt32 domain. It is a
  prefill-only active change; no directdecode gain should be attributed.
  Archivead46cf89/manifestb29c645b. Hu15R1 runtime preparation pending.
- `linear-combine-address/hashinfer`ce0bbca (19+/13− in2ownedfiles)
  uses the live linearworker for reduceraddresses. For actualstatic route
  strides sT/sK/sH, offset=8*w*sH+t*(sT-H*sH)+k*sK, promotingw/ttoInt64 before
  products; contiguous outputoffset=8*w uses existingfrontendcontract. Raw
  combine buffers are not assumedcontiguous; existingcopyalignment unchanged.
  Initialpreparation/math/barriers are unchanged. Archivef56bbc70/manifest40a93915;
  scopedhooks pass, source reviewpending. Hu115successor afterthree-armclosure.

Both are benchmark-first, independent of eachother and unpromoted. They test
instruction/lifetime opportunities visible in earlier SASS, without claiming
those instructions dominate latency. Native/codegen qualification only if
full13performance merits it; sanitizer stays deferred.

## 2026-09-19 — address trial results and compile repair

Coordinate recurrence63f49bc R1 completed onhu15 with104 exact outputs and13
unchanged tactics. Independent terminal audit b0f93d19 verifies169 member files,
source/control/runtime and process/GPU closure. Active prefill ratios are
1.007633/.990740/1.008518×. The4K quarters are modestly favorable,8K regresses,
and16K has opposite first-half/second-half directions with dispersion much
larger than its median gap. No useful broad gain; keep unpromoted. Decode
0.999797× is inactive continuation-path variation, not a causal benefit.
Full table: reducer-coordinate-recurrence/decode13-benchmark-hu15/RETENTION.md.

Linear-address ce0 D1 onhu115 failed before its first timing row. All8 rank
logs identify lost source-pointer alignment proof in the128-bit universalcopy
(16bits inferred,128bits required). No runtime output or timing is claimed.
Exact104 source and all10 process groups/GPU closure pass at1789832333.054.
Failure evidence stays in linear-combine-address/decode13-benchmark-hu115.

A six-line successor3b42f0d imports gcd and annotates route_offset via cute.assume
with divby=gcd(8*sH,sT) or1. Existing frontend/kernel H%32 makes this divisor
identical to gcd(8*sH,sT-H*sH), the offset's integer-combination guarantee.
No stronger alignment/contiguity requirement or runtime guard is added.
Installed CuTe4.7.1 source core.py2258 accepts anypositiveint divisor and emits
ConstrainedIntType; CPU-only capture69fdea10 documents it. Originalcopy atoms,
math and output alignment remain unchanged. Frozen-v2 archive dbde5e75,
manifest d7feacc2; scopedhooks pass, independent source/runtime review pending.
Rerun as separateD2 against unchanged freshhu115A1; never splice failedD1.


## 2026-09-19 — corrected linear-address full sweep

3b42 D2 compiled successfully and completed all13 rows onhu115 against its
original d01/A1. All104 finite BF16 output pairs are bit-exact, all13 selected
tactics match. DecodeGM1.005821638× (6/8wins), butT8 .941938× andT64 .967603×
regress. Prefill4K/8K/16K ratios1.008967/.962814/.971607× do not justify retention.
Keep d01; no generated-code qualification, extra timing repeat, native suite or
sanitizer for this mixed candidate. The alignment repair is functional; initial
ce0 compile failure is not used as performance evidence.

D2 launch1789832979.761842/PID26774, terminal1789833571.5956037; source104,
allownedgroups andGPU closure pass. Prepared3b7aad40/runtime d4e2d60c reviewed
f02ebfcb; frozen-v2 source dbde5e75/d7feacc2 reviewa068a23b. Sealedgzip
`d6d61e46e1b5528326ef69a4c057b41fa75dd3a43f9da4aa301ed4bf1c54919f`
remains remote. Compact602551B collection736e4d6a has158newmembers plus8cached
exactserialized outputs, covering166originalmembers. Independent terminal
audit pending. Raw table/MAD/quarters are under linear-combine-address/
decode13-benchmark-hu115-v2. No new candidate queued in this batch.

D2 final independent terminal audit1b64cd87 passes all166 original member bytes,104 exact outputs and expectedclosure. Full13/MAD/quarters are in RETENTION.md (SHA37b6f14c). T8/T64 slower quarter ranges remain separated; address change is active there, with no tactic switch/inactive-path explanation. All completed candidates in this batch remain unpromoted. Both devboxes are idle; no further GPU job/transfer is queued. Canonical d01 source and PR body were not changed.
