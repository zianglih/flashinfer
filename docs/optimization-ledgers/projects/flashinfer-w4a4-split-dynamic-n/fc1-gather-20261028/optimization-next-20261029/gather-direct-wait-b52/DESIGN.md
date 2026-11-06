# One-CTA gathered-input completion

Candidate: let the one-CTA MMA warp acquire its existing local gathered-input completion barrier, then issue the existing async/shared proxy fence before SFB S2T. Only two-CTA MMA needs an activation-warp relay to collect both CTAs' completed local memory. This follows the existing compile-time CTA-group topology; no public option, dtype/model rule, or tactic axis is added.

## Ordering and lifetime

The local barrier combines `1 + min(route_tile, 128)` arrivals with payload transaction bytes. One producer announces all Gather4 bytes; possible SF owners issue `cp.async.mbarrier.arrive.noinc` after their SF copies. A successful local acquire establishes completion of both sources. The consumer then crosses the proxy before SFB S2T and MMA. The proxy fence is relocated, not removed. [PTX cp.async completion](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-cp-async-mbarrier-arrive), [mbarrier wait](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-mbarrier-test-wait-mbarrier-try-wait), [proxy fences](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-membar).

Every gather stage is still acquired for reuse through the operand-empty barrier. MMA releases that stage only after both channel tiles' operations, including SFB S2T, so the producer cannot overwrite a stage before the new direct local wait. Local and former relay consumers start at phase0 and advance once per K stage, without resetting at tile boundaries. Zero-work CTAs do not issue stage operations. CLC keeps the same tile/K ordering; its metadata arrival count now excludes the inactive one-CTA relay warp. The activation warp still executes common PDL startup acquisition/publication before role dispatch. All final joins, operand tails and two-CTA TMEM lifetime synchronization remain.

The prototype deliberately preserves storage and initialization of the unused one-CTA relay barriers: all shared offsets, stage calculations and capacities remain exactly fixed for the first codegen comparison. If retained, remove the dead storage only with an explicit planner/storage proof. The second barrier and cluster publication remain unchanged for group2. W4A16 is untouched.

## References and previous attempts

- Current `moe_swap_ab_kernel.py`: local barrier initialization near2720; activation relay near3009; MMA gather wait near3221; gather completion near3509–3568; final join near3585. `next_work` releases metadata on every consuming warp. The old 11-warp group1 CLC count becomes10; group2 leader/peer and nongather counts stay fixed.
- Rubin `blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1449–1487,2341–2400,2720–2731` already selects direct local cp.async completion for one CTA and a relay for two. Its `custom_pipeline.py:62–215` combines AsyncLoad completion with UMMA empty release. This is relevant topology precedent, not identical mixed-payload code.
- `relay-scope-audit/README.md` explicitly preserved the relay and changed only local versus cluster publication scope. `optimization-20261029/relay-publication` changed the older broad GPU fence to shared publication. `gather-pipeline-audit-ce4/VERDICT.md` did not establish direct local completion. Targeted `.md`/`.patch` searches found no identical trial.

## Evidence limit and risk

The current d9 N3U EP16K trace is a **two-CTA** M512/N128/K4 winner, which this candidate leaves unchanged. Its relay wait median128ns and MMA gather-ready median32ns overlap other work and are not removable latency estimates. Earlier R6 relay traces predate retained publication-scope fixes. There is no current one-CTA trace demonstrating that the relay is critical.

Removing a wait/arrival handoff and an entire metadata-consuming warp loop reduces work, but moves the proxy fence onto the MMA path. That can expose latency previously hidden on the relay warp. Codegen must compare the whole MMA role, not just total instruction counts. The same general no-new-local/resource gate applies; unchanged group2 and FC2 binaries should remain identical.

## Qualification boundary

`audit_source.py` binds all514 files, reverses only four intended AST changes to recover b52 exactly, enumerates metadata consumers and checks10240 ring/tile cases. Scoped hooks passed. Candidate stays unstaged. Initial compile-only probe reuses matching b52 controls, covers all four formats, N16/32/64/128/256, static/CLC, K96 tails and native ReLU2/SiTU. No owned MoE launch or performance until the source/resource result is reviewed.
