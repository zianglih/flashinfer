# N32 optimization with GLM5 as the primary workload

User request: audit and improve the N32 hot path, then use the retained C2
devbox only after the ongoing K3 tests and benchmark finish. This supersedes
the earlier no-devbox instruction for the completed tanh-revert turn.

Starting source: `866c80d0c70a90624b4c2056d12d1543d709609e`, draft PR #6277.
Preserve the original SiTU approximation and instruction-exact reference,
two decoder warp groups, original scheduler, PDL, fused deterministic combine,
and disabled fused TMA/FC2 reduction. Routing is prepared outside timing.

## Execution boundary

- Existing owner: blog K3 campaign
  `captures/b300-rerun/pr6277-866c80d0-k3-20261009` under remote blog root
  `/data/home/ziangli/nvfp4-w4a16-blog-draft`.
- Its supervisor owns
  `/data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/.k3-perf.lock` through
  the whole campaign. Read-only status checks are allowed; no source changes,
  installs, GPU experiments or interruptions until it completes.
- Before optimization, require successful campaign completion, acquire the
  same lock and confirm the GPUs are idle. Use an independent study checkout;
  preserve the existing blog source cache and captures.
- Retain the devbox after this work. Do not cancel or remove it.

At 12:18 UTC, the owner recipe was verified to run **two** native 100-sample
sweeps. Sweep 1 finished at 12:10 UTC; sweep 2 is active. The completion gate
waits for the full campaign, including both sweeps and its final receipts.
Earlier observations of T16384 described sweep 1, not campaign completion.

The full K3 campaign completed successfully at 12:43:56 UTC. The local watcher
then transferred the sealed v1 bundle and launched its supervisor at 12:44 UTC
(PID 187931). The gate and dispatch receipt are preserved in
`evidence/n32-glm5-v1-dispatch.json`; no optimization work started before that
completion. GPU idle, lock, source and runtime checks remain mandatory in the
remote supervisor.

The initial control exited before any timing samples: the new checkout lacked
the ordinary setup-generated `flashinfer/data` source/include symlinks, so Ninja
could not find `fp4Quantize.cpp`. All eight ranks reported the same missing path.
The queue stopped at 12:45:39 UTC and left both candidates unrun. Preserve this
failed capture; the retry will create the standard source links under the lock
and use new run/queue namespaces without reinstalling packages or changing the
measured harness.

The corrected control `glm5-n32-866c-control-v1r1` completed all 13 points
successfully; all 104 rank/tactic receipts agree and all 100 samples per point
are retained. Its selected tactics and timing differ at some points from the
historical AUTO16 run (notably M128 at T64). Candidate retention therefore uses
the fresh control, with historical BEFORE/AUTO16 columns kept separately.
The FC1 candidate follows before the independent FC2 candidate. The pinned
Compute Sanitizer 2026.3 binary is staged under project-local `tooling/`, with
its checksum and version in `tooling/compute-sanitizer-2026.3/staging-c2.json`;
no sanitizer GPU checks have run yet.

## Measured candidate decisions

`glm5-n32-fc1-n16-v1r1` completed all 13 points. Versus fresh866c, geometric
speedup is 1.00765x across eleven retention points and 1.00982x for decode.
Do not retain this candidate: T64's largest gain changes M128 to M256, T16/T128
also switch group sizes, and T4/T32/T256/T512 regress. The five retention
points with identical complete tactics are flat in aggregate (0.99949x);
three of those are the unchanged prefill path. The added narrow branch and
shuffle path do not have sufficient performance support. No numerical tests
were launched for this rejected candidate.

Full medians, tactics and untrimmed samples remain in
`evidence/n32-glm5-v1r1-after-glm5-n32-fc1-n16-v1r1-20261009T132918Z.json`
and its Markdown table. FC2 direct-pairing/early-release is the next independent
arm. A smaller branch-free FC1 full32 register-transpose follow-up is sealed
in `next-n32-glm5-v2-retry`; its only runnable arm reuses the successful
fresh control and cannot replay it accidentally.

