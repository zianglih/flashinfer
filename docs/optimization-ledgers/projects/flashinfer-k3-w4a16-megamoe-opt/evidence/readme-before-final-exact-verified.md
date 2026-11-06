# K3 W4A16 MegaMoE optimization

Optimize Kimi K3-shaped W4A16 MegaMoE and maintain draft
[FlashInfer PR #6277](https://github.com/flashinfer-ai/flashinfer/pull/6277), with
matched DeepSeek V4.1 Flash and GLM5 model-shape checks. Benchmarks use synthetic
NVFP4 routed-expert weights and inputs; these are layer timings, not checkpoint
accuracy or end-to-end serving measurements.

## Current scope and open catalog decision

- Native FP32 SiTU tanh and packed pair multiplies, with the corresponding Mega
  instruction reference and existing zero-tolerance comparisons.
- M128/N32 and M256/N32 FC1/FC2 epilogues, preserving existing N64/N128 paths.
- Currently published default catalog: `((128,32,256), (256,32,256), (256,64,256),
  (256,128,256))`, in that order; group hints512/1024 × epi/dispatch return =
  16 no-reduce tactics. M128 is admitted only at N32. **Retention of the
  M128/N32 default tactics is open:** a new DSV AUTO12 sweep will omit M128
  from the candidate list and compare with saved AUTO24 and BEFORE. Manual
  M128 geometry admission and existing exact cases are unchanged by this probe.
- K3, DeepSeek V4.1 Flash and GLM5 benchmark presets; original DeepSeek V3
  remains the default.
- The user removed the scheduler optimization from the final scope. Local
  scheduler bytes now exactly match original baseline
  `a7103ae2a97f38f4dbbf410c32acc7c6fe99cab1`. Scheduler-only tests and their
  scaffolding are removed; all eight N32 logical cases and the reference remain.
- Keep the established two decoder warp groups, eight decoder warps, 640 CTA
  threads, register partition, weight layout, PDL and deterministic combine.

The reduced scope is committed and pushed as `48fce528a70b7bc10c26307dfd2155491d50cfe9`;
the local checkout is clean. Focused pre-commit and commit hooks passed. Do not
claim the old `ce03` exact qualification proves the final assembled source.
The eventual12-versus16 catalog decision, source-map receipt and new GPU
exact qualification remain pending.

## Chosen performance evidence

- **K3 final:** `runs/k3-scheduler-off-auto-v1`, reusing `runs/full-base-v2` as
  BEFORE. AUTO24 speedup is **1.01623× overall**, **1.01897× decode**, and
  **1.00897× prefill** across the eleven retention points.
- **DeepSeek V4.1 Flash final:** `runs/dsv41-flash-scheduler-off-auto-v1`, with
  its own `runs/dsv41-flash-before-v1`. AUTO24 speedup is **1.01777× overall**,
  **1.02346× decode**, and **1.00274× prefill**.
- **GLM5 measured AUTO16:** completed `runs/glm5-final-auto-v1` versus its own
  `runs/glm5-before-v1`: **1.01967× overall**, **1.02348× decode**, and
  **1.00961× prefill**. The strict combined report is
  `evidence/cross-model-scheduler-off-v1.{json,md}`. Default-catalog retention
  remains open while the DSV AUTO12 comparison proceeds.

All K3/DSV final AUTO24 winners belong to final16. Their changed final16 search
order was not independently timed; do not label those captures as AUTO16. The
complete authoritative comparison is
[`evidence/scheduler-auto-complete-v1.json`](evidence/scheduler-auto-complete-v1.json).
It remains local study evidence; the clean public body shows only BEFORE/native/
final K3 and model-specific BEFORE/final DSV/GLM, with every final selected tactic.

Protocol: EP8 on eight B300 GPUs; one fresh process group per arm; 3 warmups,
100 untrimmed cold-L2 CUDA-graph CUPTI samples per point. Report median
per-iteration rank-MAX GPU activity span. Routing preparation, tuning, capture
and L2 flushing are untimed. Routing weights are applied in deterministic
combine (`apply_topk_in_fc1=False`). PDL is enabled; fused TMA/FC2 reduction is
disabled. Preserve all13 global token counts:
`1,2,4,8,16,32,64,128,256,512,4096,8192,16384`; only1/2 are excluded from aggregates.

Each new model BEFORE uses original a7103 kernel sources plus its matching
benchmark overlay. K3 reuses its earlier BEFORE/native captures; its later final
capture uses the DSV-extended driver, with normalized seeded-fixture equality
checked by the strict report. No samples or model timings are pooled.

## Qualification deferred until the catalog decision

The cleaned multirank test file is SHA256
`4caa18263e861454f384da31d17deb5f39f961c748838a618671223a826d25a0`;
reference SHA256 is
`a1ad0fd730f91498261c75a8f7d25af8980cd12f7285a5bc1c0a7a2cd5d39684`.
Focused pre-commit and commit hooks passed after formatting; the removal audit
is `evidence/scheduler-retention-decision-v4-remove.json`. Complete static output
and receipt are `evidence/focused-precommit-scheduler-removal.{json,log}`;
focused source review is `evidence/self-review-scheduler-removal.md`. The final
GPU exact gate has **not** passed yet, and the full repository suite was not run.

`next-glm5-final-auto-v3` completed successfully at2026-10-09T09:12:36Z using
original-scheduler AUTO16 and cleaned test4caa. The DSV AUTO12 diagnostic changes
only the candidate list in `autotune.py` and reuses saved DSV AUTO24 and BEFORE
rather than rerunning those arms. It started at09:12:52UTC; queue
`queues/dsv-m256-auto12-v1`, capture `runs/dsv41-flash-m256-auto12-v1`.
Sealed bundle `next-dsv-m256-auto12-v1` manifest
`f900532ae1e8eb32904434944ddc1a8d1d60f5a3d17236b8f8bf859f6326a2ba`.

The exact v3 follower was dispatched earlier, then cancelled at
`2026-10-09T08:59:59.599993Z` **before test start**, with source unchanged:
`correctness/scheduler-revert-n32-exact-v3/cancelled-before-start.json`.
Its prior intended scope was eight existing logical N32 EP2 cases (`-k n32`,
port29683). There is no final GPU qualification from that cancelled run. A new
exact gate waits for the eventual catalog decision. Prepared unsealed bundle:
`next-final-catalog-n32-exact-v1`, explicit `--catalog 12|16` choice; no
qualification run or restoration is implied before it is sealed/dispatched.

Historical sealed manifest hashes remain GLM
`9bb9b46e80b734e13320efaea4391dc936beafffad909527d097c8c27919c0be`
and cancelled exact
`e4ebcb7b1043462772360c7846426b0108ca5e18a0e987577abacc427eb623f8`.
The owner handles scheduling, final review and publication.

Historical native qualification passed13 logical cases/40 rank-local checks.
Earlier combined/M128 gates remain in the ledger and receipts; they do not
replace this final assembled-source qualification. Measure performance first;
use the existing exact oracle without tolerance changes. No further IKET or
decoder warp-group redesign is authorized.

## Drafts, artifacts and environment

- Published clean body: [`PR_BODY_INTERIM_CLEAN_48FCE_GLM.md`](PR_BODY_INTERIM_CLEAN_48FCE_GLM.md).
  Live body/head/draft equality verified in `evidence/pr6277-published-clean-glm-table.json`.
- Renderer: [`runner/PR_CROSS_MODEL_RENDERER.md`](runner/PR_CROSS_MODEL_RENDERER.md).
- Pending final source/test review: `evidence/pr-final-source-review-pending.json`.
- Public source reproduction audit: [`evidence/PUBLIC_SOURCE_REPRODUCTION.md`](evidence/PUBLIC_SOURCE_REPRODUCTION.md);
  reconstructs the measured AUTO24 catalog from public48fce with exact hashes
  without implying a final12-versus16 retention decision.
- Full studies and rejected candidates: [`OPTIMIZATION_LEDGER.md`](OPTIMIZATION_LEDGER.md),
  `PERFORMANCE_PROGRESS.md`, `runs/`, `correctness/` and `evidence/`.
  The previous README chronology is preserved in
  `evidence/readme-before-final-clean-scope.md`.
- Public raw export must use the chosen renderer receipt. Only K3 BEFORE/native/
  final, DSV BEFORE/final and completed GLM BEFORE/final belong in the clean PR.
  The full local archive includes other studies and must not be uploaded.

Retain both devboxes and serialize C2 GPU work. Current C2 devbox is
`k3-w4a16-opt-c2`, namespace `ziangli`, node `hu-pdx-120`; remote workspace is
`/data/home/ziangli/flashinfer-k3-w4a16-megamoe-opt`. Image:
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.1, CuTe DSL4.7.1.
The previous `nvfp4-blog-kimi-k3-ep8` disappeared; this task did not delete it.

Persistent cache folders remain available, but direct `cute.compile` bypasses
CuTe's file cache. See
[`evidence/dsv-t32-compiled-artifact-audit.md`](evidence/dsv-t32-compiled-artifact-audit.md).
No cache integration or environment change is part of this PR.

The prior blog workspace and sealed captures remain untouched. Its pin
`b730d5f6f5929fe666b24b466144a57f5587ba4b` has the same relevant kernel and
benchmark source as the a7103 baseline. PR #4540 and #5019 context is archived
under `evidence/pr4540.*` and `evidence/pr5019.json`.
