# Fresh retained prepare/combine counters

Retained61c2c367 source, B300/CUDA13.2, TP8/EP1,16K MXFP4x8, public functional API, PDL on, unfused swapAB. Both model captures passed348-file source, frozen tactic, managed-cache and routing-identity checks. GPU7 was exclusive to this work and explicitly released after completion. All28 artifacts are SHA-verified, including raw `.ncu-rep`, CSV, SASS PC export, logs and receipts; archiveSHA `849ffb4a9c4b6008cc1066d84c840540bee45246bd07261195a885f232730c8f`.

## Bounded memory/stall collection

Each model used15 requested metrics and5 application replay passes, filtering only prepare/combine. No autotune or timing benchmark was run.

| Model / stage | DRAM read / write(GB) | DRAM sustained peak | L2 sustained peak | Long-scoreboard | Registers |
|---|---:|---:|---:|---:|---:|
| tp-v3-mxfp / prepare | 0.691 / 1.002 | 69.84% | 40.19% | 93.07% | 32 |
| tp-v3-mxfp / combine | 1.878 / 0.281 | 85.50% | 49.18% | 92.57% | 64 |
| tp-kimi-k3-mxfp / prepare | 0.529 / 0.998 | 66.37% | 42.23% | 91.00% | 30 |
| tp-kimi-k3-mxfp / combine | 1.879 / 0.162 | 78.79% | 47.94% | 92.53% | 68 |

Combine reads essentially the1.879GB useful BF16 input in each model, has<0.2% aggregate L2 sector hit rate and reaches79–86% sustained DRAM throughput in these instrumented captures. This supports a bandwidth-heavy diagnosis, not removing arithmetic or a scheduler barrier. Prepare has more bandwidth headroom, so one additional K3 prepare-only SourceCounters capture(6 passes) resolved its dependency PCs.

Nsight Compute serializes/perturbs kernel execution; its application replay with cache-control none preserves a different counter context from the normal PDL overlap. Raw DRAM bytes may include cache writeback and are not simply the logical per-kernel source/store byte count. Do not turn these durations, sampled stalls, theoretical sectors or peak percentages into a claimed end-to-end speedup. The existing NSYS trace remains the uninstrumented overlap evidence. [NVIDIA profiling guide](https://docs.nvidia.com/nsight-compute/ProfilingGuide/#replay).

## Prepare PC attribution

Among17,056 sampled long-scoreboard stalls:

-12,040(70.59%) land on payload `STG.E.ENL2.256`, waiting for the preceding `LDG.E.ENL2.256` result.
-2,958(17.34%) land on the first instruction consuming the loaded expanded-route mapping.
-1,252(7.34%) land on the row-limit comparison after its metadata load.
-562(3.30%) land on the first SF-address instruction that reuses a register after its scale preload. This is a data/register dependency, not a CTA barrier.

The remaining signed index arithmetic is visible in `pc-attribution.json`: source `row // route_tile`, `row % route_tile` and `mapping[row] // top_k` still generate signed floor correction sequences. For K3's mapping quotient by16, the SASS includes a sign shift, adjusted high LEA, mask/comparison and correction instructions despite valid expanded indices being nonnegative. The earlier fixed128-row SF bit-index cleanup is already retained and is not being proposed again.

## One concrete, bounded candidate

Use `Uint32` operands for these nonnegative internal row/mapping quotients and remainders, preserving the existing signed `source` branch join and `Int64` promotion before byte-address multiplication. This is a general index-domain declaration for every positive route tile/top-k, not a power-of-two or model specialization. It keeps the same routing traversal, payload/SF work, invalid-row zeros, memory instructions, ownership, PDL and public API. Shared BF16 W4A16 preparation benefits from the same source change.

The domain follows the positive grid-stride row iteration and routing's valid expanded-index writes: `RoutingKernel.cuh:527–543` and `trtllm_fused_moe_routing_custom.cuh:300–312` write nonnegative expanded indices only to valid local permuted positions. The prepare validity branch at`:121–124` precedes mapping use. Invalid logical mapping slots may contain negative sentinels and must remain unread. `unsigned-index-proof.json` checks62,205 positive-divisor/int32 cases; this is an algebra check, not compiler or GPU validation.

First qualification must show reduced correction SASS, no new memory operations/spills/resource regression, exact payload/SF bytes, unchanged padding canaries and replay behavior across scaled/BF16, PDL, empty/reactivated and non-power-of-two top-k. This cannot remove the dominant payload traffic or its observed load latency, so speedup is unproven. The user also values simpler instruction sequences when performance is neutral.

SF stores still account for23.21% of measured LSU store sectors, the known scattered canonical-layout cost. Their coalescing/remapping experiments remain rejected; these counters supply no new reason to reopen them. No new combine candidate is justified.
