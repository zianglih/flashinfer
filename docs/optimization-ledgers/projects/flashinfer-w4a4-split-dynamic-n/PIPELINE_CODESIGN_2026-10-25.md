# Epilogue and synchronization co-design

Production is clean and pushed at `aab93f854054de834447bdd8985b8bbd653fb3c8`.
This round starts from that corrected source. Earlier primary-grid and TRTLLM
results remain attributed to their recorded commits; no old campaign is rerun.
Experimental edits stay unstaged in independent project-local source clones.

## Constraints and findings

- Target one resident CTA per SM for the persistent GEMM. Its launch already
  specifies `min_blocks_per_mp=1`; no explicit register cap is constraining the
  current narrow specialization. Existing emitted code has zero local spills.
  A physical SM register budget is not interchangeable with the registers
  allocated to a CTA. The earlier register redistribution screen is closed.
- The direct N16 epilogue removes FP32 TMEM transpose traffic but previously
  expanded scale-factor address/conversion work. The current experiment
  coordinates direct loads, earlier accumulator release, packed scale
  conversion, and distributed scale-store ownership.
- The common epilogue and both core callers repeat a TMEM completion wait.
  Remove the common terminal duplicate while keeping caller drains and all
  waits that protect early accumulator release.
- Narrow one-CTA operand payload and scales have the same post-MMA lifetime,
  but separate full and empty rings. A separate experiment merges both rings
  while retaining independent TMA issue warps and the required SF proxy fence.
- Preparation and deterministic combine contain no CTA rendezvous to remove.
  Their PDL waits protect producer outputs. Preparation already uses 256-bit
  payload copies; the earlier packed-combine and SF-vectorization screens
  remain closed. No replacement of working TMA with scalar/global loads.
- Scope stays split CuTe DSL. MegaMoE is read-only reference; public APIs,
  weight preparation, per-token NVFP4 and existing format behavior remain.

## Reviewable experiments

| Experiment | Source copy | Initial scope |
|---|---|---|
| Direct epilogue and early accumulator release | `flashinfer-epilogue-codesign-review` | Generated NVFP4 FC1 N16, existing weight/output layout, four operand stages and two accumulator stages |
| One mixed operand full/empty ring | `flashinfer-merged-operand-ring-review` | One-CTA narrow dedicated-epilogue path, 128 SF arrivals plus three elected TMA arrivals |
| Earlier PDL startup handoffs | `flashinfer-pdl-startup-review` | Preparation and GEMM signal after their existing dependency waits; finalizer metadata publication remains ordered |

Experiments use fresh adjacent corrected-aab controls on `fi-w4a4-narrow-1025`, C1,
B200-92, image `nvcr.io/nvidia/pytorch:26.05-py3`. GPU2 runs paired timing;
GPU3 ran the operand-ring screen and now runs the independent PDL timeline audit.
Each begins with a bounded
source/codegen check and focused exact smoke, then native fixed-tactic
T32/T128 ABA/BAB timing if eligible. Ten warmups, 100 cold-L2 CUDA-graph CUPTI
samples, input fingerprints and initialized output/SF byte checks are retained.
These diagnostics do not substitute for the primary retention grid or a fresh
same-host TRTLLM comparison after any retained NVFP4 performance change.

## Evidence and audits

- [Whole-kernel barrier/lifetime audit](scripts/epilogue_codesign_audit/PIPELINE_SYNC.md)
- [One-CTA register/role audit](scripts/epilogue_codesign_audit/REGISTER_ROLES.md)
- [Epilogue source and generated-code audit](scripts/epilogue_codesign_audit/physical_n16_source_codegen_20261025.md)
- [Early release and accumulator-ring proof](scripts/epilogue_codesign_audit/early_release_ring_20261025.md)
- [Epilogue experiment manifest and results](scripts/epilogue_codesign_experiment/README.md)

## Completed direct-epilogue screen: do not retain

The intended codegen changes occurred: seven TMEM loads and three stores became
two loads and no stores; two distinct-value E4M3 pair conversions and one SF-byte
store replace four scale-address paths. Registers fell64→45, shared memory
197504→181120B, with zero spills and unchanged one-CTA occupancy. The sole TMEM
load completion precedes the sole early accumulator release and activation math.

| Tokens | Full-chain control/candidate | FC1 | FC2 |
|---:|---:|---:|---:|
|32|0.996049×|1.001188×|1.000001×|
|128|1.000514×|1.003438×|0.999120×|

