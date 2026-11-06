# Dense W4A16 CAKE versus CuTe DSL: source audit

Audited checkout: `flashinfer/`, upstream main `e500442f83fe9aac7969eb1c8731b6921fa6f180`, with the single local CuTe O2 change in [cute-o2.patch](cute-o2.patch). Source references below use verified one-based lines. This is a source and harness audit; launch counts are derived from code, not profiler measurements.

## Source and compiler provenance

- The dense CuTe dispatcher, kernel, and kernel utilities have no changes between #4686 merge `b5993208e1ff5b86330e449ef270de15033e048f` and this main revision. The kernel and kernel utilities also match historical benchmark commit `100e95275d55280c110c66e9a4693b07b86ff4d4`.
- The retained search space is 15 structural tile/cluster combinations times both raster directions: **30 tactics**. Public output channels map to the kernel M mode, and public activation rows map to its N mode. [Tactic enumeration](flashinfer/flashinfer/gemm/gemm_bf16_fp4_cute_dsl.py:611)
- The requested O2 change applies only to the SM100/103 `cute.compile` call: `--opt-level 2 --enable-tvm-ffi`. [Compile site](flashinfer/flashinfer/gemm/gemm_bf16_fp4_cute_dsl.py:708)
- CAKE retains its production NVCC `-O3 --use_fast_math` device build and host C++ `-O3`. These are distinct compiler settings from CuTe DSL's optimization level. [Device build](flashinfer/flashinfer/jit/blackwell_bf16_fp4.py:152), [host build](flashinfer/flashinfer/jit/blackwell_bf16_fp4.py:177)
- #4941 head `5af0b7575a37c1654c821dcab138aa8422fa7488` contains O2 plus an additional no-autotune fallback selector. This comparison does not import that selector; it uses fresh production autotuning. CAKE's audited Python/JIT/CUDA files match #5138 head `c636be773cdd04ba4cccdb2b4209e94dfffb8822`.

## Prepared layouts and kernel organization

All three arms start from identical canonical E2M1 weight bytes and E4M3 block scales, and prepare their own backend layout before timing.

| Backend | Prepared weight | Prepared scales |
|---|---|---|
| SM100/103 `cute-dsl` | uint8 `[N,K/2]` | Canonical 128x4 swizzled buffer, exposed as a six-dimensional MMA view |
| `blackwell-native` | uint8 `[N,K/2]` | Linear E4M3 `[N,K/16]` |
| `blackwell-tiled` | int32 `[K/16,2N]` | S0E5M3 uint8 `[K/16,N]` |

Sources: [SM100 CuTe preparation](flashinfer/flashinfer/gemm/gemm_bf16_fp4_cute_dsl.py:421), [CAKE native/tiled preparation](flashinfer/flashinfer/gemm/gemm_bf16_fp4_blackwell.py:88). Consequently, #5138's “CuTe-DSL ABI” label does not identify the current #4686 SM100 CuTe implementation. Prepared tuples are not interchangeable.

CuTe's dense kernel decodes weights to BF16 and uses TCGen05 BF16 MMA with FP32 accumulation; its MMA dtype follows the BF16 activation operand. [Kernel contract](flashinfer/flashinfer/gemm/kernels/cute_dsl/dense_gemm_bf16_fp4_sm100.py:29), [MMA dtype assignment](flashinfer/flashinfer/gemm/kernels/cute_dsl/dense_gemm_bf16_fp4_sm100.py:566)

The generic CAKE tiled kernels instead convert fragments to FP16 and execute warp-level `mma.sync.aligned.m16n8k16.row.col.f32.f16.f16.f32`. This describes internal arithmetic; the benchmark's public activation and output tensors remain BF16. [M32 conversion](flashinfer/csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_generated_sm103.cu:72958), [M32 MMA](flashinfer/csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_generated_sm103.cu:73014), [M64 MMA](flashinfer/csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_generated_sm103.cu:88840)

## Production dispatch versus exact specializations

The original 16 rows use `(N,K)=(6656,19968)` and `(19968,6656)`, each with `M=1,8,32,128,512,1024,2048,4096`. They satisfy the CAKE shape requirements, including tiled `N%64=0`.

