# Gather relay shared-memory publication candidate

Candidate: `candidate-kernel.py`, built from exact R6, SHA256
`da060e963548bba403d4afac14e32143c0854b739c217e7028f8af3764890a9a`.
`source-proof.json` and `candidate.diff` record the complete change.

The producer keeps its local completion wait and bidirectional async proxy
fence, then publishes with a shared-only cluster release followed by relaxed
cluster arrival. The MMA consumer uses relaxed cluster wait followed by a
shared-cluster acquire fence. The elected relay publishes only completed local
shared payload/SF writes; global routing metadata uses the existing independent
pipeline. Both CTA counts use the same helpers and CTA0 barrier mapping.

The local wait acquires tracked cp.async and TMA completion. The retained proxy
fence bridges generic SF writes and async MMA reads. Release/acquire causality
is transitive, including previously acquired writes. Both publication endpoints
now explicitly cover the cluster; the old implicit wait scope was CTA. The
shared-only fences apply to the actual operand/SF objects, so no global-memory
publication is requested. Barrier counts, phases and reuse authority are
unchanged. A one-CTA cluster remains valid because launch explicitly supplies
`cluster=(self.cta_group_size, 1, 1)`.

Official [PTX fence documentation](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-membar)
contains both producer and consumer patterns and requires PTX 8.6 / SM90+.
[PTX release/acquire patterns](https://docs.nvidia.com/cuda/parallel-thread-execution/#release-and-acquire-patterns)
define transitive causality;
[mbarrier wait](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-mbarrier-test-wait-mbarrier-try-wait)
defines the default scope and async completion guarantees.
The [CUDA guide](https://docs.nvidia.com/cuda/cuda-programming-guide/03-advanced/advanced-kernel-programming.html#async-thread-and-async-proxy)
distinguishes nonbulk cp.async's generic proxy from TMA's async proxy.

This intentionally does not use `fence.mbarrier_init`: it only publishes barrier
initialization. It also does not substitute a unidirectional proxy release
without a matching proxy acquire. The existing bidirectional proxy fence stays.

Local AST parsing and exact reverse-substitution proof passed. Candidate has
not been compiled or GPU-validated by this agent. Next checks: emitted PTX/SASS,
1/2-CTA bit-exact coverage, then frozen-tactic CUPTI comparisons. In particular,
verify that the former cluster arrival's `MEMBAR.ALL.GPU` disappears and that
consumer ordering does not reintroduce equivalent broad publication costs.

CUTLASS precedent: local `references/cutlass` commit
`91843b71d90737e0a9b86f7d9df213cff5a3526f` has
[`fence_view_shared` and `arrive_relaxed_cluster`](https://github.com/NVIDIA/cutlass/blob/91843b71d90737e0a9b86f7d9df213cff5a3526f/include/cutlass/arch/barrier.h#L802),
with the same shared release and relaxed cluster arrival primitives.
Its [SM100 scheduler](https://github.com/NVIDIA/cutlass/blob/91843b71d90737e0a9b86f7d9df213cff5a3526f/include/cutlass/gemm/kernel/sm100_tile_scheduler.hpp#L625)
uses the shared fence after writing a CLC response. This is a primitive/source
precedent, not a claim that CUTLASS uses this exact gathered-relay protocol.

The saved R6 generated PTX declares `.version 9.4`, `.target sm_103a`, with an
NVVM header reporting CUDA compilation tools 13.4.59; this toolchain supports
these PTX8.6 instructions. Container/toolkit identity is separate from this
observed bundled compiler version.
