# Source audit for the rebased benchmark refresh

Compared retained measured `a620ce7790b32f7f0ae524a811417d2c6cee1152` against `2b4732791a3ce48bc3ae6c030a283fab73854e0e`. Read-only audit; no source edits or GPU execution. Evidence: `source-blob-comparison.json`, `tactic-ast-comparison.json`, and the previous `integration/pr7290-refresh-20261030` publication receipts.

## Conclusions

- The existing frozen choices remain semantically valid. Benchmark model/route definitions, swap-AB tactic file, all tactic-generation functions, W4A16 filtering/defaults, and both runner hashes are unchanged. The generic runner filter changed only to reject ClampedRelu2 on Rubin; it does not change the SM103 matrix.
- Persisted cache **keys must be regenerated**. Upstream #6139 removes `local_expert_offset`: old generic runner extras index 8 and old W4A16 extras index 3. Preserve every recorded tactic and each existing W4A16 `-1` default; do not tune or substitute fallback choices. Replaying unchanged old keys can miss, invalidating a matched-choice comparison.
- No changed timed GPU operation is identifiable from source for the four existing model activations. This is not proof of identical generated instructions or performance; the swap-AB compile structure changed and fresh kernel-resource/codegen evidence remains useful.

## Timed-path scope

| Area | Difference from measured head | Consequence for this refresh |
|---|---|---|
| Model and benchmark script | Byte-identical | V3/V41F use SwiGLU, K3 uses SiTU, N3U uses ReLU²; none uses new ClampedRelu2. EP/TP shapes and quantizer inclusion remain unchanged. |
| W4A16 FC1/FC2/dequantization | Kernel and helper bytes identical | No new device arithmetic, pipeline, store, scheduler, or register-policy change. Launcher only narrows the activation validator to preserve upstream unsupported-mode errors. |
| Swap-AB FC1/FC2 | Adds runtime ClampedRelu2 support; local epilogue object copy and explicit unbound calls | Old activations compile out clamp pointer/tensor use and arithmetic. Nongated classification evaluates exactly as before for ReLU² and FC2. The copy is Python compilation work; no device allocation. No tiler, stage count, CLC, PDL, barrier, cache hint, or register policy changed. |
| Routing and finalize | Relevant MoE utility/routing C++ sources and DSL finalizer bytes identical | Same route fixtures and same selected tile contract remain valid. |
| Timed NVFP4 input quantizers | CuTe per-tensor/per-token sources and recipe helper bytes identical | Existing `include_activation_quant` NVFP4 timing covers the same quantizer implementations. W4A16 has no input quantizer. |
| MXFP8 swizzled CuTe quantizer | Upstream #5982 adds early PDL consumer release | Not used by this matrix's input preparation, which explicitly uses `backend="cuda"`, and MX input quantization is outside the timed MoE call. FC1 in-kernel quantization is unchanged for existing activations. |
| Host API validators | New clamp validation and argument forwarding | Existing calls pass None; no tensor read or CUDA synchronization added. Host dispatch changes are outside captured GPU spans. |

## Native compilation provenance

The old measured cohort recorded four native modules: `dsv3_fused_routing`, `moe_utils`, `fp4_quantization_103`, and `mxfp8_quantization_sm100`. Current native builds must remain normal source-derived builds, with separate current-source cache provenance.

- `fp4_quantization_103` **and** `mxfp8_quantization_sm100` compile the changed `csrc/nv_internal/cpp/kernels/quantization.cu`. Their common `quantization.cuh` and `quantization_utils.cuh` changed as well. Do not transplant historical ELFs or insist that new hashes equal the old cohort.
- Changes include #6207 two-load scheduling selected for devices with at most 1024 threads/SM (SM107, not the B300 SM103 matrix), #6278 TMA batch/grid and scale-row bounds, #6322 moving device scale reads after the PDL wait, and #7976 hoisting the NVFP4 reciprocal. Some single-load compiled code can still differ after the new template/control structure, so host-side architecture gating alone is not proof of identical native code. These native quantizers prepare weights or MX input outside candidate timing; timed NVFP4 candidate input quantization uses CuTe.
- The native MoE-sort sources, `noAuxTcKernels.cu`, their JIT builders, BMM artifact metadata, JIT compiler/cache builders, and submodule gitlinks are unchanged. Their rebuild output may still reflect toolchain/environment differences, so record actual loaded files and normal-loader results.
- The requirements change only raises cuDNN frontend to 1.32.0 among these dependencies; the CuTe requirement remains `nvidia-cutlass-dsl>=4.8.0`. The lower bound does not pin the installed version. Record current actual DSL, CUDA/PTXAS, Torch, driver, and GPU clocks before interpreting differences from the older C2 run.

## Autotuner and timing implementation

`flashinfer/autotuner/autotuner.py` changes CUPTI initialization/fallback coordination during fresh tactic profiling; `protocol.py` and `autotune_cache.py` add an execution-generation counter for managed-store attachment/reload. The persisted key construction/search algorithms are unchanged. These changes do not alter recorded replay choices. Fresh profiling is forbidden by the replay harness. Public timing uses `flashinfer/testing/utils.py`, which is byte-identical across the two source arms, rather than the modified autotuner profiling routine.

## Interpretation and next checks

The prior refresh used 31 jobs / 36 supported arms / 468 raw cells (396 excluding 1–2 tokens), frozen routes/tactics, 100 strict CUPTI graph samples after 10 warmups, cold L2, and two candidate phases. Reusing its choice fixtures is justified; reusing its candidate timing as current timing is not. Historical TRTLLM, legacy and pre-PR W4 denominators stay reference comparisons, not same-run causal controls.

For the first new job, inspect current-key cache hits, exact selected tactic/default, zero profiling calls, native/source manifests, actual register/local-memory receipt, and sample-count/clock evidence before launching the whole matrix. If a repeatable regression appears under those constraints, compare swap-AB old/new SASS and resources first; for W4A16, begin with native routing/toolchain/timing provenance because the W4 device sources did not change.
