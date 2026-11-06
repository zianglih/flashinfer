# Split CuTe DSL W4A8 dynamic-N benchmark

This separate campaign measures the public Blackwell W4A8 backend (MXFP8
activations, MXFP4 weights, block size 32 with UE8M0 scales, BF16 output). It
preserves the frozen W4A4 scripts and existing W4A4 results without modification.
The baseline is current upstream a65d5b09e7e4c4c5c160b0161c48becd100b3970.

## Native driver adapter

`benchmarks/bench_moe_deepseek.py` currently rejects W4A8 and has no W4A8 backend
selector. `native_w4a8_adapter.py` adds that arm locally without changing either
source checkout. It calls the native `create_inputs`, `_collect_expert_histogram`,
`_autotune_context`, `_measure_or_profile`, `BenchResult`, and `calc_tflops`.
Routing uses the same `fused_topk_deepseek` operation. Activation preparation uses
`mxfp8_quantize` with linear UE8M0 scales; weight preparation uses the public
`CuteDslConfig.prepare_weights` MXFP4/MXFP8 contract exercised by existing tests.
Only `CuteDslMoEWrapper(quant_mode="w4a8")` is timed. No optional CAKE, CUTLASS,
TRTLLM, or W4A16 benchmark arm is invoked. Native input generation does retain
its existing out-of-band NVFP4 weight preparation, as in the W4A4 campaign.

W4A8 currently requires fused finalize and does not support SiTU. Accordingly
this campaign measures fused finalize, separately from W4A4's unfused campaign;
it does not present a K3/SiTU W4A8 result. A later upstream benchmark extension
can expose the same arm, but both source arms must use identical preparation,
workload, routing, timing, and adapter code for a primary comparison.

## Workload, timing, and retention

- H7168/I2048; 256 global experts; top-k8; groups8/top-groups4; routed scale2.5;
  native seed42 and routing-bias scale0.01; default SwiGLU.
- One GPU, simulated EP8/TP1, 32 local experts at offset0. Time routing plus both
  split GEMMs and required fused combine. Initial MXFP8 quantization, weight
  preparation, autotuning/compilation, and communication are excluded.
- Ten native warmups and 100 native cold-L2 CUDA-graph CUPTI samples per point;
  record the native median. CUPTI13+ is required; timer fallback is an error.
  Individual timing samples are not exported by the native driver.
- PDL on; distribution-aware autotune off; saved-cache loading off. Every sweep
  uses a fresh process and ordinary AUTO. Saved tactic caches are evidence only.
- Run sequential ABBA: beforeR1, afterR1, afterR2, beforeR2, same reserved GPU and
  environment. Preserve raw JSON, stdout, routing histograms, AUTO caches,
  compiler/runtime versions, explicit image, commits, all source hashes, and
  exact frozen harness/adapter code. Production changes must be committed.
- Tokens: 1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Report1/2 but exclude them
  from retention. Decode4–512 uses eight listed points; prefill uses4096/8192/16384.
- Per-repeat speedup=before/after; paired=sqrt(R1*R2); aggregate geometric means
  over the exact groups. Inspect every point, both repeat directions, AUTO
  choices, and prefill tradeoffs. No minima, pooled samples, diagnostic
  substitutions, silent reduced grids, or universal percentage threshold.

## Commands

Use the already reserved CUDA13.2 environment, exposing one GPU. The helper
never reserves resources or starts other GPU workloads itself.

```bash
project=/workspace/flashinfer-w4a4-split-dynamic-n
export CUDA_VISIBLE_DEVICES=0
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1
unset FLASHINFER_NVFP4_4OVER6 FLASHINFER_NVFP4_4OVER6_E4M3_USE_256
unset FLASHINFER_NVFP4_4OVER6_ERR_MODE FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH
"$project/.venv/bin/python" "$project/scripts/w4a8/run_split_benchmark.py" \
  --repo "$project/baseline" \
  --expected-head a65d5b09e7e4c4c5c160b0161c48becd100b3970 \
  --image nvcr.io/nvidia/pytorch:26.05-py3 \
  --output "$project/results/w4a8-baseline-r1.json" \
  > "$project/results/w4a8-baseline-r1.log" 2>&1

"$project/.venv/bin/python" "$project/scripts/w4a8/run_campaign.py" \
  --baseline-repo "$project/baseline" --candidate-repo "$project/candidate" \
  --baseline-sha a65d5b09e7e4c4c5c160b0161c48becd100b3970 \
  --candidate-sha "$candidate_sha" --image nvcr.io/nvidia/pytorch:26.05-py3 \
  --reuse-baseline-r1 "$project/results/w4a8-baseline-r1.json" \
  --output "$project/results/w4a8-primary-$candidate_sha"

"$project/.venv/bin/python" "$project/scripts/w4a8/summarize_results.py" \
  "$project/results/w4a8-primary-$candidate_sha" \
  --output-prefix "$project/results/w4a8-primary-$candidate_sha-summary"
```

Baseline reuse verifies exact harness+adapter, source/environment/GPU, token
sequence, completed log, and cache hashes, then copies raw artifacts and original
timestamps. It runs only afterR1, afterR2, beforeR2. Any mismatch fails rather than
silently rerunning existing data. Preserve the frozen adapter after baselineR1.
A bounded diagnostic may pass `--tokens`; the summary then requires
`--allow-partial` and explicitly marks incomplete retention groups.
