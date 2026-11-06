# Native activation loader audit, frozen 13ca1475

Outcome: preserve Gather4. Direct cp.async128 and Blackwell LDG256 controls write the existing B shared-memory ring, preserve all arithmetic/SF layouts, and pass the bounded exact checks, but regress native NVFP4 FC1 at 8K and 16K. No production changes.

Environment: C1 fi-w4a4-dyn-n-1024, NVIDIA B200 GPUs0/6, nvcr.io/nvidia/pytorch:26.05-py3, CUDA13.2, CuTe DSL4.7.1. Frozen core 13ca1475d96839f3bf3c46699cc63204b4d3b409. Actual native DeepSeek routing, H7168/I2048, top-k8,32 local experts; FC1 logical M512/N128, physical M256 two-CTA MMAs with two channel tiles. Initial quantization and routing are prepared by the native benchmark. Ten warmups/100 cold-L2 CUDA graph CUPTI samples, isolated FC1 only.

## W4A16 source distinction

Retained split W4A16 explicitly materializes expert-sorted BF16 activations: `flashinfer-w4a16/flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16.py:454-464` calls `moe_permute(x,hidden_workspace)` and FC1 consumes `hidden_workspace` at468. Actual full-row copy is `csrc/nv_internal/tensorrt_llm/kernels/cuteDslKernels/moeUtils.cu:88-94`. Kernel regular TMA B is at `moe_w4a16_kernel.py:721-731,1415-1427`.

Mega BF16_NVFP4 also materializes expert-sorted GMEM within dispatch: `megamoe_kernel.py:491-501` views the GMEM l1_token_buffer; `token_comm.py:1182-1192` pulls source rows into SMEM;1300-1307 TMA-stores to expert-pool GMEM. Regular TMA B then consumes the pool at `megamoe_kernel.py:1029-1036`. The software pool name is not hardware L1. This copy is fused in Mega but still adds global payload write/read traffic.

Current blockscaled Gather4 maps original source rows directly into B SMEM, avoiding that global payload stage. Swap-AB/dynamic-N orientation and payload materialization are independent choices. Prior W4A16 activation-load alternatives were rejected (`w4a16_optimization_experiments.md:455-478`), but their regular-TMA/materialized input differs from this direct-gather control.

## Loader contracts

- Four lanes cover one128-byte logical B row; each lane loads32 naturally aligned bytes. Existing format K contracts produce a row stride divisible by32 bytes; probe harness enforces base/row alignment. No runtime fallback branch.
- LDG256 uses `ld.global.v8.b32`, supported on SM100+; PTX8.8 introduced this form. The access is32 bytes and requires natural alignment. [PTX ISA, ld](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-ld).
- Existing SW128 maps the two16-byte halves to separate shared addresses. The swizzle acts on the absolute shared address, including the128-byte-aligned B base; assuming a1024-byte-aligned base caused the first prototype's exact-check failures. Corrected prototypes passed. Failed smoke logs are retained as prototype-development history, not performance evidence.
- LDG256 uses one global load plus two STS128 writes, with generic-to-async proxy fence before producer arrival. Payload completion shares the existing SF cp.async ring and two-CTA relay; no extra global payload buffer or shared-memory stage.
- cp.async128 uses two16-byte copies per lane with the same row assignment and existing async completion.
- ldgprefetch issues all per-stage row loads before acquiring the shared ring, retains payload in registers, and stores after the existing A/SFA TMA and SFB copy issue.

## Exact checks

Each variant (`ldg256`, `cpasync128`, `ldgprefetch`) passes24/24 strict sentinel-reset byte comparisons against frozen Gather4: six supported dtype/SF combinations × quantized output or per-token BF16 × short/long K. Short K covers64/128, long K1536 FP4/768 FP8, routed tails133, nontrivial top-k8 mapping, and partial logical M512 channel tiles. Native phase cases also compare payload and SF bytes with a shared output allocation.

## Native isolated FC1 results

| Tokens/GPU | Order | Median us |
|---|---|---|
|16384/0|Gather4 → LDG256 → Gather4|284.0315 →389.8550 →284.2070|
|16384/6|Gather4 → cp.async128 → Gather4|281.1525 →297.5365 →284.4645|
|16384/0|Gather4 → LDG prefetch → Gather4|284.3675 →344.5270 →285.5515|
|8192/0|cp.async128 → Gather4 → LDG prefetch → Gather4|173.9675 →166.4310 →208.6875 →166.3040|

## NCU / machine code

NCU full-set native16K profiles (GPU6) and cubin/PTX are retained. SASS confirms `LDG.E.ENL2.256` and separate `STS.128`, with94 registers/thread,189312 bytes dynamic shared memory, and zero local spill sectors for all variants. These are profiler replay times, not replacement benchmark medians.

| Metric | LDG256 | cp.async128 | LDG prefetch |
|---|---:|---:|---:|
|NCU duration us|396.384|310.528|349.536|
|DRAM read MB|589.549|653.326|591.684|
|LSU global load requests|1568756|2040948|1568756|
|Long-scoreboard per issued instruction|12.5158|8.6112|10.2912|

The original LDG profile places4868 long-scoreboard samples at its first payload `STS.128` (load-use dependency), versus467 at the next row's first store. All four payload STS128 sites show zero excessive shared wavefronts. The aggregate shared-bank-conflict counter is therefore not evidence of B-store bank conflicts. Prefetch reduces the load-use penalty but remains substantially slower than Gather4. The greater LSU burden and synchronous register dependency, not reduced global vector width, explain why LDG256 alone does not help this kernel. The causal attribution is limited to these measured schedules; it is not a claim that every possible direct-load schedule is slower.

Raw100-sample JSONs, exact-check logs, NCU raw/source CSV, reports, PTX/cubin, scripts and source hashes are archived under `evidence/activation-loader-13ca1475`.
