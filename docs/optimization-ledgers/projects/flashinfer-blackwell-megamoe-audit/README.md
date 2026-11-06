# FlashInfer Blackwell MegaMoE status audit

Checked upstream on 2026-09-07. Read-only research; no GPU benchmarks rerun.
Source checkout: `flashinfer/`, main `91bda04c66f7cb851e1ab3b78b9fecea644b9844`.
Latest published release observed: `v0.6.18.post1`, published 2026-09-05.

## Assessment

The expert-parallel fused communication and compute path is shipped and usable
for pinned serving integrations. Performance evidence favors large prefill;
decode depends on workspace sizing, graph coverage, and tuning. The public
entry point is established, but configuration names are being migrated and
serving behavior is still being refined.

## Primary evidence

- Release history: https://flashinfer.ai/releases/
  - v0.6.16 (July 31): MegaMoE backends shipped.
  - v0.6.17 (August 11): graph capture, fused quantize/stage, prequantized
    weights, pooled symmetric workspaces, persistent offline knob cache.
- Framework readiness and historical vLLM benchmarks:
  https://github.com/flashinfer-ai/flashinfer/pull/4079
- Benchmark methodology and complete raw tables:
  https://github.com/flashinfer-ai/flashinfer/blob/91bda04c66f7cb851e1ab3b78b9fecea644b9844/flashinfer/moe_ep/kernel_src/cutedsl_megamoe/TUNING.md
  - July 22 microbench, 4x GB200 EP4, DSV3-like H7168/I2048/E256/K8:
    8192 tokens/rank: DeepGEMM FP8xFP4 3072.9 us; CuTeDSL NVFP4xNVFP4
    BF16 combine wire 1896.4 us (1.62x); NVFP4 combine wire 1655.3 us (1.86x).
    8 tokens/rank: 215.0 / 222.2 / 228.3 us respectively.
    `e2e_pipelined` stages input once outside timing, so it excludes activation
    quantization and staging. These are different compute/wire precision points.
  - Historical vLLM 0.25.1 integration, DSV4-Flash 4x GB200 TP4/EP4:
    native 45701 -> FI NVFP4 53962 prefill tok/s; native 21049 -> 22614
    output tok/s at 1024-sequence decode concurrency. Native uses MXFP4
    checkpoint; FI NVFP4 uses NVFP4 checkpoint and BF16 combine wire.
    Requires graph coverage including prefill chunks and per-role tuned caches.
  - MXFP8 W8A8 does not share the NVFP4 speedup: 0.63/0.82/0.88/0.96x
    DeepGEMM FP8xFP4 at 1024/2048/4096/8192 tokens/rank; higher precision.
- API rename, merged August 14, deprecated aliases retained for future removal:
  https://github.com/flashinfer-ai/flashinfer/pull/4449
  Example: `Nvfp4CutedslMegaMoeConfig` ->
  `Sm100_Nvfp4_Nvfp4_Bf16_Cutedsl_MegaMoeConfig`.
  Public flow remains MoEEpLayer + MegaConfig, warmup on all ranks, forward.
- vLLM DSV4 integration merged August 25, opt-in, FI >=0.6.17:
  https://github.com/vllm-project/vllm/pull/49636
- Generic vLLM CuTeDSL integration still open:
  https://github.com/vllm-project/vllm/pull/54049
- SGLang FI MegaMoE integration still open:
  https://github.com/sgl-project/sglang/pull/31470
  Existing SGLang `megamoe` calls DeepGEMM, not this integration.
- Open mixed-prefill/decode workspace performance issue:
  https://github.com/flashinfer-ai/flashinfer/issues/4727
  September 4 clarification asks that reduction work scale with actual tokens;
  it does not require changing the workspace API.
- SM100 BF16 MegaMoE merged to main August 19:
  https://github.com/flashinfer-ai/flashinfer/pull/4386
  Do not infer a matched-precision BF16 serving speedup from quantized comparisons.

## Scope boundaries

MegaMoE here means fused EP dispatch, expert FC1/activation/FC2, and combine.
Local `cute_dsl_fused_moe_nvfp4` / W4A16 performance is a separate operator.
GB200 benchmark results are not fresh B300/EP64 or GLM workload evidence.
Kernel numerical-reference tests and a small GSM8K sample do not establish
model-wide numerical equivalence across all quantization/combine settings.
