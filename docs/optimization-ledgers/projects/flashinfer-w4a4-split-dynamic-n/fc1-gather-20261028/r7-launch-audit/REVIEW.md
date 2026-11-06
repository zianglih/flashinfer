# FC1 incoming-PDL launch diagnostic

The proposed one-line change is semantically valid:

```python
use_pdl=self.enable_pdl and not self.gather_input
```

Keep self.enable_pdl and all device waits/releases/triggers unchanged. CuTe lowers use_pdl to CUDA's programmatic-stream-serialization launch attribute. It governs this kernel's incoming dependency, not permission to signal successors. CUDA's example launches the primary normally and enables PDL only on its secondary. In captured graphs, FC1's incoming edge becomes ordinary completion-ordered while FC2 retains its programmatic incoming edge. FC1's existing wait is satisfied by its already completed predecessor. [CUDA PDL guide](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html)

This preserves FC1 startup routing publication and FC2 prewait weight/scheduler overlap. It removes overlap of heavy FC1 initialization with unfinished routing, by design. No payload path, tactic, public argument or device arithmetic changes. W4A16 uses a separate implementation; non-gather FC2 launch eligibility is unchanged.

Early residency is possible, but its scope matters. Provided-top-k routing signals early in block≤4 and eligible dynamic-block≤16 paths. Cluster routing up to8192 tokens and the final cooperative/offset paths signal after permutation writes. A severe large-prefill loss therefore cannot simply be attributed to FC1 starting while substantial routing work remains. Launch/cluster retirement overhead is still testable, but resource contention is not established solely by the384-thread/~220KB footprint. Concurrent PDL execution and scheduling benefit are not guaranteed.

Compare R7 with its same-source parent using identical frozen winners/GPU assignment. Disabling incoming FC1 PDL should preserve its outgoing signal. Existing exact checks cover correctness; a launch/graph trace, if already captured, can verify the intended edge. No new policy or test axis is justified before timing. This auditor made no source edit or GPU launch. receipt.json binds the frozen R6 and unchanged routing/host/SDK sources.
