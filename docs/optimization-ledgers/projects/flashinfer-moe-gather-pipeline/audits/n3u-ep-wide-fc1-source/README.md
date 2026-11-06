# N3U EP8 16K: wide FC1 source and native audit

Retained `2b8eb9d8`, swap kernel `482b636a`. This audit changes no source and
does not create a new tactic or policy. The existing-space retune changed only
FC2 M256 to M512; its independent holdout was neutral. FC1 stays M512/N128/C2.

**No new implementation candidate is justified yet.** A fresh wide-geometry
FC1 profile can distinguish transport issue pressure from epilogue/accumulator
backpressure. The old TP profile is M128/N256/C1 and predates the retained
integer-carried FC1 store, so its sampled bottleneck is not a wide-EP result.

## The gather task bound is already removed

`replay.py` verifies the actual retained-source exact-qualified
M512/N128/C2/K256/K96 image. For this geometry `b_copy_rows=64`, `row_groups=16`,
`tasks=16`, and four warps each issue four Gather4 operations per K stage.
Across all four emitted K stages, the sixteen PTX issue sites have only the
standard elected-lane guards: there is no `task < tasks` comparison. PTXAS
emits all sixteen SASS `UTMALDG.2D.GATHER4` instructions unpredicated. There is
no branch between the first and fourth issue of each stage. An unrelated
next-work comparison is scheduled into the last issue block; it is retained
in the receipt and does not predicate a Gather4 instruction.

The image uses H1024/I640/T193/top2, static scheduling and PDL, with168 initial
registers and zero local bytes. It is **representative native evidence**, not
the exact N3U H2048/I5120/T16384/top22 image. The unchanged task arithmetic does
not depend on those different logical dimensions. A fresh N3U capture can
confirm the same elimination; no special-case source rewrite is warranted.

## What the current wide path already does

- Logical M512 comprises two physical M256 channel tiles sharing one gathered
  B/SFB stage. The weight producer loads both A/SFA tiles, and MMA issues both
  channel tiles before releasing the shared operand stage. It must not release
  B after only the first tile.
- N128 and two channel tiles use256 accumulator columns. Forty-eight scale
  columns round to a64-column protected prefix; the two overlapping windows
  reserve448 columns plus scales. Ordinary two full256-column banks do not fit.
  The epilogue handles eight32-token slabs and releases the shared interval
  after the two protected slabs have completed their reads/transpose, before
  finishing activation/quantization/stores. This is existing overlap, not a
  missing second accumulator bank.
- The ordinary scheduler is static persistent. Operand phases and stage
  indices span work items, and TMEM is allocated once per CTA. Metadata-ring
  depth and per-work-item TMEM initialization are not costs of this winner.
- The current ReLU2 epilogue already joins adjacent converted halves into one
  16-byte FP4 store. Its two SF16 quantization blocks retain their required
  independent scales. Shared FP32 transpose, K-major/channel-inner MMA order,
  and the reverted maximum-dependency change are closed leads.
- Four gather warps issue payload Gather4, while each lane copies four SF
  bytes per K word. For K256/SF16 there are four such words per row. Both CTAs
  currently need the full-N SFB image for the group-2 S2T contract. Their SF
  transport has a larger byte ratio to payload than the old one-CTA/N256
  geometry, but byte ratios alone do not establish a bottleneck.

## Smallest useful diagnostic

Use the held runner's existing aggregate metrics first: tensor activity,
DRAM/L2 traffic and utilization, issue activity, long/short scoreboard, MIO,
barrier/wait stalls, instruction count, registers and shared allocation. No
new metric family or kernel instrumentation is needed. NCU durations are
diagnostic and cannot replace the native CUPTI holdout.

If these metrics again show low tensor utilization with appreciable issue or
scoreboard pressure, one actual-source SourceCounters capture should separate:

| Question | PCs to distinguish | Interpretation boundary |
|---|---|---|
| Is input transport late, or merely backpressured? | MMA gather-ready versus operand-ready; gather operand-empty; SF cp.async/completion versus Gather4 issue | Large gather-empty observations can be downstream pressure. Do not infer that faster input loads help from body samples alone. |
| Is the wide accumulator release exposed? | MMA accumulator-empty; the protected two TMEM read/transpose slabs; remaining epilogue quant/store | Preserve scratch ownership. The existing early release means total epilogue work is not all serialized with the next MMA. |
| Is the single weight/MMA issuer expensive for two channel tiles? | Weight TMA/address issue; SFA0/SFA1/SFB S2T; both MMA issue blocks | The already-rejected MMA reordering and split producer ownership are not automatic remedies. Look for actual redundant instructions first. |

Any PC report must map every sampled address to the exact returned ELF,
preserve uniform-register `MOV.SPILL` separately from local-memory spills,
and distinguish the terminal CTA join from steady-state waits. Sample counts
are warp observations, not duration fractions. No implementation should be
selected from this source audit alone.

References: `profiling/n3u-ep-w4a4-16k/held-retained-2b8/`, the saved native
component records in its parent, `profiling/n3u-tp-w4a4-16k/RESULTS.md`,
`audits/accumulator-depth/README.md`, `audits/scheduler-depth-history.md`,
`audits/sfb-vector-layout/README.md`, and `experiments/CLOSED_LEADS.md`.
