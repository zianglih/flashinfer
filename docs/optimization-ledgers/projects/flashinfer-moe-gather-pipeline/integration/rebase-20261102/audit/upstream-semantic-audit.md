# PR7290 upstream audit

Audited the retained `a620ce7790b32f7f0ae524a811417d2c6cee1152` delta from
`002529e17b22567a071091053c6c4dc2a55e050e` against upstream `e29bf6d52`.
Read-only audit; no canonical source changes. Exact intersecting file/commit
inventory is in `upstream-overlap.json`.

## Required semantic integration

- **ClampedRelu2 (#7286, `8a645b6a5`)** adds a runtime `(1,)` FP32 CUDA tensor
  `clamped_relu2_limit` through public functions, wrapper, generic tuner and the
  legacy Blackwell blockscaled gather launcher. It adds validation and reads the
  limit after PDL wait; its value deliberately stays out of compilation and
  autotuning cache keys. Preserve the complete legacy path and tests.
- The new swap-AB kernel still implements Swiglu, GegluTanh and Relu2 only.
  Its constructor explicitly rejects other activations (so it cannot silently
  produce plain Relu2). The globally expanded normalizer now accepts
  ClampedRelu2. If scope remains unchanged, reject ClampedRelu2 early for swap-AB
  using the existing support guard and leave new-activation support to separate
  work. Do not pass `clamped_relu2_limit` unconditionally into the swap launcher,
  whose signature has no such parameter. The public/runner/core argument wiring
  must preserve the upstream legacy call's limit tensor while swap-AB remains
  callable with normal activations.
- **Rank-invariant persisted keys (#6139, `9ef2e8884`)** removes
  `local_expert_offset` from `get_cache_key_extras` in both blockscaled and
  W4A16 runners. Preserve these removals, including the swap-AB branch of the
  generic runner. Reintroducing the offset can deadlock distributed autotuning
  when only the publishing rank hits the cache. Do not remove the offset from
  runtime routing; upstream only changes persisted cache keys.
- **W4A16 ClampedRelu2 rejection** must preserve upstream's narrower
  `W4A16_CUTE_DSL_MOE_ACTIVATION_TYPES` normalization in the launcher and tuner,
  plus the public API error. This does not change supported W4A16 arithmetic.

## Independent upstream changes to retain unchanged

- #6832 (`8ab3a4965`): Prims-TS Rubin/localized execution, partitioned exports,
  supported activations, trace definitions and common test helper changes.
  These overlap shared files but not the new swap-AB implementation.
- #8050 (`645783136`): export `populate_trtllm_moe_routing_metadata_`; no
  swap-AB helper or benchmark contract changes.
- #7459 (`3043489e8`) and #7838 (`f416759b9`): documented routing-ID validity
  and Frost-specific behavior in `api.py`. Preserve alongside swap-AB docs.
- #6853 (`ddf3e7bc1`): cuDNN grouped-MoE offset-boundary docs in runners.
- `cute_dsl/availability.py`: cached capability query for an indexed CUDA
  device; equivalent admission behavior for this SM100/SM103 backend.
- `tests/test_helpers/utils_fp4.py`: allows FP32 MXFP4 oracle input in addition
  to FP16/BF16, no changed numerical formula for existing inputs.
- Upstream packaging and pre-commit changes concern other backends. Preserve
  their configuration without adding unrelated adjustments. The pytest marker
  change only handles native Rubin availability; C3 Blackwell is unaffected.

No intervening upstream changes touch the shared Blackwell custom pipeline,
finalizer, W4A16 kernel/dequantizer, per-token NVFP4 quantizer, 4over6 helpers,
or MegaMoE BF16/NVFP4 kernel. Those retained implementations should remain
byte-identical through rebase unless an independently justified follow-up is
needed.

## Targeted validation

- Existing zero-tolerance swap-AB and W4A16 accuracy cases, including MX modes,
  per-token quantization, gated/nongated activation, and legacy/new W4 layout.
- Existing upstream ClampedRelu2 validation and GPU accuracy/runtime-limit
  tests on the non-swap path; preserve tests for W4A16 rejection.
- Existing rank-invariant cache-key test for both runners. Parameterizing it
  for `swap_ab=False/True` would cover the new mode without a standalone test.
- Changed-file hooks plus AST/signature inspection of public wrapper, runner,
  internal core and trace handoff. Do not treat old performance data as a fresh
  benchmark of the rebased source.

## Rebased result and follow-up implementation

The single rebased commit is `b17f941056c36ccca799a7fd84d4cd3aa65a0b15` on
`e29bf6d52`. Reviewed public/wrapper/core/runner ClampedRelu2 handoff, test
merges, trace changes, and persisted cache keys. No semantic conflict-resolution
miss was found. The listed shared kernels/utilities, quantizer, and swap-AB
tactics remain byte-identical to retained a620 at this commit.

The user subsequently requested closing the ClampedRelu2 gap rather than
rejecting swap-AB. That supersedes the narrow rejection recommendation above.
A separate follow-up now adds support in `moe_swap_ab.py` and
`moe_swap_ab_kernel.py`: runtime Float32 limit pointer, upstream validation,
limit/reciprocal load outside the persistent loop after existing PDL wait, and
packed RN scaling/tanh.approx/ReLU/square in the nongated FC1 epilogue. Existing
CLC, phase retirement, quantization and FC2 paths are unchanged. No clamp value
is added to the specialization key. Python compilation, Ruff and diff-check
passed; C3 exact/runtime tests remain the required validation.

The trace reference originally used `activation != Relu2` to detect gated
weights, which would misclassify ClampedRelu2. The root agent changes this to
the actual enum gatedness and extends the shared approximate trace oracle's
clamp handling. Reviewed that proposed handoff; it uses the alpha-folded FC1
result and the runtime tensor without interleaving nongated weights.
