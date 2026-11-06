# Public API benchmark transition and final evidence

The benchmark now needs to exercise the same public function or wrapper a
caller uses for every format. The candidate exposes homogeneous MXFP8 as
`quant_mode="w8a8"` and admits unfused W4A8. It removes benchmark-owned
sort/FC1/FC2/combine assembly and all private prefetch decisions. The public
library owns those policies; experiment-only observers may inspect them but
must not change them for final timing.

## Compatibility gate

Before timing, compare the frozen8b74 assembly and the new function/wrapper:

- Same canonical BF16 inputs, quantized payloads and block scales, routing
  values/ids, model configuration and global scales. Use the existing public
  weight preparation helper; explicitly verify its output against the old
  CUDA quantization and MMA-scale-layout path.
- Same supported tactic set for each actual geometry, packing factor and
  output type. W8A8 has one byte per weight; W4A8 has two FP4 values per byte.
  Cache identities distinguish these modes.
- Same selected explicit geometry, launch order, dependency flags and output
  for both function and wrapper, including small/large route tiles, two CTAs,
  nonzero expert offset and zero local routes.
- Preserve graph autotuning for MX modes. The wrapper's existing
  `use_cuda_graph` controls auxiliary resource lifetime; the new direct
  `autotune_use_cuda_graph` controls the tuner and defaults false, preserving
  existing NV behavior. Timing remains10 warmups and100 cold-L2 CUDA-graph
  CUPTI samples, fresh AUTO without loaded tactics.
- The exact gate establishes implementation parity, not a new mathematical
  bit-exact reference for W8A8. Trace dequantization/reference support must use
  true MXFP8 scales, the16-row gated layout and explicit local expert offset.

## Final runs

Wait for API and retained kernel source to stabilize, then freeze all source
and helper hashes. Include `flashinfer/fused_moe/api.py` and
`flashinfer/trace/templates/moe.py` in clean final source pins, in addition to
the previous83-path set. Do not infer their inclusion from a dirty diff after
the source has been committed.

Run the actual `benchmarks/bench_moe_deepseek.py` public APIs with the existing
untimed observer. Both V3 EP8 and V41-Flash EP4 retain the full token grid:
1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Measure1/2 but exclude them from
retention. NV family includes W4A4/W4A16 and TRTLLM NVFP4/BF16; MX family
compares CuTe and TRTLLM within MXFP8 and MXFP4×MXFP8 and includes TRTLLM BF16.
No CUTLASS arm. CuTe finalize remains unfused and NVFP4 remains per-tensor.

The final PR needs four complete raw public table outputs. Separate CuTe-only
repeats may supply native medians for retention. Each measured output must
record source, runtime, GPU UUID, tactic cache and route identity without
adding GPU work inside the timed region.

## Original-to-final comparison

Reuse originala65 C1/C2 from `evidence/b300-original-final-v3-r3` unchanged.
Fresh final A1/A2 use the same B300 GPU UUIDs: NVFP4 GPU2, MXFP8 GPU4, mixed
GPU6. Final arms call the corrected public benchmark. Map its native observer
medians into the existing original/final report schema with an explicit
adapter and input/timer/route provenance. Do not patch the old MX assembly to
choose new library behavior.

Compute `sqrt(old_C1 * old_C2 / (fresh_A1 * fresh_A2))` for each token and
format. The reused controls precede the new final arms, so this is an archived
control comparison and does not bracket intervening temporal drift. Fresh
both-model incremental retention evidence remains separate; do not multiply
its ratios into the original-to-final result. No original control timing is
rerun. Preserve old helper and timing receipts unchanged.

This supersedes the forwarding-only plan in
`evidence/b300-original-final-pdl-update-plan`; that archived plan and its
two-prefetch-keyword AST proof describe an earlier candidate and cannot bind
the public API correction. The published PR body must distinguish the
archived internal MX baseline from the final public-wrapper measurements.

No final timing is launched by this document. The public API correction is
retained and pushed as `adf02fdd4a8fd2a5d4d2ca54b6969cd65572d93d`, with all85
pins byte-identical to the measured review copy. Its bounded native screen
shows four-point affected-format means from0.997000 to1.001310; V41 mixed T4
is0.990194 in the paired comparison and loses in both repeats. This is an API
correction, not a claimed kernel speedup. Final53 focused tests and full-grid
timings remain separate from that bounded gate. Binding:
`evidence/public-mxfp-retained/receipt.json`.

The clean retained source passed53 focused tests, with all85 files unchanged;
`evidence/public-api-focused53/validation.json`. Final timing is launched by
`evidence/public-api-final-adf-r1/launch.json`, not by this document.

## Compilation-cache boundary

The source-specific `CUTE_DSL_CACHE_DIR` values are configuration/provenance,
not evidence of persistent artifact reuse. The installed CuTe4.7.1
`cute.compile` entrypoint forces `compile_only=True` and `no_cache=True`,
bypassing disk reads and writes. Current FC1/FC2 factories still reuse
compiled callables within each process through `functools.cache`. No
environment-only setting overrides this entrypoint. A future compile/export/
load mechanism would need a separate review and source/ABI binding; it is not
introduced during the final timing campaign. The installed source captures
and exact read-only audit are in `evidence/cute-sdk-cache-readonly-audit`.
