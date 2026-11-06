# Optimization ledger

## Current decision — original activation restored, devbox untouched

User authorized reverting native tanh and explicitly prohibited devbox access.
Commit `866c80d0c70a90624b4c2056d12d1543d709609e` restores `_swiglu_act`,
`_tanh` and the full `w4a16_reference.py` exactly from original a7103ae2.
Only activation source and reference changed. N32 geometry, retained 16 tactics,
model presets and tests remain unchanged. Focused pre-commit, commit hooks,
Python syntax compilation, `git diff --check` and exact baseline source/reference
comparisons passed; see `evidence/tanh-revert-static-checks.json` and its log.

No GPU check or benchmark was run, no remote connection or synchronization was
made, and no devbox state was changed. All previous K3 candidate/native timings
and exact gates are historical. DSV/GLM SwiGLU measurements remain evidence for
unchanged paths, not new 866c qualification. New K3 performance and assembled-
source GPU qualification are deferred. Public/local source differs from the last verified remote 48fce snapshot;
this task did not synchronize it, and later remote activity is unknown. The
09:38:47 UTC remote-state receipt is historical. Preserve the devbox for later separately authorized blog work.

Current published draft PR body: `PR_BODY_REVERT_TANH.md`. Publication and
live head/body/draft verification at 866c80d0 are recorded in
`evidence/pr6277-tanh-revert-publication-receipt.json`. Frozen 48fce body, source/test receipts,
all raw data, numeric tables and historical entries below remain preserved.

## Historical pre-revert final decision — 2026-10-09 UTC

Retain native SiTU tanh, M128/N32 and M256/N32 support, the 16-tactic catalog
and model benchmark presets at public commit
`48fce528a70b7bc10c26307dfd2155491d50cfe9`. The original scheduler is restored;
its intermediate performance studies and prefix tests are not in the final PR.
K3 and DSV reuse completed original-scheduler AUTO24 captures; all selected
winners belong to the retained16, without claiming those searches measured
AUTO16. GLM completed AUTO16. All 13 points remain visible; only T1/T2 are
excluded from aggregates. No baseline rerun, IKET or decoder redesign.

The final focused exact gate completed with eight EP2 logical cases / 16
rank-local passes and zero failures/errors/skips. All 4,018 kernel/benchmark
files and 102 tests match `git archive 48fce528` before/after the test boundary.
Receipt: `evidence/final-catalog-n32-exact-verified-v1.json`. Complete model
results and the final source/test review are in `PR_BODY_FINAL_CLEAN_48FCE.md`
and `evidence/pr-final-source-review-48fce.json`; root owns publication.
The chronology below is preserved and superseded by this final decision.

## Historical interim decision — 2026-10-09 UTC

The complete native-tanh AUTO sweep was flat (0.99716x), so the native tanh
change alone is not a demonstrated broad speedup. Reuse `full-base-v2` BEFORE
and `full-native-v2` intermediate; do not launch replacement baselines. The
residual-prefix candidate completed all 13 points at 1.01540x versus BEFORE
(11 retention points), and four focused EP2 exact cases passed on both ranks.
It is applied locally for integration, with stronger boundary coverage planned.
A separate N32 token-tile screen is active. All earlier decisions below are
historical; later complete sweeps supersede short-screen interpretations.
Decoder WG count, partition, and role register design are fixed by user request.
The four-group attempt is cancelled and excluded, with source restored exactly.

The replacement runtime is EP8 on eight B300s, C2 `k3-w4a16-opt-c2`, node
`hu-pdx-120`, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.1 / CuTe DSL
4.7.1. Source baseline is `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`.
PDL is enabled, fused TMA/FC2 reduction is disabled, and W4A16 MegaMoE's fused
deterministic combine is active. Devboxes remain allocated. No further IKET
work is planned; existing capture data, receipts, and unsuccessful diagnostic
attempts remain archived. The final full-grid CPU visualization was stopped by
the owner after real GPU captures completed; it is not a kernel failure.

## Completed native AUTO A/B/A performance

Fresh AUTO original/native/original completed on the replacement B300 container.
Pooled baseline medians use 200 untrimmed samples; candidate uses 100.

| Tokens | Original A1 us | Native B us | Original A2 us | Original pooled us | Pooled speedup |
|---:|---:|---:|---:|---:|---:|
| 32 | 237.250 | 225.938 | 235.779 | 236.5465 | 1.0470x |
| 512 | 415.748 | 413.589 | 417.010 | 416.339 | 1.0066x |
| 4096 | 602.5495 | 591.910 | 595.7825 | 598.8045 | 1.0116x |
| 16384 | 2080.085 | 2066.102 | 2085.631 | 2082.130 | 1.0078x |

T32 is faster than both individual controls (237.250 and 235.779 us) using the
same N64/G1024 tactic. Other points show smaller gains; do not generalize this
as a uniform 5% speedup. Kernel source is native-tanh-v2, not packed-only SiTU.
Raw archive: `evidence/native-auto-v3.tar.gz`; samples and provenance:
`evidence/native-auto-v3-screening.{json,md}`. The three run directories are
`runs/native-auto-v3-{a1,tanh-b,a2}/`. Timing uses native CUPTI, cold-L2 CUDA
graphs, 3 warmups, and rank-MAX activity spans; route preparation, tuning,
capture, and L2 flushing are untimed. These four points establish the gate,
not the complete performance curve.

