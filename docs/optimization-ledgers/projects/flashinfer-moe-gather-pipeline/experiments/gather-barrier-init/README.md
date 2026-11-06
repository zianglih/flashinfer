# Lane-distributed gather barrier initialization

Unstaged prototype on retained `49c91adf`; swap kernel SHA `352388283b692ee26a5f35395ddbc089ef02988f0c48ed1cb6af675737bf6022`. Only the two custom FC1 gather-barrier arrays change initialization ownership: warp0 lanes initialize distinct stages in constexpr32-lane chunks. Barrier addresses, arrival counts, the existing all-thread init fence, two-CTA cluster rendezvous, and all-thread TMEM allocation rendezvous remain unchanged. FC2 has no gather initialization and is unchanged.

The generic mapping has no stage-depth cap. The present planner's maximum observed depth is11; that is evidence, not dispatch policy. Distinct lane addresses lower to two predicated `STS.64` sites and one extra `SYNCS.CCTL.IVALL`, without an elected dynamic-address serialization loop in the four captured signatures. This is a code-generation observation, not a timing claim.

Eight exact calls / twelve actual native pairs passed with unchanged resources and zero local memory. Captured FC2 and combine PTX/cubins are byte-identical. The added W4A4 case uses actual native CLC, PDL, SF16 and K96; per-token covers SF16/K96 and two CTA. Initial cases cover static one/two CTA, narrow/wide N, MXFP4x8 and MXFP8. This is bounded qualification, not the full accuracy suite or a sanitizer run.

| FC1 signature | Removed serial init sites | Startup non-NOP | Rest of kernel non-NOP |
|---|---:|---:|---:|
| MXFP4x8 N16, 1CTA |20|110→89|1102→1105|
| MXFP8 N256, 2CTA |12|177→166|3469→3466|
| W4A4 N16, native CLC+PDL, K96 |18|129→112|1122→1121|
| Per-token N128, 2CTA, K96 |8|159→152|3150→3150|

The narrow MXFP4x8 body has compiler churn (+3 net instructions, including additional R2UR/election sites). Savings in startup therefore do not establish end-to-end gains. Keep all performance losses and repeat/clock records.

`qualification-gate.json` binds the frozen source, two immutable four-call campaigns, actual PTX/cubins/SASS and resource records. `performance/screen/perf-config.json` prepares23 jobs /28 supported swap arms at tokens32 and4096:56 cells, four CAAC phases,100 native CUPTI samples per phase,22,400 samples. It keeps original explicit recorded tactics/routes, NVFP4 input quantization and unfused swap finalize. W4A16 is outside this screen. Both independent setup reviews and release-cache/idle preflight passed. The56-cell CAAC screen completed all23 jobs on original-node GPUs0–1 asPID109366, with full source postflight and unchanged native libraries. GPUs0–1 are idle/released. Full raw replay and independent audit passed. Rejected as performance neutral: overall+0.03138%, tokens32+0.06662%, tokens4096−0.00385%;21/56 cells regress. All112 paired native compilation resources are unchanged with LOCAL0. Two of896 telemetry quartiles are missing; no observed clock exceptions. No full364 expansion. The completed review worktree and branch were retired; source, patch, helpers and evidence are preserved.
