# Current state: exact tail-reduction descriptor correction

**Latest pushed HEAD:** `21fd7ce48b0a7406175191aa5542f0578a6371e8`.
The current uncommitted candidate changes frontend.py, megamoe_kernel.py and
epilogue.py (+155 net lines) for exact post-tail FP32 reduction. Source review
and scoped mypy/Ruff hooks pass. The first native batch (original 17007) is
closed: both False controls compiled with byte-exact SASS against the saved
controls (5480/6192 instructions, REG96, 640 threads, zero stack/local memory).
All three True captures failed before launch because dynamic combine-buffer
strides hid the alignment required by 128-bit BF16 loads. Closure a36dcb1a
preserves the failed exit and source094e; no GPU numerical or timing result is
claimed. The narrow True-only static-stride descriptor correction passes
scoped hooks and is now frozen as source7b87bd03 / manifest d3aa00b6 under
frozen-stride-fix. Retry 75318 passes all three True captures in 19.15 s:
REG96/640 threads, zero stack/local memory, unchanged shared-memory allocations.
Actual CPU/fake descriptor parity passes for static combine/scores and dynamic
output n=0/n=3. Closure e8b4e70e confirms source7b87/native06752caf and idle.
Independent native ordering/register review passes: the dispatch-role reachable
tail stays below its 64-register limit, final barrier follows the peer drains,
and dynamic-n addressing/ordered FP32 math/final BF16 store are correct.
The reviewed test patch ccbde4dc is now applied in primary (+90 net lines in
three existing test files); scoped hooks pass. Existing products add ordered
FP32, top-k boundaries, graph replay, same-allocation changing-n and empty-source
graph coverage. Test-augmented source0bf9 / manifest5bfc passes 18 EP1 cases,
four EP2 graph cases per rank, and five seven-round routing calls per rank.
Each source/native/idle closure passes. Original44195 timings are 62.851,
35.461 and 41.670 seconds respectively. Original80523 is running one additional
H2048/I256/n512 reference call per rank to cover more than one reduction-loop
iteration. Full14 True performance follows that result; no timing claim yet.
The retained
readiness extension requires the FC1-ready
pointer that its sole caller always supplies, removing 21 lines of optional
state/branch plumbing. Both live peeks and field/value serialization order are
preserved. The normalized AST matches the original non-None specialization;
scoped and commit hooks pass. No fresh GPU, native or performance run is claimed
for this source-only specialization. The proposed/retained file is
`custom_ext.py` SHA a4f690c0 under `candidates/w4a16_custom_ext_required_ready`.

Preceding commit `c8155c6f23cc8374912019810fff8fa10ed3b056`, frozen source
`c8f48f4434a8cb9378fe65e588d15923a8821c32bd5a13a9307636131b5d95da`,
inlines the owned autotuner's single-use protocol/callback plumbing, removing
32 host-only lines. Existing AUTO lifecycle validation passed on node15:
two EP1 cases (28.27 s), one EP2 case per rank (27.27 s). Original 18872 and
fetch 13061 passed; final closure dfb01a81 confirms source c8f48f44,
native 06752caf and idle. No performance or standalone native replay.
Those tests remain attributed to c815/source c8f48f44, not the later readiness
cleanup. Combined implementation reduction is **919 net lines**: 866 earlier,
32 autotune and 21 readiness. Each cohort retains its original attribution.

**Published performance:** root published/read back PR5019 body 12244235 at draft
head `d6f8502b7f69da64e78641203917186280d01ebb`. One same-node split full14 run
(711.024306 s) on promoted eb73 pairs with the completed F4 Mega full14 run
(423.277836 s) on source996 using the exactly equivalent ordered F4 subset.
Both saved readers pass 14 rows/1,400 samples, with 112 selections per arm;
Mega has 56 candidate entries. Source/native/idle closures pass. Over 8–8192,
geometric split/Mega is 1.142387284× (12.464012% lower Mega latency), all 11 rows
favor Mega. Only T1 is slower across all 14. No row substitution, Mega replay,
or statistical-confidence claim. `FINAL_TABLE.{json,md}` is under
`candidates/w4a16_publication_split_refresh/recovery0911b/`.

**Current live PR body:** root published and read back exact body
`6489d8406b5c3841963b91ca56383267d0fedd69f9668720fd605f801528cf42`
on draft head `21fd7ce48b0a7406175191aa5542f0578a6371e8`.
`PR_BODY.md` includes both cleanup commits and total 919. Its complete Final
section stays byte-exact to body 12244235; all timing remains attributed to
measured source996/promoted d6. `PR-fixed-f4-published.json` preserves the earlier
F4 publication event and its original head.

**Current scope:** iteration_prep owns the freeze/install and five native captures
for the exact tail candidate, based on actual primary above 21fd. False controls
retain the old path; enabled N64/direct, N128/reuse and top-k32 cover the new
worker. No numerical or performance success is claimed yet. Source and barrier
review are in candidates/w4a16_exact_tail_reduce. The early weight/decode audit
confirms existing overlap with activation readiness; see
candidates/w4a16_pipeline_orchestration_review/EARLY_WEIGHT_DECODE_AUDIT.md.
The earlier N256 experiment and its separate revert remain history.

Every future performance sweep covers 1–8192 in one 14-row run; 1/2/4 remain
reporting-only for retention. Complete fixed-F4/F8 cold and matched hot evidence
is at `logs/cu132-fixed-f4-vs-f8-auto14-comparison-001/README.md`; manual F8 remains
supported while the public catalog uses F4.

The following notes preserve the preceding experiments and transitions.

**Current decision:** the user judged the N256 gain too small and requested a
commit followed by a separate revert. Experiment commit
`4db0979cff9adfe7553b5ab0fcb066a41a360616` preserves the five-file implementation;
revert `4733b060227ec8cba05c4facb2b1d65dde116225` restores the complete tree exactly
to `a26dc8b88eae499b90c02b0d9869b90887b81812` (source996, eight tactics).
Both commits are pushed to the existing draft PR. No extra tests or timing
are needed for the byte-exact restoration. The Final performance table stays
unchanged, and no publication split run was launched. Remote source restoration
from5069 to996 is complete: stage72991/install88612/fetch94865 all pass,
closure73c97a62 confirms source996/native47f and idle node15. No GPU replay.

Every future performance sweep now covers1–8192 in one14-row run;1/2/4 remain reporting-only for retention.
Unselected rows with identical native code are treated as measurement variation,
not as evidence for or against a new tactic. RefinedN256 wins4096 hot ranking
444.0 versus446.7us (~0.60%); at8192 it loses765.0 versus730.4us (+4.74%).
The8192 cold-forward result is0.796246ms with oldN128/F4/reuse selected; there is
no8192 cold BEFORE. Saved checks pass (proof50b9d784/resulta9e677c8), with original
98.673429s run/closure/fetch all successful. Both failed singleton-reader
attempts are preserved; no GPU run was repeated. The user chose not to retain
the small4096 improvement. The N256/K128 idea was stopped before any edits.

**Active experiment:** fixed flag_batch4 versus8 on restoredsource996. Each
arm tunes the remaining N64/N128 × direct/reused-return product (four choices),
with separate fresh caches, the same100-sample CUPTI metric, and one full14-row
1–8192 sweep. F4 completed all14 rows in423.277836s (original17417, closure85112,
fetch86077 all zero); its saved reader runs locally while fixedF8 original39394
uses fresh arm caches on the idle-checked same source/node. No production edit
or split run; compare full cold-forward latency and saved hot scores to assess
retaining this axis.

The following notes preserve the completed experiment and earlier validation;
their unpromoted/active wording describes earlier points in the investigation.

Draft PR5019: https://github.com/flashinfer-ai/flashinfer/pull/5019
Latest pushed commit `a26dc8b88eae499b90c02b0d9869b90887b81812` restores the
useful `_autotune_winner` field exactly to its pre-cleanup backend implementation;
the benchmark remains unchanged. Total cleanup now removes866 net implementation
lines across9files fromdde36ec. Hooks pass. Retained source99681e83 / manifest
ca4ecbbc is in `candidates/w4a16_implementation_cleanup/frozen-retained-winner`.
The completed native3/host80+1skip/EP142/EP225perrank/M1282perrank validation
belongs to a8b5a47cd/sourceeb9cc, whose device code is unchanged by the restoration.

