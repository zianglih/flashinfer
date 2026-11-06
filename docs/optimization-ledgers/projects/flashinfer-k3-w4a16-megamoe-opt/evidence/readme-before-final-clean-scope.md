# K3 W4A16 MegaMoE optimization

Optimize the Kimi K3-shaped NVFP4 routed latent MoE core on the retained C2
eight-B300 devbox and maintain the draft upstream FlashInfer PR. The benchmark
uses synthetic NVFP4 weights and inputs; outer latent projections are excluded.

- Source baseline: upstream `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`.
- Workload: EP8, D=3584, E=3072, N=896, K=16, SiTU(4,25).
- Controls: PDL enabled; fused TMA/FC2 reduction disabled; W4A16 Mega's
  deterministic fused combine enabled. Precomputed, identical routes.
- Timing: native distributed benchmark, cold-L2 CUDA graphs, CUPTI,
  3 warmups and 100 samples per point. The completed AUTO comparison uses one
  baseline and one candidate process over all 13 token counts; subsequent
  candidate-only screens reuse the recorded native AUTO winners. The earlier
  four-point A/B/A screen is reported separately with actual process counts.
  Medians use untrimmed rank-MAX GPU activity spans. Preparation and tuning
  are untimed.
- Token counts: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384.
  Report every point; exclude only 1 and 2 from retention decisions.
- Iteration gate: measure performance first; correctness begins only after a
  speedup is confirmed. Exploratory measurements are not final PR evidence.
- Retain both existing C1 and C2 devboxes. Serialize all C2 GPU experiments.

The prior blog workspace and sealed captures remain untouched. Its source pin
was `b730d5f6f5929fe666b24b466144a57f5587ba4b`; the relevant W4A16 Mega kernel
and distributed benchmark have no upstream changes between that pin and this
baseline. New matched measurements still establish the comparison.

