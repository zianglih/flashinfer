# No-transpose epilogue reuse boundary

Preparation only; no candidate kernel edits, CUDA compilation, or GPU launch.
New baseline is corrected `aab93f854054de834447bdd8985b8bbd653fb3c8`.
Parent owns mapping/design integration. Old source and measurements remain frozen.

## Reusable code with no SF publisher

The prior independent `flashinfer-physical-n16-review` is the appropriate donor,
not the later publisher/readiness/localwait compositions. Its core SHA is
`1e46f56a9932a248b592bcd9441e3a3594b0cc460a7b0218f1ac2ae8df1181f6`;
utils SHA is `e14d3300a97fa508b0039065a6b29b876a0e14d20a5456ef18bf0a662c168274`.

- `blackwell/utils.py:219`, `_blockscaled_load16x16_native`: direct
  `Ld16x256bOp(Repetition.x2)`, exactly16TMEM columns, eight FP32 registers/lane.
  Up and gate use separate16-row fragments within each warp's32-row datapath.
- `utils.py:231`, `_blockscaled_reorder_packed_fp4`: three butterfly exchanges
  after FP4 conversion to assemble eight contiguous channels of one token in
  each lane's32-bit store. It removes FP32 TMEM round trips, not all ownership
  conversions; this packed-register exchange remains a candidate design cost.
- `utils.py:566`, `_run_narrow_fp4`: loads up/gate, calls the existing `_activate`
  arithmetic, performs SF reduction/rounding, converts once to FP4, and stores
  output/SF directly in existing routed layouts. SF16 requires four maxima/lane,
  each reduced with three shuffles at offsets4/8/16 (12shuffles), plus the three
  packed-nibble exchanges. All source/data ownership changes remain warp-local.
- `utils.py:1215`: narrow dispatch before generic32-token transpose path.
  Final `fence_view_async_tmem_load` remains in the shared `run` tail.
- The prior core's entire diff is24lines: physical B/C16 eligibility,16-column
  accumulator alignment at all three pointer sites, and epilogue flag plumbing.
  It leaves original operand/SF loaders, SF S2T publication on MMA warp, role
  loops, stages, cache hints, preparation, scheduler, and output contracts intact.

The minimal composition onto aab would port only those helpers/dispatch and
approved allocation/alignment changes. Preserve aab's retained proxy fence.
Do not import `sf_publisher`, compact SFB layout, separate SFA pipeline, extra
TMEM SF ring, distributed-TMA producer loops, or startup padding experiments.
This is a donor plan, not an edit authorization before the mapping is settled.

## Numerical and geometry boundaries

The measured gate was N16 gated NVFP4 FC1 with generated FP4 output (SwiGLU or
Geglu), E4M3/SF16. It retained four operand stages,288threads, two accumulator
stages,128 allocated TMEM columns, and4096B SFB/source stage. True C16 reduced
accumulator occupancy from64 to32 logical columns but did not reduce rounded
TMEM allocation. It used regular payload TMA and the original cp.async SF path.

Per-token public FC1 produces BF16, so it stayed on original physicalN32;
code inside `_run_narrow_fp4` mentioning per-token scaling or SF32 was not
admitted by that core's gate and is not prior validated coverage. Ordinary
BF16/F16/F32/FP8 outputs, SF32, nongated Relu2, FC2, N32/N64 and larger tiles
need their own mapping/contracts if the co-design extends them. No silent
fallback or generalized-coverage claim follows from the e14 donor alone.

The native register layout associates each lane with four token groups and
two channels. Reduction offsets4/8/16 change channel ownership while preserving
that group's token. Thus inactive-token NaNs must not mix with live-token SF
maxima. The packed reorder needs its existing bijection proof or a replacement
proof whenever the load shape, channel layout or output vectorization changes.

Activation scaling/order, SF rounding `(absmax*(1/6)*norm_const).to(sf_dtype)`,
reciprocal/clamp, FP4 conversion, original-token per-token indexing, output SF
swizzle, and accumulator release/fences must stay consistent with retained
contracts. Changing the raw TMEM-to-register layout is not permission to alter
these numerical operations.

## Prior evidence, not a retained result

PhysicalN16's bounded98fd screen was unretained: full chain0.996584x atT32 and
1.005456x atT128. It removed the FP32 TMEM transpose but still paid15shuffles.
Resource evidence:197504→181120B SMEM,64→50registers,0local bytes,one CTA/SM.
See `scripts/physical_n16_experiment/README.md` and its immutable raw archive.
The new co-design must use fresh adjacent corrected-aab controls; no old98fd
performance or current TRT ratio can substitute for that comparison.
