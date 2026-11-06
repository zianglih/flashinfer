# Trace-guided optimization experiments, 2026-09-25

Control: HashInfer `002ef1454cbacde09972ed5e2ec7dcfe37e55749` (PR13).
Owned devbox: `hashinfer-trace-labels-0924`, c2, `hu-pdx-38`, B300.
Preserve this box for iteration. Trace files remain outside the repository.

## Evidence and protocol

See `ledger-audit.md` for historical context, explicitly qualified as older
source/compiler/workload evidence. See `trace-analysis.md` and its raw tables
for the current rank2 IKET trace. IKET is diagnostic, not a latency benchmark.

The target is H6144/I2048/E256/top8, EP4, **256 tokens/rank = 1024 global**,
uniform routing (32 rows/expert), using the exact trace inputs and weights.
`benchmark.py` adapts only the native benchmark fixture. It preserves full
public forward including runtime alphas, staging and finalization, 3 warmups,
100 cold-L2 CUDA-graph CUPTI samples, per-iteration rank-MAX, and native AUTO
with a fresh cache for each process. All four arms run serially A1/B1/B2/A2;
the comparison pools 200 raw samples per arm. Hot tuner scores are separate.

`benchmark_checked.py` additionally checks two untimed outputs after timing
for finite/repeat-bit equality and compares the target (or native T128) against
the independent reference. This distinction is explicit: the initial predecode
pilot has no numerical qualification and cannot be promoted from timing alone.
If the target improves, qualify the full historical H7168/global-token matrix
and EP8 guard before retaining it. Keep every row, source hash and raw sample.

## Candidates

1. **Full predecode** (`predecode/`): decode K256 into registers before directly
   acquiring the decoded TMEM destination. Remove initial and loop-tail
   `producer_try_acquire`, which can suspend despite its name. Preserve raw
   release, TMEM store fence, decoded commit, stage depth and arithmetic.
   Hypothesis: overlap decode with the preceding MMA's ownership of the slot.
   Completed target ABBA: before 334.434 us, after 435.779 us, speedup 0.7674x
   (200 samples/arm). All fixtures match. Reject: 30.3% latency regression.
   See `predecode-target-summary.{md,json}`. No PR change or numerical claim.
2. **Wider TMEM store** (`store16/`): owned kernel copy atom repetition8→16.
   Hypothesis: replace eight STTM.x8 per K with four STTM.x16 and reduce store
   address/instruction overhead. Generated code, numerics and timing required.
   Completed checked target ABBA: before 333.171 us, after 327.859 us, 1.0162x.
   Finite BF16 bits match the independent reference on all ranks; before/after
   output signatures agree. The gain is modest with run-to-run movement.
   Full native EP4/EP8 qualification is queued against the reusable 002 baseline.
   See `store16-target-summary.{md,json}`; no retention decision yet.
3. **No speculative probes** (`no_peek/`, isolated trial complete): retain current acquire
   before decode, but use direct waits for current raw/TMEM stages. Remove
   lookahead `consumer_try_wait` and `producer_try_acquire`, avoiding a
   potentially suspending probe on a future stage while current work is ready.
   Hypothesis: reduce control overhead and premature waiting with a small diff.
   Isolated target ABBA: before 335.875 us, after 336.147 us, 0.9992x; bit-exact.
   See `no-peek-target-summary.{md,json}`. Inspect instruction costs before
   deciding whether to test/retain this atop the preceding retained version.

No arbitrary one-CGA launch restriction, operand completion-ring coupling,
new scheduling knob, or change to mathematical accumulation is proposed.

## User clarification: current-head before/after reuse

The final comparison follows PR11's Runtime alpha batching methodology, captured
in `pr11-methodology.json` and audited in `pr11-contract-audit.md`. On 2026-09-25
the user explicitly authorized freezing current PR head 002ef145 as the before
source and reusing its results. Full native EP4 and EP8 before sweeps are queued
once; candidate after sweeps reuse them. Completed target ABBA experiments are
extra pilot evidence, not a claim that PR11 used ABBA.

`source-manifest.json` records each candidate content digest and patch hash.
`benchmark_checked_v2.py` also verifies source content after each run.

## Cumulative retention contract

The user clarified that instruction reduction can justify retaining a small
change with a small performance gain, beyond the wider-store candidate.
Optimizations must stack: each new retention decision compares against the
**previous retained version**, while 002 remains the overall PR baseline.
Isolated trials above are exploration only and do not establish incremental
benefit on a different stack. Generated-code checks include resource/local
memory costs, not just total static instruction count.

Pending stack candidates are `store16_no_peek/`, `counts_overlap/` (early
scheduler metadata readiness), and `parallel_payload/` (payload/route preparation
on separate existing warp groups). The FC1 fragment-64 trial remains separate.
Each needs fresh source-bound timing and correctness before retention.

## Dispatch overlap source investigation

`dispatch-history.md` records earlier measured/rejected attempts. They lacked
causal kernel traces, so they guide risk assessment rather than vetoing a
current trial. Two small candidates are being prepared on top of store16:

- **Count-ready scheduler:** use the existing packed receive-count sum's high
  word as a rank-completion count. Each source rank publishes one release
  contribution after its local grid barrier. The scheduler acquires finalized
  counts before producing weight work; activation still waits for token-ready
  flags and the original global dispatch publication remains. This avoids
  assuming homogeneous CTA counts. See `dispatch-overlap-audit.md` and the
  candidate's ordering proof. No GPU correctness/performance claim yet.
- **Parallel payload staging:** existing epilogue warps copy BF16 payload while
  dispatch warps stage IDs/weights and prepare routing. One local 256-thread
  handoff joins payload writers before the unchanged grid/NVLink publication.
  This overlaps local preparation, rather than hiding an arbitrary peer delay.
  See `parallel-payload.md` and its source audit. No GPU claim yet.

Each overlap candidate will be compared incrementally with the previous
retained stack. No speculative expert computation assumes uniform routing.

## Ownership and later upstream sync

The user explicitly permits direct edits to otherwise protected upstream
implementations for clean experiments. Protection rules must not narrow the
optimization search. Once an optimization is retained, move the modified
implementation into the owned W4A16 MegaMoE layer and restore the protected
source. Verify the ownership port separately; do not silently treat earlier
prototype measurements as measurements of different generated code. No
upstream synchronization is authorized in this task.

The count-ready prototype currently changes the inherited count publication
in vendored token_comm.py. If retained, own its dispatch_barrier method in
W4A16TokenComm. The no-probe prototype currently changes the shared grouped
decoder; if retained for MegaMoE, own its modified transform method in
_MegaMixedInput. These are experimental boundaries, not reasons to reject
either optimization.

## Further store-width exploration

Prepared isolated repetition32 and repetition64 candidates, each changing
only the same owned copy atom. Both are compared against repetition16 on
the uniform target; instruction savings require native SASS and resource
checks. A wider spelling is not evidence of fewer issued instructions or
better performance. No retention decision has been made.

The serial queue now contains complete native before, complete store16
native after, fragment64 target/codegen diagnostics, then the R1-relative
target candidates. GPU performance runs and IKET captures never overlap.

## Frozen native baseline completed

Both 13-row EP4 and EP8 sweeps completed on source 002ef145. Logs verify the
same production source digest at start and finish. All 156 rank/shape output
checks are finite and bit-identical on repeated forwards; independent native
T128 references pass on all 12 ranks. `native-before.json` preserves all raw
samples and winners, with the complete logs under `results/`.

EP4 raw median milliseconds, T1 through T16384 in the declared row order:
0.065633, 0.084240, 0.110929, 0.142913, 0.196722, 0.262914, 0.302466,
0.323155, 0.329379, 0.354788, 0.814855, 1.462221, 2.858201.

EP8: 0.079952, 0.088288, 0.102160, 0.131937, 0.143073, 0.168113,
0.189569, 0.195840, 0.203857, 0.207041, 0.465188, 0.790070, 1.522037.

These results are the reusable overall before source, not a retention
baseline for all future steps: later retained changes compare incrementally.

## Store16 native EP4 first sweep

Completed all 13 rows with source closure, identical before/after output
hashes on all ranks/shapes, and passing independent T128 reference. Full table
and samples: `store16-native-ep4-summary.{md,json}`. Decode T4–512 geometric
speedup is **0.9820x**. T2/T4/T8 speedups are 0.8968/0.9307/0.8980; T64/T128/T512 improve 2.7%/0.9%/2.3%. Prefill 4K/8K/16K speedups are
1.0248/0.9848/1.0003. This does not yet justify retention.

T4 selected the same N64/G512/epilogue tactic in both arms. A bounded fixed-
winner T4 ABBA is queued to distinguish the source change from run-to-run
movement. Matched native T4 and uniform N64/N128 codegen exports will inspect
TMEM stores, register packing/moves, local accesses, and allocated resources.
EP8 qualification and the wider32/64 variants remain pending. No result is
hidden or discarded, and isolated uniform-target gains are not substituted
for the native retention matrix.

The dispatch/no-probe candidates currently use a **provisional store16 parent**
for controlled exploration. This is not a retention decision. If that parent
is rejected or replaced, rebuild promising candidates on the actual retained
source and measure their incremental effect there before promotion.

## Store16 native EP8 first sweep

All 13 rows completed with matching paired output hashes, finite/repeated
outputs, independent T128 reference, and source closure. EP8 improves the
decode aggregate while EP4 regresses; do not pool the EPs to hide that split.
`store16-native-ep8-summary.{md,json}` preserves the full comparison and raw
samples. Prefill medians are 460.692, 786.690 and 1480.067 us at 4K/8K/16K,
versus 465.188, 790.070 and 1522.037 us before. The sparse T4 fixed-winner ABBA
and exact-capacity SASS comparison remain required before interpreting the
EP4 regression or deciding retention.

## Initial native SASS and fragment64 decision

Uninstrumented O3, uniform256, fixed N64/G512/epilogue winner, actual timed
int32-ID/contiguous-BF16 ABI (`00-w4a16-megamoe`). All four staging ABIs were
exported separately; source fingerprints and compilation ownership passed.
Artifacts are in `codegen/<candidate>/rank0/`; native T4/N128 follow-ups are
queued and these uniform results must not be generalized silently.

| Source | Static kernel instructions | Weight STTM per K tile | LDL / STL | Registers / stack bytes |
|---|---:|---|---:|---:|
| Control | 5128 | 8 x8 | 0 / 0 | 96 / 0 |
| Store16 | 5112 | 4 x16 | 0 / 0 | 96 / 0 |
| No probes, isolated | 5088 | 8 x8 | 0 / 0 | 96 / 0 |
| FC1 fragment64 | 5144 | 8 x8 | 0 / 0 | 96 / 0 |
| Full predecode | 5288 | 8 x8 | 71 / 63 | 96 / 136 |

Store16 leaves MOV/PRMT counts unchanged in this specialization. No probes
reduces static TRYWAIT sites from 106 to 98; the whole kernel includes other
roles' waits and epilogue stores, so those totals are not decoder-only counts.
Native baseline code streams stores among decode arithmetic. Full predecode
holds decoded values across the acquire, adding local-stack traffic; this
supports its existing rejection, rather than attributing the slowdown only
to the source-level wait duration.

**Reject FC1 fragment64.** Its checked target median is 338.739 us versus the
latest reusable control sweep's 339.091 us (1.0010x; MADs 1.456/1.552 us), with
16 additional instructions and no resource improvement. There is no compelling
timing or instruction benefit to promote. `fc1frag64-target-summary.{md,json}`
retains that comparison, all fixtures/checks and its reused-control limitation.


## Cumulative target sweep, 2026-09-25 09:11–09:16 UTC

Fresh native eight-candidate AUTO per arm, uniform256 target, 100 cold-L2
CUPTI samples. Provisional store16 parent median329.827us, MAD1.583us.
All four completed candidates have identical fixture/output hashes, four
independent finite BF16 reference passes, repeated bit equality and source
closure. Summaries preserve every sample and tactic in `<arm>-cumulative-summary`.

| Candidate added to provisional store16 | Median us | Incremental speedup | Tactic |
|---|---:|---:|---|
| Count-ready scheduler |340.899|0.9675x|N64/G1024/epi|
| Parallel payload |327.491|1.0071x|N64/G512/epi|
| Remove lookahead probes |330.818|0.9970x|N64/G512/epi|
| Store32 replacing store16 |330.723|0.9973x|N64/G512/epi|

These single-order results are exploratory, not retention decisions. Counts
changes winner; a matched-tactic trace/SASS comparison and the reviewed
fence-amortization candidate will distinguish added publication cost from
overlap benefit. No-probe may still merit retention from its instruction
reduction if native guard results remain acceptable. Store32 needs native
resource evidence. Store64 is **rejected in its current form**: ptxas C7600
fails register allocation at the144-register dynamic target during AUTO,
before numerical/timing evidence. Log retained; do not describe it as a
correct or benchmarked candidate.

Partial33 heterogeneous-grid qualification initially stalled in torchrun
rendezvous before worker launch: container hostname hu-pdx-38 had no hosts
entry. Adding127.0.0.1 hu-pdx-38 to this devbox's /etc/hosts resumed the pending
launcher. Subsequent qualification launches explicitly use master address
127.0.0.1/port29774. This is an environment/launcher correction, not a kernel
failure; original log retained. No GPU run overlaps another experiment.

