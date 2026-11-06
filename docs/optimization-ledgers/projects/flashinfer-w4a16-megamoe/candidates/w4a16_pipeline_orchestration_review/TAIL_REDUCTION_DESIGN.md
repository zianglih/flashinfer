# Exact reducer tail: secondary source note

This remains an unimplemented secondary direction after N256. Source inspected
at published a26dc8b88 plus the local N256 geometry experiment. The relevant
transport/reducer bytes are identical to cleanup eb9cc. No timing is inferred.

The universal `TokenInPullTokenBackPush.kernel_tail` first rendezvous all640
threads, then only dispatch warps8..11 execute the cross-rank drains, shared
counter reset/publication and final local reset. Two possible final mappings:

- Reuse only those128 dispatch threads after `kernel_tail`: no new CTA barrier,
  but only4warps/SM participate while the persistent CTA still owns its large
  shared-memory allocation. This can underutilize reduction bandwidth.
- Have all640 threads rendezvous again after `kernel_tail`, then run a simple
  grid-stride reduction over actual local output rows. This gives20warps/SM and
  requires one CTA barrier; it preserves the existing global drain/reset protocol.
  All role branches currently fall through to the tail, so no new role state,
  shared signal or cross-rank barrier is implied by this mapping. This still needs
  native proof and tests before any device implementation can be admitted.

The existing BF16 TopkReduce assigns8hidden values/thread, prefetches scores for
K<=16, uses one FP32x2 multiply for k0 followed by ordered FP32x2 FMA for k1..K-1,
then casts once to BF16. On SM100/103 these are existing public CuTe packed-math
primitives. A future owned tail should preserve those exact operations and the
BF16 combine buffer, without inheriting a W4A4 compute pipeline or changing vendor
code. The grid-stride bound must use actual output rows, not allocated capacity;
empty local ranks still participate in the entire communication tail.

At H7168/top8/512localtokens the existing reducer reads approximately58.7MB of
BF16 terms perGPU. Fusion removes its separate launch, but does not eliminate
those reads, ordered math or visibility requirements. It also needs the final
output pointer and row count in the Mega callable and frontend shape/stride contract;
all eager/graph/empty-source contracts must remain intact. The change may cost
more complexity, instruction/cache footprint and resident-kernel time than the
saved launch. Earlier instrumented NSYS reducer duration is not current CUPTI
benefit evidence. Do not start this direction merely to claim more optimizations.
