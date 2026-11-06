# CAKE versus optimized CuTe DSL dense W4A16

This effort compares both CAKE backends from FlashInfer PR #5138 with the
SM100/SM103 CuTe DSL dense backend optimized in PR #4686, using CuTe O2 to
avoid the compiler regression documented in PR #4941. No PR is modified.

The sweep is complete: **115/115 workers passed**, with zero evidence or
independent numerical-audit errors. See [RESULTS.md](RESULTS.md) for the
measured comparison, plot, raw tables and complete evidence archive.
The temporary devbox was released after the archive and final plots were
saved locally; see `artifacts/devbox-cleanup.log`.

## Source and environment

- Independent checkout: `flashinfer/`, main commit
  `e500442f83fe9aac7969eb1c8731b6921fa6f180`.
- Only production modification: `cute-o2.patch`, changing the SM100/SM103
  `cute.compile` option from `--opt-level 3` to `--opt-level 2`.
- All 30 structural/raster tactics from #4686 remain available. #4941's
  separate no-autotune selector is not imported; every baseline is autotuned.
- CAKE source files match #5138 head
  `c636be773cdd04ba4cccdb2b4209e94dfffb8822`. Its independent NVCC and host C++
  compiler settings remain unchanged.
- `source-manifest.json` records source hashes and the O2 patch hash. Every
  worker records critical source hashes; CuTe workers record the actual O2
  compile setting, and CAKE workers verify the loader's source paths/hashes.
- Devbox: `c2/ziangli/cake-w4a16-o2`, host `hu-pdx-10`, eight B300 SXM6 AC GPUs;
  measurements use GPU 0 sequentially, without other benchmark workers.
- Image: `nvcr.io/nvidia/pytorch:26.05-py3`, the newest CUDA 13.2 PyTorch image
  in the live NVIDIA catalog/release matrix checked on 2026-09-13. Later
  releases use CUDA 13.3 or 13.4.
- Driver 590.48.01, CUDA/nvcc 13.2/13.2.78, PyTorch
  `2.12.0a0+5aff3928d8.nv26.05`, CuTe DSL 4.7.0, CUPTI Python 13.2.0,
  NVIDIA CUPTI 13.2.86, cuda-bindings 13.2.0, TVM FFI 0.1.13.post3. Complete package inventories
  and GPU UUIDs are recorded before timing in worker JSON.

## Measurement contract

The retained historical drivers are copied byte-for-byte into `historical/`
from commit `100e95275d55280c110c66e9a4693b07b86ff4d4` in the prior
`flashinfer-dense-w4a16-perf` project. `scripts/bench_worker.py` adapts the
same input/oracle/correctness method to three public backend calls.

- Each shape runs A1 CuTe O2, CAKE native, A2 CuTe O2, CAKE tiled, A3 CuTe O2.
- Every arm is a fresh process. Every CuTe arm performs fresh production
  autotuning over the legal members of the 30-tactic space, using an exact-M
  tuning bucket. The selected tuple and actual O2 compile calls are recorded;
  a fallback tactic is an error. Fixed-source compiler artifacts may be shared,
  but each arm has a distinct initially absent tactic-cache file.
- All arms use identical seeded BF16 activations and canonical NVFP4 E2M1
  weights/E4M3 block16 scales with a calibrated FP32 alpha. Each backend
  prepares its own weight layout outside timing. Canonical input hashes must
  match before ratios are accepted.
- Output is preallocated BF16. Weight creation/quantization/preparation,
  compilation, tuning, allocations, correctness and graph-stream warmup are
  outside timing.
- Same historical oracle: FP32 activation/dequantized-weight matmul, then
  FP32 alpha multiplication, then BF16 conversion. FP32 reference matmul uses
  highest precision/TF32 disabled. Tolerances stay `rtol=atol=0.015`.
- Each arm requires finite output, reference agreement, bitwise eager
  repeatability, bitwise graph replay repeatability and graph/eager agreement.
  This checks one seeded input per shape. Bitwise checks are within each
  backend; cross-backend agreement is assessed through the shared tolerance
  reference, without requiring bitwise equality between implementations.
