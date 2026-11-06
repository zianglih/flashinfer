# Qualified EP4 GLM-5 uniform4096 trace

Current source: `679828c1f757a3ecfcb55a5650b7690ab9f297e2`; source-plus-fixture SHA256 `2156bd7a52f8fae316a92c51e61592cb87f9b1acd9d43c190399640521ccb32c`.

HashInfer PR13 [private repository link omitted] is pushed and remains draft. The owned marker-only sync is published in [FlashInfer PR5019](https://github.com/flashinfer-ai/flashinfer/pull/5019) at `b1eab683`; protected transport changes and trace helpers remain excluded upstream. Neither PR is merged.

Fresh AUTO winner: **N128 / group512 / reuse_dispatch_warps**, 587.168008 µs maximum rank-median hot graph-event score. All 1,600 samples and all four numerical/native trace reports pass. Each rank checks 6,291,456 BF16 outputs with zero mismatches/nonfinite values. All four non-dispatch combine WGs are active; 336 actual combine ranges appear per recorded cluster. Keep the unmodified full grid; IKET filters recording only.

- [Accepted audit and all candidate results](audit-3/audit.md)
- Perfetto traces: [rank0](audit-3/rank0.pftrace), [rank1](audit-3/rank1.pftrace), [rank2](audit-3/rank2.pftrace), [rank3](audit-3/rank3.pftrace)
- [Rank2 interpretation and limits](PR-trace-snippet-v3.md)
- [Exact accepted launch script](run-c2-v3.sh); raw collection is `remote-v3`, backed by `/data/ziangli/hashinfer-w4a16-device-trace/trace4096-20260926-v3` on C2.
- [Published PR evidence](PR-body.md), [exact readback](published.json), [completion receipt](completion.json)
- [Independent evidence review](final-evidence-peer-review.json)

The earlier `remote` / `audit-1` capture failed native scanner binding. The `remote-v2` / `audit-2` retry failed runtime nesting. They are preserved and rejected, not used for current timing or trace claims. Final code removes only the unreliable per-token return pair and retains whole-call dispatch/return coverage. `README-initial-preset.md` preserves the initial 4ba shape handoff.

Default remains128global; use `--shape glm5-ep4-uniform4096` in both baseline and capture for4096global (1024/rank). All traces/helpers remain outside the PR. Keep C2/infra devbox `fi-w4a16-align256-r2-0926` on `hu-pdx-43`; GPU work is complete and the last checked compute-process list was empty.
