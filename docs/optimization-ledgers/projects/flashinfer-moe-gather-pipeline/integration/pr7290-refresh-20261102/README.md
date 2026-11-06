# PR7290 current-head benchmark refresh

Requested on 2026-11-02: refresh both EP/TP speedup heatmaps and the four
existing benchmark-table comments on the latest PR head, checking for
regressions against the previous measured implementation.

- Candidate: `2b4732791a3ce48bc3ae6c030a283fab73854e0e`.
- Matched control: `a620ce7790b32f7f0ae524a811417d2c6cee1152`.
- Workloads: V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, N3U EP8/TP8;
  the same 36 supported model/dtype arms and 468 token cases as the prior
  publication. Tokens 1 and 2 stay in raw tables, excluded from heatmaps and
  retention summaries. Skip configurations without supported comparators.
- Timing: whole rank-local MoE pipeline, no communication; unfused candidate
  finalize; initial NVFP4 activation quantization included; strict CUPTI,
  CUDA graphs, cold L2, 10 warmups and 100 samples per process. Freeze existing
  choices and routes to isolate the rebase and activation-state cleanup.
- Prefer a full control/candidate/candidate/control campaign on each job's
  same GPU. Two candidate phases provide the refreshed publication values;
  matched controls diagnose regressions. Existing TRTLLM, non-swap and pre-PR
  W4A16 denominators remain historical and are not rerun.
- Cache keys may need rebinding to upstream's rank-invariant schema; preserve
  tactic choices and verify live cache hits. Keep native compilation artifacts
  in cluster persistent storage and separate source-specific CuTe caches.
- Do not modify production sources unless the measurements establish a
  regression needing a fix. Do not hide negative points or replace earlier
  diagnostic results with a better rerun.

Publication replaces the two existing external-comparison heatmaps and edits
table comments 6519314397, 6519315021, 6519315606 and 6519316131 in place. Table
text comes from the benchmark's table printer using fresh candidate data and
the original unchanged TRTLLM results, without parsing or rewriting ASCII
tables. Root owns public writes; runtime and publication agents prepare data.

Status: both the full CAAC campaign and separate serial ACCA diagnostic are complete, with source/native postflight checks passed. Main data/report: `fetched/1793691596500669000/`; diagnostic: `isolated-fetched/1793692299844142000/data`. Original matrix values are unchanged. See `RESULTS.md`, `RUNTIME.md`, and `publication/` for independent validation and publication artifacts.
