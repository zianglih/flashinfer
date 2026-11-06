# Accumulator depth: keep the current policy

Read-only audit of retained `49c91adf47d30fc2049c76cbaf34d0ccf3291434`.
No production edits, CUDA compilation, GPU work, or new performance claim.

**No experiment is justified by the current evidence.** Two banks are not a
universal hardware or lifetime limit. Narrow, non-overlapping banks could be
deeper with the existing index-based addressing. But the profiled narrow
ordinary-scheduler case has almost no observed MMA accumulator-empty wait,
wide-N cases cannot fit a third bank, and the one-slot CLC metadata handoff
already limits how far MMA can get ahead of its epilogue. Filling TMEM does not
remove any current work or raise epilogue throughput by itself.

## Prior experiments, with the actual depth distinguished

The old project is `../flashinfer-w4a4-split-dynamic-n`. A targeted search of its
Markdown ledgers and experiment Python/patch files, excluding source copies and
large embedded source snapshots, found **no completed measurement with more
than two accumulator banks**. This is a search result, not proof that no
unindexed historical run exists.

| Prior record | What changed | Boundary |
| --- | --- | --- |
| `CORE_PERFORMANCE_ITERATIONS.md`, isolated overlap after `de4f1aa4` | One to two accumulator banks at N≤128, with separate loader/epilogue warps | MX8 N128 FC2 347.521→266.400 µs; old balanced-route diagnostic, not a >2-bank result or a current retained comparison. |
| `scripts/n192_doublebank_experiment/README.md` | FC2 N192 one to two disjoint banks | Different route geometry; diagnostic only. No three/four-bank trial. |
| `scripts/nb2_overlap_experiment/README.md` and `scripts/pipeline_acc_overlap_audit_20261027/README.md` | Two partially overlapping 256-column windows behind a **one-stage** pipeline | This is the retained wide-window ownership mechanism, not missing ordinary double buffering. |
| `scripts/nb3_experiment/README.md` | Three physical channel tiles share B in logical M768 | “Three” refers to channel tiles, not accumulator queue depth; rejected larger-tile experiment. |
| `scripts/epilogue_codesign_experiment/early_release_ring_20261025.md` | Proposed four physical-N16 banks in the same 128-column allocation | CPU ownership proposal only. The completed narrow epilogue experiment explicitly retained **two** banks and was neutral/rejected (`README.md`). Physical N16, 288 threads and standalone preparation predate the dedicated gather warpgroup. |
| `perf-general-20261026/clc-info-{depth,lookahead}/` | Metadata depth=accumulator depth or accumulator depth+1 | Two/three **metadata** slots, while accumulators remained one/two. Rejected decode regressions; do not describe these as accumulator-depth results. |

`../scheduler-depth-history.md` has the precise metadata trial numbers and
source pins. The recent gather redesign changes the producer mix, but it does
not turn the old unmeasured four-bank suggestion into supporting evidence.
Moreover, current physical allocation is at least N32: four narrow banks plus
scales now require a 256-column allocation, so the old physical-N16 proposal's
"four banks in the same 128 columns" premise does not carry over.

## Current TMEM ownership

The retained planner uses `acc_cols = max(32, route_N) * channel_tiles`, one
SFA/SFB region, and `min(2, floor((512-scale_cols)/acc_cols))` full banks
(`moe_swap_ab_kernel.py:1619–1640,1676–1685`). The allocation is rounded to a
power of two. Pipeline construction accepts the resulting static depth; no
two-slot-only implementation was found in `PipelineUmmaAsync`.

For non-overlapping storage, the MMA and epilogue use
`state.index * acc_cols`; SFA/SFB begin at `acc_stages * acc_cols`
(`:2354–2358,3054–3076,3130–3140,3377–3391`). A 32-column epilogue transpose
uses the current bank's slab as scratch, including both 16-row halves, and all
TMEM reads complete before that bank's release (`:424–500,854–952,3413–3415`).
Extra disjoint banks would not require a different scratch layout or another
SF ring. The existing single MMA issuer and ordered SF-copy/MMA sequence still
own SF reuse; merely deepening the accumulator queue does not parallelize MMA
issuers or epilogue warpgroups.

The wide path is different: when `acc_cols=256`, one full bank plus scales fits,
but two full banks do not. Eligible FC1 and single-channel bulk FC2 use two
phase-selected overlapping windows; FC1 consumes the scale-footprint-derived
protected prefix, and FC2 consumes 64 protected columns, before releasing
ownership. Other wide cases retain one ordinary bank. The shared prefix remains TMEM
transpose scratch until the last protected read. A capacity or power-of-two
depth formula leaves this one-stage/two-window path unchanged. It must not be
reinterpreted as an ordinary multi-bank ring.

The CPU proof executes the **actual retained planning methods**, changing only
the hypothetical depth formula inside the audit. It checks bank/scratch/SF
intervals for 448 storage-admitted combinations of public M/N/K geometries,
four operand-width/SF families, both FC roles, and static/CLC. The remaining
32 combinations exceed existing storage. This is storage arithmetic and
interval evidence, not a CuTe/native qualification or broad API acceptance.