These are six-arm geometric ratios from fixed-N16 diagnostics, not primary
retention or TRTLLM results. All3600 samples and their medians were independently
verified. Seven fresh paired byte-oracle cases, two exceptional-input cases,
native phase/final output checks, and1016 scalar/vector SF conversion boundary
values passed. The full-chain change is neutral or slightly slower; leave the
source copy unstaged and unretained. No broad format/sanitizer campaign follows.

[Raw evidence and summary](evidence/epilogue-codesign-aab93f/summary.json),
[independent verification](evidence/epilogue-codesign-aab93f/root-verification.json).
Archive SHA256: `9e490bdd61df3571ebcc1c09c84b8c2d9c6df2f8d0003cd76fda70799047b24c`.

## Completed merged-operand-ring screen: do not retain

One readiness ring replaces the separate TMA and SF rings. Emitted code confirms
131 arrivals, three elected own-byte TMA announcements,128 SF completions,
one full wait and one post-MMA operand release. Static SASS sites decrease
1152→1120, branches79→71 and SYNCS68→44, with unchanged resources. These counts
do not establish a latency bottleneck or executed-instruction savings.

| Tokens | Full-chain control/candidate | FC1 | FC2 |
|---:|---:|---:|---:|
|32|0.998546×|0.999590×|1.003319×|
|128|1.001485×|0.999817×|1.004905×|

Seven paired exact cases and all36 native arms passed. All3600 samples, medians,
ratios and byte/input/source guards were independently verified. The FC2 phase
gain does not yield a meaningful full-chain improvement. The source copy stays
unstaged and unretained; no broad validation follows.
[Results](scripts/merged_operand_ring_experiment/README.md),
[independent verification](evidence/merged-operand-ring-aab/root-verification.json).
Archive SHA256: `aca17a807bbfab95de9fbd326151ff94ab7fdf39eeb652b93a12de37b16cb93f`.

## PDL follow-up

The user's added direction is startup/initialization overlap across preparation,
FC1, FC2 and combine. Current GEMM already performs allocator/barrier/descriptor
setup before its wait, but its signal is at the end. The new bounded candidate
moves preparation and GEMM signals immediately after their existing waits.
No input reads move before their wait. FC2's elected signal issuer publishes
completed prerequisite routing metadata with a device-scope release fence before
signaling, because combine intentionally preloads that metadata before its own
output dependency wait. No extra CTA rendezvous or new register policy is added.

Large GEMM shared-memory footprints limit FC1/FC2 overlap to available SMs near
the grid tail; combine can fit alongside FC2. Preparation's existing many-CTA
grid may delay the all-CTA launch signal and stays unchanged in the first test.
The old7829 early-PDL screen used Gather4; the current regular-TMA preparation
handoff is a new stage. Actual per-arm preparation modules and their separate
kernel caches must be selected, not merely the core class.

The current PDL codegen gate passes: FC2 emits wait→release.gpu→one elected
trigger→metadata read; FC1 and preparation emit wait→trigger without an added
release. Resources are unchanged. The screen includes T4/T16 as well as
T32/T128, because startup savings can disappear in memory-bound larger cases.
An independent CUDA-graph timeline will distinguish actual overlap from the
source/spec capability. See the [PDL audit](scripts/epilogue_codesign_audit/PDL_AUDIT_20261025.md).

The first PDL screen passed native phase/final byte checks with PDL enabled and
disabled. All 9,000 timing samples and the source identities were independently
verified. The unconditional early-signal candidate has a reproducible decode
gain but a material wide-prefill regression, so it is **not retained**:

| Tokens | Tactic token width | Full-chain control/candidate | FC1 including preparation | FC2 |
|---:|---:|---:|---:|---:|
| 4 | 16 | 1.054800× | 1.033394× | 1.001003× |
| 16 | 16 | 1.028967× | 1.017034× | 1.000641× |
| 32 | 16 | 1.026890× | 1.025398× | 0.999851× |
| 128 | 16 | 1.024658× | 1.012531× | 0.999896× |
| 16384 | 256 | 0.890570× | 0.799410× | 0.965479× |

The T16384 result is 12.29% slower in full-chain time; most of its cost appears
in the FC1-plus-preparation diagnostic. Phase times are not additive. These
are fixed-tactic diagnostics, not the primary retention grid or TRTLLM results.
[Results](evidence/pdl-startup-aab93f/summary.json),
[independent verification](evidence/pdl-startup-aab93f/root-verification.json).
Raw archive SHA256: `57925f35e9170957aea1ad56bc57bc89ab061b9a2c52384c0e68bdfd4438027b`.