## Dispatch stress qualification and fence follow-up

Store16, counts_overlap and parallel_payload each passed partial33/heterogeneous:
EP4 H288/I448/E132/top8,32capacity/rank, stridedBF16/int64,1/2/3/4clusters
perrank; tactics6+1, nine changing-route/live-size phases. Every source passed
90collective /360rank output checks with finite bit equality and all-rank
source closure. Final summaries/logs are under results/dispatch-first-pass.
The same workspace is reused; first updated execution is graph replay before
any updated eager call. This covers partial local expert groups, count-bank
rotation, empty/refill and idle compute ranks. It is not full-grid GLM5 or
all-tactic validation; payload's target winner2 needs explicit coverage later.

counts_fence is a separate frozen experiment: sourceSHA
771d8c303c79f299980ce97b9ffff53a24d86afea4ab1383bd2bfdd942d75951.
It adds one system fence per publishing CTA0 thread after local grid sync,
then uses relaxed count REDs. The trailing publication fence/barriers remain.
Two independent CPU reviews agree the early scheduler's aggregate-count and
staged-score contract is preserved; in-loop per-source count STGs are NOT
published by that prefence and remain gated by the original dispatch barrier.
Source audit, exact parent delta and proof: counts-fence.md,
counts-fence-source-audit.json, count-release-fence-hypothesis.md.
No GPU or performance claim yet. Queued matched N64/G512 diagnostics hold the
same tactic for store16/counts/counts_fence/payload, then independently autotune
counts_fence. This is separate from native AUTO retention evidence.

## Wider-store follow-up native evidence

NativeT4 (H7168, capacity1/rank,28FC1Ksteps) and uniformN128 (H6144,
capacity256/rank,raw4/decoded2) both reproduce store16's exact -8instructions
perKphase with no extra packing/localmemory; allREG96/STACK0.
The sparse regression has no specialization-specific spill explanation in
these dumps. FixedT4ABBA remains pending. Exactartifacts are under
codegen/{control,store16}-{native-t4,uniform-n128}-codegen/rank0.

**Reject store32.** UniformN64 native kernel5152 instructions versus store16's
5112. Widerstores reduce8weightx16 to4weightx32 in total acrossFC1+FC2, but
MOV grows426→461 and totalinstructionsgrow40. No spills, but target0.9973x
provides no compensating timing benefit. Native report will preserve
phase-aware packing details. This rejects the32-wide candidate, not the
proven16-wide instruction reduction. Store64 compile failure remains separate.

## R1 retained: store16

The fixed native T4 ABBA at the identical prior AUTO winner gives **122.017 →
112.385 us (1.0857x)**, pooling 200 untrimmed samples per arm. Individual
A1/B1/B2/A2 medians are 121.665 / 113.713 / 111.010 / 122.641 us. Fixture/output
hashes and source closure pass. This is fixed-tactic confirmation, not a
replacement for the full native AUTO table.

The benchmark emits a null `_autotune_winner` for explicit knobs. The preserved
`run-t4-confirmation.sh` and source contract attest the fixed choice. The
summarizer requires fingerprinted provenance for that case; raw logs are
untouched. Nine CPU evidence tests pass. The report explicitly distinguishes
this driver attestation from a runtime-emitted winner record.

Retain the one-line owned copy-atom change as **R1**. The consistent reduction
of eight instructions per K-step in each phase, no resource cost, target ABBA
1.0162x, and EP8 decode 1.0297x support the user's instruction-reduction
preference. The first full EP4 decode 0.9820x, T2/T8 regressions, and small
prefill changes remain disclosed. The T4 repeat contradicts a repeatable T4
regression; it does not establish that the other rows are noise. Future
retention compares R1 performance, not the original 002 source.

`retention.json` records the exact source parent and evidence. The primary
checkout records R1 in local commit `916461b3f5801d49ebfb7cb4bee937b52e0e6b44`; it remains unpushed pending the final stack. Documentation corrections are still uncommitted. Scoped pre-commit and whitespace checks passed.

**Reopen store32 for native qualification.** The detailed phase-aware audit
supersedes the provisional rejection above: its decoder loops save two FC1
and five FC2 instructions per K-step against R1. The 47 additional instructions
outside those loops include epilogue/dispatch costs, not decoded-payload
packing or out-of-line decoder wait costs. Those costs are not all one-time.
The user's preference warrants a full incremental native comparison; no
retention yet. Exact localization is in `native-codegen-followups.md` and
`native-codegen-followup-analysis/extra-regions.json`.

## Matched dispatch trace and timing follow-up

`results/causal-first-pass` contains source-bound matched-tactic native IKET
captures for R1, the original count-ready scheduler, and parallel payload.
Both CTAs are reported relative to the same GPU's CTA0 dispatch-range end;
GPU clocks are never aligned across ranks. The native instruction-point audit
binds every decode context to its original cubin and passes all four ranks:
109 points for R1/counts, 113 for payload. Launch geometry remains 148 CTAs.

The initial CTA0-only display was incomplete for mechanism assessment. The
updated table includes both CTAs: count-ready scheduling lets CTA1 on ranks
0/1 decode 1.024/1.408 us before dispatch-sync end, while neither CTA on ranks
2/3 does so. CTA0 first MMA is not consistently earlier. Payload staging
naturally overlaps route preparation by 0.896–1.216 us. These instrumented
one-shot leads are mechanism evidence, not full-forward timing or GPU
utilization. The full report preserves both CTAs and numerical/trace audits.

Matched fixed N64/G512/epilogue target timing, 100 cold-CUPTI samples per run:

| Execution order | Arm | Median us |
|---|---|---:|
| 1 | R1 control A1 | 336.627 |
| 2 | Original count-ready scheduler | 337.299 |
| 3 | Count-ready with one pre-loop fence | 330.291 |
| 4 | Parallel payload | 330.307 |
| 5 | R1 control A2 | 336.163 |

Every candidate's four independent-reference checks, repeated finite BF16
bits, paired output hashes, fixtures and source closure pass. Comparisons
against each bracketing control are separately preserved in
`dispatch-second-<arm>-vs-{A1,A2}.{md,json}`. Fixed knobs are explicitly
attested by the fingerprinted driver rather than a runtime AUTO winner.
Each candidate has one run, so these are not separate ABBA experiments.

The fence candidate then independently autotuned all eight native choices:
327.714 us, versus the reusable R1 AUTO target's 329.827 us (**1.0064x**).
This small target gain is insufficient by itself for native-matrix retention.
Native SASS exports for counts_fence and parallel_payload are now preserved;
fence count/order and resource audits are pending. Store32's complete native
EP4/EP8 run is active, followed by full-grid GLM5 changing-route qualification
for counts_fence and payload at tactics 2, 6 and 1. No dispatch candidate has
been retained or ownership-ported.

## Native count/payload evidence and ownership follow-up

The completed codegen audit `native-codegen-overlap.md` passes all16 exports
(four staging ABIs each for R1, count-ready, count-fence and payload). The
prefix-fence revision saves eight whole-kernel static instructions versus the
original release-RED experiment: three net ordering instructions and five
padding NOPs, not eight synchronization instructions. Native polling loads
only the used high32 readiness word, although the source/PTX acquire is64-bit.
The original trailing publication remains. Payload's NB11 handoff is before
local grid publication, with epilogue arrival before144-register allocation
and dispatch wait after its64-register donation. No register/stack/spill
increase occurs in these exports.

Store32's complete EP4 comparison against R1 is1.0107715x decode, with all13
selected tactics identical and all52 output hashes matching. EP8 is still
running. No Store32 or dispatch retention decision has been made.

A final ownership audit found that owning only a new count publisher would
leave existing protected vendor trace edits. The final port must account for
all reachable markerized transport methods as well as `_transform_tile`, so
protected files can match the PR base. This port is deliberately deferred
until candidate decisions; experiments continue against frozen source hashes.
No global IKET monkeypatch is acceptable as a shortcut. The agent's bounded
review is checking method dependencies and semantic equivalence requirements.

Prepared `prepare_increment.py` to compose a fingerprinted feature delta onto
an explicitly selected frozen parent in a project-local worktree. Prepared
`run-incremental-native.sh` for one serialized candidate's uniform target and
full EP4/EP8 native sweeps. Neither helper makes retention decisions. A
pending-only final PR draft lives at `FINAL-PR-BODY-DRAFT.md`; it is not
published and does not relabel prototype evidence as final-head testing.

## Store32 final decision: reject; R1 remains the retained parent

Both complete native sweeps pass source closure, all paired output hashes,
fixture identity and13-row timing audits. EP4decode is1.0107715x relative to
R1, EP8decode0.9858163x, and uniformtarget0.9972923x. EP8T4 regresses at the
same selected tactic,98.849→107.728us(0.9176x); some other rows change group
hint. Prefill EP4 ratios are1.0172/1.0364/1.0031x, EP8 ratios
1.0165/1.0110/0.9894x. Complete raw results are retained; do not pool EPs.

The native FC1/FC2 per-K savings(2/5instructions) are real and spill-free,
but the whole kernel grows40 static instructions and neither EP8 nor the
uniform target demonstrates an incremental benefit. The extra code is not
proven to cause the timing regressions. Reject Store32 after full review;
this supersedes its reopened status. R1/store16 stays the actual parent.

The queued no-probe run compares store16_no_peek directly with R1: fresh
uniform target, full13-row EP4/EP8 AUTO, then cumulative native codegen.
Prepared two further source-only candidates, store16_no_peek_counts and
store16_no_peek_payload, using frozen feature deltas. They are not retained
and no GPU work is scheduled for them until no-probe's parent decision.

## Dispatch changing-route second pass: complete

`dispatch-second-pass-audit.md/.json` and `audit_dispatch_second_pass.py`
independently verify the completed counts_fence partial33/heterogeneous,
counts_fence GLM5/full and parallel_payload GLM5/full runs. Each covers135
collective checks /540 rank outputs at tactics2,6,1, all nine phases and five
executions per phase. All nonempty independent references have zero errors;
all source closures pass. Exact grid records are1/2/3/4 clusters by rank for
the heterogeneous fixture and74/rank for GLM5. The audit checks actual
fixture updates, score-only mutation, hot-owner routing and restored-output
parity. Total1,620 rank outputs. These are EP4/O3/FC2-topk-placement prototype
results, not final owned-port, sanitizer, FC1-placement or NCU evidence.

The next queued run, no-probe-after-r1, completed its fresh uniform AUTO at
334.484us versus reusable R1 329.827us(~0.9861x); full native EP4/EP8 and
cumulative disassembly are pending, so no retention is inferred. A final
source-only benchmark wrapper `benchmark_checked_final.py` additionally
requires an explicit tested commit attestation and verifies expected package
bytes on every rank; no measurement algorithm is changed and it is not yet
used for a GPU result.

## Probe-deletion attribution follow-up queued

Before making a no-probe retention decision, split the two deletions on R1:
`store16_no_raw_peek` removes only initial/next raw-TMA try-waits and the
matching consumer-wait status argument; `store16_no_tmem_peek` removes only
initial/next decoded-TMEM try-acquires and the matching producer-acquire
status argument. The other probe's source text is unchanged. Blocking waits,
state advancement, release, decode, store, fence and commit remain intact.
`prepare_partial_probe_removal.py` checks the exact two guarded probes, one
initial Boolean and one wait argument for each variant; all Python parses
and whitespace checks pass. Neither candidate is retained or device-tested.

`run-partial-probe-pilots.sh` is queued after no-probe's full native sweep and
codegen. It runs fresh uniform AUTO on R1→raw-only→TMEM-only→both, preserving
100cold-CUPTI samples, independent reference, fixture/output hashes and source
closure per run. This also provides a contemporaneous parent target control.
These are short attribution trials, not substitutes for native EP4/EP8
qualification. No further speculative directions are planned beyond finishing
this transform choice and the cumulative dispatch candidates.

## No-probe native EP4 complete; bounded EP8 drift check queued

All13 EP4 rows pass fixture/output/source closure, with identical before/after
selected tactics. DecodeGM is1.01210985x versus R1. T16 is0.9530x
(196.258→205.939us); prefill ratios are0.98785/0.99931/1.00536. Uniform is
0.98608x. Full EP8/codegen/partial-probe target results remain pending; no
retention yet.

Both recent Store32 and no-probe EP8T4 runs are near108us, versus older R1's
98.849us. Similarity alone does not identify the cause. After the queued
partial-probe series, `run-no-probe-ep8-t4-check.sh` will run fixed ABBA at the
actual R1 EP8T4 AUTO winner, N64/G1024/epilogue. It preserves200 untrimmed
samples per arm and driver-attested knob provenance. This diagnostic does
not replace the full native AUTO table or establish causes for other rows.

Preparation first asserted that the old EP4T4 knob record matched EP8; that
assertion correctly failed (G512 versus G1024). No source/test was launched.
A subsequent missing-script shell attempt exited immediately; its log is
preserved as no-probe-ep8-t4-check-launch-failed.log. The corrected driver is
derived from the verified EP8 record and fingerprinted in
no-probe-ep8-t4-fixed-provenance.json before the successful queued launch.

