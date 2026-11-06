# One physical accumulator / three decoded stages at N128

Source-feasible as a later private TMEM tradeoff, but not a one-line change and
not a predicted gain. No patch, constructor/native compilation, GPU execution,
remote operation, public knob or queue change accompanies this note. FC1 release,
staging and group256 stay ahead of it.

Inspected current private kernel:
`7e16537e99d9b959242f2e3dc7d07aa329c9feef439f3466c6d4254b097cc315`;
epilogue:
`1131c7e804126d1306d77248dde53f3f5c4b2ea58d7c7254e88217665e65b569`.
The held FC1 early-release epilogue943f is discussed separately; it is not
assumed retained. This is a source identity, not a new completed runtime owner.

## Physical capacity and a bounded geometry rule

`shim/w4a16/kernel.py:74–115` computes one accumulator's column count from the
actual MMA fragment, asserts it equals token-N, and gets128 columns per decoded
K256 tile. These are per-CTA TMEM columns, including the two-CTA MMA geometry.

| Geometry | ACC / decoded counts | Physical column ranges |
| --- | --- | --- |
| N128 current | 2 / 2 | ACC0–127,128–255; decoded256–383,384–511 |
| N128 proposed trade | 1 / 3 | ACC0–127; decoded128–255,256–383,384–511 |
| N64 preserved | 2 / 3 | ACC0–63,64–127; decoded128–255,256–383,384–511 |

A private host/constexpr capacity rule could preserve ACC2 whenever it already
fits three decoded stages, otherwise choose ACC1 only when it permits three.
It would use the computed column counts, not runtime token counts or a new tuner
field. For all currently admitted K256/M128-or-M256 geometries, this selects
only the N128 change. Actual allocation/free remains512; occupancy does not
increase. Exactly two decode WGs and five total WGs remain; initial REG96×640
and the144/80/64/96/96 redistribution are untouched.

## Required private wiring

The current accumulator literals must all agree; changing the mixed helper's
return alone would leave a destructive layout mismatch:

- Mixed stage calculation at74–115: use selected ACC count in decoded fitting,
  returned stage count and `num_acc_tmem_cols`. Both `_make_mixed` calls must
  resolve identically, including the minimum-depth bootstrap and fitted FC1/FC2.
- Shared storage at309 and `_fit_raw_stages` call site: allocate twice the ACC
  count, alongside twice the decoded count. At N128, decoded barriers add16B
  and ACC barriers remove16B. All are Int64 arrays: combined control footprint
  remains equal, though the B/ACC barrier addresses shift. Re-run the existing
  exact allocator; no new raw/B capacity is expected from this exchange.
- Kernel assignments at661, `PipelineUmmaAsync.create(num_stages=2)` at999,
  `acc_fake` stage extent at1052, and MMA producer state at1264 must take the
  selected count. The existing decoded destination uses
  `mix.num_acc_tmem_cols` in both shared `_setup_transform_partitions:325` and
  private MMA `kernel.py:1251`; these must remain identical.
- Private epilogue construction must explicitly set the matching physical and
  pipeline counts and rebuild its cached stage layout after `super().__init__`.
  The immutable vendor constructor `epilogue_refactor.py:1084–1105` hardcodes
  physical2 and records `(cta_m,cta_n,2)` with stage pitchN. The private geometry
  initializer is a narrow ownership point for this adjustment; vendor edits or
  a copied epilogue loop are unnecessary. Extend the existing column assertion
  to compare the physical layout and both stage counts.

The private run loop already selects `acc_consumer_state.index`, advances once
per work item and uses `self.num_acc_pipeline_stages` (`epilogue.py:158–208`).
With one stage, index stays0 and phase toggles **every output work tile**;
producer starts phase1 and consumer phase0. Do not reset it at FC1/FC2/expert
boundaries or tie it to K-loop counters. Decoded state still advances modulo3
per K tile. The saved installed PipelineState source in
`w4a16_n64_transform3/pipeline-state-reference.txt` supports this progression.
The saved `PipelineUmmaAsync` implementation in
`w4a16_m128n64_cluster1/installed-pipeline-reference.txt:827–1025` allocates full
and empty arrays from the supplied count; its tail advances `count-1` then
acquires. For count1 that is zero advances and one acquire, not a missing drain.
This is retained dependency-source evidence, not a new installed-library check.