The old-node baseline attempts below have no completed result. Attempt001 failed helper catalog
admission before launching;002 exposed the removed winner field after first-row
tuning, with zero completed rows. Temporary benchmark-only source d3acae fixed
reporting for003, but the devbox disappeared during the run (remote termination137,
missing terminal marker). No rows or source/native/idle closure were recovered.
Keep these failed/interrupted runs; they are not performance evidence.

Replacement `fi-w4a16-mega-0911b` is ready on c2/hu-pdx-15 with eight B300 GPUs, using explicit
`nvcr.io/nvidia/pytorch:26.05-py3`, the newest CUDA13.2 release confirmed from the
live NGC catalog and NVIDIA26.08 matrix. Driver590.48.01; UUIDs and idle state recorded. Sole remote executor owns bootstrap and
has completed published retained996 as the whole Mega-only AUTO13 BEFORE:
570.176644s,13rows/104compiled/104rankings/1300samples, true exit0 and source/native/
GPU-idle closure1f714039. Saved reader passed; proofa419b6e2/result9bc538d7 under
`logs/cu132-retained996-default-direct-auto-reconstruction-001`. `_autotune_winner`
reporting is validated across all13rows. N256 native and numerical validation
are complete; the full AUTO12 AFTER is running as detailed below.
No split rerun. The PR Final table retains its complete measured shared-c8 source.

The user requested substantial established pipeline/orchestration patterns instead
of marginal lifetime tuning. Source comparison is in
`candidates/w4a16_pipeline_orchestration_review/README.md`.
The first candidate adds M256/N256 routed-token tiles: one256-column accumulator
plus two128-column decoded stages. Five WGs/two decoder WGs remain fixed. Native4
completed0 in18.914s: N256 direct/reuse actualACC1/raw2/B2/D2/226688B/REG96/640/
STACK0/LOCAL0; N64/N128 exact native encodings/schedules5480/6192 match controls.
Independent detailed reviewea10972d passes fixed ACC slot/phase, scratch bounds,
release order and16 direct pointer registers. Numerical24rankcalls pass; graph
2cases/rank passes. Combined validatione1b7c493 is bound to source59bbe/node15/
actual native47f6150f and final source/native/idle closure54cf7daf.

Primary has five uncommitted N256 files: three implementation files, the
autotune product expanded8→12 (old8order retained), and one existing geometry
test parameter. Source50fa/manifesta60a passes added-test2cases/rank, followed
by complete AUTO12 original15885/closure84886/fetch43182 and saved reader/
comparator. Run802.144196s,13rows/156rankings/104selected+winners/1300samples,
source50/native47f/idle closureb0eb661e. Completiond32350a3; whole proof3b660010/
resulte443f36d. [Full table](logs/cu132-n256-acc1-vs-retained996-comparison-001/README.md).

**Hold unpromoted:** N256 selected0/13. Versus whole retained996,8–4096 GM
latency−0.395944%,5/10lower; selected N64/N128 native code is unchanged, so this
is not demonstrated N256 improvement. Best N256 hot score is1.67% behind the
winner at4096, but17.91–41.02% behind for8–2048. No new current best or split
publication run. PR Final table retains its complete same-node129 sources.

The next local draft narrows activation TMA payload for partial N256 work while
preserving the fixed B ring and dynamic MMA contract; see
`candidates/w4a16_pipeline_orchestration_review/ACTIVATION_WIDTH_DESIGN.md`.
The one-file loader refinement is ported to primary and passes scoped hooks.
First native attempt64 failed a raw shape-nesting assertion; a15 corrected it
to logical size but exposed a host-IR object used inside the kernel. Both
failures are closed with no GPU work. The final region fix passes the half-MMA
object explicitly into kernel/helpers (None for N64/N128), avoiding extra state.

Current source50696104 / manifest32424e16, kernel4ab7b2bf is installed. Batched
install/preflight/native4 original6380 passes; native18.791719s, closureddb46134,
source5069/native47f/idle. N256 emits6744/6728instructions (+128 each), keeps
REG96/640/STACK0/LOCAL0/SMEM226688/raw2/B2/D2/ACC1. N64/N128 are exact native
controls5480/6192. Root/direct and independent/reuse reviews pass correct
131072/65536 full/half transactions, fixed K-plane offsets95616/112000/128384/
144768, stage<<16, global tile_idx*256 and correct two-CTA starts; no new
per-K runtime choice. All28 numerical calls and28 actual compiled objects
passed in original20871. The batched inline parent caused a false positive in
the idle checker, then standalone closure5290 passed (189117f3). Graph upload
82373 failed before launch on a missing helper directory; after mkdir, actual
graph4471 passed2cases/rank in27.920617s, executione2b20d1f/closure3d7d0104.
No numerical replay or weakened guard; all failures preserved separately.

AUTO12 admissionbaf01431 and exact bindingbea1c36f are sealed. Final runtime
stage36832 (69b0660a) passed. Full13 AFTER original75059 completed in815.607396s
as `cu132-n256-activation-width-default-auto13-direct-001`, with closure8002,
proofb7701365/resultd3161f78 and comparison4a09b39c. All13rows/156rankings/
104selected+winners/1300samples pass. N256 wins at4096 only (F4/reuse).
Over8–4096, latency GM is+0.199263% versus immediate50 (4/10 lower), and
−0.197470% versus retained996 (3/10 lower). At4096: .463187→.458531ms versus50,
but retained996 is .457218ms. No broad cold-forward improvement is established.
Best N256 hot scores improve across all13 rows by1.683–4.929%; at4096,
451.6→444.0us versus the same-run best old geometry446.7us. These ranking
scores have a different timing/cache boundary from the cold-forward metric.
Source stays fixed with no competing GPU/compiler workload. Current28-call
numerics cover long-K258routes→[256,2] and partial66/128/130/194; changing257
is capacity, not514 observed routes.


Whole50 is the refinement BEFORE; whole996 is the retained control. Keep all
13rows, excluding1/2/4 only from retention. The user now also includes8192:
one separate AUTO12 point completed as original41480 in98.673429s, with
closure99825/fetch37080 true0. Its saved-reader singleton admission needs a
local repair; no benchmark replay. There is no8192 cold BEFORE, so compare
the selected tactic with old-geometry hot scores within this run and report
the cold latency separately. The candidate is uncommitted; PR
Final performance remains unchanged. Reuse saved full BEFORE runs without
new baseline or split timing.

## Historical development notes

**Preceding retained dispatch overlap/compact rank selection (Entry092).**
Commit `2699213f62b57dafccec5f8beeed9ef3fee58288` contains tested source
`71a1b68888f3d1d114e82c28489fc141037d6ab6214472790fa71a6de5300db8`,
manifest81193dfc. All1,583 commit blobs match the frozen source; applicable
pre-commit and commit hooks passed, including mypy/Ruff; publication was clean.
This combines the previously unpublished Entry085–091 dispatch refinements with
compact rank selection and its5/17-source test round. Their individual historical
mixed results remain recorded below; the retained decision uses the whole chain.

Native3 review21d8ea76 passes with1,016 fewer instructions per fixture versus
d788, unchanged REG96/640/STACK0/LOCAL0, stages and protected transport operations.
Numerical39884/closure52453/fetch21340 passes14/38, summary5f12349f and
closureb4325613. The new uneven-source round is observed in both standard
geometries/return modes. FullAUTO69639/closure81390/fetch65471 exited0 in537.484839s;
reader/comparator each passed once,13rows/104compiled/104winners/1300samples.
Whole proofae178216/result94e1a8c9/closure1d61d0eb/comparisonb41024cf/completion031840b4.

Over8–4096, −0.621516% latency GM vsd788 (7/10 lower), and −0.855141% versus
fresh same-build retained61ee (7/10 lower). Higher rows against61ee are512+1.174%,
2048+.067% and4096+.612%. Root retains modest improvement plus simpler dispatch;
there is no all-rows or large isolated speedup claim. [Complete tables](logs/cu132-recovery0911a-dispatch-rank-peeling-loop-vs-current-and-retained-comparison-001/README.md).

