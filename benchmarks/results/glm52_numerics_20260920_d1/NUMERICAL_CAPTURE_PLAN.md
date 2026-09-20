# Bounded r3 numerical capture

The preserved r3 failure is **N3**, after N1 passed. This diagnostic runs the frozen `6f88c235b658104053761aad15158e954f439a41` benchmark's native shared-weight creation, Split setup/reference and Mega warmup/reference check in N1 → N3 order. Its original `atol=rtol=1e-2` gate remains unchanged. A numerical failure remains exit 1 even when all requested tensors were saved.

- Capture helper: `setup/capture_r3_numerical_failure.py`, SHA256 `84739673d444b9140f569cff5c6d5fe7cf7239ea6fa3e0112b37d24afe663332`.
- Before launch, the separately reviewed parent launcher probes the actual environment and validates the frozen r3 initial/prepared/timing receipts, confirms the prior run failed and GPUs are idle, and creates a new exclusive diagnostic directory. The capture helper independently checks clean source commit, all three benchmark file hashes, unchanged production kernels against `ad0a5e5e78e57070ec7c582efe733cb55cd8839f`, original job/precision flags, and cache boundaries before CUDA initialization.
- Cache reuse is limited to r3's existing `compiled-cache` paths. The new knob path and diagnostic outputs are outside the old run; runtime compilation may append to reused compiler caches. No source, kernel, old result or old log is overwritten.
- Actual r3 metadata confirms PDL enabled, no fused finalize, no per-token activation, routing included, `knobs=None`, and live Mega capacity 1. Split's per-rank 4096 budget is multiplied by EP4 into its original 16384 tuning bound.

After parent approval, its remote launcher command is:

```sh
/opt/sglang/bin/python3 /data/home/ziangli/flashinfer-sglang-megamoe-benchmark-alignment/setup/helpers-glm52-numerics-20260920-d1/run_numerical_diagnostic_remote.py \
  --task-root /data/home/ziangli/flashinfer-sglang-megamoe-benchmark-alignment \
  --run-id glm52-numerics-20260920-d1
```

The launcher uses static loopback torchrun on four GPUs and passes the new `diagnostics/glm52-numerics-20260920-d1/capture` root to the helper. Deployment and execution are owned by the parent; this note records a plan, not a launch or GPU validation claim.

Each of eight rank/case pairs saves a hash-bound `.pt` containing CPU tensors and a `.json` summary. Contents include both arms' raw input/logits/bias; Split padded global BF16 inputs, int32 IDs and FP32 weights; native BF16 per-route FC2 terms and expert ownership mask; Split native BF16 rank partial and NCCL result; Mega staged inputs/IDs/weights, native BF16 route terms and output; and original reference, actual output, strict mismatch mask and thresholds. Empty ranks preserve `(0, 6144)` outputs. The native Mega backend returns the provided output tensor; its external-reduction combine buffer is `(1, 8, 6144)` here.

Snapshots run only outside autotune and graph capture. They synchronize/copy tensors and therefore perturb scheduling. Timing and graph execution are omitted; explicit native generators preserve input/weight seeds, but this does **not** reproduce r3's prior allocator, tuner or graph state exactly. There are no accepted performance measurements. High-precision offline sums are diagnostic calculations, not bitwise emulation of GPU FMA or NCCL's reduction tree.

Local validation: 11 real-Git fixture checks passed in `artifacts/numerical-capture-contract-validation.json`; Ruff and Python compilation passed. No CUDA/NCCL operation was executed by these checks. Source findings and rounding-order hypotheses remain in `artifacts/R3_NUMERICAL_FAILURE_SOURCE_AUDIT.md`; they do not establish the failure's cause.
