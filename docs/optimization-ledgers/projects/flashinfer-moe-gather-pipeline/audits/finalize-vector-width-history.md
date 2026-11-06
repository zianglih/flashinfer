# Shared combine vector width: no new prototype

Keep the current128-bit path. Actual256-bit combine, metadata coalescing/prefetch, and vector-outer traversal have already been tested. Their historical results do not establish a benefit on the current source, and current TP counters identify payload bandwidth rather than instruction throughput as the main limitation. An alignment fallback, new knob, or additional metadata scheme is not justified. No source changes or GPU runs were made for this audit.

Retained source: `2b8eb9d8`, `moe_finalize.py` SHA `2a7d7b445772d6c23d6b7f4cb2e37aceb886e46dd8dbb6998445b345ca478f95`. [Evidence hashes and raw-median replay](finalize-vector-width-history.json) preserve the distinctions below.

## Current contract and simple widening boundary

- `_bf16_vector` (`moe_finalize.py:91–102`) declares fourUint32 words with16-byte alignment. The kernel copies128bits, expands each BF16 pair directly into packed FP32, preserves slot0 multiply and subsequent ascending-slot FMAs, then converts/stores BF16. Four vectors/thread above1024 tokens amortize metadata; they are separated by `threads*8` BF16 elements, not adjacent chunks within one thread. Joining their registers alone cannot form a contiguous256-bit load.
- The shared `moe_unpermute` contract explicitly permits `H%8==0` and16-byte-aligned input/output (`:229–264`). A valid H24 row has48-byte stride, so even a32-byte-aligned base produces alternating16/32-byte row alignment. A contiguous output view with a16-byte storage offset also satisfies the existing contract. A256-bit memory access requires32-byte natural alignment. [PTX alignment rule](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#addresses-as-operands).
- Swap's FC2 scratch is newly allocated by `fused_moe.py:881`; W4's hidden workspace is newly allocated by `moe_w4a16.py:58–88`. Supported benchmark widths are32-byte row-aligned, so these particular inputs can support wider loads. That does not guarantee32-byte alignment of a caller-supplied `moe_output`: the API explicitly accepts it, and the finalizer validates only16-byte alignment. The shared helper also serves other expanded/permuted callers.
- Globally changing four words to eight would therefore narrow supported inputs. Retaining compatibility needs width selection/fallback, head/tail handling, or a stronger private handoff; merely declaring32-byte alignment is invalid. Leaving only16-byte alignment cannot promise native256-bit copies. A width change also changes per-thread ownership and, unless compensated, CTA coverage and parallelism. It is not an isolated instruction substitution.

## Actual historical experiments

Paths below are relative to the old project `../flashinfer-w4a4-split-dynamic-n/`.

**Packed128 / wide256, Oct24–25.** `scripts/finalize_vector_experiment/sparse-r1.json` binds the actual three source hashes,72 edge checks plus six timed exact cases, B200/CuTe4.7.1,10 warmups/100 cold-L2 CUDA-graph CUPTI samples, PDLoff. `wide.py` uses16 BF16/thread,32-byte alignment/H%16, packed FP32 arithmetic, and halves prefill vectors4→2 to preserve the old CTA width. Its comparison includes the change from the old scalar BF16 conversion/arithmetic; it is not a pure width comparison against today's raw-word packed implementation.

| H7168/top-k8 proxy | Control1 | Wide256 | Control2 |
|---|---:|---:|---:|
| T8 expanded |5.600|6.048|5.505|
| T8 permuted |6.144|6.368|6.1275|
| T8192 expanded |46.640|47.456|46.528|
| T8192 permuted |50.304|49.5515|50.3525|
| T16384 expanded |85.472|87.056|85.472|
| T16384 permuted |91.232|90.9605|91.328|

All values are microseconds. The positive permuted rows remain explicit; the outcome was mixed, not universally negative. Random sparse routing, standalone timing, and the older arithmetic/compiler limit extrapolation to current B300 E2E behavior.

**Wider row coverage and prefetch.** `evidence/finalize-geometry-7196/raw/logs/finalize-geometry/prefetch-r1.json` and its source/dumps preserve `wide_row`, which also expands CTA coverage. Captured8192-token SASS contains **32 `LDG.E.ENL2.256` and4 `STG.E.ENL2.256`**, versus control32 `LDG.E.128` and4 `STG.E.128`; both have16 scalar metadata loads. Registers rose59→108, LOCAL/STACK stayed0. This proves real wide memory instructions, not just a larger `CopyUniversalOp` request. It does not prove fewer dynamic instructions for equal work: this variant handles a different tile width. T16384 expanded85.312/85.248→95.488µs; permuted91.120/91.184→95.520µs.

The same archive's `prefetch.py` issues all vectors' payload loads for one valid slot before arithmetic. AtT16384 it loses expanded85.312/85.248→87.5525µs but improves permuted91.120/91.184→86.976µs. `meta.py` coalesces routing/scale reads in each warp then broadcasts with SHFL; it loses expanded85.184/85.1675→89.024µs and permuted91.568/91.552→96.5125µs. These are existing attempted mechanisms with layout-dependent outcomes, not newly discovered missing overlap.

**Vector-outer traversal, Oct27.** `optimization-20261027/finalize-vector/RESULTS.md` binds actualB300/CuTe4.8 exact/native captures. Loop interchange kept128-bit copies and packed arithmetic, but increased static instructions936→1328 for H7168/top-k8/seven vectors and736→1136 for H2048/top-k22. Registers changed80→40 and58→102 respectively. It was rejected before timing; do not describe it as a measured E2E loss.

**Raw-word packed arithmetic.** `scripts/packed_combine_review/README.md` distinguishes the later shift/mask BF16-pair expansion from old PRMT-based packed128/wide256. It preserved the16-byte/H%8 contract, including explicit H24 and16-but-not32-byte-aligned exact cases. Its original phase gains were only0.13–0.23%; current production contains that raw-word mechanism. Consequently, old wide256 binaries are not current-code predictions. Repeating widening now still lacks a new bandwidth/ownership mechanism.

## Present overlap and bottleneck evidence

Current routing/scales load before the sole PDL dependency wait; all expert-output payload loads follow it. No shared memory or CTA barrier exists here. Moving payload before FC2 completion would violate readiness; the old metadata and prefetch proposals do not remove that dependency. Negative routes are masked before reading payload, and ordered slot arithmetic is part of the exact contract.

`profiling/v3-tp-mxfp8-16k/combine-summary.json` binds measured822 to exactly the current finalizer bytes. Its five application-replay diagnostic reports331.136µs,1,877,658,624DRAM read bytes,277,002,496write bytes,84.82% peak DRAM throughput,0.17% L2 hit,22.67% issue activity,92.08% long-scoreboard stalls,0.03% MIO throttle, no barrier stalls,64 registers and no shared memory. This strongly supports bandwidth as the principal limit in that TP case, but is not proof of an absolute bandwidth floor or of every model's behavior.

For current-source-equivalent N3U EP8/T16384/W4A4, `profiling/n3u-ep-w4a4-16k/native-components.json` preserves200 CUPTI samples: combine duration56.608/56.672µs and interval-union extension53.856/53.968µs of558.899/559.299µs E2E. This establishes a roughly10% contribution, **not** a combine bandwidth or instruction diagnosis for EP. Its compiler/environment belong to the recorded campaign; these are not new measurements on the recovery node. Component extensions are not a dependency-DAG proof.

Decision: no distinct simple candidate survives this audit. Preserve the public alignment/rounding/PDL contracts and the frozen performance rows. Do not repeat wide256 or introduce a compatibility branch based only on the current source's128-bit width.
