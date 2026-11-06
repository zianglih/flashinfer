# Unsigned gather metadata and R14 independent audit

These are artifact-only candidates. Neither the review checkout nor the parent
composition input was modified. No GPU was launched by this work.

| Artifact | SHA256 |
|---|---|
| Exact R6 `../metadata/r6_base.py` | `deba8b639fba89e6f76381e8c6bf8bc323ccaf850b973c836f476f8144c4cc0a` |
| R6 plus unsigned metadata `candidate-kernel.py` | `eebecfad1155d51541d876f5fa185a5279237c25ad431c2003028aa3b00f2f0e` |
| Parent R10+R11+R12 `../combined/candidate-kernel.py` | `70a57d26d2c51c93b9b43c6fc86b4259914f3a3d4d135a7858f4730fc86bacd3` |
| R14, composition plus unsigned metadata `combined-kernel.py` | `6605aeacc09dfe16232312d17bcf00d320f4e5065e8a5ed34514b9542f6cf372` |

`build.py` and `build_combined.py` verify exact input hashes, reverse all edits
byte for byte, and check that the changes remain entirely inside gather
metadata setup before the K loop. The two `*-source-proof.json` files record
those assertions. Both candidates parse as Python; compilation into a CUDA
kernel is a separate gate owned by the parent task.

## Change and producer contract

Only valid expanded-route IDs are converted to `Uint32` before division by
positive compile-time `top_k`; the quotient is explicitly cast back to `Int32`
for TMA coordinates. The combined candidate covers vector `routes[j]`, scalar
payload tails, and scale-factor rows. Lane arithmetic whose domain is 0–127
uses shifts/masks. Output coordinate type, positive OOB coordinate, all valid
row guards, 64-bit SF offsets, four-warp task assignment, stage counts,
synchronization, PDL, and FC2 remain unchanged.

The local review sources establish the existing producer contract:

- `csrc/moe_utils_binding.cu:390–394` distinguishes the two mapping buffers and
  connects `permuted_idx_to_expanded_idx_ptr` to
  `mPtrPermutedIdxToExpandedIdx`.
- `include/flashinfer/trtllm/fused_moe/RoutingKernel.cuh:527–543` stores a
  nonnegative, bounded expanded index in each valid local permuted slot.
  The `-1` at lines 538–540 is stored in the inverse
  **expanded-to-permuted** buffer, which is not the gather input.
- The other producer paths store the same expanded index at lines 903–916
  and 1206–1222.
- Inactive or padded rows can be unwritten or contain arbitrary bits. The
  candidate does not load or cast those rows: payload loads require
  `source_row + j < valid`; SF loads require `row < valid`. Vector loads require
  all four rows valid. No nonnegative assumption is applied to sentinel data.
- Expanded IDs already use signed Int32 throughout this routing API. The
  candidate preserves its existing range, rather than extending it to IDs
  above `INT32_MAX`.

R6 generated K3 PTX in
`../codegen/evidence/0-ep-kimi-k3-mxfp/capture/000-fc1.ptx:1443–1453`
uses a ten-instruction signed floor-division correction sequence for division
by 16. The SF row offset has similar signed correction work at 1398–1417.
This is the instruction-level motivation. Actual R14 PTX/SASS must confirm
that the unsigned spelling eliminates it; no speedup is claimed here.

## Independent R14 source audit

The audit refers to the exact frozen combined hash above and leaves it intact.
`audit_combined.py` generates `combined-audit.json` without importing CUDA.

- **Mapping and alignment:** checked 1,503 valid-row/CTA combinations over
  route N16/32/64/128/256, both CTA group sizes, and every partial valid count.
  All 23,824 complete vector groups are 16-byte aligned and in bounds. The
  dynamic two-CTA offset is rounded N/2, always a multiple of eight rows; with
  a four-row payload group and route-tile-aligned route start, the vector
  assertion remains valid for N16/two-CTA.
- **Task coverage:** 131,688 issued Gather4 tasks cover every row/K chunk
  exactly once. Each task selects the corresponding cached four row IDs.
  Issued payload bytes equal the local barrier's expected transaction bytes.
  For N16/two-CTA and one K chunk, only two payload tasks exist; the inactive
  payload warps still perform their assigned SF work and completion arrival.