**Completed publication step:** one split-only full1–4096 CUPTI/AUTO sweep on
0911a/hu-pdx-129 provides the PR Final split column; whole Mega94e1a8c9 is reused.
Command0f7ca1ec, stage6afc488d and saved reader3ce4de69 retain the established
output/source/native/idle/exit envelope. No new Mega, numerical or profiling run.
The old hu-pdx-115 split column must not be paired with these current Mega rows.
Split58069 completed all13 with underlying returncode0 in632.989829s. Its wrapper
returned1 only at strict post-cache closure: first split use added54 native/cache
files and changed one diagnostic log. Afterinventoryb5866755/integrity65aad148
confirms every old85d7 non-log entry remains byte-exact, with0missing/0changed.
No timing rerun was performed. Expanded closure88009/fetch87983 passed
f4145df3; the saved reader ran once and passed13 rows/104tactics/1300samples,
proofb8d3b2b1. Independent inventory/table reviewb3767051 confirms additions only.
The published table uses all13 exact six-decimal medians and four-decimal ratios;
the shared-weight split reproduction bridge is syntax-checked, not separately run.

**Entry093 complete, held: late scratch READ wait.** Frozen d1849fe4 passed
native3 and numerical14/38. Full AUTO84724/closure4538/fetch32319 completed0
in536.463376s. Reader/comparator passed once: proof52c95075/resulte51c4070,
closureafc1b269/comparison1e761801. Over8–4096 it is +0.444494% versus published
71a1 (4/10 lower; T32 +3.044%). It is an unpromoted refinement base, not a new
best. [Complete table](logs/cu132-recovery0911a-dispatch-read-wait-before-overwrite-vs-current-and-retained-comparison-001/README.md).

**Retained Entry094: remove the nonempty rank-round guard.** Primary kernel and
frozen source600cff5f/manifestc1b1f37a/transport55650c3c remove the remaining
`num_active_ranks > 0` wrapper and impossible empty fallback. A valid residual
slot remains below the sum of remaining counts after each failed positive
rank-peeling round, so every reached round is nonempty. Both the old unrolled
mapper and current compact loop already skip later work after selection.
Native3 passes: N64/F4 4456→4456, N128/F8 5168→5128, F1 4416→4408;
REG96/640/LOCAL0, stages, publication and overwrite boundaries unchanged.
Independent review75e604c8; native closure0a9bf5fd. Numerical10219/closure75479/
fetch64930 all0,14/38, summary67515ae8/closurea03581c1. Full AUTO70617/closure41532/fetch67269 passed0 in537.570946s; one reader/comparator
passed13rows/104compiled/104winners/1300samples. Proofa48e0966/resulte862342d,
closure9030627a/comparisonef998a5c. Over8–4096,−1.119975% vs whole d184 (6/10
lower),−0.680459% vs whole published71a1 (5/10 lower); largest higher rows32
+2.685%,128+2.264%. Retain modest improvement and simpler code. Root committed
597b797be and pushed; all1,583 commit blobs match600c. That completed performance source contains oldtest5675 and excludes cleanup below.

**Test and API cleanup: runtime fixture correction512c now validating.** All
five PR-added W4A16 test files are folded into eight existing suites with explicit
W4A4/W4A16 mode products and shared numerical references. Private/cache/AST tests
are removed. The added public weight keyword-only restrictions are removed;
shared shim/autotune.py and W4A4 weights.py match PR-base bytes exactly. Collective
graph timing lives in the owned W4A16 autotuner, and its private shared exports
are removed. Static syntax, Ruff, mypy and changed-file hooks pass; local test
collection is blocked by missing dependencies, not claimed a runtime pass.
Combined actual source6617e0e9/manifestf646a085/deltad4a64480/stagef1379701
has1,578 full paths/354 required,13 modifications/five deletions. All changed-file
hooks pass. Stage40511/install79500/wrapper-stage94542 passed; host18965 active.
Host:80 unique passes,1 unrelated missingDeepGEMM skip. Initial EP1:37passed,
5 failures before kernel launch because manual W4A16 fixtures lacked a process
group under MEGA_NO_DIST. Shared session NCCL fixture fixes two test files only;
new actualsource512cc1b3/manifest83c4f83a/deltadd424417/stagead6d6116. The existing
sessionfinish owns teardown; existingPG must be world1/rank0/NCCL. All oracle,
tolerance and production bodies remain unchanged. Fixed EP1 original47565 passed7/7 with closure; together with35 unchanged
passes this gives42 uniqueEP1passes. EP2 original54162 was stopped after
882.623355 seconds with one completed item per rank and both GPUs busy. It is
incomplete, not a pass. Both workers exited on SIGTERM; original torchrun and
wrapper exited 1. Source/native/GPU-idle closure e7a3d66b passes. Two bounded
diagnostics identified a rank-1 compile failure: a valid contiguous FP32 expert
scale slice is offset by eight bytes, but the frontend assumed 16-byte alignment.
Collective freeing in the exception path hid the original error. Both diagnostics
timed out as bounded and closed with source/native/GPU-idle checks.
Reviewed fix414b uses four-byte alignment for scalar alpha descriptors only,
mirrors the shared frontends' direct compile call, and keeps both scale tensors
as expert-shard views in the existing EP2 helper. Hooks pass; production fix is
commit f22a18d21. Final full EP2 retry95790 passes 25 cases per rank, no failures
or skips, in185.208415 seconds; source/native/GPU-idle closure1579b52e passes.
Test commitffb6adc5c removes five files and extends eight existing suites, net
1,491 fewer test lines. API cleanup, scalar fix and test commits are pushed.
Current native3 original61514 has returned0 for all three cases; downloaded
evidence/resource review is pending before fresh owned AUTO. Native descriptors
now bind alpha4 explicitly through the reviewed sibling capture adapter.
Production scope cleanup is commit e6ca01d01db18392d27911ce1b85cb5da82259cf;
scalar alignment is f22a18d21 and tests are ffb6adc5c. All are now pushed.

The user-directed comparison takes priority over the held [two-pending pool-write proposal](candidates/w4a16_dispatch_two_pending_writes/README.md)
changes only pre-store F>1 fullwait0→1. READ0 still protects scratch reuse and
full publication/tail drains remain. No primary or remote trial has started.

**Entry091 redundant-exhaustion guards: complete, unpromoted refinement base.**
Source d78808f4/manifestb85f584c/transportb848151a removes three checks implied by
the received-total/nonnegative-prefix invariant. Native3 review2128140c passes:
16/8/16 fewer instructions, unchanged resources/stages/protected operations;
closure2c1c2f8f. Numerical50588/closure91690/fetch39662 passes14/38, summary71ab3463
and closure21a58573. FullAUTO94214/closure72065/fetch67698 exited0 in565.251131s.
One reader/comparator pass confirms13rows/104compiled/104winners/1300samples.
Proofd094203c/result59f0a00d/closure70a7262c/comparisonfae75769/completion8156b128.

Over8–4096, +0.988840% latency GM vs64a8 (3/10 lower), and −0.235087% versus
fresh retained61ee (7/10 lower). T256 is +8.902% versus64a8 and +6.562% versus
61ee; root holds chain promotion and continues general dispatch cleanup.
[Complete before/after tables](logs/cu132-recovery0911a-dispatch-total-bound-no-exhaustion-checks-vs-current-and-retained-comparison-001/README.md).
Published source/head and PR Final table remain unchanged; no split refresh.

The support-cache backup is downloaded locally (archive09d57636,2,882,586bytes,
receipt459be14b), with restore_validated:false. The active85d7 support inventory
remains byte-exact across the completed same-build controls and trial.

**Received-total chain (Entry090): complete, unpromoted refinement base.**
AUTO79283/closure88226/fetch86811 exited0 in562.989909s. One reader/comparator pass
validates13rows/104compiled/104winners/1300samples. Whole proofa4ab91d1,
result5dffdb7a, closure8fa28b04 and comparisondc097500. Over8–4096,−1.211942%
latency GM versus fresh61ee,6/10 lower; T128 regresses5.575% on the same tactic.
Root holds chain promotion and continues general cleanup. All13+.021177%;1/2/4
remain excluded only from retention. [Full same-build table](logs/cu132-recovery0911a-dispatch-total-bound-vs-same-build-retained-comparison-001/README.md).
This is the complete transport chain versus retained61ee, not an isolated total
bound measurement. Published source remains61ee/773c9b and PR tables are unchanged.

