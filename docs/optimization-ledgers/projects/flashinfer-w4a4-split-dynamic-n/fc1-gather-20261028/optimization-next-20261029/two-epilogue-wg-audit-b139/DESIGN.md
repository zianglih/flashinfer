# Two FC1 epilogue warpgroups: feasible ownership, register gate first

Read-only audit of retained b13963b0, swap kernel f4171232. No implementation, new tactic, compilation, or GPU run was made. The preceding static SF-selector experiment is rejected separately.

## Recommendation

A bounded compile-only FC1 prototype is defensible, but two epilogue groups are not yet a qualified policy. Partition the existing **32-column virtual accumulator slabs**, retain the current transpose and arithmetic, and leave FC2 unchanged. This removes the ownership/layout uncertainty before considering performance. Stop if the required 128-register epilogue budget introduces new local memory traffic; do not rescue it with dtype/model exceptions or a quota sweep.

The sampled N3U EP16K trace at d9 showed about 4 microseconds in each epilogue body, with its nested initial TMEM loads and two transposes accounting for about 40–45%. This is an instrumented, two-cluster sample using its frozen winner, not a causal estimate or a speedup prediction for b139. Two groups do the same total work: the proposed benefit is concurrent independent slabs hiding instruction and TMEM latency. A shared TMEM/issue throughput limit would prevent that benefit.

## Registers are the deciding constraint

| FC1 design | Threads | Control | Gather | Epilogue groups | Role register total |
|---|---:|---:|---:|---:|---:|
| Retained | 384 | 120 | 128 | 1 × 256 | 64,512 |
| Proposed uniform allocation | 512 | 128 | 128 | 2 × 128 | 65,536 |
| Duplicating retained epilogue | 512 | 120 | 128 | 2 × 256 | 97,280 — impossible |

Counts are per thread; each role has 128 threads. A 512-thread launch can reserve at most 128 registers per thread in a 64K SM file. Prefer uniform128 across all four groups: remove the three FC1 reconfiguration sites, give control eight more registers, and avoid dynamic donation. This exactly fills the register file while still allowing one CTA per SM. Retaining initial168 with512 threads cannot fit. The control/MMA group already has known synthetic descriptor spills at120, so reducing its quota is not a free solution. Explicitly cap the diagnostic compile at128 and verify the actual CUBIN allocation; launch geometry alone is not a substitute for that check.

The retained epilogue reachable-SASS register-index audit spans R68–R124 for ten captured FC1 configurations, but MXFP8 N256 ReLU2 reaches R161. These are assigned indices, **not peak-live pressure**. Halving slabs can shorten static liveness, but each 32-column slab still owns the same per-thread16/32 FP32 values; simply splitting the loop does not halve that working set. Require paired generated code before any numeric/performance run. Evidence: `../native-tmem-fc1-audit/retained-epi-register-indices.json` and its source-bound captures.

