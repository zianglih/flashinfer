# Unstaged regular-TMA AUTO A1 screen

This is a separately named observer for the actual `regular-tma` source checkout at base `442d2aa53f68b4640c3ab5118a76f1599ff60d34`. It does not make Git report a clean tree. It accepts exactly the two modified kernel/host files plus new `blackwell/moe_prepare.py`, all unstaged, and verifies the complete source map and patch against `--experiment-manifest`.

No GPU benchmark has been launched by this preparation task. Run the commands below only after the parent approves the experimental source and the decode gate. A changed source requires a fresh reviewed three-file manifest, full experiment manifest, preflight, and output directory; do not reuse this manifest or relabel existing evidence.

`run_nvfp4_experiment.py` and `run_mx_experiment.py` are generated copies of the frozen helpers. The only differences are strict dirty-source verification, explicit manifest/provenance arguments, the new file's source hash, and the original MX helper directory. The entire measured loop, native AUTO, cache saving, timing, and token sequence are byte-identical. `adapter-equivalence.json` and `cpu-checks.json` record the proof and negative CPU checks. Original helpers and production benchmark files are untouched.

The screen uses the existing 13 tokens `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`, simulated EP8/TP1 with 32 local experts, standard per-tensor quantization, unfused finalize, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. Initial activation quantization remains outside timing. The new payload/SF preparation is inside the actual FC1 call and is therefore included. No fixed tactic or saved AUTO cache is injected. Tokens 1 and 2 remain measured but are excluded from retention decisions. The unchanged primary helper records each token median, AUTO caches, and logs; it does not persist the100 individual timing samples. The separate fixed-tactic diagnostics retain individual samples, and their evidence must not be conflated with this AUTO screen.

## Freeze and CPU preflight

The supplied manifest records the reviewed grid16 source. To freeze a newly approved version, use a new output filename:

```bash
python3 scripts/fc1_regular_tma_auto/experiment_contract.py freeze \
  --repo flashinfer-regular-tma \
  --review-manifest scripts/fc1_regular_tma_experiment/review_snapshots/grid16/manifest.json \
  --output scripts/fc1_regular_tma_auto/NEW-experiment-manifest.json
```

After transferring this helper directory without modifying any active source, run on the existing C1 devbox:

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n
source scripts/recovery442/env_candidate.sh
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0 FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0
export OMP_NUM_THREADS=1
EXPERIMENT=scripts/fc1_regular_tma_auto
MANIFEST=$EXPERIMENT/experiment-manifest.json
OUT=results/regular-tma-auto-grid16-A1
mkdir "$OUT"
.venv/bin/python "$EXPERIMENT/experiment_contract.py" preflight \
  --repo regular-tma --experiment-manifest "$MANIFEST" \
  --output "$OUT/preflight.json"
```

Preflight is read-only apart from its new receipt and launches no GPU work. It verifies unchanged original B1 bytes and all cache files; baseline source hashes; live UUID/index/driver and software; original target/build receipts; actual candidate native sources; pinned outer validators; and the existing routing/quantization/timing preparation contract. The source checkout's native data path must resolve to the existing candidate's native files. No baseline execution command exists.

Native compiled extensions keep `FLASHINFER_WORKSPACE_BASE=/workspace/flashinfer-w4a4-split-dynamic-n/cache/candidate-442`. Each mode gets a private CuTe cache under `cache/regular-tma-auto/<manifest-sha>/<mode>`. That exact CuTe relocation is the only addition to the reviewed recovery environment allowances. Both actual environment and dirty Git status are recorded.

## Approved launch commands only

These commands do run GPUs. They are documentation, not an automatic launcher. NVFP4 uses GPU0; MXFP8 followed by mixed W4A8 uses GPU1. Original B1 is reused unchanged. No A2/B2 is launched.

```bash
MANIFEST_SHA=$(sha256sum "$MANIFEST" | cut -d' ' -f1)
COMMON=(--repo regular-tma --expected-head 442d2aa53f68b4640c3ab5118a76f1599ff60d34 \
        --image nvcr.io/nvidia/pytorch:26.05-py3 --experiment-manifest "$MANIFEST")
CUDA_VISIBLE_DEVICES=0 \
CUTE_DSL_CACHE_DIR="$PWD/cache/regular-tma-auto/$MANIFEST_SHA/nvfp4" \
.venv/bin/python "$EXPERIMENT/run_nvfp4_experiment.py" "${COMMON[@]}" \
  --output "$OUT/A1-nvfp4.json" > "$OUT/A1-nvfp4.log" 2>&1 &
NV_PID=$!

CUDA_VISIBLE_DEVICES=1 \
CUTE_DSL_CACHE_DIR="$PWD/cache/regular-tma-auto/$MANIFEST_SHA/mxfp8" \
.venv/bin/python "$EXPERIMENT/run_mx_experiment.py" "${COMMON[@]}" \
  --frozen-tools results/unfused-baseline-epoch-v2-tools \
  --weight-format mxfp8 --gated-group-size 16 \
  --output "$OUT/A1-mxfp8.json" > "$OUT/A1-mxfp8.log" 2>&1
CUDA_VISIBLE_DEVICES=1 \
CUTE_DSL_CACHE_DIR="$PWD/cache/regular-tma-auto/$MANIFEST_SHA/mxfp4" \
.venv/bin/python "$EXPERIMENT/run_mx_experiment.py" "${COMMON[@]}" \
  --frozen-tools results/unfused-baseline-epoch-v2-tools \
  --weight-format mxfp4 --gated-group-size 16 \
  --output "$OUT/A1-mxfp4.json" > "$OUT/A1-mxfp4.log" 2>&1
wait "$NV_PID"

.venv/bin/python "$EXPERIMENT/experiment_contract.py" verify-results \
  --repo regular-tma --experiment-manifest "$MANIFEST" \
  --preflight "$OUT/preflight.json" --directory "$OUT" \
  --output "$OUT/verification.json"
```

Use a shell with `set -euo pipefail`. Preserve any failed or partial output; do not rerun into an existing directory. Verify-results checks every frozen source/helper/build receipt again, all 39 token rows and cache hashes, input routing histograms, the exact authorized observer hash transition, GPU1 mode ordering, and the exact private cache path. It emits B1/A1 ratios with explicit 1/2-token exclusion flags. This is an initial screen, not completed ABBA retention evidence. Do not compare absolute fixed-tactic GPU5 times with primary GPU0/1 as paired measurements.
