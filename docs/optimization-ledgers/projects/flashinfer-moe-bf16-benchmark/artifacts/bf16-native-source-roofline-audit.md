# BF16 native kernel source and arithmetic-intensity audit

The evidence so far establishes a real BF16 GPU latency gap, but does not establish an avoidable BF16 implementation defect. Low Tensor Core utilization alone is compatible with the measured weight traffic and high DRAM utilization. Register counts are high, but count alone does not demonstrate spilling; the extended NCU counters are the appropriate check.

## Arithmetic intensity and the 4096-token question

These are isolated EP8 shapes with 256 global experts and 32 local experts. The global/input token count is not the row count of each local expert GEMM. Actual native routing replay gave:

| Input tokens | Local assignments R | Active local experts E | R/E | Selected token tile | Sum ceil(rows/tile) | Padded rows | Useful row fill |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 32 | 31 | 21 | 1.47619 | 8 | 21 | 168 | 18.45% |
| 4096 | 3715 | 32 | 116.09375 | 128 | 40 | 5120 | 72.56% |

At 4096, eight experts have more than 128 rows, so those experts use two token tiles. These are token tile counts, not total output-channel CTAs.

With H=7168 and I=2048, excluding SwiGLU scalar work:

- FC1 useful FLOPs = 2 * R * H * (2I) = 4RHI.
- FC2 useful FLOPs = 2 * R * I * H = 2RHI.
- One read of active BF16 weights costs 4EHI bytes in FC1 and 2EHI bytes in FC2.
- Therefore both GEMMs have weight-only useful arithmetic intensity R/E FLOP/byte.
- A simple activation-traffic model adds 2R(H+I) bytes per GEMM, assuming each logical BF16 activation input and output is transferred once. This is a reference model, not a measured byte count: repeated channel-tile loads, padding, L2 reuse, and native output packing can alter actual DRAM traffic.

| Input tokens | FC1 useful GFLOP | FC2 useful GFLOP | FC1 BF16 weights GB | FC2 BF16 weights GB | Weight-only AI | FC1 AI with ideal activations | FC2 AI with ideal activations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 32 | 1.820328 | 0.910164 | 1.233125 | 0.616563 | 1.47619 | 1.47551 | 1.47482 |
| 4096 | 218.145751 | 109.072876 | 1.879048 | 0.939524 | 116.09375 | 112.01190 | 108.20733 |

