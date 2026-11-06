# TMEM allocation permit: supported early release

CPU/source-only follow-up at immutable98fd; no kernel, production, or allocator edits and no GPU launches.

The existing kernel allocates its one TMEM region and waits for its pointer at `flashinfer-profile-98fd/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py:968–969`, but releases the allocation permit only after all work and the final CTA barrier at1524, immediately before the128-thread deallocation barrier and `free` at1525–1526. It never allocates TMEM again in the persistent loop.

Early permit release is an existing supported pattern in the same retained source:

- One CTA: `flashinfer/attention/prims_ts/kernels/mla_decode/throughput_latency_1cta/kernel.py:2543–2549` performs `tcgen05_alloc(...CTA_1)` then immediate `tcgen05_relinquish_alloc_permit(...CTA_1)`. Pointer-readiness barriers and compute follow; `tcgen05_dealloc` remains at2614.
- Two CTA: `flashinfer/prims_ts/gemm/kernel.py:3707–3709` allocates and releases the permit, then retrieves the pointer after a barrier; task execution follows and deallocation remains at3739.
- CUTLASS `TmemAllocator.relinquish_alloc_permit` routes the operation only through its allocator warp and does not reset the tracked allocation size. The method promises no further allocation. `wait_for_alloc` is a separate pointer-publication barrier. The inspected local CUTLASS source is the W4A16 project’s vendored snapshot, not a claim about a newly installed package version.

The [official PTX allocation-management specification](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-instructions-tcgen05-alloc-dealloc-relinquish-alloc-permit) forbids future allocation after relinquishment; it does not free the allocation. The ordinary final deallocation and its existing synchronization must stay. Current online documentation is PTX9.4; the experiment does not use its newly added exclusive-allocation feature.

For the one-shot small-N kernel, calling its existing allocator helper after `wait_for_alloc` therefore preserves the allocation/use/free lifetime. The old end-of-kernel relinquish call must be removed for that specialization. All original allocation/free warps, pointer barriers, collective participants, buffer sizes, and final drain remain.

## Occupancy boundary

Our98fd NCU reports establish64/90registers,197504B SMEM,288threads and register occupancy limits3/2 for FC1/FC2. They do **not** prove a two-CTA launch after reducing stages. The experiment owner subsequently reported that the candidate’s static driver occupancy stayed1 despite99200B shared memory, and identified `EIATTR_VRC_CTA_INIT_COUNT=128` plus late `UVIRTCOUNT.DEALLOC.SMPOOL` in its generated code. These are the owner’s observations, not a fresh independent GPU measurement here.

The early-permit experiment tests whether the initial virtual-resource reservation can be returned while the128-column allocation remains live, admitting another block dynamically. No cubin metadata edits or occupancy-result bypass establishes that behavior. Keep resource bounds valid, then verify actual steady-state residency and exactness. Static admission may remain conservative even if the dynamic permit is released.

Known supported metrics from preserved B200 reports:

- `sm__warps_active.avg.per_cycle_active`: baseline T32 FC1=8.95, FC2=9.01 warps/SM for288-thread CTAs.
- `sm__warps_active.avg.pct_of_peak_sustained_active`:13.99%,14.07%.
- `sm__warps_active.max.per_cycle_active` exists, but baseline already reports9.73/9.55, so a tiny max above9 is insufficient evidence. A sustained average approaching18 with unchanged roles is stronger; directly supported CTA counters or a bounded SMID/block-overlap trace would be preferable if needed.

The W4A16 ledger’s rejected experiments at1311 and1667 moved allocation/pointer-readiness barriers to overlap producer setup. They did not investigate returning the allocation permit early to enable concurrent resident CTAs. This mechanism is distinct.
