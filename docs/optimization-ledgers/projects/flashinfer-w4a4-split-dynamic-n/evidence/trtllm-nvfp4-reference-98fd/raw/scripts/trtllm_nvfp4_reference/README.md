# Native TRTLLM NVFP4 comparison

Every future NVFP4 performance update for this effort includes a same-shape native TRTLLM W4A4 reference column, or explicitly marks it pending. Keep the original before/after retention campaign and its exclusions unchanged.

This first comparison runs two fresh TRTLLM sweeps (`T1`, then `T2`) and reuses the final, immutable CuTe DSL review `A1` / `A2` measurements. It is a **later backend reference**, not an interleaved ABBA experiment. Per-row speedup is `sqrt(T1*T2/(CuteA1*CuteA2))`; greater than one favors CuTe DSL. Run all 13 token counts; exclude 1 and 2 from decode/prefill/overall geometric means. Decode is 4–512, prefill is 4096/8192/16384. Do not rerun existing CuTe or baseline data.

- **Source:** clean independent `trtllm-reference-98fd`, commit `98fd3566b5f945c100f48cddacf25deb2432cbc2`. The benchmark and timing utility are byte-identical to the saved CuTe arms. The new observer is generated from frozen `scripts/run_split_benchmark.py`; its declared substitutions reverse byte-for-byte to that helper. No input generation, timing, AUTO, or cleanup loop changes.
- **Native entry:** `benchmarks/bench_moe_deepseek.py::_benchmark_single` → `bench_trtllm(precision="nvfp4")` → `trtllm_fp4_block_scale_moe`. Selector `trtllm-nvfp4`, logits routing, native `RoutingMethodType.DeepSeekV3`, default uniform input generation. No routed realization factory, `torch.distributed`, communication, or distribution-aware tuner.
- **Workload:** single process / physical GPU0 only, simulated EP8/TP1: 256 total / 32 local experts, offset0, hidden7168, intermediate2048, topk8, routing groups8/topk_groups4, routed scale2.5. Tokens `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`.
- **Measured region:** logits routing, native GEMMs/activation/requantization, and native finalize. Initial activation quantization and weight quantization/shuffle are outside timing. TRTLLM keeps `do_finalize=True`; the CuTe result uses deterministic split finalize. Native backend scale preparation differs: TRTLLM uses the benchmark's computed per-tensor/per-expert global scales, while CuTe uses its existing preparation. This is native same-shape latency, not bit-exact output equivalence or an isolated kernel comparison.
- **Timing:** unchanged native AUTO prewarm, then 10 warmups / 100 cold-L2 CUDA-graph CUPTI iterations, native median. `TRTLLM_ENABLE_PDL=1`, `FLASHINFER_DIST_AWARE_AUTOTUNE=0`, `FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0`. Persist per-token medians, logs, cumulative AUTO caches, cache hashes, source map, and environment. The original observer does not expose individual timing samples.
- **Environment:** `nvcr.io/nvidia/pytorch:26.05-py3`, existing C1 B200-83 GPU0 UUID `GPU-7d34f345-ddcf-6ad5-4791-84a6f16c1281`. Reuse the candidate-442 native cache and its verified native-data resolution. The sole declared runtime-environment exception is a private CuTe cache at `cache/trtllm-reference-98fd/cute_dsl`; all other recorded software/runtime fields and GPU inventory must match saved CuTe A1.
- **Prior data:** local filename and JSON backend-label searches under this project's `results` / `evidence` found no matching TRTLLM timing rows. Only source text in preparation receipts matched.

Run the outer helper from the remote project, with the pinned manifest hash reported by `build_adapter.py`:

```bash
source scripts/recovery442/env_candidate.sh
export CUDA_VISIBLE_DEVICES=0
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0 FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0
export CUTE_DSL_CACHE_DIR=/workspace/flashinfer-w4a4-split-dynamic-n/cache/trtllm-reference-98fd/cute_dsl
.venv/bin/python scripts/trtllm_nvfp4_reference/run_reference.py --arm T1 --manifest-sha 5a86d78d89e03b4e093dd34cf7292711671fb11014a2aa414fe53dcc38b51704 --preflight-only
.venv/bin/python scripts/trtllm_nvfp4_reference/run_reference.py --arm T1 --manifest-sha 5a86d78d89e03b4e093dd34cf7292711671fb11014a2aa414fe53dcc38b51704
.venv/bin/python scripts/trtllm_nvfp4_reference/run_reference.py --arm T2 --manifest-sha 5a86d78d89e03b4e093dd34cf7292711671fb11014a2aa414fe53dcc38b51704
```

The helper refuses existing arm directories, pins both reused CuTe raw records and their caches, verifies production/native sources and the observer before/after each sweep, and checks all 13 routing histograms against CuTe. No branch launches CuTe or original baseline measurements.
