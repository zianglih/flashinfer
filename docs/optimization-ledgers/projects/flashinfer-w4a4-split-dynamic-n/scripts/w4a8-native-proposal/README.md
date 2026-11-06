# Native W4A8 benchmark proposal

Prepared separately from both measurement checkouts and the frozen W4A4/W4A8
harnesses. Do not apply this patch until the current primary measurements have
finished: their provenance requires the original native benchmark file.

`w4a8-native-benchmark.patch` changes only `benchmarks/bench_moe_deepseek.py`.
`bench_moe_deepseek.py` is the complete proposed replacement. `provenance.json`
records the original and proposed source hashes and frozen adapter hash.

The extension adds opt-in `--backends cute-dsl-w4a8` and
`--profile-backend cute-dsl-w4a8`. The default backend set and `cutedsl`'s existing
W4A4/W4A16 behavior stay unchanged. W4A8 uses public MXFP8 activation and MXFP4
weight preparation, linear input SF, the existing routing operation, ordinary
AUTO pre-warm, and the existing cold-L2 timer. W4A8 requires fused finalize and
rejects per-token NVFP4 scaling. Wrapper/functional, profiler, cache, and optional
initial-quantization flags use the existing driver conventions. No CAKE arm is
introduced or invoked.

## Apply after primary measurements

```bash
project=/Users/ziangli/playground/projects/flashinfer-w4a4-split-dynamic-n
git -C "$project/flashinfer" apply --check \
  "$project/scripts/w4a8-native-proposal/w4a8-native-benchmark.patch"
git -C "$project/flashinfer" apply \
  "$project/scripts/w4a8-native-proposal/w4a8-native-benchmark.patch"
```

For remote reproduction, first copy this proposal directory alongside the
existing scripts. After the primary campaigns finish, the identical
benchmark-only overlay can be installed in both source arms:

```bash
project=/workspace/flashinfer-w4a4-split-dynamic-n
cp "$project/scripts/w4a8-native-proposal/bench_moe_deepseek.py" \
  "$project/baseline/benchmarks/bench_moe_deepseek.py"
cp "$project/scripts/w4a8-native-proposal/bench_moe_deepseek.py" \
  "$project/candidate/benchmarks/bench_moe_deepseek.py"
```

These are proposed copy commands, not actions performed by this task. Retain
the measured implementation commit and frozen adapter with the primary result
tables. Adding this CLI extension later does not require repeating their data.

## Native reproduction command

Run each source/repeat in a fresh process, sequentially in beforeR1, afterR1,
afterR2, beforeR2 order on the same reserved GPU. Set `repo` to the chosen
source checkout and use a distinct log for each repeat. The native command is:

```bash
project=/workspace/flashinfer-w4a4-split-dynamic-n
export CUDA_VISIBLE_DEVICES=0 TRTLLM_ENABLE_PDL=1
export FLASHINFER_DIST_AWARE_AUTOTUNE=0 FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0
export OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
unset FLASHINFER_NVFP4_4OVER6 FLASHINFER_NVFP4_4OVER6_E4M3_USE_256
unset FLASHINFER_NVFP4_4OVER6_ERR_MODE FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH
cd "$repo"
"$project/.venv/bin/python" benchmarks/bench_moe_deepseek.py \
  --backends cute-dsl-w4a8 --ep 8 --tp 1 \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 \
  --warmup 10 --iters 100
```

CUDA graphs, CUPTI, normal AUTO, wrapper execution and fused finalize are the
driver defaults. Initial activation quantization stays excluded. Use the same
CUDA13.2 image and software environment as the saved primary evidence. Report
T1/T2 but exclude them from retention; preserve the existing eight-point decode,
three-point prefill, paired speedup, and geometric-mean definitions.

The existing frozen adapter remains the evidence harness: it also records
per-point histograms, AUTO caches and environment/source metadata that this
native CLI does not export on its own.

## Verification

- Ruff format/lint, Python syntax, and `git apply --check` passed.
- Native input generation, histogram, routing helper, AUTO context, timer,
  campaign loop, CUTLASS and TRTLLM benchmark functions are AST-unchanged.
- CPU traces show identical preparation/calls/timing for existing W4A4/W4A16.
- The proposed W4A8 trace matches the GPU-proven frozen adapter's preparation,
  routing, wrapper calls, AUTO boundary, and 10/100 graph/CUPTI timing.
- CPU CLI checks cover selection, profiler selection, unsupported flags, and
  filtering W4A8 out while profiling an existing backend.
- This proposed native extension has not been GPU-run. Primary GPU evidence
  continues to use the unchanged frozen adapter.
