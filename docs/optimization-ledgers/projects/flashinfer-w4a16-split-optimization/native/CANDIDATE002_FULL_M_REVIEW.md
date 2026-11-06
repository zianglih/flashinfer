# Candidate002 full-M native review

Read-only review, 2026-09-13. **PASS for intended bounds specialization and captured resource fit.** This is code evidence, not a latency improvement claim. No compile, GPU launch, numerical rerun, or benchmark reader execution was performed by this review.

Actual captured source: wrapper `aa446d91adfd1335d59bf30acb8ed240f6b592bd78724d02f230cde7806fd90d`, kernel `22fefac2a21e2efb5f9b5e0f2b402202dddf8f7136c1c50585105466ae2794a0`. Compare `candidate002-full-m-{fused2,ordinary0}-m{256,288}` against `candidate-topk-{fused2,ordinary0}` in this directory. Each result records real compilation and `returned_callable_invoked=false`.

| Case | Immediate top-k SASS rows | Candidate rows | Whole SASS identical? |
| --- | ---: | ---: | --- |
| Fused top-k2, M256 aligned | 1584 | 1568 | No, −16 |
| Fused top-k2, M288 partial | 1584 | 1584 | Yes, including encoding/scheduling |
| Ordinary top-k0, M256 aligned | 1664 | 1624 | No, −40 |
| Ordinary top-k0, M288 partial | 1664 | 1664 | Yes, including encoding/scheduling |

Both partial PTX files are also identical to their controls after removing only `.loc`/`.file` metadata. The baseline M argument was256 but remained dynamic; therefore this is direct emitted-code equivalence for the retained partial handler, not a same-M numerical comparison.

- **Fused aligned:** PTX2928–2931 retains routed-row guarding; PTX2951 sets the copy length to256 bytes (128 BF16 elements), used by `cp.reduce.async.bulk` at2954. The M subtraction, positive-length branch, and min clipping are absent. SASS `UMOV UR6,0x10` at0x38f0 supplies the fixed length to `UBLKRED.G.S.ADD.BF16.RN` at0x4240.
- **Fused partial:** PTX2598–2601 retains Int64 subtraction and128-element clamp; PTX2939/2943 retains positive-length gating; the bulk reduction at2963 consumes the clipped byte count. Whole SASS identity includes those guards and the existing BF16 reduction sequence.
- **Ordinary aligned:** SIMT epilogue predicates contain routed-row comparisons; the additional M comparisons/combinations are gone. Partial ordinary code is exactly the prior implementation. Store bodies/widths, TMA path and pipeline barriers are preserved by source review; the aligned changes are confined to the feature-bound specialization.
- **Resources/ABI:** all four captures remain REG128, STACK0, LOCAL0, static SHARED1024, CONSTANT[2]12; CONSTANT[0]1888 fused/1856 ordinary. GPU parameter declarations are exact (25 fused/23 ordinary), with no new device bool argument. Launch threads512 and four control-role `setmaxnreg.dec80` sites plus epilogue `inc176` remain. Dynamic shared-memory allocation is **not exported** by this compile-only capture;1024 is not total SMEM. Source layouts/stage fitting are unchanged.
- **Quality caveat:** smaller full-path code also changes scheduling. Fused base/stride loads that were uniform `LDCU.64` at0x3690/0x36b0 become predicated per-thread `LDC.64` at0x3b50/0x4090 in the aligned capture. This does not establish a regression cause, but instruction count alone cannot establish a better critical path.

Native scope is MMA128×64×256, cluster1, static scheduler, no activation, PDL disabled, N256/K512/groups8, with actual output tokens65 for fused. C2/CLC/gated behavior relies on the separate source proof and numerical package; these four captures do not claim native coverage for it. No timing result was recomputed here. Root reported the complete candidate sweep at +0.326679% latency GM8–8192 versus its immediate top-k repeat,4/11 lower; the native reduction does not override that lack of demonstrated latency benefit.

Result SHA256, ordered fused256/fused288/ordinary256/ordinary288:

```text
8f0739f6320cc1873203127f04594f1545cbb763387e9879be5ee3c626c2f586
9c42aa02e5d0dbdb3efa412d2085e93f83f1890ab0685f7d482089354f710ad2
532d3e31b2f23c850a49ff9d13521cfc69146e9dd2c5c6d098562fb84212df84
2d44d1ebcd19d28645ffcc705ab103e35c7052bfba5efe1271b7b8c8970ebb66
```