## Ownership and final trace preparation complete (CPU only)

`prepare_owned_trace_port.py` is frozen at SHA256
5547e555724c3cd46c5d5a4c8088472c84bc29b35df4f66202cb1544075de25e.
Seven source fixtures and nine mutation-rejection checks pass. A separate R1
port-test worktree passes method/member AST, import-origin, protected-file
hash and whitespace audits. No primary or frozen performance source changed.
The helper preserves the selected probe mode and optimizations, owns only
needed methods, and restores all three protected files to PR base.

Final dispatch trace support passes18 synthetic cases, all12 historical
captures with their original causal values unchanged, and a labeled synthetic
full-trace integration. The strict final mode requires all three once-only,
ordered, nested CTA0/warp8 subsections. JSON exposes warp/CTA identity, not
per-lane execution; lane uniformity remains a source/native-point audit claim.
`capture_causal_traces.py --require-dispatch-subsections` now forwards that
requirement to the summarizer and records it. Final capture remains pending.
The final guide amendment draft and CPU evidence are under
final-trace-validation/. Historical causal reports were not overwritten.

## Raw-only probes selected for the next qualification, not retained yet

The fresh target pilot control is326.450us. Removing only raw-TMA lookahead
probes is324.642us(~1.0056x); removing only TMEM probes is328.995us(~0.9923x).
The both-removal rerun is still pending. Each completed pilot has independent
reference/finite/repeated-bit checks; the agent is auditing exact paired
hashes and tactic choices. These single target runs do not establish native
matrix gains or a causal explanation for the EP8 regressions.

Queue `run-raw-probe-native.sh` after the fixed EP8T4 confirmation. It runs
full13-row EP4/EP8 AUTO on store16_no_raw_peek, then exact uniformN64 codegen.
The already-fresh uniform pilot is reused rather than redundantly repeated.
The generic native runner gained an explicit scope selection with the old
three-scope default unchanged; its executed v1 text is preserved under
executed-harnesses/run-incremental-native-v1.sh. This selection is an
experimental qualification decision only; R1 remains the retained parent.

## Both-probe removal rejected; raw-only qualification active

Both-probe native/codegen and all partial pilots are complete. Exact stacked
SASS saves10FC1/14FC2 instructions per K and40 whole-kernel instructions,
with unchanged136 conversion/scale instructions, x16 stores and no spills.
Despite this real reduction, full EP8 decode0.970334x, target0.9860785x and
fresh target0.9888529x do not support consistent incremental benefit. The
fixed EP8T4 ABBA yields104.4165→107.201us(0.97402543x) from200 samples/arm;
A1/B1/B2/A2 medians102.1765/106.657/107.793/109.2165us show material drift.
This diagnostic is not a clean2.6% causal penalty nor a substitute for AUTO.
Reject both-probe removal; R1 remains the retained parent.

Fresh uniform partial series is326.4505us control,324.642us raw-only
(1.00557075x),328.9945us TMEM-only(0.99226735x),330.1305us both
(0.98885289x). Raw-only matches controlN64/G512/epi; other two chooseG1024.
All4 fixtures, output/source closures and independent references pass.
Only raw-only advances to full native EP4/EP8 plus exact SASS qualification;
no partial candidate is retained yet. The fixed T4 evidence only has finite,
repeat, paired fixture/output and source checks; independent-reference
coverage comes from uniform1024 and nativeT128 separately.

## Source preparation while raw-only runs

Prepared/transferred `store16_raw_counts` by applying the frozen counts_fence
feature (relative to R1) onto frozen raw-only. Package SHA256 is
`3ec75add37d200d2c06d986436f3a87c61774706c0c79d0bfab0878b7baf99c1`.
This is source preparation only; it has not run or been retained. Use it only
if raw-only becomes the actual retained parent. Otherwise counts_fence remains
the next R1-based candidate. Do not compare a noncumulative variant and label
it cumulative evidence.

CPU fixture check: `uv run --no-project --with pytest python -m pytest
--noconftest -q tests/moe_ep/test_trace_w4a16_fixture.py` passes3 tests.
Plain local Python lacked pytest; the first isolated-UV attempt passed test
bodies but failed repository session teardown because this Mac environment
lacks torch. `--noconftest` is valid for these standalone fixture invariants
and avoids the unrelated distributed teardown. This is CPU routing coverage,
not GPU numerical evidence.

## Raw-only EP4 qualification complete

All13 rows pass source/fixture/output closure. Decode GM versus R1 is
1.01044581x; T4096/8192/16384 ratios are1.009814/1.017911/0.999592x.
T2 selects N128/G512 versus R1 N64/G1024; G-only changes occur at
T4/8/64/256/16384. Full records are raw-probe-ep4-review-r1.{json,md}.
EP8 and exact codegen remain pending; no retention decision from EP4 alone.

Live PR11 body was refreshed to PR11-current-reference.md. Its published
alpha-copy benchmark confirms this experiment's shape, full8-tactic AUTO,
3warmups/100cold-CUPTI samples, full-forward activity span, per-iteration
rankMAX then untrimmed median, and decode4–512/prefill reporting boundary.
Software versions differ as explicitly recorded; historical PR11 timings
are not used as this experiment's baseline. PR13 remains draft at002ef145
with pre-commit passing; its base is still406bc0d. GitHub identity restored
to zianglih after the private read.

## Ownership/driver preparation checks while EP8 runs

The R1 ownership CPU fixture passes pinned pre-commit Ruff and mypy on its
two owned source files. No candidate source was changed by those checks.
`counts-fence-correctness-review.md/.json` records the fresh source/PTX-model
review and plan-only owned-port checks for counts_fence and store16_raw_counts.
No new race was identified within the stated early-reader, collective-launch
and nonoverflowing-count contract; this is not GPU proof for a future stack.

The final native driver is prepared/transferred, not run. It accepts explicit
source/packagehash/testedcommit and serializes uniform→EP4→EP8 through
benchmark_checked_final.py, preserving exact timing while checking completion.
Its hash and CPU failure-path validation are recorded in final-validation.md.
The PR evidence renderer now verifies all seven common tactic fields and
labels raw PERFORMANCE_CSV units as milliseconds. R1-pr-performance-v2.md is
CPU regeneration of the same R1 results, not a new measurement.

## R2 retained: raw-TMA probe removal on R1

Retain frozen store16_no_raw_peek (SHA85f18dc5...4171ff) as the new parent.
Exact native target disassembly: whole5112→5096; FC1perK225→220;
FC2perK231→223. Both phases retain four x16 stores,136 conversion/scale
instructions and their two five-opcode outlined blocking-wait helpers.
96REG/0STACK/0LOCAL, zeroLDL/STL/PMTRIG; source/ABI/config/artifact hashes pass.
Fresh uniform1.00557075x and nativeEP4decode1.01044581x support the user's
preference for small instruction reductions. EP8decode0.99066792x remains
a regression; EP8prefills0.998927/1.000041/0.981305x, T1/T2 ratios
0.81835/0.95723 with N128 choices, T32same-tactic0.96918 andT1280.98118
are preserved. This is not an all-shape improvement or proof of noise.

All26 native rows plus fresh uniform pass fixtures, output bits, source
closure and the scoped independent references. R2 is experimentally retained,
not yet applied to primary or owned-port validated. Primary remainsR1.
Next run is counts-after-r2 using store16_raw_counts: uniform+fullEP4/EP8
AUTO, then exact fixedN64/G512 uninstrumented codegen, serialized alone.
Incremental comparison is against R2, not olderR1 or002.

## Cumulative count-ready plus prefix fence rejected

Counts-after-R2 uniform324.642→330.723us (0.98161301x), sameN64/G512/epi.
Complete13row EP4 decodeGM0.98029014x; prefill0.989762/0.998840/1.003145x.
All paired source/fixture/output checks and scoped independent references
pass. Reject this addition; early isolatedR1 improvements cannot substitute
for actual retained-parent performance. See counts-after-r2-retention-review.

At2026-09-25T11:39:56Z, after verifying EP4's13 rows and source closure,
sentSIGTERM only to the exact EP8torchrun pid134211 with cache argument
counts-after-r2-ep8-cache. Record includes exact argv and reason in
results/counts-after-r2-ep8-stopped.json. This unfinished guard is preserved
and excluded, not a passed fullEP8 result or kernel failure. All GPU workers
and its driver exited; nvidia-smi showed no compute processes. Local launch
session4301 completed. No unrelated process was signaled.

Started run-counts-codegen-then-payload-r2.sh, PID135796: first collect the
rejected combination's exact fixedN64/G512 native codegen, then run
store16_raw_payload (SHA1bc75d6fa090a747ed0e54e6924feba94039c4cdf4f6c0da4207e371738950db)
as payload-after-r2, uniform/fullEP4/fullEP8 plus codegen. This source applies
the frozen parallel_payload feature only ontoR2. It is not retained.
The source was prepared/transferred earlier without executing it.

## Rejected counts codegen execution failure; static artifacts preserved

The separate counts-after-R2 export wrote all4 compiler records, manifests,
PTX/cubins/SASS/resource summaries, and the tactic record. Rank3 then exited
with hostSIGSEGV11 at2026-09-25T11:41:28Z; torchrun terminated its other ranks.
There is no PERFORMANCE_CSV or BENCHMARK_COMPLETE. The exact cause is unknown;
do not attribute it to the earlier guard cancellation or to CUPTI without
additional evidence. Static artifacts remain source/fingerprint-auditable
compilation evidence, but this diagnostic execution failed. It supplies no
new timing/correctness result. The candidate was already rejected by the
completed independent uniform/EP4 runs. Preserve the log and artifacts.

Because the queued script uses set-e, it correctly stopped before payload.
All processes exited, GPUs had no compute contexts and0MiB used. Started
payload-after-r2 separately with fresh processes/caches and
PYTHONFAULTHANDLER=1 (signal diagnostics only; timer/method unchanged).
Driver is results/payload-after-r2-driver.log. Counts is not rerun solely to
collect static artifacts that were already exported successfully.

## Retained R2 ownership committed

Commit55cd345d57ccc56327966201bd0725767a11593a owns the selected transform and
five reachable transport tracing methods. All3protectedfiles match PRbase406bc0d;
AST/source-origin/scopedprecommit checks pass. Frozen git-archive snapshot
retained_owned_r2 packageSHAa7001bd59e04b03b372ba4315b3cad8cdcfd7e2db40a96006a5a987c08939e29
is copied toC2. No payload/countoverlap is in this port. NoGPUfinal-source
validation yet; publishedPR13 still002, no upstreamsync.

## Payload on retained R2: complete native sweep

All 27 rows pass source, fixture, output and cache closure: 160 paired rank
outputs, independent references at uniform global1024/all4 and native
global128/all4+all8. Uniform 324.642→330.659us (0.981803x); EP4 decodeGM
1.00149395x, prefill1.015769/1.011789/0.999451x. EP8 decodeGM0.979254x,
prefill0.971098/1.003851/0.988984x. EP8T4/T8/T16 regress0.942329/0.958157/
0.945988x; all rows/tactics remain in payload-after-r2-performance-audit.json.

Fixed codegen exported all4 ABIs and reached BENCHMARK_COMPLETE. Its old
benchmark.py wrapper never emits EXPERIMENT_COMPLETE_JSON or reference checks;
do not infer failure from that absent unsupported marker or call this numerical
qualification. One cold 0-warmup sample22.179705ms is diagnostic only.
Driver137483 exited; allGPUcontexts empty before the next launch.

At12:13UTC started fresh fixedtarget ABBA driver149011, label
payload-r2-fixed-confirmation-1. Exact frozenR2/payload, N64/G512/epilogue,
3warmup100coldCUPTI samples per run in A1/B1/B2/A2 order. This checks target
movement without replacing completed AUTO evidence. Final retention pending.

## Payload addition rejected; final owned gate started

Fresh fixed N64/G512/epilogue A/B/B/A completed with all source/fixture/
reference checks: R2 pooled330.499us, payload331.650us (approximately 0.9965x),
200 untrimmed cold-CUPTI samples per arm. Individual mediansA1330.851,
B1333.203, B2330.291, A2330.226us; MAD1.392/2.017us pooled. The fresh
control is slower than the older324.642us control, so the prior1.8%target
loss cannot be cleanly attributed. Fresh evidence still shows no advantage.

Reject payload onR2: EP4decode1.001494x, EP8decode0.979254x and no target
benefit; nativewhole5096→5104 (+8), FC1/FC2perK220/223 unchanged, no
resource improvement. Its barriers/numerics passed tested prototype scopes,
but that is not a reason to retain an unhelpful performance change. Keepall
logs, proposals and earlierR1results; no payload ownership port required.

At12:17UTC allABBAworkers exited and GPUs were empty. Started final owned
R1+R2 gatePID152026 (run-owned-r2-final.sh) on exactcommit55cd345/a7001bd.
It will runcodegen, fullnativebefore/afterafter-arm, freshwinnertrace, and
selectedtests serially. Explicit codegen exit0receipt is required; completed
markers followedbyteardownfailure do not qualify as success. NoGPUresult
fromthisfinalgate hascompleted yet. Devboxretained; nopush/upstreamsyncyet.

