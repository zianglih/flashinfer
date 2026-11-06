# CAKE versus optimized CuTe DSL W4A16: measured results

**CAKE showed no speedup over our optimized CuTe DSL backend compiled at O2 in this B300 sweep.** Both CAKE backends had higher measured medians on all 16 original projection shapes and all seven supplemental shapes. All 115 workers passed correctness and evidence validation; the independent numerical audit found zero errors.

Speedup is paired CuTe O2 GPU time divided by CAKE GPU time. Values below 1 favor CuTe. The geometric means below weight each shape equally; the reciprocal gives CuTe’s geometric-mean speed advantage.

## Original 16-shape suite

`(N,K)=(6656,19968)` and `(19968,6656)`, each at `M=1,8,32,128,512,1024,2048,4096`.

| M group | Shapes | CAKE native speedup | CAKE tiled speedup | CuTe advantage over native / tiled |
|---|---:|---:|---:|---:|
| All M | 16 | 0.095× | 0.152× | 10.50× / 6.57× |
| M≤32 | 6 | 0.287× | 0.210× | 3.48× / 4.76× |
| M>32 | 10 | 0.049× | 0.125× | 20.35× / 7.97× |

CAKE wins: **0/16 native, 0/16 tiled**. Small M describes decode-like dense GEMM shapes; these timings do not measure serving throughput.

![Historical paired speedups](artifacts/historical-speedup.png)

For example, down projection at M=1 takes **37.184 µs paired CuTe versus 116.417 µs native** (0.319×), and **37.192 µs paired CuTe versus 160.690 µs tiled** (0.231×). Down projection at M=1024 takes **149.882 µs paired CuTe versus 3596.278 µs native** (0.042×), and **149.978 µs paired CuTe versus 1416.895 µs tiled** (0.106×).

## Supplemental shapes

These six distinct shapes from #5138 and the #4941 regression shape use the same BF16-output, calibrated-alpha, preallocated-output and autotuned-CuTe contract. They do not reproduce every output ownership, dtype, alpha or tuning variant in #5138. All times below are microseconds. Each CAKE arm has its own bracketing CuTe denominator.

| (M,N,K) | CuTe paired with native | CAKE native | Native × | CuTe paired with tiled | CAKE tiled | Tiled × |
|---|---:|---:|---:|---:|---:|---:|
| (1,4096,4096) | 11.736 | 17.136 | 0.685 | 11.616 | 35.473 | 0.327 |
| (768,2112,2048) | 11.352 | 40.512 | 0.280 | 11.432 | 32.897 | 0.348 |
| (7,4160,192) | 4.768 | 5.664 | 0.842 | 4.760 | 5.808 | 0.820 |
| (13,11008,128) | 4.976 | 6.272 | 0.793 | 4.984 | 6.240 | 0.799 |
| (17,3072,3072) | 9.712 | 20.992 | 0.463 | 9.736 | 12.576 | 0.774 |
| (16,1024,1024) | 5.824 | 9.344 | 0.623 | 5.736 | 5.984 | 0.959 |
| (256,4096,4096) | 12.448 | 137.121 | 0.091 | 12.448 | 51.553 | 0.241 |

Supplemental geometric means are **0.443× native** and **0.540× tiled**, with **0/7 wins** for either backend. The closest result is tiled at `(16,1024,1024)`: 0.959×, or about 4.3% longer GPU time. Its CuTe controls select different tactics and span 3.12%, so this small difference deserves more restraint than the large projection gaps. Both bracketing CuTe medians are still below the tiled median.

Across all 46 comparisons, no slower/faster conclusion reverses when the
paired mean is replaced by either individual CuTe control. At the closest
tiled case, those endpoint ratios are 0.944–0.973×. Fresh autotuning selected
different A tactics in 13 of 23 shapes, so control variation includes tactic
selection variation.

## Measurement and validation

