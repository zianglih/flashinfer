# Homogeneous Blackwell grouped-MoE phase benchmark

This task-local adapter covers the formerly supported homogeneous combinations
that have no public `CuteDslMoEWrapper.quant_mode` selector. It leaves the
frozen W4A4, W4A8 and per-token harnesses and existing evidence unchanged.

Run each of these configurations separately for `fc1` and `fc2`:

| Config | Activation and weight | Scale format | Block size |
| --- | --- | --- | ---: |
| `fp4-e8m0-sf16` | FP4 E2M1 | UE8M0 | 16 |
| `mxfp4-sf32` | FP4 E2M1 | UE8M0 | 32 |
| `mxfp8-e4m3-sf32` | FP8 E4M3 | UE8M0 | 32 |
| `mxfp8-e5m2-sf32` | FP8 E5M2 | UE8M0 | 32 |

The paired phases are independent microbenchmarks, not full-MoE timings and not
components that can be summed into an end-to-end latency. FC1 uses SwiGLU and
BF16 output without output quantization; FC2 uses BF16 expanded output without
fused combine. All four input configurations previously supported this common
output contract. Existing W4A4/W4A8 measurements cover their quantized FC1 paths.
These measurements do not cover every supported output dtype or quantization
recipe; in particular FP4 output with UE8M0 scales is not measured here.

The native `benchmarks/bench_moe_deepseek.py` supplies BF16 tensors, deterministic
routing, histogram and the unmodified timer. Workload: H7168/I2048, E256, top-k8,
groups8/top-groups4, routing scale2.5, seed42, bias0.01. Single GPU simulates EP8
with 32 local experts at offset0 and TP1. FC1 retains native up64/gate64 weight
interleave. FC2 input is the deterministic first I columns of the native BF16
hidden states, gathered by the exact native route mapping. It does not depend
on an optimized FC1's results. Preparation quantizes each operand outside timing
and uses linear input scales for FC1, swizzled scales for FC2 and expert weights.
The public FP4 quantizer does not emit UE8M0 SF16, so that case retains its
MXFP4 payload and duplicates each SF32 scale into two SF16 blocks, preserving
every represented operand value; public `block_scale_interleave` produces the
swizzled storage where required. E5M2 input preparation re-encodes the public MXFP8 quantizer's E4M3 values as
E5M2 while retaining UE8M0 scales; it is not a new E5M2 quantizer contract.

Routing, operand preparation, memory allocation, compilation, AUTO selection,
inter-GPU communication and output combine are outside each phase timer.
For each exact token shape the standard AutoTuner selects among the phase
catalog from that source revision, filtered through its own `can_implement`.
Tuning uses cold-L2 CUDA graphs and the actual prepared native routing. There
is no high-level homogeneous MoE bucket policy to reuse. No handpicked tactic,
external saved cache, DA policy or fixed old/new source hash substitutes for
AUTO. Selected and available tactics plus route capacities are saved per row.

Measurement uses 10 warmups, 100 cold-L2 CUDA-graph CUPTI samples, returning the
native median. CUPTI fallback is an error. PDL is enabled, DA and loading saved
AUTO caches are disabled. Four fresh processes run baseline R1, candidate R1,
candidate R2, baseline R2 in ABBA order per configuration/phase. All source,
harness, environment, GPU, routing histogram, tactic and raw median evidence is
preserved. The existing verified-baseline-R1 reuse option is available here but
only accepts this exact config, phase, source and harness.

Full tokens: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. Report T1/T2 and
exclude only those points from retention. Decode is T4 through T512; prefill is
T4096/T8192/T16384. Summaries show both before/after repeat ratios, their paired
geometric mean, pointwise agreement and aggregate geometric means. Incomplete
grids require `--allow-partial` and cannot silently produce full aggregates.

## Commands

Set `candidate_sha` and `explicit_ngc_image` to the committed candidate and
pinned CUDA13.2 image selected for the primary campaigns. No GPU is reserved by
these scripts. Use the same reserved GPU/runtime for all source arms.

```bash
project=/workspace/flashinfer-w4a4-split-dynamic-n
export CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0
unset FLASHINFER_NVFP4_4OVER6 FLASHINFER_NVFP4_4OVER6_E4M3_USE_256
unset FLASHINFER_NVFP4_4OVER6_ERR_MODE FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH
for dtype_config in fp4-e8m0-sf16 mxfp4-sf32 mxfp8-e4m3-sf32 mxfp8-e5m2-sf32; do
  for phase in fc1 fc2; do
    "$project/.venv/bin/python" "$project/scripts/homogeneous/run_campaign.py" \
      --dtype-config "$dtype_config" --phase "$phase" \
      --baseline-repo "$project/baseline" --candidate-repo "$project/candidate" \
      --baseline-sha a65d5b09e7e4c4c5c160b0161c48becd100b3970 \
      --candidate-sha "$candidate_sha" --image "$explicit_ngc_image" \
      --output "$project/results/$dtype_config-$phase-$candidate_sha" || exit
    "$project/.venv/bin/python" "$project/scripts/homogeneous/summarize_results.py" \
      "$project/results/$dtype_config-$phase-$candidate_sha" \
      --output-prefix "$project/results/$dtype_config-$phase-$candidate_sha-summary" || exit
  done
done
```

A standalone pre-candidate baseline uses `run_split_benchmark.py --repo ...
--expected-head ... --image ... --dtype-config ... --phase ... --output ...`.
Keep the same-stem stdout log beside the JSON for later
`run_campaign.py --reuse-baseline-r1 <that-json>` verification. Full sweep
completion is required; the driver never overwrites partial evidence.

Local validation: Python compilation, Ruff and API/signature checks only.
The adapter still requires its first GPU smoke run before primary measurement.
