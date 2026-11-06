# Native W4A4 MegaMoE benchmark API audit

Source inspected: project-local `flashinfer/`, HEAD `44a04fd247cf2f93bee4052bf439bc93f32c7f8c`, 2026-09-23. This is a read-only implementation audit, not GPU validation. Repository `AGENTS.md` delegates to `CLAUDE.md`; both were read. No repository code, index, commits, or remote resources were changed by this audit.

## Recommended construction

Add `BenchVariant("w4a4_megamoe", use_nvfp4_activations=True, use_megamoe=True)` and select the existing public `Sm100_Nvfp4_Nvfp4_Bf16_Cutedsl_MegaMoeConfig` in the shared MegaMoE runner. Keep the same `MoEEpLayer`, `BootstrapConfig`, `FleetParams`, `MegaConfig`, `MoEEpTensors`, input generation, routing, per-case capacity, warmup, timing function, and destruction flow as W4A16 MegaMoE.

```python
MegaConfig(
    megakernel=Sm100_Nvfp4_Nvfp4_Bf16_Cutedsl_MegaMoeConfig(
        intermediate_size=CFG.intermediate_size,
        top_k=CFG.top_k,
        apply_topk_in_fc1=args.apply_topk_in_fc1,
        # Existing public defaults: input_norm_const=1.0,
        # enable_in_kernel_fc2_reduce=False, combine_dtype="bf16".
        knobs=w4a4_knobs,
    ),
    quantize_input=True,
)
```

Feed the original BF16 activations and FP32 top-k weights plus int32 top-k IDs. Feed runtime `fc1_alpha` and `fc2_alpha` vectors of ones, identically to the existing W4A16 benchmark. Weight preprocessing stays outside timing. Activation quantization stays inside every measured `forward`.

Public defaults and staging contract are in:

- `flashinfer/moe_ep/backends/mega/kernel/sm100/nvfp4_nvfp4_bf16_cutedsl/config.py:13-55`.
- `flashinfer/moe_ep/modes/config.py:26-48`: `quantize_input=True` and `preprocess_weights=True` by default.
- `flashinfer/moe_ep/modes/mega_layer.py:362-438`: BF16 validation, owned-output allocation, input staging, compute.
- `flashinfer/moe_ep/backends/mega/kernel/sm100/nvfp4_nvfp4_bf16_cutedsl/backend.py:178-251`: activation staging plus batched runtime alpha staging.

## Matching the workload

The benchmark's `_create_shared_ep_weights` already returns canonical `PrequantizedMoEWeights` with packed uint8 FP4 and raw E4M3 per-16 scales, using a fixed global scale of one. Both Mega backends can consume that same pack. W4A4 preprocessing changes layout only: it interleaves `[gate, up]` in 16-row groups, creates transposed views with K stride one, and swizzles scale planes. It does not requantize prequantized inputs. Its FC2 packed weights are also consumed directly. See `.../nvfp4_nvfp4_bf16_cutedsl/weights.py:102-225`.

For W4A4 input staging, the normal path fuses BF16-to-NVFP4 quantization and route repacking in one `DataPreprocess` launch. `FLASHINFER_MEGA_FUSED_STAGE=0` selects a slower torch-composed fallback, so record this environment and retain the existing setting. Input scale factors are per contiguous block of 16 elements, with a scalar `input_norm_const` defaulting to one. FC1's SwiGLU result is requantized to NVFP4 with per-expert `fc1_norm_const` (also defaults to one). Both GEMMs use NVFP4 activations and weights; dispatch inputs are NVFP4, while the selected combine wire and output remain BF16. See `.../staging.py:18-97`, `.../src/moe_nvfp4_swapab/runner_common.py:689-717`, and `.../shim/nvfp4.py:1109-1114,1208-1228`.

Explicitly pass the benchmark's routing placement boolean. Native W4A4 defaults to `apply_topk_in_fc1=True`, whereas W4A16 defaults to `False`. Letting each backend keep its default would change both activation precision and routing placement. `False` is supported by the W4A4 implementation: `src/moe_nvfp4_swapab/megamoe_kernel.py:1532-1541` applies routing scores in the terminal reduction when FC1 weighting is disabled. W4A4 IKR requires FC1 weighting, so leave IKR disabled for the default comparison (`shim/nvfp4.py:171-180`).