**Entry090 source and recovery history.**
[Source proposal](candidates/w4a16_dispatch_total_bound/README.md), patch42dbb68c,
sums each lane's already-cached count list, performs one warp add reduction,
and replaces the outer cursor-exhaustion guard. Valid prefix/rank mapping is
unchanged; idle/final suffix scans are avoided. It inherits the existing Int32
prefix domain and preserves phase, publication/tail and return handoff. No
workspace, public knob or extra per-token branch.
Root applied/froze the exact proposal in the primary checkout. Source
`64a81ed859ecf81c6e91dd8816cd2eceb1be5d397303faca84dcab58376a6e5a`,
manifest `1fd5d00d9a310729b467803e86d67dc747ea5aaf6fff032eb20e4f50638f771d`,
deltaef53c7c1/stagebe1f775b/transport199a9c28. Stage17622/install75893,
preflight21108/runtime59224/fetch96527+62331 passed. Native2704 and all downloads passed;
unchanged parallel-driver wall13.245422677s. Native3 review PASS: one startup full-mask add reduction, new initial/steady
loop guards, unchanged valid mapping and tail. N64F4/F1+8 instructions, N128F8
unchanged; resources/stages exact and protected PTX sequences preserved modulo
register renaming. Closure13345/fetch50440 passedf5745a41. Numerical14/38 is
completed76559/closure99372/fetch61980,14/38 PASS with closure39fa3e21.
FullAUTO5672 was interrupted when fi-w4a16-mega-0910b disappeared. Outer exit1,
remote wrapper137, no end marker; underlying benchmark exit and completed-row
boundary remain unknown. No complete performance result or comparator exists.
Native3 and numerical14/38 results remain saved locally. Receipt
[cb7a1ef0](candidates/w4a16_dispatch_total_bound/execution/auto-interruption001.json).
Managed listing40979 exited0 and showed no ziangli/c2 devboxes or jobs.

Replacement fi-w4a16-mega-0911a is ready on the same hu-pdx-129 and all eight
original GPU UUIDs. The loaded compiler/CUDA/CuTe/Torch/NCCL/profiler stack matches
in all13 compared fields. Explicit image remains26.05-py3. Exact64a8 was restored;
source/native/idle closure63902 passed. Fresh support builds took110.05s for FP4
quantization and21.11s for routing. Their .so hashes differ from0910b despite
matching source/compiler and identical sizes; exact old bytes are not archived.
No code-equivalence or native-byte-continuity claim is made.

Fresh published61ee control40802 is complete: original40802/closure7708/fetch22112
all exited0. One saved-reader pass validates13rows/104compiled/104winner records/
1300samples; wall565.2958466s. Whole proof
`29b1e822539f2a9d4037fc8da2c806cc1e49cba0f2cafd7a3d7219217e35537c`,
result `a0e022f96b26de51ed77c0b05f8c9bbd4231e4264ed558fdc8222c9354f9378a`,
closure8c93898b, actualpreflight53670902 and new85d7 native inventory.
[Fresh control](logs/cu132-recovery0911a-retained61ee-default-direct-auto-reconstruction-001/).

Exact64a8 fullAUTO79283 completed
cu132-recovery0911a-dispatch-total-bound-default-auto13-direct-001,
command4283e5e7, actualpreflight5268b5e3 and source/native/idle21183. This compares
the combined unpromoted transport chain against the whole retained61ee control. Old0345 remains historical
context; its mixed-build microdifference cannot isolate the total-bound effect.
Later trials reuse the new same-build controls. iteration_prep alone restores
remote61ee/64a8 through guarded existing installers and executes these sweeps;
primary has advanced to Entry091 above. No numerical/native3/profiler/split rerun was selected for recovery64a8.
The three-guard removal is now active in Entry091; compact rank peeling and
delayed READ wait remain held. All preserve current GEMM stages.


**Elected payload writer (Entry089): complete, unpromoted refinement base.**
Source03459447/manifestcdaeaf7d/transport41bf279e; scalar weightSTG is within the
existing payload/provenance election after commit. Native3 confirms early
unpredicated LDG and first mainline wb5 result wait at the delayedSTG; divergent
recovery0x24 remains qualified. N64F4/F1 instructions unchanged5488/5440;
N128F8−8→6192. Resources/stages exactREG96/640/LOCAL0/STACK0. Parallel native48943
exited0, measured driver wall17.369935244s; no earlier comparative wall exists.
Numerical18123/closure68365/fetch62416 passed14/38, summary78fffbfc and
closure9c9b5eba. All38 retain two decode groups/REG96/640/LOCAL0.

AUTO97992/closure1751/fetch22744 exited0 in568.126318033s. Source/native/idle
closure8236616b, reconstructionceab13ca/result46f0535a and comparison31923269
passed once,13rows/104compiled+winner records/1300samples. Over8–4096,
**−1.236098% vs4bf (7/10 lower)** and **+.134758% vs retained61ee (6/10 lower)**.
All13−.201608%/+.902145%. [Complete tables](logs/cu132-recovery0910b-dispatch-weight-payload-issuer-vs-current-and-retained-comparison-001/README.md).
Root holds chain promotion and uses this complete0345 run as Entry090 BEFORE;
retained61ee7b23defb/effe5a0d remains the separate same-node control. No split,
control rerun, PR/body update or restoration is selected. Integration remains
interrupted; iteration_prep is sole remote/execution owner.

**Post-counter warp barrier deletion (Entry088): completed, unpromoted.**
Source4bfbe75b/manifestae9725dd/transport8eefb5eb removed only the sync after
constant-phase0 tracker accumulation. Full-mask same-issuer scratch reuse,
prepublication/tail syncs, full/READ waits and final handoff remain. Election is
not treated as a memory fence. Native3 passed with eight fewer instructions per
case, unchanged protected protocol and REG96/640/LOCAL0. Numerical94762,
closure46487 and fetch30696 passed14/38; summary7f0fd26a/closureb1cb2aa5.

FullAUTO66788/closure48848/fetch74176 exited0 in564.711888067s. Source/native/
idle closure9efcbda3, reconstruction93dad2ac/resultdc8f7719 and comparison40d4faa7
passed once:13 rows,104 compiled and winner records,1300 samples. Over8–4096,
latency GM **+.863031% vs b9db (2/10 lower)** and **+1.388013% vs retained61ee
(2/10 lower)**. All13+1.189782%/+1.105982%. Root holds promotion and retains4bf
only as the next trial base. [Complete tables](logs/cu132-recovery0910b-dispatch-post-flag-sync-vs-current-and-retained-comparison-001/README.md).
No PR/body/split update or benchmark repeat. Native elapsed was not captured
because `/usr/bin/time` is absent; next capture uses a tiny stdlib wrapper.

**Preceding routing-weight trial b9db: complete, held for refinement.**
Source `b9db4c19`, manifest `b9e68860`, transport `0cbc2af8`. Native3 safety/
resource review [ccc21e98](candidates/w4a16_dispatch_weight_after_payload/execution/NATIVE_REVIEW.md)
passes, with +24/+32/+24 instructions and unchanged config/stages/REG96/640/
STACK0/LOCAL0. The full-warp mainline defers the routing LDG's scoreboard-5
wait until its post-payload STG; generic divergent-election recovery waits
earlier. No all-CFG-path overlap claim. Numerical99535/closure8994/fetch15946
passed14/38; closure `7a931df7`, summary `b338c0ec`.

The underlying benchmark subprocess exited0 after568.609844s (23:12:45 to
23:22:13 UTC). Root read-only status26099 confirmed all13 completed rows;
iteration_prep recovered closure/download/reader/comparison without a new run.
Original outer launcher session ID/exit are unknown and remain explicitly null;
they are not replaced with the underlying subprocess exit. Saved source/native/
idle closure `c52c7bcf` and single reader/comparator pass13rows/104compiled+
winner records/1300samples. Proof
`4a7394fcef68e198df7e594389cfe15c76e2ea79a44b3a403a82d7caaef2dd28`,
result `a88fc9bafb7e24cd8c78f958e3b8f00eb6977f5f08fe31936be39f246d59f1ee`.

Over8–4096, latency GM is **+.069733% vs7da (6/10 lower)** and
**+.520489% vs retained61ee (5/10 lower)**. All13 changes are−.771745% and
−.082815%, respectively;1/2/4 remain excluded only from retention.
[Complete tables](logs/cu132-recovery0910b-dispatch-weight-after-payload-vs-current-and-retained-comparison-001/README.md).
Root holds promotion and keeps b9db as the refinement base. No PR/body/split
update, benchmark repeat or validator repeat occurred.

