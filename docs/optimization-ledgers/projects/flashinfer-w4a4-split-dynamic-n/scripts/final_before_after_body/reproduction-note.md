# Correct final before/after reproduction

The original a65 benchmark has the same `_benchmark_single` keyword signature needed by NVFP4 and native TRTLLM, but no MX backend cases. Its weight preparation explicitly calls `_interleave_linear_and_gate(..., group_size=64, dim=1)`.

`candidate/benchmarks/bench_cute_dsl_mxfp8.py` at 8c1a is byte-identical to the helper used for all archived MX before/after arms (SHA256 `632e8587180b88c2fd867d42a03899c5072b04cdcea0fabc58badfcb883b9b23`). Load this benchmark-only helper by an explicit path, without copying any production code into the baseline. Its FlashInfer imports resolve to the selected target repository; all public wrapper calls and native tuning policies therefore come from that source.

For MX modes, call native `create_inputs(n, routing_bias_scale=0.01)` and `_collect_expert_histogram`, then this helper with `gated_group_size=64` for a65 and `16` for 8c1a. Its default `do_autotune=True`, `profile_cuda=False`, `autotune_cache=None` match the archived native adapter exactly. The result latency is milliseconds. It already uses unfused finalization, includes routing/prepare/FC1/requantization/FC2/combine, and excludes initial input/weight quantization. Do not send MX modes to the original `_benchmark_single`.

The concrete self-contained replacement driver is `run_reproduction.py` beside this note. It was parsed/compiled statically; it was not GPU-executed and does not replace the exact archived source/provenance observers. Its independent process imports select the requested source before any FlashInfer import, and its helper hash is asserted.

Use three explicit checkouts in the setup block:

```bash
before_sha=a65d5b09e7e4c4c5c160b0161c48becd100b3970
candidate_sha=8c1a20173cf166b9fc279f6ae3ec5386250c5c5e
trt_reference_sha=aab93f854054de834447bdd8985b8bbd653fb3c8
git clone https://github.com/zianglih/flashinfer.git baseline
git -C baseline checkout "$before_sha"
git clone https://github.com/zianglih/flashinfer.git candidate
git -C candidate checkout "$candidate_sha"
git clone https://github.com/zianglih/flashinfer.git trt-reference
git -C trt-reference checkout "$trt_reference_sha"
for task_repo in baseline candidate trt-reference; do
  git -C "$task_repo" submodule update --init --recursive
done
```

Preserve the existing environment/dependency setup, changing its editable `./control[cu13]` installation to `./baseline[cu13]`. Preserve the native TRT source at aab so the existing same-GPU comparison stays unchanged. Each process selects the source through `sys.path`; the final candidate editable install does not select the source by itself.

Save the driver as `run_native.py` next to these three checkouts. Existing `run_one` and `run_cute_arm` functions can stay unchanged. Change the invocation sequence to:

```bash
run_cute_arm B1 baseline
run_one T1 trt-reference trt 2
run_cute_arm A1 candidate
run_cute_arm A2 candidate
run_one T2 trt-reference trt 2
run_cute_arm B2 baseline
```

This is a **fresh reproduction recipe** for the final before/after sources and workload, not a claim that the archived measurements used this exact schedule or one host. Published before results reuse a65 B1/B2 on B200-83; final A1/A2 and unchanged TRT T1/T2 were measured on B200-92. Remove the public C1/aab→A1/8c incremental orchestration block. Retain it only in the local ledger. No old data needs rerunning for the PR-body correction.