Compiled evidence in `evidence/codegen-staging-v3/` matches all four staging
specializations on all eight ranks. The epilogue has no static spill loads/stores
in either arm. Native tanh removes 336 static instructions at T512/N64 and 672
at T4096/N128. This establishes generated-code changes, not dynamic instruction
counts or a bottleneck claim. The formula is algebraically unchanged, while
native tanh changes the approximation bits; the exact oracle is updated to match.

## Completed exact correctness gate

`correctness/native-exact-v3/exit.json` reports `complete: true`,
`returncode: 0`, finished `2026-10-09T04:28:48.899061+00:00`.

| Existing test selector | Execution | Result |
| --- | --- | --- |
| `test_moe_ep_nvfp4_cutedsl_mega_multirank.py::test_nvfp4_w4a16_epilogue_contract` | EP4 | 9 cases passed on each of 4 ranks; 0 skipped |
| `test_nvfp4_cutedsl_kernel_vs_reference.py::test_nvfp4_w4a16_fp32_scales_and_routing` | EP1 | 4 cases passed; 0 skipped |

This is 13 logical cases (40 rank-local passes), all with the existing exact
W4A16 comparison. Coverage includes unchanged SwiGLU/MiniMax, gate-only and
gate/linear SiTU, non-FP32-exact beta constants, small/saturated inputs, both
return modes, runtime/config scales, and CUDA graph replay with changed runtime
normalization. No tolerance was relaxed and no separate non-exact behavioral
test was added. Exactness is against the updated native-tanh instruction oracle,
not bit identity with the previous tanh approximation.

Commands, JUnit XML, source manifests, logs, and runtime versions are in
`correctness/native-exact-v3/`; the combined archive is
`evidence/native-exact-all-attempts.tar.gz`. V1 stopped on the diagnostic
predecessor decision and V2 stopped before collection because pytest was absent;
neither was a numerical failure. V3 ran after installing pytest 8.4.2.

## Final full-sweep policy — results pending

`next-final-full-v2/` defines one fresh original AUTO sweep and one fresh
native-tanh-v2 AUTO sweep, 100 samples / 3 warmups per point. The complete token
list is **1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384**.
Only T1 and T2 are excluded from the retention decision; they remain in all raw
results and reports. Retention covers all eleven remaining points, including
T4 and all three prefill sizes.

Pool actual untrimmed rank-MAX samples by matching point and arm with the
completed replacement-container AUTO A/B/A screen. Do not average run medians,
trim first samples, mix fixed-tactic probes into AUTO evidence, or pool the old
container's runs. Preserve each AUTO-selected tactic. The intended new outputs
are `runs/full-base-v2/`, `runs/full-native-v2/`, and `queues/final-full-v2/`.
No completed local result for these full sweeps is recorded at this update.
The bundle supersedes the undispatched 11-point V1 specification. No additional
full repetitions or IKET work are planned.

## 2026-10-09 cooperative expert-group scan

Fixed N64/G1024 original/candidate/original completed on the replacement
`k3-w4a16-opt-c2` devbox, same B300 node and pinned core runtime. This is a
screening result, not a retained optimization. All 100 samples per point are
untrimmed; the two baseline runs are pooled (200 samples).

| Tokens | Baseline pooled us | Cooperative scan us | Speedup |
|---:|---:|---:|---:|
| 4 | 109.824 | 110.624 | 0.993x |
| 32 | 240.545 | 237.250 | 1.014x |
| 128 | 375.058 | 378.210 | 0.992x |
| 512 | 416.291 | 417.0745 | 0.998x |
| 4096 | 732.035 | 726.133 | 1.008x |

The second baseline alone is faster than the candidate at both apparent winning
points (T32 236.1135 us; T4096 723.717 us). No consistent speedup is established.
Do not retain or run correctness on this candidate on the present evidence.
Raw runs and queue are preserved in `evidence/cooperative-scan-v3.tar.gz`;
complete samples/provenance in `evidence/cooperative-scan-v3-screening.{json,md}`.
The scan patch and its source/integer audit are archived only; neither the scan
nor its proposed tests belongs to the selected upstream diff. Subsequent native
tanh codegen, AUTO screening, and exact validation are recorded above.

## Setup

New source baseline `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`; independent local
and remote clones. C2 was idle at initial inspection (all eight B300 GPUs at
0% utilization and 0 MiB allocated). The following entries preserve the earlier
exploratory stages; the current decision and completed gates above supersede
their provisional conclusions.

Earlier ledgers are reference material, not evidence that a new K3 candidate
has been measured or retained. Keep arithmetic changes separate from catalog
changes during exploration.

## Reciprocal contract audit

The first packed/native activation probe artifacts use the split kernel's
`f32_reciprocal` helper, following PR #4540. Existing MegaMoE instead rounds
`1 / beta_python` to FP32; the two differ for some non-FP32-exact beta values.
For measured K3 beta=4/25 the constants are identical, so those probes remain
valid performance experiments. The selected `native-tanh-v2.patch` restores
MegaMoE's original reciprocal contract; the completed exact gate guards
non-FP32-exact beta values. The instruction-exact reference was updated for the
native tanh approximation, as authorized. The earlier separate FP64 tolerance
test was rejected and remains an unrun archive, not part of validation.

## First fixed-N64 screen

Native K3 preset, EP8 B300, M256/N64/K256 C2 G1024 F4, epilogue return,
100 untrimmed CUPTI samples per point. These are exploratory single sweeps,
not final AUTO performance evidence. Baseline A2 brackets the activation probes.

