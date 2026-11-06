# Control warpgroup quota112→120

Candidate: c0c0bc41 plus one constant change, control quota112→120. Gather128, epilogue256, launch384threads and168initial registers stay unchanged. The total64512-register demand exactly fits the executable initial CTA reservation. No dtype/model/tile predicate or tactic change.

The broad native search exposed a new wide MX tactic outside the earlier fixed-winner guard set. At N3U EP8,16384tokens, both MXFP8 and MXFP4x8 selected FC1 N256/twoCTA/K256. Fresh executable codegen confirms112 has an8-byte stack frame,7LDL and1STL sites;120 has zero stack/LDL/STL. The spilled scalar is total_tiles: num_tiles[0] loaded at0xb90, multiplied by20 at0xbd0, then stored before the role-specific register decrease.51 uniform-to-GPR MOV.SPILL and51 R2UR.FILL sites remain in each version; they are distinct from local-memory spilling. The legacy helper's UR2R.SPILL-only count misses this MOV.SPILL spelling; codegen-summary.json includes both.

FC2 SASS equality for the two dtype captures: [True, True]. These captures use compiler artifact flags and are diagnostic only, not retention timing. Source, native-selected winners, routes and executable register reservations were verified. The candidate's first harness attempt stopped before compilation because the copied guard still asserted112; the independent guard was then explicitly changed to120 and rerun. Production source was unchanged by that repair. Raw evidence is under evidence/ and all96 exported files were hash verified.

The general120 policy is undergoing existing exact cases and source-bound C-A-A-C across models/dtypes before any retention decision.