| Original matrix | Selected CAKE route |
|---|---|
| Native, all 16 rows | Generic native TMA, public output tile 16x64 |
| Tiled, M=1/8/32 | Generic persistent warp M32/K128 |
| Tiled, M=128/512/1024/2048/4096 | Generic persistent warp M64/K128 |

[Dispatcher](flashinfer/csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_binding.cu:666) contains exact native branches for `(M,N,K)=(1,4096,4096)` to split-K2, and `(768,2112,2048)` to GroupM128. Separately, [kernel metadata](flashinfer/csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_kernel_specs.h:151) selects exact tiled kernels for `(17,3072,3072)` and `(768,2112,2048)` when explicit alpha and PDL are both enabled. None of these exact cases occurs in the original 16 rows. The supplemental PR-body cases should therefore remain a separate result group.

## Launch arithmetic for the down projection

For `(N,K)=(6656,19968)` on the benchmark's 148-SM SM103 device:

| Public M | Native | Tiled |
|---:|---|---|
| 1 | Grid `104x1`: 104 CTAs; tile 16x64; 312 K64 iterations per CTA | 104 CTAs; tile 32x64; 156 K128 iterations per logical tile |
| 1024 | Grid `104x64`: 6,656 CTAs; tile 16x64; 312 K64 iterations per CTA | 1,664 logical 64x64 tiles over 148 persistent CTAs; 11 or 12 tiles per CTA; 156 K128 iterations per logical tile |

Native uses 512 threads and 107,520 bytes dynamic shared memory per CTA. Tiled uses 160 threads, with 218,112 bytes for M32 and 73,728 bytes for M64. These are launch settings, not measured occupancy. Sources: [native launch/grid](flashinfer/csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_binding.cu:441), [tiled persistent grid](flashinfer/csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_binding.cu:560), [native resources](flashinfer/csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_kernel_specs.h:17), [tiled resources](flashinfer/csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_kernel_specs.h:149), [native K loop](flashinfer/csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_generated_sm103.cu:3744), [tiled M32 work loop](flashinfer/csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_generated_sm103.cu:72889), [tiled M64 work loop](flashinfer/csrc/blackwell_bf16_fp4/flashinfer_blackwell_bf16_fp4_generated_sm103.cu:88653).

The native `K%256` dispatcher condition chooses the TMA path; the generated kernel's inner K step is 64. Native does not gain the GroupM128 route merely because M is large.

## Harness symmetry and interpretation limits

- Each arm calls the public API once per captured graph with backend-specific prepared tensors, identical alpha mode, `enable_pdl=True`, and a preallocated BF16 output. [Preparation and call](scripts/bench_worker.py:537)
- CuTe tunes with the exact M bucket and repeats that bucket override during runtime cache lookup. The worker rejects fallback tactic `-1` and records actual selected tuples and O2 compile calls. CAKE uses its fixed production dispatcher. [Runtime/tuning path](scripts/bench_worker.py:585)
- JIT, preparation, allocation, and graph-resource warmup precede timing. CAKE's actual selected source files are checked against the checkout hashes. [Source guard](scripts/bench_worker.py:382), [graph stream prewarm](scripts/bench_worker.py:411)
- Final timing is one call to the unchanged CUPTI helper with CUDA graphs, cold L2, five warmups and thirty samples. It measures first GPU activity start through last GPU activity end, including both split-K partial and reduction kernels when present. Python dispatch, host descriptor encoding, and the preceding L2 flush are excluded. [Timing call](scripts/bench_worker.py:711), [CUPTI aggregation](flashinfer/flashinfer/testing/utils.py:1285)
- The old direct kernel builder and current public-path builder use the same constructor arguments, pointer types, dimension mapping, fragment heuristic, cluster calculation, alpha and PDL settings. Historical input/reference/correctness helper ASTs and the final timing helper ASTs match. This does not imply identical selected tactics across historical and current runs.

No extra timed preprocessing, allocation, or repeated GEMMs were found that would inflate CAKE relative to CuTe. The launch arithmetic establishes which production work runs; it does **not** establish the quantitative cause of a measured slowdown. Bottleneck attribution would require separate profiling.