**Preceding two-sync trial7da: complete; held as refinement base.**
Native3 removes24 instructions each with required ordering and unchanged
resources; review64a62e13 and closure010f528e pass. Numerical61309 passes14/38,
closure0adf967b/summaryf116c71d. FullAUTO43592 exits0 in564.903732s;
closure57231/fetch93821 exit0, source/native/idle closuref6e603a8 passes.
Proof6c3458a39fdf7f0dc2362252eac897ed7dbcd6029abc4514f7c1e728dfec2662,
resultacb3ef49bfa00fcef45fe31cd7cfb332075d2bd5212622b4a29732991066c1e5.
All13 rows/104 compiled and winner records/1300 samples pass once, all104
REG96/640/LOCAL0. Over8–4096,−1.158901% vs precedingb407 (6/10 lower),
but+.450442% vs retained61ee (5/10 lower). Root holds promotion of the
combined transport change and proceeds to routing-weight overlap without
restoring the source between related trials. [Complete tables](logs/cu132-recovery0910b-dispatch-pull-barriers-vs-b407-and-retained61ee-comparison-001/README.md).

**Preceding b407 result: not promoted alone; preserved as refinement base.**
Native3 passed with5496→5496,6208→6200,5472→5448 instructions and unchanged
resources/protected compute operations (review8ef37e77). Numerical14/38
passed, all38 REG96/640/LOCAL0/two decode, including T1777/W592 full batches,
partial tails and zero destination. FullAUTO22056 completed in567.827s:
proofadba763d8dd174172c8fa29c0663551846c48949ce7ffd8ad47875dd53d43045,
resultad27222221c96b27ccbb6ba6ccb53092a9379c410f13dd5c5216ec4fbda62ff3,
closure58dc906d confirms b407/nativef13fed/idle.13 rows/104 records/1300samples
pass once. Versus retained61ee,8+ latencyGM+1.628212%,3/10lower; no standalone
promotion or PR update. [Full table](logs/cu132-recovery0910b-dispatch-read-wait-f1-elect-vs-current-and-whole-best-comparison-001/README.md).
Archives README69ff27a8/VALIDATIONab7545e5/retention10ddbaaf preserve this
boundary and corrected completionada47c95 (13 arrays×100 samples), with old
receipt retained. No source restoration between related trials.

The elected-weight-issuer candidate is now active above. Its held source proof
and execution handoff remain preserved in
[candidate notes](candidates/w4a16_dispatch_weight_payload_issuer/README.md).
A bounded [remaining-overlap audit](candidates/w4a16_remaining_transport_overlap_4bf.md)
found no additional credible per-token barrier deletion without changed scratch
ownership or added runtime state. It makes no throughput claim.

A separate source-only initialization cleanup is held in
`candidates/w4a16_dispatch_init_sync_coalesce/`: remove the first of two
initialization rendezvous separated only by independent register/metadata work.
Patch4fec9dbd/proofe181b51a, no runtime/source application. PTX has both syncs,
but final SASS has no explicit intervening WARPSYNC; effect may be nil.
Stage-policy auditf8bb7952 finds independently bound rings and full TMEM use,
with no credible fresh stage-only trial selected.

The selected parallel native3 driver064852df uses isolated per-case caches/logs
in `candidates/w4a16_parallel_native3/`; its actual time benefit is unmeasured.
One publication-time split-only adapter remains held in `candidates/w4a16_publication_split_refresh/` preserving the same
shared weight factory as Mega. Neither helper changes product code or timing
methodology. Split refresh is not GPU-queued. Saved native receipts do not
contain elapsed timestamps, so no measured parallel speedup is claimed. The
next native command will record elapsed time without recapturing a control.

**Latest retained/published change: local FC2 router wait specialization.**
Commit `773c9b0725f19500ffdd6bdd03c84f56f552dbc5`, source
`61ee217a17e0d83bb8f06e3cfba2fdd8025b7384c5c335f5a0a35d44ab72c65c`,
is pushed to the fork. Hooks passed, epilogue34dbafab remains tested bytes.
It removes the metadata-free reuse path's early peek/wait branch at compile
time, retaining the final full accumulator wait and direct metadata protection.
Native2 passed with16 fewer instructions each (5736→5720 /6224→6208), same
resources and protected synchronization. Numerical8/32 passed, closure50c7039a.
Full13/8/100 completed83872 in569.658s, all104 records/1300 samples valid:
proof7b23defbf4df776e3ac8fe86bdcfbe254e5536a5f04d08a342ebd12a6172b4c3,
resulteffe5a0d99f1fde5432b62b4938ae375ac11c9b31843e3380aa29212d9db0478.
Against fresh64126b65baf/825908b8,8+ GM−1.435173%,6/10lower; affected reuse
winners2048+.235% and4096−.653%. Retained as constexpr simplification with no
material affected-path regression, not an isolated causal aggregate speedup.
[Full table](logs/cu132-recovery0910b-fc2-local-router-wait-vs-current-and-whole-best-comparison-001/README.md).
PR readback remains OPEN/draft, head773c9b/body3bb7471f; validation is current
and every Final performance row remains exact. Historical115 split is not
paired with new129 Mega. [Archived decision](candidates/w4a16_fc2_local_router_wait/execution/retention.json).

Scheduler construction cleanup is retained/pushed as
`b8ecada440c4b81993abcadcbb36ad1642b19f5d`, source
`641c6fe875ea1a13ad6e5b194794d829bb7af0af4c373859edee621bf04360ba`.
Only its broadcast-pipeline factory/dead Python storage plumbing changes
(+14/−32); first atomic claim order is unchanged. Both entire N64/N128 SASS
files are byte-exact retained controls (5496/6032 instructions including all
PCs and scheduling words), with resources/descriptors/options exact. Native
reviewad8cc6e3 and closure28894955 confirm source641/nativef13fed/idle129.
Hooks including mypy/Ruff passed, tested bytes unchanged. No numerical or
performance sweep was rerun for this mechanical cleanup. PR remains draft;
body3cc265aa records the bounded validation and leaves all raw table rows exact.

Group1024 was not retained: full13/8/100 measured **+1.905248% latency GM over
8–4096,2/10lower**; all13+3.222286%,3/13lower. Native2 and targeted numerical8/8
passed. Catalog512 was restored locally/remotely before cleanup: receiptcf047b6e/
closure82955c7f, source3b425/nativef13fed/idle129. [Full table](logs/cu132-recovery0910b-group1024-vs-current-and-whole-best-comparison-001/README.md).
AUTO7354/closure39482/fetch50185 exited0, wall566.101s; proof9134a6ca/result94669d7b
validate13 rows/104 selected objects and rankings/1300 samples. Launcher-only
DNS and saved-reader count-field repairs preserve original failures; completed
GPU results and validators were not rerun. No group1024 publication.

The original BF16 input-transfer proposal, now refined above, was: use a source-read wait to permit scratch reuse during the previous
pool write, and fully drain that write before issuing another store or publishing
readiness. It requires native/resource/numerical/performance evidence. Final held proposal
is `candidates/w4a16_dispatch_read_wait_f1_elect/`, patchb04cec7a/tokencommd03984fc;
source reviewc102e047 passes; actual sourceb407 is frozen. F1 skips unnecessary inter-token/tail drains at
compile time; the existing full-mask election replaces one pre-store sync only.
Publication/tail memory-ordering syncs remain. Vendor files remain immutable;
an owned BF16 pull-only specialization reuses universal transport setup and tail.
Small-capacity flag pruning remains held source-only.

Raw6 was not retained: complete13/8/100 measured **+2.169545% latency GM over
8–4096, only1/10lower**, all13+2.673236%,2/13lower. Native2 and numerical8/32
passed, with generic actual fitting and no spills. N128 native was identical;
its4096 row still moved+2.36%, so the observed run difference is not wholly
attributed to the stage change. [Complete table](logs/cu132-recovery0910b-raw6-b3-s2-vs-current-and-whole-best-comparison-001/README.md).
The primary kernel is restored byte-for-byte; remote restoration also closed
with receiptb0dd456c/closure886ff415, retained3b425/nativef13fed and idle GPUs.
No commit, push or PR body change was made for raw6.

