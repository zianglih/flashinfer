# General swap-AB pipeline optimization — 2026-10-27

Baseline: PR7290 `e2728a2908f38cbcfa997c031bea059e3724ccde`. The fresh all-model baseline is in `../swap-ab-full-rerun-20261027`. Selected changes passed the full screen and were committed as `1e69d0a39`; further experiments stay unstaged in separate active review clones.

## Retained

- **Weight reuse priority:** use the normal L2 priority for weight payload and scale TMA when a neighboring route tile belongs to the same expert; stream single-tile experts with evict-first. Compute once per work tile in the TMA producer warp, including startup prefetch. Activation priority remains unchanged. This follows actual routed reuse and introduces no dtype/model/token threshold or tactic. Removed the now-dead separate private weight-scale policy. See `cache-scales/` for the nested C/W/S/S/W/C screen and source/codegen receipts.
- **Prepare scale preload:** issue each lane's scale loads before the payload copy and retain their values in registers until the existing scale stores. Same grid, thread count, layout, arithmetic, and synchronization. See `prepare/` for exact graph replay, SASS, CUPTI and Nsight evidence. The V3 full-chain gain exceeds the prepare-only trace difference and must be judged by the full campaign.
- **Idle producer CLC waits:** five affected cells are effectively neutral (GM -0.035%, worst -0.247% with 0.222% control drift); include for instruction/synchronization sanity, not a speedup claim. Keep physical CTA roles and all full-CTA joins; only active producer warps participate in the per-tile producer loop and CLC metadata barrier. See `clc-producers/`.

## Closed directions in this iteration

- Uniform normal weight priority hurt decode, despite large-prefill gains.
- FC2 metadata hoisting and source-level packed-scale shuffle grouping did not justify retention.
- Unsigned prepare-index rewrites and split payload/scale warps regressed representative cases.
- Reducing finalizer vector capacity generated identical machine code; no source change.

Raw evidence, source patches, scripts, and rejection details remain in each experiment directory. The full screen uses fresh candidate native AUTO, unchanged verified control winner selections, and fresh matched-route CUPTI samples for every displayed cell. No historical timing rows are mixed into the final result. Tokens 1/2 run but remain excluded from retention and the displayed table. Sanitizers remain deferred.

## Frozen combined candidate

`flashinfer-cache-scales-perf-review`, parent `e2728a290`: 57 additions / 26 deletions in three files. Kernel SHA256 `c772b41dff20189180c68cadd5a8f3e27a1a4a23c8fe9f15b495350c5f46fe63`; wrapper `9f094f2b254b943bd7cdbb89906bb708541c5ce2d2a08ecb196300951bb94ff7`; prepare `1f35cd5dea0d691a8bd6a0e721ef626cd4ed72c553781b6bd90e0b2c75f3a97f`. Ruff and diff checks pass. Combined gate passed: 24 existing exact tests (no skips), plus 96 static/CLC × PDL graph replays matching baseline storage-bit hashes, including changing and empty routes. All eight full benchmark campaigns subsequently completed; the retained commit and publication receipts are recorded below.

## Final retention decision

Retained as `1e69d0a391fd926d21a35388cacf2df3c1c22baf`. The complete eight-GPU, 54-phase campaign contains 179,400 fresh CUPTI samples with verified route/source/cache identity. Across blockscaled dtypes and tokens >=4: decode GM +4.04% against TRTLLM / +19.03% against non-swap; prefill GM +10.30% / +9.17%. These compare final implementations with freshly measured baselines, not causal improvement over the previous campaign. Existing tests:24 passed plus96 storage-bit graph replays. Full-suite and sanitizer runs remain deferred.

Two crossed-source/winner checks isolate suspicious N3U losses: per-token4096 source -0.15% with the former winner and +5.02% with the fresh winner, while the fresh winner itself costs3.37% on retained source; MXFP4x8T4 source -0.54/-0.57% at K8/K4, versus4.80% from selecting K4. Retain the general kernel changes with these small fixed-tactic costs acknowledged; investigate tuning-workload fidelity separately. No tactics or public policies changed.

Changed-file pre-commit checks pass. Formatter changes two pre-existing formatting nits; source-equivalence receipt proves identical ASTs versus the measured bytes. All raw evidence, frozen sources and rejected-direction notes remain local.

