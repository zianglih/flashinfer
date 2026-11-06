# Read-only preparation for the C1/A1 performance decision

No candidate source changes or GPU launches were made for this audit. The frozen
stage-capacity r2 source remains authoritative. This note proposes diagnostics
only; it does not assert new performance results.

## What the existing 13 tactics cover

The actual definitions in `cute_dsl/tuner.py` provide one tactic each at routed
N16/N32/N64, six combinations at N128, and four at N256. FC1 chooses physical
M128 or M256, plus logical M512 at N128; FC2 chooses M128 or M256. Both phases
share the routed capacity. Only M128 is available below N128.

V4.1 Flash introduces no output-channel tail in any of these geometries:

| Phase | V3 | V4.1 Flash | Existing channel tiles |
|---|---:|---:|---|
| FC1 channels, including gate/up | 4096 | 4608 | Both divisible by 128, 256, and 512 |
| FC2 channels | 7168 | 5120 | Both divisible by 128 and 256 |
| FC1 reduction K | 7168 | 5120 | Both divisible by current K256/K512 FP4 tiles |
| FC2 reduction K | 2048 | 2304 | V4.1 has a half-tile tail at FP4 K512 |

The NVFP4 narrow-route K8 policy uses a K512 operand tile. V4.1 FC2 therefore
executes five K512 stages for 2304 values, or 2560 values of MMA work, an 11.1%
padding overhead. V3's four K512 stages are exact. MXFP8 and mixed-format K8
use K256, so 2304 divides exactly into nine stages. The native MMA helper
currently issues all inner-K instructions in every stage, including the tail.

Under uniform routing, V4.1 EP4 expects 1.5T local routed rows across 96 experts,
or T/64 rows per expert. V3 EP8 expects T rows across 32 experts, or T/32 per
expert. Thus at T4096/8192/16384 the expected V4.1 occupancies are 64/128/256,
versus 128/256/512 for V3. These are analytical averages, not measured routing
histograms. Existing N64/N128/N256 choices already cover those capacities.

Dynamic MMA N prevents the entire N128 compute tile from being wasted when an
expert has 64 live rows. Physical operand storage and epilogue work still differ
between N64 and N128, while N128 can use channel reuse and two-CTA instructions.
The full-chain tuner should decide that tradeoff; occupancy averages alone do
not justify adding a model-specific routing threshold.

## Attribute measured changes to the actual selected policy

`tactic-policy-map.json` joins all 13 source-derived tactics with the audited
old/new stage counts and bulk slabs for both models and all three benchmark
modes. It is ready to join with C1/A1 selected-tactic outputs.

- NVFP4 N16/N32/N64 retains four operand stages in both phases. MXFP8 and mixed
  N64 also retain four. For matching selections there, the capacity candidate
  changes no active stage/bulk policy; investigate timing variance or changed
  selection before blaming stage depth.
- MXFP8 and mixed N16/N32 change four stages to five in both phases.
- FC1 logical M512/N128 keeps its prior depth for every benchmark mode. Its
  common FC2 M256/N128 partner changes five stages to six for NVFP4 and to seven
  for MXFP8/mixed.
- FC2 M128/N256 deliberately trades four stages and a 32-token/one-stage bulk
  slab for three stages and a 64-token/two-stage slab. Any regression selecting
  this geometry may involve the output-storage tradeoff, not just input depth.

## Smallest controlled follow-ups if the measurements warrant them

1. **Same geometry, neighboring depth.** If a newly deeper selected policy
   regresses, compare its capacity-selected depth with one fewer stage through
   the existing explicit private `num_stages` knob. Keep routing, MMA K, bulk
   slab, producer organization, and all numerical behavior fixed. This is a
   diagnostic, not justification for a new dimension-specific lookup table.
2. **N256 output-storage tradeoff.** If FC2 M128/N256 is the regressing winner,
   compare the existing two valid slab contracts with capacity recomputed around
   each reserve. This isolates the three-stage/wider-output-slab tradeoff.
   Do not silently disable TMA just to fit another input stage.
3. **K4 versus K8 for a reduction tail.** If narrow-route NVFP4 FC2 is a
   bottleneck, compare K256 with the existing K512 tile, allowing the same
   capacity calculation to size their buffers. K256 removes the V4.1 tail but
   increases nine versus five pipeline iterations. The generic predictor is
   padded-K fraction and reduction iterations, not a named model or K2304
   special case. K8 already won prior V3 diagnostics, so both models must remain
   in the comparison.

No tactic expansion is the first step. Prior task-local small-two-CTA trials
were exact but slower in sparse diagnostics (`scripts/decode_geometry_experiment/
RESULTS.md`). The current core also removed unreachable non-TMA cross-CTA SF
relay machinery; enabling M256/N64 would require restoring a correct publication
contract, not merely adding a tactic tuple. Logical channel reuse on narrow
one-CTA tiles would likewise require new TMEM/epilogue geometry. These are larger
experiments to consider only after measured winners and phase evidence identify
that gap.

## Calculation simplification

The current helper split has a useful purpose: actual layouts, byte accounting,
aligned metadata, then the allocation policy. The decrement loop is compile-time
only and preserves barrier-alignment jumps; replacing it with an unproven closed
form would weaken clarity. The two bulk-selection passes handle distinct cases:
reserve-before-autosizing and fit-after-explicit-depth. Removing the explicit
depth tuning knob would permit consolidation, but would also remove the smallest
controlled experiment above. Leave the frozen calculation unchanged until the
performance decision. Any later cosmetic consolidation should be checked against
all 180 saved stage/bulk/storage policy records.
