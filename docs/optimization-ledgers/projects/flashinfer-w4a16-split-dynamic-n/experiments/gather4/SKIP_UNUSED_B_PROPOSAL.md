# V10: omit Gather4 rows outside actual MMA N

**Rejected experiment.** The 32 boundary cases and 8 forced-fallback cases passed exact comparison, but AUTO subsequently stalled at T512 tuning profile 8/10 after completing T16. Root observed no progress from 11:45:29 through 11:47:32 and stopped the experiment. The cause is unknown; the source-level accounting argument below does not establish general kernel liveness. No further GPU work is planned for v10.

Off-tree patch: `skip-unused-b-branch-hoist.patch`, applied after the cache48 and branch-hoist patches. Complete kernel: `skip-unused-b-proposal/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`. Production is unchanged.

## Exact bound

The existing dynamic MMA uses `valid = max(1, min(distance_to_boundary, allocated_N))`. Its instruction N is `align16(valid)` for two-CTA MMA and `align8(valid)` for one-CTA MMA. The existing nonleader B shift already moves parity1's source start to `runtime_N / 2`.

Consequently each CTA consumes B destination rows `[0, runtime_N / CTA_group)`. The candidate omits a four-row Gather4 group only when its destination start is at or above that bound. The bound is a multiple of8, so no Gather4 straddles it. Invalid routed rows **inside** the instruction extent retain their existing TMA zero-fill. Static-N paths and minimum allocated N8/N16 paths emit no skip/completion code.

No first-use zero-fill is needed for omitted rows: the current MMA never reads them. Every later tile reloads all rows in its own consumed extent, even if the ring-buffer slot previously served a smaller N. This differs from FlashMLA's all-invalid-data skip, where the skipped region can still be consumed and must first contain zeros.

## Completion accounting

For BF16 K tile256, the existing leader expectation is `allocated_N * 256 * 2` bytes. Retained transfers complete `runtime_N * 256 * 2` bytes per physical MMA pair. The leader supplies the difference:

```text
missing_bytes = (allocated_N - runtime_N) * K_tile * 2
```

One elected activation-loader lane on **each** physical MMA leader performs one local completion after producer acquire, guarded by `missing_bytes > 0`. Nonleaders do not do this, and the completion is not multicast. Preferred cluster4's two pair leaders each complete their own barrier; actual Gather4 multicast continues to supply their retained bytes normally. A pair with no locally owned active row group can still receive active rows from its peer pair through the unchanged multicast mask.

The helper uses the CUDA13.2 [documented local completion instruction](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-mbarrier-complete-tx):

```ptx
mbarrier.complete_tx.relaxed.cta.shared::cta.b64 [leader_barrier], missing_bytes;
```

The barrier remains local to the issuing leader; no peer-bit rewrite or `mapa` is needed. The expected byte count, arrival count, reader-release masks, stages and pipeline phases remain unchanged. Existing [CTA-group2 TMA semantics](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async-bulk-tensor) and the kernel's leader-bit handling continue to govern actual copy completion.

Example: allocated N192 and actual N128 retain65,536 bytes and software-complete32,768 bytes at each pair leader, totaling the original98,304-byte expectation. Uniform two-CTA loading removes32 of96 Gather4 instructions from each CTA's K256 stage. These are source/accounting counts, not timing results.

## Bounded implementation choice

The row groups remain statically enumerated because a runtime loop index would dynamically index the register-cache tensor, risking selection or local-memory overhead. A single consumed-row predicate guards each group before row-cache access and TMA issue. It is eliminated at compile time for minimum-N/static-N cases. No separate full-tile fast path is added in this first screen; unchanged full tiles can still pay guard cost, which timing must evaluate.

## Local validation

Python syntax, Ruff and incremental patch application pass. Host enumeration passed 2,327 geometry/valid-count cases, checking row coverage and completion-byte accounting under the proposed protocol. The GPU gate passed 32 boundary cases plus 8 forced-fallback cases. The subsequent AUTO stall rejects this experiment despite those bounded checks; see the status above.
