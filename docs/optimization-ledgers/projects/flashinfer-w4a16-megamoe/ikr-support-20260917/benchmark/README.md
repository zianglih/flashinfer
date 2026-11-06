# Default-path IKR support regression check

Compare baseline `4bc278892b3ced0a8c81501f858de517931e2ae9` against an isolated source snapshot matching final commit `1098a348a1b2a4457cafba4e5263609451914043`. Both arms keep in-kernel FC2 reduction **disabled** and retain deterministic external FP32 weighted combine. Both construct the same weight pack without explicit global scales; baseline defaults and final workspace alphas are verified as identical unit FP32 vectors.

The worker and orchestration adapt the existing PR5019/PR5279 comparison harness. `native/` contains byte-exact copies of the baseline distributed benchmark and its DeepSeek workload module, verified by `native-manifest.json`. This is the historical PR workload: H7168, I2048, 256 experts, top-k8, EP8, global tokens 1–8192 in powers of two. Each arm uses native full autotuning, 3 warmups and 100 cold-L2 CUDA-graph CUPTI samples. Latency is the median of per-sample rank-MAX GPU activity spans for routing plus public `layer.forward`; setup, input/weight preparation, compilation, tuning, capture and L2 flushing are outside timing. No split benchmark is run.

Both arms run sequentially on the same dedicated 8×B300 node with `nvcr.io/nvidia/pytorch:26.05-py3`; full software evidence is in `../gpu-setup/verified.json`. Numerical tests must release GPU ownership before launching this benchmark. `prepare.py` performs CPU-only upload and independent task-local Git-worktree creation, freezing all modified tracked files and recording SHA256 manifests. Both worktrees share read-only build dependency trees. The benchmark uses fresh per-arm caches. `CUTE_DSL_KEEP=ptx,cubin` saves generated artifacts; rank-specific dump paths avoid output races, with no extra profiler run. CuTe reuses sanitized dump filenames across configurations, so these files retain only the latest emitted specialization for each filename; codegen comparisons do not imply all autotune variants were separately captured.

```bash
# Local, once source is final and uploaded:
python3 ikr-support-20260917/benchmark/prepare.py

# Dedicated devbox; run only after numerical validation yields GPU ownership:
/workspace/mega-ikr/venv/bin/python /workspace/mega-ikr/ikr-benchmark/run.py \
  --root /workspace/mega-ikr/benchmark-sources \
  --output /workspace/mega-ikr/ikr-benchmark/results-001 \
  --implementations baseline,current \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192 \
  --iters 100 --timeout 3600
```

Full fixture and output hashes, selected configurations, per-rank results and all timing samples are recorded. Repeated-output/finite checks are smoke checks only; separate numerical tests establish correctness. Sequential run order does not eliminate temporal drift, and small timing changes require cautious interpretation.

## Completed evidence

- Final source: `1098a348a1b2a4457cafba4e5263609451914043`; isolated AFTER worktree retains baseline Git HEAD, with all 21 changed files verified byte-for-byte against final commit by `after-commit-verification.json`.
- Both full 14-row sweeps passed on all eight ranks, with identical canonical weights, inputs/routes, effective unit alphas, selected tactics and all 112 paired output hashes. Every row contains 100 raw CUPTI samples.
- 8–8192 geometric mean BEFORE/AFTER speedup: **0.999521×**. Per-row variation is retained in [the paired table](collected/results-001/comparison.md); the measured aggregate is effectively unchanged. Sequential runs retain temporal drift and do not establish statistical significance.
- Fresh setup/JIT/tuning/sweep wall times: BEFORE **530.04 s**, AFTER **498.60 s**. Both processes exited successfully and GPUs were idle afterward. The owned devbox was released after independent artifact verification; see `../gpu-setup/release-receipt.json`.
- Latest retained rank-0 MegaMoE, BF16 input staging and TopkReduce CUBINs are byte-identical across arms; instruction/encoding hashes and resource reports match. These are the final emitted specializations, not a complete archive of every tuned variant. [Codegen evidence](collected/results-001/codegen-comparison.json). MegaMoE raw cuobjdump reports REG96, STACK0, static SHARED1024, LOCAL0 in both arms; dynamic shared-memory allocation is not represented by that static SHARED field.
- Recorded runtime maps confirm `/usr/lib/x86_64-linux-gnu/nvshmem/13/libnvshmem_host.so.3.6.5` in both arms.
- [Historical three-way table](collected/results-001/historical-comparison.md) compares archived pre-merge `4d183b83` on node15 with post-merge `4bc27889` and final `1098a348` on node129. Pre-merge/final 8–8192 geometric mean is **1.005964×**. All archived canonical weights/inputs/routes and unit-alpha hashes match; archived output hashes do not exist, so cross-version bitwise output parity is not asserted. Cross-node differences preclude causal attribution.
- Scope is static unit alphas with default external FP32 combine; no IKR or per-forward runtime alpha-copy performance claim. Separate numerical validation covers those behaviors.

Reproduce local historical comparison:

```bash
python3 ikr-support-20260917/benchmark/historical_report.py \
  --archived pr5279-comparison-20260917/benchmark/collected/results-002/results-002/ours \
  --results ikr-support-20260917/benchmark/collected/results-001
```