- **SF ownership:** all 128 gather threads own distinct four-byte words in
  each 128-row SF bank. Both CTAs retain the full-N SF image required by group-2
  S2T. The 291,072 checked ownership cases contain no invalid mapping access.
- **Partial K:** the existing contract requires K divisible by four SF
  values (`is_valid_shape:2128`, `wrapper:2155`). Therefore every predicated-on
  four-byte SF copy fits wholly inside its source row. The last operand stage
  may be short, while the MMA loop emits a separate compile-time short
  section. The audit checks 18,432 stage/ring cases, including reductions
  shorter than one stage. All participating roles advance once for every
  stage, with no phase reset between tiles. K96 machinery is unchanged.
- **CLC:** the declared metadata consumers are exactly the active roles:
  weight, relay/activation, four epilogue warps, four gather warps, plus the
  leader's MMA warp. This is 352 threads on the leader and 320 on a follower.
  The scheduler is excluded, and the follower's inactive MMA warp is excluded.
  Every active role consumes the terminal item before the final CTA join.
- **Register donation:** `warp < 4`, `warp < 8`, and the remaining gather
  branch are mutually exclusive 128-thread warpgroup branches. Donation is
  the first instruction in each role block, after the common setup, and the
  branches reconverge only after their work loops. FC2 compiles all donation
  instructions out. C80/E256/G128 needs 59,392 registers per CTA; source alone
  does not prove that the compiler reserves this pool for every variant.
  Keep the authoritative cubin resource guard, including initial-pool checks,
  for every compilation. R11 K3 and N3U captures showed REG168; this is evidence
  for those variants, not a universal guarantee.
- **Publication/reuse:** 128 issuing threads plus one transaction announcement
  still complete the local barrier. Each CTA's relay retains local completion
  and the proxy fence before shared-only cluster release/arrival. The leader
  acquires after both arrivals. Only the MMA consumer returns the operand
  slot after both channel tiles have consumed it. Counts, phases, and reuse
  authority did not change. The detailed ordering proof is
  `../relay-publication/ORDERING.md`; actual generated scopes remain a codegen
  gate.
- **PDL:** gather FC1 has `prefetch_weights_before_wait=False` in
  `moe_swap_ab.py:248`; all roles acquire the upstream routing publication
  before reading metadata. Routing publishes only after its global stores
  (`RoutingKernel.cuh:550–559`). R14 changes none of these waits/triggers.
  FC2 retains its earlier weight-prefetch behavior. Do not move route-dependent
  FC1 work ahead of this wait without introducing a valid earlier metadata
  publication contract.

The standalone unsigned equivalence check additionally covers 123,375
quotients (including Int32 boundaries and non-power-of-two top-k values),
1,055,136 payload coordinates, and 1,746,432 SF coordinates, with zero invalid
sentinel reads. These are local arithmetic/accounting checks, not a substitute
for bit-exact GPU tests, launch-pool checks, or performance measurement.

## Future opportunities, outside R14

1. **Descriptor prefetch before the dependency wait** is a bounded startup
   experiment. Current swap-AB does not prefetch descriptors, while W4A16
   does so at `moe_w4a16_kernel.py:1133–1138`, Rubin gather at
   `rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1374–1379`,
   and Hopper finalize at `hopper/contiguous_grouped_gemm_finalize_fusion.py:398–400`.
   Descriptor addresses do not depend on routing payload, so this need not
   weaken PDL ordering or add waits. Benefit is unmeasured.
2. `row_base < self.b_copy_rows` is mathematically redundant after modulo by
   `self.b_copy_rows // 4`. First inspect R14 SASS: the compiler may already
   remove it. Do not expand this candidate just to remove source expressions.

No further SF-address hoisting is needed: row IDs and row-stride products are
already outside the K loop, and R6 PTX hoists the SF base at 1713. A wider
8/16-byte SF cp.async is not a drop-in improvement: adjacent global SF words
are separated by 512 bytes in the destination layout, while adjacent
destination words belong to independently routed rows. A layout change or
extra transpose would be required. Cross-tile row caching adds state and
branches without evidence that scheduler order supplies enough reuse; the
existing channel-tiles path already reuses each gathered B/SFB stage for
logical M512. These are reasons to preserve the current small R14 scope.