## Closed tuning follow-ups

- Actual-input profiling is rejected: a zero-local-work warmup naturally selected a tactic that was12.237% slower on the real N3U per-token4096 workload, with0.010% control drift and0.027% candidate spread over400 fresh CUPTI samples. Source, shapes, 320 admitted tactics and11,180 real local routes were identical. No need to expand the holdout after this decisive counterexample. Evidence under `actual-routing/`; its owned experimental source copies were removed after verification.
- First-hint follow-up is rejected and closed:48 exact replays/source and PDL-off codegen identity passed, but the32-cell broader screen was GM -0.129% / decode +0.070%, with unstable MX prefill cells. Skipping two first-tile neighbor loads did not justify added per-tile state/branching. Evidence remains under `first-hint/`; owned local and remote candidate source copies were removed after hash/ownership verification. Measured controls, caches and results remain.
- `flashinfer-weight-layout-api-review` is unowned pre-existing WIP and was not touched.

The closed combined candidate review clone was removed after commit/source verification. PR7290 body readback matches SHA256 `445f194f21dce715e3e54ec622ad53aeeb2dd8485515a2142b0d833965e81949` at `1e69d0a39`; refreshed heatmap is under `retained-rerun/plots/`.

Actual-route profiling screen: N3U per-token4096 +3.048% (320.210→310.738us), W4A4T4096 +7.934% (236.610→219.218us), MXFP4x8T4 neutral with the same winner. Eighteen phases/1,800 CUPTI samples verified; all43 control/candidate profile pairs have identical admitted tactics. W4A4's native selection now uses two-CTA FC1. These seed-specific gains do not justify retention given the serving-warmup counterexample above. No production tuner policy change.

Two separate follow-ups are authorized: a swap-AB-only Hopper-style seed515 global top-k initializer, preserving existing native measurement modes; and unchanged-source graph-versus-eager native profiling for the two N3U NV prefill cells. Neither adds tactics or cache axes. The latter is a measurement/winner-selection diagnostic, not a kernel speedup: SGLang currently leaves the public graph-profiling argument at its eager default even when serving CUDA graphs. Production defaults, existing public options, W4A16 and legacy/Rubin remain unchanged during these experiments.


Both tuning follow-ups are closed. Seeded-uniform routing produced no gain in the fresh matched screen (W4A4T4096 −0.285%, per-tokenT4096 −0.264%, MXFP4x8T4 −1.513%; 1,800 CUPTI samples), and its owned source copies were removed. Graph-versus-eager native profiling did not establish a policy gain: a fresh eager control selected the same per-token winner and the same faster W4A4 geometry. All evidence is retained under `synthetic-routing/` and `tuning-measurement-audit/`.

## Retained warp-specialization redesign

Retained and pushed as `99f4d0c277746fb706d10a4bb303c98c5f31e0a9`: eight fixed warps, independent all-TMA operand producers, private route-padded scale atoms, one shared operand ring, and natural weight prefetch through the normal loop. The local review clone was bumped to that commit, verified clean, and removed after retention; the canonical checkout contains all pushed changes. The unowned weight-layout review copy remains untouched.

The source-bound gate passed144 exact public replays,28 existing accuracy cases,96 preparation checks,110 routed quantizer replays and six default quantizer contracts;72 generated candidate binaries have256 threads and zero spills. The80-cell matched CUPTI pilot is +0.759% overall, +1.189% forT4/T64 and +0.473% forT512/T4096/T16384. All80cells remain included. V3/K3 per-tokenT4 native-pair losses are mainly selected-winner effects; fixed old-winner source deltas are +0.015%/−0.256%. Eleven16K drift repeats were bounded and preserved separately; nine remain inconclusive. N3U W4A4T4096 +7.318% includes a winner change and is not a source-only claim. No tactic axis or special-case selection was added.

All applicable commit hooks pass. Two existing option-dictionary typing errors were fixed with local annotations and required Ruff formatting in `fused_moe.py`; normalized AST and recursive bytecode equivalence to gated r2 are recorded, excluding compiler-generated source/debug locations only. Four changed kernel/helper files are byte-identical to the gated source. Fresh full PR table/heatmap rerun is running on eight GPUs; historical public evidence remains labeled1e69 until refresh.
