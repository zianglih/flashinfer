# Current five-WG FC1 post-scratch release: native review

**PASS for the planned runtime/numerical gate.** These are the two current candidate-only captures on epilogue943f, kernel7e/raw5 ceiling, explicit scheduler2 and five WGs. Performance owns original source/native/process/resource admission; no control was recompiled and the reviewer performed no native/GPU action. Historical512/REG128 captures are not current admission.

| Current epi-return fixture | Actual B/raw/decoded/S | Saved five-WG S2 reference rows | Current rows | Change | REG / stack / local / MMA |
|---|---|---:|---:|---:|---|
|M256/N64/C2|3/5/3/2|5528|5536|+8 /128 bytes|96 /0 /0 /16|
|M256/N128/C2|3/4/2/2|5840|6072|+232 /3712 bytes (+3.97%)|96 /0 /0 /16|

References are `profiles/scheduler-depth2-activation-b3-m256n{64,128}c2-001/candidate/codegen`: saved actual B3/S2/epi144, with the same descriptor geometry. Their default-S2 host source differs from the current explicit-S2/default-S3 catalog arrangement; this is saved resolved-configuration code context, not a fresh paired performance/control run. Current capture results attest epilogue943f and unchanged kernel7e/frontend6e44/dynamic-mainloopaac315.

## Actual ownership and partial paths

| Path | Final two scratch loads | PTX load-wait annotation | ACC arrival | Subsequent packing /256-bit STG | Normal fallback arrival |
|---|---|---|---|---|---|
|N64|0xa520 /0xa530|0xa540|0xa550|0xa570–0xa5e0 /0xa5f0|0xa640|
|N128 final subtile|0xb510 /0xb520|0xb530|0xb540|0xb560–0xb610 /0xb620|0xb670|

Each PTX sequence explicitly contains both `tcgen05.ld.sync.aligned.16x128b.x4` scratch reads, then `tcgen05.wait::ld.sync.aligned`, the existing cluster-mapped accumulator barrier arrival with count1, and only RMEM permutation/packing, output addressing and STG afterward. The SASS NOP carrying the fence source line is not itself the completion proof. There is no subsequent TMEM access on the successful FC1 path before the next-work join.

N64 valid>=1 selects the full two-half body. Its early arrival precedes the lane/feature store predicate, so every epilogue thread arrives even when its output row is masked; both successful branches bypass the normal fallback arrival. Zero valid tokens bypass the body and arrive once through the fallback. Both sites form the same accumulator-empty address from stage base+0xc0 and the unchanged cluster mapping.

N128 computes valid>=1 and valid>=65 before acquisition. Zero bypasses the first body and final body, then arrives once via fallback. Valid1–64 executes only the first subtile, including both halves and its stores, then takes the final guard's fallback. Valid65–128 executes both static subtiles, then reaches exactly one early arrival after final half1. Both final output-guard paths bypass fallback. Early and normal arrivals use the same stage base+0xa0. No runtime last-subtile helper dispatch or inactive-half guard was added. The partial-tile behavior remains the intended static-final-subtile contract, not earliest release on every N128 partial tile.

The group/count constructors are unchanged:128 epilogue participants per CTA,256 accumulator consumer arrivals across the two-CTA instruction. Output completion remains later: the original outer state advance, scheduler consume, named barrier and FC1 done publication still follow output stores. Accumulator reuse is not token-completion publication.

## Alpha, code growth and unchanged work

N64 alpha LDG0x9470 precedes the blocking accumulator check0x9480. The slow path0x14930–0x14980 uses R2/P1 and preserves alphaR3 and valid predicateP0. N128 alpha LDG0x93a0 precedes check0x93b0; slow path0x16a70–0x16ac0 uses R5/P0 and preserves alphaR56 and valid predicatesP1/P2. The same scalar feeds the existing FP32 multiplies in both N128 subtiles.

N64 adds only the alternate-release branch/address/arrival and NOP count changes; arithmetic/load/store/MMA counts are unchanged. N128 replaces its shared runtime FC1 body with two static subtile bodies. Static FC1 FMUL2 increases80→160, EX2/RCP32→64 each, BF16 packs16→32 and output-store sites2→4, as expected. Per valid subtile the arithmetic and two-half work are unchanged. This is code-size growth, not twice the dynamically executed math for the same route.

There is no extra decoder, TMA or MMA instance: both geometries retain2 packed3D TMA,2 SF4D TMA,8 activation2D/2CTA TMA,16 LDS128,128 FP4 unpack instructions,16 SF unpack instructions,64 HMUL2/64 HFMA2 BF16 and16 decoded STTMx8 sites. Both actual kernels retain640 threads, initialREG96, control80/epilogue144/dispatch64 and two decode groups retaining96, with no LDL/STL or stack/local allocation. Register renaming and some surrounding N128 CFG/constant-load scheduling change; no whole-kernel binary identity is claimed.

Current N128 static growth and the shorter remaining accumulator-live interval must be measured. This review does not predict a gain. Actual numerical/graph/return/tail tests and the authorized AUTO timing remain separate, with all13 rows reported and retention assessed over8–4096.

## Reviewed current artifacts

- `profiles/fc1-post-scratch-release-raw5-fixed8-m256n64c2-001/codegen/result.json` SHA `bb63f97c31dcc1c78d7d6bde52eb45406ec1a77b48801731e8c1a02ea5be73c4`
- `profiles/fc1-post-scratch-release-raw5-fixed8-m256n64c2-001/codegen/sass.txt` SHA `d22bf3d86367f8aac9ace85595a4316ded04e1961c35cd5c03900fed8c020f25`
- `profiles/fc1-post-scratch-release-raw5-fixed8-m256n64c2-001/codegen/dsl/cutlass___call___flashinfermoe_epkernel_srccutedsl_megamoeshim_reuse512_compile_onlykernelSm100W4A16MegaMoEKernel_object_at__FakeTensorBFloat16div1div1i64div11_FakeTensorInt64div1d.sm_103a.ptx` SHA `f80eeb14541a8ddc9b883b02fed212eaeffd415e2daa852503786b4fb500b344`
- `profiles/fc1-post-scratch-release-raw5-fixed8-m256n128c2-001/codegen/result.json` SHA `9ef3379ccec0c832ae943b2c88898695bd47b2347a8c4c7e328e293e5096287b`
- `profiles/fc1-post-scratch-release-raw5-fixed8-m256n128c2-001/codegen/sass.txt` SHA `b3f5c6744826f6a2cc42014429f12e4dcc70c51c016318f8c973a6224f3322f2`
- `profiles/fc1-post-scratch-release-raw5-fixed8-m256n128c2-001/codegen/dsl/cutlass___call___flashinfermoe_epkernel_srccutedsl_megamoeshim_reuse512_compile_onlykernelSm100W4A16MegaMoEKernel_object_at__FakeTensorBFloat16div1div1i64div11_FakeTensorInt64div1d.sm_103a.ptx` SHA `37308714ce144944e83f71f348e3afad6a07022e19ad5aef3b3c6be75e9e0901`
