## Scope

@humansand

Track implementation and follow-up work for the SM100-family CuTe DSL NVFP4 MoE path with BF16 activations (`quant_mode="w4a16"`). #4249 captured the original B200 W4A16 feature request; this issue consolidates the implementation, integration, and related follow-ups.

This tracker is limited to work with explicit W4A16 scope. General CuTe DSL / NVFP4 infrastructure and activation quantization are omitted unless they directly enable or modify this path.

Status last updated: 2026-11-04 (UTC). Checked items are merged or concluded; unchecked items remain open.

## Tracked contract

- **Hardware:** SM100-family CuTe DSL path; validation in the linked PRs covers B200/SM100 and B300/SM103 where documented.
- **Precision:** BF16 activations and block-scaled NVFP4 weights.
- **Path:** `cute_dsl_fused_moe_nvfp4` / `CuteDslMoEWrapper`, including eager and CUDA graph execution plus fused and deterministic finalize modes.
- **Out of scope:** dense W4A16 GEMM implementation, SM12x/b12x kernels, and the TRT-LLM MoE backend. Related SM100 dense work is linked below for context.

## Shared foundations

- [x] #3976 — `feat(moe): add deterministic CuTe DSL NVFP4 finalize mode` — Adds the reusable deterministic `moe_unpermute` path that #4048 explicitly builds on.
- [x] #4192 — `fix(moe): serialize CuTe DSL autotune replay` — Fixes a shared CuTe DSL MoE runner deadlock hazard during selected-tactic replay; this is not W4A16-specific, but applies to the runner reused by W4A16.

## Core implementation

- [x] #4048 — `feat(moe): support BF16 activations in CuTe DSL NVFP4 MoE` — Adds the explicit W4A16 mode, dedicated online NVFP4-to-BF16 weight decode and kernels, runner/API integration, autotuning, fused and deterministic finalize, PDL/CUDA graph support, tests, and B200 evidence.

## Direct follow-ups

- [x] #4394 — `feat(moe): support GeGLU and SiTU in W4A16` — Adds GeGLU-tanh and SiTU, including parameter plumbing and autotune/compiled-kernel cache identities.
- [x] #4558 — `fix(moe): release W4A16 CuTe DSL scratch workspaces` — Removes per-runner scratch retention that can cause multi-GiB serving memory retention/OOMs while preserving eager allocator reuse and CUDA graph ownership. Merged.
- [x] #4540 — `perf(moe): fold W4A16 SiTU reciprocals` — Replaces trace-time per-element divisions with FP32-rounded reciprocal multiplies and adds controlled B200 evidence. Merged.
- [ ] #4366 — `feat(moe): support input-side router weights in CuTe DSL W4A4/W4A16 MoE` — Adds opt-in pre-FC2 router-weight placement for cross-stack numerical alignment. Open.
- [ ] #4678 — `perf(moe): prune score-routing compilation from moe_utils` — Uses source-owned post-topK wrappers to prune unreachable score-routing compilation from the shared SM10x CuTe DSL W4A4/W4A16 `moe_utils` JIT while retaining the existing routing/permutation kernels. Fresh B200 cold first-run wall time drops from 244.03 s to 121.28 s for W4A4 and from 245.19 s to 120.99 s for W4A16; open draft, built on merged #4082.
- [x] #5186 — `perf: reduce split W4A16 routing and output overhead` — Specializes top-k and physical-cluster feature bounds and improves non-fused expert scratch stores, preserving fixed-order FP32 combine. Includes separate fused/non-fused B300 performance tables for 1–8192 tokens. Merged.
- [x] #5019 — `feat(moe): add CuTe DSL NVFP4 W4A16 MegaMoE` — Adds fused expert-parallel dispatch, FC1/SwiGLU, FC2 and token return with BF16 activations, online NVFP4-to-TMEM weight decode, and fixed-order FP32 combine. Includes CUDA 13.2/B300 performance results for 1–8192 tokens. Merged.

