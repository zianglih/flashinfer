# Minimal MegaMoE external-finalize PDL patch

Baseline: HashInfer `68eb1fefb84701131213e423f2c20cf953bb5918`.
Source patch: `pdl-source.patch`. Reproducible static check: `python3 audit_source.py`.

- The producer retains its ordinary, non-PDL launch. Therefore it cannot begin reading staged inputs before the preceding staging kernel completes. The reducer's routing scores are also ready before the producer starts and can be prefetched independently.
- For external finalize only, warp 0 elects one lane in every producer CTA to issue `cute.arch.griddepcontrol_launch_dependents()`. The trigger precedes the CTA-leader calculation; both members of a two-CTA cluster signal. IKR compiles this branch away.
- `TopkReduce(enable_pdl=False)` keeps existing shared callers unchanged. Only the W4A16 external-finalize caller opts in. Opt-in explicitly rejects non-BF16 combine formats because their readers were not changed.
- The BF16 consumer has PDL launch permission. Its existing metadata, pointer setup, accumulator allocation, and routing-score prefetch precede `cute.arch.griddepcontrol_wait()`. Every dependent combine read remains after that wait.
- The wait remains inside the original valid-worker guard. PTX defines the wait for the executing thread, not as a CTA collective. Inactive tail lanes access neither combine data nor output and need no wait. No additional barrier, predication, or geometry change is required.
- The wait requires full producer completion and memory visibility. Existing producer CTA rendezvous, NVLink drain, counter reset, and publication are untouched. Local FC2 completion alone is not used as a readiness signal; peer output returns remain protected by the existing cross-rank protocol.
- No GEMM math, reduction arithmetic/order, resource setting, tactic, or transport barrier changes. The expected opportunity is prologue/launch overlap; actual concurrent execution and performance are unproven until GPU validation. The full-SM persistent producer's register allocation can limit consumer residency.

PTX primary reference: [griddepcontrol semantics](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-griddepcontrol).
CUDA primary reference: [Programmatic Dependent Launch and Synchronization](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html).

Static evidence: all three source files recover the baseline AST after removing exactly the new synchronization additions; eight actual constructor-body cases cover both boolean values for all four existing combine formats. Scoped pre-commit hooks passed. The repository's existing hook exclusion applies to the shared drop, which is covered here by syntax/AST checks. This receipt does not claim GPU correctness, generated-PTX ordering, or performance validation.
