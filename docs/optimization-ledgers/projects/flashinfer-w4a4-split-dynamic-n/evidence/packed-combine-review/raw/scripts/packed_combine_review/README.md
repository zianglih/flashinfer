# Raw-pair packed FP32 combine experiment

This isolated experiment evaluates a new BF16-pair expansion mechanism. Source is
in `../../flashinfer-packed-combine-review`, an independent detached clone of
`442d2aa53f68b4640c3ab5118a76f1599ff60d34` plus the exact three frozen regular-TMA
review files. All changes remain unstaged. `manifest.json` records source hashes;
`control_finalize.py` is the unchanged retained finalizer from base442.

Only combine changes. The TMA GEMM paths and preparation remain the frozen review
implementation. Public API, invocation ownership, copy alignment, launch geometry,
PDL ordering, runtime token parameter and cache-key dimensions are unchanged.

## Mechanism and prior evidence

The prior packed128/wide256 experiments were rejected; see
`../finalize_vector_experiment` and `../finalize_geometry_experiment`, with the
decision in `../../OPTIMIZATION_LEDGER_2026-10-24.md:236`. Their packed arithmetic
already generated `FMUL2`/`FFMA2`, persistent packed accumulators, and (for the wide
variant) real 256-bit memory operations. Repeating those source substitutions is
not the mechanism here.

The archived wide-row SASS expands each adjacent BF16 pair through `PRMT` plus
two shifts before packed FP32 math. This variant instead loads four raw `Uint32`
words per existing 128-bit copy, expands each word to two FP32 lanes with a shift
and mask, then emits explicit non-FTZ `mul.rn.f32x2` / `fma.rn.f32x2`. Output uses
`cvt.rn.bf16x2.f32 hi, lo`. The 16-byte input/output alignment contract and existing
seven-vector native prefill geometry remain unchanged. The experiment tests
whether removing conversion instructions improves performance; the previous
DRAM-bound profile means instruction reduction alone is not evidence of a win.

PTX `.f32x2` multiply and FMA require SM100+ and PTX8.6; `.rn` without `.ftz`
preserves subnormals. Official reference:
[CUDA13.2 PTX mul](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#floating-point-instructions-mul),
[FMA](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#floating-point-instructions-fma).

## Validation and timing boundary

`probe_exact.py` imports the actual variant source and a frozen control file.
The four smoke checks and 98 extended checks passed exact output-byte equality
and output guards. Coverage includes expanded/permuted layouts; FP32/BF16/FP16
scales; top-k1/2/8/16; no tokens; masked original slot0; all-masked poisoned scales;
every BF16 input bit pattern (including signed/signaling NaNs); infinities;
signed zeros; midpoint and subnormal output rounding; PDL; H24 and intentionally
16-byte-aligned but not32-byte-aligned pointers; and native seven-vector geometry.
The full matrix also exercises the original four-vector permuted geometry.

The arithmetic contract remains original slot0 multiply, followed by valid later
slots' ordered FP32 FMAs. It does not multiply the first *valid* slot. Masking
precedes payload reads and all-masked output is positive zero.

`probe_native.py` captures actual native NVFP4 routing and FC2 output from the
regular-TMA source copy, checks exact bytes, and times only combine. Each process
uses the same captured payload/mapping/scales for all three arms. ABA and BAB
are separate captures, with per-process route/payload hashes recorded; there is
no claim of identical permutation between processes. Timing is10 warmups and100
cold-L2 CUDA-graph CUPTI samples per arm, keeping the captured PDL flag. This is
neither a full-chain benchmark nor an AUTO comparison.

Environment: C1 `fi-w4a4-pipeline-1025`, GPU2 only, B200,
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTeDSL4.7.1. Every shell sources
`scripts/recovery442/env_candidate.sh`; the experiment has its own CuTe cache.
The native candidate cache and frozen source copies are not changed.

Results and retention decision are pending native timing and SASS inspection.
