# Cyclic epilogue with a general protected interval

Base: retained `e780f02c`. One swap kernel file changes; W4A16, quantizers,
routes, tactics, scheduler, operand pipeline, and PDL contracts stay unchanged.

The protected accumulator interval is the SF footprint rounded to a complete
epilogue read slab: 32 columns for FC1, the selected 32/64-token slab for FC2.
The two accumulator windows occupy `2*C-P` columns; SF storage starts afterward.
The cyclic traversal consumes their shared interval before the existing TMEM
read fence and consumer release. No remaining read or transpose touches that
interval after release. The CPU proof covers 42 geometries and 20,052
phase/live-row cases, including nongated and two-channel-tile ownership.

The output TMA ring must follow logical slab order even when a slab is skipped
or uses SIMT. The old full-store-only commit policy fails at P128, phase0,
192 live rows: traversal 2/3/0/1 stores group2 in stage0, skips group3, then
`wait_group.read 1` does not yet protect stage0 before group0 overwrites it.

Two general policies are safe: count actual issued stores and index stages by
that runtime ordinal, or commit one bulk group per logical slab (empty when no
TMA issued). This candidate uses the second. It moves the existing commit
outside the branch, preserving constant stage addresses and constant wait
thresholds, without a new counter or behavior knob. For logical step i, the
prior use of its stage is i-stages or earlier; `wait_group.read(stages-1)`
completes that source read, including when newer groups are empty. All issuing
threads commit; the existing warpgroup barrier after the wait protects the
shared writes by all epilogue warps. Partial SIMT output uses TMEM scratch,
not the shared TMA stages. Tiles with a real store retain the terminal drain;
empty-only tiles have no outstanding shared source reads.

The ring proof covers 6,168 phase/span/live-row cases for each safe policy and
264,196 successive-tile cases. It intentionally retains the 128 failures of
the old policy as counterexamples. This is a proof under the documented
instruction contract, not a substitute for hardware exactness/codegen checks.

Reference: [CUDA13.2.2 PTX bulk commit/wait semantics](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async-bulk-wait-group).
PTX explicitly permits empty committed groups and orders waits by committed
group age; `.read` protects source/tensormap reads. MegaMoE uses cyclic TMEM
traversal but a single output scratch stage drained per slab; Rubin's output
path also drains per copy. Neither supplies a multi-stage ring directly.

Validation reuses existing exact oracles. The 33-case gate includes a 480-row
K8/N256 case for all four formats (224-row tail), and six forced-multiwave
ReLU2/GeGLU/SiTU cases at448 rows andK8 (192-row tail), covering both phases
and per-token/per-tensor FC1 output. Actual CUBIN register guards run before
launch. No new repository tests or sanitizer run.

Performance constraint: the retained cyclic change slowed N3U TP8 per-token
16K by1.83%, with disjoint critical-path extensions +7.8us FC1 and+25.0us FC2;
the quantizer changed by-0.2us. The next matched screen must retain this point
and the earlier rejected wider-overlap cases. No performance claim yet.
