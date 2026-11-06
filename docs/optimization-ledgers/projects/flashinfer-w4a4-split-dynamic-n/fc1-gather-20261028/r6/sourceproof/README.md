# R6 local Gather4 completion

Frozen kernel: `deba8b639fba89e6f76381e8c6bf8bc323ccaf850b973c836f476f8144c4cc0a`. Patch: `473cf890685b737f245ff8fd37b2094bc3181cd5f88ac3e0a6a33135200688f8`. Built from immutable R4, not from R5. All scoped hooks pass; no GPU work was launched by the implementation agent.

R6 preserves R4's descriptor, four-warp task assignment, source coordinates, nominal payload coverage, shared layout and stage planner. Each Gather4 operation uses CTA group1 and completes into that issuing CTA's existing local completion barrier. This isolates the group2 payload transport/leader completion path while retaining TMA and its cache hint. Weight and weight-SF TMA retain their existing native CTA-group behavior.

The local barrier expects129 arrivals:128 asynchronous SF arrivals, plus exactly one ordinary arrive-and-expect-tx from gather thread0. The announced transaction count is `b_copy_rows * tile_k * activation_width / 8`, equal to the sum of all512-byte Gather4 commands in that CTA, including OOB zero-filled rows/K regions. The maximum checked per-stage count is65,536 bytes. The global operand TMA barrier announces only weights and SFA, with the existing CTA-group multiplier.

If another warp completes Gather4 before thread0 announces bytes, the local transaction count may be negative. The remaining announcement arrival prevents premature phase completion; the eventual expected-byte addition balances those completions. Likewise, SF arrivals cannot complete the phase while payload bytes remain pending. The source-extracted proof checks448 shuffled completion/announcement orders and the hardware transaction-counter bound. This is counter algebra, not a substitute for actual hardware qualification.

Warp1 waits for the combined local payload/SF phase, fences the async shared view, then publishes one release arrival per CTA to leader readiness. MMA still waits for global weight TMA and this readiness before S2T/MMA. Its existing operand-empty release protects all stage reuse. No extra barrier, queue, warp, tactic or API field was introduced. Metadata allocation and producer/consumer stage advances remain R4's.

The proof also checks40 transfer geometries,4,008 live-row states,3,348 payload intervals, exact cached coordinate selection,24 weights-only global byte formulas and retained FC2 kernel/weight-loader AST equivalence. Actual CuTe lowering, output exactness, resources and performance remain parent-run qualification boundaries. R5/R5b and R4 artifacts are preserved separately.