`glm5-n32-fc2-combined-v1r1` also completed all 13 points: 1.00726x across
the eleven retention points, 1.00764x for decode, and 1.00626x for prefill.
T64 improves 169.666 to 157.730 us with the same M128/N32/G512/epi tactic
and separated within-run IQRs. T32 and T128 regress; all prefill IQRs overlap.
This point-specific signal is not yet enough to retain a broad optimization.
Raw evidence is in `evidence/n32-glm5-v1r1-after-glm5-n32-fc2-combined-v1r1-20261009T134535Z.json`.

The final bounded follow-up is `next-n32-glm5-v3`, seal
`3508e877c461133a2e17292cb9869e7106cde8ce6360116be220276ed8608153`:
the branch-free full32 FC1 transpose, then the independent FC2 version that
pairs adjacent FP32 register values for multiplication before cross-fragment
BF16 packing. Both reuse the successful fresh control. This replaces the
unused v2 queue; do not launch that duplicate. V3 was independently reviewed
and dispatched as PID207840 after the prior queue completed and restored866c.
The source and original scheduler, SiTU arithmetic, decoder groups, AUTO16
catalog and timing protocol remain isolated and fixed between candidates.

`glm5-n32-fc1-register32-v2r1` completed all 13 points: 1.00235x across
retention points and 1.00052x for decode. Reject this full32 FC1 candidate.
T128 regresses from160.481 to166.866 us with the identical M256/N32/G1024/epi
tactic, while the T64 gain changes M128 toM256. T512 is flat. The original
activation math is preserved, but the additional register transpose has no
useful aggregate performance support. No FC1 candidate is retained, and the
two proposed FC1-specific exact-test rows remain unapplied. Complete evidence:
`evidence/n32-glm5-v3-cumulative-after-glm5-n32-fc1-register32-v2r1-20261009T140432Z.json`.

Final FC2 adjacent-pair multiplication completed all 13 points, and v3 restored
the control and exited0 at2026-10-09T14:20:41Z. Speedup is1.00921x all11,
1.01103x decode and1.00439x prefill. T64 improves169.666 to155.363 us with
the same M128/N32/G512/epi tactic, but T4/T32/T128 regress with separated
within-run IQRs as AUTO switches toM128. The other seven decode points are
flat in aggregate (0.99995x, sensitivity diagnostic only; no retention-point
exclusion). Prefill IQRs all overlap. Reject both FC2 candidates: preserve
their point-specific evidence for future work, but do not add code for this
mixed sub-1-percent overall gain.

**Final source decision:** retain upstream PR6277 head
`866c80d0c70a90624b4c2056d12d1543d709609e` unchanged. No new epilogue experiment
or extra FC1 test row is applied. Existing N32 tiles and16-tactic catalog remain.
Proceed with the owned HashInfer sync,17logical/52rank-local exact cases per
repository, and six HashInfer N32 sanitizer cases. All raw samples, full token
lists and selected tactics are retained in the final cumulative report:
`evidence/n32-glm5-v3-cumulative-after-glm5-n32-fc2-adjacent-mul-v3r1-20261009T142049Z.json`.

## Measurement contract

GLM5: D6144/E2048/N256/K8, EP8, one routed-expert layer on eight B300 GPUs.
Use the native `benchmarks/bench_cute_dsl_moe_distributed.py`, AUTO16 tactics,
100 untrimmed cold-L2 CUDA-graph CUPTI samples, three warmups. Always run
`1,2,4,8,16,32,64,128,256,512,4096,8192,16384`; exclude only 1/2 from aggregate
retention. Report selected tactics for every candidate column. Existing
original BEFORE and intermediate results remain separately attributed.
Run the existing zero-tolerance correctness cases only after a useful
performance gain is confirmed. Do not run IKET.

Historical GLM5 AUTO16 selected N32 at every decode point. M128 appeared at
T1/T8; the other decode points chose M256. All three prefill points selected
M256/N128. New N32-only changes should leave those larger-tile paths intact.

## Candidate audit

1. FC2 direct pairing: scale FP32 top/bottom fragments into the BF16-pair
   order consumed by the transpose, avoiding conversion followed by repacking.
   Preserve the same multiplication and BF16 rounding for every element.
2. FC2 early accumulator release: after the final scratch loads complete,
   release the accumulator before the remaining register permutation/packing.
   Keep output publication and peer-return fences unchanged.
