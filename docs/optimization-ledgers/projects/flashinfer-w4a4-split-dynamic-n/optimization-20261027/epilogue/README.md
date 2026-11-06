# Scatter metadata preload experiment

Parent: `e2728a2908f38cbcfa997c031bea059e3724ccde`. Rejected experiment; the solely owned inactive review clone was removed after verifying its exact patch. This experiment changes only `moe_swap_ab_kernel.py`.

The candidate builds FC2 scatter row and rounded-scale register fragments once per work tile, before the accumulator completion wait. Both direct and bulk epilogues consume those fragments; channel tiles no longer recompute the same routing metadata. The existing helper retains all bounds, per-token indexing, fused-output routing, multiplication and final-scale rounding. The epilogue roles have already completed their PDL dependency wait before these loads. No value derived from the accumulator moves before its completion barrier, and no synchronization, buffer capacity, tactic, activation, layout or public API changes.

Routing fragments live through the accumulator wait, so narrow decode register allocation and local-memory spills are checked before timing. An initial version also moved scalar expert alpha in FC1; that unrelated register-lifetime change was removed before the retained candidate screen. The inactive-channel CTA may now load valid route metadata before skipping its output, but every load remains bounded by the valid route count. The existing final TMEM wait, accumulator release and bulk shared-read drain remain.

Source review consulted the local synchronization audit and closed experiment history. This is not a repeat of terminal bulk-drain deferral, SF32 scratch double buffering, balanced amax, protected-prefix buffering, or allocator/scheduler startup restructuring. Those experiments remain rejected.

The bounded gate adapts the existing public-wrapper source-paired harness: four supported format/scale configurations, narrow and wide routes, one/two CTA, PDL on/off, and changing/empty/reactivated routing. It captures PTX, SASS and resource usage for each compiled FC1/FC2 variant, checks all final BF16 storage bits against the control, and records raw source identities. No sanitizer, native AUTO sweep or broad timing campaign is launched by this gate. GPU2 on the existing C3 B300 devbox; persistent verified C++ cache reused, CuTe cache private to the candidate source.

Status and actual validation results are in the accompanying deployment and gate receipts. No performance gain is claimed before source-bound paired timing.

## Completed gate and initial screen

The v2 source (`915f90bb07113f306a53cc06aa7d9b36f56a827b8770f8080199e92d125f51ed`) passes64 paired exact public-wrapper replays (32/source) spanning tensor NVFP4, per-token NVFP4, MXFP8, MXFP4x8, narrow/wide route tiles, one/two CTA, PDL off/on and changing/empty/reactivated routing. Eight separate small fused-output source pairs also preserve every output bit; fused top-k1 avoids unordered atomic summation ambiguity. These are local qualification harnesses, not additions to the upstream test suite.

Codegen: all eight FC1 SASS files are byte-identical, FC2 register allocations are unchanged, and no spills appear. Some FC2 variants add two actual non-NOP instructions; others are unchanged. The metadata loads move before the accumulator wait in both PTX and SASS (`metadata-order-proof.json`). This is an overlap/reuse change, not a blanket reduction in final instruction count. Original alpha evaluation in FC1 is preserved.

The completed initial frozen native-tactic C-A-A-C screen covers32 cells: four models × four blockscaled modes × T32 and prefill (T16384 for V3/Nemo; T4096 for V41/K3). All48 phases pass the source/tactic/route/CUPTI checks. It uses ten warmups and100 cold-L2 graph samples, includes the NVFP4 input quantizer, and measures unfused public swap-AB API calls. No AUTO rerun or historical latency reuse. Initial geometric mean is1.002423× (+0.242%); most decode gains are0.04–0.29%, V41 per-token T32 is−0.404%. Nemo per-token T16384 is+1.475% with <0.04% phase drift.

The large V3/Nemo MX cells show up to6% control/candidate repeat drift; their apparent gains/regressions are not accepted as stable. A separate four-cell reversed A-C-C-A repeat uses the same source and saved native winners. `timing-summary-final.json` holds the full initial32-cell screen; the repeat is separately recorded in `repeat-timing-summary.json`.

Diff review: one private source file, +33/−34 lines. Register metadata replaces redundant bulk-epilogue route/scale pointer arguments and the unused final-scales argument; no public API or default legacy path changes. The two explicit role-entry builders are necessary to support the existing inline and dedicated epilogue organizations. No additional policy branching, shape exceptions, buffer change or synchronization is introduced.

## Final decision: reject

The reversed four-cell large-MX repeat did not establish a consistent improvement: V3 MXFP4x8 −1.55%, MXFP8 +1.46%; Nemo MXFP4x8 −2.85%, MXFP8 +2.63%. Intra-arm drift remained as high as 5.58%. Nemo MXFP4x8 was negative in both orders, and the small stable gains elsewhere do not justify retaining the extra register-lifetime and internal-argument changes. No large-MX speedup is claimed. Both review copies for rejected epilogue experiments are removed; canonical production and existing user WIP were untouched.

All 56 frozen phases, 14,400 CUPTI samples, source/route/tactic hashes and optional fused output pairs are saved in `timing-evidence/`; independent verification is in `timing-verification.json`. Archive SHA256: `820ba7269fa9be579e9ba55455764bcff1c64dff69765f51efc4dec8062758d1`. No sanitizer run, AUTO expansion, commit or push.
