# CUDA 13.0 W4A16 comparison completed

- Naming refactor cancelled and fully reverted; existing `interleave_cute_dsl_moe_weights` name retained. No source commit or source-branch push. Production remains clean at `a620ce7790b32f7f0ae524a811417d2c6cee1152`.
- Fresh C3 B300 comparison: pre-PR `002529e1` original 64-row gated layout versus `a620ce77` 16-row gated layout, same eight EP/TP workloads, frozen per-arm choices, unfused finalize. All 104 cells / 41,600 CUPTI samples passed execution and independent raw replay. Tokens 1/2 stay raw and are excluded from 88 reported cells.
- Geomeans: +6.03% overall, +3.64% decode, +12.70% prefill; EP +1.36%, TP +10.93%. Eight negative cells, minimum -1.53%; 14 cells have >1% repeat spread, maximum 8.90%. No filtering or selective reruns.
- Image `nvcr.io/nvidia/pytorch:25.11-py3`, native CUDA 13.0.2 / NVCC 13.0.88. CuTe DSL 4.8 embeds NVVM 13.4.59; no generated PTX capture claim. No new numerical or sanitizer qualification.
- Appended results/heatmap after the unchanged GLM5 section in [PR7290](https://github.com/flashinfer-ai/flashinfer/pull/7290). Existing body prefix/suffix, title and comments preserved; API readback verified.
- Immutable assets commit `b53831030d2cca89520d44648dafefc5dc382c6b`; old asset prefixes unchanged. Eleven core public assets, including all three archives, were HTTP downloaded and hash-verified.
- [Heatmap](https://raw.githubusercontent.com/zianglih/flashinfer/b53831030d2cca89520d44648dafefc5dc382c6b/a620ce77-cuda130-20261102/cuda130-w4a16-before-after.png), [full tables and original stdout](https://github.com/zianglih/flashinfer/blob/b53831030d2cca89520d44648dafefc5dc382c6b/a620ce77-cuda130-20261102/tables.md), [raw evidence](https://github.com/zianglih/flashinfer/blob/b53831030d2cca89520d44648dafefc5dc382c6b/a620ce77-cuda130-20261102/evidence-index.md).
- Persistent source-specific C++/CuTe compilation caches remain under `/data/ziangli/flashinfer-moe-gather-pipeline/cuda130-w4a16-20261102/cache` on C3. Optimization remains paused.

## Post-publication dequantization path audit

Matching diagnostic replay captured both arms FC1/FC2 PTX and SASS: all four use direct packed BF16 dequantization, with no FP16-to-FP32 weight widening. These are new diagnostic artifacts, not the original timed-run cubins; source, tactics and executed symbols match. See [artifact audit](dequant-artifacts/README.md).

Latest SGLang image `lmsysorg/sglang:nightly-dev-cu13-20261102-38d9e4a3` was inspected through its actual OCI layers. Its CuTe CUDA13 compiler binary matches the measured runtime byte-for-byte (`f325e99ecfd4e49411d694bf7b08f3d9aa4f3e8fa1f0da9d3b456038fa4c0d32`), whose `cutlass.CUDA_VERSION` is13.4. Its FlashInfer gate therefore selects the same direct path on the CUDA13 deployment. The user-authorized conditional fallback rerun does not trigger; no benchmark or PR-body replacement was performed. See [image evidence](dequant-artifacts/sglang-image/image-audit.json).

## PR-body section removed at user request

Removed the added CUDA13.0 regression section only. Live API readback equals the original pre-addition body exactly; GLM5, other evidence, title and comments are unchanged. Artifacts and archived evidence remain available. See publication/remove-pr-section/receipt.json.
