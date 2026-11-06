# Swap-AB synchronization audit

Scope: retained cb35 kernel and the independently qualified single-announcer
follow-up. The scatter4 store experiment is still isolated and does not change
these lifetime rules. This is a source/codegen audit, not a sanitizer result.

| Resource / handoff | Required ordering | Audit outcome |
|---|---|---|
| Pipeline initialization / TMEM allocation | Deferred barrier initialization must be visible before any role uses a ring; every role needs the allocated TMEM address. | Preserve the initialization fence and TMEM retrieval rendezvous. Two-CTA kernels additionally publish cluster barriers before use. Moving producer work before this join is unsafe without replacing its publication role. |
| Operand stage reuse | Each producer must wait until MMA releases the preceding use of that shared-memory slot. | Preserve separate empty-stage waits. Neither activation nor weight producer should wait for the other producer's issue loop. |
| Operand availability | MMA must see every weight, activation and scale byte from the whole CTA group. | Retain one weight-owned full-barrier announcement of the combined byte count. Activation only waits for reuse, then issues independently. The pending-arrival counter prevents early completion when TMA finishes before the announcement. |
| Operand completion / reuse | Both channel tiles must finish consuming B/SFB before either producer overwrites them. | Preserve the one shared MMA completion/release after both channel tiles. Separate resource rings would add control without changing this common last use. |
| Scale factors in TMEM | Scale copies must precede the MMA using those scales. | Existing ordered MMA-role issue sequence remains. No additional cross-warp scale-publication barrier is introduced. |
| Accumulator windows | Epilogue must wait for MMA completion; subsequent MMA must wait until the overlapping accumulator/scratch interval is released. | Preserve the accumulator ring and last-use TMEM fences. Early release remains at the existing ownership boundary, not at the end of all epilogue math. |
| SF32 adjacent-warp exchange | Partner values must be published before reading, and both reads must finish before reuse. | Both publication and reuse joins remain necessary. The isolated pair-only barrier experiment was neutral/slower and was rejected. |
| FC2 shared output stages | All stmatrix writers must publish before TMA stores; every issuer must finish reading a stage before writers reuse it. | Preserve async-proxy fence, publication join, per-thread read waits and the following warpgroup join. Multiple issue lanes/warps do not share one thread's bulk-group completion state. |
| FC2 final output-stage use | Outstanding bulk reads must finish before scratch reuse by a later work tile or kernel exit. | Preserve final read drain and warpgroup join. Deferred-drain alternatives already failed retention. |
| CLC response | Cancellation result must finish before scheduler reads; response readers must finish before the next request reuses storage. | Preserve the separate response ring and its tail. It has a different lifetime from published work metadata. |
| CLC work metadata | Every consuming role must acquire published tile fields and finish reading before scheduler overwrites them. | Preserve the metadata ring. Only the leader CTA's MMA warp consumes it; follower MMA work and quorum participation were already removed in cb35. |
| Ordinary scheduler | Static tile progression requires no cross-role publication. | Keep direct independent arithmetic/metadata reads; introducing a shared scheduler ring would add synchronization. |
| PDL | Payload consumers acquire their predecessor's publication; independent weight and scheduler work can run ahead. | Preserve delayed waits for independent roles and their final dependency completion. Disabled PDL emits no GDC waits/signals. No extra producer rendezvous is added. |
| Final CTA / peer teardown | All roles must finish using local metadata, barriers and TMEM; peer-CTA TMEM lifetime also requires its handshake. | Preserve final all-role join and allocator deallocation handshake. A consumer's early accumulator release does not establish completion of every later epilogue or asynchronous remote-barrier use. |

Evidence is linked from `STATUS.md`, `combined/GATE_RESULTS.md`,
`producers/next-audit/README.md`, `scheduler/sole-announcer-review/REVIEW.md`, and
the exact/codegen and matched CUPTI receipts beneath those directories.

The single-announcer screen measured -0.022% overall, +0.065% decode and
-0.109% prefill over64 matched cells. Its retention is an instruction/protocol
simplification, not a speedup claim. One stable V3 MXFP4x8 T4096 cost of1.057%
is recorded explicitly. No model/dtype exception or additional tuning axis is
introduced to hide that result.

Other apparently redundant source constructs were checked against generated
code: absmax already uses native FMNMX3, and SFB copy elections are already
merged. Rewriting them would not remove executed instructions. The previously
rejected per-token single-transpose design would also delay today's earlier
accumulator release until after activation; it was not repeated.

Sanitizer remains skipped at the user's request. Independent storage-bit checks
and codegen inspection qualify the tested configurations, not all possible
future parameter combinations.
