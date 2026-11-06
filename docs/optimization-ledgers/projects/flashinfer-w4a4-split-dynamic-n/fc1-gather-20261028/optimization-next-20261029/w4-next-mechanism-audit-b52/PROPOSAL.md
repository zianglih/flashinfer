# W4 next-mechanism audit at b52

No new high-value source experiment is justified by the inspected evidence. One distinct ownership idea remains lower priority: give otherwise-idle FC1 control warp7 the scale-TMA leg while warp6 retains packed weights. Do not run it merely because a warp is available.

## Current evidence and resource boundary

Retained head `b52e4e09649dc180fc7583a25ec35ff55f04654d`; W4 kernel `de042712ac4fcab0f14eb5f870824416f65dce15e2243198b28ffb4226ac0d58`.

The two final cold-graph, two-cluster sampled traces in `../w4-output-acquire-iket-b52` give these mean instrumented scope durations (ns). Concurrent roles overlap; these are not additive critical-path components or E2E timings.

| Scope | K3 EP4K | V41F TP4K |
|---|---:|---:|
| Gather4 issue | 343.24 | 352.17 |
| Weight/scale TMA issue | 54.13 | 56.47 |
| Transform raw-ready wait | 31.48 | 30.69 |
| Transform decoded-slot wait | 29.81 | 29.77 |
| Transform load/decode | 325.96 | 311.86 |
| Transform store/commit | 85.34 | 81.27 |
| MMA A-ready | 146.70 | 112.30 |
| MMA B-ready | 48.28 | 47.83 |
| PDL dependency wait | 33.20 | 30.00 |

The MMA tests A before B; neither its short B wait nor A wait is an independent operand-arrival measurement. Gather issuing and decoding remain substantial useful instruction work. Output/decoded-slot/PDL waits are near the 32 ns timestamp floor. Resources are the unchanged five-WG FC1: epi0–3 at144, MMA4/scheduler5/weight6/idle7 at80, two dequant WGs8–15 at96, gather16–19 at64. All sampled loaded functions have launchREG96/LOCAL0.

## Conditional candidate: use the existing idle FC1 warp for scale issue

Source: `moe_w4a16_kernel.py:349–366` defines the roles; `:1256–1258` explicitly excludes the unused FC1 warp7 from metadata consumers. `:1823–1921` has warp6 issue packed A then scale TMA, both against the same raw pipeline. FC2 uses warp7 for activations and must retain its current path.

The mechanism would split only FC1 static-data producers, without adding threads, a warpgroup, a buffer, a stage, a tuning axis, or work on the scheduler/MMA warp:

1. Warp6 issues packed-A TMA and warp7 issues scale TMA into the existing disjoint allocations.
2. Both consume the same ordered tile metadata and preserve their own raw-ring index/phase progression. Restore warp7's32 metadata-consumer arrivals; do not let either producer wait on the other's metadata release.
3. Each producer first waits for its existing empty phase, then contributes one arrival and its own transfer bytes to the common full barrier before issuing its copy. Increase the raw full barrier's expected producer arrivals from1 to2. Existing transform wait sees both arrivals and the sum of both byte completions.
4. Raw-stage release still follows all existing LDS/decode/store work; decoded publication, CLC, PDL signal, gather and terminal drains remain unchanged. The common empty barrier prevents either producer overwriting a stage that transforms still read.
5. Preserve identical stage capacities, storage and multicast destinations. FC2 remains source/compile equivalent.

This requires a precise per-producer byte handoff: local CUTLASS `PipelineTmaAsync.producer_acquire` has no `expected_tx` override and uses its full barrier object's fixed count. Do not call it twice with the current total count. A minimal internal wrapper or per-role static barrier view would be needed, preserving one physical barrier and existing consumer semantics. Do not add a named rendezvous that serializes the two issuers.

**Expected generated-code effect:** remove the scale descriptor/address/copy sequence from warp6's per-K critical issue body; place it on already-allocated warp7. Total TMA instruction count is unchanged. There is an additional full-barrier arrival and metadata consumer, and extra control/descriptor instructions in a previously idle warp. The mechanism is worthwhile only if those costs buy useful overlap; it is not automatically an instruction reduction.

**Why it is distinct:** the July ledger `w4a16_optimization_experiments.md:1098–1130` tried an added thirteenth warp (hang before measurement) and then the scheduler warp (sparse metadata backpressure, EP about−1.2%, TP about−0.7%). The current complete20-warp CTA has an idle warp7, so neither failure mechanism is necessarily inherited. The later merged A+scale ring at `:1000–1043` was retained; this proposal must preserve it, rather than restoring the old separate six-stage scale ring. Targeted current W4 ledger/Markdown searches found no identical idle-warp7 trial; that is a bounded history statement.

**Priority:** low. Current weight+scale issue averages only54–56ns and raw-ready wait averages31ns, while the decoder's useful work is much longer. These traces do not establish scale issue as a bottleneck. No clone, production source edit or GPU run is recommended now.

## Reference comparison and excluded rediscoveries

- Rubin CuTe's gather loop (`rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1973–2090`) uses four issuers and preloads row IDs outside K. W4 already has those properties. Its common input barrier and extra SF roles are not a drop-in reason to merge W4's serial dequant and direct-B lifetimes.
- Blackwell/Rubin MegaMoE explicitly makes one gathered row a128B swizzle atom (`block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:_plan_gather_geometry`). Wider contiguous row boxes cannot directly feed native K-major MMA B. `../wide-gather-audit/README.md` already proves this using CUTLASS `mma_sm100_desc.hpp:830`; no wider-box retry. The CUDA13.2.2 [Tensor Map API](https://docs.nvidia.com/cuda/archive/13.2.2/cuda-driver-api/group__CUDA__TENSOR__MEMORY.html) also bounds a swizzled inner box by its swizzle span.
- MegaMoE's two independent static TMA issuers show that role-separated loads can share completion, but its reorganized activation-SF layout and gather rendezvous differ from this W4 contract. This supports auditing ownership, not adopting its synchronization wholesale.
- Current tile-info loading already calls CUTLASS `make_contiguous_group_work_tile_info`, which uses `cute.autovec_copy` for the4-int record. A hand-written vector metadata loader is not an unimplemented capability.
- PDL startup, narrowed TMEM allocation waits, descriptor prefetch, route batching, live-row pruning, elected issuer scope, producer lookahead, quota redistribution and stage sweeps have existing negative evidence. No repeat proposed.
- Decode packing/bit decoding, two/four-scale conversion helpers, interleaved conversion/multiply and wider STTM repetition were previously tested (`w4a16_optimization_experiments.md:243–255,1133–1238,1698–1724,2022–2068`). More nominal packing is not a new mechanism; compiler already interleaves decoded stores with subsequent decode under the current quota.

Read-only audit only. No novel high-confidence throughput improvement emerged from these comparisons; the lower-priority producer split is preserved as a source-grounded hypothesis with a specific dependency contract and measurable costs.
