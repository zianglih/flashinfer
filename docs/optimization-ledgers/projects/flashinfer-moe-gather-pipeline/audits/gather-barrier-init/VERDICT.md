# Gather barrier initialization: legal distribution, native benefit unproven

Read-only source audit of retained `49c91adf47d30fc2049c76cbaf34d0ccf3291434`, swap kernel `482b636a1714486e2ffb34c8ae005da3cef26f25f0ce034ba1eb59c6198d6276`. No source edit, compiler probe, timing, or GPU launch was performed by this audit. The integration agent owns the separately authorized two-signature compiler probe.

## Legality and lifetime

Distributing distinct barrier objects across lanes is legal. Each object remains an aligned 8-byte local CTA-shared allocation and has exactly one initializer. `mbarrier.init` has no `.aligned` collective qualifier or uniform-address requirement. Initializing an already-valid object again is undefined, so the unique-address mapping matters. The init fence orders only initializations performed by the same executing thread; every initializer must reach it. The current unconditional fence, then existing two-CTA cluster synchronization and all-thread TMEM rendezvous, provide the required publication before any producer/consumer uses the arrays. No barrier count, allocation, phase, arrival count, or PDL boundary changes. [CUDA 13.2.2 PTX9.2 init and lifecycle](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-mbarrier-init), [fence semantics](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-membar).

Precise source chain: `moe_swap_ab_kernel.py:2731–2741` initializes both arrays with counts `cta_group_size` and `1 + min(route_tile,128)`; `:2743–2748` fences, joins the two-CTA cluster if selected, allocates TMEM, and waits. The allocator uses named barrier3 with `threads_per_cta` participants. Installed CuTe4.8 `memory/tmem.py:509–519` calls that barrier unconditionally in `wait_for_alloc`. This holds for static/CLC, active/empty work and both CTA groups because role/work divergence occurs later. All array addresses are in disjoint Int64 storage fields.

## General stage handling

Use a compile-time chunk loop and unique lane remainder, not a stage cap or a dynamic cursor:

```python
if warp == 0:
    for chunk in cutlass.range_constexpr((self.num_stages + 31) // 32):
        stage = tidx + chunk * 32
        if stage < self.num_stages:
            # Existing two mbarrier_init calls and arrival counts, unchanged.
```

The quotient/remainder mapping visits every stage exactly once for any positive compile-time depth. `proof.py` checks1–4096 and extracts the actual storage planner without importing CUDA. Its current supported-type/geometry enumeration bounds capacity at11; increasing tile-metadata depth or scratch cannot raise that bound. All364 saved FC1 native selections replay to their recorded capacities: stages2/3/4/5/6/8/9/10/11 occur8/13/106/124/11/5/19/53/25 times. Explicit depths remain governed by the existing actual allocation check. The source must not encode11 or assume depths fit one warp.

## SDK and reference distinction

- Current installed CuTe4.8 `pipeline/helpers.py:330–353` sets `use_uniform_mbarrier_init=True`, elects one lane in warp0, and serially initializes the array. Its `cute/arch/mbar.py` docstring describes a same-object single-thread call; the implementation directly emits NVVM and does not elect a lane internally. The distinct-object interpretation above follows the PTX object contract and the existing Mega example, rather than treating that wording as permission for duplicate same-object initialization.
- CUTLASS C++ `arch/barrier.h:110–157` aligned array helpers also elect one lane and loop. Rubin GEMM pipeline construction uses these pipeline abstractions. Thus the proposal does **not** simply reproduce installed GEMM initialization.
- Existing Rubin Mega token communication `token_comm_gen_specialized.py:1369–1378` and its refinement path initialize distinct `base+thread_idx` objects in separate threads, then fence and CTA-join. This establishes a source precedent only, not efficient native lowering.
- W4 kernel `:1211–1307` constructs its raw/decoded/B/accumulator/metadata/CLC pipelines through SDK classes, then uses the common pipeline-init protocol. It has no extra manual gather initializer to change. SDK-wide or W4 changes are outside this proposal.
- Installed source bytes and SHA256s are preserved in `../barrier-init-installed.json`; independent publication proof is `../gather-barrier-init-peer.md` and `.json`.

## Native and history boundary

Retained N3U narrow FC1 has ten custom `SYNCS.EXCH.64` instructions for five stages, using uniform addresses/data (`UR31+offset`, `UR10/6`) around0x330–0x3e0. Lane-varying addresses may require matching/uniformization loops, extra registers or serialization. Two static PTX init sites do not prove fewer native transactions or a shorter CTA startup. Inspect full native control flow, dynamic address handling, actual resources and unchanged post-init work before any performance screen. No existing profile proves this startup dominates E2E.

A warp-striped alternative could keep one elected issuer per existing warp and assign `stage=warp+chunk*(threads_per_cta//32)`. Unique mapping and existing all-thread publication make it legal in principle; however it adds elections/participation and still needs native proof. It is held, not a second prototype. If the lane probe necessarily serializes or adds more control work, report that before proposing further experiments.

Bounded history search covered the old project's `CLOSED_LEADS.md`, synchronization audit, October27 startup/fence ledgers and current project audit notes; no prior exact distinct-address initializer distribution was found. This is not proof of absence from every unindexed artifact. The nearby closed experiment `scripts/clc_tmem_startup_20261027/screen-v2/screen-results.md` removed scheduler TMEM participation and moved pointer reads; it added209/60 static instructions across CLC/static cases and was neutral (overall0.99971x). The retained `scripts/pipeline_init_fence_20261027/gate/result.md` consolidated redundant fences. Neither changed the initializer-to-object mapping. Preserve their final common fence/rendezvous rather than reopening either protocol.