There is no native per-token row-scale vector ABI in this W4A4 Mega backend. Reject `--use-per-token-activation` when `w4a4_megamoe` is selected. Likewise, the Mega staging path does not implement the split quantizer's environment-driven 4over6 algorithm. Do not describe it as per-token or 4over6 W4A4; record or reject that incompatible environment for this arm.

## Timing, tuning, and evidence

Keep the current full-forward CUPTI activity-span timing, per-iteration rank maximum, median across iterations, cold L2 flush outside measurement, CUDA graph replay, fixed precomputed routing, 3 warmups, and 100 iterations. Native W4A4 activation quantization, alpha staging, communication, both GEMMs, BF16 terminal reduction, and owned-output copy all belong inside the measured forward. Do not use prequantized activations or `return_workspace_view=True` to remove that cost. `backend.py:335-429` confirms the default `output.copy_` path. Setup, tuning, compilation, and weight layout preparation remain excluded.

Maintain distinct knobs for W4A16 and W4A4, especially if a pinned W4A16 JSON dictionary is used for the final table. Their candidate spaces and built-in profiles differ. `knobs="auto"` is supported for W4A4 and runs collectively during the first warmup; it persists a winner to the W4A4 cache namespace. Record effective knobs and the cache path for reproducibility. `knobs=None` uses cache lookup or the built-in heuristic rather than always selecting a fixed default (`shim/nvfp4.py:1129-1154`).

The existing W4A16 auto log reads `layer._kernel._autotune_winner`. W4A4's backend does **not** define that attribute: it discards the return value from `autotune_nvfp4_mega_moe`, while the effective winner is installed into the workspace frontend config. Generalizing the log verbatim will crash after tuning. Read effective frontend knob fields for W4A4 or otherwise log that state without adding an unrelated production-kernel change. See `backend.py:360-380`, `shim/autotune.py:320-333,336-415`.

Keep the existing strict `--refcheck` specifically as the same-weight W4A16 split-vs-Mega assertion at `atol=rtol=1e-2`. W4A4 changes both input and SwiGLU handoff quantization, so the same tolerance is not a W4A4 quality criterion. Existing W4A4 public-layer and torch-oracle tests cover the native FC1-weighted contract; shared helper arguments labeled `apply_topk_in_fc1=False` are applied only to W4A16 in the constructor, so those labels do not independently establish W4A4 FC2-weighted oracle coverage (`tests/moe_ep/test_moe_ep_nvfp4_cutedsl_mega_multirank.py:1328-1350`; `tests/moe_ep/test_nvfp4_cutedsl_kernel_vs_reference.py:238-310,751-812`). A fresh finite-output/GPU smoke at the actual benchmark contract is useful; do not claim W4A4 parity from W4A16 refchecks.

Report both speedup denominators unambiguously:

- Existing W4A16 Mega speedup over split: `split_w4a16_ms / w4a16_megamoe_ms`.
- W4A16 Mega speedup over W4A4 Mega: `w4a4_megamoe_ms / w4a16_megamoe_ms`.

## Benchmark integration pitfalls

- Generalize hardcoded Mega variant checks in parser validation, TP exclusion, NCU kernel requirement, profile label construction, shared-weight selection, and console/CSV output. Keep the default `w4a4,w4a16` behavior and column order unchanged.
- Apply refchecks only to `w4a16_megamoe`; sorting split variants before Mega variants remains correct.
- Preserve `stage::MegaMoE` for profiling. NCU application replay's `--lockstep-nvtx-include=stage::MegaMoE/` matches that exact name. Existing profiler launch selection already uses `variant.use_megamoe` in most locations.
- NCU compute-only setup currently switches to shared weights only when the literal `w4a16_megamoe` appears. Include either Mega variant so split profile weights match benchmark weights when only W4A4 Mega is selected.
- Keep all-rank NCU coordination and nonempty-rank application-replay constraints. Never use isolated-rank replay for W4A4 Mega either.
- Preserve owned output and exact capacities for both Mega arms, including empty source ranks at small global token counts. W4A4 staging explicitly invalidates stale route rows and notes zero staged tokens.
- `--no-fused-finalize` and `--no-pdl` configure the existing split path. Do not claim these flags introduce corresponding native Mega implementation modes; the native API and timing boundary stay as above.
