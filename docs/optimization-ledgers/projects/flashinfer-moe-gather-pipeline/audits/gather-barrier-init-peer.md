# Gather barrier initialization distribution: independent source review

Source49c91adf / swap kernel482b636a. Read-only review; native candidate not yet compiled.

The proposed mapping is legal if each barrier address has exactly one initializer and every initializing lane executes the existing fence. PTX imposes per-object initialization/visibility requirements, not a requirement that all distinct barrier objects use the same CTA thread. The installed CuTe helper's single-thread wording describes its usual same-address call; its implementation directly invokes NVVM without electing a lane. The installed `MbarrierArray` intentionally uses uniform warp0/elected initialization, so it is a lowering precedent to compare against, not evidence of a cross-lane prohibition. [PTX mbarrier.init](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-mbarrier-init).

The existing publication is sufficient and must stay intact. `fence.mbarrier_init.release.cluster` covers only initialization issued by the same thread, but the current source executes it unconditionally in every thread. One CTA then reaches the all-thread named barrier3 through `TmemAllocator.wait_for_alloc`; two CTA additionally execute the existing fence→cluster-arrive-relaxed→cluster-wait before allocation. No role accesses a gather barrier before this rendezvous. No extra warp/CTA wait is needed. [PTX fence](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-membar), [cluster synchronization](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-barrier-cluster).

Precise source anchors:

- `moe_swap_ab_kernel.py:2720`: allocator uses named barrier3 with `threads_per_cta` participants.
- `:2731–2741`: both custom gather arrays, unchanged arrival counts (`cta_group_size` and `1 + min(route_tile,128)`).
- `:2743–2748`: unconditional fence, optional2CTA cluster synchronization, allocation and all-thread wait.
- Installed4.8 `cute/arch/mbar.py:121–140`: direct NVVM initialization/fence wrappers.
- Installed4.8 `memory/tmem.py:509–519` and `pipeline/helpers.py:689–701`: wait_for_alloc→named barrier→CTA barrier.
- Existing SM100 Mega token communication `token_comm_gen_specialized.py:1373–1376` initializes different addresses by different threads, then fences and synchronizes. This is a source precedent, not measured native lowering evidence.

A generic source form can keep the loop bound compile-time without assuming stages≤32:

```python
if warp == 0:
    for chunk in cutlass.range_constexpr(cute.ceil_div(self.num_stages, 32)):
        stage = tidx + chunk * 32
        if stage < self.num_stages:
            cute.arch.mbarrier_init(storage.gather_barriers.data_ptr() + stage,
                                    self.cta_group_size)
            cute.arch.mbarrier_init(storage.gather_local_barriers.data_ptr() + stage,
                                    1 + min(self.route_tile, 128))
```

`num_stages` is already a positive compile-time value selected/checked against shared storage. The chunk form admits every positive stage count and avoids a hardcoded architectural limit. CPU enumeration checks exactly-once coverage for1–1024 stages; the general proof is the unique quotient/remainder of each stage by32.

Native caution: retained N3U narrow FC1 has ten custom initializer `SYNCS.EXCH.64` sites (five stages, two arrays), all using uniform addresses/data, at0x330–0x3e0. Lane-varying addresses could cause compiler uniformization loops or hardware serialization. The candidate must demonstrate actual native instruction/control-flow benefit, unchanged resources/LOCAL0 and intact fence/rendezvous before timing. Two PTX sites alone are insufficient. No warp-striped alternative or added policy is proposed.
