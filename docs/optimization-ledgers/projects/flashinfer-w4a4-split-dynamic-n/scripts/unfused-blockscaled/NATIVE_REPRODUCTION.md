# Native before/after reproduction

These commands reproduce the native workload; existing valid B1 data is reused,
not rerun. Execute one mode per fresh process, in ABBA order per mode. Keep NVFP4
on GPU0 and the two new modes on GPU1, matching their existing B1 GPU identities.
Use the pinned image `nvcr.io/nvidia/pytorch:26.05-py3`, the existing `.venv`,
CUDA13.2/Torch2.12nv26.05, DSL4.7.1 and CUPTI13.4. No 4over6 overrides may be set.

The final native extension is two files: `bench_moe_deepseek.py` and
`bench_cute_dsl_mxfp8.py`. Copy the identical files into a benchmark-only overlay
used by both source arms. The baseline a65 preparation has no layout selector and
uses literal group64. The task-local launcher checks this exact source contract
and installs an explicit group64 shim only in that benchmark process. Candidate
uses its real group16 selector. No production source file or public backend API
is changed in the baseline checkout.

```sh
cd /workspace/flashinfer-w4a4-split-dynamic-n
mkdir -p results/native-overlay-v2
cp candidate/benchmarks/bench_moe_deepseek.py results/native-overlay-v2/
cp candidate/benchmarks/bench_cute_dsl_mxfp8.py results/native-overlay-v2/
sha256sum results/native-overlay-v2/*.py
export OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0
for task_recipe_name in ${!FLASHINFER_NVFP4_4OVER6@}; do unset "$task_recipe_name"; done
```

The archived v2 helper SHA is
`632e8587180b88c2fd867d42a03899c5072b04cdcea0fabc58badfcb883b9b23`.
The driver SHA is recorded beside the local overlay in
`artifacts/unfused-blockscaled/native-overlay-v2/sha256.json`.

Run each baseline command once per required fresh-process repeat; use distinct
log names. These commands are documentation, not permission to rerun retained B1:

```sh
CUDA_VISIBLE_DEVICES=0 .venv/bin/python scripts/unfused-blockscaled/run_native_overlay.py \
  --repo baseline --expected-head a65d5b09e7e4c4c5c160b0161c48becd100b3970 \
  --benchmark-dir results/native-overlay-v2 --gated-group-size 64 --mode nvfp4
CUDA_VISIBLE_DEVICES=1 .venv/bin/python scripts/unfused-blockscaled/run_native_overlay.py \
  --repo baseline --expected-head a65d5b09e7e4c4c5c160b0161c48becd100b3970 \
  --benchmark-dir results/native-overlay-v2 --gated-group-size 64 --mode mxfp8
CUDA_VISIBLE_DEVICES=1 .venv/bin/python scripts/unfused-blockscaled/run_native_overlay.py \
  --repo baseline --expected-head a65d5b09e7e4c4c5c160b0161c48becd100b3970 \
  --benchmark-dir results/native-overlay-v2 --gated-group-size 64 --mode w4a8
```

Candidate commands use the same overlay and explicit group16. Set `candidate_sha`
to the final measured full commit; these commands also reject uncommitted
production edits:

```sh
candidate_sha=$(git -C candidate rev-parse HEAD)
CUDA_VISIBLE_DEVICES=0 .venv/bin/python scripts/unfused-blockscaled/run_native_overlay.py \
  --repo candidate --expected-head "$candidate_sha" \
  --benchmark-dir results/native-overlay-v2 --gated-group-size 16 --mode nvfp4
CUDA_VISIBLE_DEVICES=1 .venv/bin/python scripts/unfused-blockscaled/run_native_overlay.py \
  --repo candidate --expected-head "$candidate_sha" \
  --benchmark-dir results/native-overlay-v2 --gated-group-size 16 --mode mxfp8
CUDA_VISIBLE_DEVICES=1 .venv/bin/python scripts/unfused-blockscaled/run_native_overlay.py \
  --repo candidate --expected-head "$candidate_sha" \
  --benchmark-dir results/native-overlay-v2 --gated-group-size 16 --mode w4a8
```

Every command invokes native `run_benchmark`: tokens
1,2,4,8,16,32,64,128,256,512,4096,8192,16384; EP8/TP1;10 warmups;100 cold-L2
CUDA-graph CUPTI samples; normal AUTO; per-tensor input quantization outside
timing; unfused finalize. T1/T2 are reported but excluded from retention.
For primary evidence use `run_split_benchmark.py`/`run_campaign.py`, which additionally
preserve source/software/GPU provenance, histograms and per-token AUTO caches.

The two new modes also have literal native CLI selectors on candidate:

```sh
cd candidate
CUDA_VISIBLE_DEVICES=1 ../.venv/bin/python benchmarks/bench_moe_deepseek.py \
  --backends cute-dsl-mxfp8 --ep 8 --tp 1 --no-fused-finalize \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --warmup 10 --iters 100
CUDA_VISIBLE_DEVICES=1 ../.venv/bin/python benchmarks/bench_moe_deepseek.py \
  --backends cute-dsl-w4a8 --ep 8 --tp 1 --no-fused-finalize \
  --num-tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 --warmup 10 --iters 100
```

NVFP4-only selection uses the existing native programmatic
`profile_backend="cute-dsl", profile_cuda=False` filter, as the original frozen
harness does. The literal CLI pairs `--profile-backend` with `--profile-cuda`, so
that pair must not be presented as an ordinary-timing NVFP4-only CLI command.
