# Initial fixed-256-thread codegen screen

Snapshot kernel85f12b60, before root argument cleanup and logical-row-only preparation. CLC+PDL representatives below; all128binary records (64per source) are in initial-evidence/codegen-summary-initial.json. Counts are static instruction sites, not executed instructions.

|Config / FC|Registers old→new|Stages old→new|Scalar cp.async old→new|LDGSTS old→new|UTCBAR old→new|SYNCS old→new|
|---|---:|---:|---:|---:|---:|---:|
|0 / FC1|83→75|9→9|4→0|4→0|2→2|131→122|
|0 / FC2|74→70|4→4|40→0|40→0|2→2|145→129|
|1 / FC1|112→110|10→10|4→0|4→0|2→2|151→142|
|1 / FC2|92→86|5→5|8→0|8→0|2→2|137→149|
|2 / FC1|91→82|9→9|2→0|2→0|3→3|149→133|
|2 / FC2|78→78|4→4|4→0|4→0|2→2|121→161|
|3 / FC1|86→79|11→11|2→0|2→0|3→3|175→158|
|3 / FC2|78→70|5→5|4→0|4→0|2→2|145→181|
|4 / FC1|87→72|4→4|0→0|0→0|2→2|104→112|
|4 / FC2|104→94|6→6|0→0|0→0|2→2|166→186|
|5 / FC1|92→90|2→2|0→0|0→0|2→2|78→85|
|5 / FC2|158→152|3→3|0→0|0→0|2→2|127→158|
|6 / FC1|92→87|3→3|0→0|0→0|2→2|100→108|
|6 / FC2|114→112|5→5|0→0|0→0|3→3|134→130|
|7 / FC1|76→74|3→3|0→0|0→0|2→2|85→92|
|7 / FC2|96→96|5→5|0→0|0→0|3→3|118→113|

All sampled candidate kernels have256threads, no scalar SFB cp.async/LDGSTS, no stack/local bytes, unchanged accumulator and operand stage counts, and no SETMAXNREG. The additional independent producer changes static wait/announce instruction sites, so totals do not establish a universal reduction. Epilogue BAR counts and UMMA release sites stay unchanged. The native pipeline expected_tx call elects once and performs an empty wait plus one role-specific expected-byte arrival; it does not require an extra per-stage CTA join.

Config mapping:0 NVFP4 N16/CTA1 SiTU;1 per-token N32/CTA2 SwiGLU;2 MXFP8 N64/CTA1 SiTU;3 MXFP4x8 N16/CTA2 SiTU;4 NVFP4 N128/CTA2 SwiGLU;5 per-token N256/CTA1 SiTU;6 MXFP8 N256/CTA2 SwiGLU;7 MXFP4x8 N128/CTA1 SwiGLU.
