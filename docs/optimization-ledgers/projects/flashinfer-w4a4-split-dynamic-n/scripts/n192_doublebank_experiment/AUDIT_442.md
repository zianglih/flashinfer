# Logical M512/N192 feasibility at 442d2aa53

CPU source audit only. No prototype changes, GPU launches, or production
tactic additions. Recommendation: low priority; do not repeat the existing
single-window geometry without a new mechanism.

## Existing evidence

This directory already tests FC1 logical M512/N192 with one accumulator
window. The `double` variant doubles FC2's accumulator banks, not FC1's.
At commit `13ca1475`, its forward/reverse native checks were exact. The
T16K FC1 medians were 280.033/281.537 us against N128's 283.137 us; most
of the full-pipeline gain came from FC2. At T8K, FC1 was 174.801/174.657 us
against 166.128 us. See [the existing README](README.md) and
[raw samples](nvfp4-prefill-r3.json).

Current 442 N128 has materially better FC1 overlap than that old control.
The recent matched GPU7 control is 258.769 us at T16K. This is context,
not a new matched N192-vs-442 measurement.

## Resources and local changes

- NVFP4 K256 gives two 192-column accumulators, 384 columns total. Two
  16-column SFA regions plus two 16-column SFB regions require 64 more.
  A single window therefore uses 448 of 512 allocated TMEM columns.
- Per CTA, two weight tiles use 32 KiB, 96 activation rows use 12 KiB,
  two SFA blocks use 4 KiB, and two SFB blocks use 4 KiB. Four operand
  stages use 208 KiB before the existing small metadata and FC1 scratch.
  This fits; five stages do not. This is the same K256 layout already used
  in the old diagnostic.
- SF32's existing logical-M512 five-stage policy cannot be copied blindly:
  FP4/SF32 has 48 KiB per stage and FP8/SF32 has 46 KiB per stage at N192.
  Both exceed the CTA shared-memory limit with five stages, so they need a
  resource-derived four-stage policy. Mixed FC1 retains its inline epilogue
  and should retain a separately verified storage-size calculation.
- [Current core line 358](../../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py#L358)
  uses floor division for SFB row blocks; N192 needs `ceil(N/128) == 2`.
  The old diagnostic already makes that change. This controls SFB allocation,
  copies, TMEM footprint and both row-block loops together.
- Gather4 uses 96 rows per CTA, which is three complete 32-row runs. N192
  route starts are divisible by 8 and 32, preserving vector metadata loads
  and epilogue slabs. Dynamic MMA N is still aligned to 16. The ordinary
  FC1 epilogue loops to `tile_n` in 32-row groups, and the core advances each
  channel tile by `allocated_n`, so one-window N192 does not require a new
  epilogue structure. Host/core capability checks need explicit N192 support.
- FC1 output SF allocation already rounds routed capacity up to 128 rows.
  Its stores index the global canonical SF layout by absolute routed row,
  so a route tile beginning at row 192 is valid without changing layout.

## Current overlap cost

[The current overlap guard](../../flashinfer/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py#L401)
requires `acc_cols == 256`. N192 has 384 columns, so it takes the existing
single-window path and releases only after both channel epilogues finish.

Generalizing overlap would require more than removing that guard. For an
accumulator extent `A` and a scale footprint `S` rounded up to 32 columns,
the shared interval is `max(0, 2*A + S - 512)`. The current expression uses
only `S`, which is valid when `A == 256`.

For NVFP4 N192: `A=384`, `S=64`, hence protected=320 and stride=64. The
windows would be `[0,384)` and `[64,448)`, followed by scales `[448,512)`.
The existing alternating slab traversal is dimension-general, but ownership
must be released after 10 of 12 slabs. Only the last 2/12 slabs remain to
overlap for a full tile; this is a count of epilogue slabs, not a measured
latency saving. Current NVFP4 N128 releases after 2 of 8 slabs, leaving 6/8.
Partial-N cases alter the live slab count and would require a new ownership
proof before implementation.

## Full-chain compatibility caveat

N192 native routing also requires an N192 FC2 path. The current FC2 TMA-SFB
predicate is `route_tile >= 128`, which relies on every route start being
128-row aligned. N192 route starts alternate between offsets 0 and 64 inside
a canonical SF atom. Therefore a naive current-core N192 admission would
load the wrong scales on odd route tiles. Use the existing cp.async SFB path
for non-128-aligned route widths (`route_tile % 128 != 0`) or design a new
aligned TMA partition. The old diagnostic used cp.async SFB for all FC2 tiles
and does not validate the newer TMA predicate.

The prior FC2 double-bank resource calculation remains relevant: two N192
banks plus scales fit in 512 TMEM columns, and the existing padded bulk
epilogue supports three 64-row slabs. It is a distinct FC2 implementation
choice, not a benefit from extending FC1 overlap.