- **Source:** main `e500442f83fe9aac7969eb1c8731b6921fa6f180`; the dense CuTe implementation retains #4686’s 30 tactics, with the single O3→O2 compile-option patch. Every CuTe arm freshly autotunes at exact M and verifies the actual selected tactic and O2 compile call. #4941’s separate untuned selector is not included. This is an O2 baseline comparison, not an O2-versus-O3 experiment.
- **CAKE:** source-identical to #5138 head `c636be773cdd04ba4cccdb2b4209e94dfffb8822`. Native/tiled production dispatch is unchanged, including CAKE’s separate NVCC/host `-O3` settings. Those compiler options are distinct from CuTe DSL O2.
- **Hardware/software:** one B300 SXM6 AC GPU (SM103, GPU 0 on `hu-pdx-10`), image `nvcr.io/nvidia/pytorch:26.05-py3`, driver 590.48.01, CUDA/nvcc 13.2/13.2.78, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CuTe DSL 4.7.0. Full package inventories and the GPU UUID are recorded in every worker JSON.
- **Sequence:** A1 CuTe O2 → native → A2 CuTe O2 → tiled → A3 CuTe O2, five fresh processes per shape. Native ratio is `mean(A1,A2)/native`; tiled ratio is `mean(A2,A3)/tiled`, using each worker’s median.
- **Timing:** one CUDA Graph + PDL + cold-L2 CUPTI measurement per worker, five warmups and 30 samples. The GPU activity span includes split-K partial and reduction work. Weight preparation, JIT, autotuning, allocation and the preceding L2 flush are outside the reported time. Event fallback is forbidden.
- **Inputs/correctness:** identical canonical NVFP4 weights and BF16 activations per shape, separate backend layout preparation, calibrated FP32 alpha and preallocated BF16 output. One seeded input per shape passes the unchanged FP32-reference tolerance `rtol=atol=0.015`, finite checks, and within-backend bitwise eager/graph repeatability. Cross-backend bitwise equality and exhaustive numerical coverage are not claimed.
- **Evidence:** 115/115 complete and valid workers, 3,450 raw timing samples, zero worker failures, zero independent numerical-audit errors. The maximum CuTe A1/A2/A3 span is 3.12%; historical maximum is 2.90%. There is one 30-sample candidate worker per backend and shape, so near-parity differences are descriptive rather than confidence claims.

## Interpreting the PR body

#5138 does not identify the exact kernels and commits behind “Live FlashInfer” and “Exact incumbent.” Its “CuTe-DSL-prepared ABI” also differs from the current SM100 CuTe prepared layout. These new ratios therefore answer the comparison against our explicit #4686/O2 denominator; they do not reproduce or refute the PR’s original ratios.

The original projection matrix uses CAKE’s generic routes. Several supplemental dimensions activate exact-shape specializations, and they remain separate above. The [source audit](source-audit.md) verifies dispatch, layouts, launch arithmetic and timing symmetry. It finds no extra timed preprocessing or repeated GEMMs in the CAKE arms. Resource and launch counts alone do not establish the bottleneck behind the measured slowdown.

## Reproduction and raw evidence

- [Method, environment and commands](README.md)
- [All raw worker medians, selected tactics, drift and per-worker JSON/log links](artifacts/full-summary.md)
- [Machine-readable summary](artifacts/full-summary.json) · [CSV](artifacts/full-summary.csv) · [Independent numerical audit](artifacts/numerical-audit.json)
- [Source manifest](source-manifest.json) · [O2 patch](cute-o2.patch) · [Source audit](source-audit.md)
- [Plot PNG](artifacts/historical-speedup.png) · [Vector PDF](artifacts/historical-speedup.pdf)
- [Complete archive: raw results, canonical input cache and compiler/tactic caches](artifacts/benchmark-evidence.tar.gz) · [SHA256](artifacts/benchmark-evidence.sha256) · [Archive file list](artifacts/archive-files.txt)
- [Full run log](artifacts/full.log) · [Setup log](artifacts/setup.log)

The complete archive was checked locally, and the temporary benchmark devbox
was released after the raw evidence and final plots were preserved. The
[cleanup log](artifacts/devbox-cleanup.log) records the deletion.

Sources: [#4686](https://github.com/flashinfer-ai/flashinfer/pull/4686), [#4941](https://github.com/flashinfer-ai/flashinfer/pull/4941), [#5138](https://github.com/flashinfer-ai/flashinfer/pull/5138).
