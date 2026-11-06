# Shared FP32 exchange: compile-only R1

Frozen ce4-based kernel `fb91defb`. All8 representative FC1 signatures and8 matching FC2 captures completed without launching an owned MoE kernel. `codegen-analysis.json` binds all119 fetched artifacts and immutable ce4 controls. This is not an eight-case numerical pass.

All FC1s retain168 launch registers and their original120/128/256 role quotas. Seven have zero stack/local sites; the pre-existing M512/N128/K8 MXFP4x8 stress case retains160-byte stack and20LDL/20STL sites. No resource/local-site increase. Shared payloads lower as exactly16 scalar STS, four LDS128 and two warp barriers per exchanged fragment. All FC1 TMEM transpose stores disappear.

| FC1 signature | Total SASS sites, before→after | Operand stages |
|---|---:|---:|
| NVFP4 N256, one CTA |3632→3448|2→2|
| GeGLU per-token N128 |1504→1512|3→3|
| SiTU MXFP8 N16 |1344→1384|5→5|
| NVFP4 N16 |1488→1504|10→9|
| MXFP8 N256, one CTA |3880→3664|2→2|
| MXFP4x8 M512/N128/K8 |4264→4080|2→2|
| ReLU2 NVFP4 N256 |4088→3640|2→2|
| Native N3U EP16K MXFP8 ReLU2 |4200→3744|3→3|

The mixed instruction deltas preclude a universal instruction-count claim. Additional scratch grows by8192B where stage depth is unchanged; one sampled decode signature loses one stage. The independent full native-planner audit reports87/364 cells lose one stage, including21 prefill; no problem-specific enablement was added.

All8 FC2 PTX blobs are byte-identical. Seven CUBIN/SASS pairs are also byte-identical. The wide one-CTA MXFP8 FC2 instead changes only12 uses/definitions of the uniform register pairs UR16/17 and UR18/19 between PCs0x1420 and0x2180; the analyzer proves that pair permutation maps every instruction in the interval exactly, with all other instructions unchanged. Both have2328 sites and identical resources. This is explicitly not a byte-identical CUBIN claim.

Source/math/mapping/lifetime peer review passed (`peer-source-audit.json`). Initial alignment-annotation failure is preserved in sibling `shared-fp32-transpose-ce4`; R1 adds the proven16-byte private pointer alignment, with unchanged payload geometry. Next qualification must compose the retained b52 quota change, compile against its immutable controls, and run the existing exact gate before any timing.