- Primary timing: CUDA Graph + PDL, cold L2, five warmups, 30 CUPTI samples.
  Exactly one CUPTI timing call per process; event fallback is forbidden.
  The metric spans first GPU activity start through last activity end for
  the graph replay, including CAKE split-K partial/reduction kernels and any
  gaps. The preceding two-times-L2 flush is excluded.
- Native speedup is `mean(A1 median, A2 median) / native median`; tiled speedup
  is `mean(A2 median, A3 median) / tiled median`. Values above one favor CAKE.
  Baseline drift is reported independently. Sub-1% movements are not claims.

## Workloads and scope

- Primary historical suite: `(N,K)=(6656,19968)` and `(19968,6656)`, each with
  `M=1,8,32,128,512,1024,2048,4096` (16 rows).
- Supplemental suite: six distinct M/N/K triples from #5138, plus the
  #4941 `M=256,N=K=4096` case. They use the same calibrated-alpha, preallocated
  BF16-output, production-autotuned contract as the historical suite.
- These supplemental runs are not a reproduction of every #5138 output
  ownership/dtype/autotune/alpha variant. In particular, FP16-output and
  untuned rows are outside the main comparison.
- The #5138 body does not identify the precise kernels/commits behind its
  "Live FlashInfer" and "Exact incumbent" columns. Its prepared-ABI labels
  also do not identify the #4686 SM100 CuTe backend. This experiment provides
  a new, explicit denominator; it does not reproduce or refute those columns.
- CAKE has exact-dimension specializations for some #5138 shapes; those rows
  remain separate from the original projection matrix in summaries.
- These are GPU dense GEMM timings, not MoE, model or serving throughput.
  Old PR timing numbers are historical context only and are never mixed into
  the new ratios. Failed/unsupported cells remain explicit.

The source audit found no post-#4686 change in the dense CuTe dispatcher or
kernel at the chosen main commit. The historical direct compiler builder and
the new public-API path use matching kernel/scale/PDL arguments; input,
reference and CUPTI helper implementations also match. Fresh autotuning can
choose different tactics than the archived runs, so an old latency must not
be used as the denominator for a new CAKE timing. Complete historical DSL
runtime/TVM-FFI fingerprints were not recorded, which also prevents claiming
binary-identical compiler environments across the old and new experiments.

The remote tree is a source snapshot because `h sync` excludes `.git`.
Reduction verifies all eleven recorded critical source hashes against the
local commit-plus-O2-patch manifest; it does not invent remote Git metadata.

## Reproduction

Setup uses `scripts/setup_remote.sh`. Remote root is
`/hai-workspace/flashinfer-cake-w4a16-comparison`.
For a later reproduction, pin `apache-tvm-ffi==0.1.13.post3` in place of
the setup script's original version range and retain the container's PyTorch.
The script is preserved as executed; all resolved packages are in worker JSON.

```bash
CUDA_VISIBLE_DEVICES=0 CONTAINER_IMAGE=nvcr.io/nvidia/pytorch:26.05-py3 \
  python scripts/run_sweep.py --suite all \
  --output-dir results/full --input-cache-dir results/input-cache \
  --warmup 5 --iters 30
```

Raw worker samples, pre-timing correctness metadata, logs and the sweep
manifest are retained under the result directory. Local setup/launch logs
are under `artifacts/`. A worker failure is retained; a retry uses a new
output directory so failed evidence and tactic caches are not overwritten.

After copying the raw result tree locally, reduction and a separate numerical
audit use the following commands. A complete run requires all 115 workers;
an incomplete snapshot exits nonzero and explicitly reports missing evidence.

```bash
python3 scripts/summarize_results.py --results artifacts/final/full \
  --output-prefix artifacts/full-summary --source-manifest source-manifest.json
python3 scripts/audit_results.py --results artifacts/final/full \
  --summary artifacts/full-summary.json --output artifacts/numerical-audit.json
python3 scripts/plot_results.py --summary artifacts/full-summary.json \
  --output-prefix artifacts/historical-speedup
```

Plotting is CPU-only and requires matplotlib. The source/dispatch audit is
retained in [source-audit.md](source-audit.md), including the different prepared
weight layouts and exact-shape specializations.

## Sources

- https://github.com/flashinfer-ai/flashinfer/pull/4686
- https://github.com/flashinfer-ai/flashinfer/pull/4941
- https://github.com/flashinfer-ai/flashinfer/pull/5138
- https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-26-08.html
