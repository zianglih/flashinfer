# Remaining fixed8 overlap hypotheses

Local source/history investigation after raw4 rejection, 2026-09-09. No kernel,
catalog, runtime, GPU, native compilation or GitHub change. FC1 scratch release
is already in flight and fused BF16 staging is already prepared; neither is a
new proposal here. The current clean eight-tactic product and five-WG/two-decode
roles remain the reference. These hypotheses have no measured benefit.

## 1. Revisit the held group256 direction without reviving its old18 catalog

This is an existing, unexecuted scheduler opportunity, not a newly discovered
knob. Current `shim/autotune.py` keeps group_hint512 in all eight dictionaries.
The scheduler's `_advance_group` in
`src/moe_nvfp4_swapab/fc1_fc2_fuse_sched.py:1098–1155` greedily includes whole
experts until their cumulative FC1 cluster-tile work reaches group_hint. It
then emits that group's FC1 range followed by FC2; `_switch_to_fc2:1032–1050`
rewinds the saved group offsets and changes phase. The threshold counts FC1
cluster tiles, not tokens or experts. It neither changes grid size nor splits
a heavy expert to enforce an exact threshold.

For I2048/M256, one routed-token cluster tile contributes16 FC1 feature tiles
per expert. In the illustrative case of32 local experts each using one such
token tile,512 groups all32 while256 can create two16-expert groups. This is
source arithmetic, not a claim about observed routing. Below the threshold,
or under whole-expert skew, both values can produce identical boundaries.

For the actual H7168/I2048/E256/EP8 workload there are32 local experts. If
expert e receives r_e routes, its FC1 contribution is
`16*ceil(r_e/N)` and FC2 is`28*ceil(r_e/N)`, where N is64 or128 for the current
product. Thus changing256/512 can change the linear FC1/FC2 order whenever
the whole-expert prefixes cross different thresholds. Exact r_e is required
to say which benchmark rows do so; global token count alone is insufficient.
There is no FC1-completion requirement in this index mapping: FC2 metadata can
be emitted with `peek_ready=false`; the real activation wait remains later.

`force_static_sched=True` does **not** select static work assignment here.
The inherited constructor (`src/moe_nvfp4_swapab/kernel_fc12.py:95–120`)
requires the lean scheduler family and rejects the unwired CLC alternative.
Separately, private `_launch_fc12:632–648` passes `load_balance_mode` and
group_hint unchanged; the actual dictionaries use`atomic_counter`.
`fc1_fc2_fuse_sched.py:859–953,1389–1407` therefore uses a global atomic
cluster-tile index and DSMEM broadcast, rather than the static-stride path
at842–856. The index is decoded through the same group boundaries
at1305–1349. Atomic assignment changes which cluster receives a tile, and
clusters need not complete in assignment order, but it does not erase or
force512 grouping. Smaller groups advance some FC2 indices; they do not
create a cross-cluster FC1 barrier or guarantee earlier physical FC2 issue.

Earlier FC2 metadata lets warp5 fetch FC2 weights and both decode WGs transform
them sooner (`shim/w4a16/kernel.py:1074–1116,1218–1245`). Warp6 still waits for
the matching FC1 completion before reading its activation buffer
(`1142–1163`). Producer/consumer index and phase persist across work tiles;
all raw/B/decoded/accumulator ownership and the existing completion counters
remain necessary. Group storage is not a new ring and does not increase with
group count. More groups also mean more phase changes, metadata scans and
possibly earlier stalls on FC2 activations; less independent FC1 work can hurt.

**Measurable hypothesis:** shortening producer-to-consumer distance for some
expert groups improves the full-forward GPU span or activation reuse enough
to offset extra scheduling transitions. Compare complete AUTO100 runs over
the unchanged eight geometries/flags/returns, changing only the existing
group_hint value if root selects this trial. Retention remains8–4096; retain
all13 rows and realized choices. Do not use a host grouping prediction as
primary latency or tune a special token range. No fresh baseline is requested.

The [existing group audit](../w4a16_group_hint_audit/README.md) and
[source-only fixture review](../w4a16_group_hint256_independent_review/README.md)
already provide the API/lifetime analysis and a balanced E8 fixture whose256
and512 boundaries differ. The normal E4 small fixtures and merely increasing
their skewed token count do not prove changed group boundaries. Actual routed
counts/group boundaries are required if the direction is selected. That
fixture reuses the original oracle; no new harness is proposed here.

The old [group256 curated18 patch](../w4a16_group_hint256_curated18/README.md)
targets an obsolete16-entry catalog and must stay held. Checked current/older
ledgers contain no isolated256-versus512 W4A16 execution. Earlier profile
comparisons also changed static/atomic scheduling and flags, so they are not
evidence that256 wins or loses. Split W4A16 has no fusedFC1/FC2 group axis.

## Closed source question: activation address preparation

The initial source-only question was whether warp6's GMEM view, nonleader
shift, partition and TMA address setup in `_activation_task:867–894` could
move before its dispatch/FC1 readiness wait at1124–1127/1142–1149. It would be
legal to prepare those scalar operands from the copied work record while
keeping every payload read, B-slot acquire and TMA after the same dependency.
`moe_persistent_scheduler.py:169–191` copies metadata into registers before
releasing its slot; `custom_ext.py:438–475` forms the B view without loading
activation or dispatch-routing payloads. Other Mega implementations retain
the same conservative source ordering; the split kernel supplies comparable
address construction, not a tested per-tile reorder.

**Do not prepare this patch.** Root relayed design's actual current SASS read:
meaningful GMEM/shift/tile/descriptor preparation is already before the
readiness spin in both FC phases and both geometries. Only seven simple
uniform/setup instructions remain after the wait, with no descriptor or
payload load. Saved evidence: `../w4a16_activation_setup_current_native_audit.md`
(SHA prefix6a3cd87c). The compiler already supplies the proposed useful overlap;
source order was misleading. This is a negative codegen finding, not a
performance measurement, and it removes the second implementation candidate.

## Deliberately excluded repeats

The [20ae audit](../w4a16_next_overlap_audit_20ae/README.md) already records the
decoded-A-only MMA readiness probe, and the
[0d795 audit](../w4a16_next_overlap_audit_0d795/README.md) records raw-producer
carried acquire. Neither had a demonstrated useful independent instruction
window. They are not new recommendations here. Descriptor prefetch, activation
producer carry, dual-operand polling, broad packed/decode lookahead, early raw
release, raw4/raw7 and B4 have prior rejected or insufficient evidence. No
decode instruction change, one-/four-WG alternative, shape-specific dispatch,
PDL protocol or communication-tail barrier removal is proposed.

Only the held group256 direction remains a distinct structural scheduling
hypothesis from this pass. It stays behind the existing FC1 release and BF16
staging work; no additional preparation or execution is requested now.

Source anchor: private kernel SHA
`7e16537e99d9b959242f2e3dc7d07aa329c9feef439f3466c6d4254b097cc315`
(published fixed8/raw5 content2fe). FC1 epilogue changes in the next active trial
are separate; no source ID for an unexecuted combined candidate is declared.