| Global tokens | Baseline A1 (us) | Packed SiTU (us) | Native tanh (us) | Empty-half guard (us) | Baseline A2 (us) |
|---:|---:|---:|---:|---:|---:|
| 32 | 236.258 | 235.298 | 234.210 | 239.458 | 234.210 |
| 128 | 376.514 | 372.834 | 373.155 | 375.876 | 388.114 |
| 512 | 415.331 | 413.364 | 412.867 | 416.499 | 414.707 |
| 4096 | 720.326 | 717.428 | 713.702 | 725.413 | 722.901 |
| 8192 | 1360.841 | 1308.793 | 1306.330 | 1336.121 | 1349.753 |

Decode improvements are within observed variation. Packed/native activation
shows roughly 3–4% at T8192, requiring matched N128 and AUTO confirmation.
N64 is not the earlier K3 AUTO prefill winner. Empty-half skipping is rejected
from the prospective PR: weak/mixed results do not justify its extra control
flow. Its source and boundary-test prototypes are archived under
`evidence/candidates/`; neither is retained in the working implementation.

This stage preceded the completed tactic screens, N128 comparison, fresh AUTO
gate, and exact validation. It is not pooled into final evidence.

## Timing-boundary confirmation

The campaign always passes `--precomputed-routing`, for DeepSeek/GLM and K3.
The native Mega callback times only `layer.forward(tensors)`; `route()` executes
before warmup/capture. Input staging, communication, FC1/activation/FC2, applying
the precomputed route weights, and combine remain inside the body. K3 requires
the flag; standalone DeepSeek without it would include its top-k router.

Raw prefill samples show noticeable within-sweep drift. For N64 T8192, baseline
A1's first/last 25-sample window medians were 1219.98/1393.90 us; native tanh's
were 1207.34/1378.00 us. Therefore the roughly 3–4% full-median difference is
not yet a robust optimization claim. Retain all samples, repeat matched arms,
and confirm using N128/AUTO rather than selecting favorable windows. A live
idle hardware read showed SM2032MHz, memory3996MHz and no active power/thermal
slowdown flags; this does not diagnose the in-run drift. No clocks or power
limits were changed.

## Updated validation direction (user request, 2026-10-08)

Use the existing `tests/moe_ep/w4a16_reference.py` and zero-tolerance W4A16
bit-exact tests. Extend their cases concisely; update the instruction-matching
reference for retained algebraically equivalent activation arithmetic. Do not
add a separate non-exact behavioral test. The proposed FP64 tolerance test was
removed from the repository and archived as an unrun, rejected prototype.
Correctness execution still follows confirmed performance improvement.

## Fixed N128 activation comparison

Same source baseline, native model preset v2 (nullable epilogue knob parser fix),
N128/G1024/F4/epilogue return; 100 samples per row.

| Tokens | Baseline A1 us | Packed us | Native tanh us | Baseline A2 us |
|---:|---:|---:|---:|---:|
| 4096 | 598.6430 | 595.6355 | 591.0915 | 599.5395 |
| 8192 | 1085.4635 | 1088.7765 | 1076.3415 | 1077.1100 |
| 16384 | 2063.8390 | 2062.8135 | 2066.8300 | 2082.8455 |

Packed SiTU is effectively flat. Native tanh shows about1.3% at4096; the larger
rows remain within baseline variation. No material broad prefill win is
established. Cache invalidation was audited: CuTe4.7.1's direct `cute.compile`
forces `no_cache=True`; every fresh-process helper change is compiled anew,
regardless of the persistent cache directory. See `CUTE_DSL_CACHE_AUDIT.md`.

## Secondary directions

G256 is rejected: T4/32/512 measured125.793/241.250/437.795us, versus the
bracketing initial control109.969/231.538/412.4345us. No G128 follow-up.
S3, M128/C1, epilogue publication batch4, and G4096 repetition completed without
a repeatable gain and are rejected. G4096's initial T4 result near 101 us failed
repetition: 107.360 us versus the final control 106.631 us. Preserved run summaries
are `runs/scheduler3-i/`, `runs/single-cta-j/`, `runs/epiflag44-k/`,
`runs/group4096-repeat/`, and `runs/secondary-a2/`. No tactic-catalog extension
is retained. The separate K16 combine result follows.

A proposed static empty-half optimization was rejected at source review.
Capacity alone does not bound expert rows when top-k IDs repeat; no new
uniqueness assumption will be added.
`evidence/candidates/STATIC_SMALL_TOKEN_HALF_REVIEW.md` records the reasoning.
No implementation or GPU run was made.

## K16 score-lifetime screen completed

The existing per-route scalar score-load path was probed at K16 by changing
`prefetch <= 16` to `< 16`. Same N64/G1024/F4/epilogue tactic, baseline/candidate/
baseline, 100 cold-CUPTI rank-MAX samples per point. Pooled baseline versus
candidate: T4 104.197/104.996 us, T32 235.8015/235.561 us, T512
417.169/411.456 us, T4096 725.498/724.8735 us. Only T512 has a modest 1.39%
speedup; no repeatable broad gain is established. Do not retain this change
or describe register spills as the cause without further evidence. Raw output
and provenance: `evidence/secondary-combine.tar.gz`, `runs/combine-*`, and
`evidence/combine-screening.{json,md}`.

`auto-base-1` completed its original 11-point AUTO run. It belongs to the earlier
runtime and is retained as historical evidence, not pooled with the replacement
container's final comparison. Native-tanh-v2 subsequently passed the fresh
AUTO and exact gates described above.

## Traffic model and rejected scheduling hypothesis

