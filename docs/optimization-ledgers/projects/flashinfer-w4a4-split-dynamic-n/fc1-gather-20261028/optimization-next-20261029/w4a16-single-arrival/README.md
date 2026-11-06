# W4A16 one-arrival gathered B pipeline

Active source: `flashinfer-w4a16-single-arrival-review`, unstaged. Control is the frozen W4A16 direct-TMA cleanup b3617fba; the experiment changes only stage arrival ownership, not rows, TMA instructions, payload layout, PDL, register budgets or cache hints.

- Keep four warp Gather4 issuers and their existing row/K partitioning.
- Warp0 of the gather WG waits for stage reuse and announces the full statically known B transaction count. The other three warps wait only for reuse, then issue independently.
- Reuse the existing B pipeline `tx_count`, already computed from one destination stage times MMA CTA-group size. No per-warp ceiling-division accounting and no new barrier.
- MMA readiness still requires every payload byte; UMMA release still protects all issuers from overwriting the stage. Multicast and2CTA shape checks remain in the exact gate.
- The PTX transaction count is signed, and phase completion requires both the pending arrival count and transaction count to be zero. One pending owner arrival prevents an early phase transition when another issuer completes before the owner announces the full transaction count. [PTX mbarrier semantics](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-mbarrier).

Pre-commit passed. Source manifest, full-index patch and frozen control snapshot are local. Existing exact cases must pass before the32-cell same-GPU C-A-A-C screen; no sanitizer. Performance decision remains open.
