# Quantizer scalar-hoist validation reuse

**Cancelled without deployment or timing.** The general candidate failed the compact exact/native resource gate before the failing candidate was launched. The prepared plan remains unchanged; see `cancellation.json`.

CPU-only preparation for the one-file candidate on retained `2b8eb9d8`. No tests, profiles, timing, remote source copies, or benchmark controllers were launched by this preparation. The candidate owner owns the source freeze and exact/native qualification.

## Existing exact and native entrypoints

The durable prior effort is `../flashinfer-w4a4-split-dynamic-n/fc1-gather-20261028/optimization-next-20261029/per-token-warp-reduce/`.

- `direct_gate_r1.py`: 52 direct cases over FP16/BF16, PDL off/on and K16..16384; 208 graph replays change live rows to 0/1/129/4097; four routed-hole cases preserve64 logical/128 physical SF rows. It compares the same source at128 threads against the retained/default width (forced32 at8192/16384 to exercise two-pass); therefore new source-paired outputs or hashes are still required for the scalar-hoist change.
- `selection_plugin.py` plus `run_gate.py`: existing repository tests only. The archived80 selection has48 TE-reference cases,18 wide-row cases,6 scale-fold cases and8 MoE cases. The current recipe test already includes precise/fast FP4 math, FP16/BF16, ordinary NVFP4 and4over6, layouts128x4/8x4/linear, and random/boundary/zero/max/subnormal inputs. The old K<=2048 pairwise selection includes only7 of8 four-over-six recipes (MAE256/error-fast is absent); current collection must supply an existing omitted case if all8 are claimed.
- `test_nvfp4_quantize_per_token_cute_dsl_wide_rows`: old compact selection M130 and K1536/18432/69632 spans default multiwarp/register-resident and two-pass paths, both input dtypes and all3 layouts. The old descriptive comment predates the retained CTA-width policy; inspect actual kernel attributes rather than inferring threads from the comment.
- `test_nvfp4_quantize_per_token_out_scale_fold`: M17, both dtypes and all3 layouts checks unchanged payload/SF bytes, exact folded scales, and padding.
- `quant_codegen_record.py`: successful historical recorder, but explicitly adds `--keep-cubin` and `no_cache=True`, and does not identify all specialization fields. Use the current native capture mechanism with unchanged compiler options and actual loaded resources. Do not reuse `quant_guard_plugin.py`: its `compiled.library` assumption failed historically.

Recommended first paired native cases are BF16 K640/M4097 with precise FP4 math plus MSE256/error-fast (default64 threads), then FP16 K512/M4097 fast FP4 math (default32). Native evidence must identify dtype, main fast-math flag, full4over6 recipe, SF layout, thread count, register-resident/two-pass path, fold option, actual PTX/cubin, resources and options. Existing precise-error recipes can already have local allocation; compare the exact same specialization to the current control rather than imposing a historical universal LOCAL0 claim.

The archived measured quantizer `9960490f` is AST-equivalent to current formatted `0d86930d`; this is useful source history, not a fresh-runtime native-control replacement. Fresh paired captures should prove the scalar load and precise reciprocal move outside the persistent row loop without changing row arithmetic or PDL wait/signal order.

## Held performance subset

`reuse-plan.json` verifies all24 cells have explicit recorded choices, source-bound routing fingerprints and `--include-activation-quant` in the original benchmark command. It selects the eight existing PER-TOKEN jobs: V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8 and N3U EP8/TP8, each at32/4096/16384 tokens.

Reuse the established controller, native timer/cache observers and current resource guard. Keep strict CUPTI, cold-L2 CUDA-graph timing,10 warmups,100 samples per C-A-A-C phase (9,600 samples), input quantization included, no autotuning or changed choices/routes. The benchmark recipe is precise base FP4 quantization with MSE4over6/E4M3=256/error-fast; the standalone exact matrix covers other recipes separately. Preserve all negatives, repeat spreads and clock observations. No historical TRT/non-swap baseline needs regeneration. Timing remains held until the candidate's native gate and parent authorization.
