# Runtime alpha copy batching: matched HashInfer experiment

This experiment compares sequential `fc1_alpha` / `fc2_alpha` copies with batched
copies on HashInfer PR #11. Both arms use the same benchmark from this directory.
It supplies unit FP32 runtime alphas through `MoEEpTensors`, so every timed
forward stages scales, as SGLang does with shared workspaces and weight reloads.
Previously these alphas were supplied only in the backend config; the old sweep
did not execute runtime alpha copies. Old results are not a matched control for
this optimization.

## Measurement contract

- C2, NVIDIA B300, `nvcr.io/nvidia/pytorch:26.05-py3` (CUDA 13.2); record actual
  Torch/CUPTI versions and GPU identity in `ENVIRONMENT_JSON`.
- EP4 and EP8, GLM-5 geometry: hidden 7168, intermediate 2048, 256 experts,
  top-k 8. Fixed-seed BF16 inputs, canonical NVFP4 weights, FP32 unit per-expert
  alphas, and precomputed DeepSeek group-routing scores.
- Global tokens: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384.
  Decode retention uses 4–512; report 1/2 without using them for retention.
  Inspect each prefill row independently.
- Full native autotune in each fresh process, distinct empty knob caches.
  Compiled-kernel caches may be shared; selected tuning winners are not reused.
- Three warmups and 100 cold-L2 CUDA-graph replays. Native CUPTI first-to-last
  activity span includes all launch-correlated kernels, MEMCPY and MEMSET
  operations in public forward, including alpha copies. This is a span, not
  the sum of individual operation durations. Graph capture, routing,
  quantization, tuning, compilation and L2 flushing are outside timing.
- Aggregate each sample by MAX across ranks, then take the median of all 100
  samples. No trimming. Raw per-rank samples, rank-MAX samples and all-rank
  selected tactics are retained. No split-MoE arm.
- Reuse the previously validated CUPTI workaround: retain registered callbacks
  and defer `cupti.finalize()` until the full sweep and process group drain.
  The native timer and per-row activity enable/flush/disable are unchanged.
- Two additional untimed forward calls check finite, repeated bit-exact outputs
  and retain SHA256 for before/after comparison. Independent bit-exact reference,
  alpha mutation, shared-workspace layer alternation and graph replay tests are
  separate validation. This benchmark alone does not establish weight-sync safety.

## Run on the devbox

Upload the four frozen helpers `run_arm.py`, `worker.py`,
`cupti_lifecycle.py`, and `bench_cute_dsl_moe_distributed.py` into
`/workspace/hashinfer-alpha-0923`. Extract source snapshots into sibling
`before` and `after` directories, each containing `hashinfer/` and `pyproject.toml`.
Run serially on an otherwise idle node; use the same GPU subset per EP arm.
The runner checks for active GPU processes and refuses existing output folders.

```bash
cd /workspace/hashinfer-alpha-0923
.venv/bin/python run_arm.py \
  --source before --revision '<before commit>' --ep 4 \
  --output results/before-ep4 --compile-cache compile-cache
.venv/bin/python run_arm.py \
  --source after --revision '<before commit plus candidate patch SHA256>' --ep 4 \
  --output results/after-ep4 --compile-cache compile-cache
.venv/bin/python run_arm.py \
  --source after --revision '<before commit plus candidate patch SHA256>' --ep 8 \
  --output results/after-ep8 --compile-cache compile-cache
.venv/bin/python run_arm.py \
  --source before --revision '<before commit>' --ep 8 \
  --output results/before-ep8 --compile-cache compile-cache
```

Each source snapshot is hashed before and after its sweep, as are the four
helpers. The same snapshot timer must be used in both arms. Results contain a
full benchmark log, source/helper hashes, process/environment metadata, the
independent knob cache and one evidence JSONL per rank. No source files are
patched by the runner. The frozen external benchmark imports current HashInfer
namespaces, including `kernel_src.sm100.cutedsl_megamoe`.

Copy results locally or run the comparator on the devbox:

```bash
python3 compare.py results/before-ep4 results/after-ep4 --output comparison-ep4
python3 compare.py results/before-ep8 results/after-ep8 --output comparison-ep8
```

The comparator verifies same node/boot, helper and native timer identity,
matching input/weight fixtures, all 13 rows and 100 samples, shared tactics
across ranks, per-rank MAX reconstruction, and bit-exact paired outputs. It emits
JSON and Markdown with all rows, before/after tactics, decode geometric-mean
speedup, MAD and successive 25-sample medians. Mixed tactic selections should
remain visible when interpreting marginal timing differences.

## Scope and provenance

`cupti_lifecycle.py` is byte-for-byte copied from the September 20 EP4 optimization
harness. The current PR #11 native benchmark is used in both arms, with runtime
alpha staging enabled. `worker.py` only adds observations outside timing;
`run_arm.py` orchestrates source isolation and fresh caches. No sanitizer or
independent PyTorch reference loop is added to the timing sweep.
