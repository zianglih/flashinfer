# Regular-TMA scheduler experiments

Retained baseline: `fca8462cbd9096059d0019a206aa760fb34ca8c4`.
PR7290 contains its four complete V3/V41 public benchmark tables and direct
original-to-retained results. Exact publication readback is archived in
`artifacts/pr7290-published-fca8462-model-tables.json`.

The user requested a fresh CLC/scheduler-depth investigation because regular
TMA changes the pipeline balance and V41-Flash has more work tiles. Both V3
EP8 and V41-Flash EP4 determine retention. Tokens1/2 are measured but excluded
from the existing decode/prefill/overall decision groups. Experiments remain
unstaged in independent source copies. No retained source has changed yet.

## Evidence and initial design

- Historical W4A16 scheduler audit and independently recomputed old results:
  `scripts/pr7290_scope_cleanup/clc-w4a16-history-resource-audit.{md,json}`.
  Static metadata depth3 was useful there; CLC favored depth1 because deeper
  queues claimed work ahead of execution. These historical measurements use
  different kernels/token grids and are not present-day retention evidence.
- Previous block-scaled CLC rejection:
  `scripts/clc_current_experiment/README.md`. On pre-regular-TMA442 code,
  FC1 gained roughly1–2%, but whole-chain results were inconsistent across
  order/dtype. Only logicalM512/N128 FC1 was changed in that trial.
- Current exact-route/AUTO geometry diagnostic:
  `evidence/clc-regular-tma-work-audit/README.md`. AtT16384, FC1 work tiles are
  V3NV1232 versusV41NV2502, and V3MX81232 versusV41MX84230. Both use74 resident
  two-CTA clusters. Rounded-N variation also differs. These are geometry
  counts, not measured stalls or a timing model.
- Fresh full native C1s:
  `evidence/pr7290-{v3,v41}-clc-baseline-c1/raw`. Sources, routes, native AUTO
  caches and timing receipts are preserved. V3 usesGPUs4/6, V41 usesGPUs2/3.

First candidate adds one scheduler warp without changing existing producer,
MMA or epilogue warp IDs. Direct compile-time knobs control CLC and metadata
depth. It starts with one metadata slot, acquires that slot before requesting
cancellation, consumes CLC responses with the full warp, filters padded route
slots and publishes one terminal sentinel. Scheduler storage participates in
capacity fitting before operand stage selection. Depth2 remains an independent
lookahead experiment; queue capacity is not automatically maximized with SMEM.

Independent review identified two attribution/compatibility checks:

1. The shared static path changes its work loop from `for` to `while` when the
   CLC helper is introduced. A false-CLC control is needed to isolate this
   codegen change from the scheduler mechanism, especially for unchangedFC2.
2. A full CLC problem grid does not honor a smaller caller-provided `sm_count`
   the way the old persistent grid does. The next candidate disables CLC when
   the caller reserves fewer SMs than the device has. The first gate source is
   preserved as an experiment and will not receive a performance sweep.

Resources are captured independently from cleanfca onGPU0, including compiled
registers/local memory/SMEM/occupancy and PTX/SASS. Correctness during this
iteration is a targeted persistent/raw-output/SF comparison; broad numerical
and sanitizer gates remain deferred until a performance candidate warrants it.

## Frozen R2 admission and initial gate

`flashinfer-clc-scheduler-reservation-review` preserves the explicit SM budget.
Its full patch is pinned by `evidence/clc-regular-tma-r2/source.json` (SHA256
prefix `eb431be4`). The revised gate passed 57 exact payload/scale cases,
including zero-live one/two-CTA sentinels and explicit SM2 fallback; 360 actual
layout policies fit shared memory. Source bytes were unchanged during the gate.

The baseline-winner admission audit found all 78 model/dtype/token cells
eligible under the allocated-grid policy. Twelve are eligible only because of
padding, all at excluded tokens1/2; every retained-grid point (T>=4) has more
live work clusters than resident capacity. This narrows the first performance
question to scheduler overhead versus balancing, rather than accidental
activation on a one-wave retained workload. Recompute this check for candidate
AUTO winners, which may choose different geometries.

