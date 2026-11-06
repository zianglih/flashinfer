# R4 scale-completion relay audit

Reviewed frozen kernel SHA256 `6fae1558326e72aa8beab25520c9e7be1734e03b6ff39d190025f2445d09ed2a`, base `d35fcfda03875077b3af8455575cc1d20e866a8c`. No production source edits were made by this audit.

- Each of the 128 scale-copy issuing threads contributes exactly one `cp_async_mbarrier_arrive_noinc` per stage to its CTA-local barrier, initialized to128. The asynchronous arrival tracks that thread's prior scale copies. Producers no longer block on `wait_group0` before issuing the next stage.
- Warp1 waits for the local completed phase, performs the async-shared fence, then one elected thread publishes to the MMA leader. Two-CTA publication explicitly uses cluster scope. The leader-ready barrier count is the CTA group size, so it receives one completed-CTA publication from each CTA.
- The existing operand-empty handoff protects both the scale storage and local completion phases. A producer cannot reuse a stage before MMA consumes it; MMA cannot consume before the relay publishes readiness. Therefore a subsequent local phase cannot overtake the relay's old-phase observation. No independent empty ring is needed.
- The relay follows the same static/CLC tile and K-stage sequence as the producers. Adding its32 metadata consumers gives352 on the leader and320 on the peer. FC2 stays on the existing regular-TMA branch.
- The existing weight-producer tail and final full-block rendezvous retain the shared-storage lifetime. A gather thread may reach exit before its last asynchronous arrival completes, but the dependent MMA and shared tail cannot finish until relay completion has made that stage available.

The source-level lifetime chain has no identified blocker. This is not a formal proof of every interleaving. The subsequent selected runtime gate passed12/12: ten bit-exact tests and two existing MXFP8 ReLU2 tolerance/cosine tests, six cases with actual compiled CLC in both GEMMs, PDL on/off, and one/two-CTA tactics. See [BROADER_QUALIFICATION.md](BROADER_QUALIFICATION.md).

The same artifact plan/plugin/runner bytes were reused from R3; the plan's documentary `revision: r3` labels that unchanged fixture recipe. Execution was bound to R4 `runtime.json` and `source.json`, verifying all513 files and the full R4 patch before/after each case. No R3 source or executable was reused as the candidate.

R3's separate [codegen report](../r3/cache-codegen/CODEGEN_REPORT.md) shows the removed wait/fence/per-thread-arrival sequence and no local-memory spills. Its CUPTI samples are diagnostic only. R4 performance measurement remains owned by the parent task.
