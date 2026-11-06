# Old CuTe DSL comparison: source and compatibility

Source audit on 2026-10-27; no GPU run or production source modification. This
records the final requested policy: current is unfused; old uses unfused where
supported and its native fused finalize where required. It supersedes the
earlier all-unfused proposal.

- Current: `0b7fe90151340d4fca6a5ec41a91019dde743819`, `../flashinfer`.
- Old: `002529e17b22567a071091053c6c4dc2a55e050e`, clean detached independent
  checkout `../flashinfer-old-cute-baseline`. This is the exact merge base.
- The first replacement commit is `c9b840ba58219d97ed14b475d45c30c02dacd3ae`.
  The baseline already includes upstream MXFP8 wiring (`b92f1129`), W4A16/
  deterministic combine #7196 (`03d7f4a3`), and quantization #7501 (`fb022756`).
- `baseline-provenance.json` pins audited file SHA256 values, Git trees,
  source status, and CPU-only API/layout checks. The old checkout has no patches.

## Native support

All entries below are source-supported, pending the campaign's runtime admission
and correctness checks. The same canonical inputs/routes must feed both arms.

| Model | D / I / experts / top-k / EP | Activation | Old NVFP4 | Old per-token NVFP4 | Old MXFP4x8 | Old MXFP8 | Current four formats |
|---|---|---|---|---|---|---|---|
| V3 | 7168 / 2048 / 256 / 8 / 8 | SwiGLU | Unfused | Unfused | Fused | Fused | Unfused |
| V4.1-Flash | 5120 / 2304 / 384 / 6 / 4 | SwiGLU, limit 10 | Unfused | Unfused | Fused | Fused | Unfused |
| Kimi K3 | 3584 / 3072 / 896 / 16 / 8 | SiTU 4, linear scale 25 | Unfused | Unfused | N/A: SiTU | N/A: SiTU | Unfused |
| Nemo3 Ultra | 2048 / 5120 / 512 / 22 / 8 | ReLU2 | Unfused | Unfused | Fused | Fused | Unfused |

The Nemo values are the requested routed-latent-expert workload, not a claim
that this times the model's surrounding latent projections.

Old `flashinfer/fused_moe/cute_dsl/fused_moe.py:438–445` rejects per-token MX,
non-BF16 MX output, unfused MX, and MX SiTU. This applies to both weight formats
because the dispatch tests MXFP8 activation dtype. The public runner repeats
these restrictions in `flashinfer/fused_moe/runners.py:4961–5034`.
NVFP4 supports SiTU and ReLU2; the old FC1 kernel implements non-gated
`max(alpha * acc, 0)^2` at
`blackwell/blockscaled_contiguous_gather_grouped_gemm_act_fusion.py:2772–2799`.
SiTU's gate and optional smooth linear clamp are at `2818–2899`.

All four requested D/I pairs meet the 128-element mixed-format alignment;
Nemo's I5120 is divisible by the existing 128/256 FC1 channel tiles. Its
non-gated FC1 has I rows, not 2I. The old tuner derives this from the activation
and weight rows (`tuner.py:766–775`), and existing `moe_unpermute` iterates an
arbitrary positive top-k (`blackwell/moe_finalize.py:133–163,210`). No top-k22
rejection was found in this path; runtime validation remains necessary.

## Benchmark overlay boundaries

The current benchmark cannot run unmodified on the old source:

1. It imports `_cute_dsl_gated_weight_group_size`, which does not exist upstream.
   Its current manual NVFP4 packing uses new Blackwell 16-row gate/up groups.
   Old native weights use 64-row groups. Copying the new helper or prepared
   weights into the old source would silently violate the old epilogue layout.
2. Its MX argument guard currently requires unfused. Permit the requested old
   native fused arm in the benchmark overlay only. Do not remove the old API's
   support checks or change its kernel.
3. Its input generation, FLOP count, manual packing and activation kwargs
   currently assume gated SwiGLU/SiTU. ReLU2 needs I FC1 rows, no interleave,
   `activation=ReLU2()` in weight preparation and
   `activation_type=ActivationType.Relu2.value` in the wrapper/functional API.