| Hypothesis | Different depth among 448 cases | Depths | Max extra metadata | Operand/bulk-stage changes in this enumeration |
| --- | ---: | --- | ---: | ---: |
| Full capacity | 352 | 1,3,6,7,14,15 | 256 B | 0 |
| Largest power of two within capacity | 256 | 1,2,4,8 | 128 B | 0 |

Both change SF placement and kernel specialization. They add full/empty barrier
storage and initialization, and usually expand rounded TMEM allocation to
512 columns. The metadata planner is part of automatic K/stage selection, so
an implementation would still need to qualify that coupling; the zero stage
changes above apply to the explicitly enumerated K choices, not a claim about
arbitrary future geometries.

## Scheduler and state costs

The ordinary scheduler is already **static persistent**. Each role independently
advances by grid stride; all operand and accumulator states span work tiles.
There is no per-work-item TMEM allocation to amortize. A deeper ring could
absorb variation in tile/epilogue duration, but cannot improve the sustained
rate of a single slower epilogue. Two banks already permit one tile to be
computed while another is consumed. This does not prove that all transient
backpressure is impossible.

CLC currently publishes one metadata slot. Every role copies/releases its
current item before doing the tile's work. While the epilogue handles tile i,
MMA may consume metadata and compute i+1; the scheduler cannot publish i+2
until the epilogue finishes i and copies/releases i+1. Therefore deeper
accumulator storage cannot give CLC a larger completed-tile lead under the
current handoff. Changing metadata depth would reopen a separately rejected
policy, which this audit does not propose.

The captured installed `PipelineState.advance()` implementation
(`../installed-pipeline/helpers.py:883–925`) increments index/count, compares
index to the constant depth, then resets index and flips phase. All accumulator
calls use the default single-step advance. It does **not** divide/modulo by
depth on this path, even for non-power-of-two depths. Thus the old claim that
four banks are inherently cheaper than three is not established for the
current source; only native compilation could establish an instruction-cost
difference. Depth 2 may have compiler simplifications, but no generated-code
claim is made here. No per-bank register payload array is required.

## Actual profiles do not show the required bottleneck

The current-head N3U TP8 MXFP4x8 T32 profile is the most relevant many-small-GEMM
case (`profiling/n3u-tp-mx4x8-32/RESULTS.md`). Both FCs use static scheduling,
M128/N16, allocated N32, two accumulator banks, and 128 allocated TMEM columns.
FC1/FC2 have 1,925/6,160 work items and 8/5 K stages per item.

| Recorded property / hypothesis | FC1 | FC2 |
| --- | ---: | ---: |
| Accumulator columns / SF columns | 32 / 16 | 32 / 8 |
| Retained operand stages | 5 | 10 |
| Full-capacity accumulator stages | 15 | 15 |
| Power-of-two accumulator stages | 8 | 8 |
| TMEM allocation: retained→either hypothesis | 128→512 columns | 128→512 columns |
| Shared bytes: retained→full capacity | 215936→216192 | 215936→216192 |
| Shared bytes: retained→power of two | 215936→216064 | 215936→216064 |
| MMA accumulator-empty sampled observations | 0 | 18 |
| Epilogue accumulator-full sampled observations | 938 | 463 |

These are PC samples, **not time fractions or a formal speedup bound**; the MMA
warp and epilogue warpgroup have different participation. Still, they do not
identify accumulator queue exhaustion as the exposed limiter. Weight traffic,
operand/gather readiness and epilogue scalar dependencies remain stronger
observed signals. Adding thirteen banks to address essentially absent sampled
FC1 backpressure has no current causal support.

The N3U TP W4A4 16K and V3 TP MXFP8 16K FC1 profiles use N256 and one pipeline
stage with overlapping windows. Their TMEM capacity cannot admit a deeper full
bank under either hypothesis. Those older source-bound profiles are not fresh
49 measurements, and their wait counts are not extrapolated across the later
instruction cleanups. Their geometry alone establishes that this proposal
cannot improve those recorded wide winners.

## Decision boundary

Keep `min(2, capacity-derived depth)`. It is a conservative throughput/queue
policy, **not** a proof that hardware forbids deeper narrow rings. There is no
new source-simple measured opportunity here: CLC is metadata-lead bounded,
wide winners are TMEM-capacity bounded, and the current narrow ordinary profile
does not show appreciable accumulator-empty pressure. A future source-bound
narrow **ordinary** winner with sustained accumulator-empty stalls could
justify revisiting queue depth, with scratch/phase/SF/native resource checks;
no such experiment or additional tuning axis is requested now.

Reproduce the CPU receipt with `python3 audits/accumulator-depth/proof.py`.
`proof.json` binds the retained source, captured PipelineState source, script,
all enumerated cases, and the two profile geometry calculations.
