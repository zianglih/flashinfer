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

PTX `.f32x2` multiply and FMA require SM100+ and PTX 8.6; `.rn` without `.ftz`
preserves subnormals. Official reference:
[CUDA 13.2 PTX mul](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#floating-point-instructions-mul),
[FMA](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#floating-point-instructions-fma).

## Validation and timing boundary

`probe_exact.py` imports the actual variant source and a frozen control file.
The four smoke checks and 98 extended checks passed exact output-byte equality
and output guards. Coverage includes expanded/permuted layouts; FP32/BF16/FP16
scales; top-k 1/2/8/16; no tokens; masked original slot0; all-masked poisoned scales;
every BF16 input bit pattern (including signed/signaling NaNs); infinities;
signed zeros; midpoint and subnormal output rounding; PDL; H=24 and intentionally
16-byte-aligned but not 32-byte-aligned pointers; and native seven-vector geometry.
The full matrix also exercises the original four-vector permuted geometry.

The arithmetic contract remains original slot0 multiply, followed by valid later
slots' ordered FP32 FMAs. It does not multiply the first *valid* slot. Masking
precedes payload reads and all-masked output is positive zero.

`probe_native.py` captures actual native NVFP4 routing and FC2 output from the
regular-TMA source copy, checks exact bytes, and times only combine. Each process
uses the same captured payload/mapping/scales for all three arms. ABA and BAB
are separate captures, with per-process route/payload hashes recorded; there is
no claim of identical permutation between processes. Timing is 10 warmups and 100
cold-L2 CUDA-graph CUPTI samples per arm, keeping the captured PDL flag. This is
neither a full-chain benchmark nor an AUTO comparison.

Environment: C1 `fi-w4a4-pipeline-1025`, GPU 2 only, B200,
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.7.1. Every shell sources
`scripts/recovery442/env_candidate.sh`; the experiment has its own CuTe cache.
The native candidate cache and frozen source copies are not changed.

## Result: not retained

The mechanism works but the phase saving is too small to justify integration.
All 102 direct exact cases and both native orders passed. Each native arm retained
100 valid samples and passed exact bytes again after timing (1,800 samples total).
The raw three-arm medians in microseconds are:

| Tokens | Control → variant → control | Variant → control → variant |
|---:|---:|---:|
|128|4.224 /4.208 /4.192|4.192 /4.192 /4.160|
|8192|44.864 /44.736 /44.816|44.7845 /44.8955 /44.800|
|16384|83.072 /82.912 /83.1355|82.976 /83.072 /82.960|

Prefill improvements are only 0.13–0.23% depending on order, below 0.25 µs. The
expanded native seven-vector SASS confirms the intended reduction:

| Static instruction/resource count | Retained control | Raw-pair variant |
|---|---:|---:|
|Scalar FP32 multiply / FMA|56 /392|0 /0|
|Packed FP32 multiply / FMA|0 /0|28 /196|
|PRMT|224|0|
|128-bit global loads / stores|56 /7|56 /7|
|Registers/thread|80|80|
|Local memory / spills|0 /0|0 /0|

The new conversion uses `SHF` or `IMAD` for the low lane and `LOP3` for the high
lane. Final output conversion remains 28 `F2FP` instructions. The 128-token case
uses 34 registers versus 32 for control. No 256-bit load or TMA replacement is part
of this candidate. Removing arithmetic/conversion instructions barely affects
the measured phase, consistent with the prior memory-bound profile; this run
does not provide a new NCU attribution. No full-chain timing or integration was
performed. GPU 2 is released; all source changes remain isolated and unstaged.

Verified raw archive:
`../../evidence/packed-combine-review/raw.tar.gz`, SHA256
`233655f8bab74530623db553a21c151fbec6d14809828f298cb9a8f3000542f6`.
`conclusion.json` derives the ratios from raw medians, records source hashes, and
verifies the three frozen regular-TMA review files were not changed. The raw
archive includes source, full samples, environment, PTX, cubins, SASS and
register/spill counts. Its captured README predates this final decision; this
file and `conclusion.json` are the final local interpretation.

## Reproduction commands

Provision the independent copy once using `python3 scripts/packed_combine_review/provision.py`
from the local project. It refuses an existing remote destination. On the remote
devbox, from `/workspace/flashinfer-w4a4-split-dynamic-n`:

```bash
source scripts/recovery442/env_candidate.sh
export CUDA_VISIBLE_DEVICES=2
export CUTE_DSL_CACHE_DIR=$PWD/cache/packed-combine-review
.venv/bin/python scripts/packed_combine_review/probe_exact.py \
  --repo packed-combine-review --output logs/packed-combine-review/exact-full.json
export CUTE_DSL_CACHE_DIR=$PWD/cache/packed-combine-review-native
export CUTE_DSL_KEEP_PTX=1 CUTE_DSL_KEEP_CUBIN=1
export CUTE_DSL_DUMP_DIR=$PWD/logs/packed-combine-review/dumps-native
.venv/bin/python scripts/packed_combine_review/probe_native.py \
  --repo packed-combine-review --tokens 128,8192,16384 \
  --variants control,variant,control --output logs/packed-combine-review/native-aba.json
.venv/bin/python scripts/packed_combine_review/probe_native.py \
  --repo packed-combine-review --tokens 16384,8192,128 \
  --variants variant,control,variant --output logs/packed-combine-review/native-bab.json
```

The probes refuse existing output files; select fresh paths for a new run.
`collect.py` retrieves and verifies the evidence archive using the managed HAI
CLI and refuses to overwrite an existing local archive.