The startup-claim trial was not retained: complete13/8/100 measured
**+2.768335% latency GM over8–4096, only1/10lower** against the whole current-node
control. Native2 and unchanged numerical8/32 passed, with correct intended
ordering and unchanged resources, but +24/+16 native instructions. All13 was
+2.553115%,2/13lower. [Complete table](logs/cu132-recovery0910b-startup-claim-vs-current-and-whole-best-comparison-001/README.md).
Primary startup files are restored byte-for-byte before applying raw6. Remote
restoration also passed: receipta1c7d59d/closured0bffb1d, unchanged nativef13fed,
GPU idle, no repeated tests/timing. No commit, push or PR body change for startup.

The direct-FC2 null-tracker trial passed native2 and numerical8/32, but the
complete same-node sweep measured+1.892538% latency GM over8–4096, only2/10lower.
Root did not retain it. The epilogue is restored locally and remotely to HEAD; guarded
restoration closurefd1a12e8 passed before startup staging. [Full comparison](logs/cu132-recovery0910b-fc2-null-tracker-vs-current-and-whole-best-comparison-001/README.md).
No commit or PR update was made for that trial.

Previous devbox0910a was reclaimed. Replacement0910b/request80106 is on a different
physical B300 node, hu-pdx-129; the loaded stack matches, with explicit image
`nvcr.io/nvidia/pytorch:26.05-py3`. The complete retained3b425 baseline on this node
is19a83070/e94d7f2f (568.944s), reused for the independent trials. Older host timings
remain historical and do not supply admission rows. Recovery evidence is in
[cuda132_recovery_0910b](candidates/cuda132_recovery_0910b/).

Communication-WG epilogue assistance remains held: current finite-ring and accumulator ownership provide no
clean mid-stream join after input pulls. Published checkpoint details follow.

**Pre-cleanup retained source:** `3b42507e7fd9c405c9e4112a0692942dc303c6d2a2cfd5268aeb57e67f72f186`.
Early raw-slot release is retained as a modest general scheduling change;
commit `ceb619b21b02fb9d6235edd3eed10ea06627ba51` is pushed to the fork.
All applicable hooks passed including mypy/Ruff; tested bytes are unchanged
and the publication checkout was clean. The two-file patch51944eca sits above
published cleanup commit `0f361bc04664c574c91f96ecff3c259b8d4fdb14`.
It preserves the shared split default completion order; only Mega returns the
packed-weight/SF slot before TMEM store completion, with decoded publication
still fenced. Native2 direct and unchanged numerical8/32 both modes passed,
preserving REG96/640/two decode WGs/LOCAL0. Full13/default8/AUTO100 completed
in590.424s: 13 rows,104 compiled/ranking records and1,300 samples.