The T128 graph trace confirms larger overlap windows at all three boundaries;
those windows include dependency waits and are not independent useful-work
measurements. The next diagnostic mixes the same frozen actual source modules
to isolate early preparation versus early GEMM signals at T4 and T16384. The
independent timeline audit also covers T16384. No token-count policy or new
register/stage variant is added to explain away the regression.

## PDL regression isolation

The T16384 Nsight trace shows preparation essentially unchanged (25.408→25.536µs),
while FC1 grows from 200.705 to 263.744µs. Candidate FC2 starts only after FC1 has
already run for 230.432µs, longer than the entire control FC1. The large regression
therefore precedes downstream FC2 execution. Wide FC1 registers change 80→88,
with the same 195584B shared memory, 288 threads and one CTA per SM; FC2 changes
120→122 registers. Register counts establish a generated-code difference, not
its cause or an occupancy threshold.

The component ablation uses the same frozen actual modules. T4 gains split
between preparation-only (1.015107×) and core-only (1.027427×). At T16384,
preparation-only is roughly neutral (0.995163× full chain, 1.009034× FC1), while
core-only reproduces the regression (0.884711× full chain, 0.801845× FC1).
No token-count or geometry exclusion policy is justified by these results.

The next single source revision restores the original all-thread issue pattern
for FC1's early trigger, eliminating its new warp0/election control flow. FC2
retains the elected release→trigger handoff. Preparation remains unchanged from
the early-signal candidate. A new independent clone preserves the frozen first
candidate, and compile-only artifacts are explicitly distinguished from the
cubin executed by the native timing process.

[Timeline audit](scripts/pdl_timeline_audit/),
[independent timeline verification](scripts/pdl_timeline_audit/root-timeline-verification.json),
[causal audit](scripts/epilogue_codesign_audit/PDL_PREFILL_CAUSAL_AUDIT_20261025.md).
The graph API helper's first edge record is invalid; its original metadata is
partial evidence. Kernel timestamps independently establish overlap. Profiled
single warm replays are diagnostics, not retention timings.

## Uniform early PDL: simplify both signal issuers

Two independent source copies preserve the progression:

- `flashinfer-pdl-fc1-trigger-review`: FC1 all-thread trigger, FC2 elected trigger.
  Core SHA `ac1aef1e9ff52ee57a10841eb69a1ce2cf44790968f5283fa36533f9022358fa`.
- `flashinfer-pdl-allthread-review`: common all-thread trigger; each FC2 nonfused
  PDL issuer executes its own release fence before signaling. No unfenced issuer,
  extra CTA barrier, token-count policy, or geometry-specific PDL switch.
  Core SHA `adcc6506dd4ba28769cf7a5f65526e9dc927363847150de231eb850cc6c9b4b9`.

Both retain preparation SHA `a3b0042ea0ae64f66cfc968768c85b96118ed750fa92a668cb1485f91866a67b`.
Each screen passed all 36 exact native arms and 3,600 samples, independently verified.

| Revision | T4 full chain | T16384 full chain | T16384 FC1 incl. prep | T16384 FC2 |
|---|---:|---:|---:|---:|
| FC1 all-thread | 1.053221× | 0.954754× | 0.991481× | 0.965757× |
| Both all-thread | 1.048780× | 0.985217× | 0.987545× | 1.000955× |

Wide FC1 returns from 88 to 80 registers and restores the control's static code
extent. FC2 returns from 122 to 120 registers; its extra collective/control-flow
sites are also removed. Both keep one CTA per SM and zero reported local memory.
These are codegen indicators, not executed-instruction counts. A high FC1 median
in the final screen remains in the reported statistics; no sample is filtered.

The user explicitly wants unified PDL to benefit prefill as well as decode.
Keep the all-thread PDL design as the development base and resolve the residual
1.50% wide-prefill full-chain cost before promoting it. Do not disable PDL by
workload size. The ac1 trace separately attributes the remaining chain extension
to spans after FC1 and FC2 completion; those spans include scheduling and wait
return, so cache contention is still a hypothesis.

[FC1-only issuer results](evidence/pdl-fc1-trigger-aab93f/README.md),
[both issuers](evidence/pdl-allthread-aab93f/README.md),
[revised trace](scripts/pdl_timeline_audit/ac1-prefill/README.md).

## Full-chain cache lifetime co-design