## Final owned code generation is identical to retained R2

Exact55cd345/a7001bd port completed fixedN64/G512/epilogue codegen using
benchmark_checked_final.py,3warmup100samples and all4 independent BF16
references. Explicit successful process exit receipt and source closure pass.
All4 compiled input ABIs have byte-identical cubins and identical complete
SASS instruction text to frozenR2: vector5096/strided5152 instructions,
FC1perK220/FC2perK223,4x16stores/136conversion-scale operations perphase,
unchanged outlinedwaits and REG96/STACK0/SHARED1024/LOCAL0. NoPMTRIG/spills.
Report native-codegen-owned-r2-final-analysis/audit.json. This validates the
ownership refactor for those compiled ABIs, not the pending full test matrix.

Final nativeAUTOuniform completed324.915us,N64/G512/epilogue; fullEP4/EP8
continue serially. A source-bound matching historical002 AUTO control exists
in no-peek-target-A1/A2:332.275/339.091us, pooled335.8745us (200samples).
Bothcontrols pass independentreferences, source/fixture/output/cachechecks;
useboth and explicitly report6.816us temporal difference. They are historical
orderedcontrols, not a fresh ABBA bracket around finalafter. Finalcomparison
awaits the overallnative drivercompletion and source-bound audit.

## Final EP4 negative rows trigger a fresh control

Completed finalowned EP4 comparedwithauthorizedold002 control: decodeGM
0.9857865155x. T1/T2/T4/T8/T16 are0.8742/0.8818/0.9419/0.9136/0.9594x;
prefill1.0091/1.0187/0.9985x. SameN64/G512T1 moved65.633→75.073us;
earlierexperimentalR2 same-tacticT1 was67.889us. Wrapperdiff shows only
pre-import attestations/metadata additions, no timer or numerical-hook change.
Original13rowtable remains in owned-r2-final-ep4-review-before.

To clarify this material variation, rootwill runonefresh full EP4control002
withtheexisting13rowAUTO/3warmup100coldmethod, thenreportit separately.
At12:35:49UTC sentSIGSTOP to onlyverifiedouterPID152026 (bashrun-owned-r2-final.sh).
Its nativechild153509 andEP8GPUworkers continue normally; stateverified.
Do notstartfreshcontroluntilchildfinishesandGPUsareempty. Aftercontroland
workerexit, SIGCONT verifiedouter152026 tocontinue trace/tests. NoGPUwork
wasinterrupted; theholdonlyinsertsone serialcontrolbeforethenextphase.
Receipt results/owned-r2-final-outer-hold.json. Firstkubectlstdinattempt lacked
-i and executed noPython; correctedexec-i producedtheverified receipt.

## Final native completion and fresh control launch — 2026-09-25 12:48 UTC

The final owned native driver completed uniform plus all thirteen EP4 and
EP8 rows and wrote its COMPLETE receipt. The child was a zombie awaiting its
held parent; all GPU contexts were empty. Parent 152026 remains deliberately
SIGSTOP-held. At 12:48:46 UTC, launched the prepared full original-002 EP4
control as PID 164320, with a fresh cache and the unchanged v2 timer/reference
wrapper. It runs alone. The original before/after tables remain authoritative
and unchanged; this additional reverse-order confirmation will be reported
separately. Once it finishes and workers exit, resume only the verified outer
152026 so the final tuned trace and selected numerical suites can run.

Final correctness evidence collector received an independent CPU review:
no actionable false-pass issue found in exact case/rank membership, JUnit
closure, source/helper identity, strict records, or incomplete preservation.
This is preparation evidence, not an assertion that GPU suites have passed.

## Unexpected pod loss and recovery — 2026-09-25 12:53 UTC

Old devbox pod disappeared while the fresh control was running. Kubernetes
reported Stopping container and later no pod/stateful work resources; node
hu-pdx-38 remains Ready. Cause is unknown. This task did not delete it.
Original held PID152026 and child/control PIDs are obsolete: never signal
these numbers on the replacement. Completed owned codegen and all27 native
rows had already been preserved locally and audited. The incomplete new
control is excluded; only its first two console observations were seen. No
final trace or final selected test had started.

Verified managed /usr/local/bin/h; initial effort-root invocation was rejected
because it requires a HAI checkout. Reissued the same managed binary from the
project-local read-only HAI context. Auto-update warned about private GitHub
authentication but the installed CLI successfully created a bare8xB300 devbox
hashinfer-trace-final-0925 in C2/ziangli/default queue, no size override. It
landed on the same hu-pdx-38 with the same26.05 image digest. Live NGC and
NVIDIA release table reconfirm26.05 is newestCUDA13.2 (26.06/07=13.3;26.08=13.4).
Fresh results/codegen are linked to task-owned persistent Weka paths. Inputs
are restored from frozen local snapshots, not reconstructed by hand.

The follow-up is bounded cap1 codegen and fixedT1 ABBA, then trace/tests. It
does not erase the completed original before/after table. Full details and
resource identities are in recovery-20260925/interruption.json.

Recovery runtime matches torch2.12.0a0+5aff3928d8.nv26.05, CUDA13.2,
DSL4.8.0/cuda-python13.2.0/cuda-core1.2.1/TVMFFI0.1.14.post1/CUPTI13.4.0.
Installed NVSHMEM wheel3.8.0 matches the original environment; the actually
loaded host library remains image-provided3.6.5, verified from process maps.
`nvshmem_info_get_version` reports API1.3, distinct from library release3.6.5.
At12:57:20UTC root launched only final retuned trace PID1728 while the bounded
T1 driver is prepared. No old native sweeps rerun. Numerical continuation
`run-owned-r2-recovery-numerics.sh` is prepared, not launched. One README
ownership-table documentation correction is local and does not change the
frozen tested package or test/benchmark source.

## Final trace complete and recovered validation queue — 2026-09-25 13:09 UTC

Fresh50sample native tuning selected N64/G512/epilogue,322.272us hot score.
All4baseline/reference and capture/baseline bitchecks pass. Source/cubin/
tracker/config native bindings match115points/rank,maxspan128B; timestamp
unit and fullrange/publisher structure audits pass on all4ranks. Selected
cluster contains bothCTAs of the full148CTA launch. Artifacts copied locally
and rank2 is visibly open in a new Codex Perfetto tab4. Pipeline analysis and
startup interpretation are under results/owned-r2-final-winner-1.

At13:03:03UTC launched outer4578: bounded nativeT1 codegen/ABBA followed by
selected numerical suites. T1 all4prototype/owned cubins and native text are
byte-identical. All6stage exits/source closures completed; ABBA audit pending.
Outer has moved to EP4case00; remaining26outercase total remains unqualified.
README-only scheduler-ownership correction committed867e9d2; package SHA
a7001bd and all test/benchmark bytes still match tested55cd345. README hooks
pass; source/test commits are not pushed yet.

## NativeT1 confirmation audit completed

All4 nativeH7168/cap1 input ABIs have byte-identical prototypeR2/ownedR2
cubins and fullnativeinstructiontext. Vector5096/strided5160 whole,
FC1perK220/FC2223,REG96/STACK0/SHARED1024/LOCAL0. All6stages have successful
exit/source/helper/fixture/tactic/output closures; T1 checks are finite,
repeat and paired hashes, with no independentT1oracle in these wrappers.

Fresh fixedN64/G512/epilogue original002→ownedABBA pooled200samples/arm:
69.3765→69.729us =.9949447x. A1/B1/B2/A2 medians64.5125/68.016/73.953/72.496us.
Control A2−A1=+7.9835us; candidate B2−B1=+5.937us. B2 quarters
75.649/74.497/67.713/73.632us are nonstationary. Neither old AUTO T1
65.6325→75.073us regression is declared resolved, nor is a precise causal
penalty assigned. Original fullmatrix unchanged. This confirms compiled
ownership parity and reports bounded timing honestly.

Audits: native-t1-confirmation-analysis/audit.{md,json}, timing-comparison.*.
Selective localcopy retains actuallogs/receipts/4ABIartifacts, excludingcaches.

## Draft PR updated while final selected tests run

Verified remote draftPR13 still002, clean local867, and ancestor relation.
Pushed002→867e9d2 without force. Updated title to "Add IKET profiling and
reduce W4A16 transform instructions" and published the reviewable50KB body
with completed native/codegen/T1/trace evidence; selected final tests are
explicitly pending. No comments, merge or upstream operations. Verified
OPEN/draft/exacthead. Private gh identityziang-and used, then restoredzianglih.
Receipt recovery-20260925/pr13-pushed-pending-tests.json. Final body must still
be refreshed after actual selected-test audit; this is not task completion.

## Final selected validation and publication — 2026-09-25

Outer4578 completed both boundedT1confirmation and all selected numerical
suites; driver emitted OWNED_R2_RECOVERY_FINAL_COMPLETE. All26cases /58rank
pytest outcomes pass, no failures/errors/skips. Strict finiteBF16bits pass
128combinations,384collective references and1,984collective pairs. Immutable
191file snapshot and independent audit verify exact source/test/helper
identity, every rank exit/JUnit, rawlog/JSONL equality and unique comparison
membership. Raw report: results/owned-r2-final-correctness-1.{md,json}.
Snapshot archive SHA256:
42ac11eb818f8bc00ed45ad8c898d879bae4eca0e4085377439f1933ac56251e.
No sanitizer/fullmatrix/model-serving qualification is claimed.

Final independent review found two documentation issues: the scheduler
source inventory named dispatch waiting but the actual modified range is
next-work-tile selection; and the uniform cold-CUPTI reproduction needs
the project-owned fixture adapter, not the repository H7168 benchmark or
hot trace tuning. Corrected README in docs-only commita1486e2 and added
exact adapter invocation/limitations to the PRbody. No kernel/test/benchmark
bytes changed from55cd345; README hooks pass. All52native rawCSVrows and
source/hash/ownership/reproduction-node claims were independently reviewed.

Pushed a1486e2fc63d5a54fe727b3123ee04b1e611c035. Updated draftPR13 body
(64,317bytes) with complete raw selected-test evidence and removed pending
claims. Read-back verified exact body/head/OPEN/draft state. Final pre-commit
CI SUCCESS: run36142491108/job108095458812. No follow-up comments, merge or
upstream sync. Activeghaccount restoredzianglih. Publication receipt:
recovery-20260925/pr13-final-published.json. PR-body.md mirrors publishedbody.

Ownership qualification is complete; retention.json current_parent is now
retained_owned_r2, with prototype parent identity preserved. Next candidate
must compare against this actual owned retained stack. Final devbox remains
Running/Ready onhu-pdx-38 with noGPUcomputeprocesses and zero restarts; it
was not released. Receipt recovery-20260925/final-idle-devbox.json.

## User-directed withdrawal of TMEM widening — 2026-09-25

User: "withdraw tmem widening since a few ep4 decode shapes regressed too much. refresh end to end before vs after speedup table". The prior small-instruction-reduction preference no longer retains R1. Commit5f2094b3b9f7cfbc724d84794632e278331ffd98 restores Repetition8; independent audit verifies this is the sole package change froma1486e2. Both TMEM probes, zero raw probes, owned methods and markers remain. Protected files still equal406bc0d. New packageSHAa0ee8df00da58df7b871ab7a45a93c89df3c5ed221a7cdc3daa0429dba686b8a. UpdatedREADME/guide and scopedprecommit pass.

Historical R1+R2 results remain immutable. Standalone raw-probe effects cannot be inferred by multiplying or subtracting prior stacked results. Launch14:57:40UTC outerPID37111 serially runs new uniform/nativeEP4/nativeEP8, fixedN64codegen, fresh trace and focused numerical coverage on keptsame-node devbox. No other GPUcomputeprocesses were active. New snapshot/sourcearchive/driver are inwithdraw-tmem-20260925. Original002 baseline reuse remains authorized; primarytable will explicitly preserve this historical-control boundary.

The first x8EP4T8 row remains156.753us versus historical002142.913us, close to prior x16after156.433us. This does not establish widening caused that regression. To address control drift, root will refresh the full original002 uniform/EP4/EP8 control after the serial candidate queue, using the identical wrapper/source fixture/timing contract. The primary table will compare those fresh controls to the fresh x8run, with after→before order explicitly disclosed; authorized historical control comparison stays separately visible. No selective replacement of shapes or ABBA claim. RemotecontrolpackageSHAverifiedc366a5e7. No extra GPU work has launched yet.

Published withdrawalcommit5f2094b to draftPR13 and changed title to "Add IKET profiling and remove W4A16 raw-weight probes". Body now describes x8/raw-only current scope and explicitly pending newmeasurements; oldx16evidence is archived/historical. Verifiedexacthead/body/OPEN/draft and restoredghaccountzianglih. Receiptwithdraw-tmem-20260925/published-pending.json. Finalmeasurementpublicationremainsoutstanding.