3. FC1 at most 16 routed tokens: evaluate a narrower N32-only load and
   register transpose. Preserve all activation arithmetic, normalization,
   routing-weight order and BF16 handoff. Symbolic layout proof is required
   before GPU screening; it is not a substitute for exact validation.
4. Lower-priority accumulator buffering experiment: N32 leaves 64 TMEM
   columns unused after two accumulator and three decoded-weight stages.
   Four accumulator stages can use those columns without changing the
   decoder design. All ring storage/state/layout definitions must agree.
   Extra buffering may have no value if another pipeline limits progress.

Candidate artifacts live under `evidence/candidates/n32-glm5/`. They are
experimental until measured; preparing them does not modify the active PR
source. A fresh control and the same-node AUTO candidates will distinguish
useful changes from noise or different tactic selection.

The historical `packed-transpose-v1` K3 trial was flat, but evaluated a
different change on N64/N128: it kept both 32-token halves and their activation
work, then packed the BF16 results into one scratch transpose. The N16 candidate
reduces raw loads and activation work and removes scratch TMEM. It therefore
has a distinct mechanism. Confirm x8 loads, reduced arithmetic, 12 shuffle
sites and the release boundary in the narrow branch, rather than comparing
whole-binary counts that include its fallback.

FC2 direct packing has a weaker hypothesis: the compiler may already fold the
old BF16 gather. Retain it only if measured results and generated instructions
show a benefit; inspect PRMT/MOV packing, release placement, and local-memory
spills. A fixed warp register budget alone does not demonstrate spill freedom.

## Downstream sync and sanitizer gate

After completing performance selection, sync the owned W4A16 subset at
the final upstream PR #6277 head into an independent `hashinfer/` checkout
and open a draft PR to the private kernel fork, following PR #11's documented
namespace/adapters/source-pin pattern. Preserve HashInfer-owned tracing,
compiler controls and cache namespace. Do not merge or advance HAI gitlinks.

Extend the existing `tests/moe_ep/test_w4a16_megamoe_sanitizer.py` with focused
N32 coverage. Validate every retained N32 AUTO tactic, both routing-weight
placements, eager and graph replay, actual per-expert 15/16/17/31/32/33 tails
and empty/refill reuse. Use memcheck, synccheck and racecheck serially with
strict per-rank clean reports. Record exact tool/source pins and the existing
tensor-checker exclusion; do not claim broader race coverage than the tool
provides. Keep numerical validation in the existing zero-tolerance suite.

Draft HashInfer PR14 is now open at `f088518a8b0f24018bfd49420457eb9f873fcfaa`,
syncing upstream866c. The complete110-file identity matches the committed
source and refreshed25-pass host checks; scoped pre-commit passes. Final owned
parity audit SHA256 is`17d9a874e194c5ae588a8b2733b0dcccbfc624bbae9052d20b945c4f7e459a64`.
The GPU qualification sequence launched asPID221166 using exact-v3 and
sequence-v2. Both exact gates now passed:17logical/52rank-local cases each,
zero failures or skips, with source identities unchanged. HashInfer N32
Compute Sanitizer was pending at that checkpoint; the final v2 pass is below. The public PR6277
body now contains the current866c GLM5 results and completed exact evidence
(body SHA256`efecfd5fbffd005e25e8d74543a4c6956e6fbb4a498ffb595b91e48aa0b2fdac`).
Its first source-preflight attempt
mistook a tracked CCCL directory symlink for a regular file. V3 records literal
Git link targets and their hashes, with no vendored source changes. The
HashInfer flat110-file identity remains unchanged. No GPU test ran in that
failed preflight. See`evidence/n32-qualification-dispatch.json` and
`evidence/n32-final-source-v1/` for final commands and identities.

### Sanitizer runner correction (GPU source unchanged)

The first memcheck/FC2-routing case passed all eight ranks, all eight N32
tactics and all nine routing rounds (`1 passed, 17 deselected in 342.37s`).
The subsequent strict source-map check rejected a single generated PTX file
at the checkout root. All 110 committed files remained byte-identical; no
file was changed or removed. Preserve this attempt as partial evidence only:
`correctness/n32-retained-sequence-v1/hashinfer-sanitizer` and archive
SHA256 `63b74c3c3cdbf773837b183c27353eeac7ef60ad604aa4587df68e23214f87a5`.

