# Copy only the logical N16 activation prefix

Read-only feasibility audit. No source edit, compilation, GPU launch, or new
benchmark was performed. Source/metric/history hashes are bound in `review.json`.
Current c5c source retains the profiled common core; the NCU capture itself is
explicitly from clean adf. NCU ordinary kernel replay is not native PDL timing.

## Candidate

Separate activation **copy extent** from **allocated/consumed layout**. For the
existing one-CTA logical N16 tactic, make the B TMA copy cover exactly the first
16 token rows of each K slab while retaining physical B32 storage, its complete
K/stage strides and swizzle. Keep every MMA/TMEM/epilogue descriptor, accumulator
allocation, stage count, SFA/SFB layout, thread role, cache hint, and PDL sequence.
This is a copy-only prefix, not the prior physical-N16 allocation/bulk epilogue.
No model/dtype/token-count threshold is needed: the extent is the compile-time
logical route tile. Existing N>=32 and two-CTA tactics already have no such
allocation padding and retain their current copy. W4A16's separate core stays
unchanged. NVFP4 (including per-token), homogeneous MXFP8 and mixed MXFP4x8 use
the same prefix rule in this common core.

The required changes would be local to B TMA construction/partition and its
expected transferred-byte count. Do not change `physical_tiler`, `b_layout`,
`allocated_n`, `b_rows` as an allocation property, or the capacity calculation.
Derive a separate copy-row count. Startup weight prefetch acquires the same joint
A/SFA/B barrier as the main producer, so its compiled expected-byte value must
also use the reduced B copy size; B still completes that barrier after the PDL
wait. There is no new barrier, allocation, metadata publication or dynamic branch.

## Source and transfer evidence

The current core rounds `allocated_n=max(32,route_tile)` because its epilogue
transposes 32 columns (core lines350–353). The same physical tile is passed to
`make_tiled_tma_atom_B` (796–803), and the producer views B at allocated N
(1299–1318). MMA instruction N independently rounds valid routes to 16 (line143),
so logical N16 consumes no B rows16–31. The final output predicate continues to
mask the already-existing extra epilogue/TMEM columns. SFB remains canonical and
unchanged, including zero-fill/valid handling and per-token scale handling.

The V41 T128 MXFP8 FC2 NCU transfer count is exact:

- 82 active routed tiles × 40 channel tiles × 9 K stages = 29,520 stages.
- A 32,768B + SFA 1,024B + physical B32 8,192B per stage = **1,239,367,680B**.
- Copying B16 instead gives **1,118,453,760B**, saving **120,913,920B** (9.7561%
  of these TMA bytes), while preserving all A/SFA bytes.
- The TRT capture transfers 1,059,886,080B: its narrower N8 activation footprint
  accounts for most remaining difference. Its 512-thread organization and
  scheduling differ, so this is a traffic comparison, not a causal performance
  decomposition. Our scale LDGSTS traffic is only2,903,040B here.
- DRAM read traffic is approximately1.001GB versus TRT0.998GB; the gap is mainly
  L2/TMA amplification, not another weight-HBM pass. NCU shows memory pressure,
  no local-memory spill, and no evidence supporting cache-priority reversal.

## Feasibility and the critical address constraint

The installed CuTe4.7.1 `make_tiled_tma_atom_B` accepts a distinct SMEM layout
and `mma_tiler_mnk`: it derives the global CTA coordinate map from the latter and
forwards the supplied SMEM layout independently to TMA lowering. Its Blackwell
SMEM helper tiles the K-major atom in N, K, stage order. The SDK source excerpt is
saved at `evidence/v41-mxfp8-gap-adf-ncu-l2-r1/cutlass-tma-source.txt`.

A compact B16 layout must **not** be substituted: it changes the stride between
K slabs and stages. Instead, restrict the existing nonstaged layout's N domain
and retain its original strides, or construct an equivalent generic TMA copy
view of the logical prefix. Existing codegen already splits K into swizzle-sized
TMA transactions (the NV K512 example has two B2D instructions with4,096B
physical-N32 destination separation). The candidate must preserve those K-slab
addresses and transaction count while each transaction copies only16 rows.
If the high-level MMA-partition helper cannot express the prefix, use the
existing generic `cpasync.make_tiled_tma_atom` for the copy view; do not change the
MMA B descriptor. This remains a feasibility inference until actual layout/
codegen checks prove it. Reject a lowering that repacks the destination or adds
per-row TMA instructions.

CUDA13.2's tensor-map contract permits a16-row outer box: box dimensions are
nonzero and <=256; the contiguous dimension retains its16-byte and swizzle
constraints. Packed FP4's special first-dimension restriction must remain
unchanged. See the official
[CUDA13.2 tensor map documentation](https://docs.nvidia.com/cuda/archive/13.2.0/cuda-driver-api/group__CUDA__TENSOR__MEMORY.html).
The SM100 MegaMoE generation path also separates generic activation-copy atoms
from native K_SW128 B layout (its FC1 Gather4 one-row atom), showing this
abstraction separation is already used locally; that is not a recommendation to
restore Gather4 or import MegaMoE's pipeline.

## Why the closed N16 results do not settle this candidate

The modern physical-N16+bulk experiment changed three files, accumulator base
alignment, bulk epilogue ownership and physical allocation. NV stages changed4→5,
SMEM197,504→230,016B; MX stages stayed5 but TMEM128→64, registers90→43 and
SMEM215,936→199,296B. Its paired chain ratios were0.992761NV,1.000942MX8 and
1.000256mixed. That is strong evidence against the combined policy. It did not
isolate a reduced copy box with the current32-column compute/storage contract.
The older small-B experiment also forced five stages; descriptor-only N8 changed
MMA work rather than transferred B bytes. Those are distinct mechanisms.

This distinction does not guarantee a gain. Weights dominate DRAM, current B-last
caching already provides reuse, and the old MX result was neutral. The candidate
has modest expected upside and should be closed quickly if transfer savings do
not improve native latency. Its value is that it tests this traffic hypothesis
without the epilogue/resource changes that confounded the earlier result.

## Acceptance requirements for any later authorized experiment

1. Exhaustively compare retained first16-row SMEM addresses across supported
   FP4/FP8 formats and K4/K8/stage counts; confirm untouched storage/policy fields.
2. Generated code must preserve MMA descriptors, TMEM allocation, epilogue and
   roles; B transaction count/coordinates and only B expected bytes may change.
3. Cover no-work, partial route tiles, persistent tiles, PDL on/off, FC1 generated
   output SF, FC2 scatter, and NVFP4 per-token with the existing byte-exact gates.
4. A narrow NCU check should show the predicted B-byte reduction, then a fixed
   full-chain native bracket on both models/allthree formats determines whether
   it is useful. No latency/retention claim exists from this read-only audit.