V3 and V41 native A1 sweeps completed on the same GPUs as their fresh C1s.
A separate CLC-disabled control measures the shared loop refactor. No new
optimization is retained at this point.

## First native screen (not a retention result)

| Model | Precision | Decode C1/A1 | Prefill C1/A1 | Overall C1/A1 |
|---|---|---:|---:|---:|
| V3 | NVFP4 | 1.005900 | 0.982511 | 0.999466 |
| V3 | MXFP8 | 1.001794 | 1.019945 | 1.006712 |
| V3 | MXFP4×MXFP8 | 1.006152 | 0.997729 | 1.003848 |
| V41 | NVFP4 | 1.007095 | 1.007647 | 1.007245 |
| V41 | MXFP8 | 1.001740 | 0.964199 | 0.991359 |
| V41 | MXFP4×MXFP8 | 1.016643 | 1.002093 | 1.012654 |

The V41 MXFP8 T16384 regression (0.889448×) coincides with FC1 AUTO changing
M256/N128 to M512/N128; FC2 is unchanged. V3 NVFP4 T8192 changes FC1 the same
way and measures 0.958514×. This correlation is not yet proof of causality.
V3 MXFP8 T16384 improves 1.074978× with unchanged M256/N256 tactics. Preserve
all measurements and choices, including unfavorable ones. Complete A2/C2 and
run fixed-geometry diagnostics before interpreting these small aggregate gains.

The false-CLC loop-refactor control is approximately neutral in four fixed
V41 NVFP4 cases (1.0013×, 1.0010×, 0.9994×, 1.0052×); the last case has visible
baseline drift. It does not establish an exact codegen identity. Full source,
routes, tactics and timings are in the paired experiment evidence.

## Completed queue-depth decisions

R2 completed C1/A1/A2/C2 on both models. Across the three affected formats,
overall geometric means are V3 **1.003019×**, V41 **1.007980×**. The full
six-format breakdown is in each `pr7290-*-clc-r2-a2/independent-paired` report.
Some prefill AUTO choices are unstable; do not attribute all whole-patch
changes to CLC alone. The static FC2 loop refactor also changes codegen.
R2 additionally passed the existing focused49 gate with no failures/skips;
`evidence/clc-r2-focused49` pins the unchanged source before and after.

**Reject depth2.** Fixed V3 T16 comparisons hold N16/M128 tactics and exact
routes constant: NVFP4 71.712→73.960µs, MXFP8 114.680→118.336µs, mixed
73.9045→80.752µs. Repeats agree closely. These establish a depth regression,
not proof that work hoarding is the mechanism. Keep the trace hypothesis
separate from the measured result.

**Reject a global static metadata queue.** Depths1/3 passed39 persistent exact
cases and360 layout checks, but fixed NV decode is0.2–0.7% slower, MXFP8 decode
is flat/slightly slower and V41 MXFP8 T16384 loses5.5%/3.5%. Mixed decode
improves0.5–1.1%, insufficient to justify the global replacement. Raw evidence
and all36 native runs remain in `evidence/static-tile-info-r1`.

**Final policy screen:** `flashinfer-clc-single-cta-review` retains the exact
R2 core and depth1, with the FC1 caller requesting CLC only for one-CTA tactics.
This isolates cross-CTA scheduler coordination without model/token/dtype
thresholds. Seven of13 existing paired tactics request CLC; six use the
existing static fallback. FC2 remains static. This is an experiment, not a
retention decision; both model grids still determine whether it is useful.

