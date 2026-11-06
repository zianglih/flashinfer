# CLC metadata padding: rejected before timing

Source4951b965 adds only two zero stores to the reserved fourth metadata word, based on clean c1ac. Four existing exact arm calls and six native pairs pass; source/cache pre/post and fresh GPU2 idle closure pass. All four capture/oracle helpers are unchanged. There was no timing run.

| Case | Kernel | Non-NOP control→candidate | Registers | Driver CTA capacity |
|---|---|---|---|---|
| nvfp4-clc-1cta | Sm100BlockScaledGroupedGemmKernel | 1251→1252 | 168→168 | [1, 1] |
| nvfp4-clc-1cta | Sm100BlockScaledGroupedGemmKernel | 873→873 | 76→76 | [1, 1] |
| nvfp4-clc-1cta | _MoeFinalizeKernel | 81→81 | 26→26 | [None, None] |
| nvfp4-clc-2cta | Sm100BlockScaledGroupedGemmKernel | 1547→1548 | 168→168 | [1, 1] |
| nvfp4-clc-2cta | Sm100BlockScaledGroupedGemmKernel | 1061→1061 | 72→72 | [1, 1] |
| nvfp4-clc-2cta | _MoeFinalizeKernel | 83→83 | 26→26 | [None, None] |

All LOCAL0, shared bytes and compile options unchanged; both finalizers have raw-identical PTX/cubin/SASS. Driver capacity is not measured concurrent residency.

Both live and terminal scheduler publications consolidate from STS.64+STS to STS.128 in each GEMM. However, the live publisher materializes the fourth zero with HFMA2 (one-CTA) or IMAD.MOV (two-CTA), and terminal publication adds CS2R zeroing. These replace the removed store instructions. There is no net issue-work reduction; FC1 grows one non-NOP and FC2 stays equal. No new counter/branch reduction or metadata bottleneck evidence offsets this result. Parent rejected before any timing; no rewrite, route-slot revival or rescue.

Representative one-CTA FC1: control live STS.64/STS at0xc50/0xc60 becomes zero HFMA2 at0xc40 plus STS.128 at0xc60. Terminal replaces scalar-zero STS with CS2R at0xdd0. Two-CTA FC1 uses zero IMAD.MOV at0x12a0 then STS.128 at0x12c0; terminal CS2R at0x1430 then STS.128 at0x1450. Full opcode deltas remain in qualification-summary.json.

Raw: qualification/evidence (archive SHA2575264a104193c560f4ea518fe5d5b25470ea8bce885c2c8c13c3ec2d5b2952). Native comparison replay: analyze_qualification.py. Candidate patch/source/static checks are preserved at this experiment root. The first fetch was correctly rejected while full source postflight was incomplete; no partial archive or result was used.

The current production consumer interface and unused fourth-word behavior remain unchanged. Historical route-in-slot3 and uniform-route variants remain separately rejected; see ../../audits/clc-metadata-vector-c1ac.md.