For K3 EP8, one read of all 112 experts on a rank costs
`3 * 3584 * 3072 * (1/2 + 1/16) * 112 + 2 * 4 * 112` =
2,080,899,968 bytes including packed weights, block E4M3 scales and two FP32
expert scales. At a 414 us layer span that is 5.026 TB/s.
This is a workload traffic model, not an HBM counter measurement: cache hits,
repeated tile loads, activations and communication are omitted. It is consistent
with substantial weight traffic in the small-token regime, but does not prove
that HBM or dequantization is the limiting stage.

This motivated the warp-cooperative greedy group-boundary scan for more than
32 local experts (K3 has 112), preserving whole-expert grouping, claims,
publication, and phase order. The later matched GPU screen rejected it; see the
completed cooperative-scan entry above. Source-only residual-scan and sparse
expert-seek follow-ups remain hypotheses and are not selected or queued.

## Progressive campaign policy (2026-10-09)

Reuse the completed BEFORE baseline and recorded intermediate measurements for
subsequent candidates. Do not schedule another baseline/control sweep by default.
The full BEFORE run `full-base-v2` completed all 13 counts. Keep the native-tanh
step as the current candidate and investigate further improvements; PR6277 stays
draft. Recorded-winner screening may avoid repeated AUTO search while keeping
the native fixture and CUPTI timing path; label it separately from AUTO results.
All subsequent benchmark invocations still cover the full 13-token list, with
only T1/T2 excluded from retention and no further IKET.

## Completed 13-point native-tanh comparison

`full-base-v2` and `full-native-v2` completed with exit code 0. Native tanh
remains provisional: the geometric-mean speedup over the 11 retention points
is 0.99716x (0.99910x with the earlier four-point controls pooled). T4 regresses
5.18%; most decode rows are close to parity and prefill is mixed. The earlier
4.7% T32 screen is not a broad performance claim. Full tables and raw samples
are in `evidence/final-full-v2-report.*`.

Further candidate-only work reuses this BEFORE baseline and native intermediate.

## Packed FC1 transpose screen

`packed-transpose-v1` compiled and completed all 13 points with 100 samples and
the exact recorded native AUTO winners. Tables and raw-data validation are in
`evidence/progressive-packed-v1.*`. Geometric-mean speedup versus BEFORE is
1.00080x overall, 1.00167x for decode, and 0.99847x for prefill. This is effectively
flat, so the candidate is not promoted; no GPU correctness or additional codegen
qualification was started.

The independent count-cache follow-up restores the exact native epilogue first
and changes only scheduler count reads. It completed successfully at
2026-10-09 05:09 UTC. No baseline was repeated.

## Completed count-cache screen

`count-cache-v1` completed all 13 points, 100 untrimmed samples per point, using
the exact recorded native AUTO winners. Source-manifest validation confirms
only the scheduler differs from the measured native intermediate: no packed
transpose was carried over. Archive: `evidence/count-cache-v1.tar.gz`; complete
comparison: `evidence/progressive-packed-count-v1.{md,json}`.

Geometric-mean speedup versus BEFORE is 1.00672x across 11 retention points,
1.00825x for decode, and 1.00266x for prefill. Versus the native intermediate it
is 1.00959x overall. T16 and T32 improve by 1.01873x and 1.03305x versus BEFORE;
T256 and T8192 are slightly slower. The result is a small candidate gain, not a
demonstrated broad improvement or a measured scheduler bottleneck. No GPU
correctness qualification has been started for this candidate. Keep its source
and results while evaluating a distinct decoder-concurrency experiment.

## Decoder WG experiment cancelled by user

The user explicitly directed that the well-established decoder WG design remain
unchanged across Mega and split MoE. The `four-decode-wg-v1` worker was stopped
with SIGTERM; its supervisor and all eight workers exited. Original kernel and
frontend hashes were restored under the benchmark lock at 05:15:34 UTC. The
partial capture is preserved but cannot enter retention reports. It is not a
completed performance result, failure diagnosis, or retained change. No exact
qualification ran. Do not revisit decoder WG count, partition, or register-role
redesign in this effort. Devbox and all artifacts remain allocated/preserved.

## Residual-prefix performance result

`residual-prefix-v1` completed all 13 points at 05:27 UTC, using the saved native
AUTO winners, 100 samples, and the unchanged decoder design. Full validated raw
results: `evidence/progressive-residual-v1.{json,md}`. Versus BEFORE, geometric
mean speedup is 1.01540x overall, 1.01456x for decode, and 1.01765x for prefill.
Ten of eleven retention points are faster; T64 is 0.12% slower. T16 improves
160.0815 to 152.8335 us; T4096 improves 593.6060 to 580.1980 us. These are saved
control comparisons, not a new interleaved control experiment or proof of which
scheduler work was exposed. The gain meets the gate for focused exact testing.

Qualification will extend the existing uneven/empty/refill zero-tolerance test
with four logical cases: N64/SwiGLU/epilogue return and N128/SiTU/dispatch return,
each in static and atomic scheduling. Sixteen global experts and group_hint=4
exercise multiple groups without adding a separate non-exact oracle.

## 2026-10-09 residual-prefix exact gate

`correctness/residual-exact-v1/exit.json` completed successfully at
05:34:25 UTC. The existing uneven-source/empty-refill test, `-k prefix`,
passed four logical EP2 cases (8 rank-local passes), with zero failures, skips,
or tolerance changes. Source hashes match the measured residual candidate.
The fixture exercises multiple groups, static/atomic scheduling, N64/N128,
both return modes, config/runtime scales, and empty/refill transitions.
Independent review found no correctness issue; a follow-up strengthens F1=2
and single-block coverage to a non-power-of-two divisor and multi-block expert.

