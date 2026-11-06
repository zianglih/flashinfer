# DeepSeek MoE MXFP8 benchmark through 16384 tokens

Upstream draft PR: https://github.com/flashinfer-ai/flashinfer/pull/5301

Public evidence: https://gist.github.com/zianglih/57b5bfa0f047a4bc199fda98f58eddaa

The benchmark adds TRTLLM MXFP8 immediately before TRTLLM BF16, reusing `bench_trtllm` and the native MXFP8 preparation helpers. It follows #4985's DeepSeek-V3 workload: H7168/I2048/E256/top8, groups8/top4, routed scale2.5, seed42, routing bias0.01, EP8 local simulation (32 experts, offset0), TP1. Token counts are powers of two from1 through16384.

## Measurement and source provenance

Three configurations: inference per-tensor, inference per-token, and deterministic RL (per-token activation, 4over6, CuTe two-stage finalize). Each point has three fresh-process observations, 10 warmups and100 measured iterations, CUDA graphs, CUPTI, and cold L2. Initial activation quantization is included; weight preparation and prewarm autotuning are excluded. CUTLASS is skipped by request. This is a single-GPU local-MoE microbenchmark, without expert communication or end-to-end model claims.

- Original batch: `1cafd1a22ea7be32497c1b8e66c466ea873bb0af`, tokens1..4096,9 processes,585 observations. Raw files remain under `artifacts/runs/` and `artifacts/runs.json`.
- Added-token batch: `48f8a7a7bf2282cdb976dd4e28ec01ff32bf9cd1`, tokens8192/16384,9 processes,90 observations. Raw files are under `artifacts/extension-16k/`. This commit adds only `tune_max_num_tokens=max(n,8192)`, enabling actual16384-token TRTLLM profiling while preserving the previous bound at smaller sizes.
- Corrected TRTLLM NVFP4 per-tensor batch: final source `964f6fd2a582da1a7b57b5c20e3872caea80f693`, all15 token counts,3 processes,45 observations. Raw files are under `artifacts/nvfp4-linear/`. This fixes activation scale layout: the original arm passed128x4-swizzled scale bytes into a native path requiring linear scales. The final source requests linear scales and declares that layout explicitly. Per-token NVFP4 already produced linear scales.

There are720 raw observations,675 selected comparison cells,45 superseded NVFP4 per-tensor observations, and45 configuration/token medians. The superseded observations remain in the raw files and a separate table, excluded from all derived comparisons. Every other old cell is retained with its original measured source attribution. A shared repeat label pairs independent processes across the three batches.

`build_results_report.py` verifies all raw hashes, printed CSV against unrounded JSON, exact settings, package versions, and narrow source differences. `artifacts/results-provenance.json` records selection and provenance; `artifacts/results.md` contains every selected and superseded measurement. `build_pr_body.py` and `stage_evidence.py` generate the publication artifacts. Original publication summaries are preserved under `artifacts/original-4096-summary/`.

At16384 tokens, TRTLLM MXFP8 takes about0.92ms versus1.54–1.57ms for TRTLLM BF16, a1.67–1.71x speedup across the three configurations. Across all45 medians its speedup versus BF16 ranges1.31–1.72x. The largest repeat spread remains14.6% for TRTLLM NVFP4 at2 tokens in inference per-token; close ratios are not decisive differences.

## Validation

Historical MXFP8 validation remains at its original source: eight small quantized-reference/API cases and two full DeepSeek cases at32/4096 tokens. The small-shape reference uses a provisional broad fuzz envelope; no cross-precision accuracy claim is made.

Final source passed changed-file pre-commit,12 CPU/meta token-profile checks,6 NVFP4 activation operand checks at1/8192/16384 tokens with initial quantization off/on, and a full DeepSeek MXFP8 case at16384 tokens with finite output, API checks, and three exact CUDA-graph replays. The NVFP4 operand harness intercepts native MoE execution: it verifies actual benchmark payload/scales and quantization placement against a direct linear control, plus an independent inverse128x4 permutation and activation-QDQ old-layout control. It does not establish full-MoE numerical accuracy. Full repository tests and all-files pre-commit were not run.

Final reports and logs are in `artifacts/nvfp4-linear/`. Helpers are `validate_trtllm_token_cap.py`, `validate_nvfp4_activation_layout.py`, and the unchanged `validate_mxfp8_benchmark.py`. The old48f8 cap helper and the deliberately interrupted first attempt are preserved under `artifacts/diagnostics/`.

## Devbox and cache retention

Keep C2 namespace `ziangli` devbox `flashinfer-moe-mxfp8-0917`, pod `devbox-flashinfer-moe-mxfp8-0917-0`, and its warm compilation caches. Remote workspace: `/workspace/flashinfer-moe-mxfp8-benchmark`. Eight B300 GPUs are allocated; all performance and sequential GPU validation used GPU0 during this extension. Host: `hu-pdx-5`.

Image: `nvcr.io/nvidia/pytorch:26.05-py3`, digest `sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`. CUDA13.2.1.009, driver590.48.01, PyTorch2.12.0a0+5aff3928d8.nv26.05. All three batches use identical package versions; editable-install Git metadata differs as recorded. Full environment and package snapshots are retained per batch.

`run_extension_16k.sh` collected the additional token rows. `finish_extension_16k.sh` waited for completion, advanced only the local benchmark checkout to the scale-fix commit, ran validation, then invoked `run_nvfp4_linear_baseline.py`. Both pipelines completed with exit code0. No GPU validation ran concurrently with performance.

The original verified Weka backup is `/data/ziangli/flashinfer-moe-mxfp8-benchmark/2026-09-17-1cafd1a2`. `retain_devbox.sh` creates a new revision-specific backup without overwriting it, while leaving the live workspace/cache intact. The original restored cache came from `/data/ziangli/flashinfer-glm5-kimi-k3-moe-benchmark/2026-09-13-a2b23d27/flashinfer-cache.tar.gz`; no previous devbox or cache was deleted.

Publication refresh is complete. The public gist contains89 verified files, and the draft PR was read back with final HEAD964f6fd2 and an exact body match. Body SHA256: `c71cc70d503f61fbde50d5106404767bb1e359a91ea63d5b1c146d1a294086da`. No follow-up comments were posted.

Updated Weka backup completed and passed SHA256 read-back and gzip integrity checks: `/data/ziangli/flashinfer-moe-mxfp8-benchmark/2026-09-17-964f6fd2`. The original backup remains intact. Live devbox and cache retained.

```text
39d3b0b7574195cb5f2c62e15a9bf15d55d175fbe63f38277c55052c9bd8671a  /data/ziangli/flashinfer-moe-mxfp8-benchmark/2026-09-17-964f6fd2/flashinfer-cache.tar.gz
d98b965852f6793ebe3701f372a9a9ec533cc0da7058f24655c5de3d4546b399  /data/ziangli/flashinfer-moe-mxfp8-benchmark/2026-09-17-964f6fd2/workspace.tar.gz
```
