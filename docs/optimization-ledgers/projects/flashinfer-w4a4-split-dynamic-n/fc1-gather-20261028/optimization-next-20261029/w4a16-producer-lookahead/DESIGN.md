# W4 Gather4 empty-barrier lookahead

Source base6c6515f2; new independent unstaged flashinfer-w4a16-producer-lookahead-review. Only FC1 Gather4 producers change. The preceding retained loop-order improvement, four issuers/arrivals, register budgets, shared layout/capacity, CLC/static scheduling, PDL, weight decode, metadata and FC2 remain fixed.

Evidence: sampled K3EP4K/8K traces identified activation delivery/issue as the increased MMA wait, while decoded-weight timing did not increase. Retained Gather4 issues16/24 operations per warp/stage. The long batch provides independent work over which the next empty-barrier readiness check may be overlapped. A performance gain is not assumed.

References inspected:

- Rubin block_scaled_swap_ab_fc12_mainloop.py:732–750 saves current barrier/stage, advances state and probes next empty state before issuing TMA copies.
- CUTLASS sm100_mma_warpspecialized_mixed_input.hpp load_B:849–870 follows the same order.
- W4's existing weight producer already passes a try-acquire token (moe_w4a16_kernel.py:1880–1927), although its probe is after the current copies. Existing transform/MMA protocols remain untouched.
- Installed CuTeDSL4.8 PipelineTmaUmma source was inspected live: producer_try_acquire only calls empty.try_wait(index,phase); producer_acquire waits when the token is absent/false, then still performs the same leader arrive-and-expect-tx. The expected_tx override is preserved.

Dependency proof: acquire locks the current slot before any writes. Its stage index and full-barrier pointer are saved before advancing private producer state. Every Gather4 destination and completion uses those saved current-slot values. Advancing the private cursor issues no shared synchronization. The probe is nonblocking, does not acquire/reserve a slot or publish data, and cannot authorize use of the next slot until its existing empty condition succeeds; false tokens still enter the normal acquire wait. The next iteration performs the same four issuer arrival contributions and per-issuer transaction bytes. A slot cannot be recycled past a participating issuer's pending payload/arrival. No wait, arrival, byte expectation or final all-slot drain is deleted. The last K iteration skips the unused lookahead. Cursor index/phase at the next work tile and terminal drain are identical to retained source; only the point of private advance within an iteration changes.

Resource proof: no shared/TMEM/barrier allocation or launch quota changes. Added live values are one readiness Boolean and saved current-stage index/barrier pointer. Actual N16/N128/N192 SASS/local-storage gates are required because uniform-register allocation can still change despite adequate general-register headroom. Metadata loads/divides and issue count are unchanged. No new tuning axis, problem-specific policy or warp ownership exception.

This does not repeat the rejected speculative MMA-ready probe: the changed role is the independent Gather4 producer and the overlapping work is the current payload issue batch. It does not change the rejected single-arrival protocol, cp.async transport, register quotas or live-row pruning. If added branch/state work does not yield useful bounded performance, reject without a broad sweep.

GPU3 only, source-bound codegen first; existing33 exact cases then same-policy four-cell CAAC if codegen has no spill/resource regression. No sanitizer, clock locking or native autotuning. Immutable6c control is the measured w4a16-linear-issue-simple source, verified against canonical514-file manifest; actual remoteGit1b0 and logical6c are distinct.