Local receipts: `evidence/residual-exact-v1-receipts.tar.gz`. The first full
archive transfer was truncated; it is preserved with a `truncated-transfer`
name, not treated as a valid archive. The full source-before snapshot remains
on C2 (24,488,473 bytes, SHA256
`23d860104f280d07ce70322d0cea101a0c9ccf517655e69044a93effb9c8797f`).

## N32 screen and combined exact qualification

`n32-token-v3` completed all 13 points at 05:49:58 UTC. It uses the recorded
native winner at each point, overriding only N to 32. Decode geometric-mean
speedup versus BEFORE is 1.03505x; individual T4–512 gains are 2.11–6.10%.
Prefill falls to 0.545–0.555x BEFORE. This qualifies N32 for an optional AUTO
candidate, not a universal replacement. The complete fixed-screen result,
including dense losses, stays in the cumulative report.

`correctness/combined-exact-v1` completed at 05:56:49 UTC with eight logical
EP2 cases / 16 rank-local passes, zero failures or skips. The existing
zero-tolerance reference covers the combined prefix scheduler and N32 paths:
static/atomic scheduling, both return modes, SwiGLU/SiTU, runtime/configuration
scales, uneven/empty/refill routing, and eager/graph replay. Stronger prefix
cases use a non-power-of-two FC1 tile count and multiple token blocks. The
catalog-only extension then starts `combined-auto-v2`: twelve M256 tactics,
including N32 through the original tile loop. No additional BEFORE sweep.

## M-axis retention policy

The user requested one direct-axis expansion, M=(256,128), N=(128,64,32),
with `use_2cta_instrs=(M==256)` and unchanged cluster=(2,1,1). Default AUTO
grows from 12 to 24 tactics. The established two decoder warp groups and
register-role partition stay unchanged. M128/N32 needs only bounded admission
updates; M128/N64 and M128/N128 already have the relevant cluster support.

Run `expanded-auto-v1` only after the complete M256-only AUTO predecessor.
Reuse that result and BEFORE, preserve every intermediate column, and report
which M128 cases win plus their incremental microsecond and percentage gains.
Selection alone is insufficient. If the gains are only marginal, omit M128
from production AUTO to reduce tuning cost. Assess all T4–16384, including
prefill; T1/T2 remain recorded but excluded from retention. No M128 GPU
correctness work starts unless performance warrants retaining the candidate.

## Completed M256-only combined AUTO

`combined-auto-v2` completed all 13 points at 06:14:37 UTC. The sealed source
and all-rank tactic records validate against the exact-qualified combined
kernel and 12-tactic catalog. N32 is selected for every T1–512 point; N128 is
selected for T4096/T8192/T16384. The overall geometric-mean speedup versus
BEFORE is 1.016306x, decode is 1.023714x, and prefill is 0.996813x. T32 improves
238.0665 to 222.9780 us, but T4 regresses 108.1610 to 112.1610 us and T8192
regresses 1069.0370 to 1085.1800 us. Retain those pointwise losses in every
summary; this is not an all-shape improvement.

Local archive: `evidence/combined-auto-v2.tar.gz`. Validated raw report:
`evidence/progressive-combined-auto-v2.{md,json}`. `PERFORMANCE_PROGRESS.md`
preserves every earlier column and adds the completed M256 result.
`expanded-auto-v1` started at 06:14:59 UTC after the successful predecessor,
using the same full13/100/3/CUPTI protocol, with no repeated BEFORE control.

## User-directed sparse M128 specialization

During the expanded sweep, all M128 selections through T64 are N32 (T1/T2,
which are excluded from retention, and T4/T8). The user proposed the explicit
four-tile loop `(128,32,256), (256,32,256), (256,64,256), (256,128,256)`.
If the complete result supports it, this limits the production extension to
M128/N32 and 16 default tactics rather than all 24 explored combinations.
Preserve the measured 24-tactic result as such; a pruned catalog is a separate
source boundary. Verify retained winner membership and qualify M128/N32 using
the existing exact oracle before publishing a retained specialization. The
meaningful-gain criterion remains; the added catalog cost is four tactics.

## Final M128/N32 specialization and qualification

`expanded-auto-v1` completed all thirteen points at 06:40:11 UTC. M128 wins
selection only at N32 for T1/T2/T4/T8; all later decode winners are M256/N32
and all prefill winners are M256/N128. The expanded capture measures 1.029298x
BEFORE and 1.012783x the M256-only capture over eleven retention points.
These aggregate changes are not attributed wholly to M128: T16 and other
improved points still select M256. M128's T4 median is 105.6650 versus
112.1610 us (5.792% latency reduction); T8 is 137.4890 versus 136.3215 us
(0.856% slower). T1/T2 remain excluded from retention. Hot-input autotuner
scores favor M128 by only 1.07%/0.17% at T4/T8; those scores are diagnostic,
not substituted for cold-L2 CUPTI samples.

Following the user's narrowed specialization, retain only M128/N32 alongside
M256/N32/N64/N128, in the exact requested order. The 16-tactic subset keeps all
13 measured winners while removing eight exploratory tactics. This is a
selective small-shape option, not a broad M128 speedup claim. No 16-tactic
AUTO sweep was added; subset membership does not prove identical selection
under the changed ordering. Complete validated comparison and subset proof:
`evidence/progressive-expanded-auto-v1.*` and
`evidence/m128-n32-narrow-membership.json`.

