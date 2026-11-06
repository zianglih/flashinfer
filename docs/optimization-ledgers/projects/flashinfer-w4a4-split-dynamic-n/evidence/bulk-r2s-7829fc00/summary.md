# Bulk FC2 register-to-shared vectorization

Production is frozen at `7829fc00dc7121341cc40cd4190660507e006490`. This task-local experiment replaces only the
BF16/FP16 bulk FC2 epilogue's scalar register-to-shared stores. GPU2/GPU5 on
fi-w4a4-dyn-n-1024 (c1/ziangli), B200, nvcr.io/nvidia/pytorch:26.05-py3,
CUDA13.2 and CuTe DSL4.7.1. No production or MegaMoE source edits.

## Source contract

Current `_run_bulk` loads32 TMEM rows, leaving each lane one hidden channel's
32/64 token values. It scales/converts, then emits32/64 scalar16-bit shared
stores per thread. MegaMoE's current UBLK R2S loop follows the same scalar
pattern (`epilogue_refactor.py:2881`).

CUTLASS `Copy_Traits<SM100_TMEM_LOAD_16dp256b8x>` gives destination bit layout
`((4,8),(64,2,8)):((64,2048),(1,16384,256))` for a16×64 FP32 rectangle.
Consequently lane//4 selects channel0..7, lane%4 selects a pair of token
columns, alternating register pairs select channel+8, and successive groups
of four registers select the next8 tokens. Two loads cover a warp's32 TMEM
rows. Scaling and BF16/FP16 conversion preserve the operation order.

Those converted register pairs directly match `stmatrix.m8n8.trans` fragment
ownership: lane//4 is the input row/channel and lane%4 its token pair. Four
matrix words cover32 channels and8 tokens. Each source warp lane supplies
shared address `(token8*8+lane%8, warp*32+(lane//8)*8)`. The instruction's
transpose writes the existing token-major shared layout. For64 tokens this
uses8 `stmatrix.x4` instructions instead of64 scalar stores, with two TMEM
loads instead of one. There is no MOVM, register shuffle transpose, or TMEM
rewrite. This differs from the rejected pre-bulk MOVM experiment, which
transposed through TMEM before direct global stores.

Primary references:

- CUTLASS read-only commit b46b16d003484063bca4ed365e44095c4c6ed633,
  `include/cute/atom/copy_traits_sm100.hpp:571-586`.
- CUTLASS `examples/python/CuTeDSL/blackwell/mamba2_ssd/mamba2_ssd.py:3140`,
  using Ld16x256 and transposed StMatrix through `make_tiled_copy_D`.
