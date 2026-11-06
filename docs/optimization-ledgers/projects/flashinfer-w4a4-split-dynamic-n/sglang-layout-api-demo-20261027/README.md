# SGLang integration demo for FlashInfer #7290

Local, unstaged design demo. No tests, lint, compilation, GPU validation or
benchmarks were run. The demo edits remain uncommitted and unpushed.

- SGLang checkout: `../sglang`, upstream main at
  `010eb729bea2b7ef2bcd572a72c171f75ad900fb`.
- Companion FlashInfer API: `../flashinfer-weight-layout-api-review`, clean at
  `c980f007`, published to PR #7290 as a single commit with the same source tree
  as the preceding `dd16512a` refactor.
  It contains the opt-in `swap_ab` refactor and preparation helper.
- The earlier `7ae6244d` PR state is archived in the fork before the squash.
  The published source checkout `../flashinfer` remains separate from this demo.

## Proposed caller interface

```python
from flashinfer.fused_moe import interleave_cute_dsl_moe_weights

# Checkpoint tensors already loaded on the execution device, in [up, gate]
# order. Block scales are still row-major.
w13_weight, w13_weight_scale = interleave_cute_dsl_moe_weights(
    layer.w13_weight.view(torch.uint8), layer.w13_weight_scale, swap_ab=True
)
```

The wrapper uses the same explicit choice:

```python
moe = CuteDslMoEWrapper(..., quant_mode=quant_mode, swap_ab=True)
```

FlashInfer selects the gated row grouping internally and permutes the weight
and its block scales together. `swap_ab=False` preserves the existing 64-row
layout and kernels on Blackwell/Rubin; `swap_ab=True` selects the optimized
16-row Blackwell layout and rejects unsupported architectures. This demo
explicitly opts into the Blackwell path in both preparation and execution.
The caller does not query a group size. The helper is only used for gated FC1; FC2 and non-gated FC1 keep their existing preparation.
Its input is canonical checkpoint data, not an already interleaved weight.

This proposal deliberately covers row interleaving only. SGLang keeps its
existing scale swizzle/MMA conversion, padding, parameter rebinding and reload
flow. Global/input scales and quantized values are unchanged. The helper works
on the shared weight layout used by static NVFP4, per-token NVFP4 and W4A16.
W4A16 already uses activations on B; the flag selects its matching weight
layout so phase-selective W4A4/W4A16 can keep sharing one prepared weight set.

`CuteDslConfig.prepare_weights()` already hides row grouping for BF16 inputs,
but it also quantizes them and derives scales. SGLang loads quantized checkpoint
weights with calibrated scales, which is why this demo adds a layout-only API.
A larger prequantized-weight preparation API could additionally own scale
swizzling and MMA conversion; that would require moving more of SGLang's
padding and derived-parameter lifecycle across the boundary.

## Upstream SGLang changes

- `modelopt_quant.py`: replace its hardcoded 64-row interleaving with the paired
  FlashInfer call. Existing parameter rebinding remains in place.
- `moe_runner/flashinfer_cutedsl.py`: remove the now-unused local row interleaver
  and select `swap_ab=True` when constructing either phase wrapper.
- Existing standard-v2 test fixtures: prepare the quantized payload and scales
  through the same public helper. The numerical reference stays independent;
  no new test cases are added or executed.

The ModelOpt change also covers `NvFp4OnlineFusedMoEMethod`, which inherits this
postprocessing, and the phase-selective W4A16 path that shares these weights.

DeepEP's masked CuTe path uses plain `[gate, up]` halves and stays unchanged.
SGLang's dense fused SwiGLU implementation keeps its own 64-row contract.
MegaMoE and TRTLLM preparation are separate paths. Current SGLang MXFP4 dispatch
uses TRTLLM/CUTLASS, and its FP8 CuTe selection redirects to Triton; wiring those
to the new split backend would be a separate feature.

## Review boundary

The new helper is a proposed API, available only in the companion review copy.
SGLang will need a FlashInfer version containing it before these edits can ship.
No dependency pin is changed for this demo. Existing 64-row prepared weights
remain valid with `swap_ab=False`. Switching
to `swap_ab=True` requires rebuilding weights from canonical checkpoint rows;
raw tensors have no tag that lets the wrapper infer their row semantics.
The eventual SGLang opt-in/configuration surface is a design decision; this
demo does not add a new environment variable or change a dependency pin.

```bash
git -C ../sglang diff
git -C ../flashinfer-weight-layout-api-review diff
```
