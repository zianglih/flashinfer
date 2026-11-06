# Public CuTe DSL MX MoE path

Source prototype: `flashinfer-public-mxfp-moe-review`, based on retained `8b74eb6fa77651bb20dacb56b8e13872f3ad9885`. Changes remain unstaged. Production is untouched.

- Extend the existing function/wrapper/core/tuner with explicit `quant_mode="w8a8"` (homogeneous MXFP8) and allow deterministic unfused W4A8.
- Reuse the existing 13 Blackwell tactics, workspace, routing, FC1/FC2 and combine. No kernel implementation or PDL policy changes.
- Existing NV defaults, W4A16 and localized/Rubin paths stay unchanged. W4A8/W8A8 are Blackwell SM100/SM103, BF16 output, no per-token scaling or SiTU.
- Public `CuteDslConfig.prepare_weights` gains MXFP8×MXFP8 for the function/wrapper workflow. `MoELayer`/its separate `CuteDslRunner` does not gain that pair.
- Benchmark MX arms use this public preparation and whole-MoE wrapper/function. The benchmark-local assembly runner and pipeline control flags are removed. Display labels remain MXFP8 and MXFP4×MXFP8.
- Appended `autotune_use_cuda_graph=False` on the wrapper matches the functional option. The benchmark explicitly enables it for MX to preserve the old assembly's tuning policy. Existing NV defaults are preserved; the new wrapper option rejects W4A16.
- The approximate trace reference handles true FP8×E8M0 weight decoding, gated 16-row interleave inversion and nonzero local expert offset. It is not a bit-exact GPU reference.

## Validation

`evidence/public-mxfp-moe-r1/source.json` pins 85 source files and the full unstaged patch. Scoped pre-commit passes. `probe_public.py` compares the frozen retained benchmark assembly with the new wrapper and function: both MX formats, N16/N64/N128 two-CTA, partial and zero-local routes, three changing-data graph replays. It checks quantized input bytes, filtered tactic lists, actual common-core launch arguments, graph-autotune settings, and 72 exact output comparisons. Six focused repository API/cache cases also pass. The trace CPU fixture lives in `evidence/public-mxfp-trace-r1`.

The first gate deployment exceeded the platform argument limit before remote execution. `retry_transport.py` uploaded the exact frozen program in hash-checked chunks. Failed transport artifacts are preserved; no GPU run was repeated.

## Native AUTO screen

`launch_native.py` stages existing runner/observer bodies, adds actual JIT package version metadata, and narrows the token list to 4,32,128,512 through a task-local driver. It runs existing W4A8 API tests before launching. Each model uses C–A–A–C on fixed GPUs: V4.1-Flash EP4 NV2/MX3; V3 EP8 NV7/MX6. Each arm uses fresh native AUTO, 10 warmups, 100 cold-L2/CUPTI CUDA graph iterations, PDL on, initial quantization excluded, per-token off and fused finalize disallowed. Controls are clean retained8b74 internal assembly; candidates use the public API source. Compiler caches are source-specific and reused across repeats, but no tuning cache is loaded. No original a65 baseline rerun.

The old assembly evidence remains historical; it is not relabeled as public API evidence. No performance claim is made from the exact gate.
