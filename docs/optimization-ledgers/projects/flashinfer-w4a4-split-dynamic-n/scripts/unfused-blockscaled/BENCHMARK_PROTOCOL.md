# Unfused MXFP8 activation MoE comparison

The same `bench_cute_dsl_mxfp8.py` assembly is used unchanged in both source arms.
Modes are homogeneous E4M3 MXFP8 weights/activations (`--weight-format mxfp8`)
and E2M1 MXFP4 weights/E4M3 MXFP8 activations (`--weight-format mxfp4`, W4A8).
Both use UE8M0 SF32. These are complete MoE measurements: native DeepSeek router,
sort, SwiGLU FC1 with generated MXFP8 scales, FC2 expanded BF16 output, and the
existing deterministic BF16 combine. Fused finalize is always disabled.
Initial activation and weight quantization and inter-GPU communication are excluded.
The earlier fused W4A8 and homogeneous per-phase data do not satisfy this scope.

- H7168, I2048, E256, top-k8, groups8/topgroup4, route scale2.5, seed42, bias.01.
- Single B200, simulated EP8/TP1,32 local experts, offset0.
- Tokens:1,2,4,8,16,32,64,128,256,512,4096,8192,16384.
- T1/T2 reported but excluded from retention; decode4..512, prefill4096/8192/16384.
- Native dynamic token buckets and seeded routing tuning policy, unchanged;
  each source supplies its own full supported tactic catalog. No fixed tactic.
- PDL on, distribution-aware AUTO off, file AUTO loading off, 4over6 overrides unset.
- Fresh process per sweep;10 warmups,100 cold-L2 CUDA-graph CUPTI measurements.
- Sequential ABBA: baselineR1,candidateR1,candidateR2,baselineR2. Report each raw
  native median and both repeat speedups; paired speedup=sqrt(R1*R2). Group
  geomeans use only included tokens. Do not pool timings or select minima.
- Raw JSON, successful log, AUTO cache per token, routing histograms, complete
  tracked source hashes, helper hashes and software/environment/GPU identity retained.
- Baseline gated weights use up64/gate64; candidate uses up16/gate16. This is
  the sole preparation parameter difference; source selector and audited native
  preparation changes establish the expected value. FC2 weights stay ordinary.

## Standalone T4 smoke (not primary evidence)

Run only after the GPU/cache owner clears the source-arm switch. Expose one GPU.
The baseline command uses the current upstream baseline; substitute the approved
candidate commit and `--gated-group-size 16` for the candidate arm.

```sh
cd /workspace/flashinfer-w4a4-split-dynamic-n
CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 \
TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0 \
FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0 \
.venv/bin/python scripts/unfused-blockscaled/run_split_benchmark.py \
  --repo baseline --expected-head a65d5b09e7e4c4c5c160b0161c48becd100b3970 \
  --image nvcr.io/nvidia/pytorch:26.05-py3 \
  --weight-format mxfp8 --gated-group-size 64 --tokens 4 \
  --output results/mxfp8-unfused-baseline-smoke-t4.json \
  > results/mxfp8-unfused-baseline-smoke-t4.log 2>&1
```

For mixed W4A8, use `--weight-format mxfp4` and a distinct output name.
Use `run_campaign.py --help` for sequential ABBA with validated optional baselineR1
and candidateR1 reuse. Both arms use the frozen common helper and sweep.
`preparation_contract.py` verifies the native benchmark preparation-only diff,
unchanged routing/quantizers/timer, identical helper bytes, and identical native
runner constructor plus seeded activation initializer (the entire dynamic-bucket
policy). `summarize_results.py` verifies chronology/provenance before reporting.

## Native integration proposal

`native-proposal/bench_moe_deepseek.py` adds opt-in selectors
`--backends cute-dsl-mxfp8,cute-dsl-w4a8 --no-fused-finalize` and calls the same
helper. Existing defaults and existing backend behavior are unchanged. Copy the
helper to `benchmarks/bench_cute_dsl_mxfp8.py` and apply the companion native patch
after review. The native extension was committed locally as benchmark-only commit `5b9d2f6d`;
the initial candidate smoke exercised the same numerical pipeline. A subsequent
stable runner hash preserves native bucket reuse across token points and includes
mode, architecture and tactic-catalog contracts; initial v1 smokes are diagnostic
only. Primary data uses frozen v2 helper bytes. The baseline
checkout remains unmodified and uses the task-local adapter. No production API extension, extra test file, or optional CAKE import.

GPU full-chain compile/runtime and numerical smoke are still required before
collecting primary evidence. Rigorous correctness/sanitizers remain deferred to
retained optimizations per the user's iteration preference.