Remote root: `/data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt`.
Devbox: `k3-w4a16-opt-c2`, C2, namespace `ziangli`, node `hu-pdx-120`.
The former `nvfp4-blog-kimi-k3-ep8` disappeared on 2026-10-09; it was not
deleted by this task. The replacement uses the same node and persistent checkout.
Image: `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.1, CuTe DSL 4.7.1.

## Initial candidates

1. Compare Mega W4A16, Mega W4A4, and split W4A16 SiTU arithmetic, including
   the reciprocal-folding contract from PR #4540.
2. Compare actually selected K3 and GLM5 W4A4 tactics, then test compatible
   geometry/scheduling/return-mode extensions for the narrow W4A16 catalog.
3. Preserve rejected experiments and their measurements in `OPTIMIZATION_LEDGER.md`.

PR references are archived in `evidence/pr4540.json`, `evidence/pr4540.diff`,
and `evidence/pr5019.json`.

## Draft change and validation

Draft upstream PR: https://github.com/flashinfer-ai/flashinfer/pull/6277

Kernel/test qualification source: `ce03ada4a1e1cceff5f4f823d6e133799e9c1218`. The change combines
N32 FC1/FC2 epilogues, the residual-prefix scheduler, native SiTU tanh, K3/GLM5
benchmark presets, and the four-tile AUTO catalog requested by the user:
`((128,32,256), (256,32,256), (256,64,256), (256,128,256))`.
The catalog has 16 default tactics; the established two decoder warp groups
and register roles remain unchanged.

The completed 24-tactic exploration selected M128 only with N32 at
T1/T2/T4/T8. The final subset retains all thirteen measured winners. It has
not been benchmarked as a 16-tactic selector; the changed candidate order is
not claimed to reproduce identical tuning decisions. Measured expanded AUTO
is 1.02930x BEFORE over all eleven retention points. M128's selected T4 case
reduces latency by 5.792% relative to M256-only AUTO, while T8 is 0.856% slower.
Improvements at points still selecting M256 are not attributed to M128.

Focused exact gates passed separately: 13 earlier native cases (40 rank-local
passes), eight combined M256 cases (16 rank-local passes), and four new
M128/N32 cases (eight rank-local passes). The new gate used the final source,
existing bit-exact oracle and zero tolerance. All eleven changed files pass
focused pre-commit; the entire repository test suite was not run.

`PERFORMANCE_PROGRESS.md` preserves every incremental speedup column and adds
the selected final measured tactic. Full raw samples, source identities,
selection-only diagnostics and exact receipts are under `evidence/`, `runs/`
and `correctness/`. `OPTIMIZATION_LEDGER.md` preserves rejected candidates.
K3 BEFORE was reused throughout its optimization; no IKET was run.
The C2 devbox and persistent compilation caches remain available.


## DeepSeek V4.1 Flash and GLM5 follow-up

The user requested matched BEFORE/AUTO comparisons for both model shapes and
selected tactics beside every final-results column. Stage 1 launched on the
retained C2 devbox at 2026-10-09 07:02 UTC: DeepSeek BEFORE, its full M128/256 x
N32/64/128 scan, then GLM5 BEFORE. All use EP8, the same full thirteen token
counts, 100 CUPTI samples and 3 warmups, PDL, and fused deterministic combine
without fused TMA/FC2 reduction. Routing weights are applied in deterministic combine;
`--apply-topk-in-fc1` is omitted consistently with the K3 study.

Current PR head: `bacf4861523ff7a1c1b5ad1e9d7a73a19151564a`.
The new `deepseek-v41-flash` preset is D5120/E2304/N384/K6 with clamped SwiGLU
and precomputed sqrt-softplus top-k routing. Both models use synthetic weights
and inputs to isolate the routed layer. Dedicated NVFP4 checkpoints exist;
checkpoint conversion/format is not a concern of this tactic study.

Every BEFORE arm restores the original a7103ae kernel sources and receives
only the same benchmark overlay used by its candidate. DeepSeek's 24-tactic
selection results determine whether M128/N32 remains sufficient. GLM5 final
AUTO follows that review. Bundle: `next-cross-model-validation-v1/`; remote
queue: `queues/cross-model-validation-v1/`. All three stage-1 captures completed
successfully by 07:51 UTC, including GLM5 BEFORE.


The published body was simplified during this follow-up: fixed N32 and
M256-only columns and the M128-axis section are omitted, while the local
incremental tables remain complete. The completed scheduler ON/OFF DeepSeek table
is now published in `PR_BODY_DSV_ON_OFF_UPDATE.md`; verified receipt:
`evidence/pr6277-published-dsv-on-off-table.json`. The cross-model renderer uses
`PR_BODY_CROSS_MODEL_TEMPLATE.md` and adds the two completed model pairs.


Scheduler retention is now under an AUTO comparison on both K3 and V4.1 Flash.
The scheduler-off sweeps use `next-cross-model-scheduler-auto-v1/`; DeepSeek
started at 07:51 UTC after GLM5 BEFORE. Existing scheduler-on full24 scans are reused; the same
full24 catalog/order stays enabled. Fixed-tactic plans were superseded without
execution. Keep the scheduler optimization only if a clear benefit remains;
GLM5 final follows that decision. DeepSeek's completed scheduler-on scan chose
only final16 members (M128/N32 decode; M256/N128 prefill) and was roughly flat
against its original BEFORE overall.

DeepSeek OFF completed at08:15:35UTC; K3 OFF started at08:15:40UTC. DeepSeek
OFF is 1.017770x BEFORE across eleven retention points and 1.023465x for
decode. ON/OFF is 0.984286x overall, 0.978551x decode, and 0.999746x prefill
(below one favors OFF). All OFF winners remain in final16. Complete raw,
source, tactic and quartile checks are in
`evidence/scheduler-auto-dsv-complete-v1.{json,md}`.

The user explicitly decided to **remove the scheduler change** for a clean PR scope after the complete K3/DSV studies. Final K3 and DSV performance reuses the completed OFF AUTO24 captures; native SiTU and the tile/tactic extensions remain. The original scheduler will be restored locally by the owner and remotely by the GLM v3 bundle.

Historical bundles are preserved: v1 follower PID103343 was cancelled at08:39:07UTC before any GLM capture or source mutation (`queues/glm5-final-auto-v1/cancelled-before-start.json`); v2 was sealed ON locally but never synced or dispatched. Earlier ON retention notes are superseded.

Fresh `next-glm5-final-auto-v3` is unsealed and only accepts OFF:

```bash
python3 -B next-glm5-final-auto-v3/seal_scheduler_choice.py --scheduler off
python3 -B next-glm5-final-auto-v3/follow_on.py --check-only
```

After the owner syncs it, remote `follow_on.py` queues `queues/glm5-final-auto-v3`. The unused capture name remains `runs/glm5-final-auto-v1` for report compatibility. It reuses GLM BEFORE and preserves all13 AUTO16 / CUPTI100 / 3-warmup controls.

`next-scheduler-revert-n32-exact-v3` can then be sealed with `seal_after_off_choice.py`, synced, and queued using `run.py`. It gates successful GLM v3 and runs only the unchanged eight logical N32 EP2 exact cases under the shared lock, without replacing source, tests or reference. Both v3 bundles remain unsealed and undispatched. Potential scheduler-only test cleanup has not been applied to these manifests.