- [x] #5319 — `perf: optimize CuTe DSL W4A4 and W4A16 unfused finalize` — Shares a vectorized BF16 finalizer with ordered FP32 reduction and overlaps standalone finalize setup with FC2 through PDL. B300 simulated-EP8 results cover 1–16384 tokens: W4A16 improves at 14/15 points, with a 1.22% regression at 8192. Also fixes CUTLASS benchmark finalize-flag forwarding. Merged.

- [x] #6277 — `Add small-shape W4A16 MegaMoE tactics and model benchmarks` — Performance optimization follow-up to #5019: adds N32 paths and a 16-tactic autotune catalog, plus Kimi K3, DeepSeek V4.1 Flash and GLM5 benchmark presets. Preserves activation numerics and deterministic combine. Merged (verified 2026-10-16).

- [x] #7196 — `perf: optimize split CuTe DSL W4A16 MoE and add bit-exact MoE/GEMM tests` — Uses live routed-token counts for runtime MMA N while retaining existing split MoE tactics. Aligns activation and standalone combine rounding with MegaMoE and shares a bit-exact, zero-tolerance reference across split MoE, MegaMoE, and full-K dense CuTe DSL W4A16 GEMM tests. Includes B300 before/after results for simulated EP8 and distributed Kimi K3/SiTU. Merged.

- [x] #7290 — `Add swap-AB mode and bit-exact testing to split CuTe DSL MoE` — Moves W4A16 BF16 input gathering into FC1 for both the original 64-row and swap-AB 16-row gated weight layouts, removing standalone input permutation while preserving the W4A16 tactic set and shared exact reference. Adds weight-layout validation and autotuning coverage for both layouts. Merged; the B200/B300 small-token EP regressions and planned follow-up are documented in the PR.

## SGLang integration

- [x] [sgl-project/sglang#35120](https://github.com/sgl-project/sglang/pull/35120) — `feat: add FlashInfer CuTe DSL NVFP4 W4A16 mode` — Adds opt-in W4A16 dispatch through `CuteDslMoEWrapper(quant_mode="w4a16")`, supports no-A2A and FlashInfer A2A on SM100/SM103, and adds online-quantized Nemotron-3 plus serialized ModelOpt Qwen3 coverage. Merged; depends on FlashInfer #4048, #4394, and #4558.

The original https://github.com/sgl-project/sglang/pull/39210 was split into two PRs, both merged:

- [x] https://github.com/sgl-project/sglang/pull/43789 — Startup autotuning for MegaMoE, including capacity-specific profiles and autotune cache/workspace ownership.
- [x] https://github.com/sgl-project/sglang/pull/44036 — Opt-in NVFP4 W4A16 for `flashinfer_megamoe` with serialized ModelOpt weights and `nvfp4_online`, reusing `SGLANG_FLASHINFER_CUTEDSL_NVFP4_W4A16`. Adds BF16 activations/EP transport/combine, shared W4A4/W4A16 weight reload, and SiTU/Kimi K3 wiring on top of FlashInfer #5019.

## Related dense W4A16 work

- [x] #4466 — `feat: sm100 cute_dsl w4a16 gemm` — Adds a dedicated SM100/SM103 CuTe DSL dense BF16-by-NVFP4 kernel, architecture-specific weight preparation and dispatch, and autotuning. The implementation adapts the W4A16 MoE TCGen05/dequantization design and tactic family while retaining a separate dense ABI and scheduler. #3597 established the earlier public dense API and cuDNN/SM12x foundation. Merged.

- [x] #4686 — `perf(gemm): optimize CuTe DSL W4A16 dense GEMM` — Compiles the SM100/SM103 kernel at O3 and expands all 15 structural tactics across both raster directions. Controlled B300/SM103 A/B/A measured `1.029759x` geometric-mean speedup across the #4466 shape matrix (`0.996866x`–`1.060623x`). Merged.

## Concluded experiment

- [x] #4424 — `perf(moe): persist SM100 CuTe DSL kernels to disk cache` — Evaluates persistent disk caching for W4A4 and W4A16. Closed without merge; measurements and design tradeoffs are documented in the PR.

## Related issue

- #4249 — Original B200 W4A16 feature request, closed after the core implementation landed in #4048.
