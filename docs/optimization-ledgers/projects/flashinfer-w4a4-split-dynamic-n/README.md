# Split CuTe DSL block-scaled MoE dynamic MMA N

Draft upstream PR: https://github.com/flashinfer-ai/flashinfer/pull/7290


## Current workspace

Develop only in `flashinfer/` on `codex/w4a4-split-dynamic-n` for upstream [PR7290](https://github.com/flashinfer-ai/flashinfer/pull/7290). The retained input-gathering implementation is integrated at `4376662a`; current pushed head `658a0c89` adds the tested accuracy-suite consolidation. [Fork PR8](https://github.com/zianglih/flashinfer/pull/8) is closed and preserved as historical reference; `flashinfer-fc1-gather-review/` is no longer an active development checkout.

The full EP/TP plots, tables and statistics show the latest complete gather-design data, with source attribution kept explicit: swap-AB `b52e4e09`, W4A16 `1e4b127a`; later cleanup/reverts have not been remeasured. [Publication receipt](upstream-integration-20261029/publication-receipt.json). The fresh helper-only GLM-5 MegaMoE EP8 comparison completed on eight B300 GPUs:5,200 CUPTI samples, +1.54% overall and +0.89% prefill, with mixed/noisy individual decode points. [Complete results](upstream-integration-20261029/megamoe-glm5/summary.csv). The consolidated existing K-tail and deterministic accuracy tests passed all92 cases; the GPU-tested tracked-file tree matches pushed658a0c89. [Coverage and validation](upstream-integration-20261029/design-audit/TEST_CONSOLIDATION.md).

Active next experiment: split the two TMA producer warps by elements/scales for both swap-AB and W4A16, covering FC1 and FC2 while preserving PDL runahead and weight/scale prefetch. The preceding benchmark/test/publication work is complete. Implementation is unstaged in `flashinfer-element-scale-review/`, based on658a0c89; [ownership, design and benchmark plan](element-scale-ownership-20261029/README.md). Do not resume unrelated optimization directions.

## Historical cleanup checkpoint (d35fcfda)

Canonical `flashinfer/` is clean and pushed at `d35fcfda` (`refactor: tighten swap-AB MoE implementation`). The whole-PR audit retained nine-file cleanup (+50/−88): shared tactic decoding, simpler host planner/scale forwarding, reused exact-multiply reference helper, consolidated manual sanitizer kernel lists, and benchmark notices that use the actual swap/finalize flags. Public APIs, the tactic catalogue and production device execution are unchanged. All95 existing selected tests passed (33 accuracy,62 API/wrapper/graph/autotuner), with zero skips; full-PR and commit pre-commit passed. [Cleanup ledger](cleanup-20261028/README.md).

The PR component counts and validation are refreshed; benchmark values, raw outputs and heatmaps remain attributed to measured `33b7e526`. No performance or sanitizer rerun. The completed local cleanup review clone is removed after513-file verification against the retained commit; the remote source is advanced to that clean commit. Evidence and all nine persistent native cache links remain. [Publication receipt](cleanup-20261028/publication.json).

## Historical pipeline polish checkpoint (33b7e526)

The `33b7e526` follow-up changes only the swap-AB kernel (+54/−31): compile-time live SF-word copies, terminal CLC publication outside the recurring loop, and skipping the empty TMA drain for SIMT-only FC2 output. W4A16, public interfaces, layouts and tactics are unchanged. [Retention decision](optimization-20261028/post-hybrid-polish/composed/RETENTION.md).

The full EP/TP tables, raw native outputs and red/green heatmaps are refreshed for the exact committed source: [publication receipt](optimization-20261028/post-hybrid-polish/composed/publication/publication.json). The 468-case refresh has 936 fresh medians / 93,600 strict CUPTI samples; all saved external baselines remain unchanged. Scaled-format geomeans versus retained61c2 are +0.038% EP / +0.101% TP, effectively neutral. Fresh same-GPU K3 repeats do not reproduce three ~1% apparent losses. Prefill deficits remain visible. Combined exact gate:256 paired replays /32 GEMM pairs; scoped and commit hooks passed. Sanitizer skipped as requested.

Completed SF-tail, FC2-drain, CLC-terminal and combined review clones were removed after frozen-source verification; their ledgers, harnesses, patches, raw results and persistent native caches remain. The subsequent shared-prepare unsigned-index experiment is rejected: the full468-cell refresh was slightly negative, and fresh same-GPU CAAC reproduced K3 TP16K losses of2.47% W4A4 and1.71% per-token. Its completed review clone was also removed after348-file verification; all evidence remains under [prepare-index/integrated-full](optimization-20261028/post-hybrid-polish/prepare-index/integrated-full). Canonical source and published tables remain33b7. [Current optimization round](optimization-20261028/post-hybrid-polish/README.md).

## Historical retained FC2 hybrid checkpoint (61c2c367)

Canonical `flashinfer/` is clean and pushed at retained `61c2c367`. The user retained the FC2 hybrid candidate: padded routed BF16 output, existing inverse routing map, full-slab TMA and coalesced SIMT tails. This follow-up changes five files (+131/−262), without W4A16 kernel/layout/tactic changes. `flashinfer-swap-ab-fc2-hybrid-review/` was advanced to the retained commit after exact tree comparison and is clean. Other experiment copies were not modified. [Paired performance](optimization-20261028/fc2-hybrid-vs-head/RESULT.md): EP decode/prefill −0.38%/+0.20%; TP −1.88%/+4.51%; worst N3U TP8 T4 MXFP4x8 −9.71%. Earlier padded-output and native-tail alternatives remain historical experiments. [Publication receipt](optimization-20261028/fc2-hybrid-vs-head/publication/publication.json).

The full EP/TP tables and red/green heatmaps are refreshed for this exact source: [publication](optimization-20261028/fc2-hybrid-vs-head/publication/README.md). All 468 current cases / 936 candidate medians / 93,600 candidate CUPTI samples passed source, route, tactic and timing checks; saved external baselines are unchanged. The complete same-GPU C-A-A-C experiment has 187,200 samples. TP prefill gaps remain. Scoped and commit hooks passed; prior exact qualification was reused for the source-identical candidate. No sanitizer was run this iteration.

The static launch-capacity bound is retained as a neutral launch-work cleanup in `61249e0b`; [retention/integration evidence](optimization-20261028/tp-small-gemm-round/static-grid/composed/RETENTION.md) records the exact-code/actual-grid proofs, all 15 timing rows and completed local/remote source cleanup. Scale-row arithmetic and shared quantization parameters are retained; the closed producer review was removed after every tracked file matched the retained commit. [Retention and integration receipts](optimization-20261028/tp-small-gemm-round/producers/sf-combined-r2/RETENTION.md) preserve the exact/codegen gates, full diagnostic table and mixed prefill confirmation. The rejected scheduler review has been removed. The old baseline clone is read-only. The obsolete weight-layout review was removed; no pending API-layout change remains there. Keep only active experiments as source clones; preserve helper scripts/results and persistent native caches.

## Historical swap-AB separation checkpoint (2026-10-27)

Retained source:

- `flashinfer/`: canonical source, clean and pushed as one commit `c980f007` on `002529e1`. This final squash has exactly the same source tree as `dd16512a`, including the swap-AB separation. The full prior PR state is preserved in [fork archive PR #7](https://github.com/zianglih/flashinfer/pull/7), archive branches and an annotated tag. [Archive, squash and publication records](swap-ab-refactor-20261027/README.md).
- Historical `flashinfer-weight-layout-api-review/` (now removed): the separation checkpoint was `c980f007`. Legacy block-scaled implementations are restored; fixed `swap_ab=True` selects dedicated kernel, launcher, preparation and tuner modules. W4A16 shares swap-AB preparation and retains its legacy-layout transpose. No code validation has been run for this refactor.
- `sglang/`: active unstaged integration demo using the same explicit flag for preparation and execution. [Design demo](sglang-layout-api-demo-20261027/README.md).
- [Old/current comparison](old-cute-comparison-20261027/README.md): 208 completed cells, 78,000 primary samples, +20.00% decode and +6.51% prefill geometric speedups (excluding 1/2 tokens). All 112 comparable decode cells improve; individual prefill regressions remain. Old MX uses native fused finalize where unfused is unavailable; current remains unfused, and old K3 MX is N/A. Full raw pass medians are published in the PR and verified by readback.
- Retained [packed per-token FC2 scaling](old-cute-comparison-20261027/bulk-scale-pairs/README.md): 64–256 fewer instructions per tested FC2 specialization, 18 paired exact checks, no spills, four net source lines. Eight native CAAC cells are timing-neutral (1.000217×); V4.1 prefill loses 0.688%. This is an instruction-efficiency cleanup, not a claimed end-to-end gain. The completed source copies are removed and PR publication is verified.
- The bulk-drain and FC1 protected-prefix experiments are rejected: the former has no repeatable benefit, while the latter loses 2.54% on Nemo per-token 4096 with substantial code/register growth. Their verified local/remote source copies are removed; helper notes/results/caches remain in the comparison folder. That performance round ended with all eight GPUs idle. [Round disposition](old-cute-comparison-20261027/round-decision.md).
- W4A16 preparation now shares `moe_prepare.py`; scheduler metadata synchronization and static M/K/cache cleanup are retained. The original 23 tactics and scheduler heuristic are unchanged. The unproven 46-tactic expansion was removed before publication.
- Validation: 50 existing tests and 72 targeted checks pass. Same-winner CAAC across V3 EP8, V4.1-Flash EP4 and K3 EP8 is neutral at 1.0002x overall (1/2 tokens excluded). [Results and decision](w4a16-perf-20261027/no-tactic-expansion/retention.json), [full table](w4a16-perf-20261027/composed23/speedups.md), and [verified PR publication](w4a16-perf-20261027/no-tactic-expansion/publication.json).
- No active W4A16 review copy remains. All four completed copies were removed; notes, scripts, raw evidence and persistent GPU caches remain. [Cleanup receipt](w4a16-perf-20261027/no-tactic-expansion/source-copy-cleanup.json).

Completed: [rebase onto merged #7196 and #7501](rebase-merged-deps-20261027/README.md). All 104 focused B300 tests and the separate legacy64 layout check pass; the PR body is updated and verified by readback. The [preceding performance round](scripts/perf_round_20261027/README.md) and [implementation simplicity review](IMPLEMENTATION_SIMPLICITY_2026-10-27.md) are retained as source-bound history.

Each active experiment may have its own review copy. Completed or rejected source copies are removed; helper documentation, scripts and benchmark evidence are retained. Source paths mentioned below are historical unless listed here. FlashMLA and CUTLASS under `references/` are read-only reference clones. [Cleanup receipt](scripts/shared_clc_20261026/stale-source-cleanup.json).

## Fixed FC1 CLC comparison: unretained

The non-W4A16 policy candidate (fixed FC1 CLC request, static FC2; 360→180 tactics) was not retained. Its stale review copy has been removed. [Campaign notes](fixed-fc1-clc-20261027/README.md) record current-source native AUTO and paired results for all four formats and three model shapes.

The complete 156-cell comparison is −0.94% overall, −0.79% decode and −1.32% prefill, excluding 1/2 tokens. K3 has material prefill losses (up to −11.30%); no candidate change has been retained or pushed. [Full signed table](fixed-fc1-clc-20261027/speedups.md) and the separately reported noisy-point confirmation are preserved locally.

## Historical pre-rebase retained source (2026-10-27)

`flashinfer/` is clean and pushed at **ee88cf2acc59748a64ee2614fed2f16f05f67988**. The five-line per-token epilogue change releases accumulators after their last transpose, before register-only activation work. It passes 32 exact replays/source and six fixed-tactic CAAC points (2,400 samples); the three affected V3/K3/V4.1-Flash points improve 0.22%/0.44%/0.52%. K3 FC1 uses 10 more registers, with no spills; every measured FC2 is encoded-identical. This is bounded evidence, not a new full AUTO sweep or closure of every TRTLLM gap. [Decision](scripts/perf_round_20261027/epilogue-release/decision.json), [evidence](scripts/perf_round_20261027/epilogue-release-gate/completion.json), and [review-copy cleanup](scripts/perf_round_20261027/epilogue-release/source-copy-cleanup.json). All GPUs are idle and caches remain in persistent storage.

The preceding **f175faea1bd97a038fcbf3b51c84c22fd41843ed** removes the redundant inactive-SF source-row selection: 64 exact replays/source, unchanged resources and no spills, one fewer selector in each narrow-SFB core. The 48-point screen is neutral at 1.001574x; a targeted repeat leaves a small V41 prefill loss, with no E2E speedup claimed. [Disposition](scripts/perf_round_20261027/sf-source-address-gate/disposition.md) and [workspace bump](scripts/perf_round_20261027/sf-source-address-gate/workspace-bump.json). Six public tables remain attributed to their measured `f7182d5c` source.

The preceding **f7182d5c871b367f4641d6d7e2098254d63147e3** Hardware-derived dynamic N alignment uses 8 columns per CTA in the group, removing masked work with unchanged instruction counts/resources. The 96 exact replays and 48-point CAAC screen pass; timing is neutral at 1.001360× overall. [Evidence](scripts/perf_round_20261027/mma-alignment/retention.json). Six fresh public AUTO tables on this final composition are published and verified by readback. Older remote measurements retain their original source identities.

The preceding **94a89e2cdef523da2bc57e262ab12b37f2ff064a** packed FP32 multiply/FMA combine preserves the existing exact contract. All98 bounded exact cases pass; summed static instructions across74 compiled variants fall18,384→15,528, with no candidate spills. The48-point fixed-tactic screen is neutral:1.001934× overall,1.001416× decode,1.002452× prefill. Retained for instruction efficiency, not a large performance claim. [Round evidence](scripts/perf_round_20261027/packed-combine-scalar/retention.json). Active local copies were bumped to this commit with their in-progress patches unchanged; remote measurements remain pinned to2995. The completed combine source copy was removed.

The preceding **2995bfda8338ca6ae623fbc2657d44e35e665627** prose-only follow-up restores accurate upstream comments/docs and the original copyright year, reducing the overall PR diff by 57 lines. Executable ASTs and all existing upstream headers match; scoped pre-commit passes. The diff-size table is refreshed while benchmark outputs and source attribution remain unchanged. [Prose cleanup receipts](scripts/simplicity_20261027/comment-diff/).

The preceding **54f5c682** structural cleanup places the epilogue beside the shared grouped kernel, leaves utilities at 156 lines, and restores original helpers/comments/dictionaries to minimize review churn. Existing file headers remain unchanged. Validation passes 48 exact replays, 42 existing tests and dependency imports. Of 24 GEMM and eight preparation pairs, 31 have identical encoded instructions; the remaining pair differs only by a reviewed descriptor-register permutation, with scheduling and resources unchanged. No new timing claim. The PR diff-size table was refreshed; all six benchmark outputs retain their measured-source attribution. [Retention and source-copy cleanup](scripts/simplicity_20261027/structure/).

The preceding **1fab0dc8** cleanup passed 120 exact replays, identical encoded SASS/resources for 60 GEMM and 22 preparation pairs, 42 existing tests, and 32 marker-enabled replays. Its optional original helper removals and tuner dictionary deduplication were subsequently undone at the user's request to minimize the final PR diff. [Full cleanup history](IMPLEMENTATION_SIMPLICITY_2026-10-27.md).

The FC1/FC2 boundary audit is complete: keep the one shared regular-TMA mainloop and existing phase adapters. Rubin/Hopper have materially different phase producers; a literal two-kernel split would add duplication. Notes live under `scripts/simplicity_20261027/phase-boundary/`. The follow-up comment/doc audit is complete; all receipts remain under `scripts/simplicity_20261027/comment-diff/`. A new performance round is active as listed above.

The preceding **ed67c485** synchronization cleanup remains retained. The synchronization audit retains shared TMA/SF completion, conditional barrier storage with explicitly aligned CLC metadata, allocator-warp teardown, a later bulk-store reuse rendezvous and removal of a redundant quantizer fallback barrier. Three files change by +41/−42. Final validation passes 120 source-paired exact replays across 60 compiled core pairs, no spills, and all scoped pre-commit checks. The separate quantizer gate passes 24 exact replays and 18 existing tests. The 48-point fixed-tactic CAAC screen is timing-neutral: 1.000965× overall, 1.000658× decode and 1.001271× prefill. Retention is for simpler synchronization and fewer instructions, not a meaningful end-to-end speedup. [Audit](SYNCHRONIZATION_AUDIT_2026-10-27.md), [retention receipt](scripts/sync_audit_20261027/composed/retention.json), [full paired results](scripts/sync_audit_20261027/composed/independent-screen-review.md).

The preceding **9334cb34** commit retains one shared FC1/FC2 CLC autotune flag (360 raw tactics instead of 720), versions the tactic cache and updates existing tests. The exact policy patch previously passed all 13 tactic tests; scoped pre-commit and policy-equivalence checks passed again before publication. [Retention receipt](scripts/shared_clc_bench_20261026/retention.json).

The preceding `9c9ed58a` commit consolidates pipeline initialization fences, changing two files by +12/−4 lines. It passes 88 exact replays per source across 44 compiled core pairs, with unchanged registers/storage and no spills. Compiler review confirms fewer startup instructions and no added steady-state instructions. The 48-point screen is timing-neutral: 0.99918× overall, 1.00028× decode and 0.99808× prefill. Retention is for the requested instruction-cleanup criterion, not an end-to-end speedup claim. [Source, raw timings, compiler review and push receipts](scripts/pipeline_init_fence_20261027/). The completed fence and rejected TMEM source copies are removed.

The preceding `9b4721b0` composition removes the duplicate epilogue TMEM wait, hoists invariant epilogue normalization, runs CLC metadata scheduling ahead of the payload wait, and removes the redundant metadata tail drain. It passes 40 exact changing-route comparisons against saved controls; all 20 core variants retain registers/storage and have no spills. The normalization integration separately passes 11 existing GPU tests. See [composition receipts](scripts/composed_clc_cleanup_20261027/), [normalization integration](scripts/epilogue_norm_integration_20261027/), [terminal wait receipts](scripts/terminal_wait_20261027/), and the [optimization ledger](CLC_GENERALITY_2026-10-27.md).

The latest published six raw model/family tables are [here](scripts/perf_round_20261027/pr-body-ee88cf2a.md), all measured at **f7182d5c** with fresh native AUTO: 377 medians and 37,700 samples. [Publication readback](scripts/perf_round_20261027/pr-publication-ee88cf2a.json) and [remaining gaps](scripts/perf_round_20261027/public-refresh/final-public-f7182d5c/remaining-gaps.md) are recorded. The top speedup table excludes tokens 1/2; NV includes initial activation quantization, MX inputs are prequantized. TRTLLM remains the comparison baseline. The older 7f4e1703 tables remain historical evidence in `perf-general-20261026/final-combined/`.

The shared FC1/FC2 CLC on/off flag reduces raw AUTO tactics from720 to360 with no replacement tuning axis. The paired native comparison is complete and near-neutral in aggregate. The user explicitly chose to retain this simpler policy on 2026-10-27, accepting the recorded point regressions. The FlashMLA-inspired elected-owner experiment is rejected: fixed-lane V2 gives0.97673x and helper-isolated V3 gives0.98316x control/candidate geomean over48 affected points each; all model/backend aggregates regress. The rejected local owner clone is removed after exact source verification. [Complete raw tables and codegen evidence](scripts/clc_elected_owner_20261026/owner-screen-results.md) and [cleanup receipt](scripts/clc_elected_owner_20261026/local-source-cleanup.json) remain. The shared flag is retained and pushed; improving CLC-only performance remains open.

The [full shared-flag speedup tables](scripts/shared_clc_bench_20261026/full-speedup-table.md) include all tokens and the unchanged W4A16 control. Affected-backend overall speedup is 0.99955×, excluding tokens 1/2. The policy patch was retained byte-for-byte on top of `9c9ed58a`; the original timing remains attributed to `9b4721b0`. The completed review copy was removed after verifying it matched the pushed commit. [Workspace bump receipt](scripts/shared_clc_bench_20261026/workspace-bump-9c9ed58a.json).

Historical always-CLC policy trial: The [native all-CLC ABBA screen](scripts/all_clc_20261026/results.md) covers3models×4formats with420measurements/42,000samples, but this policy is **not retained**: decode is close to neutral and some V3/K3 prefill regressions remain material. The superseded four-field tactic cleanup was in `flashinfer-clc-policy-cleanup-20261027/`; its180 Blackwell launch parameter sets match the timed six-field True/True choices, all8 Rubin parameter sets remain identical, and146 existing CPU checks pass. The intermediate all-CLC copy was `flashinfer-all-clc-20261026/`; both stale source copies have now been removed. Both had been bumped to9b4721b0 so their unstaged diffs contain only pending policy changes; the clean policy's stale scheduler docstring was also corrected, with a separate local equivalence receipt.

Bounded-ticket CLC, both deeper metadata defaults and request-before-slot-acquisition were rejected. The final request-order screen reuses three existing points and adds45: all24 decode points are slower, overallGM0.999956×. Keep one-slot fine-grained CLC and acquire-before-cancel. The independent startup/dependency and drain/normalization cleanups are retained at9b4721b0; all jobs for this round finished and GPUs were released. Seven redundant retained source clones and eight rejected/superseded clones were removed; useful helper documents and raw history remain. The all-CLC policy still needs work on prefill performance before retention. Independent frozen remote sources and native C++ cache remain on persistent Weka under `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026`; changed DSL sources use private cache namespaces. Environment remains c3 `fi-moe-nvfp4-port-1026`, B300, explicit `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2. Broad correctness/sanitizers and Rubin hardware validation remain deferred.

## Historical post-rebase status at 0def601d

Canonical checkout: `flashinfer/`, clean and pushed at `0def601d6603df828ea39679b41ccbce64f7f09e`, two commits on upstream `215f83cb27e39b6b973c0691b93fc378a53a10e4`.
The separate `flashinfer-generality-review/` checkout is clean at the same commit. The full 41-commit history, including cleanup `6c3fdea87500227a66c7b8ed3cdcd2127c43293b`, is preserved in the fork's `archive/pr7290-pre-squash-20261026` branch and annotated tag `archive-pr7290-pre-squash-20261026`. See [rebase and integration evidence](rebase-20261026/README.md).

The [rebased scope audit](audit-rebased-20261026/README.md) removes incidental diagnostic/validation rewrites and restores upstream Rubin public defaults, calls, tactics and admission. The public MXFP8 mode inherits upstream `mxfp8`, including unified wiring. The replacement Blackwell device implementation is retained. Current diff: 24 files, +5,594/−7,935 (net −2,341).

All six fresh NVFP4/MXFP tables are published: V3 EP8, V4.1-Flash EP4 and Kimi K3 EP8. See the [published benchmark body](audit-rebased-20261026/pr-body.md), [benchmark summary](audit-rebased-20261026/benchmark-summary.md) and [exact publication readback](audit-rebased-20261026/publication.json). The measured source is `eb141478`, preserved in fork tag `archive/pr7290-benchmark-20261026`. The intervening `65c2c5c4` restores upstream Rubin host plumbing and convenience defaults; its [source equivalence proof](audit-rebased-20261026/rubin-scope-restoration/proof.json) verifies the benchmark execution path and device implementation were unchanged. These timings predate the NVFP4 epilogue arithmetic alignment in `0def601d`. Initial quantization remains opt-in; the NV campaign enables it, while MX uses prequantized inputs. TRTLLM is the performance baseline.

Measured `eb141478` passes 71 focused B300 tests and 24 exact unified MX API comparisons. The `65c2c5c4` source equivalence checks retain the 32 CPU trace checks, 1,080 tactic roundtrips, and upstream host/Rubin equivalence results. The separate `0def601d` port exactly matches the 11-line production change in [PR #7372 at 5ead7268](https://github.com/flashinfer-ai/flashinfer/pull/7372/changes/5ead7268e7e3756abcc3c4ca129da42c818de3c2): standalone standard NVFP4 quantization arithmetic with FP32 activations through FP4 conversion. No tests or reference files were added; scoped pre-commit passes. Eight existing NVFP4 accuracy tests pass at `0def601d` on c3 B300, with zero skips/failures/errors and clean unchanged source. [Port provenance, raw validation and body draft](nvfp4-epilogue-port-20261026/) are saved locally; root owns publication. Broad correctness/sanitizer campaigns and Rubin hardware validation remain deferred. PR #7196 must merge first. W4A4 overall TRT/CuTe geometric means (tokens 1/2 excluded) are 1.0656x V3, 1.0377x V4.1, 1.0165x K3; K3 decode remains near parity and some MX/per-token rows trail TRTLLM. One sweep does not establish stable wins.

All 86 redundant older local source copies have been removed. Experiment outcomes, rationale, scripts and raw evidence remain in the project. The [source-copy ledger](SOURCE_COPY_ARCHIVE_LEDGER.md) records their history and disposition. Unretained experiment recovery archives were discarded as requested. New optimization experiments use separate project-local checkouts with unstaged changes, including the [warp-owned preparation candidate](prepare-warp-20261026/README.md).

## Historical CLC retention round (0c1e)

Retained and pushed `0c1e00fc3e4f913c8c241796c70a29673737c542` in `flashinfer/`;
`flashinfer-pr-scope-review/` matches that clean commit. The latest round is
[regular-TMA CLC and scheduler-depth optimization](SCHEDULER_OPTIMIZATION_2026-10-25.md).
One-slot CLC is selected for one-CTA FC1 tactics, with static scheduling for
FC2, two-CTA tactics, explicit reduced SM budgets, one-wave allocated work,
and grids exceeding CUDA's Y limit. There are no model/token-specific thresholds.
Across the three formats, paired overall ratios versus fca are 1.004298× on
V3 EP8 and 1.011253× on V41-Flash EP4; tokens 1/2 are run but excluded.
Static FC2 codegen also changes, so whole-patch gains are not wholly CLC gains.
The exact final source passes 49 focused tests; broad correctness and
sanitizers remained deferred at this round. Separate unstaged copies were used for the experiments; their current disposition is recorded in the source-copy ledger.

The preceding fca round introduced model/family benchmark selection and
shape/layout/capacity-derived operand stages. PR #7196 should merge first,
then #7290 should be rebased to remove the overlapping combine changes.
All four fresh final-source tables and the direct original-a65 comparison are
published in the PR body. Direct original-to-retained overall ratios are
1.058198× NVFP4, 1.100470× MXFP8 and 1.186711× mixed; the different-host
boundary remains explicit. Current single-sweep NVFP4 TRT/CuTe decode is
1.006310× on V3 and 0.975938× on V41, so stable TRT decode superiority is not
established. [Published body](pr-body-final-0c1e00fc-model-tables.md) and
[exact readback](artifacts/pr7290-published-0c1e00fc-model-tables.json).

## Earlier PDL review round (8c1a)

The PR body for that round showed the original a65 baseline against final 8c1a,
reusing archived B1/B2 and final A1/A2 data. Overall ratios were 1.049936× NVFP4,
1.111071× MXFP8 and 1.160942× mixed W4A8, with the B200-83/B200-92 host boundary
stated explicitly. TRTLLM results were unchanged for that update. PR #7196 should merge first
because both PRs include the standalone-combine changes; rebase #7290 afterwards
to remove the overlap. [Direct comparison audit](scripts/final_before_after_body/audit.json).

Earlier round: [epilogue and whole-pipeline synchronization co-design](PIPELINE_CODESIGN_2026-10-25.md).
Retained and pushed `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e`: direct compile-time
behavior controls selected by FC1/FC2 callers, early preparation/FC1 PDL signals,
and FC2 signaling at producer exit before operand drains. No `is_fc1` flag.
The persistent GEMM targets one CTA per SM. Separate experiment copies remain
unstaged, including the preserved direct-accumulator and unified-readiness trials.
[Final paired evidence](evidence/pdl-retention-8c1a/full/README.md) shows decode
gains versus corrected aab of 2.27% NVFP4, 0.84% MXFP8 and 0.84% mixed W4A8;
NVFP4 prefill is 0.12% slower. [Ten focused tests](evidence/pdl-behavior-focused-validation-8c1a/README.md)
pass on the same frozen source; broad correctness/sanitizers remain deferred.

Separate correctness follow-up: [one-CTA SF proxy-ordering repair](scripts/sf_proxy_fence_experiment/README.md).
All 31 focused cases pass; emitted PTX confirms the fence placement. Its bounded
native full-chain cost was 0.6–0.7%. This repair was pushed as
`aab93f854054de834447bdd8985b8bbd653fb3c8` and is the current paired campaign's
control. The older 98fd whole-PR campaign remains historical evidence; its
different-host ratios are not chained with the new incremental comparison.

Previous round: [physical N16, concurrent TMA issue and SF publication](NARROW_PIPELINE_2026-10-25.md),
including compact scale layouts, independent readiness, NCU diagnostics and
warp reuse. Experiments remain in separate unstaged source copies. No performance
candidate from that earlier round was retained.
The preceding [eight decode candidate screens and TRTLLM source/cubin audit](DECODE_OPTIMIZATION_2026-10-25.md)
are preserved. The stable decode-win target remains unmet.

- Retained PR checkout: `flashinfer/`, clean and pushed at
  `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e`.
- Current unstaged review: `flashinfer-pdl-behavior-review/`; identical clean
  measured freeze: `flashinfer-pdl-retention-frozen/`.
- Frozen review checkout: `flashinfer-regular-tma-review/`, an independent clone
  rooted at442. All experimental source changes are unstaged for
  direct review. Do not stage, commit or push this copy during experimentation.
- Closed pipeline variant: `flashinfer-regular-tma-pipeline/`, an independent
  clone with unstaged changes preserved for review. Reusing loader warps and
  barrier storage for separate weight/activation TMA pipelines did not produce
  a repeatable native gain; it is not being integrated.
- Frozen measured candidates: `flashinfer-regular-tma/` (grid16),
  `flashinfer-regular-tma-ldg256/` (256-bit payload copies), and
  `flashinfer-regular-tma-validcopy/` (copy only valid payload rows). Each is an
  independent clone with its source changes preserved unstaged. The tiled SF
  transpose in `flashinfer-regular-tma-sf-tile/` is closed after a 2–3x slowdown.
- Retained design: byte-preserving routed activation/SF preparation followed
  by regular FC1 B/SFB TMA, preserving fused activation and dynamic MMA N.
  Preparation is included in full-chain timing. The latest 39-row screen is in
  `evidence/regular-tma-auto-validcopy-A1/`. The review copy removes statically
  dead Gather4 code from this candidate; its normalized AST matches validcopy.
  Its own final paired campaign reused original B1 and completed fresh A1/A2/B2:
  `evidence/regular-tma-final-review/`. The exact kernel files are now retained
  in98fd3566b, plus a proven docstring-only wrapper update. New packed combine
  and non-TMA SF-load experiments use separate independent source copies.
- Harnesses, raw results, design notes and archived prototype source:
  `scripts/fc1_regular_tma_experiment/`. Future experiment implementation changes
  live directly in a reviewable FlashInfer source copy, not only in overlays.
- Earlier retained-source evidence: `evidence/regular-tma-final-review/` (complete
  paired ABBA), `evidence/regular-tma-review-exact-126/`, and
  `evidence/regular-tma-review-validation/` (95 tests,126-case memcheck/racecheck
  probes and three reference memchecks, all passing). Previous442 results are
  preserved in their original evidence directories.
- Closed non-TMA experiments: [raw-pair packed combine](scripts/packed_combine_review/README.md)
  saved less than0.25µs in prefill and was not retained; [SF source vectorization](evidence/prep-sf-vector-review/summary.md)
  regressed all three preparation phases. Source copies
  `flashinfer-packed-combine-review/` and
  `flashinfer-regular-tma-sf-vector-review/` remain unstaged for review.
  Detailed decisions and evidence hashes are in the
  [optimization ledger](OPTIMIZATION_LEDGER_2026-10-24.md).

Closed decode residency family: [K8/two-stage](scripts/small_n_occupancy_experiment/README.md)
proved nearly two CTAs per SM after early TMEM permit release but lost 1.56–3.49%;
[K4/four-stage follow-up](scripts/small_n_k4_occupancy_experiment/README.md)
lost 4.0% at T32/N16. Both source copies remain unstaged, with all samples and
resource evidence archived. Production was at 98fd for those experiments.
The [small-N linear-SF bypass](scripts/small_n_linear_sf_experiment/README.md)
kept regular B TMA but showed no full-chain gain at T32/N16 (0.997931×); its
three-file unstaged prototype and all600 samples are preserved.

Standalone upstream FlashInfer optimization. Source checkout: `flashinfer/`, branch `codex/w4a4-split-dynamic-n`, baseline `a65d5b09e7e4c4c5c160b0161c48becd100b3970`.

The existing FC1/FC2 wrappers and MoE orchestration are retained. SM100 NVFP4, MXFP4, MXFP8, and mixed MXFP8/MXFP4 use weights on MMA A/M and routed activations on B/N, with runtime instruction N. Both old Blackwell kernel bodies are superseded by one shared core. It supports M128/one-CTA geometry at all routing capacities and M256/two-CTA geometry at N128/N256; FC1 also offers logical M512/N128 as two physical M256 instructions sharing activations. FC1 and FC2 choose channel geometry independently. Rubin remains a separate architecture implementation. MegaMoE provides implementation reference only; no MegaMoE source changes. Gated Blackwell FC1 now interleaves up16/gate16, matching the warp-local geometry of SM100 GenPhase MegaMoE while retaining CuTe's semantic order. FC2/non-gated rows and public call signatures remain unchanged. The existing weight preparation function selects group16 on SM100/SM103 and group64 on SM107. W4A16 shares this preparation and removes its now-redundant gated decode permutation.

Per-token NVFP4 remains supported with its existing row scales, quantization, activation, and combine semantics. The replacement changes physical MMA/cluster geometry and live instruction width; preserve logical values and existing phase dtype restrictions. Preserve the BF16/FP16 routing-scale conversion point before FC2 accumulator scaling.

## Current benchmark scope

NVFP4 optimization target: repeatable decode wins over native non-distributed TRTLLM W4A4 on the retained 4–512-token grid. Keep 1/2-token measurements outside retention aggregates. Earlier 8c1a final-source two-repeat ratios were 1.003372× decode, 1.155006× prefill and 1.042634× overall. T32/T128/T256 remained slower in both repeats, so that campaign did not meet the stable across-shape decode target. [Historical comparison](evidence/pdl-retention-8c1a/full/README.md).

Every NVFP4 performance update also includes a same-shape, single-GPU native
TRTLLM W4A4 reference column (or an explicit pending status). The reference keeps
TRTLLM's native finalize enabled and distribution-aware autotuning disabled; it does not
change the unfused CuTe before/after retention protocol. Its first two later
sweeps reuse the completed CuTe A1/A2 rows. See the
[comparison protocol](scripts/trtllm_nvfp4_reference/README.md).

Latest user scope: full-MoE before/after for per-tensor NVFP4 W4A4, homogeneous MXFP8 E4M3, and MXFP4 weights × MXFP8 E4M3 activations. Fused finalize is disallowed for every primary arm. BF16×BF16 was explicitly dropped because this SM100 split backend has no existing path. Preserve per-token functionality and other low-level dtype support, but do not run additional primary campaigns for those modes. W4A16 receives only the shared gated-layout compatibility update.

Reuse the existing per-tensor NVFP4 baseline. Existing fused-W4A8 and phase-only homogeneous baselines are archived diagnostics, not substitutes for the newly requested unfused full-pipeline arms. A common benchmark-only host assembly uses existing generic FC1/FC2 kernels, native routing, deterministic unpermute, and normal AUTO on both revisions; no production API extension is required. Native selectors are `cute-dsl-mxfp8` and `cute-dsl-w4a8`, with `--no-fused-finalize` required.

## Validation environment

Current C1 devbox `fi-w4a4-narrow-1025`, namespace `ziangli`, eight B200 GPUs on
B200-92, explicit image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.78,
Torch2.12.0a0+5aff3928d8.nv26.05, CuTeDSL4.7.1. The prior
`fi-w4a4-pipeline-1025` on B200-83 no longer exists. Its primary and TRTLLM
measurements remain historical evidence; new diagnostic controls are adjacent
on the replacement node, with no inherited controlled TRTLLM ratio. A new-node
TRTLLM comparison is pending only if a candidate earns broader retention work.
Durable remote project:
`/data/ziangli/flashinfer-w4a4-split-dynamic-n/recovery442-20261025`, linked from
`/workspace/flashinfer-w4a4-split-dynamic-n`. Source the candidate or baseline
cache environment in `scripts/recovery442/` before GPU work. Detailed recovery,
build-target equivalence and binary-identity limits are preserved there.

Use `/usr/local/bin/h ssh fi-w4a4-narrow-1025 -c c1 -n ziangli -- bash -lc '<command>'`.

## Evidence

`results/baseline-r1.json` and same-stem log/caches remotely contain the completed first NVFP4 baseline sweep. The new unfused baselines are `results/mxfp8-unfused-baseline-r1.json` and `results/mxfp4-unfused-baseline-r1.json`. Preserve and reuse all three; do not rerun them. The earlier fused W4A8 adapter/campaign under `scripts/w4a8/` is archived diagnostic evidence outside the primary scope. See `scripts/BENCHMARK_PROTOCOL.md` for the native benchmark protocol, exact token grid, retention exclusions, and ABBA methodology. Development smoke snapshots and logs live under `transfer/` and remote `logs/`.

`scripts/per-token/` preserves the earlier W4A4 experiment with `use_per_token_activation=True`. Its existing GPU1 evidence is outside the primary campaign and must not be substituted for the per-tensor baseline. Initial activation quantization is excluded; internal per-token rescaling and requantization remain in the timed MoE call. Do not compare timings across modes or GPU identities as paired measurements.

Performance iteration precedes full correctness/sanitizer validation. Existing tests are updated for the new physical tile axes; no new test suite is introduced.

## Candidate checkpoints

- `22d1305ecd4476ad2791126e6536ef4dff0cb4cd`: initial dynamic-N core with a temporary payload exchange; superseded.
- `00e4ff61cd116a55970abc9b052f6f8e2b982325`: warp-local up16/gate16 preparation/epilogue, minimal W4A16 consumer update; existing API workflow retained. Full TRT row-shuffle exploration is archived under `transfer/trt-layout-proposal/` and `artifacts/trt-layout-draft/` and is not part of this candidate.
- `653924161b0ed19ee048e23b669595bc9c2cf10f`: explicit routing/tactic-width validation; pushed for review. The first full NVFP4 sweep regresses (decode 0.825x, prefill 0.358x before/after); this checkpoint is not retained. Exact raw records and summary are under `evidence/nvfp4-screen-65392416/`.
- `5b9d2f6d`: native unfused MXFP8 and MXFP4×MXFP8 benchmark selectors and common assembly. Both candidate T4 runtime smokes passed. This does not establish numerical correctness or comparative performance for those modes.

- `de4f1aa4989998676d1d8a09da7c4afe1cb7c75b`: hoisted gathered addresses, conflict-free SF copies, TMA weight SF and contiguous FC2 activation loads, N256 support, and stage policy. All three full-grid screens complete, but this checkpoint is not retained: NVFP4 decode/prefill 0.912/0.611x, MXFP8 0.971/0.830x, mixed W4A8 0.959/0.789x. These are single before/after screening ratios, not final ABBA results. Raw evidence is in `evidence/nvfp4-screen-de4f1aa4/` and `artifacts/unfused-blockscaled/candidate-screen-de4f1aa.tar.gz`.

- `d9074cb6e9e934d387e358a069e90ddf084f5ef7`: integrated Gather4, M128/one-CTA and M256/two-CTA shared core, pipelined epilogues, preloaded FC2 metadata and 256-bit stores. Eleven paired tactics preserve route N while choosing channel geometry independently. Pushed for review. 49 existing capability/tactic/architecture-layout checks passed. All three full-grid screens completed: NVFP4 overall 0.897578x, MXFP8 0.973208x, mixed W4A8 0.942054x baseline speed. This checkpoint is not retained; no A2/B2 runs were launched. Complete B1/A1 tables and provenance are in `evidence/combined-screen-d9074cb6/`.

Source deployment uses a Git bundle into a dedicated transfer directory, then fetch/reset of the task-owned candidate. Never sync a partial source directory directly onto the candidate: HAI sync mirrors the directory and removes omitted files. Smoke23 stopped during import for this reason; it provides no numerical evidence. Candidate source and editable data links were restored from the committed checkpoint before subsequent testing.

- `94be9a712a46ab34b902605c4a34d26a4c570692`: enable small-N epilogue overlap for FC2 and nonmixed FC1; preserve mixed FC1 and large-N policy. 306 paired exact cases across all six formats passed, including K-pipeline wrap and accumulator reuse. Changed-file pre-commit passed. Pushed to PR #7290. Full three-mode screens completed: overall baseline/candidate ratios NVFP4 0.924794x, MXFP8 0.996456x, mixed 0.973007x. All three still fail retention; no A2/B2 rerun. See `evidence/combined-screen-94be9a71/`. Detailed phase evidence: `scripts/decode_geometry_experiment/RESULTS.md`.

- `7829fc00dc7121341cc40cd4190660507e006490`: issue FC1 scale loads before Gather4 and use an in-kernel shared-memory bulk FC2 epilogue when it fits without reducing operand stages. N<128, fused finalize, and other output formats retain the existing direct epilogue. The inactive M384 two-CTA tail is explicitly guarded. Changed-file pre-commit and paired format/per-token checks passed. Final three-mode native screening is complete: overall B1/A1 NVFP4 0.933210x, MXFP8 1.002184x, mixed 0.975097x. NVFP4 and mixed regress; MXFP8 is near parity. No A2/B2 or broad sanitizer runs. Full raw tables and provenance: `evidence/combined-screen-7829fc00/`.

## Current parallel optimization pass

See `OPTIMIZATION_LEDGER_2026-10-24.md` for the ongoing scheduling, stage/cache/PDL, register-budget and epilogue experiments. All intermediate evidence stays local. The PR body will report performance only for the final retained candidate.

- `285bae770c688328f0da82660c307a5be7417375`: retained incremental stage policy and padded STSM stores; pushed. Full-chain fixed-tactic checks pass exact outputs in all three modes; no primary retention claim.
- `13ca1475d96839f3bf3c46699cc63204b4d3b409`: combined logical M512 activation reuse, FC2 overlapping accumulator windows, and small-N wider-K stages. Pushed and deployed;56 capability/tactic/architecture tests pass. Primary A1 completed against preserved B1: overall NVFP4 0.973209x, MXFP8 1.055357x, mixed 1.054568x. NVFP4 fails retention; A2/B2 not launched. All12 combined full-chain exact smokes pass. Follow-up cache/load/TMEM/SM103 experiments use isolated snapshots of this clean checkpoint.