Latency GM over8–4096 is **−0.424211% versus the complete retained3efa run**,
6/10 rows lower; all13 is−0.034425%,7/13 lower. Against the separate whole098c
best,8–4096 is+1.532273%,4/10 lower. Results are marginal and mixed; **no new
performance best is claimed**, and the published098c table stays unchanged.
The preceding completed run on0910a closed source3b425/native38a68 and
GPU/worker idle with0d54a5c7. [Decision and full tables](candidates/w4a16_raw_release_before_tmem_wait/execution/README.md)
and [Entry078 completion](w4a16_optimization_experiments.md#entry078--release-packed-weight-slots-before-tmem-store-completion)
preserve the evidence. The preceding five-line empty FC1 bulk-group deletion
remains retained as pure cleanup, not a speedup; [its decision](candidates/w4a16_fc1_empty_bulk_drain/execution/README.md)
and source3efa are now this trial's completed BEFORE.

Earlier removal and optimization chronology follows; its source pins describe
those completed checkpoints, not the current retained source.

Prior published removal commit is `8d7718c9a6c76e5722e1cf201395b0df538b081e`,
source `eb036705ebe71f940bf567c94fdcb78020a5fdc21bdeb3e7ea361cc1d140a09d`.
Nine files change (+69/−1162, net1,093 lines removed). The separate commit deletes
the two CLC modules and mode/config/queue/workspace/epilogue plumbing, inlines
the default kernel body, and removes only CLC-specific tests/docs. Its parent
16b7170fe retains the published CLC implementation for future reference.

[Removal validation](candidates/w4a16_clc_removal/execution/VALIDATION.md) closed:
135 host tests; both default native captures exact (5,504/6,032 instructions,
including encoded scheduling bits); eight EP2 rank tests/32 objects passed,
all REG96/640/two decode WGs/LOCAL0. Source/native/idle closure isd15d6575.
All commit hooks pass. No full timing sweep was rerun for the simplification.
[PR readback](logs/pr5019-clc-removal-after-body-edit-001.json) confirms OPEN/draft,
head8d7718c9a and bodyc4456a06; the whole Final performance section is unchanged.

The separate [FC2 barrier candidate](candidates/w4a16_fc2_nonterminal_barrier/README.md)
completed native/numerical/full AUTO validation but was **not retained**. The
[full before/after tables](logs/cu132-recovery0910a-fc2-nonterminal-barrier-independent-comparison-001/README.md)
show +0.573089% latency GM over8–4096 vs whole57e2,5/10 lower; +2.019088%
vs the separate whole098c best,4/10 lower. All13 secondary was−0.930005% vs57e2,
but the excluded small rows do not determine retention. Actual native lowering
was predicated as intended with no resource regression; all8/32 numerics passed.
The complete run contains13 rows/104 records/13×8 rankings/1,300 samples,
wall578.813s; result45f6f6ef/proof1cba9bae/comparisond6dd21d3/idle0079bbb4.
[Retention record](candidates/w4a16_fc2_nonterminal_barrier/execution/retention.json)
preserves the decision and unchanged artifacts. Primary and remote are restored to
8d7718/sourceeb036. Restoration closure12435a4c confirms exact source, unchanged
native38a68 and GPU/worker idle; receipt3f611edb records the one-file reversal.

The retained direct-epilogue full NCU capture is complete: original90579 exited0,
all eight T1024/N64/F4/S2/EP8 reports finalized after40 replay passes. The
[downloaded reports](profiles/direct-epi-0910a-ncu-full-t1024-001/)
are verified by size and SHA, with2,472 metric names/14 rendered sections per
report. Source/native/idle closure70ca8599 preserveseb036/db4a/native38a68;
idle clocks/power match the benchmark environment. Raw archive5d4c542a is
36,594,582 bytes. [PC/SASS exports](profiles/direct-epi-0910a-ncu-full-analysis/)
keep ranks separate: actual FC2 counter polling has zero samples on every rank;
the sole source-tagged rank7 sample is pointer setup. Large replay-induced
rank skew and first-work/communication waits preclude treating instrumented
sample fractions or durations as steady-state benchmark results.

FC1 completion batch1 remains held because this profile does not support its
readiness-delay hypothesis. Next source proposal is narrow default atomic
preclaim overlap: issue the next scalar claim before current work publication,
delay all result use until afterward, and preserve the original cluster
broadcast/consumer protocol. ptxas currently adds a result-consuming shuffle,
so native quality must establish an actual overlap window. The reviewed source is now applied in the primary checkout and frozen under
candidates/w4a16_atomic_preclaim/frozen: sourceca2328e9, manifest26697b53,
patchc4df1e4d, delta76ec1e05 and stagea459d0c1. Exactly two owned files change;
HEAD remains the separately published CLC removal8d7718. Independent source
review53ac9cd5 passed, but both native captures failed the intended overlap:
ptxas still inserts an immediate result-consuming shuffle before publication
(review4cd8de92). Resources remain REG96/640/STACK0/LOCAL0; source/native/idle
closure55ad3358 passed. No numerical or AUTO run was started forca2328.

Root applied the tiny INC refinement under candidates/w4a16_atomic_preclaim_inc:
source8336b16d, manifestf4504336, patch799c5383, deltafad2e88a, stage08995e6e.
Only the scheduler asm uses INC with limit0xffffffff in place of ADD1, preserving
old-value return and full u32 wraparound. Both native captures completed but
produce byte-exact ca2328 SASS, including scheduling bits; INC did not prevent
aggregation. Source/native/idle closurec1514c50 passed; numerical/AUTO remain
unstarted. The reviewed elect.sync refinement is applied and frozen under
candidates/w4a16_atomic_preclaim_elect/frozen: sourceef43bf0f, manifest31fa4fb2,
patchba51996a, deltab7c78f83, stage2a50fb99. Full-warp election carries only two
local scalars (old counter value and actual elected lane) to one delayed shuffle;
first/static/terminal behavior and serialized state remain unchanged.

Both ELECT native captures pass the intended ordering: claim precedes the
work-slot wait, and the first claim-result consumption follows publication and
the original cluster-slot acquire. N64 ATOMG28b0 → record commit29a0 → result
SHFL2a10; N128 ATOMG2870 → commit2960 → SHFL29d0. The result wait mask0x20
appears only at the delayed shuffle. Steady-claim aggregation is gone; padded
instructions decrease by8 per geometry (5,496/6,024), with unchanged
REG96/640/STACK0/LOCAL0/grid/stages/SMEM. Native closurea9444b31 passed.

The original eight EP2 numerical rank tests/32 compiled objects passed, all with
96 registers,640 threads,two decode WGs and zero local bytes; source/native/idle
closure0963a11b passed. Integration completed the full default13/catalog8/AUTO100 run
cu132-recovery0910a-atomic-preclaim-elect-default-auto13-direct-001, original56333
(true exit0;589.757506s). Result37d047c3/proof06da025a contains13 rows/104 selected
objects/13×8 rankings/1300 samples. Closure199f8f19 confirms exactef43/native38a68
and idle. The [whole-run tables](logs/cu132-recovery0910a-atomic-preclaim-elect-independent-comparison-001/README.md)
show **+2.379625% latency GM8–4096 vs57e2,3/10 lower**, and **+3.851597% vs the
separate098c best,2/10 lower**. The ELECT candidate is rejected despite correct
native overlap and passing numerics. Primary and remote are restored exactly to cleanHEAD8d/sourceeb036.
Restoration receiptbb47edf9 and closure561691e5 confirm the two-file reversal,
unchanged native38a68 and GPU/worker idle. No tests or timing are repeated for
restoration. The complete candidate and both failed native refinements remain
archived.1/2/4 are reported but excluded from retention; batch1 stays unrun.

The PR profiling section now includes the downloaded retained8d T1024/N64 full
NCU alongside historical056ce T4096 NCU and NSYS. Readback
logs/pr5019-profiling-after-body-edit-001.json verifies OPEN/draft/head8d and
bodyb4959ceb. Every byte outside Profiling scope, including Final performance,
is unchanged. The rejected ELECT trial is not included as PR performance.

The [tail-fence reorder](candidates/w4a16_epilogue_tail_fence_after_free/README.md)
completed native, numerical and full AUTO checks but was **rejected**. It kept
5,504/6,032 native instructions and unchanged resources, with the actual system
fence after deallocation and before the common tail. All eight numerical rank
tests / 32 objects passed. The complete AUTO run (original 61214, 586.984s) has
13 rows / 104 selected objects / 13×8 rankings / 1,300 samples; result `27aed5cb`,
proof `50bc733e`, closure `0c59b40b` confirm exact source `d88c` and idle GPUs.

[Full before/after tables](logs/cu132-recovery0910a-tail-fence-after-tmem-independent-comparison-001/README.md):
8–4096 latency GM is **2.023030% higher than whole57e2 (1/10 lower)** and
**3.489875% higher than separate whole098c (2/10 lower)**. Primary and remote were restored
to exact HEAD8d/source eb036. Receipt `4075d3d4` and closure `b9fdc28b` confirm
the one-file reversal, unchanged native inventory and idle GPUs.
No test or timing repeat is needed for restoration. The PR performance table
remains unchanged.

The [empty FC1 bulk-group cleanup](candidates/w4a16_fc1_empty_bulk_drain/execution/README.md)
is now **complete and retained as cleanup, with no speedup claim**. Patch
`1f90695c` deletes five epilogue lines (`6026bd7a` → `ee769bd0`); kernel5d6d and
all real BAR1/flag/TMEM/dispatch dependencies remain. Commit0f361bc0 contains
the exact measured source3efa, manifestf85d1a5d; all applicable hooks passed.
The fork push and live draft PR head0f361bc0 are confirmed.

Two direct native fixtures passed with unchanged REG96/640/two decode groups/
STACK0/LOCAL0 and dynamic shared200064/230784bytes. N64 has5496 instructions,
N1286032; each removes three executable instructions net. Unchanged numerical
8/32 across both geometries/return modes passed (completionff5aa8a6).
Full AUTO82856 exited0 in585.834477s:13 rows/104 objects/104 rankings/1300samples.
Proofe607b472/result353b1b64/comparisoncb37def2 and closure35532e29 record exact
source3efa/native38a68/GPU-worker idle. Retention-range GM is +0.519590% vs57e2
(3/10 lower), +1.964819% vs098c (4/10 lower); all13 is−0.751061%/+1.995430%.
These complete historical controls remain separate. Root retained the deletion
for simplification under user preference, not performance. Host135 remains
historical on8d; no baseline, host, split or profiling run was added. B4 remains
held after its prior completed negative trial; no new stage trial is proposed.

The in-flight task-terminal85a1 AUTO was cancelled at the user's request. Its
original process exited1 after SIGTERM at124.915s, with onlyT1/T2 complete. No
whole reconstruction, comparison or retention applies. [Cancellation closure](logs/cu132-recovery0909e-central-task-terminal-clc-auto13-direct-001-cancelled-idle.json)
SHA104fc649 preserves exact85a1/native38a68 and confirms no GPU apps/workers.
All CLC trials and held directions are archived, not future active work. Their
local candidates/logs remain; the removal commit's parent will retain the
published CLC implementation for future reference.

The whole default PR performance table remains owned098c, unchanged. The completed
cleanup comparison uses whole default57e2 as primary BEFORE, with owned098c as
the separate whole-best comparison. Both use complete saved columns, with no
CLC baseline, fresh baseline or split run.

Published5152 public CI: pre-commit and BuildDocs pass.
The GPU setup/matrix is skipped; [Test Results Summary](https://github.com/flashinfer-ai/flashinfer/actions/runs/34452838892/job/102792347308)
reports “CI skipped — pending authorization,” not an observed GPU-test failure.
No bot comment, label or CI run was requested; devbox validation continues.
The draft PR has no human review; bot workflow success is not kernel approval.

## Central implementation and default timing completed

W4A16 now lives at `flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/`, with
frontend, autotuning and device modules at one level. Generic vendor primitives
are reused through the existing public package/kernel_helpers boundary. The
verbatim vendor source/docs remain intact, with no extra src/shim layer or
compatibility redirects. Wrapper cleanup removes six forwarding methods and
an empty transpose subclass. Exactly two decode warpgroups and five total
remain; packed NVFP4 decodes to BF16 directly into TMEM, without materialized
BF16 weights. Shared-operand-release is rejected and excluded.

Completed on57e2: **139 host tests; five native captures/all11 role comparisons
exact in disassembly, encodings, configuration and resources; 11 rank tests/41
numerical objects passed with LOCAL0 throughout compute.** Native comparisons
are under [central execution](candidates/w4a16_central_refactor/execution/),
and numerical/source/native/idle [closure](logs/cu132-recovery0909e-central-numerical-full-001-idle.json)
is `b606e836`; [compact numerical result](candidates/w4a16_central_refactor/execution/numerical-result.json)
is `3af0c730`. No original numerical validator was rerun during closure.
Frozen manifest is `a0bd502a` under
[validation/frozen_v2](candidates/w4a16_central_refactor/validation/frozen_v2/).
Entry068 in [the ledger](w4a16_optimization_experiments.md#entry-068--central-maintained-package-and-wrapper-cleanup)
preserves the initial pending state and completion chronology.

Default whole13/catalog8/AUTO100 process59432 has closed, including source,
native and idle checks. Saved result0c19b3ee/proofd56db1c9 contains13 rows,
104 compiled/winner records,13×8 rankings and1,300 samples.
[Complete comparisonf15e1811](logs/cu132-recovery0909e-owned-default-vs-central-independent-comparison-001/README.md):
**+1.437759% latency GM over8–4096,4/10 lower**; all13 secondary+2.767275%,5/13 lower.
This does not establish a gain. Keep the complete owned098c default table
(result490bdf86/reconstruction9d6b063c), with no row replacement or timing rerun.
The eight public tactics remain M256/C2/K256/S2 × N64/N128 × F4/F8 × epi/reuse;
manual APIs are unchanged.

The subsequent init cleanup is static only: sourcec2675f51/commit5152a9e7,
[proofdc703c5a](candidates/w4a16_init_cleanup/checks.json). Exactly three init
files change; all98 exports,34 lazy targets/handler and old helpers remain,
shim init matches PR base and kernel_helpers stays exact6af. No host/GPU or
performance cohort was rerun for this cleanup. Detailed chronology is appended
in [entries068–070](w4a16_optimization_experiments.md#entry-068--central-maintained-package-and-wrapper-cleanup).

## Completed CLC reference and diagnostic

Published loop commit765383cf7/source11ea completed unchanged11/41 numerics,
all compute LOCAL0, and whole CLC8 AUTO100:13 rows,104 compiled/winner records,
13×8 rankings and1,300 primary samples. Against the preceding complete CLC run,
8–4096 latency GM is **−0.376683%,7/10 lower**; all13 secondary GM is−0.052067%.
[Complete table](logs/cu132-recovery0909e-clc-before-vs-loop-independent-comparison-001/README.md),
comparison0f9ebc70/result458e3fc4/reconstruction0e2f3b06. CLC remains substantially
slower than default and stays outside its public catalog. Exact central native
comparisons preserve this CLC reference without a relocation timing repeat.

The selected global-T128 loop NSYS capture is delivered:
[report](profiles/clc-loop-0909e-nsys-t128-001/ep_w4a16_megamoe_t128.nsys-rep) and
[analysis](profiles/clc-loop-0909e-nsys-t128-001/README.md). It covers128 global
source tokens/16 per rank and two eager iterations on all8 GPUs. These are
instrumented diagnostic durations, not AUTO cold-L2 timing or a new retention
comparison. Earlier full NCU/NSYS056ce/af938 reports remain immutable:
[index](profiles/current-best-056ce-0909e-full-ncu/README.md),
[archive](profiles/current-best-056ce-0909e-full-ncu.zip), SHA9bf5498b.

## Archived CLC work (superseded by removal request)

[Launch sizing](candidates/w4a16_configurable_clc/central_refactor_followups/tight_rows/README.md)
patch101b7cca is retained and pushed as16b7170fe/source4cf. Three CLC native
captures preserve all nine role instructions/encodings/resources. Compute grid.z
is148→148 (small C1),9216→1520 (N64 C2),5120→1008 (N128 C2); transport launches,
full workspace/bitmap/queue/fallback capacity and default code remain unchanged.
Unchanged numerics passed11 rank tests/41 objects: all compute REG96/640/two
decode WGs/LOCAL0 and all123 role records LOCAL0 (closure310c8b7d).

[Full AUTO002 table](logs/cu132-recovery0910a-loop-vs-tight-rows-independent-comparison-002/README.md)
compares complete tight4cf against complete loop11ea, with13 rows/104 records/
13×8 rankings/1,300 samples and unchanged protocol. Result89420688/proof67a27f2b,
comparison2bcf7da8, idle0f0dbdff: **−0.910433% latency GM over8–4096,6/10 lower**;
all13−0.844123%,9/13 lower. Process603.33s. [Retention](candidates/w4a16_central_refactor/tight_rows_validation/execution/retention.json)
keeps the modest mixed result and smaller physical launch. CLC is still slower
than default and remains outside the public catalog. Fresh-cache/source checks
are bound; AUTO did not save host grid IR, so observed launch sizes belong to
the native fixtures. No extra capture was added.

AUTO001's default-storage observer failure is preserved separately; no timing
row was produced. Retry002 restored established CLC storage/resource/saved checks
without changing kernels, oracles, timers, catalog or samples. No completed
numerical/native cohort was repeated for that helper repair.

[Task-or-terminal](candidates/w4a16_configurable_clc/central_refactor_followups/task_or_terminal/README.md)
patche8662a2a is the active isolated trial on top of4cf. It publishes a successful
FC2 claim or an unsuccessful-pop terminal sentinel through one broadcast, keeping
the final successful task. [Frozen package](candidates/w4a16_central_refactor/task_or_terminal_validation/frozen/)
contains source85a1, manifest77e6f1ed, deltae783c29d and stage96450b5a. Its corrected
helper map is38603d81; use `performance_clc_corrected` / `readers_clc_corrected`,
not the preserved stale helper folders. Installation/preflight and three native fixtures passed: compute instructions
3296→3256,4360→4312,4888→4848, same REG96/640/LOCAL0 and exact transport roles.
The unchanged11/41 cohort passed; the subsequent full13 CLC8 AUTO100 was cancelled before completion against the
complete retained tight002 BEFORE. No default/split or cleanup rerun is added.

The following CLC proposals are archived and will not run:
- [Query/claim overlap](candidates/w4a16_configurable_clc/central_refactor_followups/query_claim_overlap/README.md), patch2130620b, is based on task-or-terminal and moves the existing single-slot CLC request ahead of independent FC2 claim publication. No extra slot/state/knob.
- [Skip-empty ownership](candidates/w4a16_configurable_clc/central_refactor_followups/skip_empty_ownership/README.md), patch eceefc318/review2329fe07.
- [Row metadata](candidates/w4a16_configurable_clc/row_metadata/README.md), patchccb26f62; [payload overlap](candidates/w4a16_configurable_clc/central_refactor_followups/payload_overlap/README.md), patch106d6ab9; and activation-SF state cleanup.

The [read-only scope audit](candidates/w4a16_central_refactor/PR_SCOPE_AUDIT_5152.md)
found no further unrelated removals or vendor drift. No additional cleanup is
proposed, and no tests were rerun for this audit.

## Recovery and execution ownership

The old `fi-w4a16-mega-0909e` disappeared before tight-row staging; that stage
failed before remote mutation or compilation. Replacement request98013 is ready
as `fi-w4a16-mega-0910a`, B300×8/bare/no size, with explicit
`nvcr.io/nvidia/pytorch:26.05-py3` selected from the live CUDA13.2 catalog.
[Hardware continuity8e48214f](candidates/cuda132_recovery_0910a/hardware-continuity.json)
confirms the same hu-pdx-115, all eight UUIDs/driver, and matching recorded idle
SM/memory clocks and power limit. [Stack continuity7df582c4](candidates/cuda132_recovery_0910a/stack-continuity.json)
confirms matching Torch/CUDA/DSL, packages, loaded library bytes, profilers and
launcher after bootstrap/setup completed with exit zero.

Exact published5152/sourcec267 was restored using the sealed
[bootstrap package](candidates/cuda132_recovery_0910a/bootstrap5152/README.md).
The [kernel-only recovery delta](candidates/w4a16_central_refactor/tight_rows_validation/frozen_recovery0910a/)
(dee6d6d9, stage6d36499c, target manifest1f937b40) then installed4cf:
[receipt68eef661](logs/cu132-recovery0910a-tight-rows-install-001/receipt.json).
The completed whole loop458e/proof0e2f remains the BEFORE on the same hardware
and matching stack. No fresh timing baseline, completed host/default cohort or
init-cleanup cohort is added. This does not relabel the historical loop run as
a new measurement.

The new cache paths initially contain only the observed empty diagnostic log
[inventoryf15fd1e7](logs/cu132-recovery0910a-setup-001/native-cache-after.json).
Historical d3ce binaries were not restored; required first builds and subsequent
inventories must be recorded from this container. The [build-only module preparation](logs/cu132-recovery0910a-native-dependencies-001/completion.json)
completed using the existing FP4 SM103 quantization and fused-routing JIT specs,
with zero tensor operations/kernel calls; the new native inventory has22 records.
Its binary hashes are fresh, not a claimed restoration of historical d3ce.
Integration owns all remote source/native/GPU execution. Local preparation
preserves historical packages.

Primary checkout: `/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/flashinfer`,
branch `feat/w4a16-megamoe`. Use managed `/usr/local/bin/h` from project `hai/`;
verify its path first. Never mutate remote source while a run is active. The
completed0909e environment was hu-pdx-115/8×B300,26.05-py3/CUDA13.2.78,
driver590.48.01/Torch2.12.0a0+5aff3928d8.nv26.05/DSL4.7.1/native13.3.27.
The restored stack comparison above separately verifies their continuity on0910a.
Earlier decisions/raw results remain in the ledger and state snapshots.