Sanitizer helper v2 sets `CUTE_DSL_DUMP_DIR` to an owned per-process output
directory before imports. It retains the full source-map invariant, all
selectors and checks, and reruns all six cases in a fresh cache namespace.
Independent CPU startup checks passed. Seal:
`36be94be6d3e1952656666e25e185dc02b7a5ec175a556b07d6c9203fbbbe30b`.
The known PTX was moved, with its hash verified, to the queue's preserved
compiler-output directory under the shared lock; the source is clean again.
PID 230278 ran `correctness/n32-retained-sanitizer-v2` against the same
f088518 head. No GPU source or test changed, so both completed exact gates
remain applicable. See `evidence/n32-sanitizer-v2-dispatch.json`.

### Final qualification: complete

Completed at2026-10-09T15:50:59.463185Z on unchanged downstreamf088518:
**6 logical sanitizer cases /48 clean rank logs, zero skips**, covering all
8N32 tactics and9ordered routing rounds per rank. Both FC1/FC2 routing placements
pass memcheck, synccheck and racecheck. Exact qualification also passed17logical
cases/52rank-local checks in each repository (104rank-local passes total).

- Complete sanitizer output: `correctness/n32-retained-sanitizer-v2`.
- Exit receipt SHA256: `9b0e0555045996d4d78c3d6c2522c34f8e0c8ad1ac5b8609b7fd5c9db099dd84`.
- Archive SHA256: `db4b2cbb752a4ff0a91b1e8bf63fb9f0940e31c0736dc7734cd111231c540a56`.
- Frozen110-file source before/after: `b902b3da20ce31ef04130e051e03bf4afdd2f4bc864e15b1af8baf949cf7cd46`.
- Runtime before/after: `49750a21e1ece24fbf3cc811a9905fa5f3103aae039095baa919b74c2cd35036`.
- Primary strict audit: `evidence/n32-qualification-progress/hashinfer-sanitizer-v2-validated.json`.
- Independent audit: `evidence/n32-sanitizer-v2-independent-complete-v1.json`.
- The independent audit also byte-checked all366regular archive members.

The existing memcheck `--check-tensor-ops no` exclusion remains; compiler TMEM,
bulk-copy and stream-order checks remain enabled, with no diagnostic suppression.
This qualifies the instrumented owned kernel scope, not arbitrary global-memory,
NVSHMEM or TMEM race freedom. Full model/HAI serving tests were outside this task.
The devbox and caches are retained; all8GPUs were idle with no compute processes
in the final receipt. See `DEVBOX_HANDOFF_N32.md` before subsequent work.

Final publication verified: HashInfer PR14 remains draft/open atf088518, with
complete raw validation output and self-contained reproduction commands. Body
SHA256`dd51515dd96dfeafbe7d0b1ec8198f2e5b9228818ed0981ab93bfa16444af8c1`;
receipt`evidence/hashinfer-pr14-complete-published.json`. Upstream PR6277 head
was rechecked at866c during publication. Neither PR was merged.

## Sanitizer simplification follow-up

Current local/PR head:5035fd6c0455330e3b15a07c04cb6eeb686e77a9.
The N32-specific sanitizer profile and its routing/result special cases were
removed. The original loop already consumes all16 catalog tactics, including
all8N32 tactics. Relative to the downstream base, the sanitizer file now only
changes `apply_topk_in_fc1` to `[False]`. This halves the ordinary matrix to
6cases (EP4/EP8 x three tools),36token/distribution workloads.

Only README and the sanitizer test changed after the GPU-testedf088518 commit;
production code and numerical tests are unchanged. Local collection reports
6cases, scoped pre-commit and diff checks pass. No devbox access or GPU rerun
was performed: the user reports that benchmarks are running there. Existing
6-case/48-log results remain explicitly tied to the earlierf088 N32 profile;
they are not a run of the revised ordinary matrix. See
`evidence/sanitizer-fc2-only-local-validation.json` and the updated PR body.