`correctness/m128-n32-exact-v1` passed at 06:42:27 UTC: four logical EP2 cases,
eight rank-local passes, zero failures/skips, unchanged bit-exact oracle and
tolerance. SwiGLU/epilogue/config scales and SiTU/dispatch/runtime scales each
run static/atomic scheduling, tail/boundary and empty/refill/graph cases.
Final kernel/catalog/test bytes stayed unchanged. The earlier eight M256 and
thirteen native cases remain distinct prior gates. All eleven final changed
files passed pre-commit, including mypy/Ruff. Final source commit:
`ce03ada4a1e1cceff5f4f823d6e133799e9c1218`. Devbox/caches retained.


## 2026-10-09: DeepSeek V4.1 Flash and GLM5 follow-up

User requested the full M128/256 x N32/64/128 exploration for DeepSeek V4.1
Flash, a true BEFORE/full-AUTO comparison for that model, and a GLM5
BEFORE/final-AUTO regression guard. Both use EP8 and the established complete
13-point token grid; only T1/T2 are excluded from retention. PDL is enabled,
fused TMA/FC2 reduction is disabled, and deterministic combine is active.

New benchmark preset commit: `bacf4861523ff7a1c1b5ad1e9d7a73a19151564a`;
benchmark SHA256 `cd70541b397a6c278219e1f8bacc7941d0e3903618f88448e1a7aad29d8e2726`.
D5120/E2304/N384/K6, SwiGLU clamp10, precomputed sqrt-softplus global top6
normalized and scaled by1.5. CPU routes remain outside all timed forwards.
No kernel, decoder-WG, or exact-reference change was made for the preset.

The user explicitly prefers the existing non-FC1 routing-weight path for
this algebraically equivalent tactic study. All new commands therefore omit
`--apply-topk-in-fc1`, as did K3. The readable reference's operation placement
is not the benchmark's target. Both K3 and V4.1 Flash have dedicated NVFP4
checkpoints; a different reference implementation's checkpoint format is not
a restriction or concern here. Inputs and weights are synthetic.

Stage1 sealed manifest: `cb5d217aa364bcc76824d7aae6c99bc7b46ab810930f1796d2c54efba0dd3b12`.
Launched07:02UTC on retained C2 B300, queue `cross-model-validation-v1`.
Sequence: DeepSeek BEFORE8, DeepSeek full24, GLM5 BEFORE8, restore current
final16 source, then await retention review before GLM5 final. BEFORE restores
all original a7103 kernel sources and receives only the identical benchmark
overlay used by its candidate. No K3 baseline rerun.

DeepSeek BEFORE completed07:15:01UTC; full24 began07:15:06UTC. Final results
and retention remain pending. Full scan evidence can be reused if every
selected tactic is retained; if a retained-catalog rerun is needed, it must
include all13 token counts and reuse this BEFORE.

PR6277 remains draft atbacf4861. Per user request the public body now removes
fixed-N32/M256-only columns and the M128-axis study; local evidence is preserved.
Public tables retain selected full-AUTO tactics. Published body receipt:
`evidence/pr6277-published-bacf4861-clean.json`.


### Scheduler retention study: AUTO stays enabled

DeepSeek full24 completed07:38:34UTC. All13×8 selected-tactic receipts agree:
M128/N32 atT1–512, M256/N128 atT4096/8192/16384. No M128/N64 or M128/N128
winner. Every winner belongs to final16; proof and hot-score margins are in
`evidence/dsv41-flash-retained16-selection-v1.{json,md}`. Overall11-point
speedup versus its original BEFORE is1.001777x (decode1.001513x,
prefill1.002481x): essentially flat. T32 is135.3455us versus122.5935us BEFORE,
while T64–512 improve. These observations do not isolate scheduler versus
tactic selection.

The user asked to test both K3 and V4.1 Flash with the scheduler optimization
removed, retaining it only if visible performance benefit remains. The user
explicitly rejected fixed tactics for this study: **AUTO remains enabled**.
The unlaunched fixed-map skeletons are superseded and retained only as history.

Queued `next-cross-model-scheduler-auto-v1`, manifest
`afbaa5de1a7eadaa99fd80acf86c6f4f775cd7f5f69cd1692b53577e001fd35a`, PID89929.
It waits for stage1 (including GLM5 BEFORE), then runs DSV scheduler-OFF AUTO24
and K3 scheduler-OFF AUTO24. All13/100samples/3warmups; same candidate order,
image, CPU precomputed routing, CUPTI/cold-L2/graphs and PDL/combine policy.
Reuses recorded scheduler-ON scans; no new original BEFORE or fixed-tactic run.
Only scheduler executable code differs; K3's older benchmark/docs equivalence
is explicitly audited. At completion restore final16+updated scheduler pending
retention decision, then benchmark GLM5 final with the chosen source.

Source audit `evidence/dsv-scheduler-source-audit.md` finds no algebraic mismatch.
DSV has18 FC1 feature blocks for both M choices. T32/G1024 is at most864 local
FC1 tiles, hence one group: any causal scheduler cost there would be startup
or generated-code behavior, not removing repeated residual walks. This is a
source-derived bound, not a measured explanation of the regression.

### Completed stage-1 evidence and current PR table

GLM5 BEFORE completed at07:51:12UTC. All13 raw-sample/tactic/source checks
passed; `evidence/glm5-before-v1.{json,md}` records the baseline. Stage1
restored the final16 source successfully. The scheduler-OFF DeepSeek AUTO24
sweep started at07:51:21UTC, with K3 queued next.

