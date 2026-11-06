# Count-only startup hoist r3

Independent frozen source: `../../flashinfer-pdl-livecount-review`, integrated PDL parent a92c on853. Only the live routed-tile count is loaded by all warps before the dependency wait and reused after it; no first-expert/limit reuse and no per-role first-tile branches.

Exact public gate324 and persistent named-codegen gate27 passed. `control-codegen-review.json` verifies useful movement with FC2 On registers106→106 and zero local/stack allocation; all other named specializations are byte-identical to control. Full source/commands/pins are recorded in source/gate receipts.

Both-model fixed C–A–A–C results are `../pdl-livecount-r3-fixed/summary.{json,md}`. Paired NV/MX8/mixed gains: V3 +0.180/+0.128/+0.187%; V41 +0.027/+0.156/+0.242%. 19/24 affected points improved in both repeats. V3 MXFP8 T32 is a small repeatable loss (0.998636×); V41 NV is effectively flat. The parent keeps this small change eligible for a combined native retention campaign; no standalone AUTO campaign or production retention is claimed.