## Ownership and the overlapping-accumulator distinction

`allow_overlap_acc=True` is **not** this proposal. Vendor code keeps two physical
stages, reduces the logical pipeline to1, overlaps part of their column ranges,
and selects storage by phase/odd turn. W4A16 correctly rejects that mode. Keep
`overlapping_accum=False`, zero overlapped columns and normal index selection;
the actual accumulator tensor's extent must be1.

MMA already acquires ACC before any output-tile MMA, waits for decoded A and
activation B separately, releases each K operand, then commits ACC once
(`kernel.py:1274–1295`). The first K16 atom disables accumulation for every work
tile (`dynamic_mainloop.py:107`), so the reused physical slot is overwritten.
Decoded stores must begin at128, never at the old physical stage1 by accident.

Both CTAs' epilogues may still use accumulator TMEM as transpose scratch after
their initial loads. Preserve the existing per-warp load fences and release
count128×V:128 for one-CTA MMA,256 for two-CTA MMA. `PipelineUmmaAsync` retains
the V-dimension completion mask and peer-CTA release destination. The leader
cannot overwrite until all participating consumers release the same phase.
No CTA may choose a stage count from its local valid-row count.

Current FC1 releases after all subtiles, final scratch reads/fence and stores.
Retained FC2 releases after the final static subtile's post-reorder scratch
reads/fence, before its register packing/STG; its existing final guard else
releases exactly once for zero tokens or N128≤64. Held FC1 epilogue943f analogously
releases after the last static half's scratch reads, retaining the ordinary
fallback release for partial/zero cases. Those safe boundaries permit the next
MMA to overlap only the remaining RMEM/output work. They do not make the initial
FP32 LDTM a safe release point. Validate both CTA halves and every partial path.

Every current epilogue call releases before the outer loop requests the next
scheduler item and publishes completion (`epilogue.py:205–234`). Thus no new
source-level cycle requires MMA to overwrite this slot in order for its owner
to release it. FC2 activation still waits for FC1 publication, not ACC release.
Metadata, raw/B rings, dispatch and all final drains must stay independent.
Numerical/lifecycle execution is still needed to establish this with one slot.

## Tradeoff and prior evidence

The extra decoded stage can hold one more K tile while MMA waits for activation
or while epilogue owns ACC. It removes output-tile double buffering: MMA cannot
start the next output's accumulation until the previous epilogue finishes its
required scratch reads. It cannot hide that serialization with additional weight
buffering once the decoded ring fills. Early post-scratch release reduces the
remaining serialized work but does not remove the activation/reorder work.

Retained split `_compute_stages_and_tmem_cols:2318–2350` uses real ACC1 for
≥256-column accumulators and ACC2 below256, with stage-indexed producer/consumer
layouts and pipelines throughout. This establishes an existing single-physical-
stage mechanism; it does not select ACC1 for current Mega's128-column case.
The split ledger `../flashinfer-w4a16/w4a16_optimization_experiments.md:1874–1916`
records a broad reduction that included ACC2→1, passed its correctness check,
but regressed EP8 T4096 by about7%; the retained policy only reduced ACC3→2.
That prior split result is relevant negative performance evidence, not current
Mega measurement. The current Mega ledger and held stage notes contain no
isolated actual ACC1/decoded3 trial found by this bounded search.

A later native gate must prove one actual ACC full/empty pair, phase reversal
each output, three decoded pairs/modulo3/tail, identical shifted decoded A
addresses in producers/MMA, and no epilogue scratch access at columns≥128 for
N128. Require identical math/load/store counts, two decode groups, no spills or
MMA cloning, preserved early alpha, all partial/empty releases and two-CTA masks.
Use existing long-K/phase-boundary, return-mode and graph/refill numerical
oracles; no new timing framework is implied. Any performance trial reports all13
rows and uses8–4096 retention criteria. Benefit remains unknown.
