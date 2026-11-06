# FlashMLA Gather4 patterns relevant to split W4A16

Read-only source audit on October 25, 2026. Official `deepseek-ai/FlashMLA` default branch resolves to **`0f11e178da1f67becb087a324b400854931ec3e3`**, committed October 15, 2026. All links below are pinned to that revision. Source snapshots are under `flashmla-source/`; no FlashMLA benchmark or GPU execution was performed.

## Most transferable observations

- **Uniform issuer owns its row indices.** The BF16 sparse-prefill implementation uses four producer warps per CTA, elects one lane per warp outside its block loop, and directly loads `int4` row indices into that issuer. Each row group reuses its indices across all 64-BF16 channel chunks. This avoids our repeated distributed-lane-to-issuer shuffles. The head128 configuration gives each elected K issuer four `int4` groups, or 16 rows, rather than assigning all 64 CTA rows to one issuer. [Producer implementation](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/cuda_kernels/sm100/prefill/sparse/fwd/head128/phase1.cuh#L395-L453)
- **The small-top-k BF16 path improves index loading, not Gather4 payload size.** Four elected producer warps fetch indices with explicit 256-bit global loads, keep the index array in issuer registers, wait for buffer availability, then issue four Gather4 channel chunks for each row group. The two CTAs split the 512 channel dimensions. [Index prefetch and issue loop](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/cuda_kernels/sm100/prefill/sparse/fwd_for_small_topk/head128/phase1.cuh#L420-L473)
- **Repeated invalid indices are a documented performance problem.** The large-head BF16 path checks whether an issuer's groups are all invalid and skips their Gather4 requests. It initially loads every ring-buffer slot to establish zero-filled storage, and skipped transfers explicitly complete the expected transaction bytes. This is an upstream implementation rationale, not an independently reproduced hardware result. Our padded rows currently all use one identical OOB coordinate. A minimal hypothesis is distinct guaranteed-OOB coordinates for padded rows, preserving zero fill and transaction size; skipping groups requires more careful barrier and stale-buffer reasoning. [Invalid-group handling](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/cuda_kernels/sm100/prefill/sparse/fwd/head128/phase1.cuh#L405-L451)

## Layout and synchronization

The BF16 descriptor has box `{64,1}` elements, no interleave, 128-byte swizzle and 256-byte L2 promotion. Therefore one Gather4 moves four 128-byte row pieces, just like our BF16 path. It does not solve instruction overhead by transferring an arbitrarily wide BF16 row in one request. The matching shared layout is tiled `UMMA::Layout_K_SW128_Atom<bf16>` with the row axis tiled before the channel axis. [Descriptor](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/cuda_kernels/sm100/prefill/sparse/fwd/head128/phase1.cuh#L663-L684), [shared layouts](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/cuda_kernels/sm100/prefill/sparse/fwd/head128/config.h#L53-L80).

The intrinsic takes one descriptor, one barrier, a destination, one channel coordinate and four row coordinates. `cta_group::2` optionally clears the peer bit to complete the leader CTA's barrier; it is not an automatic cross-warp broadcast of independent per-lane requests. FlashMLA explicitly synchronizes the cluster before either CTA can issue TMA to an initialized leader barrier. Its producer splits K/V regions and waits for consumer release before reusing each region. [Intrinsic](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/3rdparty/kerutils/include/kerutils/device/cuda/sm100/intrinsics.cuh#L9-L54), [cluster initialization](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/cuda_kernels/sm100/prefill/sparse/fwd/head128/phase1.cuh#L130-L169).

The relevant BF16 path uses `EVICT_LAST`, matching our reuse-oriented activation hint. Do not copy the quantized decode path's `EVICT_FIRST` solely because it also uses Gather4.

## Decode pattern: useful staging idea, different workload

The quantized decode path separates an index-transformation warp from one elected raw-data issuer. Index lanes prefetch the next block, compute paged-cache coordinates and validity, stage them in shared memory, and signal ready/free barriers. The issuer reads `int4` coordinates from that shared buffer, preloads the next group before issuing the current Gather4, and issues one raw-row transfer per group. [Issuer](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/cuda_kernels/sm100/decode/sparse/head64/kernel.cuh#L504-L531), [index staging](https://github.com/deepseek-ai/FlashMLA/blob/0f11e178da1f67becb087a324b400854931ec3e3/csrc/cuda_kernels/sm100/decode/sparse/head64/kernel.cuh#L533-L620).

This suggests shared index staging or direct elected-lane vector loads as alternatives to shuffles. It does not justify copying paged-coordinate math, quantized raw-row layouts, dequantization ownership, or adding a new index warp to W4A16 without measuring the cost. Split W4A16 has long K reductions and reuses the same routed-row map across K tiles; FlashMLA advances to new sparse KV rows each attention block. Its dedicated four-warp BF16 producer allocation is also substantially larger than our current activation-loader ownership.

## Our v4 emitted instruction evidence

The saved synthetic specialization is `(M,N,K)=(256,128,256)`, cluster `(2,1)`, top-k8, PDL off. Its activation K-loop in `codegen-v4/evidence/gather4/codegen-v4/ptx-topk8/fc1.sass`, addresses `0x5430–0x7080` (lines 2701–3607), has 454 static instructions excluding out-of-line barrier polling:

| Instruction | Count per K-loop body |
| --- | ---: |
| Gather4 | 64 |
| SHFL | 64 |
| R2UR | 64 |
| UMOV | 174 |
| UIADD3 | 70 |
| ELECT | 1 |

The one `ELECT` belongs to barrier arrival. Although PTX repeats election calls around unrolled row groups, the SASS Gather4 issue body contains no repeated election instructions. Optimizing source-level elections alone is therefore not supported by this emitted evidence. Row IDs are invariant across K, but their shuffle/R2UR conversion repeats each K256 iteration. For an otherwise equivalent H7168 specialization, 28 iterations imply 1,792 Gather4 instructions, 1,792 shuffles and 1,792 R2UR instructions per CTA work tile. This is a static extrapolation, not a measured instruction count; the saved synthetic launch itself has K256. The original v3 SASS was subsequently located under project-root `evidence/gather4/ptx-topk8/fc1.sass`: it contains four election/broadcast scalarization loops, each executing sixteen times for this geometry. See `SASS_COUNTS.md/json` for the complete comparison.

## Exact implementation pointers

All line numbers below refer to the pinned source snapshots above:

- `prefill-head128-phase1.cuh:398–400`: four producer warps and election outside the block loop.
- `prefill-head128-phase1.cuh:409`: issuer-owned `__ldg((int4*)...)`, with row-group and warp indexing.
- `prefill-head128-phase1.cuh:413–414`: all-invalid detection and `k >= NUM_BUFS` before skipping.
- `prefill-head128-phase1.cuh:439`: exact comment begins “TMA has performance issues when all indices are the same (even if those indices are invalid)”.
- `prefill-head128-phase1.cuh:440`: first NUM_BUFS copies initialize storage before skipping is enabled.
- `prefill-head128-phase1.cuh:442`: `plan.bar_k_part0_ready[cur_buf].complete_transaction(0u, NUM_LOCAL_ROWS_PER_WARP*4*D_sQ*sizeof(bf16), 1u);`
- `prefill-head128-phase1.cuh:451`: corresponding part1 transaction completion uses `D_tQ`.
- `small-topk-head128-phase1.cuh:426–427`: elected issuer and explicit comment that avoiding warp-index shuffle is faster.
- `small-topk-head128-phase1.cuh:439–450`: issuer-register index array and 256-bit index load.
- `small-topk-head128-phase1.cuh:452–467`: wait for empty storage, then reuse int4 indices across four channel chunks.

The separate `WIDE_GATHER_LAYOUT_NOTES.md` explains why a legal 512-byte no-swizzle TMA row is not directly compatible with TCGen05 K_INTER's fixed 16-byte inner row stride.

## Original bounded experiment plan

1. Distinct OOB row coordinates to test the repeated-invalid-index hypothesis without changing transaction bytes or ownership.
2. Reduce index movement and uniform-register operand packing across K: direct issuer vector loads or compact staging, while watching register pressure. Preserve index reuse rather than adding global reloads unknowingly.
3. Mixed FC1/FC2 cluster sizes can distribute FC1 issue work across existing CTAs; this is more compatible with the current ownership than importing FlashMLA's entire producer warpgroup. Verify actual multicast/byte accounting rather than assuming a larger cluster provides the desired split.
4. If needed, verify descriptor L2 promotion and compare the existing reuse hint deliberately. FlashMLA uses the same 128-byte swizzle and BF16 chunk width, so a layout rewrite is not established as necessary.

Use the existing candidate-only AUTO probe at T16/T512/T4096/T16384. Retain all previous baseline evidence, and use the full 13-token paired methodology only after a useful candidate survives these bounded screens. No Nsight collection was launched; existing whole-call CUPTI medians cannot be decomposed into kernel timings afterward.

## Experiment outcomes

The source audit informed completed W4A16 experiments, preserved in the [ledger](README.md). Distinct OOB coordinates showed no consistent benefit. The final uniform candidate caches up to 48 route indices across K with unchanged warp/register ownership; caching all 96 introduced spills in mixed N192. Preferred cluster4 with runtime fallback2 passed focused exact tests, but AUTO selected no mixed tactic in the measured probes. Skipping unused Gather4 groups passed focused tests but stalled during T512 AUTO profiling; its cause remains unconfirmed and the variant is rejected.

The [final full-grid comparison](results/split-v3/RESULTS.md) is 1.007745× overall, 1.030856× decode, and 0.948616× prefill, using two fresh candidate sweeps and the preserved baseline medians. The prefill regression prevents recommending this candidate as a solid optimization. Its source remains unstaged for review; these results do not establish a FlashMLA performance comparison.
