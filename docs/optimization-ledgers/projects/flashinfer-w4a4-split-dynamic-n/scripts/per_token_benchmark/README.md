# Standalone per-token benchmark arms

The frozen review source is `flashinfer-per-token-bench-review`, based on clean
`2b7fb10532dc3b5572a1cbff34bff41c2e8a2e01`. Only
`benchmarks/bench_moe_deepseek.py` changes. Parent owns integration, GPU validation,
and final public evidence.

- `cute-dsl-per-token` and `trtllm-per-token` are independent selectors. The old
  `--use-per-token-activation` CLI switch is removed.
- Default NV latency order is CuteDSL W4A4, CuteDSL PER-TOKEN, CuteDSL W4A16,
  TRTLLM NVFP4, TRTLLM PER-TOKEN, TRTLLM BF16.
- All four NV ratios use TRTLLM NVFP4 latency as numerator, ordered CuteDSL W4A4,
  CuteDSL W4A16, CuteDSL PER-TOKEN, TRTLLM PER-TOKEN. Winner includes all six.
- MX latency order is CuteDSL MXFP4x8, CuteDSL MXFP8, TRTLLM MXFP4x8,
  TRTLLM MXFP8, TRTLLM BF16. Ratios are matched dtype only; no MX winner.
- BF16 latency remains in both tables; BF16 ratio columns are removed.
- Per-token activation recipe is explicitly `NVFP44Over6Config(e4m3_max=256,
  err_mode="MSE", err_use_fast_math=True)` for initial activation quantization
  and internal FC2 input quantization. CuTe FC2 input scale is the paired inverse
  `1/(256*6)` from `make_nvfp4_global_scale`.
- Base FP4 fast math is disabled with a scoped
  `FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH=1` during initial activation quantization
  and the whole public execution/AUTO/capture/measurement scope. The prior value
  is restored even on exceptions. Shared weights are prepared outside that
  scope with explicit `nvfp4_4over6=None`; standard activation arms also pass None.
  The campaign runner should pin both FLASHINFER and TRTLLM base-fastmath aliases
  to zero as its ambient baseline, so ordinary weights retain their original
  quantization behavior.

Run `python3 scripts/per_token_benchmark/check_benchmark.py` from any directory
for CPU-only dispatch/parser/render/environment restoration and AST checks. The
receipt and illustrative output are under `evidence/per-token-benchmark-r1`.
The 62 checks do not execute CUDA or validate numeric GPU outputs. Scoped
pre-commit and py_compile also passed. Initial create_inputs, routing, timing,
TFLOPS, and histogram ASTs are unchanged from the base source.

`edit_benchmark.py` and `edit_table.py` preserve the source-edit construction as
local historical artifacts; do not rerun them against already edited source.