User followed up: "double check if the regression remains with fresh before vs after and relieves after removing the widening". Added a boundedthree-arm EP4 attribution plan overglobalT1/2/4/8/16. Eachshape runs original002 A, widened55cd345 B, x8raw-only5f2094b C, thenC/B/A; freshAUTO and100cold-L2CUPTI samples pertrial, preservingallraw rows andtactics. This directly tests withdrawalrelief in bothorders ratherthancomparing independentoldmedians. PrimaryfullEP4/EP8freshcontroltable staysseparate. Notlaunchedyet.

At15:11:02UTC root verified exactoutercommand forPID37111 and SIGSTOP-held only thatbashPID. Its nativechild continues normally through EP4/EP8. This moves freshoriginal andthree-arm timing immediately after completednativeafter data, ahead of remainingcodegen/trace/numericalwork. The active script/source stayedunchanged. Aftercontrolsfinish, rootmustverifyexactouteridentity andSIGCONT it; no otherprocessgrouporGPUjob wasstopped. Pause receiptresults/owned-raw-only-outer-pause.json.

At15:28:03UTC candidateuniform+EP4+EP8 completedall27rowswithdriverCOMPLETE. NoGPUprocessesremained. Usernewownershipguidanceauthorizesdirectmarker-onlypatchesinprotectedHashInferfiles andnaturalsharedW4helperextensions; redundantownedmethodcopieswillberemoved. Rootterminatedonlyheldouter37111afterexactcmdlineverification; itsoldsourcecodegen/trace/testcontinuationissuperseded,notthecompletedbenchmarks. Newcleanupqualificationwillprovenativecodeequivalencetofrozen5f. Freshoriginal002fullcontrolstartedPID47572 immediatelyonsameGPUs; launchreceiptresults/raw-only-fresh-before-launch.json.

Pre-launchCPUauditidentifiedcachepathnormalizationthroughpersistentresults symlink: benchmarklogusesreal/data/...cachepathwhilev1validatorassumedlogical/workspace/...path. CandidateGPUdataissuccessful; v1CPUauditstoppedwithoutclaimingsuccess. Preservefrozenv1helperbundleandprepareexplicitlogical/resolvedv2bindingwithsymlinknegativefixturesbeforeABC-CBAlaunch. NoGPUrerunorretryneeded.

## 2026-09-25 cleanup frozen while fresh control runs

User explicitly permits marker-only edits in HashInfer vendored upstream-protected files and natural shared-helper extensions. Removed six bulk method copies (net 1,010 lines): vendor transport receives only marker/predicate changes, shared transform adds default-on `use_raw_tma_probes`, MegaMoE passes False and retains x8 TMEM stores, two TMEM probes and early raw release. Fourteen CPU AST gates and scoped pre-commit passed. New cleanup commit `d453eb4f49f0bb38cf828f94c5588ec05d1b5b2c`, frozen package `b522ae25090f152c4fda9c364de7fdb256e542eaf1bb4c95c622a4b62670264e` in `retained_shared_raw_only`. Frozen A/B/C snapshots and attribution helper hashes unchanged. No GPU qualification is yet claimed for cleanup.

V2 six-file attribution runtime bundle uploaded with exact frozen hashes, CPU plan passed and saved as `withdraw-tmem-20260925/attribution-v2-remote-plan.jsonl`; no attribution GPU launch yet. Original full fresh control PID47572 remains active. After it completes, run `widening-attribution-1` ABC-CBA at EP4 global T1/2/4/8/16. Then qualify cleanup with ordinary codegen parity against measured5f at uniform N64/N128 (all four ABI variants), fresh autotuned trace and six selected numerical outer tests. Do not resume obsolete PID37111; its only completed portion is the native5f sweep.

The final publication will additionally use a direct full native sweep of cleanup d453eb4 (`shared-raw-only-native-1`) versus the fresh original002 control. This avoids relabeling measured5f timings as final-head timings based only on scoped codegen parity. The measured5f full sweep and ABC-CBA remain distinct withdrawal diagnostics. Root prepared `cleanup-20260925/run-cleanup-native.sh`; it has not launched.

Root queued the focused frozen-v2 attribution run with CPU-only dependency waiting, PID53599, `results/widening-attribution-1-driver.log`. It verifies fresh-before run COMPLETE, exact outer completion sentinel and no GPU processes before launching. At queue creation it was waiting; no attribution measurements had begun.

## 2026-09-25 final cleanup qualification queued

Frozen codegen9-file bundle uploaded and remote CPU plan passed. Nine runtime trace/numerical dependencies are verified and the EP4/EP8/tails CPU plans pass with source-contract-v2 SHA `2ba03ca07097d254f2cfd02189a34bdecd7500c53711fbe177d2f95e0162ccb8`. An initial broader upload safely stopped on an older remote local-only collector (`pull_causal_artifacts.py`); that file was left unchanged, and only actual runtime dependencies were subsequently verified/uploaded. No benchmark or GPU failure occurred.

Root qualification queue PID57812 was created at2026-09-25T15:54:59.888755Z, waiting on attribution queue53599. After attribution success sentinel and noGPUprocess check, it runs codegen five stages, direct final-head full native sweep, new autotuned uniform trace, EP4two/EP8one/EP2three numerical cases. Every output is fresh; first failure stops continuation. Outer logfile `results/cleanup-qualification-driver.log`, script/launch hashes in `cleanup-20260925/qualification-queue-launch.json`. No final-source GPU results yet.

Fresh original002 control completed all27 rows and outer sentinel; PID47572 exited. At15:56UTC root observed attribution53599 started T1-A1 after verified idle GPU. Cleanup queue57812 remains waiting. Freshcontrol collection/audit proceeds in parallel onCPU.

## Fresh original002 versus restored-x8 candidate5f audit

`withdraw-tmem-20260925/fresh-candidate-5f-evidence-1/` passes all27rows, exact source/fixture/cache/output closure and selected independent references. Uniform328.7065→324.4500us=1.013119125x. Native decodeGM EP4 0.995409997x, EP8 1.009369216x. Fresh EP4 sparse deficits remain: T1 68.657→73.696us (0.931625x, sameN64/G1024/epi), T2 91.6325→98.7365us (0.928051x, sameN64/G512/epi), T4 110.800→115.6015us (0.958465x, G1024→G512), T8 149.329→156.753us (0.952639x, sameN64/G1024/epi). T16 improves204.258→198.6895us=1.028026x. Ordered candidate→baseline sweeps (BA), notABBA; no width attribution or finalcleanup-head timing claim. All rawrows and negatives retained. ABC-CBA remains active to distinguish original/widened/x8 and tactic/order drift.

## Provisional completed T1 ABC-CBA block (full30trial experiment still running)

All six T1trials/600samples passed independent partial-block checks; selected19-file snapshot in `withdraw-tmem-20260925/partial-t1-block-1/`. A1=71.265us, B1=80.161us, C1=69.969us, C2=69.0725us, B2=73.0405us, A2=77.9205us. A=original002, B=widened55cd345, C=x8raw-only5f. AllN64/G1024/epi except B2G512. B/C=1.145664509x forward,1.057446886x reverse; reverse tacticconfounded. A/C=1.018522489x forward,1.128097289x reverse: earlier fullsweepT1 deficit is not reproduced here. OriginalA drift+6.6555us. No allshape or cleanwidth-causalclaim from thispartialblock; full30 remains required. If a latermatchedfollowup is warranted, fixedT1N64/G1024/epiABC-CBA is boundedoption, currentlyunlaunched/unqueued.

Cleanup d453eb4 pushed fast-forward to draftPR13. Pending body `cleanup-20260925/PR-body-pending.md` published and read back exactly; receipt `published-pending.json` confirms draft/head/title. It includes the completed fresh5f diagnostic table, explicitly separated from currentd453 GPUqualification stillrunning. No comments/merge/upstreamsync. GitHubCLIprivateziang-and verified for operation, publiczianglih restored andverified afterward.

Independent B55cd345→C5f2094b source review confirms exactly one executable literal across all83 packagePythonfiles: decoded-weight TMEM Repetition16→8 (oldownedkernel line1629). EntirefileAST is identical after replacing thisconstant; allotherpackagebytesmatch. Botharmshaverawprobes0/TMEMprobes2 and identical ordinary enable_iketFalse compilation. B/C isolateswidth atsourcelevel; runtimeAUTOchoices and timevariation remain disclosed. Publishedcleanupd453 pre-commit CIpassed (actions run36158805344), receipt `cleanup-20260925/ci-source-head.json`; GitHubCLIzianglih restored.

ProvisionalT2 six-trialblock: A1 113.169/N64/G512, B1 97.025/N64/G512, C1 89.409/N64/G512, C2 95.169/N128/G512, B2 94.2735/N128/G1024, A2 88.9605/N64/G512us, allepi. B/C flips1.085182x→0.990590x; A/C flips1.265745x→0.934763x; A same-tacticdrift−24.2085us. T2 doesnotestablishconsistentwithdrawalrelief. Source/output/cache/receiptchecks pass in `withdraw-tmem-20260925/partial-t2-block-1/block-analysis.json`; full30trialauditpending.

At16:33UTC root observed all30trialWIDENING_ATTRIBUTION_COMPLETE and ATTRIBUTION_QUEUE_COMPLETE; PID53599 exitednormally. Cleanupqueue57812 passed itsdependency/idle checks and started cleanup-codegen-1. Full3,000sampleattributioncollection/auditunderway; no codegencompletionclaimyet.

## Complete fresh width-attribution result

`withdraw-tmem-20260925/attribution-evidence-1/attribution.{json,md}` passes all30serialtrials and3,000untrimmedsamples;92files collected, archiveSHA `b5a1c2871ce1c1f465a9633e0da28c6673a147cd051b12325e047f8a12fd8132`. CompactPRsection `compact-review.md` containsall5pooledrows, bothorderB/C, all30rawtrialmedians/dispersion/tactics/source/helperhashes. B/Cpooled T1/2/4/8/16=1.115357/1.027232/0.967196/0.987702/1.011907x. T1x8winsbothorders; T4x8losesboth; T2/T8/T16flipdirection. T8/T16havesametacticallsixtrials. EarlierlargeT2/T8widevsoriginalregressions donotreproduceconsistently. SourcelevelB/Cisolateswidth, butAUTO/timevariationprecludegeneralcausalbenefitclaim. Noadditionalmatched-tacticGPUfollowupisplanned; preserveallrawsamples andkeepx8peruserrequest.

## Cleanup generated-code qualification completed

`cleanup-codegen-1` completed all five stages before the final native sweep. Independent local audit collected 180 selected files in `results/cleanup-codegen-1-collected` and passed `results/cleanup-codegen-1-local-audit/audit.json`. All eight 5f→d453 comparisons (N64/N128 × Int32/Int64 × vector/strided hidden) have byte-identical PTX, CUBIN, full SASS and complete resource records. Twenty compiled variants use 96 registers, zero stack/local memory, no LDL/STL/PMTRIG. Each of five stages executed one ABI with four-rank finite/repeated and independent BF16 reference checks; other ABIs are compilation coverage.

Fresh original002→finald453 N64, all four ABIs: whole static instructions −16; FC1/FC2 per-K bodies −5/−8; native TRYWAIT whole106→102. Original blocking raw waits and both TMEM probes remain. No static-count speedup inference; codegen timing samples are excluded from performance tables. Final review found no cleanup code issues. Full details in `cleanup-20260925/codegen-pr-evidence.md`.

The serial queue advanced to direct final-head `shared-raw-only-native-1`; uniform row complete and native EP4 in progress. Final trace and selected numerical suites still follow in order. No overlapping GPU launches.

## Direct final cleanup native benchmark completed and audited

`shared-raw-only-native-1` completed all 27 rows on frozen d453/b522. `withdraw-tmem-20260925/final-cleanup-native-evidence-1/audit.json` passes source/fixture/cache/output/tactic closure against fresh original002. Both arms retain all 5,400 untrimmed samples; 160 paired rank/shape outputs and 16 independent-reference rank checks per arm pass. Complete table, raw console CSV and exact tactics are in `pr-section.md`; machine-readable summary is `pr-section.json`.

Native H7168 decode GM (global T4–512): EP4 1.003700069x, EP8 1.021245598x. Separate H6144 uniform target: 328.7065→337.0745 us, **0.975174628x** (regression), same N64/G512/epi tactic. EP4 T2/T8 remain 0.965925x/0.973404x in this ordered sweep. Prefill regressions are retained: EP4 T8192 0.963719x, EP8 T8192 0.970947x, with all other rows visible. No universal speedup or width-causal claim.

Original sweep completion and final driver-provenance host timestamps are separated by 42m21.388s, with the full ABC-CBA and cleanup codegen between; this is ordered A→B, not ABBA, and these are orchestration timestamps rather than kernel timestamps. Final-source uniform timing differs from pre-cleanup5f despite exact N64/G512 generated-code parity; the ordered data cannot attribute that difference to the cleanup. No selective replacement of the final table with earlier better timings.

Retain raw-probe removal under the user's instruction-reduction preference (fresh x8 SASS −16 whole, −5/−8 FC1/FC2 per-K) with mixed measured performance explicitly recorded. Widening remains withdrawn. No new optimization or extra timing repeat is introduced during qualification. Fresh native IKET winner capture and selected numerical suites continue in the serial queue.

