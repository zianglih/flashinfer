# Nemotron-3 Ultra routed-expert benchmark

The `nemo3-ultra` preset uses routed-expert latent width **2048**, intermediate width **5120**, **512** experts, **top-22**, EP8 (64 local experts), and **ReLU²**. Model hidden width 8192 belongs to the router and latent projections; those operations, shared experts and communication are outside this local routed-expert benchmark.

Sources are pinned and hashed in `sources.json`. The HF model repository contains config/weights rather than a custom model implementation. The official Transformers Nemotron-H implementation supplies the expert/router semantics:

- `config.json` fixes `moe_latent_size=2048`, `moe_intermediate_size=5120`, `n_routed_experts=512`, `num_experts_per_tok=22`, `mlp_hidden_act=relu2`, `norm_topk_prob=true`, `routed_scaling_factor=5`, and one routing group.
- `modeling_nemotron_h.py:667–702` allocates up `[E,I,latent]` and down `[E,latent,I]`, with no gated second projection. Lines734–750 place latent projections outside the routed experts.
- Lines773–794 choose experts from sigmoid(logits)+bias, gather the unbiased scores, normalize by their sum+1e-20, then multiply5. With one group, group masking removes nothing. The benchmark reuses its deterministic CPU sigmoid routing outside timing. It orders selected experts with stable descending argsort (lower-ID ties); the source uses unsorted topk. Selected sets/weights agree absent ties; this is not a claim of identical slot order or checkpoint/RNG inputs.
- `activations.py:206–214` implements `relu(x).square()`, matching public `ReLU2` / native activation enum6.

## Implementation boundary

Only `benchmarks/bench_moe_deepseek.py` changes. GEMM1 row count and reported GEMM FLOPs now distinguish gated from non-gated activations. Both public CuTe call paths and every TRT preparation/runtime path receive the requested activation. Standard table order, timing helper, initial-quantization opt-in, per-token recipe, native AUTO workflow and saved-cache behavior remain unchanged.

CuTe NV weight preparation now uses the public source-native `CuteDslConfig.prepare_weights`, as MX already does. This naturally uses old64/current16 gated-row layouts without copied constants or version branching; ReLU2 skips interleaving in both versions. The benchmark no longer preemptively rejects fused MX: each source's actual API enforces its own capability. Comparison orchestration chooses old native fused MX where necessary and current unfused MX. Old K3 MX SiTU remains unavailable in that old implementation.

Current source capability declarations admit ReLU2 for all five CuTe table arms and all TRT table arms (NVFP4, per-token NVFP4, MXFP8, MXFP4x8, BF16). Existing TRT tests include per-token ReLU2 and MXFP8 ReLU2 top22. This is source-level API support, not a new GPU kernel-availability result. Explicit-only CUTLASS remains unavailable for ReLU2 because this benchmark arm implements only SwiGLU; its implementation is unchanged.

The comparison must keep ambient legacy `FLASHINFER_NVFP4_4OVER6` off/unset and both base fastmath-disable aliases0 during shared weight preparation. Public weight preparation internally uses the quantizer's default recipe lookup. Dedicated per-token activation quantization still uses the explicit256/MSE/fastmath recipe, inverse1/(256*6), and its scoped base-fastmath override. No new numerical changes were made to existing TRT NV scalar preparation.

## Validation

- Scoped repository pre-commit and Python compilation pass.
- `base3-checks.json`: all other functions/classes AST-identical at the compatibility snapshot; four old/current × W4A4/W4A16 public-preparation checks reproduce manual quantizer inputs and scale-layout calls exactly.
- `nemo-checks.json`:65 CPU contract checks cover pinned config, routing/caching/ties, shape/FLOP changes, exact existing-model seeded inputs and dispatch/table bytes, explicit activation kwargs, CLI EP defaults, opt-in quantization, unknown-activation rejection, and unchanged timer/route/format ASTs.
- `nongated-pack-checks.json`:eight source-extracted old/current × four-format preparations prove no interleave, exact BF16 quantizer inputs, and correct non-gated pack shapes. Quantizers/layout conversion are stubs; no GPU payload correctness is claimed.

No GPU run, source commit or push was performed by this task. Frozen source and patch hashes are in `benchmark-source.json`; `benchmark-base3.py` is the immutable earlier compatibility snapshot for parallel three-model comparisons.

## MX fused parser correction

The old native functional MX fallback is now allowed through the benchmark CLI. Only the obsolete fused-finalize parser rejection and its two help-text clauses were removed; every non-main AST is unchanged. Both functional fused and unfused MX modes reach existing dispatch in the CPU fixture. Initial snapshots and receipts used by the failed runtime smoke are preserved in `before-mx-parser-fix/`. The original preparation proofs remain historical and their preparation bodies are unchanged. No backend kernels were patched.
