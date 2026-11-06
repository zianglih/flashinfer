# Model-shape and pipeline-capacity follow-up

Starting PR source: `63d5fa0ea1c60e49242970e7721f0581e41c267a`.
The benchmark-only edit is in `flashinfer-pr-scope-review`; kernel experiments
remain unstaged in `flashinfer-stage-capacity-review` until retained.

## Workload contracts

- V3: H7168 / I2048 / E256 / top-8, grouped sigmoid routing (8 groups, top-4
  groups), route scale 2.5, ordinary SwiGLU, simulated EP8 / TP1.
- V41-Flash: H5120 / I2304 / E384 / top-6, global sqrt-softplus routing,
  normalized unbiased weights with route scale 1.5, SwiGLU gate capped at +10
  and up clipped to [-10,10], simulated EP4 / TP1. The official source is
  pinned in `evidence/v41-model-contract/receipt.json` at HF revision
  `314113f8a7dadb388215396ba5fbee2c610a04d6`.
- V41 follows the existing distributed benchmark: precomputed common routes
  are excluded from timing because the native TRT routing enum has no
  sqrt-softplus option. All backends receive the same routes. Keep V3 native
  logits-inclusive measurements unchanged and label the distinction.
- MXFP table ratios compare CuTe with TRT in the same quantized dtype only;
  the TRT BF16 reference remains as requested. No cross-quantized-dtype winner.

## Measurement and retention

Use all 13 token points: 1,2,4,8,16,32,64,128,256,512,4096,8192,16384.
Use fresh native AUTO, 10 warmups, 100 cold-L2 CUDA-graph CUPTI iterations,
per-tensor NVFP4 and unfused CuTe finalize; native TRT finalize stays native.
Exclude 1/2 only from retention aggregates. Keep original historical baseline
measurements; do not reconstruct final speedups by multiplying incremental
ratios. Record exact source and full-precision medians before retention.

The currently running V3 two-table sweep at63d5 remains evidence of that source,
not automatically evidence for later buffer-policy edits.

## Capacity audit

The present wrappers choose fixed3/4/5 operand stages by tile geometry. The
experiment calculates allocation from actual CuTe layouts, metadata alignment,
epilogue scratch, and architecture-specific shared-memory capacity. Preserve
working TMA output buffers and consider persistent cross-tile prefetch before
capping by the reduction extent. Rubin has separate existing capacity-derived
policies and must not inherit a hardcoded Blackwell limit.

H is smaller for V41, but its local expert count is96 (versus32 for V3EP8),
and I is2304 (versus2048). Thus this is a distinct local-shard workload, not a
uniform scaling-down of V3; per-expert shape, active-route density, and weight
traffic all matter when evaluating tactics.
