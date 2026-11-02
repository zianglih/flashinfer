# Reproduce the CUDA 13.0 W4A16 comparison

This is a fixed-choice comparison of the complete W4A16 pipeline, not an autotune sweep. Sources are pre-PR `002529e17b22567a071091053c6c4dc2a55e050e` with its historical benchmark-only adapter (`8078d09b…`) versus retained `a620ce7790b32f7f0ae524a811417d2c6cee1152`. Both use BF16 input/NVFP4 weights and unfused finalization. The `--include-activation-quant` benchmark option performs no input quantization in this W4A16 arm.

V3/V41F/K3 use the original 64-row gated layout before and new 16-row layout after. N3U uses ReLU² and has no gate/up interleave. EP/TP select rank-local expert/intermediate dimensions; no network communication is timed. Before uses standalone preparation; after gathers activations within FC1.

## Sources and runtime

Use `nvcr.io/nvidia/pytorch:25.11-py3` on B300 with the native Torch/CUDA toolkit intact. The recorded box has driver 595.91.07, container CUDA 13.0.2 and NVCC/PTXAS 13.0.88. CuTe DSL 4.8.0 includes NVVM 13.4.59 inside its compiler library; this is explicitly distinct from the system toolkit. Exact pins and loaded-library hashes are in `../runtime/`.

The compact replay payload contains all observer code, source manifests, pinned submodule revisions, before benchmark adapter, exact cache dictionaries, and route/winner expectations. No historical timing arrays are needed. `historical-input-projection.json` binds each compact expectation to its original path/SHA256. The original frozen manifest is preserved separately; `harness/frozen-provenance.json` is explicitly the compact replay manifest, not an assertion that its bytes were used by the measured run. Original full-run manifests remain in the fresh job receipts.

```bash
# Working directory: this reproduction payload.
python reconstruct_sources.py
python -m venv --system-site-packages ../venv
# Preserve native Torch and system NVCC. Install only the exact runtime pins.
env -u PIP_CONSTRAINT ../venv/bin/python -m pip install -r ../runtime/pins.txt
../venv/bin/python harness/configure.py --cache-root ../cache --output ../results
```

Source reconstruction obtains exact Git revisions and pinned submodules, applies only the archived before benchmark adapter, and verifies every file against the measured source manifests. The source tarballs are not duplicated in this incremental evidence archive. `configure.py` retains every cache key/tactic and updates only runtime metadata, explicitly marked in the rebound receipts. It creates source-specific persistent C++/CuTe cache directories; never seed them with CUDA 13.2 compilation artifacts.

## Fresh runs

A separate smoke (4/4096 tokens) compiles both arms and saves native compiler identity before the full run:

```bash
../venv/bin/python harness/run_pair.py --config harness/config.json \
  --job ep-v3-w4a16 --gpu 0 --tokens 4,4096 \
  --output ../smoke --dump-compiler
```

The compiler flags are only `CUTE_DSL_KEEP=ptx,cubin` and an owned dump directory; no compiler optimization change. Full timed runs omit those flags. The observer compiles/warmups before measurement, freezes tactic caches, and rejects profiling during the measured loop or CUPTI fallback.

With all eight GPUs idle, use one GPU per model/topology; each process runs its before/after/after/before phases sequentially:

```bash
gpu=0
for job in ep-v3-w4a16 ep-v41-flash-w4a16 ep-kimi-k3-w4a16 ep-nemo3-ultra-w4a16 \
           tp-v3-w4a16 tp-v41-flash-w4a16 tp-kimi-k3-w4a16 tp-nemo3-ultra-w4a16; do
  ../venv/bin/python harness/run_pair.py --config harness/config.json \
    --job "$job" --gpu "$gpu" > "../${job}.launcher.log" 2>&1 &
  gpu=$((gpu + 1))
done
wait
python audits/analyze_cuda130.py ../results --output ../audit
```

The full observer command, resolved environment, source hashes, cache hashes, GPU UUID, times, native stdout SHA, strict CUPTI activities, routing, and telemetry are captured per phase. Settings include `FLASHINFER_CUDA_ARCH_LIST=10.3a`, `FLASHINFER_DIST_AWARE_AUTOTUNE=0`, `TRTLLM_ENABLE_PDL=1`, `FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1`, `--functional-api`, `--w4a16-only`, `--no-autotune`, `--no-fused-finalize`, 10 warmups and 100 samples.

Tokens are 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384. Eight jobs × 13 tokens × four phases × 100 samples = 41,600 fresh samples. Reports use all 104 cases; plots/aggregates exclude tokens 1/2, leaving 88 cases. Each arm latency is the geometric mean of its two phase medians; signed speedup is `(before / after − 1) × 100`. Repeat stars use either arm's `(max phase median / min phase median − 1) × 100 > 1%`. No clock-based exclusion is applied. Published tactics are frozen across the runtime change; these results do not establish their optimality on CUDA 13.0.