Use each checked-out source's public `CuteDslConfig.prepare_weights` for all
formats. This public config class is AST-identical between the two commits.
Pass the same canonical BF16 expert weights, quant pair and model activation.
It selects the source-native gate/up layout and native scale packing. The
underlying `_interleave_linear_and_gate` and `convert_sf_to_mma_layout` functions
are AST-identical; only the chosen gated group differs (old64/current16 on
Blackwell). CPU row-index checks prove both permutations are bijective for all
four intermediate sizes. ReLU2 bypasses the permutation in both sources.

Keep weight preparation outside the per-token fast-math scope. Both public
preparers call `fp4_quantize` without explicitly overriding the ambient 4over6
environment; therefore clear recipe environment variables during preparation
and record that environment. The `nvfp4_4over6` argument on preparation selects
`fc2_input_scale` only. For the per-token arm, explicitly pass the same
`NVFP44Over6Config(e4m3_max=256, err_mode="MSE", err_use_fast_math=True)` to the
input and intermediate activation quantizers; disable base FP4 fast math in
that activation scope. Standard weight quantization must remain standard.
Current manual weight packing explicitly uses `nvfp4_4over6=None`; public
preparation matches it when ambient recipe selection is off.

Use native AUTO independently in each source with new source-specific winner
caches. Old raw enumeration is 16 NVFP4 tactics or 48 MX tactics, then normal
shape admission; tuples have the old three-field format. Do not overlay the
current tuner, five-field cache entries, scheduler observer assumptions, or
low-level launch helpers. The experiment is a public API backend comparison,
not a fixed-tactic kernel replacement measurement. Keep common random seeds,
canonical input/route hashes, activation inclusion, timing and device fixed.

## Numerical and finalizer boundaries

- NVFP4 standard keeps FP32 FC1 activation values through inline FP4 conversion
  in both implementations, but old inline scale arithmetic differs from the
  current shared standalone-standard helper. Do not claim bit-exact old/new
  outputs from equal dtype/recipe alone. Both intentionally keep standard,
  rather than per-token 4over6, FC1 inline quantization.
- NVFP4 per-token writes BF16 FC1 activation then uses the native standalone
  per-token quantizer with the pinned recipe. The current quantizer's launch,
  PDL and live-row handling differ from old; retain those differences in the
  source-native end-to-end comparison, including initial quantization.
- Both MX modes emit E4M3 FC1 values with E8M0 block32 scales. The old FC1
  implementation explicitly uses standalone-compatible E8M0 conversion and
  inverse scale (`gather...py:3135–3180`). Initial MX quantization stays outside
  the measured prequantized MX closure in both sources.
- **Old fused MX:** zero output, multiply each FP32 FC2 expert accumulator by
  its routing/expert scale, convert that contribution to BF16, then bulk atomic
  BF16 reduction into the token output (`fused_moe.py:787–804`, old
  `grouped...py:1980–2020,2159–2236`). Reduction order is not deterministic.
- **Current unfused MX and both unfused NV arms:** materialize BF16 expert
  outputs, then deterministic top-k-ordered FP32 multiply/FMA reduction and
  final BF16 conversion. Old already has the #7196 FMA combine contract
  (`blackwell/moe_finalize.py:143–163`); current optimizes its implementation.
  Old MX fused versus current MX unfused therefore differs in intermediate
  rounding and reduction order, as well as launch structure. Label this
  native-path comparison explicitly; use tolerant correctness, not a zero
  tolerance assertion between these two backend arms.

## Cache reuse

Git trees are identical for `csrc`, `include`, `flashinfer/jit`, `3rdparty`,
`pyproject.toml`, version files and `flashinfer/artifacts.py`; their exact object
IDs are in the receipt. Thus this PR does not require rebuilding unchanged
native C++/CUDA artifacts. Reuse only a native cache verified against that
source/toolchain/architecture/flag identity. Keep CuTe DSL compilation and
native AUTO winner caches separate by source, since the Python kernels,
geometry, quantizer and public cache keys differ. No claim about a particular
remote cache's contents is made by this local audit.