Hardware basis: Blackwell has a64K32-bit register file per SM; `setmaxnreg` uses a per-CTA pool and multiples of8, with all warps in a warpgroup participating. [Blackwell tuning guide](https://docs.nvidia.com/cuda/blackwell-tuning-guide/index.html#occupancy), [PTX register allocation](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#miscellaneous-instructions-setmaxnreg).

## Token-column ownership, without another transpose

Retain control warps0–3, use epilogue warps4–7 and8–11, and place the four gather warps last at12–15. Each epilogue group uses local warp IDs0–3 and the current `_blockscaled_load16x32` / `_blockscaled_transpose16x32` functions. The PTX access restriction is by the warp's position within its warpgroup; both groups can address all columns of their respective32-lane bands. They must own disjoint column slabs. [PTX TMEM access restrictions](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#tcgen05-memory-access-restrictions).

Use the current virtual column ordering over `channel_tiles * allocated_n / 32`. Group `g` takes logical steps `g, g+2, ...`, then applies the existing phase-dependent rotation. A slab owns the full128-row CTA slice, including each up16/gate16 pair. The group IDs therefore do not change channel layout, scale ownership, activation rounding, TMEM allocation or global output layout. N16 remains a32-column physical slab; with only one slab, one epilogue group necessarily has no useful data work. Do not split a slab into arbitrary thread halves: the current SF32 exchange and TMEM lane mapping are designed for all four warps.

Within a slab the transpose stays entirely inside its original32-column accumulator rectangle. Distinct slabs cannot overwrite each other's scratch. For two channel tiles, the existing virtual-slab mapping keeps their column ranges distinct too. `prove_partition.py` exhaustively checks disjoint output ownership and protected-step coverage for N16/32/64/128/256, one/two channel tiles, both accumulator phases, every valid-token count, and every positive protected span. `partition-proof.json` is a logical proof only, not a generated memory-model test.

## Synchronization and release

- Change accumulator consumer participation from `128 * cta_group_size` to `256 * cta_group_size`; retain the existing peer-CTA mask and all producers. Each group waits for the same ready phase and arrives exactly once on the empty barrier.
- In overlapping FC1, group `g` releases after its **last owned protected step**, including its TMEM transpose loads. A group with no protected step arrives after the ready wait without reading protected TMEM. It may then process disjoint unprotected slabs. The mbarrier itself joins the256 consumers; no new cross-group named barrier is needed. The next MMA cannot overwrite the shared interval until both groups have released. For non-overlap, release only after all assigned slabs.
- Retain the per-thread TMEM load fence at the release boundary. Partial or wholly skipped protected slabs still execute their group's release exactly once. Do not use the old single-group `step+1==protected_steps` test verbatim: odd protected counts would leave one group without a release.
- Gated SF32 needs private shared `[4,32]` Float32 scratch per group and separate128-thread named barriers (e.g.6 and7). Reusing barrier6/scratch would mix unrelated token slabs or deadlock partial tiles. Keep both before-read and before-reuse rendezvous in each group. Non-gated SF32 joins the two halves in registers and does not need cross-group exchange.
- Increase CLC metadata consumers by128 threads per CTA; preserve leader-only MMA accounting. Update TMEM retrieve and final CTA rendezvous thread counts. All epilogue groups process the same scheduled tile even when one has no live slab. Static scheduling work IDs remain unchanged.
- The current `warp>=4` payload wait includes both new epilogue groups and the final gather group. Preserve existing PDL release/signal sites, raw operand counts, gather relay and K-stage ownership. No new PDL dependency is created.

FC1 shared scratch rises by only512 bytes if each group reserves its existing512-byte scratch; that must still flow through the capacity planner. No extra TMEM columns are needed. In contrast, duplicating FC2's64-token/two-stage BF16 bulk buffers would increase its32KiB scratch to64KiB, can lower operand stages, and needs separate TMA store rings and barriers. This is why the first candidate should keep FC2 and its compile/timing behavior unchanged.

## Reference patterns and their limits

- Current SM100 MegaMoE uses four epilogue warps with256 registers, gather and control groups at80, one128-thread epilogue rendezvous, and accumulator participation proportional to consumer warp count. See `block_scaled_swap_ab_mega_moe_kernel_gen_specialized.py:74` and `block_scaled_swap_ab_fc12_epilogue.py:1173`.
- Current Rubin uses one four-warp epilogue at168 registers, separate operand/scale groups, and a128-thread epilogue barrier. See `rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:335–425,2898`. Its transformed tiled-copy layout does not establish a two-group transpose pattern.
- CUTLASS SM100 TMA epilogue fixes `ThreadCount=128`; kernel pipeline counts derive from that count. See `references/cutlass/include/cutlass/epilogue/collective/sm100_epilogue_tma_warpspecialized.hpp:127` and `gemm/kernel/sm100_gemm_tma_warpspecialized.hpp:530`. This validates making ownership counts consistent, not an existing dual-group performance claim.

## Minimum qualification if implemented

Before implementing the complete dual-group partition, the cheapest honest feasibility gate is a compile-only four-WG shell around the existing algorithm: launch512 threads, keep the original control/epilogue/gather groups, bound gather to warps8–11, let warpgroup12–15 do only required common barriers, remove all FC1 setmax calls, and compile with an explicit128-register cap. Never launch this diagnostic. Require recorded512-thread metadata, actualREG≤128, no USETMAXREG, and matched local-memory/instruction analysis. This tests the existing slab body under the real register-pool limit; it is not performance evidence and a failure does not prove a subsequently shortened half-slab live range could never fit. Do not start the more invasive ownership rewrite if this probe introduces heavy spills.

If the shell qualifies, compile the unchanged arithmetic with actual two-group FC1 ownership and128 registers. Include the real N3U EP16K winner, per-token SiTU, MXFP8 N256 ReLU2 (R161 today), M512/N128/K8 mixed-MX pre-existing spill case, N16,1/2CTA, SF16/SF32, K96/partialK and CLC/static. Require no new local traffic versus paired baselines, no direct calls, correct role endpoints and exactly unchanged FC2 code. Preserve known pre-existing spills as such.

Only after that gate, use existing exact oracles with alternating wide/narrow persistent tiles, odd protected spans (including b139's96-column span), wholly skipped slabs, changed-routing graph replay and both output layouts. Then a small frozen-winner stock-clock CAAC screen should include decode controls, because extra threads and idle groups may offset the prefill benefit. No new autotune axis is required or proposed.
