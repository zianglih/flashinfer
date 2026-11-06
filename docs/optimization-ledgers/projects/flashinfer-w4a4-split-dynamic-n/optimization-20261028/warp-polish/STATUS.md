# Warp-pipeline polish status

Retained and pushed: `17bff619c11dcbf65bd6394546fa70b21999b9ef` on PR7290.
Canonical source is clean. The follow-up changes only the swap-AB kernel (9 added,
15 removed lines): weight announces combined operand bytes while both producers
retain independent reuse waits and TMA issue. No new tactic, API option, shape
rule or synchronization was added. The earlier retained cb35 evidence remains
under `combined/`.

Current qualification:176 exact comparisons,88 paired kernels, unchanged stage,
shared-memory and TMEM geometry, zero local-memory/stack spills, and zero GDC in
44 PDL-off variants. Ruff, mypy and all applicable commit hooks passed. Matched
CAAC measured -0.022% overall, +0.065% decode and -0.109% prefill. A stable1.057%
V3 MXFP4x8 T4096 cost is documented. Retention is for a simpler protocol and one
fewer full-barrier announcement per operand stage, not a speedup claim.

Final full13-token CUPTI run:208 cells,416 medians,41,600 samples; all342 measured
source files match17bff619c. All external baselines and unchanged W4A16 were
reused. Tokens1/2 are omitted from display and retention. Against saved99f4
(historical, not matched cb35), overall +0.127%, decode +0.339%, prefill -0.437%.
Some16K timings occupy overlapping bands. Full44x9 table, red/white/green plot,
raw outputs, source binding and publication receipts live in `final-polish/`.

Closed/rejected experiments:

- Routed FC2 layout: -0.292% overall, -0.867% T4; larger small-batch scratch.
- Scatter4 r2: +0.134% overall, +0.265% prefill; implicit lane arbitration.
- Scatter4 r3: -0.167% overall, -0.344% prefill; excess coordinate liveness,
  uniform-register spills and code growth after full issue-loop unrolling.
- Scatter4 r4: +0.0043% overall, -0.0024% prefill; effectively neutral and not
  worth descriptor/metadata complexity plus5.55% larger inspected FC2 text.
  Main96-comparison gate passed. Bulk32 control64 replays and16 candidate NVFP4
  comparisons passed before the owned run was stopped; remaining candidate
  modes are unqualified. FP16 full-chain probing met the existing BF16-only
  unfused combine restriction, which was left unchanged.

Owned completed review clones are removed; see `final-polish/review-cleanup.json`.
The unrelated layout-API review and old-CuTe baseline remain untouched. Project
helpers, proofs, raw evidence and persistent native compilation caches remain.
No GPU experiment remains running. `SYNCHRONIZATION_AUDIT.md` records the lifetime
proofs and remaining necessary waits. Prior rejected single-transpose and SFB
multicast mechanisms were found in the ledger and were not repeated.

Sanitizer remains skipped as requested. Remaining performance gaps are visible
in the full table and are not claimed closed.