The current early overlap executes allocator/barrier/descriptor setup and
routing-metadata reads. Successor weight and activation payload loads remain
behind their dependency waits. There is no early future-tensor prefetch in this
candidate. The first prefill regression was largely codegen inflation, and the
remaining slowdown must not be assumed to be cache pollution.

For the traced wide workload, FC1's padded routed payload+SF is 79,478,784B,
FC2's input is 22,708,224B, and valid FC2 output is 233,390,080B. Blanket activation
LAST risks protecting dead FC1 inputs during FC2/combine; the current schedule
has no cheap trustworthy final-use point for those inputs. Preserve the measured
weight FIRST/default policy and leave activation inputs/SF unchanged initially.

The next bounded hypothesis pairs **FC2 scratch-output store LAST** with
**combine scratch-input load FIRST**. Protecting a handoff and demoting its
consumed sectors form one policy; final model-output stores stay NORMAL/default.
Cover existing TMA and ordinary-vector FC2 store paths without a token/geometry
policy, preserve vector widths and arithmetic, and add no API flags or reset
kernel. The shared finalizer's W4A16 callers must be acknowledged if its load
hint changes. Output exceeds L2 and can evict live FC2 inputs before combine is
allowed to consume it; full-chain and FC2 timing, not combine alone, decide.

[Full-chain source inventory](scripts/epilogue_codesign_audit/FULLCHAIN_CACHE_CONTRACT_20261025.md),
[lifetime and prior-art audit](scripts/epilogue_codesign_audit/L2_LIFETIME_POLICY.md).

The paired cache implementation in `flashinfer-pdl-handoff-cache-review` passed
source, emitted-width, ordering and exact-output gates. Ordinary FC2 stores remain
256-bit, bulk stores remain TMA, combine reads remain coherent 128-bit, and final
stores stay normal. Live CUDA reports 132,644,864B (126.5MiB) of L2. Its bounded
comparison against the frozen all-thread PDL source is unretained:

| Tokens | Full-chain control/candidate | FC2 |
|---:|---:|---:|
| 4 | 0.992260× | See complete raw table |
| 16384 | 0.995215× | 0.956949× |

All 36 arms / 3,600 samples and two native exact-only gates passed. Wide FC2 rises
120→134 registers and gains 58 static nonpadding SASS sites, so this experiment
has an instruction-resource confounder; it does not prove the cache policy alone
is harmful. It fails the full-chain performance gate regardless. No additional
cache-policy sweep follows. [Complete evidence](evidence/pdl-handoff-cache-adcc/README.md).

## Overlap bounded by remaining pipeline work

The fully simplified adcc T16384 trace has matching control/candidate resources.
Its diagnostic endpoint difference is 11.007µs: FC1 contributes 1.087µs, the next
FC2 interval 2.048µs, and the interval after FC2 ends 7.872µs. Combine's kernel
lifetime begins 144.992µs before FC2 ends; this establishes an overlap window,
not exact CTA residency or useful-work duration. [Trace](scripts/pdl_timeline_audit/adcc-prefill/README.md).

The next source copy, `flashinfer-pdl-producer-drain-review`, keeps preparation
and FC1 early signals. Only FC2 signaling moves to the end of producer issuance,
before the operand rings drain. This overlaps successor initialization with
queued MMA/epilogue work without making it eligible throughout the entire GEMM.
It distinguishes successor roles, not decode/prefill shapes.

Reuse the existing warp0 tail branch; do not add an election or per-tile trigger.
Every CTA, including zero-work CTAs and two-CTA followers, participates. Each
triggering FC2 thread retains wait→release→signal ordering. Drain A first, then
AB, with **independent cloned states for both tails**: each tail mutates its
phase, so sharing the advanced A state with AB could deadlock. Both drains remain
before the unchanged CTA join and TMEM release. The common drain reorder also
changes FC1 source, even though its early signal is unchanged; do not describe
it as exclusively an FC2 codegen delta without checking artifacts.

Core SHA `fe188d180960c90bbd7d5e1d436cc180ef8b1b4171b8146af3061e47be506417`;
preparation remains a3b. A focused zero-route guard precedes bounded timing.
[Source review](scripts/epilogue_codesign_audit/PDL_PRODUCER_DRAIN_SOURCE_REVIEW_fe188d18.json),
[pipeline proof](scripts/epilogue_codesign_audit/PDL_PRODUCER_DRAIN_BOUNDARY_20261025.md).

