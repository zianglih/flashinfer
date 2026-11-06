# Pipeline initialization fence consolidation — source-only candidate

Base: clean cache-tier commit `8b74eb6fa77651bb20dacb56b8e13872f3ad9885` in the independent, unstaged `flashinfer-pipeline-fence-review` clone. Patch/source hashes and exact AST-scope proof are recorded in `source.json`. No GPU gate or timing has run.

## Change

The custom Blackwell `PipelineTmaUmma.create` and `PipelineUmmaAsync.create` gain `defer_sync=False`. Their default behavior is unchanged. Only the common split blockscaled core opts in to both, and it issues one unconditional `mbarrier_init_fence()` after all pipeline and TMEM allocator initialization. This replaces the CLC-only final fence. Existing two-CTA `cluster_arrive_relaxed`/`cluster_wait`, TMEM allocation, and all-thread named-barrier wait are unchanged. No MegaMoE/W4A16 caller is edited.

## Synchronization proof

The local custom `pipeline_init_wait` name is misleading: it emits only `mbarrier_init_fence`, without a CTA or cluster rendezvous. The SDK's same-named helper is different: its wait helper emits CTA sync or cluster wait, and requires a separate fence/cluster arrival. The candidate does not substitute either SDK helper and adds no CTA synchronization.

The actual CuTe4.7.1 `MbarrierArray` constructor initializes each barrier in an elected lane of warp0. All required pipeline objects, including optional cp.async and CLC objects, are constructed before the consolidated fence; no producer or consumer operation is issued between their initializations. `TmemAllocator` initializes its two-CTA deallocation barrier and emits its own fence. That SDK-owned fence is preserved, and the consolidated fence follows it.

For one CTA, every thread then executes `tmem.wait_for_alloc()`, whose implementation calls the existing `NamedBarrier.arrive_and_wait()` with `num_threads=self.threads_per_cta`. Thus every compute/producer/scheduler warp crosses the same CTA rendezvous after the elected initialization and fence before any pipeline use, including the startup prefetch. For two CTAs, the original cluster arrival/wait precedes allocation and that same named-barrier wait, preserving visibility across peer CTAs. CLC's additional scheduler warp is covered by the derived thread count. The startup prefetch inspects routing only after initialization and TMEM synchronization; every thread still reaches the later dependency wait even for zero work. Thus zero-work routing cannot bypass the initialization rendezvous.

SDK source snapshots from the actual runtime are in `../pdl-inactive-wide-r1/sdk-pipeline-sources.json` and `sdk-pipeline-arrival-tmem.json`; no CUDA context was created to inspect them.

## Existing codegen evidence and expected boundary

The existing M256/N256 two-CTA NVFP4 FC2 PTX has three distinct startup `fence.mbarrier_init.release.cluster` instructions at lines96,115,125; the later cluster arrival/wait and `bar.sync 3,288` are at126–133. The compiler has not already merged these fences. Generated artifacts are in `../pdl-inactive-wide-r1/raw/integrated/`; all three precision formats have byte-identical inactive codegen between integrated and cache-tier sources.

The candidate defers the first two custom fences and emits one after all initialization. The SDK TMEM allocator's own fence remains for two-CTA kernels; whether the compiler coalesces adjacent fences is a generated-code question for a later bounded gate. We claim fence consolidation only, not removal of CTA/cluster barriers or a performance gain. The AST proof permits only the two new default-False knobs/conditionals, two core opt-in keywords, and replacing the CLC-only final fence with an unconditional fence; all remaining core/helper AST is unchanged. Ruff check/format and py_compile pass on both changed files.
