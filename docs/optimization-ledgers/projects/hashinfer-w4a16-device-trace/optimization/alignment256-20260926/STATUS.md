# Completed alignment/register experiment

**No candidate retained.** HashInfer PR13 remains open/draft at `cd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7`; local source is clean. No upstream sync. All experiment commits/worktrees and artifacts are preserved.

See [FINAL_DECISION.md](FINAL_DECISION.md) for the complete before/after tables, methodology, source identities, interpretation and qualification limits; [EXPERIMENTS.md](EXPERIMENTS.md) retains chronological details.

- LDG128 restore96 and late+restore96: completed six-pass comparison, no useful gain; both rejected.
- Refined256 payload/scalar-score, payload/participant96, and score-only candidates: completed fresh eight-pass comparison on hu-pdx-43. All 12 pooled candidate/shape speedups below 1. All 128 selected winner binaries have STACK0/LOCAL0 and no LDL/STL. All three rejected.
- Zero spills remains a hard retention gate. Full AUTO-catalog coverage, trace-enabled winner qualification, SM100a compile smoke and further detailed correctness were not run for rejected candidates. Do not call selected-winner coverage a full-catalog proof.
- The older wide/all96 campaign remains preserved after its unpromising A1/B1 screening. The interrupted first focused campaign is preserved separately; no samples were mixed across nodes. No old campaign should resume automatically.

## Resource retained for iteration

C2/infra `fi-w4a16-align256-r2-0926`, pod `devbox-fi-w4a16-align256-r2-0926-0`, node `hu-pdx-43`,8 B300. Image `nvcr.io/nvidia/pytorch:26.05-py3`, digest `sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`. The previous devbox disappeared; this task did not release it.

Final campaign `tail-variants-focused-r2-v1` finished 2026-09-26T06:59:58Z, wrapper exit 0; no active GPU work or continuation is queued. Keep this devbox.

Remote task `/workspace/hashinfer-alignment256-20260926`; Python `venv/bin/python`; results `/data/ziangli/hashinfer-w4a16-device-trace/alignment256-20260926`. Raw compiler/cache artifacts remain durable. Local completed evidence is `tail-variants-focused-r2-progress-v1/`, with immutable final archive and audit.