The bounded producer-drain screen completed: T4 full-chain speedup is
1.054678× and T16384 is 0.994681× against adjacent corrected-aab controls.
All 36 timed arms / 3,600 samples, native exact checks, and the true zero-route
FC2 sentinel check passed. Every timing sample is retained, including the
slower first prefill candidate arm. FC1/FC2 register counts, shared memory,
and residency match the control, with no local allocation. FC1 N16 has a
small static instruction increase from the common drain reorder.
[Complete result](evidence/pdl-producer-drain-aab93f/README.md).

The user explicitly accepts a slight prefill slowdown when decode gains
justify it; do not require a prefill win as an additional retention rule.
The next gate is broader decode/prefill and dtype evidence for this candidate,
after making its behavior configuration explicit. An initial `is_fc1` cleanup
was rejected by the user before its GPU gate: moving the same phase switch to
a named flag does not expose the actual behavior. Preserve that source copy
for review, but do not retain or benchmark it.

The requested design exposes direct compile-time behavior knobs, selected
differently by the existing FC1 and FC2 call configurations. In particular,
the PDL signal boundary must name when to signal, rather than infer it from
activation or another unrelated property. Pipeline depth and overlap choices
likewise belong to explicit configuration; activation type remains responsible
for activation math. Public API call workflows remain unchanged. The replacement
cleanup stays in another independent unstaged copy, preserving every measured
source and avoiding benchmark attribution to the rejected phase flag.

`flashinfer-pdl-behavior-review` implements that correction. The public wrappers
select required internal controls for preparation, output scatter, scale-row
indexing, K steps, operand stages, epilogue overlap, activation-accumulator
overlap, and PDL signal placement. `pdl_signal_at="startup"` and
`"producer_exit"` state the actual boundary; neither a phase flag nor activation
presence selects it. All generated-code controls participate in the cache key.
The public signatures and 13-tactic vocabulary remain unchanged.

The CPU extracted-source audit passes 90 caller selections and 9,408
constructor/epilogue/pointer-extent configurations over six formats and the
supported tiles/activations. This checks host policy equivalence, not GPU
numerics or code generation. The first native T1 exact and true zero-route
canary passed. The final bounded timing gate follows changed-file pre-commit;
a host-only identical-branch lint cleanup is preserved as a separate source
revision. Actual native compile PTX/cubin files are now archived immediately
after each compilation, avoiding a second compile solely to inspect artifacts.
[Behavior design](scripts/epilogue_codesign_audit/EXPLICIT_BEHAVIOR_DESIGN_20261025.md),
[policy checker](scripts/epilogue_codesign_audit/check_behavior_policy.py).

The final behavior source is frozen as `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e`,
an exact child of corrected control `aab93f854054de834447bdd8985b8bbd653fb3c8`.
The independent `flashinfer-pdl-behavior-review` copy stays unstaged. The clean
`flashinfer-pdl-retention-frozen` clone supplies the measured commit, with identical
six-file source pins. No `is_fc1` prototype is included.

All five bounded points passed: T4/T32/T128/T4096/T16384 full-chain ratios are
1.054183/1.027050/1.027632/1.007560/1.004910. All 90 arms, 9,000 individual
samples and exact comparisons are preserved, along with the native timed-process
PTX/cubins and true-zero-route sentinel. Native registers remain 64/90 for
FC1/FC2 N16 and 80/120 for N256, without local-memory/stack allocation. The
prefill ratios are too small to treat as a stable gain from this bounded screen.
[Independent verification](evidence/pdl-behavior-aab93f/root-verification.json).

The first full AUTO screen C1→T1→A1 completed on B200-92, with 91 rows and all
source, observer, cache, GPU UUID and routing checks passing. Decode/prefill/overall:
NVFP4 1.023044/0.998142/1.016191; MXFP8 1.008250/1.025455/1.012914;
MXFP4×MXFP8 1.008632/1.015132/1.010400. Native TRTLLM/NVFP4 candidate ratios are
1.004328/1.154992/1.043352; this first screen does not establish a stable decode
win. A2→T2→C2 is authorized unchanged to check repeats and AUTO-selection drift.
The ten existing focused tests run separately on idle GPU5 against the same
frozen source. No broad suite or sanitizer is added during this iteration.

The fresh control is aab on B200-92. Original a65 B1/B2 on B200-83 remains
immutable historical evidence: do not rerun it, pool it with the new host, or
chain cross-host ratios into a current whole-PR speedup. Final PR evidence should
describe the final retained version and this comparison boundary; detailed
experiments remain local.