Published the complete13-point scheduler-ON DeepSeek table, including selected
tactics and the T32 regression, in PR6277. Remote body exactly matches
`PR_BODY_DSV_ON_UPDATE.md`; receipt
`evidence/pr6277-published-dsv-on-table.json` confirms draft status and
head `bacf4861523ff7a1c1b5ad1e9d7a73a19151564a`. This is a completed ON
measurement, not a scheduler retention conclusion or a measured final16 scan.

DeepSeek scheduler-OFF completed at08:15:35UTC, and K3 OFF started at08:15:40UTC.
All13x8 winner/source/model/runtime checks pass; every point has100 untrimmed
CUPTI samples. All OFF winners belong to final16, with seven AUTO tactic
dictionaries changed versus ON. ON/OFF geomeans (OFF latency / ON latency)
are0.984286x across11,0.978551x decode,0.999746x prefill. OFF/BEFORE is1.017770x
overall and1.023465x decode. K3 retention remains pending. Full report:
`evidence/scheduler-auto-dsv-complete-v1.{json,md}`.

Published all13 DeepSeek BEFORE/ON/OFF medians, baseline speedups and tactics
in `PR_BODY_DSV_ON_OFF_UPDATE.md`; remote equality/draft/head verified in
`evidence/pr6277-published-dsv-on-off-table.json`. Existing K3 raw evidence
and source scope remain unchanged. This interim body explicitly leaves the
scheduler decision pending K3 and distinguishes AUTO24 measurements from
final16 subset membership.

Read-only compiled-artifact audit found no attributable DSV T32 ON/OFF binary
pair. Installed CuTe DSL4.7.1's explicit `cute.compile` entry point forces
`compile_only=True,no_cache=True`, bypassing the DSL file cache even though
persistent directories/environment flags are configured. In-process callable
reuse remains active. No environment change or recompilation was performed;
no register/spill/instruction explanation is claimed. Exact source snippets
and receipt: `evidence/dsv-t32-compiled-artifact-audit.md` and
`evidence/dsv-t32-existing-artifact-inspection.json`.

### User decision: retain scheduler and show its incremental contribution

The user clarified: retain the scheduler when K3 has concrete speedup while
V4.1 Flash is roughly flat, and add the K3 OFF result column before the final
combined result. Retain ON; the ongoing K3 full13 capture remains required for
complete evidence. K3 T4/T8/T16 favor ON by about5.5% latency, while larger
points can favor OFF; both directions remain visible. This is an AUTO-policy
comparison, with no instruction-level causal claim.

Sealed and queued `next-glm5-final-auto-v1` with ON, final16, saved GLM BEFORE,
full13/100samples/3warmups and unchanged kernel/test bytes. Manifest SHA:
`c2c22c8bbd30461b42373b800f004a74b9c1e22a8a26492e1cc0bc82a2f19b4f`.
Remote PID103343 waits for successful scheduler study completion, then runs
`glm5-final-auto-v1` and leaves the selected source intact. The conditional
OFF exact bundle is not sealed or launched; current-source exact evidence
already applies. Decision receipt: `evidence/scheduler-retention-decision-v1.json`.

### Correction: full K3 evidence is the scheduler decision gate

The user clarified that retention must be decided from the **full K3 results**;
the tanh, tile-size and tactic changes remain safe extensions. The preceding
retention decision was premature and is superseded by
`evidence/scheduler-retention-decision-v2-open.json`.

At08:39:07UTC, root verified that PID103343 was the waiting GLM supervisor,
the scheduler predecessor had not completed, and no GLM run directory existed.
Terminated only that waiting supervisor before any benchmark/source change.
Verified cancellation receipt:
`evidence/glm-final-v1-cancelled-before-start.json`. Preserve the sealed v1
bundle and cancelled queue; prepare an unsealed v2 for the eventual full-data
decision. K3 measurement continues unchanged. No extra baseline or fixed
tactic study is launched.

### Final user decision: remove the scheduler optimization

After reviewing both complete model studies, the user chose the smaller scope:
restore the original scheduler and retain native SiTU, N32 epilogues, the
four-tile AUTO catalog, and model benchmark presets. Prior ON-retention notes
are superseded by `evidence/scheduler-retention-decision-v4-remove.json`.

K3 and DeepSeek final evidence reuses the completed scheduler-OFF AUTO24
captures. All measured winners belong to the retained16 subset, but these
are not claimed as measured AUTO16 selections. GLM5 gets a fresh final16
sweep against its saved BEFORE. The eight existing N32 logical EP2 exact
cases will qualify the original scheduler on the final source.

The scheduler source is byte-identical to a7103ae. Removed only the
prefix-n64/n128 rows and their test-only boundary_tokens scaffolding. All
four N32 parameter rows are AST-identical to the preceding committed source
(eight logical static/atomic cases); the oracle is unchanged. Focused
pre-commit passed after formatting. No decoder warp-group changes.

### M128/N32 catalog retention reopened

The user requested a V4.1 Flash AUTO12 sweep removing `(128,32,256)`
from the committed AUTO16 catalog. Keep M256 N32/N64/N128 in that order,
all existing return/group choices and every runtime/timing control. Reuse
V4.1 Flash BEFORE and completed OFF AUTO24; judge the full cold-L2 body
results rather than hot-input selection scores. The diagnostic changes
only autotune.py. Manual M128 geometry admission and its exact tests remain.

The active GLM AUTO16 sweep continues unchanged as measured evidence. At
08:59:59 UTC the waiting exact v3 PID108584 was cancelled before GLM finished,
before any test/source work; the receipt is preserved. Qualification follows
the catalog decision. No new baseline run. See
`evidence/m128-catalog-retention-open-v1.json`.

