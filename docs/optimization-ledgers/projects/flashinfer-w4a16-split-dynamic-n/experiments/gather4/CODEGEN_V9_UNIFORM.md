# V9 uniform N192 code generation

The captured V9 and V7/cache48 FC1 kernels for H7168, N192, cluster2 are byte-for-byte identical in PTX, cubin, and SASS for both top-k3 and top-k8. Complete decoded instruction/address sequences match as well. The [JSON report](CODEGEN_V9_UNIFORM.json) retains both complete analyses and hashes. Raw captures are under `evidence/gather4/codegen-v9-uniform-k7168` and `evidence/gather4/codegen-cache48-k7168`.

| Top-k | Variant | K-loop address range | Instruction sites | Gather4 | SHFL | R2UR | R2UR.FILL | UMOV | Branches | LDL/STL |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 3 | cache48 and V9 | `0x5a70`–`0x8580` | 690 | 96 | 48 | 76 | 13 | 323 | 3 | 0/0 |
| 8 | cache48 and V9 | `0x5ad0`–`0x8560` | 682 | 96 | 48 | 76 | 13 | 315 | 3 | 0/0 |

Both variants use 128 registers and report zero stack, spill stores, and spill loads. Counts isolate the smallest backward branch spanning all Gather4 sites; the complete function has 2488 instruction sites in each capture. `R2UR.FILL` represents uniform/general-register movement here and does not imply local-memory spills.

The measured T16384 probes select the same complete N192/cluster2 FC1+FC2 tactic record, but V7 took 1233.5945 µs and V9 took 1183.9775 µs. These identical codegen captures provide no instruction-level explanation for that difference. They were compiled by the synthetic codegen harness with `num_tokens=256`; actual timing-kernel cubins were not separately captured. Other kernels, runtime state, or measurement variance remain possible explanations. The planned two complete candidate sweeps, with the existing baseline reused unchanged, are needed for a retention decision.

This supplements the earlier mixed-cluster [branch-hoist analysis](CODEGEN_BRANCH_HOIST.md), whose instruction savings apply to the mixed specializations that AUTO did not select. Earlier raw evidence and reports are preserved.