## Fresh final-source winner trace audited and displayed

`shared-raw-only-winner-1` passed source/capture/config/PID/CUBIN, ordered/nested ranges, and each rank's own Perfetto timestamp-unit checks. All eight hot-event tactics were freshly evaluated (50 samples/rank/tactic); winner candidate2, M256/N64/K256, G512, epi_warps, score323.119998us (MAX of four rank medians). Hot-event tuning is separate from cold-CUPTI performance. Four baseline-reference and four capture-baseline finite BF16 comparisons pass with zero mismatches; one target capture per rank. Actual115 native points/rank, maxspan208bytes; these are newly audited counts, not carried from history. OriginalCUBIN SHA91a083553ba0dc3cf0f3400115dfd73a22219b4a781c3e5711f17fb192f49d14.

Rank2 detailed analysis includes34 worktiles/480 K iterations and all16 transform warps across both recordedCTAs. Its initial input-publication subsection is2545.344us in this instrumented distributed capture; this is not the native hot/cold latency. After that anchor, CTA0 first weight/decode/MMA issue appear3.520/6.144/35.392us later. FC1/FC2 median MMA decoded-weight wait is0.736us perK, activationwait0.064us. Same-K MMA/free-slot overlap medianmeanperproducer4ns; producer waits for a laterK must not be conflated with the current consumerK. Explicit TMEM waits omit retained TMEM readiness probes outside their ranges; unmarked gaps also include loop/marker work. No hardware-cause or full-grid-utilization inference.

Evidence: `cleanup-20260925/trace-analysis-1/` and `results/shared-raw-only-winner-1/`. Loaded a byte-identical display copy `cleanup-20260925/d453eb4-ep4-uniform256-rank2.pftrace` in new IABtab5, verified visible title and warp tracks, and marked it deliverable. View zooms past initial publication to roughly2.55–3.13ms with CTA0Warp4 MMA and Warp12/13 transform visible; old traces remain untouched. Display/source hash receipt: `cleanup-20260925/perfetto-file.json`.

Numerical EP4 selected suite is active; EP8 and tails follow. No numerical completion is implied by the trace or benchmark passes.


## Final cleanup qualification and publication complete — 2026-09-25T17:35:52.026750+00:00

All four accepted audits are `passed: true` for d453eb4/b522ae25: direct full native performance, eight-way normal codegen parity, fresh winner trace and six selected numerical cases. `cleanup-20260925/final-qualification.json` indexes their exact files and SHA256 values. Independent peer reviews found no source, numerical, trace, native-table or final-body issues; all reproduced Bash blocks pass syntax checks.

Final numerics: 6 outer cases, 22 rank pytest passes, 96 strict combinations, 288 collective reference comparisons and 1,488 unique pairs. Zero failed/error/skipped rank outcomes; accepted strict comparisons are finite BF16 exact. All 22 literal pytest summaries are preserved, including one interleaved warning/summary line. The three tail/wrap cases remain separate from the strict all-tactics matrix. Snapshot: `cleanup-20260925/numerical-snapshot-1` (71 selected files); audit: `numerical-analysis-1/audit.json`. All 18 frozen qualification dependencies remain unchanged.

Published the 50,890-byte final body to draft HashInfer PR13 at d453eb4; exact body read-back, OPEN/draft state, unchanged head and pre-commit CI SUCCESS verified. Receipt: `cleanup-20260925/published-final.json`. Root `PR-body.md` and `optimization/FINAL-PR-BODY-DRAFT.md` now mirror that publication. No comments, merge, upstream sync or trace files were added to the repository. GitHub private identity ziang-and was verified for the operation; zianglih was restored and verified afterward. Source checkout remains clean.

Current retained comparison parent is `retained_shared_raw_only`. The final before/after table keeps native decode EP4 1.003700x / EP8 1.021246x, uniform 0.975175x and every sparse/prefill negative. Raw-probe removal remains a small verified instruction reduction with mixed runtime results. X16 remains withdrawn; ABC-CBA does not prove universal regression relief. Historical x16 and pre-cleanup x8 results remain explicitly separate.

All GPU stages and the serial queue completed; PID57812 exited. Devbox hashinfer-trace-final-0925 is kept Running/Ready on hu-pdx-38, zero restarts and no GPU compute processes verified at 17:27:29UTC. No further GPU work is queued. Fresh rank2 Perfetto tab5 remains a deliverable, showing the current-source pipeline beyond initial publication. Current operational notes and future-iteration entrypoint are `CURRENT.md` and the completed withdrawal runbook.


## Upstream IKET import alignment — 2026-09-25T20:20:55.943934+00:00

- FlashInfer main `bf82326b0c524048c7f810da9f0022f8316ac3ff` and PR5019 head `19e8aebb541684df09e12cc79610338aa429a2cf` contain no root `flashinfer/_compat.py`; neither recursive tree is truncated.
- Both contain the vendored `flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/iket_compat.py`, which tries experimental IKET, then older IKET, then no-op markers.
- PR5019's [epilogue](https://github.com/zianglih/flashinfer/blob/19e8aebb541684df09e12cc79610338aa429a2cf/flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/epilogue.py#L22) imports `iket` through the existing public `cutedsl_megamoe` package. Its scheduler tries old native IKET, then the facade. Its shared W4A16 helper has no IKET import yet. Downloaded source and trees are saved beside this note.

## Change and validation

Deleted the new root `hashinfer/_compat.py`, which was an exact 50-line duplicate of the unchanged vendor helper. Five consumers (kernel, epilogue, scheduler, shared transform and capture harness) now use `from hashinfer.moe_ep.kernel_src.sm100.cutedsl_megamoe import iket`. Future namespace translation matches the existing upstream epilogue path. No protected-source or kernel algorithm changes occur in this commit.

`source-audit.json` and `change.patch` prove the five files differ only by that import replacement and the removed duplicate matches the still-unchanged canonical helper. All five compile as Python syntax; scoped pre-commit (including mypy/Ruff) and `git diff --check` pass. Independent import-graph review found no cycle or new optional dependency: backend/kernel loading and CUDA/NVSHMEM initialization remain lazy; torch is already required. This is source review, not a fresh runtime import test.

The previously kept C2 pod is now absent (live NotFound; `devbox-status.json`). This turn did not release it, allocate another node, or use another task's GPU. No C2 runtime smoke, CUDA compilation, timing, numerics or trace was rerun for this import-only commit. Published benchmark/codegen/numerical/trace results retain their exact d453eb4 identity; no speedup or generated-code-parity claim is newly made for this head. Frozen evidence/snapshots remain unchanged.

Current commit: `f47315b841340c21f2c9c25ac3f3b63055817672`; full local audit and upstream snapshots: `upstream-iket-alignment-20260925/`.

Published import-alignment commit f47315b to existing draft PR13 and updated its body; exact readback, draft state and new-head pre-commit CI SUCCESS verified (`upstream-iket-alignment-20260925/published.json`, `completion.json`). Performance and all later evidence sections are byte-identical to prior body. GitHub identity restored to verified zianglih; checkout clean.


## Remaining optimization withdrawn; tracing-only scope — 2026-09-25T20:49:23.992078+00:00

The user explicitly dropped the remaining raw-TMA probe optimization and requested a tracing-only PR. Commit `fd4885d7e6af84283521681f09094762d73b5611` restores the original initial/next raw-weight readiness probes and passes their status into the original mandatory wait. It removes the `use_raw_tma_probes` constructor argument, attribute, branches and MegaMoE opt-out. The x16 widening remains withdrawn; original x8 stores are kept.

Native IKET markers, explanatory names and payloads, uniform EP4 256-token fixture, full-grid eight-tactic tuning and winner capture remain. Shared transform and inherited transport are reused; vendor edits are marker-only. The unchanged existing IKET compatibility export remains the sole fallback. Repository documentation now describes the restored raw-stage probes inside and outside marker ranges and fixes stale root-wrapper examples.

## Source and validation

- PR: [private repository link omitted] (draft, unmerged).
- Current source: `fd4885d7e6af84283521681f09094762d73b5611`; package SHA256 `df90d2d0aa8f65881624fef55fe7bcd8e1aa91a1227124796947a45e685cd716`; immutable complete source snapshot `../tracing_only`.
- `committed-ast-audit.json`: all19 source checks pass against PR base406bc0d; all5 changed kernel files match computational AST after narrow marker/import/docstring removal. Exact constructor, probes, waits, x8store, unchanged owned transport/compat/facade, and no new helper/transform duplication checked. See `audit_tracing_only.py` for the allowed normalization.
- `fixture-tests.json`: all3 existing routing-fixture functions pass via stdlib runpy (not pytest).
- `syntax-checks.json`: all7 changed Python files compile as syntax.
- `pre-commit.log`, `style-checks.json`: complete PR affected-file scope passes, including mypy/Ruff; git diff check clean.
- Current-head pre-commit CI passed: [private repository link omitted]
- `devbox-status.json`: previously kept C2 pod is absent. No release, replacement, new GPU runtime/codegen/numerical/timing test or fresh trace occurred this turn. Structural parity is not a generated-code parity claim.

## Evidence boundaries

The active PR body/title describe tracing only. Optimization speedup and SASS sections were removed from that body; their original outputs and the complete prior body are preserved under `../withdraw-tmem-20260925`, `../cleanup-20260925` and `../upstream-iket-alignment-20260925`. The historical d453/raw-probe-off trace remains available with its exact source, candidate scores and checks; it must not be relabeled as a fresh capture of the restored implementation. Its detailed load/decode subrange attribution differs now that the next-stage probe is restored.

No pipeline performance optimization remains retained. The next optimization must compare against `tracing_only` as its source baseline and obtain the necessary fresh GPU evidence. Neither prior d453 timings nor the old source's winner are qualification of current fd4885d. All frozen experiment snapshots/helpers and traces are preserved. No upstream synchronization or merge is authorized.

Historical active-state documents were copied into `tracing-only-20260925/prior-*` before replacement. The old speedup/SASS evidence remains preserved and is removed only from the active PR narrative.

Published tracing-only commit `fd4885d` and renamed draft PR13 to “Add native IKET tracing for W4A16 MegaMoE”. Exact body readback, unchanged base/head, OPEN/draft state and current-head pre-commit CI SUCCESS verified. `tracing-only-20260925/completion.json` and `published.json` preserve the receipts. Checkout clean;9 PR files, no trace/disassembly artifacts. Verified GitHub identity restored to zianglih. No upstream sync, merge, GPU allocation or release.


## 128-global-token trace fixture and authorized upstream tracing port — 2026-09-25

Current local HashInfer commit `40d0ceb67aa67dbf366ff61f85309e8ef53aa743` changes the default trace fixture to 32 tokens/rank, 128 globally, on EP4 H6144/I2048/E256/top8. Each token selects 8 distinct experts; each expert receives 4 tokens globally, one from each source rank. Explicit 1/rank and 256/rank fixtures remain available. This four-file harness/test/documentation change leaves all kernel files unchanged from tracing-only `fd4885d7e6af84283521681f09094762d73b5611`. Original probes/waits and x8 stores remain; no pipeline optimization is retained and no end-to-end performance claim is made.

`trace128-20260925/cpu-fixture-audit.json` passes all 4 fixture functions and 8 baseline/capture CLI checks at the committed source, with file hashes and no GPU imports/execution. `trace128-20260925/committed-ast-audit.json` passes all 19 structural checks at 40d0ceb against PR base406bc0d. These are CPU checks, not native codegen, numerics or trace qualification. The prior frozen `tracing_only` snapshot/package and fd4885 publication receipts remain unchanged; a new publication receipt is pending.

The user now explicitly authorizes a bounded four-file W4A16 tracing port to public FlashInfer PR5019, superseding the earlier no-upstream-sync restriction for this scope. Its local commit is `74ba96d551640938edde68d628b36ba404a7f331`. Protected vendor source, scripts, tests and documentation are excluded from the port; no merge is authorized. GPU tests and push remain pending. The independent upstream effort keeps its own source and evidence under `flashinfer-pr5019-merge-sync-20260921`.

Fresh C2/infra devbox `fi-w4a16-trace-0925` is kept alive on `hu-pdx-38` with 8 B300 GPUs, using `nvcr.io/nvidia/pytorch:26.05-py3` at digest `sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`. FlashInfer GPU tests run first; HashInfer's fresh 128-token eight-tactic full-grid baseline, winner reference validation and native IKET capture/trace audit are pending in the serial queue. Prior absent-pod receipts remain historical; do not resume old queues/PIDs. All historical benchmark, codegen, qualification and trace artifacts remain preserved and must not be relabeled as current-source results.


## 2026-09-25 — Published tracing sync and default128-global-token capture

Draft PR13 [private repository link omitted] is published at `40d0ceb67aa67dbf366ff61f85309e8ef53aa743`. The default is **128 global tokens on EP4 (32/rank)**, H6144/I2048/E256/top8, uniform routing: eight distinct experts/token, four tokens/expert globally and one/expert/source. No pipeline optimization remains retained; original raw-TMA/TMEM probes and x8 stores remain.