### GLM AUTO16 complete and PR evidence refreshed

GLM finished 09:12:36 UTC with all 13 × 100 CUPTI samples and eight-rank
selected-tactic agreement. The capture's 4,018 kernel/benchmark files and
102 test files match commit `48fce528` exactly. The saved BEFORE is reused.
Geometric mean speedup: 1.019675× overall, 1.023475× decode, 1.009609× prefill.
M128 is selected only at T1 and T8; included T8 improves from 113.4085 to
109.1690 us (3.74% lower latency), while excluded T1 is 3.55% slower.
This does not establish a causal M128 benefit versus another candidate.

Published complete GLM table and selected tactics at the user's request,
with the reduced scope and completed K3/DSV OFF24 evidence. Verified live
body equality and draft/head in `evidence/pr6277-published-clean-glm-table.json`.
AUTO12 comparison and final exact qualification remain pending. DSV AUTO12
started 09:12:52 UTC; keep M128 provisionally until its complete results.


### Retained16 catalog and final assembled-source exact gate complete

The complete DSV AUTO12 comparison did not show the requested broad improvement:
AUTO12 / AUTO24 speedup is 0.988392× overall, 0.983861× decode and 1.000578×
prefill. Root retained16, including M128/N32; this is an independent-AUTO
comparison, not a causal fixed-tactic estimate. Decision receipt:
`evidence/m128-catalog-retention-decision-v1.json`. The diagnostic and its raw
samples remain local; the clean PR omits the separate retention study.

`correctness/final-catalog-n32-exact-v1` restored16 under its lock and completed
at 2026-10-09T09:32:51.012404Z with returncode0. Both ranks passed the expected
eight existing cases, with zero failures/errors/skips. Complete summaries:

```text
8 passed, 14 deselected, 705 warnings in 101.64s (0:01:41)
8 passed, 14 deselected, 705 warnings in 101.65s (0:01:41)
```

Validator compared all 4,018 source/benchmark files and 102 test files against
`git archive 48fce528a70b7bc10c26307dfd2155491d50cfe9`. Source/test/reference
bytes are unchanged across execution; existing exact oracle remains unchanged.
Receipt SHA256 `74d9f15eeea48682e419f2a019bc21e7ec44399235aabceab972aaa61d5212da`;
source-map `08a38be0895384766a084b06b9aa1104be1c834313a6f67d66b05fa7a596329b`;
test-map `89c1f1c92630f9d8acfabfa7d98decc81a15d9e670948e7bb7b8ccdcffd47507`.
Historical native gate remains separately identified. No full repository suite,
all-files pre-commit, model-level accuracy run or new AUTO16 K3/DSV sweep is claimed.

Final clean body is `PR_BODY_FINAL_CLEAN_48FCE.md`; all performance rows are
unchanged from the reviewed three-model draft. Every one of 91 raw-result rows
was checked against the published seven-arm 9,100-sample export (SHA256
`c02661509a4d1b951ff87e7f65b84e873960e23ab9092089b280e59f91471e39`). The pinned
public download, self-contained public source/catalog reconstruction, selected
tactics for every row, exact commands and complete pytest summaries are included.
No remaining source changes or GPU work are required by this helper; root owns
final review/publication. Devboxes remain allocated.

### Final publication and retained devbox

Final clean body published to draft PR6277 at09:38:24UTC and verified byte for
byte, head48fce unchanged. It includes all three model tables, selected tactics,
the public seven-arm raw-sample file and final exact summaries. No scheduler
or AUTO12 study discussion remains in the clean scope. Publication receipt:
`evidence/pr6277-final-publication-receipt.json`.

At the user's explicit request, C2 devbox remains allocated for later HAI blog
benchmark sessions. Live09:38:47UTC snapshot confirms all8B300 GPUs, no active
campaign supervisors and no GPU compute processes. Checkout, dependencies,
captures and persistent cache directories are intact. `DEVBOX_HANDOFF.md`
records the remote base-plus-overlay contract and prior blog source pin.


### Activation/reference revert — local/public only

Supersedes the preceding retained-native activation decision. Restored original
SiTU exp2/reciprocal tanh and multiplication order, plus the original independent
reference (SHA256 `1d07ff039804505733dacd04e0f9c88824993772048f94b64be7c0915106f71a`).
Commit 866c80d0 contains only these two-file changes. Retained 16-tactic catalog, N32,
tests, benchmark fixtures and decoder design remain. Complete static validation
passed; GPU checks are explicitly deferred because the user prohibited all
devbox access. No reuse of the old 48fce exact receipt as current qualification.

The revised PR draft preserves all 143 measured numeric rows and the pinned
public 9,100-sample export. K3 candidate/native tables explicitly say historical
pre-revert; retained DSV/GLM SwiGLU measurements identify their original source
and are not labeled as 866c reruns. The earlier 48fce body remains frozen.
Remote/source divergence and old live-state timestamp are prominent in
`DEVBOX_HANDOFF.md`; no remote mutation, inspection or scheduling was performed.


Revised body published and verified against draft PR6277 at commit
`866c80d0c70a90624b4c2056d12d1543d709609e`; reviewed body SHA256
`1c6452dbf49cbfce136c423d89935c7fc2b8a2d43addb0e4b9cbced7b1de563a`.
Receipt: `evidence/pr6277-tanh-revert-publication-receipt.json`.
No devbox access or synchronization accompanied publication.