The one-CTA A1 screen completed with all source/route/tactic checks passing.
Across the three affected formats, V3 decode/prefill/overall are
1.006538/0.996693/1.003843×; V41 are1.010754/1.007818/1.009952×.
The repeated V3 NV T8192 loss from general R2 is absent here (1.000161×,
unchanged M256/N128). V41 mixed T16384 loses (0.931303×) and MX8 T16384
gains (1.151282×), both with unchanged wide static tactics. This is not
evidence of CLC balancing those particular tiles. A2 and a closing fca
control are required before retention; the preceding fca C2 is this
candidate's opening control. No source has been integrated at this point.

## Final retention decision

Retained and pushed **0c1e00fc3e4f913c8c241796c70a29673737c542**: one-slot CLC
for one-CTA FC1 tactics. Two-CTA tactics and FC2 use static scheduling. The
same generic SM-budget and work-capacity guards apply across models/dtypes.
No new tactics or model/token thresholds were added.

Both C1/A1/A2/C2 campaigns passed independent source, GPU, routing and timing
audits. Every median and native AUTO choice is kept. Speedups below are
geometric means of sqrt(C1*C2/(A1*A2)), excluding measured tokens 1/2.

| Model | Format | Decode | Prefill | Overall |
|---|---|---:|---:|---:|
| V3 EP8 | NVFP4 | 1.004833× | 0.998744× | 1.003168× |
| V3 EP8 | MXFP8 | 1.003144× | 1.003449× | 1.003227× |
| V3 EP8 | MXFP4×MXFP8 | 1.010407× | 0.996163× | 1.006502× |
| V41-Flash EP4 | NVFP4 | 1.012591× | 0.997696× | 1.008507× |
| V41-Flash EP4 | MXFP8 | 1.000542× | 1.029900× | 1.008465× |
| V41-Flash EP4 | MXFP4×MXFP8 | 1.019266× | 1.010294× | 1.016811× |

Across formats, overall ratios are V3 1.004298× and V41 1.011253×.
NVFP4 and mixed decode gains repeat. V3 MXFP8 T4 loses 1.3% and V41 MXFP8
T8192 loses 2.5%; retain these outliers in all reports. Large-prefill variation
and static FC2 codegen changes preclude attributing all gains to CLC balancing.
General two-CTA CLC, depth2 and static metadata queues remain rejected local
experiments. No NCU/iKET trace was collected during this scheduler round;
existing markers and PTX/SASS resource evidence are preserved.

Review found a launch-grid boundary after paired timing: CLC grid Y equals
allocated route-tile capacity and cannot exceed 65535. The final host-only
guard uses static scheduling above that architectural limit. Kernel bytes
and resolved constructor inputs are identical for all 156 measured dispatches
and all 338 model/token/tactic cases. Boundary and reduced-SM checks pass.
This is source equivalence for measured dispatch, not whole-file byte identity;
source-fingerprinted disk caches can differ. Evidence is in
`evidence/clc-single-cta-grid-r1/guard-equivalence.json` and `read-only-review.md`.

The exact final clean commit passed the existing **49-test gate**: no failures,
errors or skips; 98 deprecation warnings, 10.94 seconds. All 83 source pins
match before/after (`evidence/clc-final-focused49`). Broad correctness and
sanitizers remain deferred. Integration/push source receipts are in
`evidence/clc-single-cta-retained`. All four fresh current-backend tables
completed on the clean final commit and replaced the previous public PR
tables; original a65 baselines were reused. Complete stdout and source/route
receipts are in `evidence/pr7290-{v3,v41}-clc-final-tables-r1/raw`.

PR publication is verified byte-for-byte against
`pr-body-final-0c1e00fc-model-tables.md` (63,625 bytes, SHA256
`282e65ac9f279f3c21775103a002faa9440886afd91f77fe5c38fdb663322717`).
`artifacts/pr7290-published-0c1e00fc-model-tables.json` records the exact body
and PR head. The draft stays open. The body contains final original-to-retained
results, all four current backend tables and final49 output, not this
incremental ledger. Current single-sweep NVFP4 TRT/CuTe decode ratios are
1.006310× V3 and 0.975938× V41; stable decode superiority remains unestablished.