NVIDIA's current [HGX specification](https://www.nvidia.com/en-us/data-center/hgx/) gives 36 PFLOPS FP16/BF16 for an eight-GPU HGX B300 and explicitly labels this sparse, with dense at half. This is 2.25 dense PFLOPS/GPU. NVIDIA's [HGX reference architecture](https://docs.nvidia.com/enterprise-reference-architectures/hgx-ai-factory/latest/components.html) gives up to 8 TB/s HBM bandwidth/GPU. The advertised ideal dense BF16 ridge is consequently 281.25 FLOP/byte. This is a hardware reference, not a promise of attained peak at the benchmark's clocks.

Even the ideal 4096-input BF16 workload is below that ridge. If each of its 40 token tiles rereads an expert's weights, the weight-only AI falls to 3715/40 = 92.875 FLOP/byte. Actual NCU DRAM traffic should determine which reuse model applies. Counting padded MMA work instead gives 160 FLOP/byte for one weight read across 32 experts; it is still below the nominal ridge and those padded FLOPs are not useful model work.

W4A16's packed FP4 weights plus one byte per 16 weights cost 0.5625 bytes/weight instead of 2, so its ideal weight-only AI is 3.55556 times BF16: 412.77778 FLOP/byte at 4096. Thus W4A16 can move toward a compute/dequantization bound while BF16 remains constrained by weight traffic. Sharing the BF16 Tensor Core arithmetic does not force equal bottlenecks.

## Source contracts

Source commit: `2079fa00c4a2a0fb2e95bb284978a703653a4830`; the following kernel files are unchanged by this benchmark-only PR.

- `csrc/trtllm_fused_moe_runner.cu:120-145`: BF16 FC1 options use `fusedAct=true` (because DeepSeek FP8 is false), `routeAct=true`, `staticBatch=false`, `transposeMmaOutput=true`, `tileSize=tileTokensDim`, and `epilogueTileM=128`. Gather and SwiGLU are already fused into FC1.
- `csrc/trtllm_fused_moe_runner.cu:188-208`: FC1 shape is `(numTokens, 2*intermediateSize, hiddenSize)` and passes dynamic routing/CTA metadata. The transposed batched GEMM makes M the output-channel dimension and N the token dimension. A cubin label `t128x8x128` means 128 output channels by 8 tokens by K=128; it does not mean 128 padded tokens.
- `csrc/trtllm_fused_moe_runner.cu:285-312`: FC2 uses native dynamic metadata and writes its intermediate output. Finalize is a separate native step.
- `csrc/trtllm_fused_moe_runner.cu:352-373,469-485`: the complete native tactic combines independently compatible FC1/FC2 configs; enumeration checks each pair.
- `csrc/trtllm_fused_moe_kernel_launcher.cu:1602-1607`: supported BF16 token tiles are 8,16,32,64,128.
- `csrc/trtllm_fused_moe_kernel_launcher.cu:956-989`: the public candidate set centers around `num_tokens*top_k/num_local_experts`, including nearby tiles. This is a heuristic upper estimate under EP because it ignores how many input routes leave the local shard. Therefore our exhaustive sweep means every candidate returned by native enumeration, not every compiled cubin or every conceivable implementation.
- `csrc/trtllm_fused_moe_kernel_launcher.cu:1800-1826`: BF16 candidate enumeration applies that tile shortlist, then the runner's validity checks.
- `csrc/trtllm_batched_gemm_runner.cu:379-387`: GEMM reads `cudaDevAttrMultiProcessorCount` and forwards the full 148-SM count into `bmm.run`. NCU also records 148 for both BF16 GEMMs.
- `include/flashinfer/trtllm/fused_moe/RoutingKernel.cuh:47-109`: default eight-SM reservation belongs to cooperative routing overlap.
- `csrc/fused_moe/trtllm_backend/trtllm_fused_moe_routing_deepseek.cu:582-605`: small 32-token case uses the single-cluster routing path; large case uses cooperative routing with the reservation. The logged 140/148 setting is not a BF16 GEMM cap.
- `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py:146-154`: W4A16 explicitly uses `acc_dtype=cutlass.Float32`; native BF16 kernel names likewise carry `_Fp32_`. The accumulation precision is not a hidden advantage for W4A16.
- Native generated `BatchedGemmInterface.h:53-62` documents dynamic overlaunch bounds and early exit using `ptrNumNonExitingCtas`. Shape/workspace upper bounds are not evidence that every allocated padded row/expert is actually processed.

The generated native interface was read from the retained artifact cache, without modifying it:
`/root/.cache/flashinfer/cubins/1d145b82ac60add55ea213863523f12d63005651/batched_gemm-09795a1-31ee4e5/include/trtllmGen_bmm_export/BatchedGemmInterface.h`.

## Avoidable opportunities versus evidence

| Candidate concern | Evidence | Assessment |
| --- | --- | --- |
| Missing tuning or wrong cache reuse | 2852 successful profiles; cache hits outside tuning; actual-input sweep | Ruled out as the large gap's cause for 32/4096 |
| Statically caps BF16 GEMMs to 140 SMs | Native launch and NCU both use 148; reservation is routing only | Ruled out |
| Extra standalone activation kernel | BF16 FC1 has gather and SwiGLU fused | Ruled out |
| Reading all 32 experts at 32 input tokens | NCU DRAM is approximately the active 21-expert weight payload | No evidence; inactive experts are skipped |
| Register spills | 168/255 registers in the two BF16 kernels | High count alone is inconclusive; await explicit local-memory/spill metrics |
| Low token-tile utilization | 31 useful rows in 168 padded slots at 32 tokens | Real, but reducing unused MMA slots cannot by itself remove BF16 weight bandwidth cost |
| EP-aware native tile shortlist | Heuristic uses global routes divided by local expert count | Potential general improvement; no measured missed fast candidate in this workload |
| Native separate finalize | Adds a visible native output-reduction stage | Potential fusion work, with output/numerical contract tradeoffs; does not explain dominant FC1/FC2 gap |
| Different memory/storage precision | BF16 weight payload is 3.56x FP4+SF | Inherent to comparing pure BF16 with W4A16; not a BF16 kernel bug |

The NCU report's high memory utilization with close-to-minimal active weight traffic is currently evidence against filing a claim of a broken/suboptimized BF16 GEMM. A performance issue should identify a reproducible avoidable cost, not infer a defect solely from a cross-storage-precision comparison.

## Existing upstream issue search

Read-only public `gh` searches were made after selecting and verifying `zianglih`: `bf16 moe performance`, `TRTLLM BF16`, `B300 MoE performance`, `moe register spill`, and `bf16 slow`. No matching B300 BF16 performance/spill report appeared in these bounded queries. Relevant adjacent reports:

- [#3521](https://github.com/flashinfer-ai/flashinfer/issues/3521): SM90 CUTLASS BF16 versus Triton performance; different architecture/backend.
- [#3466](https://github.com/flashinfer-ai/flashinfer/issues/3466): B300 missing compatible BF16 cubin; compatibility, not a measured throughput issue.
- [#4157](https://github.com/flashinfer-ai/flashinfer/issues/4157): B200 BF16 one-token autotuning illegal address.
- [#4919](https://github.com/flashinfer-ai/flashinfer/issues/4919): B300 BF16 dynB production illegal address in small MTP/NextN shapes.
- [#3364](https://github.com/flashinfer-ai/flashinfer/issues/3364): BF16 stability and memory allocation; closed.

These issue reports do not establish a matching performance regression in the current H7168/I2048 benchmark. No issue was filed.