The fresh C2 run tested all eight native deterministic tactics. Winner: **N64/G1024/epi_warps**, maximum rank-median graph-event score **274.703994 µs**. All four ranks pass independent-reference and capture-baseline BF16 bit checks (196,608 elements/rank), source/CUBIN/115-point binding, balanced per-K markers and own-Perfetto nanosecond checks. Full launch148CTA/74CGA; recorded cluster2CTA/40warp tracks per rank. These are tactic-selection and trace results, not end-to-end speedup claims. CPU fixture/CLI/structural checks, scoped pre-commit and current-head CI pass.

W4A16 tracing is also published to [FlashInfer PR5019](https://github.com/flashinfer-ai/flashinfer/pull/5019) at `74ba96d551640938edde68d628b36ba404a7f331`. Four implementation files only; protected source, scripts, new tests and documentation excluded. Fifteen existing cases/36 rank reports plus native IKET EP4 smoke passed on C2. Upstream GPU CI awaits maintainer authorization; neither PR was merged.

C2/infra devbox **fi-w4a16-trace-0925** remains on **hu-pdx-38**,8B300, image `nvcr.io/nvidia/pytorch:26.05-py3` with the recorded digest. GPU work is finished; keep the devbox for iteration.

- [Fresh audit and all8 candidate scores](optimization/trace128-20260925/audit-1/audit.md)
- [Fresh rank2 trace](optimization/trace128-20260925/40d0ceb-ep4-global128-rank2.pftrace), open in Perfetto tab6
- [Current PR body](optimization/trace128-20260925/PR-body.md) and [publication receipt](optimization/trace128-20260925/published.json)
- [Chronological ledger](optimization/EXPERIMENTS.md) and [retention record](optimization/retention.json)
- [Tracing guide](hashinfer/docs/w4a16-device-tracing.md)

Trace files and experiment artifacts stay outside the repositories/PRs. Preserve frozen historical evidence; older d453/raw-probe-off and256/rank results are not current measurements. Shared playground/repos remains read-only. Do not resume old absent-pod queues/PIDs.


## 2026-09-25 — Native SM103 target audit and controlled SM100-family comparison started

The user noted Sm100 in the trace symbol and requested established FlashInfer architecture-selection patterns plus a same-methodology comparison. At clean HashInfer40d0ceb and FlashInfer74ba96d, source review and originaltrace CUBIN inspection establish that the B300 kernel already targets`sm_103a`; Sm100 is the shared implementation class/source namespace. CuTe4.8 detectsCC10.0→100a andCC10.3→103a. No missing production targetdispatch has been found and no kernel source change is proposed.

The meaningful B300 diagnostic is`sm_100f` versus native`sm_103a`, selected before CuTe imports in fresh processes;100a is an exact-architecture target and cannot stand in for compatible100f. The matched study source is40d0ceb, packageSHA256df90d2d0aa8f65881624fef55fe7bcd8e1aa91a1227124796947a45e685cd716. Prior performance evidence is historical and is not reused as the control.

The owning artifactdirectory is`arch-target-20260925/`, with livePR11methodology snapshot, source/runtime receipts and exact FlashInfer/CuTe source references. Benchmark preparation is in progress; no new timing or retention conclusion yet. Use fullforward cold-L2 CUDA-graph CUPTI,3warmups/100samples, rankMAX then untrimmed medians, freshnativeAUTO and balancedABBA. StandardEP4/EP8 H7168 thirteen-token sweep and separateuniform128global EP4 H6144 fixture. Preserve trace/kernel naming for future upstreamsync, and keepC2devbox allocated.


## 2026-09-26 UTC / September25 local — Architecture study completed; native default retained

Same-source HashInfer40d0ceb B300 comparison completed12 serial trials (EP4 native, EP8 native and separate EP4 uniform128, each100f/103a/103a/100f). The existing trace already contains nativeSM103a binaries. No missing target dispatch, source change, renamed implementation, PR update or retained optimization results from this study. CuTe capability detection already mapsB200→100a/B300→103a.

The complete independent audit passes108 cold rows/10,800 samples,51,200 hot tuning samples,640 winner exports/finite repeated-output records,160 cross-run matching output keys and64 independent-reference records at globalT128. Ratios are100f latency/103a latency. Decode4–512 geometric means: EP4 pooled0.994497×, first/reverse1.009698/0.988683; EP8 pooled1.005684×, first/reverse0.994808/1.014956. Uniform128:279.842/287.251µs, pooled0.974207×, first/reverse1.005275/0.961974. Direction changes and AUTO tactic differences prevent an aggregate or uniform-workload speedup claim. All13 native shapes and all27 pooled rows remain visible.

Static code comparison finds identical instruction counts, opcode histograms and resources in384 exact-matched cross-target pairs; instructions differ in ordering, register choice and reuse annotations.228 same-target repeat pairs have identical whole CUBINs.108 unmatched configuration groups are excluded. No static instruction reduction supports a target change.

Final decision and limitations: [DECISION](arch-target-20260925/DECISION.md). [Complete performance table](arch-target-20260925/PERFORMANCE.md), [order/tactic details](arch-target-20260925/final-summary-1.md), [raw audit](arch-target-20260925/final-audit-1.json), [static code findings](arch-target-20260925/codegen-final-findings.md). The verified123,327,104-byte selective archive has SHA25683d949efb3b59f1d88dd28a77759fcd055ee382e1d52b6cbc3a3932eec007793; failed helper attempts and smoke remain excluded. OnlyB300 was timed. RuntimeCUDA13.2 is distinct from the DSL bundledNVVM23/CUDA13.4 compiler recorded in PTX.

C2/infra fi-w4a16-trace-0925 remains allocated onhu-pdx-38. No GPU compute processes at2026-09-26T00:28:47Z; clean remoteHashInfer40d0ceb. LocalHashInfer40d0ceb andFlashInfer74ba96d are clean and match their tracked branches. Keep the devbox and all local artifacts for iteration.


## 2026-09-25 — WG2 token-pull visibility audit

Current rank2 trace contains `dispatch_fetch_input_tokens` only on CTA0/warp8:14.432–23.488µs relative to the first marker,9.056µs duration. All eight recorded WG2 warps have the outer `dispatch_exchange_tokens`. Inherited dispatcher calls the pull helper for every participating warp, but inner phase markers are guarded by CTA0/local-warp0. Missing labels on other warps are incomplete marker coverage, not skipped pulling. Read-only source/capture audit; no new run or code/PR change. [Exact evidence and semantics](token-pull-visibility-20260925/FINDING.md).


## 2026-09-25 — Expanded warp marker coverage started

User authorizes improving misleading/missing marker coverage, pushingHashInfer and freshwinnertrace; upstreamFlashInfer sync explicitly deferred. Localcommitcaa61896ea7cb7ec13ae11baff20ea8696cce120 addsall-warpdispatchphases andactualpublishercoverage; separatesperKproducerwait/issue; clarifiesreadinesschecks/epiloguework; exposesepiloguereadinessrendezvous; emitsdrain/reductiononlyonexecutingwarps. All19PR-basecomputationalASTcheckspass,fixture/stylecheckspass. Freshdefault128globalEP4autotune/captureinprogressonkeptC2devbox. [Live ledger](marker-coverage-20260925/LIVE.md).


## 2026-09-26 UTC — Expanded marker coverage validated and pushed

FinalHashInfercommitcd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7 pushedtoPR13; current-headprecommitCISUCCESS. Firstunpublishedcaa6189attemptfailedbeforetimingbecausefourlabels exceededIKET32bytes; finalall61markernamessatisfycontract. Savedoldbundle/runner/source/ASTreceiptandfailedlog. No computationalchanges; fullPRAST19checksand4fixturefunctionspass.

Freshdefault128globalEP4uniformworkloadautotuned8tactics/1,600hoteventsamples. WinnerN64/G1024/epi_warps274.111986µs. Baseline/capturepassall4ranks:zeroBF16bitmismatches/nonfiniteoutputs. Fullaudit2verifies8whole-dispatchranges,8/4/8publicationphasecounts,8WG2drainranges,16actualcombinerangesperrank,perKloader/transformandepiloguetaskjoins.133originalPMTRIGsitesbijectivelybound(maxspan176bytes),originalCUBINSHAf14699fe9ca1c4c6c761745f64355fe92c10c91695f880c7af659fc350719cf3; source+fixtureSHAd19f31dc6400a2f20d3bd6c64f539baea16841f88771d05aef55cc83a6d03bb9. CUBINdeclaresSM103a. EachoriginalJSONendpointmatchesownPerfettons. Audit1externaladaptermissingdelegatefailurepreserved; correctedCPUauditorreran samecapture, noGPUrerun.

[Audit](marker-coverage-20260925/audit-2/audit.md), [newrank2trace](marker-coverage-20260925/cd7cc07-ep4-global128-rank2.pftrace), [newobservations](marker-coverage-20260925/PR-trace-snippet-v2.md). InputdispatchfinishesnearstartupinrecordedCGA; producerwaitrangesrevealslotbackpressurethroughcompute. Instrumenteddurationsnotnativeperformanceorallgridutilization. Nooptimizationretained. Upstreamsyncawaitsuserauthorization. Devboxretained.

PR13 evidence published and exact readback verified on cd7cc07; current-head pre-commit CI passed. HashInfer checkout is clean and pushed. Upstream FlashInfer remains clean at 74ba96d. Publication and evidence hashes are saved in published.json and completion.json. Devbox retained; UI opening remains blocked by the locked Mac.

### Follow-up: two active combine groups at 128 global tokens

Confirmed group-major work assignment leaves WG0/WG1 idle at 32 local output rows. WG3 covers 18,944 chunks; WG4 covers 5,632; all 24,576 chunks covered exactly once. All four native traces match the derived CTA0/1 participants. Parent mapping unchanged; moving the marker into the work loop removed empty ranges. [Derivation](marker-coverage-20260925/combine-assignment.md), [receipt](marker-coverage-20260925/combine-assignment-check.json). No source changes or GPU rerun.

### Combine granularity: current arithmetic and prior narrower-width trials

[Analysis](marker-coverage-20260925/combine-granularity.md) documents fixed8 elements/lane, proposed4/2 effects, independent warp striping, and freshly inspected older EP8/H7168 rejection evidence. No current EP4 gain is claimed and no source or GPU changes were made.

### True 256-bit combine assessment; retain current128

User keeps current128. [Feasibility note](marker-coverage-20260925/combine-256-feasibility.md) distinguishes native256 hardware support and current epilogue STG256 from prior adjacent/coalesced16 combine trials that emitted two128-bit halves. Current combine remains unchanged; honest32-byte alignment/fallback and prefill before/after timing are needed for a separate trial. No new benchmark result.

### Public API alignment ownership

[Source audit](marker-coverage-20260925/alignment-ownership.md): normal SGLang integration supplies inputs and obtains outputs from FlashInfer; FlashInfer allocates both symmetric combine partials and final y.32-byte enforcement belongs inside FlashInfer. Only lower-level caller-provided-output APIs need alignment-based selection/fallback. No source or runtime changes.


## 2026-09-26 — Remaining owned marker sync and global4096 trace

User authorized the remaining W4A16 marker-only sync to FlashInfer PR5019 and an additional4096global-token trace shape. HashInfer4ba4b61 adds named128/4096 shapes; default128 and custom per-rank counts remain. Only harness/docs/existing fixture tests change. FlashInferb1eab683 refines two owned implementation files;319 protected kernel_src files remain byte-identical. Marker-stripped computational AST, source parity, scopedprecommit and six HashInfer CPUfixture checks pass. GPU tests and publication are in progress; no rejectedalignment/register/TMEM optimization is included.

Fresh C2/infra replacementboxfi-w4a16-align256-r2-0926 onhu-pdx-43, image26.05-py3, runs serial GPUwork. GLM5H6144/I2048/E256/top8/EP4 with1024tokens/rank is exactlyuniform:128tokens/expert,8192routes/owner. Fresh native8candidate AUTO winnerN128/G1024/reuse_dispatch_warps, score585.872024us (maximumrankmedian hotCUDAgraph timing, not end-to-end comparison). Independentreference and capture/baseline checks have0bitmismatches/nonfinite values over6291456BF16elements/rank.

Initialcaptureandnativepostprocess exit0, but strictaudit1 rejects missing outerdispatch ranges in rank0. This capture is pendingqualification, not acceptedcomplete evidence. OriginalarchiveSHA518a707fcb46bb7109368be5a71c781535816d0a4bc54b25003aebaf5239064d and transferfailures are preserved. InvestigatingSDK/buffer/marker behavior; do not weakenparticipantchecks. Durable work underoptimization/trace4096-20260926; upstream evidence in siblingflashinfer-pr5019-merge-sync-20260921/tracing-sync-20260926. Devbox remains allocated.

The initial135-sentinel CUBIN produced only133native patch points: predicated per-token returnpush/pop PMTRIGs were swallowed into a2080-byte pop patch span on all4ranks, losing outer dispatch/return ranges. This is a confirmedscanner failure, not a relaxedcoverage threshold. HashInferdf205c4 removes only the extra representative-warp predicate around the existing per-token push/pop pair; everyactualdispatchtokenjob is marked. Computational AST equality and scopedchecks pass. Thisprotectedtransport markerpatch remainsHashInfer-only and is excludedfromFlashInferb1eab683. Newbaselineandcapture ondf205 (source+fixtureSHAee7e6de8cc7c105968cc58cc10a453e07fe4e76bf1547245cd34559fc76ec832) pending; first4babaselineisnotrelabeledascurrent.

The df205 rerun selected N128/G1024/reuse_dispatch_warps at587.919980us. All numerical checks again passed and the135-point static native/PMTRIG bijection passed, but strict audit2 rejected dynamic token-return nesting: outer ranges ended while subsequent per-token work still appeared hundreds of microseconds later. No endpoint tolerance or decoder workaround is accepted. The next marker-only change removes the unreliable inner per-token pair, retaining all-warp whole-dispatch/return ranges, following the existing pull-marker policy. The rejected df205 capture remains archived atSHA d49ec84144d48472939377d73f0c4306d0a6a7f520104fd8999d1611bd7016f9.

FlashInferb1eab683 is pushed and live in PR5019 with exact body readback. All18 existing logical cases/42rank executions passed with0failures/errors/skips; the4rank native fixed smoke passes numerical and refined-owned-marker checks. Protected transport scope remains excluded, including its incomplete outer Pull marker coverage. Current upstream precommit/API checks pass; GPU CI is skipped pending maintainer authorization. Full source, rawlogs,8JUnit reports and native artifacts are preserved in siblingtracing-sync-20260926 (archiveSHA6af9ee678b9e20e34e9e965f07291cb5dae40f22864a964f4bb3d63c9100c097). NeitherPRmerged; devboxretained.


## 2026-09-26 — Final global4096 trace qualified

HashInfer `679828c1f757a3ecfcb55a5650b7690ab9f297e2` removes the unreliable inner per-token return pair while preserving all eight whole dispatch/return ranges. It adds no computational or synchronization change. Fresh baseline, reference comparison, native IKET collection and strict audit3 pass on all four C2 B300 ranks. Source-plus-fixture SHA256: `2156bd7a52f8fae316a92c51e61592cb87f9b1acd9d43c190399640521ccb32c`.

The fresh winner is **M256/N128/K256, group512, reuse_dispatch_warps**, score **587.168008 µs**, selected from all eight native candidates / 1,600 hot graph-event samples. This is a tactic-selection score, not a before/after end-to-end benchmark. All ranks have zero independent-reference/capture bit mismatches and zero nonfinite values over 6,291,456 BF16 elements each. The final capture uses the normal 148-CTA/74-CGA grid; native IKET records only cluster0 (two CTAs / 40 warp tracks).

All four compute/epilogue/transform combine WGs (WG0, WG1, WG3, WG4) now execute: 336 actual warp-recorded combine calls per rank's selected cluster. WG2 has all eight dispatch/return wrappers. All 133 native points bind bijectively to original CUBIN PMTRIG sites; native JSON matches each own Perfetto nanosecond timeline. Retired per-token return events are absent. Prior 4ba/df205 captures remain explicitly rejected; their failures were not hidden or repaired in postprocessing.

Evidence: `trace4096-20260926/audit-3/{audit.json,audit.md,rank0.pftrace,rank1.pftrace,rank2.pftrace,rank3.pftrace}`; complete final collection under `remote-v3`. Publication receipts will close the final source/body/CI state. Trace files and experiment helpers stay outside both source repositories; keep the idle C2 devbox for iteration.

Publication closure: HashInfer PR13 is verified OPEN/draft at679828c with exact final body readback and current-head precommit SUCCESS. FlashInfer PR5019 remains OPEN/non-draft atb1eab683 with exact final body readback; precommit/API/docs CI passes and GPU CI is gated on maintainer authorization. Both local checkouts are clean. Final trace links, archive identities and source/body receipts are in `trace4096-20260926/completion.json` and the sibling upstream completion record. GitHub identity restored tozianglih. No merge or devbox release; no trace artifacts in either PR.


## 2026-09-26: private transport phase tracing, first native attempt rejected

User requested reasonable subranges inside input pull/output return, fresh AUTO-selected traces for128 and4096global tokens, and the rank with minimum initial sync. Transport marker changes explicitly remain private toHashInfer; no upstream source is touched. Work directory: `transport-phases-20260927` (actual run timestamps are recorded in each capture).

Candidate`6afd622` adds10push/pop pairs only; source+fixture`84cc799679fbeb959ef37e5bd4639697c2bfde84239423f2f19407bfd1c5a49e`. Deleting20marker lines restores679828 bytes; CPU source/peer/precommit checks pass. Fresh128 selectsN64/G512/epi_warps at267.7440047264099us;4096selectsN128/G1024/reuse_dispatch_warps at587.0560109615326us. Both captures numerically pass but are REJECTED for event structure, so neither is a qualified finer-phase trace.

All4ranks pass static original-PMTRIG/native-point bijections:145sites128,153sites4096. Runtime duplicates remain:128store/ready ranges14,14,13,14 versus8expected;4096store/ready211,213,212,213 versus112expected.4096return stage counts107,109,107,117 but completion ranges214,218,214,234; pacing similarly duplicates. Extra pops prematurely close parent helpers. Exact diagnostics, rawcaptures, failed strictaudits and originalSASS remain in`transport-phases-20260927/{remote-v1-*,audit-v1-*,diagnostic-v1-*}`. No SDK patches, repaired events, cropping, or weakened gates.

Followup`f4dc6e1` moves transfer endpoints into EXISTING elected-lane blocks and retains8phasepairs; removes unreliable ready-batch/output-completion/pacing subdivisions. Deleting16marker lines restores679828 bytes. Source+fixture`50e19c04f93b952fdeac634f0fe36e7fb053fe37f1a31c4babb9674bdd767d69`. Fresh qualification pending; this entry does not claim the followup works. C2/infra devbox`fi-w4a16-align256-r2-0926` remains allocated.


## 2026-09-26: elected-thread transport phases qualified on both shapes

Current source `f4dc6e1b4990df3a783ab51b43f497a482811d5c`; package-plus-fixture SHA `50e19c04f93b952fdeac634f0fe36e7fb053fe37f1a31c4babb9674bdd767d69`. HashInfer PR13 [private repository link omitted] remains draft. The eight new phase pairs are private `token_comm.py` marker changes; upstream FlashInfer is untouched.

Removing the16 added marker calls restores original679828 source bytes and computational AST. Transfer endpoints use the existing elected-thread contexts. Input pull separates source resolution, issue/weight work, residual input wait, FC1 pool-store issue/completion and tail publication. Return separates FC2 expert readiness from local staging/peer issue. Separate peer-store-completion/pacing and per-batch publication scopes are omitted after duplicate-event failures; their operations remain within the whole helper ranges. No computation, barriers, alignment, register policy or pipeline policy changed.

Both fresh AUTO sweeps and native captures pass on all4ranks. Each winner was checked against the independent reference; each capture exactly matches its finite BF16 baseline. Native audits verify originalPMTRIG/config/PID binding, exact phase jobs and parent nesting, and each trace’s own Perfetto nanosecond endpoints.

| Global tokens | Winner | Hot score µs | Selected rank | Worst initial sync µs | Complete trace |
|---:|---|---:|---:|---:|---|
| 128 | N64/G1024/epi_warps | 267.648011 | 2 | 9.440 | [Perfetto](optimization/transport-phases-20260927/audit-v2-128/selected-min-sync-rank2.pftrace) |
| 4096 | N128/G1024/reuse_dispatch_warps | 586.367995 | 2 | 11.552 | [Perfetto](optimization/transport-phases-20260927/audit-v2-4096/selected-min-sync-rank2.pftrace) |

Rank selection minimizes each rank’s longest initial count-exchange/sync scope across the eight recorded WG2 tracks. It compares durations only; no cross-GPU alignment or cropping. Full148CTA/74CGA launch; native recording filters to one2CTA/40warp cluster. Scores are hot uninstrumented graph-event tactic-selection scores, not speedups or instrumented durations.128’s epi_warps winner does not execute the dispatch return helper;4096’s reuse winner does.

- [128 shape: all candidates, ranks and phase durations](optimization/transport-phases-20260927/summary-v2-128.md)
- [4096 shape: all candidates, ranks and phase durations](optimization/transport-phases-20260927/summary-v2-4096.md)
- [Source and capture runbook](optimization/transport-phases-20260927/README.md)
- [Current PR body](optimization/transport-phases-20260927/PR-body.md)
- [Chronological experiment ledger](optimization/EXPERIMENTS.md)
- [Rejected initial finer-phase captures](optimization/transport-phases-20260927/REJECTED-v1.md)
- [Previous tracing/optimization workspace overview](optimization/transport-phases-20260927/README-before-transport-phases.md)

Keep C2/infra devbox `fi-w4a16-align256-r2-0926` on`hu-pdx-43` allocated. Both accepted runs use image`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe/IKET4.8.0 and fourB300GPUs. Last post-run compute-process query was empty. Traces, native binary dumps, rejected experiments, helpers and ledgers remain outside both source repositories. Upstream checkout remains clean at`b1eab683651680e1434321b3e0adf499be79447a`; no upstream sync was performed.

The source, runtime, native point, numerical and selectedtrace evidence is in `transport-phases-20260927`. Both accepted archives were downloaded in verified4MiB chunks; initial4096archive directory-change warning was resolved by preserving that archive and repacking only after a before/after full-input hash comparison passed. No captures were repaired and no earlier failed trace was reclassified. Independent evidence receipts remain separate from each primary audit.

Publication closure: HashInferPR13 pushed at`f4dc6e1b4990df3a783ab51b43f497a482811d5c`; body SHA`a278f81dd0c28cd54bb41adb6a9c015ebd97b6c4753b58cb0abb26d5ace963f2` read back exactly; remainsOPEN/draft. Both independent capture readbacks PASS and both selectedPF files SHA-verified. Upstream checkout remains clean at`b1eab683651680e1434321b3e0adf499be79447a`. Tracefiles stay outsidePR; devbox retained, post-run GPUprocess list empty. See`transport-phases-20260927/completion.json`.

## 2026-09-26 — initial register redistribution markers

User requested ranges around the initial register changes, then explicitly retained all existing payloads and requested upstream synchronization of this marker change. HashInfer accf82d adds6flat calls for WG1 donate96→80, WG0 acquire96→144, WG2 donate96→64. No register/timing/synchronization policy changed. Source-byte recovery and scoped pre-commit passed.

Fresh EP4 uniform128 and4096 native sweeps/captures pass; selectedrank1/8.160us startup gate atT128 (N64/G512/epi,268.608004us hot score), selectedrank3/10.944us atT4096 (N128/G1024/reuse,585.856020us). All3200 tuning samples retained; all8rank captures numerically bit-equal and independently native-audited. Registeracquire med/max144/160ns atT128 and48/64ns atT4096, including instrumentation; not isolatedinstructionlatency. Fullsource and nativeevent-ID joinchecks added tolocal audit with16syntheticchecks; original v1auditor and evidencepreserved, finalv2audit reusedsamecaptures.

Evidence: `register-reallocation-20260926/` contains source/precommitreceipts, immutableallrankarchives, finalaudits, independentreadback, summaries and complete selectedPerfettotraces. HashInfercommitpushed; upstreamsix-line sync/validation is inprogress. No payload removal or traceartifactcommit. Devboxretained.

Publication closure: HashInfer PR13 remains OPEN/draft at `accf82dae0b703cb0276839dd53d3b17eb21f936`, precommit CI SUCCESS and exact body readback passed. FlashInfer PR5019 is OPEN/non-draft at `acbc0b1f389d34dbeea6b33e64eebfdcc54a0119`; exactly six owned-kernel register marker lines synced. All 18 existing logical tests / 42 rank executions and native smoke on all four ranks passed; 24 register ranges/rank and 32,768 finite BF16 reference-equal output elements/rank. Upstream concise summary refreshed without ledger sections; screenshots, historical performance tables and checklist preserved. Hosted GPU CI remains authorization-gated. Source repos clean; no trace/script/new-test sync, no private transport sync, no payload removal. C2 devbox idle and retained. Completion receipts are under `register-reallocation-20260926/hashinfer-completion.json` and sibling `flashinfer-pr5019-merge-sync-20260921/register-reallocation-sync-20260926/completion.json`.

## 2026-09-26 — merge and HAI pin update

Per explicit user request, HashInfer PR13 merged as `a4b2d9a690e302deb0feac8b7cc872ab0b31a766`; tree `2ba606e1965979308f57067bcb889235b16f04fe` exactly equals tested tracing headaccf82d. HAI PR5450 now pins the merge atfef1e716 and remainsopen. Ten fresh host bootstraptests and preflight/source checks pass; no newGPU/servingclaim. RealGitHubbodyHTML confirms crossrepo references targetHashInferPR11/13 correctly. Fullreceipts: siblingflashinfer-pr5019-merge-sync-20260921/hashinfer-merge-hai-bump-20260926/completion.json.
