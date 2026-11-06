# K8 operand stages and accumulator ownership

Control is `442d2aa53f68b4640c3ab5118a76f1599ff60d34`; the immutable candidate
core is SHA256 `30617fa295ddfb5de050450520fbe8b0a81ea71a39cde6954062b04d0e6e81d7`.
Only FC1 M512/N128 and M256/N256 change to eight native MMA K steps and two
operand stages. No production source is edited.

## Source audit

- **Geometry and scale footprint:** [candidate_core.py:303](wide_trial/candidate_core.py#L303)
  doubles the internal K tile; [lines 401–413](wide_trial/candidate_core.py#L401)
  select two operand stages and admit the resulting scale footprint.
  NVFP4/SF16 uses 96 TMEM scale columns in either geometry: two SFA32 plus
  SFB32 for NB2, or SFA32 plus SFB64 for N256. FP4/SF32 uses 48 columns;
  FP8 and mixed FP4/FP8 use 24 columns. Mixed FC1 retains its inline epilogue.
- **Accumulator ownership:** [lines 815–839](wide_trial/candidate_core.py#L815)
  round the scale footprint to complete 32-column transpose slabs. Protected
  counts 32/64/96 give strides 224/192/160. For protected96 the alternating
  windows are `[0,256)` and `[160,416)`, and scales occupy `[416,512)`.
  All offsets remain 32-column aligned. The host proof checks all live-N
  boundaries for both windows and both channel geometries.
- **Early release:** [utils.py:675](wide_trial/utils.py#L675) traverses the
  virtual accumulator in opposite directions on alternating phases and
  releases after the protected slab count. Each live slab finishes TMEM
  reads and transpose scratch use before the fence and single release
  ([utils.py:557](wide_trial/utils.py#L557)). A skipped protected slab still
  issues that release. The next MMA can overwrite only the interval already
  consumed. Nonoverlapping pending slabs and their transpose scratch remain
  disjoint from the next accumulator window.
- **Operand lifetimes:** [candidate_core.py:972](wide_trial/candidate_core.py#L972)
  derives TMA transaction bytes from internal K, channel tiles, local B rows,
  and local SF sizes. Local cp.async completion is relayed by both MMA warps
  before group-2 MMA. At [line 1592](wide_trial/candidate_core.py#L1592), scale
  copies and both channel-tile MMAs are issued before any operand-stage
  release at [line 1654](wide_trial/candidate_core.py#L1654). Pipeline stages
  decrease from 4/5 to 2 without changing producer or consumer participants.
- **Gather and K tails:** [line 1297](wide_trial/candidate_core.py#L1297)
  preserves explicit row and K predicates on four-byte SFB loads. Gather4
  at [line 1312](wide_trial/candidate_core.py#L1312) issues two native
  128-byte row chunks using the existing K8 address expression. Out-of-range
  activation rows and K coordinates use TMA zero fill. Weight/SFA TMA uses
  the doubled tile with the original global shape; no padded source read is
  introduced. The exact checks cover K64/128, K384, and K1280 to exercise
  short tiles, final tails, stage reuse, and persistent tile reuse.
- **Shared memory:** NVFP4 NB2 has 92 KiB per operand stage, hence 184 KiB
  for two stages. NVFP4 N256 has 76 KiB per stage, hence 152 KiB for two.
  Existing barrier and 512-byte FC1 scratch storage remains. A third N256
  K512 stage would require 228 KiB before metadata and is deliberately not
  attempted. No register budget, warp-role, cache-policy, or math changes.

## Completed checks and interruption boundary

The original C1 B200 devbox completed the compile-time CuTe SF layout audit
before becoming unavailable. Received terminal output confirmed:

```text
SF FOOTPRINT CASES 72
OWNERSHIP PROOF: all 3072 phase/geometry/live-N cases passed
```

The full remote layout log was not copied before the devbox disappeared;
these lines are a received-output receipt, not a recovered raw log. The
ownership proof was also run locally. Source files and their manifest are
preserved locally. No GPU kernel exactness check or performance timing had
started on the lost devbox. Repeat the compile-time audit on the replacement
and archive its full output before proceeding with the paired kernel checks.

Updated initial screen: 12 NVFP4 K64/384/1280 and per-token cases across
both geometries, then 12 protected96 boundary cases (live N80/96/112, both
geometries, per-token off/on). M768 and valid257 in the format cases
exercise accumulator phase and persistent tile reuse. Each compares all
output and scale bytes from identical initialized allocations, including
padding and per-token output paths. The full 72 six-format checks and 264
protected32/64/96 boundary suite remain prepared but are deferred until a
performance win, per the iteration-speed instruction. Native fixed-tactic
timings start only after the bounded initial checks pass and native prewarm
finishes, with a matched immutable 442 control in the restored environment.

Recovery verified the same B200-83 node and all eight original GPU UUIDs,
indices, names and driver. The container, Python setup and native caches are
a new environment epoch; see `../recovery442/README.md`. A same-GPU comparison
becomes possible after environment restoration is verified, but this narrow
probe does not initiate a new primary retention campaign against old B1 data.