## Retained direct-behavior PDL update

All 182 rows of C1→T1→A1→A2→T2→C2 passed the frozen campaign guards and
independent root arithmetic/histogram verification. Final paired speedups:

| Comparison | Decode 4–512 | Prefill 4096/8192/16384 | Overall excluding 1/2 |
|---|---:|---:|---:|
| NVFP4 vs corrected aab | 1.022727× | 0.998799× | 1.016145× |
| MXFP8 vs corrected aab | 1.008417× | 1.013744× | 1.009867× |
| MXFP4×MXFP8 vs corrected aab | 1.008362× | 1.018723× | 1.011177× |
| NVFP4 vs native non-distributed TRTLLM | 1.003372× | 1.155006× | 1.042634× |

Retain the change: NV decode improves in both repeats at every included token,
with a 0.12% aggregate prefill slowdown accepted under the user's stated
tradeoff. MX decode improves overall; MXFP8 T64 is neutral. Larger prefill changes
include AUTO selection and repeat drift, so they are not isolated PDL effects.
NVFP4 remains behind native TRTLLM at T32/T128/T256 in both repeats; the 0.34%
aggregate decode advantage does not establish the stable across-shape target.

All ten selected existing tests passed (`10 passed, 24 warnings in 6.00s`), with
zero failures or skips. Two are tolerance-based NVFP4 full-chain tests, six are
zero-tolerance FC1 analytic K-tail tests, and two are host-only PDL forwarding
tests. No new-source broad suite or sanitizer was run. The independent bounded
native exact/true-zero gate remains separate evidence. All GPU work has ended.

Production fast-forwarded to the exact measured commit
`8c1a20173cf166b9fc279f6ae3ec5386250c5c5e` and pushed to
`zianglih/flashinfer:codex/w4a4-split-dynamic-n`. Its five-file change leaves
MegaMoE untouched. Separate review copies retain their unstaged experiments.

- [Complete medians, repeats and environment](evidence/pdl-retention-8c1a/full/README.md)
- [Independent root verification](evidence/pdl-retention-8c1a/full/root-verification.json)
- [Focused test evidence and limits](evidence/pdl-behavior-focused-validation-8c1a/README.md)
- Full campaign archive SHA256: `370598302bac04bfad18eddbb1880e4a97113ab0bfd0549ea084b121bee667a2`.
- Focused tests archive SHA256: `512816640f26c12cc3bf66101c856266c6bd4112b83993638e555149b695e67a`.

PR #7290 remains draft and now reports the final retained-source tables, direct
behavior controls, exact validation boundaries and same-tactic variation. The
public body was read back byte-for-byte after publication, SHA256
`4866735ef9b2a907877266f0e34023dce758e30150e35a9bbeec213d5dcef974`.
The prior body is preserved in `artifacts/pr-body-before-8c1a.md`;
`artifacts/retained-8c1a-publication.json` records the live head/body verification.
The pre-lint T1/true-zero gate remains local r1 evidence; the public current-source
validation claim uses only the five final-source timed gates and ten pytest cases.

## Public before/final-after presentation

The user requested final whole-PR before/after numbers in place of the latest
incremental comparison, then requested cleanup and an explicit merge-first
dependency on #7196. The public body now uses original a65 B1/B2 directly against
final 8c1a A1/A2: overall 1.049936× NVFP4, 1.111071× MXFP8 and 1.160942× mixed.
No incremental ratios are chained and no benchmark is rerun. The body explicitly
states that before is B200-83 and final is B200-92; these are descriptive archived
before/final-after ratios, not a contemporaneous same-device causal experiment.
The TRTLLM raw table and aggregates remain byte-for-byte unchanged.

The shorter body retains complete raw medians, timing/environment boundaries,
focused validation output and self-contained reproduction. #7196 is still open
and should merge first because both PRs include `blackwell/moe_finalize.py`
changes; rebase #7290 after it lands. This update changes only the PR body and
local documentation, not either branch.

Independent audit: `scripts/final_before_after_body/audit.json` (156 medians,
156 AUTO-cache hashes and 117 matching routing-histogram comparisons). Prior
incremental body: `artifacts/pr-body-incremental-8c1a.md`. Published body SHA256
`4504b45ef831f6d1d00869ddbb533c8562c740ea431e1d1b85ece604e29a5e45`, verified by
readback in `artifacts/final-before-after-publication.json`.