- [NVIDIA PTX stmatrix](https://docs.nvidia.com/cuda/parallel-thread-execution/#warp-level-matrix-instructions-stmatrix):
  all32 warp threads execute with the same qualifiers; x4 row addresses come
  from all32 lanes; each matrix's row start requires16-byte alignment.

Per-token metadata uses the derived token coordinate
`(register//4)*8+(lane%4)*2+register%2`, with the same final-scale rounding.
The selected variant pads each shared row from 128 to 136 elements (256 to
272 bytes for BF16/FP16), avoiding transposed STSM bank conflicts. It keeps
the existing 64-token/two-stage or 32-token/one-stage output policy, with
capacity checks updated for the 6.25% larger scratch allocation. Operand
stages, fences, barriers, bulk scatter, partial-token guards and the M384
inactive-channel guard are unchanged. All existing output
fallbacks remain unchanged. The scalar control is a frozen module; separate
compiled caches avoid source mutation during comparisons.

## Evidence boundary

Paired full-byte output checks precede timing: 50 existing FC2 metadata/output
contract cases, 24 M384 six-format channel-tail cases, and 24 non-tail
six-format cases all pass for the selected padded variant (98 total). Native
fixed-tactic diagnostics use actual DeepSeek routing,10 warmups/100 cold-L2
CUDA graph CUPTI samples, common preallocated outputs, fallback fatal. No
primary baseline or full-MoE retention runs are part of this experiment.


## Results

All rows below are native FC2 phase medians in microseconds, T16384 actual
DeepSeek routing, H7168/I2048, 256 global/32 local experts, topk8, unfused
finalize. Each case uses the same captured inputs and preallocated output,
10 warmups and 100 cold-L2 CUDA-graph CUPTI samples. Every timed variant also
passes a full-byte output comparison against the frozen scalar control.
These fixed-tactic phase diagnostics do not establish full-MoE retention.

| Mode | Geometry | Order / GPU | Scalar control | Padded STSM |
| --- | --- | --- | ---: | ---: |
| NVFP4 | M256 N256, 2 CTA | forward / 2 | 181.536 | 177.952 |
| NVFP4 | M256 N256, 2 CTA | reverse / 2 | 181.744 | 178.112 |
| NVFP4 | M256 N256, 2 CTA | independent forward / 5 | 181.457 | 177.7605 |
| NVFP4 | M128 N256, 1 CTA | forward / 5 | 193.4885 | 192.0325 |
| MXFP8 | M256 N256, 2 CTA | forward / 5 | 257.057 | 253.9045 |
| Mixed W4A8 | M256 N256, 2 CTA | forward / 2 | 245.504 | 242.224 |
| MXFP8 | M128 N256, 1 CTA | forward / 2 | 279.9525 | 278.416 |
| Mixed W4A8 | M128 N256, 1 CTA | forward / 5 | 264.6405 | 262.817 |
| NVFP4 | M128 N128, 1 CTA | forward / 5 | 181.3445 | 173.2165 |
| NVFP4 | M128 N128, 1 CTA | reverse / 2 | 182.369 | 173.808 |
| MXFP8 | M128 N128, 1 CTA | forward / 5 | 286.561 | 286.1605 |
| Mixed W4A8 | M128 N128, 1 CTA | forward / 5 | 268.257 | 267.9365 |

Repeated NVFP4 gains are 4.5–4.7% lower latency at N128 and 2.0% at N256
with two CTAs. MXFP8/mixed two-CTA N256 improves 1.2–1.3%; one-CTA N256
improves 0.5–0.8%. MXFP8/mixed N128 changes are effectively neutral.

The 98 exact cases include BF16/F16/F32/E4M3/E5M2 output fallbacks,
FP32/BF16/F16 metadata, per-token on/off, N16/32/64/128/256, partial routes,
and M384 inactive-channel/sentinel checks. Six input formats are NVFP4,
FP4/E8M0/SF16, MXFP4/SF32, homogeneous E4M3 and E5M2 MXFP8, and mixed W4A8.
No sanitizer or broad test campaign was run.

## Profiler mechanism and rejected alternatives

NCU native NVFP4 M256 N256, two CTAs (profiler durations are not the timing
metric used above):

| Metric | Scalar control | Unpadded STSM | Padded STSM |
| --- | ---: | ---: | ---: |
| Kernel duration (ns) | 191200 | 241344 | 188544 |
| Shared store bank conflicts | 640117 | 14313426 | 479228 |
| Shared store wavefronts | 4511577 | 16249526 | 2415328 |
| Registers/thread | 126 | 126 | 126 |
| Dynamic shared memory (bytes) | 227840 | 227840 | 229888 |

Unpadded STSM passed exact checks but regressed native NVFP4 two-CTA N256
181.9045→231.8405 us and one-CTA N256 193.3925→244.960 us. Padding removes
its bank-conflict problem; the selected variant halves shared-store
wavefronts without increasing registers or lowering operand stages.

A 128-token/single-stage output slab uses the same 34 KiB as padded
64-token/two-stage scratch and passes exact checks, but regresses to
191.568 us versus 177.7605 us for the selected double-buffered variant
(control 181.457 us). Keep the existing output double buffering.

Two initial native runs exited before GPU execution because a task-local
`profile.py` shadowed Python's stdlib module through `cProfile`. Renaming it
to `profile_native.py` fixed the harness; successful replacements have the
`-v2` suffix. Failed import logs are preserved, not treated as kernel errors.

## Handoff

The selected immutable modules are `bulk_trial/stmatrixpad_utils.py`
(SHA256 `2a4a032ab24946b7d4b9819710221bce131890a6b0dfddf77a69c7d874307ddd`)
and `bulk_trial/stmatrixpad_core.py`
(SHA256 `9908a6b0e6384df7b809868fec7cc867b4a0ad652d47c1b81487306e932456e0`).
`stmatrixpad.patch` restores production import paths for review; it is not
applied. Production integration should remove the now-unused `repeat`
local and run the repository formatter. No separate kernel, new tactic,
public API change, or reference-contract change is proposed.

`collect.py` archives remote raw logs, native result JSON, NCU CSV, generated
PTX/CUBIN resource evidence, and the task-local source into
`evidence/bulk-r2s-7829fc00/`. `source-sha256.json` identifies the experiment
sources. Preserve rejected variants and failed harness logs for reference.
