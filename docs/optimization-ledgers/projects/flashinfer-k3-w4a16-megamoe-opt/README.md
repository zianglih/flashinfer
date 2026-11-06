# K3 W4A16 MegaMoE optimization

Optimize Kimi K3-shaped W4A16 MegaMoE and maintain draft
[FlashInfer PR #6277](https://github.com/flashinfer-ai/flashinfer/pull/6277), with
matched DeepSeek V4.1 Flash and GLM5 model-shape checks. Benchmarks use synthetic
NVFP4 routed-expert weights and inputs; these are layer timings, not checkpoint
accuracy or end-to-end serving measurements.

## Current scope after restoring original activation numerics

- Restore original `_swiglu_act` and `_tanh` exactly from baseline
  `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`, plus the byte-identical original
  `w4a16_reference.py`. The native-tanh change is removed. Existing exact tests
  and their zero-tolerance comparisons remain.
- M128/N32 and M256/N32 FC1/FC2 epilogues, preserving existing N64/N128 paths.
- Currently published default catalog: `((128,32,256), (256,32,256), (256,64,256),
  (256,128,256))`, in that order; group hints512/1024 × epi/dispatch return =
  16 no-reduce tactics. M128 is admitted only at N32. The complete model
  comparison retained this catalog; decision and intermediate studies remain
  archived in `evidence/m128-catalog-retention-decision-v1.json`.
- K3, DeepSeek V4.1 Flash and GLM5 benchmark presets; original DeepSeek V3
  remains the default.
- The user removed the scheduler optimization from the final scope. Local
  scheduler bytes now exactly match original baseline
  `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`. Scheduler-only tests and their
  scaffolding are removed; all eight N32 logical cases remain. The original
  activation reference is restored as described above.
- Keep the established two decoder warp groups, eight decoder warps, 640 CTA
  threads, register partition, weight layout, PDL and deterministic combine.

The activation/reference revert is committed and pushed as
`866c80d0c70a90624b4c2056d12d1543d709609e`. Only these two source files changed;
N32 geometry, the 16-tactic catalog, model benchmark presets and tests remain.
Focused pre-commit (mypy/Ruff included), commit hooks, Python syntax compilation
and `git diff --check` passed. Baseline source/reference equality is verified in
`evidence/tanh-revert-static-checks.json`; complete focused output is
`evidence/tanh-revert-precommit.log`.

The immediate activation revert was local-only at the user's request. Later,
the user authorized the N32 study after the shared K3 campaign completed.
That study and the current qualification use independent project-local remote
checkouts; the original campaign checkout remains untouched. The historical
[DEVBOX_HANDOFF.md](DEVBOX_HANDOFF.md) records the earlier state. Current results
and commands are in [N32_GLM5_OPTIMIZATION.md](N32_GLM5_OPTIMIZATION.md).

**Current qualification:** final upstream source866c and downstream sourcef088518
both pass17 logical exact cases /52 rank-local passes with zero skips. Draft
HashInfer PR #14 [private repository link omitted] syncs the retained
upstream head with standalone adapters. Four additional GLM5 epilogue candidates
were measured and rejected as small/mixed improvements; no candidate code was
retained. The six-case N32 sanitizer matrix passed with 48 clean rank logs and zero
skips, using `next-n32-qualification-v2`; complete artifacts are in
`correctness/n32-retained-sanitizer-v2`. The complete110-file source map and
runtime are unchanged. See [DEVBOX_HANDOFF_N32.md](DEVBOX_HANDOFF_N32.md).
Keep the C2 devbox allocated. Do not merge either PR or update HAI gitlinks.

## Recorded performance evidence and applicability

- **Historical pre-revert K3 candidate:** `runs/k3-scheduler-off-auto-v1`, reusing `runs/full-base-v2` as
  BEFORE. AUTO24 speedup is **1.01623× overall**, **1.01897× decode**, and
  **1.00897× prefill** across the eleven retention points. This candidate used
  the now-reverted native SiTU implementation. These timings do not establish
  performance of 866c80d0; no current K3 speedup is claimed.
- **Retained DeepSeek V4.1 Flash SwiGLU measurements:** `runs/dsv41-flash-scheduler-off-auto-v1`, with
  its own `runs/dsv41-flash-before-v1`. AUTO24 speedup is **1.01777× overall**,
  **1.02346× decode**, and **1.00274× prefill**.
- **Retained GLM5 SwiGLU AUTO16 measurements:** completed `runs/glm5-final-auto-v1` versus its own
  `runs/glm5-before-v1`: **1.01967× overall**, **1.02348× decode**, and
  **1.00961× prefill**. The strict combined report is
  `evidence/cross-model-scheduler-off-v1.{json,md}`.

DSV/GLM exercise SwiGLU paths unchanged by this revert; their pre-revert
measurements remain applicable evidence for the retained geometry/tactics.
They are not new benchmarks or qualification of 866c80d0.

All historical K3/DSV AUTO24 winners belong to the retained16. Their changed final16 search
order was not independently timed; do not label those captures as AUTO16. The
complete authoritative comparison is
[`evidence/scheduler-auto-complete-v1.json`](evidence/scheduler-auto-complete-v1.json).
It remains local study evidence. The public body labels K3 candidate/native
results as historical and preserves DSV/GLM measurements with every selected tactic.

Protocol: EP8 on eight B300 GPUs; one fresh process group per arm; 3 warmups,
100 untrimmed cold-L2 CUDA-graph CUPTI samples per point. Report median
per-iteration rank-MAX GPU activity span. Routing preparation, tuning, capture
and L2 flushing are untimed. Routing weights are applied in deterministic
combine (`apply_topk_in_fc1=False`). PDL is enabled; fused TMA/FC2 reduction is
disabled. Preserve all13 global token counts:
`1,2,4,8,16,32,64,128,256,512,4096,8192,16384`; only1/2 are excluded from aggregates.

Each new model BEFORE uses original a7103 kernel sources plus its matching
benchmark overlay. K3 reuses its earlier BEFORE/native captures; its later historical
candidate capture uses the DSV-extended driver, with normalized seeded-fixture equality
checked by the strict report. No samples or model timings are pooled.

## Historical qualification before the activation/reference revert

The following gates precede the revert and do not qualify 866c80d0. The later
current-source exact gates are reported above and in the N32 optimization ledger.

`correctness/final-catalog-n32-exact-v1` completed successfully at
2026-10-09T09:32:51.012404Z. Both EP2 JUnit files contain all eight expected
N32 cases: **16 rank-local passes, zero failures/errors/skips**. That historical
gate used the native-tanh reference, which the subsequent revert replaces. Explicit M128/M256 N32 tactics cover
static/atomic scheduling, SwiGLU/SiTU, both token-return modes, scale handling,
feature/token tails, empty/refill routing and eager/graph execution.

```text
8 passed, 14 deselected, 705 warnings in 101.64s (0:01:41)
8 passed, 14 deselected, 705 warnings in 101.65s (0:01:41)
```

Verification receipt: [`evidence/final-catalog-n32-exact-verified-v1.json`](evidence/final-catalog-n32-exact-verified-v1.json),
SHA256 `74d9f15eeea48682e419f2a019bc21e7ec44399235aabceab972aaa61d5212da`.
The tested and post-test source maps match all 4,018 kernel/benchmark files in
`git archive 48fce528a70b7bc10c26307dfd2155491d50cfe9`; the pre/post-test maps
match all 102 tests. Source-map SHA256
`08a38be0895384766a084b06b9aa1104be1c834313a6f67d66b05fa7a596329b`;
test-map SHA256
`89c1f1c92630f9d8acfabfa7d98decc81a15d9e670948e7bb7b8ccdcffd47507`.
Historical test file SHA256 was
`4caa18263e861454f384da31d17deb5f39f961c748838a618671223a826d25a0`;
historical native reference SHA256 was
`a1ad0fd730f91498261c75a8f7d25af8980cd12f7285a5bc1c0a7a2cd5d39684`.

Historical 48fce focused pre-commit and commit hooks passed; output and receipt
are `evidence/focused-precommit-scheduler-removal.{json,log}`. The repository suite
and all-files pre-commit were not run. Historical native qualification passed
13 logical cases / 40 rank-local checks and predates N32 integration. These
bounded kernel checks do not establish full-model accuracy or AUTO selection.
No tolerance changes, further IKET or decoder warp-group redesign.

Earlier cancelled exact/GLM followers and the catalog diagnostic remain in
`OPTIMIZATION_LEDGER.md` and their original receipts; none is used as a passing
gate. Both devboxes remain retained.

## Drafts, artifacts and environment

- Historical published body at 48fce: [`PR_BODY_FINAL_CLEAN_48FCE.md`](PR_BODY_FINAL_CLEAN_48FCE.md).
  Live body/head/draft equality verified in `evidence/pr6277-final-publication-receipt.json`.
- Renderer: [`runner/PR_CROSS_MODEL_RENDERER.md`](runner/PR_CROSS_MODEL_RENDERER.md).
- Current published draft PR body: [`PR_BODY_REVERT_TANH.md`](PR_BODY_REVERT_TANH.md).
  Published and verified at 866c80d0; receipt
  `evidence/pr6277-tanh-revert-publication-receipt.json`. The PR remains draft.
  Frozen 48fce body, validation and source-review artifacts remain historical.
- Historical 48fce final-body helper: `runner/render_final_clean_pr.py`. It verifies
  historical exact receipts, all 91 raw-result rows and all 9,100 public samples.
  It must not be used to claim qualification of the restored activation/reference.
- Public source reproduction audit: [`evidence/PUBLIC_SOURCE_REPRODUCTION.md`](evidence/PUBLIC_SOURCE_REPRODUCTION.md);
  reconstructs the measured AUTO24 catalog from public48fce with exact hashes.
- Full studies and rejected candidates: [`OPTIMIZATION_LEDGER.md`](OPTIMIZATION_LEDGER.md),
  `PERFORMANCE_PROGRESS.md`, `runs/`, `correctness/` and `evidence/`.
  The previous README chronology is preserved in
  `evidence/readme-before-final-clean-scope.md`.
- [Public raw samples](https://gist.github.com/zianglih/b0fab803ada6848668bf441c8c7a542c):
  seven arms, 91 points, 9,100 untrimmed samples. The verified pinned URL and
  SHA256 `c02661509a4d1b951ff87e7f65b84e873960e23ab9092089b280e59f91471e39`
  are recorded in `evidence/pr6277-public-benchmark-gist.json`. The full local
  archive contains other studies and private metadata and must not be uploaded.

## Completed N32 study and HashInfer sync

The user subsequently authorized N32 optimization with GLM5 EP8 as the primary
workload, followed by a HashInfer sync PR and clean N32 Compute Sanitizer runs.
See [N32_GLM5_OPTIMIZATION.md](N32_GLM5_OPTIMIZATION.md). The preceding blog K3
campaign completed before remote setup. Successful studies are
[v1-retry](next-n32-glm5-v1-retry/README.md) (fresh control, narrow FC1 and FC2)
and [v3](next-n32-glm5-v3/README.md) (full32 FC1 and adjacent-pair FC2).
The first v1 setup failure and all later complete captures remain archived.

The N32 study is complete: four isolated epilogue candidates were rejected
after full13-point native AUTO16 sweeps. The best additional candidate was
1.00921x across retention points, driven by T64 and mixed elsewhere. Upstream
PR6277 remains at `866c80d0c70a90624b4c2056d12d1543d709609e`. Complete cumulative
results are linked from the optimization ledger; no experimental path is retained.

HashInfer draft PR14 [private repository link omitted] is open at
`f088518a8b0f24018bfd49420457eb9f873fcfaa`. All110 committed files match the host
receipt (25passes), scoped pre-commit passes, and the82-file owned-source audit
is in `evidence/hashinfer-n32-final/`. Both exact gates passed17 logical
cases/52rank-local checks each, with zero skips. The six-case N32 sanitizer
matrix passed48 clean rank logs across all eight tactics and nine routing
rounds per rank. The existing tensor-checker exclusion remains documented.
Independent final audit: `evidence/n32-sanitizer-v2-independent-complete-v1.json`.

Qualification supervisor PID221166 ran upstream exact17logical/52rank cases,
HashInfer exact17/52, then six N32 EP8 sanitizer cases/48rank logs. Its output is
`correctness/n32-retained-sequence-v1` under the remote project root; dispatch
is recorded in `evidence/n32-qualification-dispatch.json`. It uses sealed exact-v3
and sequence-v2 bundles after fixing directory-symlink source identity handling;
the failed preflight started no GPU tests. Source manifests are archived in
`evidence/n32-final-source-v1/`. The isolated remote checkouts are
`flashinfer-n32-glm5/` and `hashinfer-n32-f088518a8b0f-source/`.
The initial sanitizer attempt stopped after one clean memcheck case because
CuTe emitted an untracked PTX file. All110 source files were unchanged. After
redirecting diagnostics outside the checkout, the complete matrix reran and
passed in `correctness/n32-retained-sanitizer-v2`, finishing at
2026-10-09T15:50:59Z. Final GPU receipts show no active compute processes.
Keep the devbox and caches allocated; use the current N32 handoff above.

## Historical C2 handoff after the tanh revert

The user explicitly requested keeping the devbox after this work for reruns in
other sessions. **Do not delete `k3-w4a16-opt-c2`.** It is on C2, namespace
`ziangli`, node `hu-pdx-120`, with eight B300 GPUs. Image:
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.1, CuTe DSL4.7.1.
Remote project root is `/data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt`;
source checkout is its `flashinfer/` child.

At the last verified remote snapshot (2026-10-09 09:38:47 UTC), Git HEAD was
original `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1` with overlays matching
48fce, including native tanh and its reference. AUTO16 was restored and the
historical focused exact run had completed. No benchmark/test supervisors or
GPU compute processes were present at that time. **This is not a fresh live
check. This task did not apply 866c80d0 to the devbox; other sessions may
have changed its state since that snapshot.** The current revert makes
no connection, source change, package/cache change or GPU launch there.
Future blog work must explicitly choose its intended source after separate
authorization; preserve the devbox and archived captures.

Persistent cache root:
`/data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt/compile-cache/c2-sm103/`.
Recorded subfolders are `flashinfer`, `cute-dsl`, `cuda-driver` and `triton`,
respectively used by `FLASHINFER_WORKSPACE_BASE`, `CUTE_DSL_CACHE_DIR`,
`CUDA_CACHE_PATH` and `TRITON_CACHE_DIR`. Direct `cute.compile` bypasses
CuTe's file cache despite these configured folders. See
[`evidence/dsv-t32-compiled-artifact-audit.md`](evidence/dsv-t32-compiled-artifact-audit.md).
No cache integration or environment change is part of this PR.

The previous `nvfp4-blog-kimi-k3-ep8` disappeared; this task did not delete it.
The prior blog workspace and sealed captures remain untouched. Its pin
`b730d5f6f5929fe666b24b466144a57f5587ba4b` has the same relevant kernel and
benchmark source as the a7103 baseline. PR #4540 and #5019 context is archived
under `evidence/pr4540.*` and `evidence/pr5019.json`.

The historical 48fce body was published and verified at 09:38:24 UTC. The
current published revert body supersedes its scope/qualification claims; this
task did not synchronize the remote checkout. [DEVBOX_HANDOFF.md](DEVBOX_HANDOFF.md) records the
divergence and the timestamp of the last historical live check.

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
