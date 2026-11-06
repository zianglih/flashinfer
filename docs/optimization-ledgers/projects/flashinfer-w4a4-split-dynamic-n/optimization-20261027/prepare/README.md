# Preparation optimization experiments

Base: `e2728a2908f38cbcfa997c031bea059e3724ccde`. The independent
`flashinfer-prepare-perf-review` clone contains only the frozen preparation
candidate, left unstaged. Parent accepted it for the combined broad retention
campaign; it is not committed or retained yet. Canonical and the unowned weight-layout review are
untouched. Persistent native C++ compilation caches are retained.

## Frozen candidate: preload scale factors into registers

Original128-thread scaled preparation and hardware-derived grid are retained.
Each lane loads its scale-factor word(s) into registers before its payload copy,
then performs the original canonical SF stores after the payload. There are no
new barriers, shared memory, vector widths, layouts or policy selectors. Signed
row/source arithmetic, zero padding and PDL are unchanged. Unscaled W4A16 remains
byte-identical in generated SASS.

All48 full-allocation byte graph replays pass. Nine codegen cases have no stack,
local memory or shared memory. Generated NV code issues payload LDG256 and SF LDG
adjacently before either store; FP8 emits SF LDG before branching into the payload
copy block. Registers vary by specialization (oneNV case32→38); this is subject
to a bounded screen, not a retained optimization claim. Two16K CAAC cells use
V3 MXFP4x8 and N3U W4A4, existing frozen winners,10warmups/100cold-L2 CUPTI samples.
Source/cache/routing/tactic identities are verified every phase.

The strict two-cell screen completed800 samples: V3MXFP4x8 +3.77%
(control drift+0.066%), N3UW4A4 +0.82% (control drift-0.81%). Matched Nsight
traces show smaller but positive prepare improvements: V3 40.8005→40.000us;
N3U22.384→20.240us. Profiled chains changed693.365→692.006us and
568.292→564.372us. Do not attribute the full26us V3CUPTI improvement to prep;
the broader campaign must establish retention. Evidence: `results-preload.md`,
`summary-preload.json`, `screen-preload-cells.csv`, `preload-codegen-proof.json`,
`evidence/screen-preload-gpu*`, and `evidence/trace-preload-*`.
`frozen-candidate.json` records exact source, patch and evidence hashes. No
further source changes are allowed in this candidate. GPUs4/5 are released.

## Closed: separate payload/SF warp groups

Rejected. Scaled CTAs doubled128→256 threads and the hardware-derived grid
halved2368→1184, without changing arithmetic, payload/SF accesses or PDL.
48byte gates passed and all3unscaled SASS cases were identical. Two-cell CAAC
was neutral overall: V3MXFP4x8 +0.98% within1.63% control drift, N3UW4A4 -0.88%
with0.42% control drift. Matched diagnostic traces explain the outcome:
V3prepare41.056→41.136us; N3Uprepare22.128→26.257us (+18.7%). Registers unchanged.
The widerCTA/gridcost erased useful issue overlap. Evidence is in
`results-warps.md`, `summary-warps.json`, `screen-warps-cells.csv`,
`evidence/screen-warps-gpu*`, `evidence/trace-warps-*`, and
`evidence/codegen-warps-candidate`. Raw Nsight reports/SQLite remain at the
persistent remote experiment root. The source diff has been superseded in the
single active review clone.

## Closed: unsigned positive-index arithmetic (v1)

Rejected. All 48 byte gates and 168 CPU offset equivalence cases passed; eight
of nine compiled kernels shrank, but FP8 top-k22/N256 expanded through compiler
unrolling. The 40-cell frozen-winner screen (four models, two families,
tokens128/16384, five CuTe dtypes; 16,000 samples) was performance-neutral:
GM +0.065%, decode -0.008%, prefill +0.137%. K3 per-token 16K had a stable -2.12%
regression. Prefill movements near control drift are inconclusive. Evidence:
`results.md`, `summary.json`, `screen-cells.csv`, `evidence/screen-gpu*` and
`evidence/codegen-v3-*`. The source diff was removed from the active clone.

## Closed: canonical SF shift/mask arithmetic (v2)

Rejected. All 48 byte gates passed and all three unscaled cubins matched control.
Scaled instruction count generally fell, but top-k22/N256 again expanded via
compiler unrolling. The 10-cell targeted screen (4,000 samples) was inconclusive:
GM +0.131%, decode -0.017%, prefill +0.279%, with V3 MXFP4x8 16K -3.98% amid
about 2.2% control movement. Evidence: `results-v2.md`, `summary-v2.json`,
`screen-v2-cells.csv`, `evidence/screen-v2-gpu*`, `evidence/codegen-v4-candidate`.
Original arithmetic is restored; obsolete source diff files were removed.

## Audit context

Current prepare is on the critical chain: fresh timeline measured V3 MXFP4x8
16K at 41.14us and N3U W4A4 16K at 22.27us. Older NCU evidence shows high long
scoreboard stalls despite modest bandwidth, motivating independent issue work.
The ledger already rejected warp-owned routed rows, half-grid PDL, destination
linear SF ownership, shared-memory SF transpose, wider SF vectors, and earlier
combine LDG256 variants; this candidate does not repeat those designs.

The shared combine already uses packed FP32 multiply/FMA, vectorized loads and
ordered routing-slot accumulation. Routing metadata loads precede its PDL wait;
expert reads follow it. Its exact arithmetic is unchanged. The separate unowned
W4A16 preparation PDL WIP was read only and was not copied.

Remote root:
`/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261027/prepare`.
